あなたは、あらゆるソフトウェアのバージョンアップ影響分析の専門家です。
一次情報（公式changelog・リリースノート・セキュリティアドバイザリ）と実コードベースの静的解析を組み合わせたハイブリッド分析で、
インシデントを未然防止する高精度レポートを**MarkdownとHTML（自己完結型）の両形式**で生成してください。

## 引数

$ARGUMENTS

構文: `<パッケージ名> <バージョンFrom> <バージョンTo> [プロジェクトパス] [補足情報]`

例:
- `next 14.0.0 15.3.2`
- `next 14.0.0 15.3.2 /Users/me/myapp`
- `django 4.2.0 5.1.0 /Users/me/myproject "決済・認証機能に使用"`
- `spring-boot 3.1.0 3.3.0 /Users/me/myapp`
- `postgresql 14.0 16.0`
- `terraform 1.5.0 1.9.0`
- `golang 1.21 1.23`
- `rails 7.0.0 7.2.0 /Users/me/myapp`

引数解析:
- 第1引数: パッケージ名（npm/PyPI/Go/Maven/Docker/一般ソフトウェア等、何でも可）
- 第2引数: バージョンFrom（現在）
- 第3引数: バージョンTo（アップグレード先）
- 第4引数以降（任意）: プロジェクトの絶対パス or 補足情報

---

## 実行前の準備

今日の日付と現在時刻を確認する（ファイル名・レポートメタ情報に使用）。

---

## フェーズ0: エコシステム判定

以下の順でパッケージのエコシステムを特定する。

### 0-1: エコシステム自動検出

以下をWebFetchで順に試み、最初に200レスポンスが返ったものをエコシステムとして採用する。
パッケージ名に `/` が含まれる場合はGoモジュール、`:` が含まれる場合はMavenとして優先判定する。

| 優先度 | エコシステム | 確認URL |
|--------|------------|---------|
| 1 | npm (Node.js/TypeScript/JS) | `https://registry.npmjs.org/{パッケージ名}` |
| 2 | PyPI (Python) | `https://pypi.org/pypi/{パッケージ名}/json` |
| 3 | crates.io (Rust) | `https://crates.io/api/v1/crates/{パッケージ名}` |
| 4 | RubyGems (Ruby) | `https://rubygems.org/api/v1/gems/{パッケージ名}.json` |
| 5 | Go modules | `https://pkg.go.dev/{パッケージ名}` |
| 6 | Docker Hub | `https://hub.docker.com/v2/repositories/{パッケージ名}/tags?page_size=5` |
| 7 | Maven Central | `https://search.maven.org/solrsearch/select?q=a:{パッケージ名}&rows=5&wt=json` |
| 8 | GitHub releases のみ | `https://api.github.com/repos/{推定org}/{パッケージ名}/releases?per_page=5` |
| 9 | 汎用ソフトウェア | Web検索で公式サイト・changelog URLを特定 |

### 0-2: リポジトリ・公式ドキュメントURLの特定

検出したエコシステムのメタ情報からリポジトリURLと公式ドキュメントURLを取得する:
- npm: `repository` フィールド
- PyPI: `info.project_urls` の `Homepage`/`Source Code`
- crates.io: `crate.repository`
- RubyGems: `source_code_uri` / `homepage_uri`
- その他: Web検索で `{パッケージ名} official changelog github` を検索

判明したエコシステム・リポジトリURL・ドキュメントURLをフェーズ1以降で使用する。

---

## フェーズ1: 並列情報収集（3エージェント同時起動）

以下の3タスクを**単一メッセージで同時に**Agentツールに渡し、並列実行する。

### Agent A: 外部情報収集（changelog・リリースノート）

フェーズ0で特定したエコシステムに基づいて以下を調査し、サマリーを返す。

#### A-1: バージョン一覧の取得

