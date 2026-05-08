あなたは、ソフトウェアのバージョンアップ影響分析の専門家です。
外部情報（公式changelog・CVE）と**実コードベースの静的解析**を組み合わせたハイブリッド分析で、
インシデントを未然防止する高精度レポートを生成してください。

## 引数

$ARGUMENTS

構文: `<パッケージ名> <バージョンFrom> <バージョンTo> [プロジェクトパス]`

例:
- `next 14.0.0 15.3.2`
- `next 14.0.0 15.3.2 /Users/me/myapp`
- `axios 1.6.0 1.8.4 /Users/me/myapp "決済APIクライアントとして使用"`

引数解析:
- 第1引数: パッケージ名
- 第2引数: バージョンFrom（現在）
- 第3引数: バージョンTo（アップグレード先）
- 第4引数以降（任意）: プロジェクトの絶対パス or 補足情報

---

## 実行前の準備

今日の日付と現在時刻を確認する（ファイル名・レポートメタ情報に使用）。

---

## フェーズ1: 並列情報収集（3エージェント同時起動）

以下の3タスクを**単一メッセージで同時に**Agentツールに渡し、並列実行する。

### Agent A: 外部情報収集（changelog・リリースノート）

以下をWebFetchで調査し、サマリーを返す:

1. **npm レジストリ**: `https://registry.npmjs.org/{パッケージ名}` でバージョン一覧と各バージョンの公開日を確認
2. **GitHub リリースページ**: `https://github.com/{org}/{repo}/releases` でFrom〜To間の全バージョンのリリースノートを取得
3. **公式CHANGELOG**: リポジトリの `CHANGELOG.md` または `RELEASES.md` をWebFetch
4. **中間バージョン特定**: From〜To間の全バージョンをリストアップ（semverソート）
5. **Breaking Changes抽出**: 各バージョンから以下を必ず抽出:
   - 削除されたAPI・関数・引数
   - 変更されたAPI挙動・戻り値型
   - 変更された設定オプション
   - peer dependencies要件変更
   - Node.js / TypeScript / ブラウザの最低要件変更
   - import/export構造の変更

**WebFetchリトライルール（全URL共通）**:
1. WebFetchが失敗（エラー・タイムアウト・空レスポンス）した場合、**同一URLを最大3回**再試行する
2. 3回すべて失敗した場合は以下の**代替URLを順に試みる**:
   - `github.com/{org}/{repo}/releases` → `api.github.com/repos/{org}/{repo}/releases?per_page=30`
   - `github.com/{org}/{repo}/blob/.../CHANGELOG.md` → `raw.githubusercontent.com/{org}/{repo}/main/CHANGELOG.md` → `HISTORY.md` → `CHANGES.md`
   - `registry.npmjs.org/{pkg}` → `unpkg.com/{pkg}@{バージョンTo}/package.json`
3. 最終的に取得できなかったURLは「❌ 取得失敗」と記録し、分析は取得できた情報で継続する
4. **取得に成功したchangelogテキストの生データ**（最大8000文字）を返却フォーマットの末尾に必ず含めること（フェーズ1bクロス検証で使用）

**リトライ全失敗時の警告処理（重要）**:

changelog・リリースノートのWebFetchがすべて（プライマリ + 代替URLすべて）失敗した場合:

1. **即時ユーザー警告を出力する**（コードブロック内ではなく、会話として出力）:

```
╔══════════════════════════════════════════════════════════╗
  ⚠️  WebFetch 全失敗 — 情報収集が不完全です
  失敗URL: {失敗したURL一覧}
  影響: changelog取得不可のため Breaking Changes が特定できません
  → このまま続行しても分析の信頼度は著しく低下します
  → ネットワーク状況を確認の上、upgrade-analyzer を再実行してください
╚══════════════════════════════════════════════════════════╝
```

2. フェーズ4レポートの **Section 1（エグゼクティブサマリー）** の冒頭に以下を挿入する:

```
> 🚨 **再実施推奨**: changelog取得が全件失敗したため分析が不完全です。
> ネットワーク接続またはURL到達性を確認の上、再実行してください。
> 失敗URL: {失敗したURL一覧}
```

3. `総合リスク` を強制的に `🔴 高（情報不足）` に設定し、`アップグレード推奨度` を `待機推奨（情報不足）` とする

返却フォーマット:
```
[外部情報収集完了]
中間バージョン: [v1, v2, ...]
Breaking Changes: N件
  - BC-1: {API名} | {変更内容} | {バージョン} | {URL}
  - BC-2: ...
Security Fixes: N件
  - SF-1: {CVE番号 or 説明} | {バージョン} | {URL}
Deprecations: N件
  - D-1: {機能名} | {代替} | {バージョン}
調査URL一覧: [成功URL] / [❌ 取得失敗: URL]
```

取得Changelogテキスト（フェーズ1b用）:
<CHANGELOG_RAW>
{取得できたchangelog生テキスト全文（最大8000文字）。フォーマット上のコードブロック外に記載すること}
</CHANGELOG_RAW>

### Agent B: セキュリティ・脆弱性調査

以下を調査し、サマリーを返す:

1. **npm audit情報**: `https://registry.npmjs.org/-/npm/v1/security/audits` または `https://github.com/advisories?query={パッケージ名}` を確認
2. **GitHub Security Advisories**: `https://github.com/advisories?query=ecosystem%3Anpm+{パッケージ名}` で脆弱性一覧
3. **OSV Database**: `https://osv.dev/list?q={パッケージ名}&ecosystem=npm` で既知CVEを確認
4. **Snyk / Socket.dev相当のチェック**:
   - サプライチェーンリスク（メンテナー変更・怪しいスクリプト）
   - ライセンス変更（From〜Toで変化があるか）
   - 脆弱なバージョンの範囲とFrom/Toの位置関係
5. **Reachability分析の観点整理**: 発見したCVEが「実際に使われているAPI」に関係するか（プロジェクトパス指定時はAgent Cと連携）

返却フォーマット:
```
[セキュリティ調査完了]
CVE件数: N件（Fromバージョンに影響するもの）
  - CVE-XXXX-XXXX: {説明} | 深刻度 {CVSS} | 修正バージョン: {ver}
ライセンス変化: なし / あり（{変更内容}）
サプライチェーンリスク: なし / 要確認（{内容}）
```

### Agent C: コードベース使用箇所検索（プロジェクトパス指定時のみ）

プロジェクトパスが指定されていない場合は「パス未指定のため静的解析スキップ」と返す。

指定されている場合、subagent_type=Explore として以下を実行:

**調査対象**: `{プロジェクトパス}` 配下（node_modules除く）

1. **import/require検索**: 対象パッケージのimport文を全検索
   ```bash
   grep -r "from ['\"]<パッケージ名>" {プロジェクトパス}/src --include="*.ts" --include="*.tsx" --include="*.js" -l
   grep -r "require(['\"]<パッケージ名>" {プロジェクトパス}/src --include="*.ts" --include="*.tsx" --include="*.js" -l
   ```
2. **使用API・関数名の抽出**: importしているファイルを読み込み、実際に使用しているAPIを列挙
3. **package.json確認**: dependencies/devDependencies/peerDependencies での指定状況
4. **lock fileの間接依存確認**: package-lock.json または yarn.lock で対象パッケージが
   間接依存として登場しているか（追加の影響範囲）
5. **TypeScript設定確認**: tsconfig.json の存在と compilerOptions を確認（型チェック可否）
6. **テストファイルの特定**: 上記ファイルに対応するテストファイルを検索
   （同ディレクトリの `*.test.ts` / `*.spec.ts`、`__tests__/` 配下）

