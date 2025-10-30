# Codex CLI 使用方法

## 1. 概要

### 1.1 このドキュメントについて
このドキュメントでは、Upgrade-analyzerをCodex CLI環境で使用する方法について説明します。

### 1.2 前提条件
- Codex CLI最新版がインストールされている
- インターネット接続がある
- プロンプトファイルが適切に配置されている

## 2. セットアップ

### 2.1 Codex CLIのインストール

#### 2.1.1 インストール方法
```bash
# Codex CLIのインストール（公式サイトから）
# https://codex.sh/ を参照

# インストール確認
codex --version
```

#### 2.1.2 初期設定
```bash
# Codex CLIの初期設定
codex init

# 設定確認
codex status
```

### 2.2 プロンプトファイルの配置

#### 2.2.1 配置場所
プロンプトファイルは以下のいずれかの場所に配置します：

**オプション1: プロジェクト内配置**
```
upgrade-analyzer/
├── prompts/
│   └── upgrade-analyzer.md
└── ...
```

**オプション2: グローバル配置**
```
~/.codex/prompts/
└── upgrade-analyzer.md
```

#### 2.2.2 プロンプトファイルの内容
`prompts/upgrade-analyzer.md` ファイルには以下の内容が含まれている必要があります：

```json
{
  "name": "upgrade-analyzer",
  "description": "ソフトウェア製品のバージョンアップ影響分析レポートを生成",
  "argument_hint": "<製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]"
}
---
# プロンプト本文
...
```

### 2.3 動作確認

#### 2.3.1 プロンプトファイルの確認
```bash
# プロンプトファイルの存在確認
ls -la prompts/upgrade-analyzer.md

# プロンプトファイルの内容確認
cat prompts/upgrade-analyzer.md
```

#### 2.3.2 Codex CLIでの確認
```bash
# Codex CLIを起動
codex

# スラッシュコマンドの確認
/prompts:upgrade-analyzer
```

## 3. 使用方法

### 3.1 基本的な使用方法

#### 3.1.1 コマンド形式
```
/prompts:upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]
```

#### 3.1.2 引数の説明

| 引数 | 型 | 必須 | 説明 | 例 |
|------|----|----|------|-----|
| 製品名 | string | 必須 | アップグレード対象の製品名 | `Next.js` |
| バージョンFrom | string | 必須 | 現在のバージョン | `15.4` |
| バージョンTo | string | 必須 | アップグレード先のバージョン | `15.5.3` |
| プロジェクト情報 | string | オプション | プロジェクトの文脈・背景・目的・特性 | `Eコマースサイト、月間100万PV` |

### 3.2 実行例

#### 3.2.1 基本実行
```bash
# Codex CLIを起動
codex

# 基本実行
/prompts:upgrade-analyzer Next.js 15.4 15.5.3
```

#### 3.2.2 プロジェクト情報付き実行
```bash
# プロジェクト情報付き実行
/prompts:upgrade-analyzer Next.js 15.4 15.5.3 "Eコマースサイト、月間100万PV、決済機能とカート機能が重要、SEOとパフォーマンスが最優先"
```

#### 3.2.3 複雑なプロジェクト情報付き実行
```bash
# 社内ツール
/prompts:upgrade-analyzer React 18.2.0 18.3.1 "社内の勤怠管理システム、認証とアクセス制御が重要、ダウンタイム許容度低"

# 金融系SaaS
/prompts:upgrade-analyzer PostgreSQL 14.1 15.0 "金融系SaaSのデータベース、トランザクション整合性とセキュリティが最重要、24時間365日稼働"

# 大規模モノリポ
/prompts:upgrade-analyzer TypeScript 5.0 5.3 "大規模なモノリポ構成、マイクロサービス30個以上、型安全性とビルド速度が重要"
```

### 3.3 実行結果

#### 3.3.1 レポート生成
実行が完了すると、以下のようなレポートが生成されます：

