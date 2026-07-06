#!/usr/bin/env python3
"""upgrade-analyzer レポート用 Markdown → 自己完結型HTML変換スクリプト。

upgrade-analyzer が生成する Markdown レポート（H2 セクション構成）を、
左サイドナビ付きの自己完結型 HTML（外部CSS/JSなし）へ決定的に変換する。
LLM によるHTML手書き生成を置き換え、MD/HTML の内容同一性と
テンプレートCSSの非破壊を構造的に保証する。

使い方:
    python3 md_to_html.py report.md -o report.html [--strict]

- アンカーリンクの整合性（href="#x" に対応する id の存在）を検証し、
  未解決があれば標準エラーに警告を出す（--strict 時は exit code 2）。
- 標準ライブラリのみ使用（Python 3.8+）。
"""

import argparse
import html
import re
import sys

TEMPLATE_VERSION = "4.5"

# チェックリスト状態の localStorage 永続化（自己完結・外部JSなし）
# __DATE__ はレポート日付に置換され、保存キーの一部になる
CHECK_SCRIPT = """\
<script>
(function () {
  "use strict";
  var key = "ua-check:" + document.title + ":" + "__DATE__";
  var boxes = Array.prototype.slice.call(
    document.querySelectorAll('.checklist input[type="checkbox"]'));
  if (!boxes.length) { return; }
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || "{}"); } catch (e) {}
  function sync(box) {
    var li = box.closest("li");
    if (li) { li.classList.toggle("done", box.checked); }
  }
  function badge() {
    var done = boxes.filter(function (b) { return b.checked; }).length;
    var el = document.getElementById("check-progress");
    if (el) {
      el.hidden = false;
      el.textContent = "チェック進捗: " + done + " / " + boxes.length;
    }
  }
  boxes.forEach(function (box) {
    var id = box.getAttribute("data-ck");
    if (typeof saved[id] === "boolean") { box.checked = saved[id]; }
    sync(box);
    box.addEventListener("change", function () {
      saved[id] = box.checked;
      try { localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {}
      sync(box);
      badge();
    });
  });
  badge();
})();
</script>"""

CSS = """\
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
/* レイアウト: 左サイドナビ + 右コンテンツ（外部JS不要） */
.layout { display: flex; align-items: flex-start; }
/* 左固定サイドナビ（height: 100vh + overflow-y: auto は必須。min-height にするとスクロール不能になる） */
.sidenav { position: sticky; top: 0; align-self: flex-start;
  width: 260px; min-width: 260px; height: 100vh; max-height: 100vh; overflow-y: auto;
  background: #fff; border-right: 1px solid #e1e4e8; padding: 20px 16px; }
.sidenav h2 { font-size: 14px; margin-bottom: 12px; color: #444; }
.sidenav ol { list-style: none; padding: 0; }
.sidenav li { margin: 2px 0; }
.sidenav a { display: block; color: #0366d6; text-decoration: none;
  font-size: 13px; padding: 6px 10px; border-radius: 6px; }
.sidenav a:hover { background: #f0f6ff; }
.sidenav a.cta { font-weight: 700; color: #1e3a5f; background: #fff6e5; }
.sidenav a:target, .sidenav a:focus { background: #e8f4fd; }
/* セクションのスクロール位置調整（アンカージャンプ先すべてに適用） */
.section, .next-action, .card[id], .section h3[id], .section h4[id],
span.anchor[id] { scroll-margin-top: 16px; }
/* 上段→詳細へのジャンプリンク */
.jump { font-size: 12px; color: #0366d6; text-decoration: none; white-space: nowrap; }
.jump:hover { text-decoration: underline; }
/* コンテンツエリア */
.content { flex: 1; min-width: 0; max-width: 1100px; margin: 0 auto; padding: 24px 40px 40px; }
/* サマリー（最重要・最上段） */
.next-action { background: #fff; border: 2px solid #1e3a5f; border-radius: 8px;
  padding: 20px 24px; margin-bottom: 20px; }
.next-action h2 { color: #1e3a5f; font-size: 18px; margin-bottom: 12px; }
.next-action h3 { font-size: 14px; font-weight: 600; color: #333; margin: 14px 0 6px; }
.next-action .kpi { font-weight: 700; margin-bottom: 12px; }
/* レスポンシブ: 狭幅では上部に折りたたみ */
@media (max-width: 860px) {
  .layout { display: block; }
  .sidenav { position: static; width: auto; min-width: 0; height: auto;
    border-right: none; border-bottom: 1px solid #e1e4e8; }
  .sidenav ol { columns: 2; }
}
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
/* チェックリスト（実input・localStorageで状態永続化） */
.checklist { list-style: none; padding: 0; }
.checklist li { padding: 5px 0; font-size: 13px; }
.checklist label { display: flex; align-items: flex-start; gap: 8px; cursor: pointer; }
.checklist input[type="checkbox"] { margin-top: 3px; flex-shrink: 0;
  width: 14px; height: 14px; accent-color: #28a745; cursor: pointer; }
.checklist li.done > label { color: #6a737d; text-decoration: line-through; }
/* チェック進捗バッジ（ヘッダー） */
.check-progress { display: inline-block; margin-left: 12px; padding: 2px 10px;
  border-radius: 12px; background: rgba(255,255,255,0.18); font-size: 12px; }
/* 通常リスト */
.content ul:not(.checklist), .content ol:not(.sidenav ol) { padding-left: 24px; margin: 8px 0; }
.content li { margin: 3px 0; }
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
"""