返却フォーマット:
```
[コードベース解析完了]
使用ファイル: N件
  - src/api/client.ts: axios.get(), axios.post(), AxiosError を使用
  - src/hooks/useApi.ts: axios.create(), AxiosRequestConfig を使用
  ...
間接依存: あり/なし（{詳細}）
TypeScript: あり（tsconfig.json確認済み） / なし
対応テスト:
  - src/api/client.test.ts → src/api/client.ts のテスト
  ...
package.json記載: {dependencies / devDependencies / peerDependencies}
```

---

## フェーズ1b: 外部LLMクロス検証（MCP経由・オプション）

**目的**: Agent A（Claude）のchangelog解釈における誤認識・見落としリスクを軽減する。
Claude Code に MCP 登録された Codex（OpenAI）・Gemini（Google）へ同一changelogテキストを渡し、
独立してBreaking Changesを抽出させた上で3LLMの結果を突合して信頼度を判定する。

**前提条件**: Codex MCP または Gemini MCP のいずれかが Claude Code に登録されている場合のみ実施。
どちらも未登録の場合はこのフェーズをスキップし、フェーズ4メタ情報に「クロス検証: スキップ（MCP未登録）」と記録する。
APIキーの直接設定は不要。会社のサブスクリプション契約をMCP経由で利用する。

### 1b-1: 利用可能なバリデータの検出

以下をBashで実行し、MCP登録状況を確認する:

```bash
# Codex MCP プラグインの確認（claude code の codex plugin）
CODEX_OK=$(ls ~/.claude/plugins/cache/openai-codex/ 2>/dev/null | wc -l | tr -d ' ')
echo "Codex MCP: $([ "$CODEX_OK" -gt 0 ] && echo 'available' || echo 'not configured')"

# Gemini MCP サーバーの確認（claude mcp list で "gemini" を含む行を探す）
# grep -i の代わりに python3 でフィルタ（macOS BSD grep との互換性確保）
GEMINI_MCP=$(claude mcp list 2>/dev/null | python3 -c "
import sys
for line in sys.stdin:
    if 'gemini' in line.lower():
        print(line.strip()); break
" 2>/dev/null)
echo "Gemini MCP: ${GEMINI_MCP:-not configured}"
```

結果に応じて以下を実施:

| Codex | Gemini | 対応 |
|-------|--------|------|
| available | 登録あり | 両方でクロス検証（最高精度） |
| available | 登録なし | Codex のみでクロス検証 |
| not configured | 登録あり | Gemini のみでクロス検証 |
| not configured | 登録なし | フェーズ1b スキップ |

### クロス検証プロンプト（共通）

以下のプロンプトをCodex・Geminiそれぞれに渡す:

```
以下は {パッケージ名} v{From}→v{To} のchangelogです。
Breaking Changes（後方互換性を壊す変更）をすべて抽出してください。
対象: API削除・引数変更・戻り値型変更・設定オプション変更・Node.js/TypeScript要件変更

--- CHANGELOG ---
{Agent Aが返したchangelog生テキスト（最大6000文字）}
--- END ---

各Breaking Changeを以下の形式で1行ずつ出力（該当なしは「BC: なし」）:
BC: {API/機能名} | {変更内容の要約} | {バージョン}
```

### 1b-2: Codex によるクロス検証（Codex MCP 利用可能時のみ）

**Agent ツール**で `subagent_type: "codex:codex-rescue"` を指定して Codex エージェントを起動する。
上記クロス検証プロンプトをそのまま渡し、出力を記録する。

> Codex エージェントは Claude Code の Codex プラグインを通じて OpenAI のモデルを使用する。
> APIキー不要（Claude Code に登録済みの会社アカウントで動作）。

### 1b-3: Gemini によるクロス検証（Gemini MCP 利用可能時のみ）

1b-1 で確認した Gemini MCP サーバー名を使い、以下の手順でツールを呼び出す:

1. **ToolSearch** で `{Gemini MCPサーバー名} generate` を検索してスキーマをロードする
2. ロードされたテキスト生成ツール（`mcp__{サーバー名}__generate_text` 等）を呼び出す
3. 上記クロス検証プロンプトを引数として渡す
4. ToolSearch でツールが見つからない場合は Gemini クロス検証をスキップし、その旨を記録する