1. **メタ情報**: 調査日、リリース状況、中間バージョン一覧
2. **差分サマリ**: 総変更数、Breaking Changes数、セキュリティ修正数
3. **主要変更点**: Breaking Changes、セキュリティ修正、バグ修正、新機能追加
4. **依存関係の既知問題**: 推移的依存関係の既知問題
5. **影響範囲の詳細分析**: コード、設定ファイル、依存関係への影響
6. **テスト戦略・観点**: 優先度別・プラットフォーム別のテスト観点
7. **リスクアセスメント**: リスク項目ごとの評価
8. **成功基準とKPI**: 必須条件、推奨条件、KPI
9. **推奨アクションプラン**: 実装計画、優先順位
10. **参考情報・出典**: 公式リリースノートURL、マイグレーションガイドURL

#### 3.3.2 ファイル保存
レポートは自動的に `reports/` フォルダに保存されます：

```
reports/
├── nextjs_15.4_to_15.5.3_20250128_143022.md
├── react_18.2.0_to_18.3.1_20250128_150315.md
└── postgresql_14.1_to_15.0_20250128_161045.md
```

## 4. 高度な使用方法

### 4.1 プロンプトファイルのカスタマイズ

#### 4.1.1 メタ情報の変更
`prompts/upgrade-analyzer.md` のJSON メタ情報を編集：

```json
{
  "name": "upgrade-analyzer",
  "description": "カスタム説明文",
  "argument_hint": "カスタム引数ヒント"
}
```

#### 4.1.2 プロンプト本文の変更
プロンプト本文を編集して、分析内容をカスタマイズ：

```markdown
---
# カスタムプロンプト本文

## 1. 基本指示
- カスタム調査手順
- カスタム出力形式

## 2. 調査項目
- カスタム調査項目
- カスタム分析観点
...
```

### 4.2 複数プロンプトファイルの管理

#### 4.2.1 新しいプロンプトファイルの追加
```bash
# 新しいプロンプトファイルを作成
touch prompts/custom-analyzer.md

# 内容を編集
vim prompts/custom-analyzer.md
```

#### 4.2.2 プロンプトファイルの一覧確認
```bash
# プロンプトファイルの一覧確認
ls -la prompts/

# Codex CLIで確認
codex
/prompts:custom-analyzer
```

### 4.3 プロジェクト固有の設定

#### 4.3.1 プロジェクト別プロンプトファイル
```bash
# プロジェクト別のプロンプトファイル
prompts/
├── upgrade-analyzer.md          # 汎用版
├── upgrade-analyzer-ecommerce.md # Eコマース特化版
├── upgrade-analyzer-saas.md     # SaaS特化版
└── upgrade-analyzer-internal.md # 社内ツール特化版
```

#### 4.3.2 使用方法
```bash
# 汎用版
/prompts:upgrade-analyzer Next.js 15.4 15.5.3

# Eコマース特化版
/prompts:upgrade-analyzer-ecommerce Next.js 15.4 15.5.3

# SaaS特化版
/prompts:upgrade-analyzer-saas React 18.2.0 18.3.1
```

## 5. トラブルシューティング

### 5.1 よくある問題

#### 5.1.1 プロンプトファイルが見つからない
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

#### 5.1.2 JSON メタ情報の解析エラー
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

#### 5.1.3 インターネット接続エラー
**問題**: `インターネット接続を確認してください` エラーが発生

**原因**: インターネット接続の問題

**解決方法**:
```bash
# インターネット接続確認
ping google.com

# Codex CLIの再起動
codex restart

# プロキシ設定の確認
codex config
```

#### 5.1.4 ファイル保存エラー
**問題**: `ファイル保存に失敗しました` エラーが発生

**原因**: 権限不足またはディスク容量不足

**解決方法**:
```bash
# 権限確認
ls -la reports/

# 権限修正
chmod 755 reports/

# ディスク容量確認
df -h

# 古いファイルの削除
rm reports/old_*.md
```

### 5.2 デバッグ方法

