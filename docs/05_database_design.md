# Upgrade-analyzer データベース設計書

## 1. 概要

### 1.1 設計の目的
Upgrade-analyzerのデータ管理仕様を定義し、開発・運用・保守の指針を提供する。

### 1.2 設計の範囲
- ファイルベースデータ管理
- データ構造設計
- データアクセス仕様
- データ整合性仕様

### 1.3 重要な注意事項
**重要**: このツールは従来のデータベース（RDBMS、NoSQL等）を使用せず、ファイルシステムベースでデータを管理します。

## 2. データ管理アーキテクチャ

### 2.1 データ管理方式
- **方式**: ファイルベースデータ管理
- **ストレージ**: ローカルファイルシステム
- **形式**: Markdown、テキストファイル
- **アクセス**: ファイルI/O操作

### 2.2 データ管理の特徴
- **シンプル**: 複雑なデータベース設定不要
- **軽量**: 最小限のリソース使用
- **可読性**: 人間が読みやすい形式
- **バージョン管理**: Git等での履歴管理可能

## 3. データ構造設計

### 3.1 ディレクトリ構造

#### 3.1.1 全体構造
```
upgrade-analyzer/
├── .cursorrules              # 設定ファイル
├── README.md                 # プロジェクト説明
├── templates/                # テンプレートディレクトリ
│   ├── prompt_template.md    # プロンプトテンプレート
│   └── report_template.md    # レポートテンプレート
├── reports/                  # レポート保存ディレクトリ
│   ├── nextjs_15.4_to_15.5.3_20250128_143022.md
│   ├── react_18.2.0_to_18.3.1_20250128_150315.md
│   └── ...
├── examples/                 # 実例レポートディレクトリ
│   ├── nextjs_15_to_15.5.3.md
│   └── ...
└── docs/                     # 設計書・ドキュメントディレクトリ
    ├── 01_requirements.md
    ├── 02_system_architecture.md
    ├── 03_detailed_design.md
    ├── 04_api_specification.md
    ├── 05_database_design.md
    └── README.md
```

#### 3.1.2 ディレクトリの役割

| ディレクトリ | 役割 | 内容 | アクセス権限 |
|-------------|------|------|-------------|
| `templates/` | テンプレート管理 | プロンプト・レポートテンプレート | 読み取り専用 |
| `reports/` | レポート保存 | 生成されたレポートファイル | 読み書き可能 |
| `examples/` | 実例管理 | サンプルレポート | 読み取り専用 |
| `docs/` | ドキュメント管理 | 設計書・仕様書 | 読み取り専用 |

### 3.2 ファイル構造

#### 3.2.1 レポートファイル構造
```markdown
# {製品名} {バージョンFrom} → {バージョンTo} バージョンアップ影響分析レポート

## メタ情報
| 項目 | 内容 |
|------|------|
| **調査日** | 2025-01-28 |
| **製品名** | Next.js |
| **現行バージョン** | 15.4 |
| **移行先バージョン** | 15.5.3 |
| **セマンティックバージョン** | PATCH |
| **重要度** | 中 |

## 🔍 差分サマリ
| バージョン範囲 | 分類 | 重要度 | 主な変更内容 |
|---------------|------|--------|-------------|
| 15.4 → 15.5.3 | PATCH | 中 | バグ修正、セキュリティ修正 |

## 📋 主要変更点（分類別）
### 1. ⚠️ Breaking Changes（互換性破壊）
### 2. 🔒 セキュリティ修正
### 3. 🐛 バグ修正
### 4. 🚀 新機能追加
### 5. 📈 パフォーマンス改善
### 6. ⏰ 廃止予定機能（Deprecation）
### 7. 🔗 依存関係の既知問題

## 🎯 テスト戦略・観点
### 🔴 高優先度テスト（必須）
### 🟡 中優先度テスト（推奨）
### 🟢 基本テスト

## 🚨 リスクアセスメント
| リスク項目 | 発生確率 | 影響度 | 対応策 | 担当 |
|-----------|---------|--------|--------|------|
| 互換性問題 | 中 | 中 | テスト実施 | 開発チーム |

## 📊 成功基準
### 必須条件
### 推奨条件
### KPI

## 📚 参考情報・出典
### 公式ドキュメント
### コミュニティ
```

