# Upgrade Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)](https://github.com/daigoarai/upgrade-analyzer/releases)
[![Cursor](https://img.shields.io/badge/Cursor-Latest-blueviolet.svg)](https://cursor.sh/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

> 🔍 ソフトウェアのバージョンアップ影響分析を自動化するツール  
> Cursor + Browser機能で公式情報を自動収集・分析

## 概要

このツールは、ソフトウェアライブラリ・フレームワークのバージョンアップ時の**影響範囲調査**と**テスト戦略立案**を効率化するためのフレームワークです。

**Cursor最新版 + Browser機能** を活用し、AIが公式情報を自動収集・分析します。

## 目的

- バージョンアップ時の見落としを防ぎ、インシデントリスクを低減
- **Browser機能**により一次情報（公式リリースノート、GitHub、セキュリティ通告）をリアルタイムで収集
- 再現可能で監査可能な調査プロセスの確立
- チーム内での知見共有とナレッジベース化

## 特徴

- 🔍 **体系的な差分分析**: Breaking Changes、バグ修正、機能追加を分類整理
- 🎯 **優先度付きテスト戦略**: 影響度に応じた3段階のテスト観点提示
- 📊 **リスクアセスメント**: 発生確率と影響度を考慮したリスク評価
- 🔗 **推移的依存関係チェック**: 依存の依存（3階層まで）の既知問題も調査
- 🌐 **クロスブラウザ互換性重視**: Windows/macOS/iOS/Android全プラットフォーム対応
  - 📱 モバイル: iOS Safari、Android Chrome、Samsung Internet
  - 💻 デスクトップ: Windows（Chrome、Edge、Firefox）、macOS（Safari、Chrome、Firefox）
  - 📲 タブレット: iPad、Androidタブレット
- 📚 **出典管理**: すべての情報に公式ソースのURL・日付を記載
- ♻️ **再利用可能**: テンプレート化されたプロンプトで任意のライブラリに適用可能

## ディレクトリ構成

```text
upgrade-analyzer/
├── .cursorrules                # スラッシュコマンド定義
├── README.md                    # このファイル
├── QUICKSTART.md               # クイックスタートガイド
├── USAGE_GUIDE.md              # 詳細な使用方法
├── SLASH_COMMAND_SETUP.md      # スラッシュコマンドセットアップガイド
├── templates/
│   ├── prompt_template.md      # 調査用プロンプトテンプレート
│   └── report_template.md      # レポート出力テンプレート
├── examples/
│   └── nextjs_15_to_15.5.3.md # 実例（Next.js）
└── reports/
    └── (調査結果を保存)
```

## ⚠️ 必須前提条件

- **Cursor 最新版** がインストール済み
- **Browser 機能が ON** になっている
- **`.cursorrules` ファイル** が配置済み（スラッシュコマンド使用時）

> 💡 詳細は [QUICKSTART.md](./QUICKSTART.md) を参照

## セットアップ

### 1. このリポジトリを入手

```bash
# Git経由で取得
git clone <repository-url> upgrade-analyzer

# または、ZIPでダウンロードして展開
# upgrade-analyzer ディレクトリに配置
```

### 2. スラッシュコマンドの設定（任意）

スラッシュコマンドを使いたい場合は、セットアップが必要です。

👉 **詳細は [SLASH_COMMAND_SETUP.md](./SLASH_COMMAND_SETUP.md) を参照**

### 3. 使用準備

特別なインストールは不要です。すぐに使い始められます。

```bash
cd upgrade-analyzer

# スラッシュコマンドを使う場合
# （このディレクトリ内では自動的に.cursorrulesが読み込まれます）

# プロンプトテンプレートを直接使う場合
open templates/prompt_template.md
```

## クイックスタート

### 方法1: スラッシュコマンド（推奨）

最も簡単な方法です。Cursorチャットで直接実行できます。

```text
/upgrade-analyzer Next.js 15.4 15.5.3
```

**構文**:

```text
/upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo> [プロジェクト情報]
```

**引数**:
- `<製品名>`: アップグレード対象の製品名（必須）
- `<バージョンFrom>`: 現在のバージョン（必須）
- `<バージョンTo>`: アップグレード先のバージョン（必須）
- `[プロジェクト情報]`: プロジェクトの文脈・背景・目的（オプション）

**実行例**:

```text
# 基本的な使用方法
/upgrade-analyzer Next.js 15.4 15.5.3
/upgrade-analyzer React 18.2.0 18.3.1
/upgrade-analyzer PostgreSQL 14.1 15.0

# プロジェクト情報を含めた使用方法（より具体的なレポートが生成されます）
/upgrade-analyzer Next.js 15.4 15.5.3 "Eコマースサイト、月間100万PV、決済機能が重要、SEOとパフォーマンスが最優先"

/upgrade-analyzer React 18.2.0 18.3.1 "社内の勤怠管理システム、認証とアクセス制御が重要、ダウンタイム許容度低"

/upgrade-analyzer PostgreSQL 14.1 15.0 "金融系SaaSのデータベース、トランザクション整合性とセキュリティが最重要、24時間365日稼働"
```

💡 **Tip**: プロジェクト情報を指定すると、そのプロジェクトに特化した影響分析・テスト観点・リスク評価が提供されます。

AIが自動的に公式情報を検索・分析し、プロジェクトに最適化されたレポートを生成します。

---

### 方法2: プロンプトテンプレート（従来方式）

プロンプトをカスタマイズしたい場合に使用します。

#### 1. プロンプトテンプレートを確認

```bash
open templates/prompt_template.md
```

#### 2. 「📋 調査プロンプト（ここからコピー）」から「（ここまでコピー）」をコピー

```text
製品名: Next.js
バージョンFrom: 15.4
バージョンTo: 15.5.3
```

#### 3. Cursorチャットに貼り付けて実行

Browser機能により、AIが自動的に公式情報を検索・分析します。

---

### 結果の保存

AIが生成したレポートを以下の形式で保存してください：

```bash
# 日付付きファイル名で保存
reports/{製品名}_{From}_to_{To}_{YYYYMMDD}.md

# 例
reports/nextjs_15.4_to_15.5.3_20251006.md
```

## 対応範囲

### 現在サポート

- JavaScript/TypeScript系: Next.js, React, Node.js, Express
- フレームワーク: Spring Boot, Django, Rails
- データベース: PostgreSQL, MySQL, MongoDB
- インフラ: Docker, Kubernetes
- ビルドツール: Webpack, Vite, Turbopack

### 今後追加予定

- クラウドサービス（AWS, GCP, Azure）
- モバイルフレームワーク（React Native, Flutter）
- 各種SaaSツール

## 利用シーン

1. **計画段階**: バージョンアップの影響範囲見積もり
2. **実装段階**: 具体的な修正箇所の特定
3. **テスト段階**: テストケース設計と優先度決定
4. **レビュー段階**: 変更内容のチーム共有

## 🔗 関連リンク

- [クイックスタートガイド](./QUICKSTART.md) - 5分で始める
- [使用ガイド](./USAGE_GUIDE.md) - 詳細な使い方
- [スラッシュコマンド設定](./SLASH_COMMAND_SETUP.md) - グローバル設定
- [GitHub公開セットアップ](./GITHUB_SETUP.md) - GitHub公開手順
- [コントリビューションガイド](./CONTRIBUTING.md) - 貢献方法
- [セキュリティポリシー](./SECURITY.md) - セキュリティ報告

## 🛠️ 関連ツール

- [impact-cli](../impact-cli/) - SBOM連携の自動化ツール（開発中）
- [testcase_generator](../testcase_generator/) - テストケース自動生成

## 🤝 コントリビューション

コントリビューションを歓迎します！詳細は [CONTRIBUTING.md](./CONTRIBUTING.md) をご覧ください。

### コントリビューター募集中

- 🐛 バグ報告
- 💡 新機能の提案
- 📖 ドキュメント改善
- 📊 サンプルレポートの追加
- 🌍 翻訳（英語版の作成）

## 📜 ライセンス

[MIT License](./LICENSE)

このプロジェクトはMITライセンスの下で公開されています。

## 更新履歴

- 2025-10-06 v3.1: **プロジェクトコンテキスト対応** - 第4引数でプロジェクト情報を指定可能に、より具体的でカスタマイズされたレポートを生成
- 2025-10-06 v3.0: **スラッシュコマンド対応** - `/upgrade-analyzer`コマンドでコピー&ペースト不要に、`.cursorrules`で簡単実行
- 2025-10-06 v2.5: **レポート構成の最適化** - 移行手順と振り返りテンプレートを削除し、影響分析とテスト戦略に特化
- 2025-10-03 v2.4: **クロスブラウザ互換性調査を全プラットフォームに拡充** - Windows/macOS/iOS/Android全対応、デスクトップ・モバイル・タブレット含む
- 2025-10-03 v2.3: **Markdownファイル出力を明示化** - レポートをそのままファイル保存できる形式で出力、ファイル名規則追加
- 2025-10-03 v2.2: 変数宣言方式に変更 - プロンプト先頭の【変数設定】だけ編集すればOK（本文編集不要で大幅に使いやすく）
- 2025-10-03 v2.1: 推移的依存関係の既知問題チェック機能追加、ブラウザ互換性調査強化
- 2025-10-03 v2.0: Cursor + Browser機能を前提とした構成に変更、プロンプトテンプレート改善
- 2025-10-03 v1.0: 初版作成、Next.js実例追加
