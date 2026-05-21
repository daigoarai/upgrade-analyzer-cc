# Upgrade Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-4.0-green.svg)](https://github.com/daigoarai/upgrade-analyzer-cc/releases)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet.svg)](https://claude.ai/code)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

> 🔍 ソフトウェアのバージョンアップ影響分析を自動化するツール  
> Claude Code のスラッシュコマンドで外部情報収集・コードベース静的解析・CVE調査を並列実行

---

## 概要

ライブラリ・フレームワークのバージョンアップ時に**インシデントを未然防止**するための影響分析ツールです。

**Claude Code** のサブエージェント並列実行を活用し、以下の3軸を同時に分析します:

| 軸      | 内容                                                  |
| ------ | --------------------------------------------------- |
| 外部情報   | 公式changelog・リリースノート・GitHub diff                     |
| セキュリティ | CVE/OSV/GitHub Security Advisories + Reachability判定 |
| 実コード分析 | プロジェクト内の使用箇所検索・言語別静的解析（TypeScript / Python / Go など） |

---

## 特徴

- **ハイブリッド分析**: changelog情報 × 実コード使用箇所のマッチングで「本当に壊れる箇所」を特定
- **並列実行**: 3つのサブエージェントが同時に調査（外部情報 / セキュリティ / コードベース）
- **外部LLMクロス検証**: MCP 経由で Codex（OpenAI）に同一changelogを渡し、結果を突合して Breaking Changes の信頼度を判定（MCP登録がない場合は自動スキップ）
- **Reachability判定**: 検出したCVEが自社コードで実際に使われているかを確認（false positive削減）
- **TypeScript静的チェック**: `tsc --noEmit` でコンパイルエラーを事前検出
- **WebFetchリトライ**: changelog取得失敗時に代替URLへ自動フォールバック（最大3回 + 代替URL）
- **間接依存の追跡**: `package-lock.json` / `yarn.lock` の transitive dependencies も調査
- **テスト影響範囲**: 影響ファイルに対応する具体的なテストファイルを列挙
- **インシデント防止チェックリスト**: リリース前の確認項目を自動生成

---

## セットアップ

### 前提条件

- ✅ **Claude Code** がインストール済み（`npm install -g @anthropic-ai/claude-code`）
- ✅ Claude Code のサブスクリプション（Pro/Teams/Enterprise）、または Anthropic API キーが設定されている

### インストール方法

GitHub にアクセスできる環境とできない環境で手順が異なります。

---

#### 方法A: プラグインインストール（GitHub アクセスあり）

`claude plugin update --all` で将来の更新も自動化できます。

**前提条件（Windows の場合）**: Git for Windows がインストールされ、SSH キーが設定されていること。未設定の場合は方法Bを使用してください。

**Mac / Linux:**

```bash
claude plugin add github:daigoarai/upgrade-analyzer-cc
```

**Windows（PowerShell / Git Bash）:**

```powershell
claude plugin add github:daigoarai/upgrade-analyzer-cc
```

その後 Claude Code を起動 → `/upgrade-analyzer` が使えます

---

#### 方法B: ZIP インストール（GitHub アクセスなし・Windows 推奨）

**① ZIP をダウンロードして解凍**

社内 Notion ページから `upgrade-analyzer-cc.zip` をダウンロードし、任意の場所に解凍します。

**② インストールスクリプトを実行**

| OS                                  | 手順                                             |
| ----------------------------------- | ---------------------------------------------- |
| **Mac / Linux**                     | ターミナルで `bash install.sh` を実行                   |
| **Windows（Git Bash / WSL）**         | ターミナルで `bash install.sh` を実行                   |
| **Windows（PowerShell / コマンドプロンプト）** | `install.bat` をダブルクリック、または `.\install.bat` を実行 |

**手動コピーの場合:**

| OS          | コピー元                  | コピー先                                                 |
| ----------- | --------------------- | ---------------------------------------------------- |
| Mac / Linux | `upgrade-analyzer.md` | `~/.claude/commands/upgrade-analyzer.md`             |
| Windows     | `upgrade-analyzer.md` | `%USERPROFILE%\.claude\commands\upgrade-analyzer.md` |

**③ Claude Code を起動** → `/upgrade-analyzer` が使えます

---

### アップデート方法

#### 方法A: プラグインアップデート（GitHub アクセスあり）

```bash
claude plugin update --all
```

#### 方法B: ZIP アップデート（GitHub アクセスなし）

新しい ZIP をダウンロードして解凍し、インストール手順を再実行してください。既存ファイルは上書きされます。

---

### MCP セットアップ（クロス検証機能 — 任意・推奨）

クロス検証機能は、**Claude Code に MCP 登録された Codex** を使います。  
現時点では Codex のみ対応しています（Gemini は公式 MCP サーバー未提供のため対象外）。

#### Codex（OpenAI）