#### 3.2.2 テンプレートファイル構造
```markdown
# バージョンアップ影響調査プロンプトテンプレート

## ⚠️ 必須前提条件
このプロンプトテンプレートは、**Cursor最新版 + Browser機能ON** での使用を前提としています。

### 事前準備チェックリスト
- [ ] **Cursorを最新版にアップデート済み**
- [ ] **Browser機能がON** になっている（Settings → Tools & Integrations → Browser Automationで確認）
- [ ] **チャット欄の「＋Browser」がON** になっている
- [ ] バージョンアップ対象の製品名とバージョン番号を把握済み

---

## 📋 調査プロンプト（ここからコピー）

```
あなたは、ソフトウェアのバージョンアップ影響分析の専門家です。
公式リリースノート、GitHub、セキュリティアドバイザリなどの一次情報をBrowser機能で調査し、正確で実用的なレポートを作成してください。

---
【変数設定】※ここだけ編集してください
製品名: {製品名}
バージョンFrom: {バージョンFrom}
バージョンTo: {バージョンTo}
---

## 調査対象
上記の製品について、バージョンFrom から バージョンTo へのバージョンアップを予定しています。

## 調査項目
以下の観点で網羅的に調査してください：

### 1. メタ情報
- **調査日**: 現在の日付を動的に取得（YYYY-MM-DD形式）
- **リリース状況確認**: 指定バージョンのリリース状況（リリース済み/未リリース/最新バージョン）
- **中間バージョン一覧**: FromとToの間にある全バージョンのリスト
- **セマンティックバージョン分類**: MAJOR/MINOR/PATCHの判定
- **重要度**: 高/中/低（プロジェクトコンテキストを考慮）

### 2. 差分サマリ
- **バージョン範囲**: From → To の全バージョン
- **総変更数**: 全バージョンでの累積変更数
- **Breaking Changes数**: 互換性破壊の変更数
- **セキュリティ修正数**: CVE修正の数
- **新機能数**: 追加された機能の数
- **バグ修正数**: 修正されたバグの数

### 3. 主要変更点の分類
- **Breaking Changes**（互換性破壊）- コード例付き
- **セキュリティ修正**（CVE番号、重要度、影響範囲）
- **バグ修正**（特に重要なもの）
- **新機能追加**
- **パフォーマンス改善**（ベンチマーク結果があれば）
- **廃止予定機能**（Deprecation）- 代替方法付き

### 4. 影響範囲の特定
- コードへの影響（API変更、関数シグネチャ変更）
- 設定ファイルへの影響（config変更）
- 依存関係への影響（peer dependencies）
- ビルドプロセスへの影響
- 実行環境への影響（Node.jsバージョンなど）
- **クロスブラウザ互換性**（全プラットフォーム対応）
  - **デスクトップ**: Windows（Chrome、Firefox、Edge）、macOS（Chrome、Firefox、Safari、Edge）
  - **モバイル**: iOS（Safari、Chrome）、Android（Chrome、Firefox、Samsung Internet）
  - 古いブラウザバージョンでの動作（特にモバイル）

### 5. テスト戦略（優先度別）
- 🔴 **高優先度テスト**（必須検証項目）
- 🟡 **中優先度テスト**（推奨検証項目）
- 🟢 **基本テスト**（回帰テスト等）

### 6. リスクアセスメント
- リスク項目ごとに発生確率・影響度・対応策を表形式で整理
- リスク軽減戦略

### 7. 成功基準
- 必須条件
- 推奨条件
- KPI（測定可能な指標）

### 8. 依存関係の既知問題（重要）
以下の観点で**推移的依存関係（依存の依存）も含めて**調査してください：
- **主要な依存モジュールのGitHub Issues**を確認（特にOpen Issues）
- 依存モジュールの3階層程度まで掘り下げて既知問題を調査
- **クロスブラウザ互換性の問題**（全プラットフォーム）
- JavaScript/CSS の互換性問題
- ポリフィルの必要性（core-js、whatwg-fetch等）
- バンドルサイズへの影響

