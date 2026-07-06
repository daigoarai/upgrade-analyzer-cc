#!/usr/bin/env python3
"""upgrade-analyzer ゴールデン評価スコアリングスクリプト。

生成されたMDレポートを、eval/cases/ の正解BCリスト（must_find）と突合し、
recall（正解BCのうちレポートに記載された割合）を算出する。
プロンプト改修の前後で実行し、抽出精度の回帰を数値で検出する。

使い方:
    python3 eval/score.py <レポート.md> --case eval/cases/next_14.0.0_to_15.3.2.json
    python3 eval/score.py <レポート.md> --case <case.json> --min-recall 0.9  # 下回れば exit 1

- 標準ライブラリのみ使用（Python 3.8+）。
- precision（誤検出率）は自動判定できないため、レポートの「根拠引用」を人手で確認する
  （手順は eval/README.md 参照）。
"""

import argparse
import json
import re
import sys


def score(report_text, case):
    matched = []
    missing = []
    for item in case["must_find"]:
        hit = None
        for pattern in item["patterns"]:
            m = re.search(pattern, report_text, re.IGNORECASE | re.DOTALL)
            if m:
                hit = pattern
                break
        (matched if hit else missing).append((item, hit))
    return matched, missing


def main():
    ap = argparse.ArgumentParser(description="レポートMDを正解BCリストと突合しrecallを算出")
    ap.add_argument("report", help="評価対象のMDレポート")
    ap.add_argument("--case", required=True, help="正解ケースJSON（eval/cases/*.json）")
    ap.add_argument("--min-recall", type=float, default=None,
                    help="このrecallを下回った場合 exit code 1（CI用）")
    args = ap.parse_args()

    with open(args.report, encoding="utf-8") as f:
        report_text = f.read()
    with open(args.case, encoding="utf-8") as f:
        case = json.load(f)

    matched, missing = score(report_text, case)
    total = len(case["must_find"])
    recall = len(matched) / total if total else 0.0

    print("ゴールデン評価: %s（%s v%s → v%s）" % (
        case["case_id"], case["package"], case["from"], case["to"]))
    print("正解キュレーション日: %s" % case.get("curated_at", "-"))
    print()
    print("✅ 検出済み: %d件" % len(matched))
    for item, hit in matched:
        print("  - [%s] %s" % (item["id"], item["title"]))
    print()
    print("❌ 見落とし: %d件" % len(missing))
    for item, _ in missing:
        print("  - [%s] %s" % (item["id"], item["title"]))
    print()
    print("recall: %.1f%% (%d/%d)" % (recall * 100, len(matched), total))
    print("※ precision はレポートの「根拠引用」を人手で確認すること（eval/README.md）")

    if args.min_recall is not None and recall < args.min_recall:
        print("\n⚠️ recall %.1f%% が閾値 %.1f%% を下回りました" % (
            recall * 100, args.min_recall * 100), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
