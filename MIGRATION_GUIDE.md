# Cursor版からCodex版への移行ガイド

## 1. 概要

### 1.1 移行の目的
このガイドでは、Upgrade-analyzerをCursor版からCodex版に移行する手順を説明します。

### 1.2 移行のメリット
- **柔軟性の向上**: JSON メタ情報とプロンプト本文の分離
- **保守性の向上**: 専用ファイルでの管理
- **拡張性の向上**: 新しいプロンプトファイル追加が容易
- **共有性の向上**: プロンプトファイルの共有が容易
- **標準性の向上**: Codex CLI標準形式

### 1.3 移行の前提条件
- Codex CLI最新版がインストールされている
- 既存のCursor版が動作している
- レポート履歴を保持したい

## 2. 移行手順

### 2.1 事前準備

#### 2.1.1 現在の状態の確認
```bash
# 現在のプロジェクト構造を確認
ls -la

# Cursor版の設定ファイルを確認
cat .cursorrules

# 既存のレポートを確認
ls -la reports/
```

#### 2.1.2 バックアップの作成
```bash
# プロジェクト全体のバックアップ
cp -r upgrade-analyzer upgrade-analyzer-backup-$(date +%Y%m%d)

# レポートのバックアップ
cp -r reports/ reports-backup-$(date +%Y%m%d)

# Git でのバックアップ
git add .
git commit -m "Backup before migration to Codex"
git push
```

### 2.2 Codex CLIのセットアップ

#### 2.2.1 Codex CLIのインストール
```bash
# Codex CLIのインストール（公式サイトから）
# https://codex.sh/ を参照

# インストール確認
codex --version
```

#### 2.2.2 Codex CLIの初期設定
```bash
# Codex CLIの初期設定
codex init

# 設定確認
codex status
```

### 2.3 プロンプトファイルの作成

#### 2.3.1 プロンプトファイルディレクトリの作成
```bash
# プロンプトファイルディレクトリの作成
mkdir -p prompts
```

#### 2.3.2 プロンプトファイルの作成
```bash
# プロンプトファイルの作成
touch prompts/upgrade-analyzer.md
```

#### 2.3.3 プロンプトファイルの内容設定
`prompts/upgrade-analyzer.md` に以下の内容を設定：

```json
{
  "name": "upgrade-analyzer",
  "description": "ソフトウェア製品のバージョンアップ影響分析レポートを生成",
  "argument_hint": "<製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]"
}
---
# プロンプト本文（.cursorrules の内容を移植）
...
```

### 2.4 設定の移行

#### 2.4.1 プロンプト内容の移行
1. `.cursorrules` の内容をコピー
2. `prompts/upgrade-analyzer.md` に貼り付け
3. JSON メタ情報を追加
4. プロンプト本文を `---` の後に配置

#### 2.4.2 メタ情報の分離
**Cursor版**:
```markdown
# Upgrade Analyzer - Cursor Rules

このプロジェクトは、ソフトウェアのバージョンアップ影響分析を自動化するツールです。

## カスタムコマンド

### /upgrade-analyzer

**説明**: ソフトウェア製品のバージョンアップ影響分析レポートを生成します。

**構文**:
```
/upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]
```
```

**Codex版**:
```json
{
  "name": "upgrade-analyzer",
  "description": "ソフトウェア製品のバージョンアップ影響分析レポートを生成",
  "argument_hint": "<製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]"
}
---
# プロンプト本文
```

#### 2.4.3 引数ヒントの分離
**Cursor版**:
```markdown
**引数**:
- `<製品名>`: アップグレード対象の製品名（必須）
- `<バージョンFrom>`: 現在のバージョン（必須）
- `<バージョンTo>`: アップグレード先のバージョン（必須）
- `[プロジェクト情報]`: プロジェクトの文脈・背景・目的・特性（オプション）
```

**Codex版**:
```json
{
  "argument_hint": "<製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]"
}
```

### 2.5 動作確認

#### 2.5.1 プロンプトファイルの確認
```bash
# プロンプトファイルの存在確認
ls -la prompts/upgrade-analyzer.md

# プロンプトファイルの内容確認
cat prompts/upgrade-analyzer.md
```

#### 2.5.2 Codex CLIでの確認
```bash
# Codex CLIを起動
codex

# スラッシュコマンドの確認
/prompts:upgrade-analyzer
```

#### 2.5.3 テスト実行
```bash
# テスト実行
/prompts:upgrade-analyzer Next.js 15.4 15.5.3

# レポート生成確認
ls -la reports/
```

### 2.6 移行完了

#### 2.6.1 移行確認
- [ ] Codex CLIが正常に動作する
- [ ] プロンプトファイルが正しく配置されている
- [ ] スラッシュコマンドが認識される
- [ ] レポートが正常に生成される
- [ ] ファイルが正常に保存される