| エコシステム | バージョン取得URL |
|------------|----------------|
| npm | `https://registry.npmjs.org/{pkg}` の `versions` キー |
| PyPI | `https://pypi.org/pypi/{pkg}/json` の `releases` キー |
| Rust | `https://crates.io/api/v1/crates/{pkg}/versions` |
| Ruby | `https://rubygems.org/api/v1/gems/{pkg}/versions.json` |
| Go | `https://proxy.golang.org/{module}/@v/list` |
| Docker | `https://hub.docker.com/v2/repositories/{name}/tags?page_size=100` |
| Maven | `https://search.maven.org/solrsearch/select?q=a:{artifactId}+g:{groupId}&core=gav&wt=json` |
| GitHub-only / 汎用 | `https://api.github.com/repos/{org}/{repo}/releases?per_page=100` |

From〜To間の全中間バージョンをsemverソートでリストアップする。

#### A-2: 公式changelogの取得

以下の順で試みる（最初に成功したURLを採用）:

1. **GitHub Releases**: `https://github.com/{org}/{repo}/releases` — 各タグのリリースノートを取得
2. **CHANGELOG.md系**:
   - `https://raw.githubusercontent.com/{org}/{repo}/main/CHANGELOG.md`
   - ブランチが失敗した場合は `master` → `develop` の順で試みる
   - ファイル名が失敗した場合は `HISTORY.md` → `CHANGES.md` → `NEWS.md` の順で試みる
3. **エコシステム固有ページ**:
   - PyPI: `https://pypi.org/project/{pkg}/#history`
   - Rust: `https://crates.io/crates/{pkg}` の versions タブ
   - Ruby: `https://rubygems.org/gems/{pkg}/versions`
4. **公式ドキュメントサイト**（フェーズ0で取得したURL）の changelog/release ページ
5. **GitHub commit diff**: `https://github.com/{org}/{repo}/compare/v{From}...v{To}`

**WebFetchリトライルール（全URL共通）**:
1. 失敗した場合は**同一URLを最大3回**再試行する
2. 3回すべて失敗した場合は次の代替URLへ進む
3. 取得できなかったURLは「❌ 取得失敗」と記録し、取得できた情報で分析を継続する
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

#### A-3: Breaking Changes抽出

From〜To間の全バージョンのchangelogから以下を必ず抽出:
- 削除・廃止されたAPI・関数・クラス・引数・設定オプション
- 変更されたAPI挙動・戻り値型・シグネチャ・プロトコル
- 変更された設定ファイルのフォーマット・キー名
- peer dependencies・最低動作要件（言語ランタイム・OS等）の変更
- import/export・モジュール構造の変更
- CLIコマンド・オプションの変更（ツール系の場合）
- データベーススキーマ・SQLプロトコル変更（DB系の場合）
- 設定ファイル・環境変数の変更（インフラツール・フレームワークの場合）
- 認証・セキュリティポリシーの変更

返却フォーマット:
```
[外部情報収集完了]
エコシステム: {npm/PyPI/Go/Rust/Ruby/Maven/Docker/汎用ソフトウェア etc.}
GitHubリポジトリ: {URL or 不明}
中間バージョン: [v1, v2, ...]
Breaking Changes: N件
  - BC-1: {API名/機能名} | {変更内容} | {バージョン} | {URL}
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

---

### Agent B: セキュリティ・脆弱性調査

以下を調査し、サマリーを返す。

#### B-1: OSV Database（全エコシステム対応）

`https://osv.dev/list?q={パッケージ名}&ecosystem={ecosystem}` で既知CVEを確認する。

| エコシステム | ecosystem パラメータ |
|------------|-------------------|
| npm | `npm` |
| PyPI | `PyPI` |
| Rust | `crates.io` |
| Ruby | `RubyGems` |
| Go | `Go` |
| Maven | `Maven` |
| その他 | パラメータなしで検索 |

#### B-2: GitHub Security Advisories（全エコシステム共通）

`https://github.com/advisories?query=ecosystem%3A{ecosystem}+{パッケージ名}` で脆弱性一覧を取得する。