Claude Code の **Codex プラグイン**をインストールすれば自動で使えます:

```bash
# Codex プラグインのインストール（未インストールの場合）
claude plugin install codex

# インストール確認
claude plugin list
```

インストール済みであれば追加設定は不要です。`/codex` または `codex:codex-rescue` サブエージェントとして動作します。

#### 登録状況の確認

```bash
claude mcp list
```

| 表示             | 状態               |
| -------------- | ---------------- |
| `codex` が含まれる行 | Codex MCP 使用可能   |
| 表示されない         | クロス検証スキップ（分析は続行） |

> **クロス検証なし（MCP未登録）でも動作します。** クロス検証は精度向上のオプション機能です。  
> MCP未登録の場合は自動的にスキップされ、Claude 単独で分析します。

---

## 使い方

### 基本構文

```text
/upgrade-analyzer <パッケージ名> <バージョンFrom> <バージョンTo> [プロジェクトパス] [補足情報]
```

エコシステムは自動判定されます。npm・Python・Go・Docker・汎用ソフトウェアなど何でも指定できます。

### 例: 外部情報のみ（プロジェクトパスなし）

```text
/upgrade-analyzer next 14.0.0 15.3.2
/upgrade-analyzer django 4.2.0 5.1.0
/upgrade-analyzer rails 7.0.0 7.2.0
/upgrade-analyzer golang 1.21 1.23
/upgrade-analyzer postgresql 14.0 16.0
/upgrade-analyzer terraform 1.5.0 1.9.0
/upgrade-analyzer nginx 1.24.0 1.26.0
```

### 例: 実コード分析 + 型チェック込み（プロジェクトパスあり）

```text
/upgrade-analyzer next 14.0.0 15.3.2 /Users/me/myapp
/upgrade-analyzer django 4.2.0 5.1.0 /Users/me/myproject
```

プロジェクトパスを指定すると:

- ソースコード配下の import / require 箇所を全検索
- 使用しているAPIを列挙
- Breaking Changes × 使用箇所を照合して「このファイルのこの行が壊れる」まで特定
- 言語に応じた静的解析（TypeScript: `tsc --noEmit` / Python: `mypy` / Go: `go vet` など）を実行

### 例: 補足情報付き

```text
/upgrade-analyzer next 14.0.0 15.3.2 /Users/me/myapp "決済・認証機能に使用、24h稼働"
/upgrade-analyzer django 4.2.0 5.1.0 /Users/me/myproject "基幹APIサーバー、週次バッチ処理あり"
```

---

## 生成されるレポートの構成

| セクション              | 内容                                                      |
| ------------------ | ------------------------------------------------------- |
| エグゼクティブサマリー        | 総合リスク評価・アップグレード推奨度（changelog取得失敗時は再実施警告を冒頭に表示）          |
| メタ情報               | 中間バージョン一覧・分析範囲・クロス検証実施状況・件数サマリー                         |
| インシデントリスク評価        | リスク種別×発生確率×影響度の表形式評価                                    |
| Breaking Changes詳細 | **信頼度ラベル付き**で全件記載（✅高信頼 / 🟡中信頼 / ⚠️要確認 / 🔴Agent A見落とし） |
| セキュリティ分析           | CVE詳細 + Reachability判定（使っているAPIか確認）                     |
| コードベース影響箇所一覧       | ファイル・使用API・Breaking Change影響・テストファイルの対応表                |
| テスト戦略              | 必須🔴 / 推奨🟡 / 回帰🟢 の優先度別テストファイル列挙                       |
| マイグレーション手順         | ファイル別・作業順の修正手順                                          |
| インシデント防止チェックリスト    | リリース前確認項目（コピー可）                                         |
| 推移的依存関係の影響         | 間接依存での変化                                                |
| 参考情報               | 調査URL一覧（発行日付き）                                          |

---

## レポートの保存先

| 状況               | 保存先                                       |
| ---------------- | ----------------------------------------- |
| プロジェクトパスを指定した場合  | `{プロジェクトパス}/reports/`                     |
| プロジェクトパスを指定しない場合 | `./reports/`（Claude Code を起動したカレントディレクトリ） |

`reports/` ディレクトリが存在しない場合は自動作成されます。

ファイル名: `{パッケージ名}_{From}_to_{To}_{YYYYMMDD}_{HHMMSS}.md`

例: `reports/next_14.0.0_to_15.3.2_20260507_143022.md`

> **Tips**: このリポジトリ内でレポートを管理したい場合は、upgrade-analyzer-cc ディレクトリで Claude Code を起動するか、プロジェクトパスに upgrade-analyzer-cc のパスを指定してください。

---

## 旧バージョン（Cursor版）との比較