#### 2.6.2 移行後のクリーンアップ
```bash
# 不要なファイルの削除（オプション）
# .cursorrules は保持することを推奨（両環境での併用のため）

# 移行完了の記録
echo "Migration completed on $(date)" >> MIGRATION_LOG.md
```

## 3. 移行時の注意点

### 3.1 コマンド名の変更

#### 3.1.1 変更内容
- **Cursor版**: `/upgrade-analyzer`
- **Codex版**: `/prompts:upgrade-analyzer`

#### 3.1.2 対応方法
- 新しいコマンド名を覚える
- チームメンバーに新しいコマンド名を共有
- ドキュメントを更新

### 3.2 ファイル構成の変更

#### 3.2.1 変更内容
- **Cursor版**: `.cursorrules` で管理
- **Codex版**: `prompts/upgrade-analyzer.md` で管理

#### 3.2.2 対応方法
- 新しいファイル構成を理解する
- プロンプトファイルの管理方法を習得
- バックアップ戦略を更新

### 3.3 メタ情報の分離

#### 3.3.1 変更内容
- **Cursor版**: プロンプト内に埋め込み
- **Codex版**: JSON メタ情報で分離

#### 3.3.2 対応方法
- JSON メタ情報の編集方法を習得
- プロンプト本文の編集方法を習得
- 両方の編集が必要になることを理解

### 3.4 引数ヒントの分離

#### 3.4.1 変更内容
- **Cursor版**: プロンプト内で記述
- **Codex版**: `argument_hint` フィールドで記述

#### 3.4.2 対応方法
- `argument_hint` フィールドの編集方法を習得
- 引数ヒントの更新方法を理解

## 4. 移行後の運用

### 4.1 プロンプトファイルの管理

#### 4.1.1 編集方法
```bash
# プロンプトファイルの編集
vim prompts/upgrade-analyzer.md

# メタ情報の編集
# JSON 部分を編集

# プロンプト本文の編集
# --- 以降を編集
```

#### 4.1.2 バージョン管理
```bash
# Git での管理
git add prompts/upgrade-analyzer.md
git commit -m "Update prompt file"
git push
```

### 4.2 レポートの管理

#### 4.2.1 レポートの確認
```bash
# レポートの一覧確認
ls -la reports/

# レポートの内容確認
cat reports/nextjs_15.4_to_15.5.3_20250128_143022.md
```

#### 4.2.2 レポートの整理
```bash
# 古いレポートのアーカイブ
mkdir -p archive/$(date +%Y%m)
mv reports/*_$(date +%Y%m)*.md archive/$(date +%Y%m)/

# レポートの検索
find reports/ -name "*nextjs*" -type f
```

### 4.3 チームでの運用

#### 4.3.1 プロンプトファイルの共有
```bash
# チーム共有リポジトリ
git clone https://github.com/team/upgrade-analyzer.git
cd upgrade-analyzer
ln -s prompts/upgrade-analyzer.md ~/.codex/prompts/
```

#### 4.3.2 レポートの共有
```bash
# 共有ディレクトリの設定
mkdir -p /shared/reports
ln -s /shared/reports reports

# 権限設定
chmod 755 /shared/reports
chgrp team /shared/reports
```

## 5. 両環境での併用

### 5.1 併用のメリット

#### 5.1.1 段階的移行
- 既存のワークフローを維持
- 新しい環境に慣れてから完全移行
- リスクの最小化

#### 5.1.2 柔軟性の向上
- 環境に応じた使い分け
- チームメンバーの習熟度に応じた選択
- プロジェクトの特性に応じた選択

### 5.2 併用の設定

#### 5.2.1 ファイル構成
```
upgrade-analyzer/
├── .cursorrules              # Cursor版設定
├── prompts/                  # Codex版設定
│   └── upgrade-analyzer.md
├── reports/                  # 共通レポート保存場所
├── docs/                     # Cursor版設計書
├── docs-codex/               # Codex版設計書
└── README.md
```

#### 5.2.2 使用方法
- **Cursor環境**: `/upgrade-analyzer` で実行
- **Codex環境**: `/prompts:upgrade-analyzer` で実行
- **レポート**: 両環境で同一の `reports/` フォルダを使用

### 5.3 同期方法

#### 5.3.1 プロンプト同期
```bash
# プロンプト内容の同期スクリプト
#!/bin/bash
# sync-prompts.sh

# Cursor版からCodex版への同期
cp .cursorrules temp_cursor.txt
# プロンプト部分を抽出してCodex版に適用
# （手動で実装が必要）

# Codex版からCursor版への同期
cp prompts/upgrade-analyzer.md temp_codex.txt
# プロンプト部分を抽出してCursor版に適用
# （手動で実装が必要）
```

#### 5.3.2 レポート同期
- レポートは同一の `reports/` フォルダに保存
- 両環境で同一のレポートを参照可能
- 履歴管理も共通

