# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

このリポジトリはコードを持たない**プロンプトのみのプロジェクト**。
`upgrade-analyzer.md` が Claude Code スラッシュコマンド定義の本体であり、あらゆるソフトウェア・パッケージのバージョンアップ影響分析を自動化する。
npm / PyPI / Go / Rust / RubyGems / Maven / Docker / 汎用ソフトウェアに対応し、Markdown・HTML（自己完結型・スクリプト変換）・JSON（機械可読サマリー）の3形式でレポートを生成する。
※ HTML変換用の `scripts/md_to_html.py` のみコードを持つ。

## スラッシュコマンドの登録

### プラグインインストール（推奨）

```bash
claude plugin add github:daigoarai/upgrade-analyzer-cc
/reload-plugins
```

`skills/upgrade-analyzer.md`（薄いラッパー）と `agents/upgrade-analyzer-agent.md`（実装本体）が同時に登録される。

### 手動登録（後方互換）

```bash
# グローバル登録（モノリシック版）
cp upgrade-analyzer.md ~/.claude/commands/upgrade-analyzer.md
```

登録後は `/upgrade-analyzer` で即使用可能。

## 使い方

```text
/upgrade-analyzer next 14.0.0 15.3.2
/upgrade-analyzer next 14.0.0 15.3.2 /path/to/project
/upgrade-analyzer django 4.2.0 5.1.0 /path/to/project "決済・認証機能に使用"
/upgrade-analyzer postgresql 14.0 16.0
/upgrade-analyzer terraform 1.5.0 1.9.0
```

## アーキテクチャ（upgrade-analyzer.md の構成）

`upgrade-analyzer.md` は6フェーズで構成される：

| フェーズ   | 内容                                                | 実行方式          |
| ------ | ------------------------------------------------- | ------------- |
| フェーズ0  | エコシステム自動判定（npm/PyPI/Go/Rust/Ruby/Maven/Docker/汎用）＋バージョン実在チェック | WebFetch順次    |
| フェーズ1  | 外部情報収集（changelog・マイグレーションガイド・codemod） / セキュリティ調査（OSV・GitHub Advisories・NVDの各JSON API） / コードベース解析（import＋設定ファイル検索・ベースライン静的解析・試験アップグレード） | **3エージェント並列** |
| フェーズ1b | MCP経由クロス検証（Codex）で信頼度ラベルを付与（追加BCは原文照合必須）         | オプション         |
| フェーズ2  | ハイブリッド影響分析（BC×コード使用箇所マッチング・Reachability判定・総合判定ルーブリック） | LLM推論         |
| フェーズ3  | テスト影響範囲の特定                                        | LLM推論         |
| フェーズ4  | Markdownレポート生成                                    | ファイル書き込み      |
| フェーズ5  | HTML変換（`scripts/md_to_html.py` 優先・未検出時LLMフォールバック）＋JSONサマリー生成＋保存前セルフチェック＋`reports/` 保存 | スクリプト実行＋ファイル書き込み |

### Agent C の対応言語

プロジェクトパス指定時に言語を自動検出し、言語別のimport検索と静的解析を実行する。

| 検出ファイル                                | 言語                   | 静的解析ツール                              |
| ------------------------------------- | -------------------- | ------------------------------------ |
| `package.json`                        | Node.js / TypeScript | `tsc --noEmit`                       |
| `requirements.txt` / `pyproject.toml` | Python               | `mypy`                               |
| `go.mod`                              | Go                   | `go vet`                             |
| `Cargo.toml`                          | Rust                 | `cargo check`                        |
| `pom.xml` / `build.gradle`            | Java / Kotlin        | `mvn compile` / `gradle compileJava` |
| `Gemfile`                             | Ruby                 | —                                    |
| `composer.json`                       | PHP                  | —                                    |

### クロス検証の信頼度ラベル

| ラベル             | 意味                               |
| --------------- | -------------------------------- |
| ✅ 高信頼           | Claude + Codex の両者が検出            |
| ⚠️ 要確認          | Claude のみ検出（単一ソース）               |
| 🔴 Agent A 見落とし | Codex のみ検出 **かつ changelog原文の引用照合OK** → BCリストに追加 |
| ❌ 不採用           | Codex のみ検出だが原文照合不可（ハルシネーション疑い）→ 参考情報に「未確認情報」として記録のみ |

## レポート保存先・命名規則