# H2セクションタイトル → 固定セクションid のマッピング（キーワード部分一致・上から評価）
SECTION_ID_RULES = [
    ("エグゼクティブ", "summary"),
    ("メタ情報", "meta"),
    ("リスク評価", "risk"),
    ("Breaking", "breaking"),
    ("セキュリティ", "security"),
    ("コードベース", "codebase"),
    ("テスト", "test"),
    ("マイグレーション", "migration"),
    ("推移的", "transitive"),
    ("新機能", "features"),
    ("参考", "refs"),
]

ANCHOR_RE = re.compile(r'<a\s+id="([A-Za-z0-9_-]+)"\s*>\s*</a>')
CODESPAN_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def section_id_for(title, index):
    # 固定ルールを先に評価（「エグゼクティブサマリー」が next-action に誤マッチしないように）
    for key, sid in SECTION_ID_RULES:
        if key.lower() in title.lower():
            return sid
    if index == 0 or title.lstrip().startswith("0.") or "サマリー" in title:
        return "next-action"
    return "sec-%d" % index


def inline(text):
    """インライン要素の変換（コードスパン退避 → エスケープ → 太字 → リンク）。"""
    placeholders = []

    def stash_code(m):
        placeholders.append("<code>%s</code>" % html.escape(m.group(1)))
        return "\x00%d\x00" % (len(placeholders) - 1)

    text = CODESPAN_RE.sub(stash_code, text)
    text = html.escape(text, quote=False)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)

    def link(m):
        label, url = m.group(1), m.group(2)
        cls = ' class="jump"' if url.startswith("#") else ' target="_blank" rel="noopener"'
        return '<a href="%s"%s>%s</a>' % (html.escape(url, quote=True), cls, label)

    text = LINK_RE.sub(link, text)

    def unstash(m):
        return placeholders[int(m.group(1))]

    return re.sub("\x00(\\d+)\x00", unstash, text)


def alert_class(first_line):
    if first_line.startswith(("🚨", "❌", "🔴")):
        return "alert-danger"
    if first_line.startswith(("⚠", "🟡")):
        return "alert-warning"
    return "alert-info"