### 9. 参考情報（必須）
- 公式リリースノートURL（発行日付き）
- マイグレーションガイドURL
- セキュリティアドバイザリURL
- GitHub Release URL
- **依存モジュールの既知問題URL**（該当する場合）

## アウトプット形式

**⚠️ 重要**: 調査結果を以下の形式の**Markdownファイルとして出力**してください。

### 必須要素
1. **視覚的な整理**: 表形式、絵文字（🔴🟡🟢⚠️🚀📊等）を活用
2. **具体性**: コマンド例、コードスニペット、URL、日付を必ず含める
3. **優先度明示**: 重要度が一目でわかるように（🔴高🟡中🟢低）
4. **実行可能**: すぐにテスト・実装に移れるレベルの具体性
5. **出典明記**: すべての情報源にURLと発行日を記載
6. **コピー可能**: コードブロックには言語指定（bash, typescript等）

### レポート構成
以下のセクションを含めてください：

1. **メタ情報**（表形式）
2. 差分サマリ
3. 主要変更点（分類別）
4. **依存関係の既知問題**（⚠️**全プラットフォームのブラウザ互換性**含む）
5. テスト戦略・観点（優先度別・プラットフォーム別）
6. リスクアセスメント（表形式）
7. 成功基準とKPI
8. 参考情報・出典（Can I Useなどの互換性情報含む）

### 保存ファイル名の推奨
```
# 基本形式（実行のたびに新しいファイル）
{製品名}_{バージョンFrom}_to_{バージョンTo}_{YYYYMMDD}_{HHMMSS}.md

例:
- nextjs_15.4_to_15.5.3_20251003_143022.md
- laravel_11.7.0_to_12.3.0_20251028_150315.md

# 重要: 既存ファイルは上書きせず、実行のたびに新しいファイルを生成
```

### 重要：ファイル生成と保存

**必ず以下の形式で出力してください**:

1. **完全なMarkdownレポートを生成**し、**必ず自動的にファイルとして保存**
2. レポートは**チームメンバーが読んで即座に行動できる実用的な内容**にする
3. すべての情報（メタ情報、差分、テスト戦略、リスク評価等）を**一つのMarkdownファイル**にまとめる
4. **必須**: レポート生成後、`reports/[ファイル名].md`として**自動的に新しいファイルで保存**
5. **重要**: 既存ファイルは上書きせず、実行のたびに新しいファイルを生成
6. **完了**: ファイル保存完了を確認し、ファイルパスを報告
7. **検証**: レポートの品質チェック（網羅性、正確性、実用性）を実施
```

**（ここまでコピー）**
```

## 4. データモデル設計

### 4.1 レポートデータモデル

#### 4.1.1 レポートエンティティ
```yaml
Report:
  id: string                    # ファイル名（例: nextjs_15.4_to_15.5.3_20250128_143022）
  product_name: string          # 製品名（例: Next.js）
  version_from: string          # 現在のバージョン（例: 15.4）
  version_to: string            # アップグレード先のバージョン（例: 15.5.3）
  project_context: string       # プロジェクト情報（オプション）
  investigation_date: date      # 調査日（例: 2025-01-28）
  file_path: string             # ファイルパス（例: reports/nextjs_15.4_to_15.5.3_20250128_143022.md）
  file_size: number             # ファイルサイズ（バイト）
  created_at: datetime          # 作成日時
  updated_at: datetime          # 更新日時
  content: string               # レポート内容（Markdown形式）
```

#### 4.1.2 メタ情報エンティティ
```yaml
MetaInfo:
  report_id: string             # レポートID
  investigation_date: date      # 調査日
  product_name: string          # 製品名
  version_from: string          # 現在のバージョン
  version_to: string            # アップグレード先のバージョン
  semantic_version: string      # セマンティックバージョン（MAJOR/MINOR/PATCH）
  importance: string            # 重要度（高/中/低）
  release_status: string        # リリース状況（リリース済み/未リリース/最新バージョン）
  intermediate_versions: array  # 中間バージョン一覧
```