```text
reports/{パッケージ名}_{From}_to_{To}_{YYYYMMDD}_{HHMMSS}.md
reports/{パッケージ名}_{From}_to_{To}_{YYYYMMDD}_{HHMMSS}.html
reports/{パッケージ名}_{From}_to_{To}_{YYYYMMDD}_{HHMMSS}.json
例: reports/next_14.0.0_to_15.3.2_20260512_143022.md
    reports/next_14.0.0_to_15.3.2_20260512_143022.html
    reports/next_14.0.0_to_15.3.2_20260512_143022.json
```

プロジェクトパスを指定した場合は `{プロジェクトパス}/reports/` に保存される。
HTMLは自己完結型（外部CSS・JS参照なし）のため、オフラインでも閲覧可能。
JSONは機械可読サマリー（リスク・推奨度・BC/CVE件数等）で、複数パッケージの横断集計に使う。

## ファイル構成と役割

| ファイル                           | 役割                                           |
| ------------------------------ | -------------------------------------------- |
| `upgrade-analyzer.md`          | 実装本体（後方互換・手動コピー用モノリシック版）                     |
| `agents/upgrade-analyzer-agent.md` | プラグイン用エージェント本体（**upgrade-analyzer.md へのシンボリックリンク** — 本体を編集すれば自動で同期される）  |
| `skills/upgrade-analyzer.md`   | プラグイン用薄いラッパー（agents/ に委譲）                   |
| `scripts/md_to_html.py`        | MDレポート→自己完結型HTML変換スクリプト（標準ライブラリのみ・アンカー整合性検証付き） |
| `.claude-plugin/plugin.json`   | プラグインマニフェスト                                  |
| `.cursorrules`                 | 旧Cursor版（v3.x）の定義。参考用                        |
| `templates/report_template.md` | レポートの構造・セクション定義                              |
| `templates/prompt_template.md` | 旧Cursor版プロンプトテンプレート（参考用）                     |
| `examples/`                    | 実際に生成されたレポートのサンプル                            |
| `reports/`                     | 生成レポートの保存先（`.gitkeep` のみコミット）                |
| `docs/`                        | 旧設計書（Cursor時代のアーキテクチャ記述）                     |
| `docs-codex/`                  | Codexレビュー記録                                  |

## プロンプト修正時の注意点

- `agents/upgrade-analyzer-agent.md` は `upgrade-analyzer.md` へのシンボリックリンク。本体の編集だけで自動同期される（手動コピー不要）
- プラグイン利用者への配布: `git push` 後に `claude plugin update --all` で自動反映
- 手動コピー利用者への配布: `~/.claude/commands/upgrade-analyzer.md` へ再コピーが必要
- エコシステム判定・バージョン実在チェックはフェーズ0（`0-1` / `0-2` / `0-3`）に記述
- WebFetchリトライロジック（エラー種別分岐）・マイグレーションガイド検索・8000文字キャップ処理はフェーズ1 Agent A の `A-2` に記述
- セキュリティ調査のAPIエンドポイント（OSV/GitHub Advisories/NVD）はフェーズ1 Agent B の `B-1`〜`B-3` に記述
- 多言語対応のimport検索パターンは `C-2`、設定ファイル検索は `C-2b`、ベースライン静的解析は `C-6`、試験アップグレードは `C-7` に記述
- MCP検出ロジックはフェーズ1b の `1b-1` セクションに記述
- 信頼度ラベル付与ロジック（原文照合必須化を含む）はフェーズ2の `2-0` セクションに記述
- 総合判定ルーブリック（リスク・推奨度・コスト）はフェーズ2の `2-5` セクションに記述
- HTML生成は `scripts/md_to_html.py` が標準。スクリプトの固定CSSを変更する場合は、フェーズ4のフォールバック用HTMLテンプレートの `<style>` にも同じ変更を適用する（両者は同一テンプレートを維持）
- MDレポートのセクションは `## {番号}. {タイトル}` のH2構成が必須（変換スクリプトがH2単位で分割するため）。構成を変える場合は `templates/report_template.md`・`upgrade-analyzer.md` フェーズ4・`scripts/md_to_html.py` の `SECTION_ID_RULES` を整合させる

## MCP オプション設定（クロス検証機能）

```bash
# Codex プラグイン確認
ls ~/.claude/plugins/cache/openai-codex/

# 登録状況確認
claude mcp list
```

未登録でも動作する。クロス検証はスキップされ、フェーズ1bがスキップ扱いとなる。  
※ Gemini は公式 MCP サーバー未提供のため非対応。公式リリース後に追加予定。