#### 5.2.1 ログの確認
```bash
# Codex CLIのログ確認
codex logs

# 詳細ログの有効化
codex --verbose

# デバッグモードでの実行
codex --debug
```

#### 5.2.2 設定の確認
```bash
# 設定の確認
codex config

# プロンプトファイルの確認
codex prompts

# ステータスの確認
codex status
```

### 5.3 パフォーマンスの問題

#### 5.3.1 処理時間が長い
**問題**: レポート生成に時間がかかる

**原因**: 大量の情報収集や複雑な分析

**解決方法**:
- プロジェクト情報を簡潔にする
- 分析範囲を限定する
- プロンプトを最適化する

#### 5.3.2 メモリ使用量が多い
**問題**: メモリ使用量が多い

**原因**: 大量のデータ処理

**解決方法**:
- プロンプトを簡潔にする
- 分析項目を限定する
- バッチ処理に分割する

## 6. ベストプラクティス

### 6.1 プロンプトファイルの管理

#### 6.1.1 バージョン管理
```bash
# Git での管理
git add prompts/upgrade-analyzer.md
git commit -m "Update prompt file"
git push
```

#### 6.1.2 バックアップ
```bash
# プロンプトファイルのバックアップ
cp prompts/upgrade-analyzer.md prompts/upgrade-analyzer.md.backup

# 定期的なバックアップ
crontab -e
# 0 2 * * * cp -r prompts/ ~/backup/prompts-$(date +%Y%m%d)/
```

### 6.2 レポートの管理

#### 6.2.1 レポートの整理
```bash
# 古いレポートのアーカイブ
mkdir -p archive/$(date +%Y%m)
mv reports/*_$(date +%Y%m)*.md archive/$(date +%Y%m)/

# レポートの検索
find reports/ -name "*nextjs*" -type f
```

#### 6.2.2 レポートの共有
```bash
# レポートの共有
scp reports/nextjs_15.4_to_15.5.3_20250128_143022.md user@server:/shared/reports/

# レポートの同期
rsync -av reports/ user@server:/shared/reports/
```

### 6.3 チームでの利用

#### 6.3.1 プロンプトファイルの共有
```bash
# チーム共有リポジトリ
git clone https://github.com/team/upgrade-analyzer.git
cd upgrade-analyzer
ln -s prompts/upgrade-analyzer.md ~/.codex/prompts/
```

#### 6.3.2 レポートの共有
```bash
# 共有ディレクトリの設定
mkdir -p /shared/reports
ln -s /shared/reports reports

# 権限設定
chmod 755 /shared/reports
chgrp team /shared/reports
```

## 7. 参考資料

### 7.1 公式ドキュメント
- [Codex CLI公式ドキュメント](https://codex.sh/)
- [Codex CLI スラッシュコマンド完全ガイド](https://qiita.com/nogataka/items/f4aa1aad77cbdf2c414c)

### 7.2 技術資料
- [セマンティックバージョニング](https://semver.org/)
- [Markdown記法](https://www.markdownguide.org/)
- [JSON形式](https://www.json.org/)

### 7.3 関連プロジェクト
- [Upgrade-analyzer GitHub](https://github.com/your-username/upgrade-analyzer)
- [設計書](docs-codex/README.md)
- [移行ガイド](MIGRATION_GUIDE.md)

## 8. サポート

### 8.1 問題報告
- [GitHub Issues](https://github.com/your-username/upgrade-analyzer/issues)
- [GitHub Discussions](https://github.com/your-username/upgrade-analyzer/discussions)

### 8.2 機能要望
- [GitHub Discussions](https://github.com/your-username/upgrade-analyzer/discussions)
- [GitHub Issues](https://github.com/your-username/upgrade-analyzer/issues)

### 8.3 ドキュメント改善
- [GitHub Pull Requests](https://github.com/your-username/upgrade-analyzer/pulls)
- [GitHub Discussions](https://github.com/your-username/upgrade-analyzer/discussions)
