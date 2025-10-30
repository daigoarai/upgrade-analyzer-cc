# Upgrade Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-3.1-green.svg)](https://github.com/daigoarai/upgrade-analyzer/releases)
[![Cursor](https://img.shields.io/badge/Cursor-Latest-blueviolet.svg)](https://cursor.sh/)
[![Codex CLI](https://img.shields.io/badge/Codex%20CLI-Latest-green.svg)](https://codex.sh/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

> 🔍 ソフトウェアのバージョンアップ影響分析を自動化するツール  
> Cursor + Browser機能 / Codex CLI + Web検索機能で公式情報を自動収集・分析

---

## 📖 目次

- [概要](#概要)
- [特徴](#特徴)
- [セットアップ](#セットアップ)
- [使い方](#使い方)
  - [Cursor版](#cursor版)
  - [Codex CLI版](#codex-cli版)
- [実例](#実例)
- [Tips & トラブルシューティング](#tips--トラブルシューティング)
- [対応範囲](#対応範囲)
- [コントリビューション](#コントリビューション)
- [ライセンス](#ライセンス)

---

## 概要

このツールは、ソフトウェアライブラリ・フレームワークのバージョンアップ時の**影響範囲調査**と**テスト戦略立案**を効率化するためのツールです。

**Cursor + Browser機能** または **Codex CLI + Web検索機能**を活用し、AIが公式情報を自動収集・分析して、包括的なレポートを生成します。

### 目的

- バージョンアップ時の見落としを防ぎ、インシデントリスクを低減
- **Browser機能**（Cursor）または**Web検索機能**（Codex CLI）により一次情報（公式リリースノート、GitHub、セキュリティ通告）をリアルタイムで収集
- 再現可能で監査可能な調査プロセスの確立
- チーム内での知見共有とナレッジベース化

---

## 特徴

- 🔍 **体系的な差分分析**: Breaking Changes、バグ修正、機能追加を分類整理
- 🎯 **優先度付きテスト戦略**: 影響度に応じた3段階のテスト観点提示
- 📊 **リスクアセスメント**: 発生確率と影響度を考慮したリスク評価
- 🔗 **推移的依存関係チェック**: 依存の依存（3階層まで）の既知問題も調査
- 🌐 **クロスブラウザ互換性重視**: Windows/macOS/iOS/Android全プラットフォーム対応
- 📚 **出典管理**: すべての情報に公式ソースのURL・日付を記載
- 🎨 **プロジェクト最適化**: プロジェクト情報を指定すると、そのプロジェクトに特化した分析を提供

---

## セットアップ

### 対応環境

このツールは以下の2つの環境で使用できます：

- **Cursor版**: Cursor + Browser機能
- **Codex CLI版**: Codex CLI + Web検索機能

### Cursor版の前提条件

以下が揃っていることを確認してください：

- ✅ **Cursor 最新版** がインストール済み
- ✅ **Browser 機能が ON** になっている（実行の度、毎回確認下さい）

#### Browser機能の確認方法

**macOS の場合**:
1. Cursorを開く
2. メニューバーの「Cursor」→「基本設定」→「Cursor Setting」を選択
3. 「Tools & MCP」タブを選択
4. 「Browser Automation」が「Ready」になっていることを確認

**Windows の場合**:
1. Cursorを開く
2. メニューバーの「ファイル」→「設定」（または `Ctrl + ,`）を選択
3. 「Cursor Setting」を開く
4. 「Tools & MCP」タブを選択
5. 「Browser Automation」が「Ready」になっていることを確認

> 💡 **重要**: 実行の度に、毎回Browser機能がReadyになっているか確認してください

### Codex CLI版の前提条件

以下が揃っていることを確認してください：

- ✅ **Codex CLI 最新版** がインストール済み
- ✅ **インターネット接続** がある
- ✅ **プロンプトファイル** が適切に配置されている

#### Codex CLIのインストール

```bash
# Codex CLIのインストール（公式サイトから）
# https://codex.sh/ を参照

# インストール確認
codex --version

# 初期設定
codex init
```

---

### インストール

#### 方法1: Gitで取得

```bash
git clone https://github.com/daigoarai/upgrade-analyzer.git
cd upgrade-analyzer
```

#### 方法2: ZIPでダウンロード

1. [リリースページ](https://github.com/daigoarai/upgrade-analyzer/releases)からZIPをダウンロード
2. 展開して`upgrade-analyzer`ディレクトリに配置

これだけで準備完了です。特別なインストールは不要です。

---

## 使い方

### Cursor版

#### 基本的な使い方（推奨）

Cursorでこのプロジェクトを開き、チャットで以下のコマンドを実行するだけです：

```text
/upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo>
```

#### 実行例

```text
# シンプルな使い方
/upgrade-analyzer Next.js 15.4 15.5.3
/upgrade-analyzer React 18.2.0 18.3.1
/upgrade-analyzer PostgreSQL 14.1 15.0
/upgrade-analyzer TypeScript 5.0 5.3
```

### Codex CLI版

#### 基本的な使い方（推奨）

Codex CLIで以下のコマンドを実行するだけです：

```text
/prompts:upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo>
```

#### 実行例

```text
# シンプルな使い方
/prompts:upgrade-analyzer Next.js 15.4 15.5.3
/prompts:upgrade-analyzer React 18.2.0 18.3.1
/prompts:upgrade-analyzer PostgreSQL 14.1 15.0
/prompts:upgrade-analyzer TypeScript 5.0 5.3
```

#### セットアップ

1. **プロンプトファイルの配置**:
   ```bash
   # プロンプトファイルを配置
   mkdir -p prompts
   cp prompts/upgrade-analyzer.md ~/.codex/prompts/
   ```

2. **Codex CLIで確認**:
   ```bash
   # Codex CLIを起動
   codex
   
   # スラッシュコマンドの確認
   /prompts:upgrade-analyzer
   ```

詳細な使用方法は [CODEX_USAGE.md](./CODEX_USAGE.md) を参照してください。

---

## 共通の使い方

### 基本的な使い方（推奨）

Cursor版またはCodex CLI版で以下のコマンドを実行するだけです：

**Cursor版**:
```text
/upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo>
```

**Codex CLI版**:
```text
/prompts:upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo>
```

#### 実行例

```text
# シンプルな使い方
/upgrade-analyzer Next.js 15.4 15.5.3
/upgrade-analyzer React 18.2.0 18.3.1
/upgrade-analyzer PostgreSQL 14.1 15.0
/upgrade-analyzer TypeScript 5.0 5.3
```

AIが自動的に以下を実行します：

1. ✅ 公式リリースノートを検索
2. ✅ GitHub Issuesを調査（推移的依存関係含む）
3. ✅ セキュリティアドバイザリを確認
4. ✅ クロスブラウザ互換性を全プラットフォームで調査
5. ✅ 依存関係の既知問題を深掘り調査
6. ✅ 現在の日付を動的に取得してレポート生成
7. ✅ 完全なMarkdownレポートを生成
8. ✅ `reports/`ディレクトリに自動保存

**所要時間**: 約2-5分（依存関係の深掘り調査により若干延長）

---

### プロジェクト情報を指定した使い方（より具体的なレポート）

プロジェクトの特性を指定すると、より実践的で具体的なレポートが生成されます：

```text
/upgrade-analyzer <製品名> <バージョンFrom> <バージョンTo> "プロジェクト情報"
```

#### 実行例

```text
# Eコマースサイト
/upgrade-analyzer Next.js 15.4 15.5.3 "Eコマースサイト、月間100万PV、決済機能とカート機能が重要、SEOとパフォーマンスが最優先"

# 社内システム
/upgrade-analyzer React 18.2.0 18.3.1 "社内の勤怠管理システム、認証とアクセス制御が重要、ダウンタイム許容度低"

# 金融系SaaS
/upgrade-analyzer PostgreSQL 14.1 15.0 "金融系SaaSのデータベース、トランザクション整合性とセキュリティが最重要、24時間365日稼働、PCI-DSS準拠必須"

# 大規模モノリポ
/upgrade-analyzer TypeScript 5.0 5.3 "大規模なモノリポ構成、マイクロサービス30個以上、型安全性とビルド速度が重要"
```

#### プロジェクト情報を指定するメリット

- ✅ **カスタマイズされたリスク評価**: プロジェクトのビジネス要件に応じた評価
- ✅ **特化したテスト観点**: プロジェクトの重要機能に焦点を当てたテスト戦略
- ✅ **適切なKPI設定**: プロジェクトの目標に合わせた成功指標
- ✅ **実践的な推奨事項**: プロジェクト固有の実装計画

#### プロジェクト情報に含めると良い内容

- **プロジェクトタイプ**: Eコマース、SaaS、社内ツール、API等
- **規模**: トラフィック量、ユーザー数、データ量
- **重要機能**: ビジネスクリティカルな機能（決済、認証、データ処理等）
- **優先事項**: パフォーマンス、セキュリティ、SEO、可用性等
- **制約条件**: ダウンタイム許容度、コンプライアンス要件

---

### カスタマイズ方法（上級者向け）

プロンプトをカスタマイズしたい場合は、テンプレートを直接編集できます：

#### Step 1: テンプレートを開く

```bash
open templates/prompt_template.md
```

#### Step 2: 【変数設定】を編集

プロンプトの先頭にある3行だけを編集します：

```text
---
【変数設定】
製品名: Next.js          ← ここに製品名を入力
バージョンFrom: 15.4     ← ここに現在のバージョンを入力
バージョンTo: 15.5.3     ← ここにアップグレード先のバージョンを入力
---
```

それ以外の本文は変更不要です。

#### Step 3: Cursorチャットに貼り付けて実行

編集したプロンプト全体をコピーして、Cursorチャットに貼り付けて実行します。

---

## 実例

実際の調査結果を確認できます：

```bash
# Next.jsの実例を確認
cat examples/nextjs_15_to_15.5.3.md
```

このファイルには以下が含まれています：

- 詳細な変更点の分類
- 優先度付きテスト観点
- 具体的な検証コマンド
- リスク評価と対応策
- 成功基準とKPI

---

## Tips & トラブルシューティング

### 💡 使い方のヒント

#### 1. レポートの保存場所

生成されたレポートは`reports/`ディレクトリに以下の形式で保存されます：

```
reports/{製品名}_{バージョンFrom}_to_{バージョンTo}_{YYYYMMDD}.md
```

例：`reports/nextjs_15.4_to_15.5.3_20251008.md`

#### 2. 全プロジェクトで使う方法

このプロジェクト以外でもコマンドを使いたい場合：

1. Cursor設定を開く（macOS: `Cmd + ,` / Windows: `Ctrl + ,`）
2. 「General」→「Rules for AI」を選択
3. `.cursorrules`ファイルの内容をコピー＆ペースト
4. 保存して閉じる

これで全プロジェクトで`/upgrade-analyzer`コマンドが使えます。

#### 3. レポートの活用方法

生成されたレポートは以下の用途で活用できます：

- **計画段階**: バージョンアップの影響範囲見積もり
- **実装段階**: 具体的な修正箇所の特定
- **テスト段階**: テストケース設計と優先度決定
- **レビュー段階**: 変更内容のチーム共有
- **ドキュメント**: 履歴として保存・参照

#### 4. 複数バージョンの比較

大きなバージョンアップの場合は、段階的に分析することをおすすめします：

```text
# 例：Next.js 14 → 15.5.3の場合
/upgrade-analyzer Next.js 14.0 15.0 "プロジェクト情報"
/upgrade-analyzer Next.js 15.0 15.5.3 "プロジェクト情報"
```

---

### 🔧 トラブルシューティング

#### コマンドが認識されない

**解決方法**:
1. Cursorを再起動してください
2. `.cursorrules`ファイルがプロジェクトルートにあることを確認
3. Cursorで`upgrade-analyzer`ディレクトリを開いていることを確認

#### Browser機能が動かない

**解決方法**:
1. Cursor設定で「Browser」機能がONになっているか確認
2. Cursorを最新版にアップデート
3. Cursorを再起動

#### レポートが生成されない

**解決方法**:
1. 製品名とバージョン番号が正しいか確認
2. インターネット接続を確認
3. 数分待ってから再度試す（タイムアウトの可能性）

#### プロジェクト情報が反映されない

**解決方法**:
1. プロジェクト情報を`""`で囲んでいるか確認
2. 情報が具体的か確認（例：「Webサイト」ではなく「Eコマースサイト、月間100万PV」）

#### エラーが発生する

**解決方法**:
1. Cursorのエラーメッセージを確認
2. バージョン番号の形式を確認（例：`18.2.0`）
3. 特殊文字が含まれていないか確認

---

### 📊 レポートの読み方

生成されたレポートには以下のセクションが含まれます：

1. **メタ情報**: 調査日、バージョン分類、重要度
2. **プロジェクト概要**（指定した場合）: プロジェクト特性の要約
3. **差分サマリ**: プロジェクトへの影響度評価
4. **主要変更点**: Breaking Changes、セキュリティ修正、バグ修正等
5. **依存関係の既知問題**: ブラウザ互換性を含む既知の問題
6. **影響範囲の詳細分析**: コード、設定、ビルド、実行環境への影響
7. **テスト戦略**: 優先度別・プラットフォーム別のテスト観点
8. **リスクアセスメント**: リスク項目と対応策
9. **成功基準とKPI**: 測定可能な指標
10. **推奨アクションプラン**: 段階的な実施計画
11. **参考情報**: 公式リンクとドキュメント

#### 優先度の見方

- 🔴 **高**: 必須対応、ビジネスクリティカル
- 🟡 **中**: 推奨対応、計画的に実施
- 🟢 **低**: 将来的に検討、影響は限定的

---

## 対応範囲

### 現在サポート

- **JavaScript/TypeScript系**: Next.js, React, Node.js, Express
- **フレームワーク**: Spring Boot, Django, Rails
- **データベース**: PostgreSQL, MySQL, MongoDB
- **インフラ**: Docker, Kubernetes
- **ビルドツール**: Webpack, Vite, Turbopack

### 今後追加予定

- クラウドサービス（AWS, GCP, Azure）
- モバイルフレームワーク（React Native, Flutter）
- 各種SaaSツール

実際には、**公式情報が取得できる任意のソフトウェア**に対応可能です。

---

## ディレクトリ構成

```text
upgrade-analyzer/
├── .cursorrules              # Cursor版スラッシュコマンド定義
├── prompts/                  # Codex CLI版プロンプトファイル
│   └── upgrade-analyzer.md  # メインプロンプトファイル
├── README.md                  # このファイル
├── CODEX_USAGE.md            # Codex CLI使用方法
├── MIGRATION_GUIDE.md        # 移行ガイド
├── templates/
│   ├── prompt_template.md    # 調査用プロンプトテンプレート
│   └── report_template.md    # レポート出力テンプレート
├── examples/
│   └── nextjs_15_to_15.5.3.md # 実例（Next.js）
├── docs/                     # Cursor版設計書
├── docs-codex/               # Codex版設計書
└── reports/
    └── (調査結果を保存)
```

---

## コントリビューション

コントリビューションを歓迎します！

### 貢献方法

- 🐛 **バグ報告**: Issueを作成
- 💡 **新機能の提案**: Issueで議論
- 📖 **ドキュメント改善**: Pull Request歓迎
- 📊 **サンプルレポートの追加**: `examples/`に追加
- 🌍 **翻訳**: 英語版の作成など

詳細は [CONTRIBUTING.md](./CONTRIBUTING.md) をご覧ください。

---

## 🔗 関連リンク

- [GitHub公開セットアップ](./GITHUB_SETUP.md) - GitHub公開手順
- [コントリビューションガイド](./CONTRIBUTING.md) - 貢献方法
- [セキュリティポリシー](./SECURITY.md) - セキュリティ報告
- [Codex CLI使用方法](./CODEX_USAGE.md) - Codex CLI版の詳細な使用方法
- [移行ガイド](./MIGRATION_GUIDE.md) - Cursor版からCodex版への移行手順
- [Codex版設計書](./docs-codex/README.md) - Codex版の詳細な設計書

---

## ライセンス

[MIT License](./LICENSE)

このプロジェクトはMITライセンスの下で公開されています。

---

## 更新履歴

- **2025-01-28 v4.0**: Codex CLI対応 - Codex CLI版を追加、両環境での利用が可能に
- **2025-10-08 v3.2**: ドキュメント統合 - README.mdに全情報を集約、より分かりやすく
- **2025-10-06 v3.1**: プロジェクトコンテキスト対応 - 第4引数でプロジェクト情報を指定可能に
- **2025-10-06 v3.0**: スラッシュコマンド対応 - `/upgrade-analyzer`コマンドで実行可能に
- **2025-10-06 v2.5**: レポート構成の最適化 - 影響分析とテスト戦略に特化
- **2025-10-03 v2.4**: クロスブラウザ互換性調査を全プラットフォームに拡充
- **2025-10-03 v2.3**: Markdownファイル出力を明示化
- **2025-10-03 v2.2**: 変数宣言方式に変更
- **2025-10-03 v2.1**: 推移的依存関係の既知問題チェック機能追加
- **2025-10-03 v2.0**: Cursor + Browser機能を前提とした構成に変更
- **2025-10-03 v1.0**: 初版作成

---

## ⚠️ 免責事項

**重要**: このツールは**サポートツール**であり、完全な調査の代替ではありません。

### このツールの位置づけ

- ✅ **補助ツール**: 調査作業を効率化し、見落としを防ぐ
- ✅ **参考情報**: 公式情報を基にした分析レポートの提供
- ✅ **効率化**: 手動調査の時間を大幅短縮

### このツールでは代替できないもの

- ❌ **完全な調査**: プロジェクト固有の詳細な影響分析
- ❌ **最終判断**: アップグレードの可否決定
- ❌ **責任**: アップグレード実施による問題への責任
- ❌ **保証**: レポートの完全性・正確性の保証

### 推奨される使用フロー

1. **このツールで概要把握** → レポートを確認
2. **公式ドキュメントの詳細確認** → マイグレーションガイド等を精読
3. **プロジェクト固有の調査** → 独自のテスト・検証を実施
4. **段階的なアップグレード** → 開発環境 → ステージング → 本番環境
5. **継続的な監視** → アップグレード後の動作確認

### 責任の所在

- **開発者**: 最終的なアップグレード判断と実施
- **このツール**: 調査効率化のサポートのみ
- **公式ドキュメント**: 正確な技術情報の提供

**このツールを使用する前に、必ず公式ドキュメントとマイグレーションガイドを確認してください。**

---

## 💬 サポート

質問やフィードバックがある場合は、[Issue](https://github.com/daigoarai/upgrade-analyzer/issues)を作成してください。

---

**最終更新**: 2025-01-28