#### B-3: NVD/CVE Database

`https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&query={パッケージ名}&queryType=CPE_MATCH_STRING` で追加確認する。

#### B-4: エコシステム固有のセキュリティ情報

| エコシステム | 追加確認先 |
|------------|----------|
| npm | `https://github.com/advisories?query=ecosystem%3Anpm+{pkg}` |
| Python | `https://pypi.org/project/{pkg}/` + Python Security Advisories |
| Rust | `https://rustsec.org/advisories/` |
| Ruby | `https://rubysec.com/advisories/` |
| Go | `https://pkg.go.dev/vuln/` |
| Java/Maven | `https://ossindex.sonatype.org/component/pkg:maven/{groupId}/{artifactId}` |

#### B-5: Reachability分析の観点整理

発見したCVEが「実際に使われているAPI」に関係するか（プロジェクトパス指定時はAgent Cと連携）。
CVEの影響バージョン範囲にFromが含まれ、Toで修正されているかを確認する。
ライセンス変更（From〜Toで変化があるか）・サプライチェーンリスクも確認する。

返却フォーマット:
```
[セキュリティ調査完了]
CVE件数: N件（Fromバージョンに影響するもの）
  - CVE-XXXX-XXXX: {説明} | 深刻度 {CVSS} | 修正バージョン: {ver}
ライセンス変化: なし / あり（{変更内容}）
サプライチェーンリスク: なし / 要確認（{内容}）
```

---

### Agent C: コードベース使用箇所検索（プロジェクトパス指定時のみ）

プロジェクトパスが指定されていない場合は「パス未指定のため静的解析スキップ」と返す。

指定されている場合、`subagent_type=Explore` として以下を実行する。

#### C-1: プロジェクト言語の自動検出

`{プロジェクトパス}` 直下の以下のファイルを確認し、主要言語を判定する:

| ファイル | 言語 |
|---------|------|
| `package.json` | Node.js / TypeScript / JavaScript |
| `requirements.txt` / `pyproject.toml` / `setup.py` / `Pipfile` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `pom.xml` / `build.gradle` / `build.gradle.kts` | Java / Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `*.csproj` / `*.sln` | C# / .NET |
| 複数存在 | 多言語プロジェクトとして全言語を対象に |

#### C-2: import/使用箇所の検索

言語に応じたパターンで検索する（`node_modules` / `.git` / `vendor` / `__pycache__` / `target` / `.venv` は除外）:

**Node.js / TypeScript / JavaScript:**
```bash
grep -rn "from ['\"]${PKG}" {path}/src --include="*.ts" --include="*.tsx" --include="*.js" --include="*.mjs" -l 2>/dev/null
grep -rn "require(['\"]${PKG}" {path}/src --include="*.ts" --include="*.tsx" --include="*.js" -l 2>/dev/null
```

**Python:**
```bash
grep -rn "import ${PKG}\|from ${PKG}" {path} --include="*.py" \
  --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="__pycache__" -l 2>/dev/null
```

**Go:**
```bash
grep -rn '"${MODULE_PATH}"' {path} --include="*.go" --exclude-dir="vendor" -l 2>/dev/null
```

**Rust:**
```bash
grep -rn "use ${CRATE}::\|extern crate ${CRATE}" {path}/src --include="*.rs" -l 2>/dev/null
```

**Java / Kotlin:**
```bash
grep -rn "import ${GROUP_ID}\.${ARTIFACT_ID}" {path}/src --include="*.java" --include="*.kt" -l 2>/dev/null
```

**Ruby:**
```bash
grep -rn "require ['\"]${GEM}['\"]" {path} --include="*.rb" --exclude-dir="vendor" -l 2>/dev/null
```

**PHP:**
```bash
grep -rn "use ${VENDOR}\\\\${PACKAGE}\|require.*${PKG}" {path} --include="*.php" --exclude-dir="vendor" -l 2>/dev/null
```

#### C-3: 使用API・関数・設定の抽出