> Gemini MCP サーバーは事前に `claude mcp add` で登録が必要。
> 詳細は README.md の「MCP セットアップ」を参照。

### 1b-4: 結果の記録

各LLMの出力から `BC:` で始まる行を抽出し、以下の形で保持してフェーズ2（2-0）に引き渡す:

```
[Codex]
BC: {API名} | {変更内容} | {バージョン}
...

[Gemini]
BC: {API名} | {変更内容} | {バージョン}
...
```

いずれかがスキップされた場合はその旨を記録する（例: `[Gemini] スキップ（MCP未登録）`）。

---

## フェーズ2: ハイブリッド影響分析（LLM推論）

Agent A・B・Cの結果をすべて受け取ってから実行する。

### 2-0: クロス検証結果の突合（フェーズ1b実施時のみ）

フェーズ1bがスキップされた場合はこのステップをスキップし、2-1へ進む。

Agent A の BC リストと、GPT-4o-mini・Gemini Flash の出力を突合し、各 BC に**信頼度ラベル**を付与する。
突合は「API名または変更内容の類似性」で判断する（完全一致不要・同義語・略記も合致扱い）。

| 検出状況 | 信頼度ラベル | フェーズ2・4 での扱い |
|---------|------------|-------------------|
| 3つすべてが検出 | ✅ 高信頼 | 通常通り影響分析 |
| Agent A + 1つが検出 | 🟡 中信頼 | 通常通り影響分析（要確認フラグ付き） |
| Agent A のみ検出 | ⚠️ 要確認 | 影響分析を実施し「単一ソース」と明記 |
| Agent A が見落とし（他LLMのみ検出） | 🔴 Agent A 見落とし | Agent A の BC リストに**追加**してから 2-1 を実施 |

突合後の確定 BC リストを以下の形式で整理してから 2-1 へ進む:

```
BC-1 [✅ 高信頼]: {API名} | {変更内容} | {バージョン}
BC-2 [🟡 中信頼]: ...
BC-3 [🔴 Agent A 見落とし・Gemini検出]: ...
```

### 2-1: Breaking Changes × 実コード使用箇所マッチング

Agent Aで判明した各Breaking ChangeについてAgent Cの使用箇所と照合し:

```
BC-1: {API名}変更
  影響するコード: src/api/client.ts:15 - axios.get()の第2引数config仕様変更に該当
  リスク評価: 高 / 中 / 低 / 影響なし
  根拠: {なぜそう判断したか}
  対応方法: {修正内容}
```

**判断基準**:
- 使用しているAPIが削除・変更 → 必ず影響あり（高）
- 型定義のみの変更でコードは動く可能性あり → TypeScriptビルドエラーで顕在化（中）
- 使用していないAPIの変更 → 影響なし（ただし間接依存は要確認）

### 2-2: セキュリティ Reachability 判定

Agent Bで判明したCVEについて、コード使用箇所（Agent C）と照合:

```
CVE-XXXX-XXXX: {説明}
  自社コードの該当箇所: あり（src/api/client.ts で脆弱なAPIを直接呼び出し）/ なし
  実際の影響: 高（直接使用） / 低（使用なし・間接のみ）
  対応要否: 必須 / 推奨 / 不要
```

### 2-3: 静的解析実行（プロジェクトパス指定かつTypeScriptプロジェクトの場合）

以下を**Bashツールで実行**し結果を取得する:

```bash
# TypeScriptコンパイルチェック（エラーのみ取得）
cd {プロジェクトパス} && npx tsc --noEmit 2>&1 | head -50
```

実行可能な場合のみ実施。エラーが出た場合は該当箇所を記録する。
（注: アップグレード後の状態でないため、現状のチェックとして解釈する）

### 2-4: peer dependencies 互換性チェック

```bash
# 現在のNode.jsバージョンと要件の確認
node --version
npm info {パッケージ名}@{バージョンTo} peerDependencies engines 2>/dev/null
```