#### 4.1.3 差分サマリエンティティ
```yaml
DiffSummary:
  report_id: string             # レポートID
  version_range: string         # バージョン範囲（例: 15.4 → 15.5.3）
  total_changes: number         # 総変更数
  breaking_changes: number      # Breaking Changes数
  security_fixes: number        # セキュリティ修正数
  new_features: number          # 新機能数
  bug_fixes: number             # バグ修正数
  project_impact: string        # プロジェクトへの影響度
```

#### 4.1.4 主要変更点エンティティ
```yaml
ChangeItem:
  report_id: string             # レポートID
  category: string              # カテゴリ（Breaking Changes/セキュリティ修正/バグ修正/新機能追加/パフォーマンス改善/廃止予定機能）
  title: string                 # 変更項目名
  description: string           # 内容
  impact_scope: string          # 影響範囲
  required_action: string       # 必須対応
  migration_method: string      # 移行方法
  code_example_before: string   # 変更前のコード例
  code_example_after: string    # 変更後のコード例
  reference_url: string         # 参考URL
  reference_date: date          # 参考日付
  project_impact: string        # プロジェクトへの影響度
```

#### 4.1.5 依存関係問題エンティティ
```yaml
DependencyIssue:
  report_id: string             # レポートID
  module_name: string           # 依存モジュール名
  issue_description: string     # 問題内容
  impact_scope: string          # 影響範囲
  affected_platforms: array     # 該当プラットフォーム・ブラウザ
  affected_versions: string     # 該当バージョン
  solution: string              # 対応方法
  github_issue_url: string      # GitHub Issue URL
  impact_level: string          # 影響度（高/中/低）
```

#### 4.1.6 テスト戦略エンティティ
```yaml
TestStrategy:
  report_id: string             # レポートID
  priority: string              # 優先度（高/中/低）
  test_name: string             # テスト項目名
  purpose: string               # 目的
  verification_steps: string    # 検証手順
  verification_commands: string # 検証コマンド例
  verification_items: array     # 検証項目
  success_criteria: string      # 成功基準
  platforms: array              # 対象プラットフォーム
```

#### 4.1.7 リスクアセスメントエンティティ
```yaml
RiskAssessment:
  report_id: string             # レポートID
  risk_item: string             # リスク項目
  probability: string            # 発生確率（高/中/低）
  impact: string                # 影響度（高/中/低）
  countermeasure: string         # 対応策
  responsible: string            # 担当
```

### 4.2 テンプレートデータモデル

#### 4.2.1 プロンプトテンプレートエンティティ
```yaml
PromptTemplate:
  id: string                    # テンプレートID
  name: string                  # テンプレート名
  version: string               # バージョン
  file_path: string             # ファイルパス
  content: string               # テンプレート内容
  variables: array              # 変数一覧
  created_at: datetime          # 作成日時
  updated_at: datetime          # 更新日時
```

#### 4.2.2 レポートテンプレートエンティティ
```yaml
ReportTemplate:
  id: string                    # テンプレートID
  name: string                  # テンプレート名
  version: string               # バージョン
  file_path: string             # ファイルパス
  content: string               # テンプレート内容
  sections: array               # セクション一覧
  created_at: datetime          # 作成日時
  updated_at: datetime          # 更新日時
```

## 5. データアクセス仕様

### 5.1 ファイルアクセス操作

#### 5.1.1 レポートファイル操作
```yaml
# レポート作成
create_report:
  input:
    product_name: string
    version_from: string
    version_to: string
    project_context: string (optional)
  output:
    file_path: string
    file_name: string
  process:
    1. ファイル名生成
    2. レポート内容生成
    3. ファイル書き込み
    4. 保存確認

# レポート読み込み
read_report:
  input:
    file_path: string
  output:
    content: string
    metadata: object
  process:
    1. ファイル存在確認
    2. ファイル読み込み
    3. 内容解析
    4. メタデータ抽出

# レポート一覧取得
list_reports:
  input:
    directory_path: string
  output:
    reports: array
  process:
    1. ディレクトリ読み込み
    2. ファイル一覧取得
    3. メタデータ抽出
    4. 一覧作成

# レポート削除
delete_report:
  input:
    file_path: string
  output:
    success: boolean
  process:
    1. ファイル存在確認
    2. ファイル削除
    3. 削除確認
```