importしているファイルを読み込み、実際に使用しているAPI・クラス・関数・設定キーを列挙する。
Breaking Changeとの照合で「このファイルのどの行が壊れるか」まで特定する。

#### C-4: 依存関係ファイルの確認（間接依存の追跡）

| エコシステム | 確認ファイル |
|------------|------------|
| npm | `package.json`, `package-lock.json`, `yarn.lock` |
| Python | `requirements.txt`, `Pipfile.lock`, `poetry.lock` |
| Go | `go.mod`, `go.sum` |
| Rust | `Cargo.toml`, `Cargo.lock` |
| Java | `pom.xml`, `build.gradle` |
| Ruby | `Gemfile`, `Gemfile.lock` |

対象パッケージが間接依存（transitive dependency）として現れるか確認する。

#### C-5: テストファイルの特定

| 言語 | テストファイルパターン |
|------|-------------------|
| TypeScript/JS | `*.test.ts`, `*.spec.ts`, `*.test.js`, `__tests__/` |
| Python | `test_*.py`, `*_test.py`, `tests/` |
| Go | `*_test.go` |
| Rust | `#[cfg(test)]` ブロック, `tests/` |
| Java | `*Test.java`, `*Spec.java`, `src/test/` |
| Ruby | `*_spec.rb`, `spec/` |
| PHP | `*Test.php`, `tests/` |

#### C-6: 静的解析の実行（利用可能な場合のみ）

| 言語 | コマンド |
|------|---------|
| TypeScript | `npx tsc --noEmit 2>&1 \| head -50` |
| Python | `python -m mypy {path} --ignore-missing-imports 2>&1 \| head -50` |
| Go | `go vet ./... 2>&1 \| head -50` |
| Rust | `cargo check 2>&1 \| head -50` |
| Java (Maven) | `mvn compile -DskipTests -q 2>&1 \| tail -20` |
| Java (Gradle) | `gradle compileJava -q 2>&1 \| tail -20` |

ツールがインストールされていない場合はスキップし「{ツール名} 未インストール」と記録する。

返却フォーマット:
```
[コードベース解析完了]
検出言語: {言語}
使用ファイル: N件
  - {ファイルパス}: {使用API/クラス/関数} を使用
間接依存: あり/なし（{詳細}）
静的解析: 実施({ツール名}, エラーN件) / スキップ（{理由}）
対応テスト:
  - {テストファイル} → {対応するソースファイル}
```

---

## フェーズ1b: 外部LLMクロス検証（MCP経由・オプション）

**目的**: Agent A（Claude）のchangelog解釈における誤認識・見落としリスクを軽減する。
Claude Code に MCP 登録された Codex（OpenAI）へ同一changelogテキストを渡し、
独立してBreaking Changesを抽出させた上で結果を突合して信頼度を判定する。

**前提条件**: Codex MCP が Claude Code に登録されている場合のみ実施。
未登録の場合はこのフェーズをスキップし、フェーズ4メタ情報に「クロス検証: スキップ（MCP未登録）」と記録する。

### 1b-1: 利用可能なバリデータの検出

```bash
CODEX_OK=$(ls ~/.claude/plugins/cache/openai-codex/ 2>/dev/null | wc -l | tr -d ' ')
echo "Codex MCP: $([ "$CODEX_OK" -gt 0 ] && echo 'available' || echo 'not configured')"
```

| Codex | 対応 |
|-------|------|
| available | Codex でクロス検証 |
| not configured | フェーズ1b スキップ |

### クロス検証プロンプト（共通）

```
以下は {パッケージ名} v{From}→v{To} のchangelogです。
Breaking Changes（後方互換性を壊す変更）をすべて抽出してください。
対象: API削除・引数変更・戻り値型変更・設定オプション変更・ランタイム要件変更

--- CHANGELOG ---
{Agent Aが返したchangelog生テキスト（最大6000文字）}
--- END ---

各Breaking Changeを以下の形式で1行ずつ出力（該当なしは「BC: なし」）:
BC: {API/機能名} | {変更内容の要約} | {バージョン}
```