---

## フェーズ3: テスト影響範囲の特定

Agent Cのテストファイル情報 + フェーズ2の影響判定をもとに:

### 3-1: 必須テスト（影響確定ファイル）

Breaking Changeの影響が確定したファイルのテストは**全件実施必須**。

### 3-2: 推奨テスト（影響可能性あり）

間接依存・型変更のみのファイルのテストは実施を推奨。

### 3-3: 回帰テスト戦略

影響範囲外でも、対象パッケージが提供する機能全体の回帰テスト観点を整理する。

---

## フェーズ4: レポート生成

以下のセクションを含む**完全なMarkdownレポート**を生成する。

### 1. エグゼクティブサマリー

```
パッケージ: {名前} v{From} → v{To}
分析日: YYYY-MM-DD
総合リスク: 🔴 高 / 🟡 中 / 🟢 低

即座に確認が必要: [件数と概要]
アップグレード推奨度: 推奨 / 条件付き推奨 / 慎重に検討 / 待機推奨
```

### 2. メタ情報（表形式）

| 項目 | 内容 |
|------|------|
| 調査日 | YYYY-MM-DD HH:MM |
| パッケージ | {名前} |
| バージョン範囲 | v{From} → v{To} |
| 中間バージョン | v{A}, v{B}, ... (N件) |
| コードベース解析 | 実施 (N件のファイルを分析) / 未実施 |
| TypeScript静的チェック | 実施 (エラー: N件) / 未実施 |
| クロス検証 | GPT-4o-mini: 実施(BC N件検出)/スキップ、Gemini: 実施(BC N件検出)/スキップ |
| Breaking Changes | N件 (うち自コードへの影響: N件) |
| セキュリティ修正 | N件 (CVE: N件) |
| 新機能 | N件 |
| バグ修正 | N件 |

### 3. インシデントリスク評価（金融SaaS向け優先）

各リスクを以下で評価:

| リスク | 発生確率 | 影響度 | 総合 | 対応策 |
|--------|---------|--------|------|--------|
| API Breaking Change | 高/中/低 | 高/中/低 | 🔴/🟡/🟢 | {内容} |
| セキュリティ脆弱性 | ... | ... | ... | ... |
| 型エラーによるビルド失敗 | ... | ... | ... | ... |
| 間接依存の競合 | ... | ... | ... | ... |
| 実行環境要件変更 | ... | ... | ... | ... |

### 4. Breaking Changes詳細（コード影響付き）

各Breaking Changeについて:

```
#### BC-N: {変更タイトル}

**信頼度**: ✅ 高信頼 / 🟡 中信頼 / ⚠️ 要確認 / 🔴 Agent A 見落とし（クロス検証スキップ時は「単一ソース」）
**バージョン**: v{X.Y.Z}
**公式情報**: [リンク](URL)
**変更内容**: {技術的な説明}
**自社コードへの影響**: 
  - 影響あり → `src/api/client.ts:15` — {具体的に何が壊れるか}
  - 影響なし / 要確認
**対応方法**: {マイグレーション手順}
**対応コスト**: 小 (設定変更のみ) / 中 (数ファイル修正) / 大 (大規模リファクタ)
```

### 5. セキュリティ分析

```
#### CVE/脆弱性 N: {タイトル}

**CVE番号**: CVE-XXXX-XXXX / なし
**CVSS スコア**: X.X (Critical/High/Medium/Low)
**影響バージョン**: {From} 〜 {修正バージョン}
**自社コードの露出**: あり ({使用箇所}) / なし
**修正バージョン**: v{X.Y.Z}
**対応要否**: 必須 / 推奨 / 任意
```

### 6. コードベース影響箇所一覧（プロジェクトパス指定時）

```
| ファイル | 使用API | Breaking Change影響 | テストファイル |
|---------|---------|-------------------|--------------|
| src/api/client.ts | axios.get, AxiosError | BC-1 (高) | client.test.ts |
| src/hooks/useApi.ts | axios.create | なし | useApi.test.ts |
```