def render_blocks(lines, ck_counter=None):
    """セクション本文（H2配下）のブロック変換。

    ck_counter: チェックボックスへ文書内で一意な data-ck 連番を振るためのカウンタ
    （[0] を保持するリスト。None の場合は 0 起点のローカルカウンタ）。
    """
    out = []
    i = 0
    if ck_counter is None:
        ck_counter = [0]
    pending_anchor = None  # 直前の <a id=...></a> を次の見出しに移植する

    def flush_anchor_inline():
        nonlocal pending_anchor
        if pending_anchor:
            out.append('<span class="anchor" id="%s"></span>' % pending_anchor)
            pending_anchor = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # 区切り線はセクション枠で表現済みのため出力しない
        if re.fullmatch(r"-{3,}", stripped):
            i += 1
            continue

        # 単独アンカー行 → 次の見出しの id にする
        m = ANCHOR_RE.fullmatch(stripped)
        if m:
            flush_anchor_inline()  # 連続アンカーは前のものを先に確定
            pending_anchor = m.group(1)
            i += 1
            continue

        # コードフェンス
        if stripped.startswith("```"):
            flush_anchor_inline()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 終了フェンスを飛ばす
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code_lines)))
            continue

        # 見出し（### / ####）
        m = re.match(r"^(#{3,6})\s+(.*)$", stripped)
        if m:
            level = min(len(m.group(1)), 6)
            attr = ' id="%s"' % pending_anchor if pending_anchor else ""
            pending_anchor = None
            out.append("<h%d%s>%s</h%d>" % (level, attr, inline(m.group(2)), level))
            i += 1
            continue

        # テーブル
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|?\s*$", lines[i + 1]
        ):
            flush_anchor_inline()
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table>", "<thead><tr>"]
            t += ["<th>%s</th>" % inline(c) for c in header_cells]
            t.append("</tr></thead><tbody>")
            for row in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in row) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # 引用ブロック → アラート
        if stripped.startswith(">"):
            flush_anchor_inline()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            body = "<br>".join(inline(q) for q in quote if q)
            out.append('<div class="alert %s">%s</div>' % (alert_class(quote[0] if quote else ""), body))
            continue

        # リスト（チェックリスト含む・インデントによる1段ネスト対応）
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            flush_anchor_inline()
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                items.append((len(lm.group(1)), lm.group(3)))
                i += 1
            is_check = any(re.match(r"^\[([ xX])\]\s+", t) for _, t in items)
            ul_cls = ' class="checklist"' if is_check else ""
            parts = ["<ul%s>" % ul_cls]
            depth = 0
            base = items[0][0] if items else 0
            for indent, text in items:
                want = 1 if indent > base else 0
                while depth < want:
                    parts.append("<ul>")
                    depth += 1
                while depth > want:
                    parts.append("</ul>")
                    depth -= 1
                cm = re.match(r"^\[([ xX])\]\s+(.*)$", text)
                if cm:
                    checked = " checked" if cm.group(1).lower() == "x" else ""
                    cls = ' class="done"' if checked else ""
                    parts.append(
                        '<li%s><label><input type="checkbox" data-ck="%d"%s> '
                        "<span>%s</span></label></li>"
                        % (cls, ck_counter[0], checked, inline(cm.group(2)))
                    )
                    ck_counter[0] += 1
                else:
                    parts.append("<li>%s</li>" % inline(text))
            while depth > 0:
                parts.append("</ul>")
                depth -= 1
            parts.append("</ul>")
            out.append("".join(parts))
            continue

        # 段落（連続行をまとめる）
        flush_anchor_inline()
        para = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", "|", ">", "```", "- ", "* "))
                    or re.fullmatch(r"-{3,}", nxt) or ANCHOR_RE.fullmatch(nxt)
                    or re.match(r"^\d+\.\s", nxt)):
                break
            para.append(nxt)
            i += 1
        out.append("<p>%s</p>" % "<br>".join(inline(p) for p in para))

    flush_anchor_inline()
    return "\n".join(out)


def split_sections(md_lines):
    """H2見出しでセクション分割。戻り値: (preamble_lines, [(title, body_lines), ...])"""
    preamble = []
    sections = []
    current = None
    in_code = False
    for line in md_lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and re.match(r"^##\s+(?!#)", line):
            title = re.sub(r"^##\s+", "", line).strip()
            current = (title, [])
            sections.append(current)
            continue
        if current is None:
            preamble.append(line)
        else:
            current[1].append(line)
    return preamble, sections


def detect_risk(md_text):
    m = re.search(r"総合リスク[^🔴🟡🟢\n]*([🔴🟡🟢])", md_text)
    if not m:
        return "low", "🟢 低"
    emoji = m.group(1)
    return {"🔴": ("high", "🔴 高"), "🟡": ("mid", "🟡 中"), "🟢": ("low", "🟢 低")}[emoji]


def meta_from_table(md_text, key):
    m = re.search(r"^\|\s*%s\s*\|\s*([^|]+)\|" % re.escape(key), md_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def validate_anchors(html_text):
    ids = set(re.findall(r'id="([^"]+)"', html_text))
    hrefs = re.findall(r'href="#([^"]+)"', html_text)
    return sorted({h for h in hrefs if h not in ids})


def convert(md_text):
    lines = md_text.splitlines()
    preamble, sections = split_sections(lines)

    title = "バージョンアップ影響分析"
    for line in preamble:
        m = re.match(r"^#\s+(?!#)(.*)$", line)
        if m:
            title = m.group(1).strip()
            break
    date = ""
    m = re.search(r"\*\*日付\*\*[:：]\s*([0-9-]+)", md_text)
    if m:
        date = m.group(1)

    risk_cls, risk_label = detect_risk(md_text)
    ecosystem = meta_from_table(md_text, "エコシステム")
    bc_count = meta_from_table(md_text, "Breaking Changes")
    cve_count = meta_from_table(md_text, "セキュリティ修正")

    meta_bits = []
    if ecosystem:
        meta_bits.append("エコシステム: %s" % html.escape(ecosystem))
    if date:
        meta_bits.append("分析日: %s" % html.escape(date))
    if bc_count:
        meta_bits.append("Breaking Changes: %s" % html.escape(bc_count))
    if cve_count:
        meta_bits.append("セキュリティ修正: %s" % html.escape(cve_count))
    meta_line = " ｜ ".join(meta_bits)

    nav_items = []
    body_parts = []
    ck_counter = [0]  # 文書内チェックボックスの一意連番（localStorage永続化キー）
    for idx, (sec_title, sec_lines) in enumerate(sections):
        sid = section_id_for(sec_title, idx)
        # 同名idの重複回避
        if any(sid == existing for existing, _ in nav_items):
            sid = "%s-%d" % (sid, idx)
        nav_items.append((sid, sec_title))
        inner = render_blocks(sec_lines, ck_counter)
        if sid == "next-action":
            body_parts.append(
                '<section class="next-action" id="next-action">\n<h2>🚀 %s</h2>\n%s\n</section>'
                % (inline(sec_title), inner)
            )
        else:
            body_parts.append(
                '<section class="section" id="%s">\n<h2>%s</h2>\n%s\n</section>'
                % (sid, inline(sec_title), inner)
            )

    nav_html = "\n".join(
        '      <li><a%s href="#%s">%s</a></li>'
        % (' class="cta"' if sid == "next-action" else "", sid,
           ("🚀 " if sid == "next-action" else "") + html.escape(t))
        for sid, t in nav_items
    )

    doc = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{css}</style>
</head>
<body>

<div class="report-header">
  <h1>📊 {title}
    <span class="risk-badge risk-{risk_cls}">{risk_label}</span>
  </h1>
  <div class="meta">{meta_line}<span class="check-progress" id="check-progress" hidden></span></div>
</div>

<div class="layout">
  <nav class="sidenav">
    <h2>📋 目次</h2>
    <ol>
{nav}
    </ol>
  </nav>

  <div class="content">
{body}
  </div>
</div>

<footer>
  生成日: {date} ｜ upgrade-analyzer v{version} ｜ md_to_html.py（スクリプト変換）
</footer>

{script}
</body>
</html>
""".format(
        title=html.escape(title),
        css=CSS,
        risk_cls=risk_cls,
        risk_label=risk_label,
        meta_line=meta_line,
        nav=nav_html,
        body="\n\n".join(body_parts),
        date=html.escape(date) if date else "-",
        version=TEMPLATE_VERSION,
        script=CHECK_SCRIPT.replace("__DATE__", date or "-"),
    )
    return doc


def main():
    ap = argparse.ArgumentParser(description="upgrade-analyzer MDレポートを自己完結型HTMLへ変換")
    ap.add_argument("input", help="入力Markdownファイル")
    ap.add_argument("-o", "--output", help="出力HTMLファイル（省略時: 入力の拡張子を.htmlに）")
    ap.add_argument("--strict", action="store_true", help="未解決アンカーがあれば exit code 2")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        md_text = f.read()

    out_path = args.output or re.sub(r"\.md$", "", args.input) + ".html"
    html_text = convert(md_text)

    unresolved = validate_anchors(html_text)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_text)

    print("HTML生成完了: %s" % out_path)
    if unresolved:
        print("⚠️ 未解決アンカー（リンク先idが存在しない）: %s" % ", ".join(unresolved),
              file=sys.stderr)
        print("   → MD側のアンカー（<a id=...></a>）を修正して再実行してください", file=sys.stderr)
        if args.strict:
            sys.exit(2)
    else:
        print("アンカー整合性: OK（未解決リンクなし）")


if __name__ == "__main__":
    main()