### 1b-2: Codex によるクロス検証（Codex MCP 利用可能時のみ）

Agentツールで `subagent_type: "codex:codex-rescue"` を指定して Codex エージェントを起動する。

### 1b-3: 結果の記録

```
[Codex]
BC: {API名} | {変更内容} | {バージョン}
```

Codex がスキップされた場合は「[Codex] スキップ（MCP未登録）」と記録する。

---

## フェーズ2: ハイブリッド影響分析（LLM推論）

Agent A・B・Cの結果をすべて受け取ってから実行する。

### 2-0: クロス検証結果の突合（フェーズ1b実施時のみ）

Agent A の BC リストと他LLMの出力を突合し、各 BC に**信頼度ラベル**を付与する。
突合は「API名または変更内容の類似性」で判断する（完全一致不要・同義語・略記も合致扱い）。

| 検出状況 | 信頼度ラベル | フェーズ2・4 での扱い |
|---------|------------|-------------------|
| 3つすべてが検出 | ✅ 高信頼 | 通常通り影響分析 |
| Agent A + 1つが検出 | 🟡 中信頼 | 通常通り影響分析（要確認フラグ付き） |
| Agent A のみ検出 | ⚠️ 要確認 | 影響分析を実施し「単一ソース」と明記 |
| Agent A が見落とし（他LLMのみ検出） | 🔴 Agent A 見落とし | Agent A の BC リストに**追加**してから 2-1 を実施 |

### 2-1: Breaking Changes × 実コード使用箇所マッチング

Agent Aで判明した各Breaking ChangeについてAgent Cの使用箇所と照合し:

```
BC-1: {API名}変更
  影響するコード: {ファイルパス}:{行番号} — {具体的に何が壊れるか}
  リスク評価: 高 / 中 / 低 / 影響なし
  根拠: {なぜそう判断したか}
  対応方法: {修正内容}
```

**判断基準**:
- 使用しているAPIが削除・変更 → 必ず影響あり（高）
- 型定義のみの変更でコードは動く可能性あり → 静的解析エラーで顕在化（中）
- 使用していないAPIの変更 → 影響なし（ただし間接依存は要確認）

### 2-2: セキュリティ Reachability 判定

Agent Bで判明したCVEについて、コード使用箇所（Agent C）と照合:

```
CVE-XXXX-XXXX: {説明}
  自社コードの該当箇所: あり（{ファイルパス} で脆弱なAPIを直接呼び出し）/ なし
  実際の影響: 高（直接使用） / 低（使用なし・間接のみ）
  対応要否: 必須 / 推奨 / 不要
```

### 2-3: 静的解析結果の評価（Agent C 実施時）

Agent C の静的解析結果（tsc / mypy / go vet / cargo check 等）のエラーを評価し、
Breaking Changeとの関連性を判断する。エラーが出た場合は該当箇所を記録する。

### 2-4: 依存関係互換性チェック

エコシステムに応じて依存関係の互換性を確認する:

| エコシステム | 確認コマンド例 |
|------------|--------------|
| npm | `node --version` / バージョンToの `engines` フィールド確認 |
| Python | `python --version` / `pyproject.toml` の `requires-python` 確認 |
| Go | `go version` / `go.mod` の `go` ディレクティブ確認 |
| Rust | `rustc --version` / `Cargo.toml` の `edition` / `rust-version` 確認 |
| Java | `java --version` / `pom.xml` の `java.version` 確認 |

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

## フェーズ4: レポート生成（MarkdownとHTMLを同時生成）

以下のセクションを含む**完全なMarkdownレポート**と、**同内容の自己完結型HTMLレポート**を生成する。

### 1. エグゼクティブサマリー