## 6. トラブルシューティング

### 6.1 移行時の問題

#### 6.1.1 プロンプトファイルが見つからない
**問題**: `プロンプトファイルが見つかりません` エラーが発生

**原因**: プロンプトファイルが正しい場所に配置されていない

**解決方法**:
```bash
# プロンプトファイルの存在確認
ls -la prompts/upgrade-analyzer.md

# 正しい場所に配置
mkdir -p prompts
cp upgrade-analyzer.md prompts/

# 権限確認
chmod 644 prompts/upgrade-analyzer.md
```

#### 6.1.2 JSON メタ情報の解析エラー
**問題**: `JSON メタ情報の解析に失敗しました` エラーが発生

**原因**: JSON メタ情報の形式が正しくない

**解決方法**:
```bash
# JSON メタ情報の確認
head -10 prompts/upgrade-analyzer.md

# 正しい形式に修正
{
  "name": "upgrade-analyzer",
  "description": "ソフトウェア製品のバージョンアップ影響分析レポートを生成",
  "argument_hint": "<製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]"
}
---
```

#### 6.1.3 コマンドが認識されない
**問題**: `/prompts:upgrade-analyzer` コマンドが認識されない

**原因**: プロンプトファイルの配置場所が間違っている

**解決方法**:
```bash
# プロンプトファイルの配置場所を確認
ls -la prompts/upgrade-analyzer.md
ls -la ~/.codex/prompts/upgrade-analyzer.md

# 正しい場所に配置
cp prompts/upgrade-analyzer.md ~/.codex/prompts/

# Codex CLIの再起動
codex restart
```

### 6.2 移行後の問題

#### 6.2.1 レポートが生成されない
**問題**: レポートが生成されない

**原因**: プロンプトファイルの内容に問題がある

**解決方法**:
```bash
# プロンプトファイルの内容確認
cat prompts/upgrade-analyzer.md

# 構文チェック
# JSON メタ情報の構文チェック
# プロンプト本文の確認
```

#### 6.2.2 ファイルが保存されない
**問題**: レポートファイルが保存されない

**原因**: 権限不足またはディスク容量不足

**解決方法**:
```bash
# 権限確認
ls -la reports/

# 権限修正
chmod 755 reports/

# ディスク容量確認
df -h
```

## 7. 移行チェックリスト

### 7.1 移行前の確認

- [ ] 現在のCursor版が正常に動作している
- [ ] 既存のレポートが保存されている
- [ ] プロジェクトのバックアップが作成されている
- [ ] チームメンバーに移行計画を共有している

### 7.2 移行中の確認

- [ ] Codex CLIがインストールされている
- [ ] プロンプトファイルが正しく作成されている
- [ ] JSON メタ情報が正しく設定されている
- [ ] プロンプト本文が正しく移植されている
- [ ] 引数ヒントが正しく設定されている

### 7.3 移行後の確認

- [ ] Codex CLIでスラッシュコマンドが認識される
- [ ] テスト実行が正常に完了する
- [ ] レポートが正常に生成される
- [ ] ファイルが正常に保存される
- [ ] 既存のレポートが参照できる
- [ ] チームメンバーが新しい環境を使用できる

### 7.4 移行完了後の確認

- [ ] 両環境での併用が可能
- [ ] プロンプトファイルの管理が可能
- [ ] レポートの管理が可能
- [ ] チームでの運用が可能
- [ ] トラブルシューティングが可能

## 8. 参考資料

### 8.1 公式ドキュメント
- [Codex CLI公式ドキュメント](https://codex.sh/)
- [Codex CLI スラッシュコマンド完全ガイド](https://qiita.com/nogataka/items/f4aa1aad77cbdf2c414c)

### 8.2 技術資料
- [セマンティックバージョニング](https://semver.org/)
- [Markdown記法](https://www.markdownguide.org/)
- [JSON形式](https://www.json.org/)

### 8.3 関連プロジェクト
- [Upgrade-analyzer GitHub](https://github.com/your-username/upgrade-analyzer)
- [設計書](docs-codex/README.md)
- [使用方法](CODEX_USAGE.md)

## 9. サポート

### 9.1 問題報告
- [GitHub Issues](https://github.com/your-username/upgrade-analyzer/issues)
- [GitHub Discussions](https://github.com/your-username/upgrade-analyzer/discussions)

### 9.2 機能要望
- [GitHub Discussions](https://github.com/your-username/upgrade-analyzer/discussions)
- [GitHub Issues](https://github.com/your-username/upgrade-analyzer/issues)

### 9.3 ドキュメント改善
- [GitHub Pull Requests](https://github.com/your-username/upgrade-analyzer/pulls)
- [GitHub Discussions](https://github.com/your-username/upgrade-analyzer/discussions)