#### 5.1.2 テンプレートファイル操作
```yaml
# テンプレート読み込み
read_template:
  input:
    template_type: string (prompt|report)
  output:
    content: string
    variables: array
  process:
    1. テンプレートファイル読み込み
    2. 内容解析
    3. 変数抽出
    4. テンプレート返却

# テンプレート更新
update_template:
  input:
    template_type: string
    content: string
  output:
    success: boolean
  process:
    1. バックアップ作成
    2. テンプレート更新
    3. 更新確認
    4. バックアップ保持
```

### 5.2 データ検索仕様

#### 5.2.1 レポート検索
```yaml
# 製品名で検索
search_by_product:
  input:
    product_name: string
  output:
    reports: array
  process:
    1. レポートディレクトリスキャン
    2. ファイル名パターンマッチング
    3. メタデータ抽出
    4. 結果返却

# バージョン範囲で検索
search_by_version:
  input:
    version_from: string
    version_to: string
  output:
    reports: array
  process:
    1. レポートディレクトリスキャン
    2. バージョン情報抽出
    3. 範囲マッチング
    4. 結果返却

# 日付範囲で検索
search_by_date:
  input:
    start_date: date
    end_date: date
  output:
    reports: array
  process:
    1. レポートディレクトリスキャン
    2. ファイル名から日付抽出
    3. 日付範囲マッチング
    4. 結果返却
```

#### 5.2.2 内容検索
```yaml
# レポート内容検索
search_content:
  input:
    keyword: string
    search_type: string (title|content|all)
  output:
    reports: array
  process:
    1. レポートファイル読み込み
    2. 内容検索
    3. マッチしたレポート抽出
    4. 結果返却
```

### 5.3 データ整合性仕様

#### 5.3.1 ファイル整合性チェック
```yaml
# ファイル存在確認
check_file_exists:
  input:
    file_path: string
  output:
    exists: boolean
    size: number
    modified: datetime
  process:
    1. ファイル存在確認
    2. ファイル情報取得
    3. 整合性確認
    4. 結果返却

# ディレクトリ整合性チェック
check_directory_integrity:
  input:
    directory_path: string
  output:
    valid: boolean
    missing_files: array
    corrupted_files: array
  process:
    1. ディレクトリ存在確認
    2. 必須ファイル確認
    3. ファイル整合性確認
    4. 結果返却
```

#### 5.3.2 データ検証
```yaml
# レポート内容検証
validate_report:
  input:
    content: string
  output:
    valid: boolean
    errors: array
    warnings: array
  process:
    1. Markdown形式確認
    2. 必須セクション確認
    3. データ形式確認
    4. 結果返却

# テンプレート検証
validate_template:
  input:
    template_type: string
    content: string
  output:
    valid: boolean
    errors: array
    warnings: array
  process:
    1. テンプレート形式確認
    2. 変数定義確認
    3. 構文確認
    4. 結果返却
```

## 6. データバックアップ仕様

### 6.1 バックアップ戦略

#### 6.1.1 バックアップ方式
- **方式**: ファイルベースバックアップ
- **頻度**: 手動実行
- **保存場所**: 別ディレクトリまたは外部ストレージ
- **保持期間**: 無制限（手動削除）

#### 6.1.2 バックアップ対象
```yaml
backup_targets:
  - reports/                    # レポートファイル
  - templates/                  # テンプレートファイル
  - .cursorrules               # 設定ファイル
  - README.md                  # プロジェクト説明
  - docs/                      # 設計書・ドキュメント
```

#### 6.1.3 バックアップ手順
```yaml
backup_process:
  1. バックアップディレクトリ作成
  2. 対象ファイルコピー
  3. バックアップ完了確認
  4. バックアップログ作成
```

### 6.2 復旧仕様

#### 6.2.1 復旧手順
```yaml
restore_process:
  1. バックアップファイル確認
  2. 復旧対象選択
  3. ファイル復旧
  4. 復旧確認
  5. 動作確認
```

#### 6.2.2 復旧検証
```yaml
restore_validation:
  1. ファイル存在確認
  2. ファイル内容確認
  3. 整合性確認
  4. 動作確認
```