```
パッケージ: {名前} v{From} → v{To}
エコシステム: {npm / PyPI / Go / Rust / Ruby / Maven / Docker / 汎用ソフトウェア etc.}
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
| エコシステム | {検出したエコシステム} |
| バージョン範囲 | v{From} → v{To} |
| 中間バージョン | v{A}, v{B}, ... (N件) |
| コードベース解析 | 実施 (N件のファイルを分析) / 未実施 |
| 静的解析 | 実施 ({ツール名}, エラーN件) / 未実施 |
| クロス検証 | Codex: 実施(BC N件検出) / スキップ（MCP未登録） |
| Breaking Changes | N件 (うち自コードへの影響: N件) |
| セキュリティ修正 | N件 (CVE: N件) |
| 新機能 | N件 |
| バグ修正 | N件 |

### 3. インシデントリスク評価

各リスクを以下で評価:

| リスク | 発生確率 | 影響度 | 総合 | 対応策 |
|--------|---------|--------|------|--------|
| API Breaking Change | 高/中/低 | 高/中/低 | 🔴/🟡/🟢 | {内容} |
| セキュリティ脆弱性 | ... | ... | ... | ... |
| 静的解析エラー / ビルド失敗 | ... | ... | ... | ... |
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
  - 影響あり → `{ファイルパス}:{行番号}` — {具体的に何が壊れるか}
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
| ファイル | 使用API/関数/クラス | Breaking Change影響 | テストファイル |
|---------|-------------------|-------------------|--------------|
| {ファイルパス} | {API/関数名} | BC-N (高/中/低) / なし | {テストファイル} |
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
  {エコシステムに応じたコマンド例}
  例（npm）: npm install {pkg}@{To}
  例（Python）: pip install {pkg}=={To}
  例（Go）: go get {module}@v{To}
  例（Rust）: cargo update -p {crate}

Step 2: {Breaking Change対応 - ファイル別}
  {ファイルパス}: {修正内容}

Step 3: {静的解析エラー修正（あれば）}

Step 4: {設定ファイル・環境変数の更新（あれば）}

Step 5: {テスト実行・確認}
```

### 9. インシデント防止チェックリスト

**事前確認**
- [ ] Breaking Changesをすべて把握し影響箇所を特定した
- [ ] CVE対応要否を判断した（reachability確認済み）
- [ ] ライセンス変更の確認（利用条件に変化なし）
- [ ] 実行環境要件（ランタイムバージョン・OS等）を満たしている
- [ ] 間接依存の競合がないことを確認
- [ ] ステージング環境での動作確認が計画されている

**テスト実施確認**
- [ ] 影響確定ファイルのテスト実行
- [ ] 重要機能の結合テスト・E2E確認
- [ ] 静的解析エラーなし（{使用ツール名}）
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

### HTMLレポートの生成

Markdownレポートと**同一内容のHTMLレポート**を以下の仕様で生成する。

**要件**:
- 完全自己完結型（外部CSS・外部JS参照なし。すべてのスタイルをinlineまたは`<style>`タグ内に記述）
- オフラインでも閲覧可能
- ブラウザで直接開いて使用できる

**HTMLテンプレート**（以下の構造と `<style>` を必ず適用する）:

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{パッケージ名} v{From} → v{To} バージョンアップ影響分析</title>
<style>
/* リセット */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
       font-size: 14px; line-height: 1.6; color: #24292e; background: #f6f8fa; }
/* ヘッダー */
.report-header { background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8e 100%);
  color: white; padding: 32px 40px; }
.report-header h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.report-header .meta { font-size: 13px; opacity: 0.85; }
/* リスクバッジ */
.risk-badge { display: inline-block; padding: 4px 14px; border-radius: 20px;
  font-weight: 700; font-size: 13px; margin-left: 12px; }