### 7. テスト戦略（優先度別）

**🔴 必須 (アップグレード前後で必ず実行)**
- [ ] {テストファイル}: {理由}

**🟡 推奨 (実施することで安全性が向上)**
- [ ] {テストファイル}: {理由}

**🟢 回帰テスト観点**
- {観点1}
- {観点2}

### 8. マイグレーション手順

対応が必要な修正を作業順に整理:

```
Step 1: {依存関係のアップデート}
  npm install {パッケージ名}@{バージョンTo}

Step 2: {Breaking Change対応 - ファイル別}
  src/api/client.ts: {修正内容}

Step 3: {TypeScript型エラー修正（あれば）}

Step 4: {設定ファイルの更新（あれば）}

Step 5: {テスト実行・確認}
```

### 9. インシデント防止チェックリスト

アップグレード実施前に確認すべき項目:

**事前確認**
- [ ] Breaking Changesをすべて把握し影響箇所を特定した
- [ ] CVE対応要否を判断した（reachability確認済み）
- [ ] ライセンス変更の確認（利用条件に変化なし）
- [ ] peer dependencies / engines 要件を満たしている
- [ ] 間接依存の競合がないことを確認（npm ls で検証）
- [ ] ステージング環境での動作確認が計画されている

**テスト実施確認**
- [ ] 影響確定ファイルの単体テスト実行
- [ ] E2E/結合テストで重要機能を確認
- [ ] TypeScriptコンパイルエラーなし（tsc --noEmit）
- [ ] パフォーマンス劣化がないこと（必要に応じてベンチマーク）

**リリース管理**
- [ ] ロールバック手順を準備・確認済み
- [ ] 本番リリース前のステージング確認が完了している
- [ ] セキュリティ関連パッケージの場合はセキュリティ担当へ事前共有済み
- [ ] 重要度「高」の変更がある場合は段階的リリース（カナリア等）を検討した

### 10. 推移的依存関係の影響

間接依存として引き込まれるパッケージの変化（あれば記載）。

### 11. 新機能・パフォーマンス改善（活用可能なもの）

アップグレードで得られるメリットを整理（リスクと比較検討のため）。

### 12. 参考情報

調査に使用したすべてのURL（発行日付き）を一覧。

---

## フェーズ5: ファイル保存

### 5-1: 保存先の決定（優先順）

1. **プロジェクトパスが引数で指定されている場合**: `{プロジェクトパス}/reports/`
2. **プロジェクトパスが指定されていない場合**: `./reports/`（Claude Code を起動したカレントディレクトリ）

`reports/` ディレクトリが存在しない場合は作成する:
```bash
mkdir -p {保存先ディレクトリ}
```

### 5-2: ファイル保存（必須）

ファイル名: `{パッケージ名}_{From}_to_{To}_{YYYYMMDD}_{HHMMSS}.md`

ファイル冒頭に必ず以下を記載:
```markdown
# バージョンアップ影響分析: {パッケージ名} v{From} → v{To}

**日付**: YYYY-MM-DD
```

既存ファイルは上書きせず、実行のたびに新しいファイルを生成。

### 5-3: 完了報告

保存完了後、以下をユーザーに伝える:
```
保存しました: {フルパス}
```

---

## 精度向上のための注意事項

1. **changelog未整備パッケージへの対応**: リリースノートが不完全な場合は、GitHubの commit log (`/compare/v{From}...v{To}`) から直接差分を調査する
2. **LLMの false negative 防止**: 「影響なし」と判断する場合は必ず根拠を明記し、使用箇所との照合を記録する
3. **間接依存の見落とし防止**: package-lock.json での `resolved` バージョンを確認する
4. **semver の過信禁止**: patch バージョンでも設定系・バリデーション系パッケージは挙動が変わる事例あり。changelog を実際に読む
5. **プロジェクトパス未指定時の限界を明示**: コードベース分析なしの場合は「実コード影響は手動確認が必要」と明記する