## 7. データ移行仕様

### 7.1 移行シナリオ

#### 7.1.1 新規インストール
```yaml
new_installation:
  1. プロジェクトディレクトリ作成
  2. テンプレートファイル配置
  3. 設定ファイル配置
  4. ディレクトリ権限設定
  5. 動作確認
```

#### 7.1.2 既存環境からの移行
```yaml
migration_from_existing:
  1. 既存データバックアップ
  2. 新環境セットアップ
  3. データ移行
  4. 設定移行
  5. 動作確認
  6. 既存環境停止
```

#### 7.1.3 バージョンアップ
```yaml
version_upgrade:
  1. 現在のバージョンバックアップ
  2. 新バージョンインストール
  3. 設定移行
  4. データ移行
  5. 動作確認
  6. 旧バージョン削除
```

### 7.2 移行検証

#### 7.2.1 データ整合性確認
```yaml
data_integrity_check:
  1. ファイル存在確認
  2. ファイル内容確認
  3. メタデータ確認
  4. 関連性確認
  5. 整合性確認
```

#### 7.2.2 機能確認
```yaml
functionality_check:
  1. スラッシュコマンド動作確認
  2. レポート生成確認
  3. ファイル保存確認
  4. エラーハンドリング確認
  5. 全体動作確認
```

## 8. データセキュリティ仕様

### 8.1 データ保護

#### 8.1.1 アクセス制御
```yaml
access_control:
  - ファイル読み取り権限: テンプレートファイル
  - ファイル書き込み権限: レポートファイル
  - ディレクトリ作成権限: 必要に応じて
  - 実行権限: スラッシュコマンド
```

#### 8.1.2 データ暗号化
```yaml
encryption:
  - ファイル暗号化: なし（ローカル保存のため）
  - 通信暗号化: なし（ローカル処理のため）
  - バックアップ暗号化: オプション
```

### 8.2 データプライバシー

#### 8.2.1 個人情報保護
```yaml
privacy_protection:
  - 個人情報収集: なし
  - 個人情報保存: なし
  - 個人情報送信: なし
  - ログ記録: 最小限
```

#### 8.2.2 データ最小化
```yaml
data_minimization:
  - 必要最小限のデータのみ保存
  - 不要なデータの定期削除
  - ログの定期削除
  - バックアップの定期整理
```

## 9. データ監視仕様

### 9.1 監視項目

#### 9.1.1 ファイル監視
```yaml
file_monitoring:
  - ファイル存在確認
  - ファイルサイズ監視
  - ファイル更新日時監視
  - ディスク使用量監視
```

#### 9.1.2 処理監視
```yaml
process_monitoring:
  - レポート生成時間
  - ファイル保存時間
  - エラー発生率
  - 成功率
```

### 9.2 アラート仕様

#### 9.2.1 アラート条件
```yaml
alert_conditions:
  - ディスク使用量80%超過
  - ファイル保存エラー
  - レポート生成エラー
  - テンプレート読み込みエラー
```

#### 9.2.2 アラート処理
```yaml
alert_processing:
  1. アラート条件検出
  2. アラート通知
  3. ログ記録
  4. 対応指示
  5. 復旧確認
```

## 10. データ最適化仕様

### 10.1 パフォーマンス最適化

#### 10.1.1 ファイル最適化
```yaml
file_optimization:
  - ファイルサイズ最適化
  - 読み込み速度最適化
  - 書き込み速度最適化
  - 検索速度最適化
```

#### 10.1.2 ディレクトリ最適化
```yaml
directory_optimization:
  - ディレクトリ構造最適化
  - ファイル配置最適化
  - アクセスパス最適化
  - 管理効率最適化
```

### 10.2 ストレージ最適化

#### 10.2.1 容量管理
```yaml
capacity_management:
  - 不要ファイル削除
  - 古いレポートアーカイブ
  - ログファイルローテーション
  - バックアップ整理
```

#### 10.2.2 アクセス最適化
```yaml
access_optimization:
  - 頻繁にアクセスするファイルの最適配置
  - キャッシュ戦略
  - インデックス作成
  - 検索最適化
```