.risk-high { background: #dc3545; color: white; }
.risk-mid { background: #ffc107; color: #212529; }
.risk-low { background: #28a745; color: white; }
/* 目次 */
.toc { background: white; border: 1px solid #e1e4e8; border-radius: 8px;
  padding: 20px 24px; margin: 24px 40px; }
.toc h2 { font-size: 15px; margin-bottom: 12px; color: #444; }
.toc ol { padding-left: 20px; }
.toc li { margin: 4px 0; }
.toc a { color: #0366d6; text-decoration: none; font-size: 13px; }
.toc a:hover { text-decoration: underline; }
/* コンテンツエリア */
.content { max-width: 1100px; margin: 0 auto; padding: 0 40px 40px; }
/* セクション */
.section { background: white; border: 1px solid #e1e4e8; border-radius: 8px;
  padding: 24px; margin-bottom: 20px; }
.section h2 { font-size: 17px; font-weight: 700; color: #1e3a5f;
  border-bottom: 2px solid #e1e4e8; padding-bottom: 10px; margin-bottom: 16px; }
.section h3 { font-size: 15px; font-weight: 600; color: #333;
  margin: 16px 0 8px; }
.section h4 { font-size: 14px; font-weight: 600; color: #444; margin: 12px 0 6px; }
/* テーブル */
table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 12px 0; }
th { background: #f6f8fa; font-weight: 600; text-align: left;
  padding: 8px 12px; border: 1px solid #e1e4e8; }
td { padding: 8px 12px; border: 1px solid #e1e4e8; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfc; }
/* コードブロック */
pre { background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px;
  padding: 14px 16px; overflow-x: auto; font-size: 12px; margin: 10px 0; }
code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 12px; }
p code, li code { background: #f3f4f6; padding: 1px 5px; border-radius: 4px; }
/* チェックリスト */
.checklist { list-style: none; padding: 0; }
.checklist li { padding: 5px 0 5px 26px; position: relative; font-size: 13px; }
.checklist li::before { content: "☐"; position: absolute; left: 4px;
  color: #6a737d; font-size: 14px; }
/* アラートボックス */
.alert { padding: 12px 16px; border-radius: 6px; margin: 12px 0;
  font-size: 13px; border-left: 4px solid; }
.alert-danger { background: #fff5f5; border-color: #dc3545; color: #721c24; }
.alert-warning { background: #fffbea; border-color: #ffc107; color: #856404; }
.alert-info { background: #e8f4fd; border-color: #0366d6; color: #084298; }
/* 信頼度バッジ */
.trust-high { color: #28a745; font-weight: 600; }
.trust-mid { color: #d97706; font-weight: 600; }
.trust-warn { color: #856404; font-weight: 600; }
.trust-miss { color: #dc3545; font-weight: 600; }
/* BC/CVE カード */
.card { border: 1px solid #e1e4e8; border-radius: 6px;
  padding: 16px; margin: 12px 0; }
.card-danger { border-left: 4px solid #dc3545; }
.card-warning { border-left: 4px solid #ffc107; }
.card-info { border-left: 4px solid #17a2b8; }
/* テスト優先度 */
.priority-must { color: #dc3545; font-weight: 700; }
.priority-rec { color: #d97706; font-weight: 700; }
.priority-reg { color: #28a745; font-weight: 700; }
/* フッター */
footer { text-align: center; color: #6a737d; font-size: 12px;
  padding: 24px; border-top: 1px solid #e1e4e8; margin-top: 20px; }
</style>
</head>
<body>

<div class="report-header">
  <h1>📊 バージョンアップ影響分析: {パッケージ名} v{From} → v{To}
    <span class="risk-badge risk-{high|mid|low}">{🔴 高 | 🟡 中 | 🟢 低}</span>
  </h1>
  <div class="meta">
    エコシステム: {エコシステム} ｜ 分析日: {YYYY-MM-DD HH:MM} ｜
    Breaking Changes: {N}件 ｜ CVE: {N}件
  </div>
</div>

<!-- 目次 -->
<div class="toc">
  <h2>📋 目次</h2>
  <ol>
    <li><a href="#summary">エグゼクティブサマリー</a></li>
    <li><a href="#meta">メタ情報</a></li>
    <li><a href="#risk">インシデントリスク評価</a></li>
    <li><a href="#breaking">Breaking Changes詳細</a></li>
    <li><a href="#security">セキュリティ分析</a></li>
    <li><a href="#codebase">コードベース影響箇所</a></li>
    <li><a href="#test">テスト戦略</a></li>
    <li><a href="#migration">マイグレーション手順</a></li>
    <li><a href="#checklist">インシデント防止チェックリスト</a></li>
    <li><a href="#transitive">推移的依存関係の影響</a></li>
    <li><a href="#features">新機能・改善点</a></li>
    <li><a href="#refs">参考情報</a></li>
  </ol>
</div>

<div class="content">
  <!-- 各セクションをMarkdownの内容に対応してHTMLで記述 -->
  <!-- セクション例: -->
  <section class="section" id="summary">
    <h2>1. エグゼクティブサマリー</h2>
    <!-- サマリーの内容 -->
  </section>

  <!-- ... 以降、MD各セクションをHTMLに変換 ... -->

  <section class="section" id="checklist">
    <h2>9. インシデント防止チェックリスト</h2>
    <h3>事前確認</h3>
    <ul class="checklist">
      <li>{チェック項目}</li>
    </ul>
    <!-- ... -->
  </section>
</div>

<footer>
  生成日: {YYYY-MM-DD} ｜ upgrade-analyzer v4.1 ｜ Claude Code
</footer>

</body>
</html>
```

上記テンプレートにレポートの全内容を変換して埋め込み、HTMLファイルを生成する。
リスクレベルに応じてバッジのクラスを `risk-high` / `risk-mid` / `risk-low` から選択する。

---

## フェーズ5: ファイル保存

### 5-1: 保存先の決定（優先順）

1. **プロジェクトパスが引数で指定されている場合**: `{プロジェクトパス}/reports/`
2. **プロジェクトパスが指定されていない場合**: `./reports/`（Claude Code を起動したカレントディレクトリ）

`reports/` ディレクトリが存在しない場合は作成する:
```bash
mkdir -p {保存先ディレクトリ}
```

### 5-2: MarkdownファイルとHTMLファイルの保存（必須）

**ベースファイル名**: `{パッケージ名}_{From}_to_{To}_{YYYYMMDD}_{HHMMSS}`

保存するファイル:
1. `{ベースファイル名}.md` — Markdownレポート
2. `{ベースファイル名}.html` — HTMLレポート（自己完結型）

各ファイルの冒頭に必ず以下を記載（Markdownの場合）:
```markdown
# バージョンアップ影響分析: {パッケージ名} v{From} → v{To}

**日付**: YYYY-MM-DD
```

既存ファイルは上書きせず、実行のたびに新しいファイルを生成する。

### 5-3: 完了報告

保存完了後、以下をユーザーに伝える:
```
保存しました:
  MD:   {フルパス}.md
  HTML: {フルパス}.html
```

---

## 精度向上のための注意事項

1. **changelog未整備パッケージへの対応**: リリースノートが不完全な場合は、GitHubの commit log (`/compare/v{From}...v{To}`) または公式サイトのブログ・リリースページから直接差分を調査する
2. **LLMの false negative 防止**: 「影響なし」と判断する場合は必ず根拠を明記し、使用箇所との照合を記録する
3. **間接依存の見落とし防止**: lock ファイル（package-lock.json / poetry.lock / Cargo.lock 等）で `resolved` バージョンを確認する
4. **semver の過信禁止**: patch バージョンでも設定系・バリデーション系パッケージは挙動が変わる事例あり。changelog を実際に読む
5. **プロジェクトパス未指定時の限界を明示**: コードベース分析なしの場合は「実コード影響は手動確認が必要」と明記する
6. **汎用ソフトウェアの一次情報**: 公式サイト・公式ドキュメントが最優先。ブログ・非公式サイトは二次情報として扱い、必ず公式ソースとの照合を行う