| 観点     | v3.x (Cursor + Browser)     | v4.x (Claude Code)            |
| ------ | --------------------------- | ----------------------------- |
| 実行方法   | Cursor チャット + BrowserTab ON | `/upgrade-analyzer` スラッシュコマンド |
| コード分析  | なし（外部情報のみ）                  | プロジェクトパス指定でimport箇所全検索        |
| 実行方式   | 単一エージェント逐次                  | 3エージェント並列（高速化）                |
| セキュリティ | リリースノート記載分のみ                | CVE/OSV + Reachability判定      |
| 型チェック  | なし                          | `tsc --noEmit` 実行             |
| 間接依存   | 限定的                         | lock file解析で transitive 追跡    |
| セットアップ | BrowserTab の毎回ON設定が必要       | 初回コマンドコピーのみ                   |

---

## ディレクトリ構成

```text
upgrade-analyzer-cc/
├── .claude-plugin/
│   └── plugin.json            # プラグインマニフェスト
├── agents/
│   └── upgrade-analyzer-agent.md  # エージェント本体（プラグイン用）
├── skills/
│   └── upgrade-analyzer.md   # 薄いラッパー（プラグイン用エントリポイント）
├── upgrade-analyzer.md        # 実装本体（手動コピー向け後方互換）
├── README.md                  # このファイル
├── templates/
│   └── prompt_template.md    # 旧Cursor版プロンプトテンプレート（参考用）
├── examples/
│   └── nextjs_15_to_15.5.3.md # レポートサンプル
├── docs/                      # 設計書
├── docs-codex/                # Codexレビュー記録
└── reports/
    └── (生成されたレポートが保存される)
```

---

## 精度の限界と注意事項

1. **changelog未整備パッケージ**: リリースノートが不完全な場合、GitHubのcommit diffで補完するが精度は落ちる
2. **LLMのfalse negative**: 「影響なし」の誤判定があり得る。「影響なし」と判断した根拠を必ず確認すること
3. **プロジェクトパス未指定時**: 外部情報のみの分析となり、実コード影響は手動確認が必要
4. **semverへの過信禁止**: patchバージョンでも設定系・バリデーション系は挙動が変わる事例あり
5. **最終判断は人間が行う**: このツールはサポートツール。アップグレード可否の最終決定は開発者が行うこと

---

## 対応範囲

公式 changelog・リリースノート・GitHub releases が取得できるソフトウェアであれば**言語・エコシステムを問わず**対応します。  
第1引数にパッケージ名を渡すと、フェーズ0でエコシステムを自動判定します。

| エコシステム | 自動判定方法 | 例 |
| ---------- | ---------- | -- |
| **npm** (Node.js / TypeScript) | npmレジストリ確認 | next, react, axios, typescript |
| **PyPI** (Python) | PyPIレジストリ確認 | django, fastapi, boto3 |
| **crates.io** (Rust) | crates.io API確認 | tokio, serde, actix-web |
| **RubyGems** (Ruby) | RubyGems API確認 | rails, devise |
| **Go modules** | pkg.go.dev確認 | gin, echo |
| **Docker Hub** | Docker Hub API確認 | postgres, nginx, redis |
| **Maven Central** (Java / Kotlin) | Maven検索API確認 | spring-boot |
| **GitHub releases** | GitHub releases API | ツール・CLIなど |
| **汎用ソフトウェア** | Web検索で公式サイト・changelogを特定 | Terraform, Kubernetes, PostgreSQL など |

> パッケージ名に `/` が含まれる場合はGoモジュール、`:` が含まれる場合はMavenとして優先判定します。  
> changelog が公式に整備されていないパッケージは、GitHub commit diff で補完しますが精度は落ちます。

---

## コントリビューション

- 🐛 バグ報告: Issue を作成
- 💡 新機能提案: Issue で議論
- 📊 サンプルレポート追加: `examples/` に追加
- 📖 ドキュメント改善: Pull Request 歓迎

---

## ライセンス

[MIT License](./LICENSE)

---

## 更新履歴

- **2026-05-08 v4.1**: 外部LLMクロス検証機能を追加（MCP経由でCodexに依頼し信頼度ラベルを付与）。WebFetchリトライロジック強化（最大3回 + 代替URLフォールバック + 全失敗時ユーザー警告）
- **2026-05-07 v4.0**: Claude Code 対応に全面移行。3エージェント並列実行・実コードベース静的解析・CVE Reachability判定・TypeScript型チェック・インシデント防止チェックリストを追加
- **2025-11-11 v3.1**: 優先度の定義明確化、優先度設定の根拠明示
- **2025-10-08 v3.0**: Cursor + Browser機能を前提とした構成に変更
- **2025-10-03 v1.0**: 初版作成

---

## 免責事項

このツールは調査効率化のサポートツールです。レポートの完全性・正確性を保証するものではありません。
アップグレードの最終判断と実施責任は開発者にあります。
必ず公式ドキュメントとマイグレーションガイドを併せて確認してください。
