# -*- coding: utf-8 -*-
"""Markdown -> standalone HTML preview (images inlined as base64)."""
import base64
import html
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
DST = Path(sys.argv[2])

INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def inline(s):
    s = html.escape(s)
    out = []
    for part in INLINE.split(s):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append(f"<strong>{part[2:-2]}</strong>")
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append(f"<code>{part[1:-1]}</code>")
        elif part.startswith("[") and "](" in part:
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part)
            out.append(f'<a href="{m.group(2)}">{m.group(1)}</a>')
        else:
            out.append(part)
    return "".join(out)


def img_tag(alt, path):
    p = SRC.parent / path
    data = base64.b64encode(p.read_bytes()).decode()
    return (f'<figure><img src="data:image/png;base64,{data}" alt="{html.escape(alt)}">'
            f'<figcaption>{html.escape(alt)}</figcaption></figure>')


CSS = """
:root{--ink:#31363C;--soft:#5C646D;--mute:#8B939C;--line:#E6EBF0;--accent:#0B3D6B;--teal:#207A70;}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#F2F4F6;color:var(--ink);
  font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:17px;line-height:1.88;letter-spacing:.012em;}
.page{max-width:800px;margin:0 auto;background:#fff;padding:68px 76px 84px;
  box-shadow:0 1px 3px rgba(16,32,48,.06),0 12px 40px rgba(16,32,48,.06);}
h1{font-size:31px;line-height:1.42;font-weight:700;letter-spacing:-.3px;margin:0 0 14px;color:#15191D;}
.meta{font-size:13.5px;color:var(--mute);line-height:1.9;margin-bottom:38px;
  padding-bottom:26px;border-bottom:1px solid var(--line);}
p{margin:20px 0;}
h2{font-size:22px;font-weight:700;margin:52px 0 20px;padding-left:14px;position:relative;
  letter-spacing:-.2px;color:#121619;line-height:1.5;}
h2:before{content:"";position:absolute;left:0;top:.24em;bottom:.24em;width:4px;border-radius:2px;background:var(--accent);}
h3{font-size:17.5px;font-weight:700;margin:34px 0 8px;color:var(--accent);}
strong{color:#101418;font-weight:700;}
code{font-family:"Cascadia Mono",Consolas,"Courier New",monospace;font-size:.86em;
  background:#F3F5F7;color:#8A2B2B;padding:2px 6px;border-radius:4px;word-break:break-word;}
pre{background:#F8FAFB;border:1px solid #EDF1F4;border-radius:10px;padding:18px 20px;margin:22px 0;
  overflow-x:auto;font-size:13px;line-height:1.7;}
pre code{background:none;color:#3A424B;padding:0;font-size:13px;}
blockquote{margin:24px 0;padding:16px 22px;background:#F6F8FA;border-left:3px solid #C9D6E4;
  border-radius:0 8px 8px 0;color:#4C565F;font-size:16px;}
blockquote p{margin:6px 0;}
figure{margin:30px 0;}
figure img{display:block;width:100%;height:auto;border-radius:8px;border:1px solid #E9EEF2;}
figcaption{margin-top:10px;font-size:13px;line-height:1.7;color:var(--mute);text-align:center;}
.tablewrap{overflow-x:auto;margin:26px 0;}
table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.7;}
th{background:var(--accent);color:#fff;font-weight:600;text-align:left;padding:11px 13px;border:1px solid #0B3D6B;}
td{padding:11px 13px;border:1px solid var(--line);vertical-align:top;}
tr:nth-child(even) td{background:#F7F9FB;}
ul,ol{margin:18px 0;padding-left:22px;}
li{margin:9px 0;}
li code{font-size:.84em;}
a{color:#1F5C99;text-decoration:none;border-bottom:1px solid rgba(31,92,153,.28);}
hr{border:0;border-top:1px solid var(--line);margin:44px 0;}
.foot{margin-top:54px;padding-top:22px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--mute);line-height:1.9;}
@media (max-width:820px){
  body{font-size:16px}
  .page{padding:36px 22px 56px;box-shadow:none}
  h1{font-size:25px}
  h2{font-size:19.5px;margin-top:40px}
  figure img{border-radius:6px}
}
"""


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    body, meta, i, title = [], [], 0, ""

    while i < len(lines):
        raw = lines[i]
        s = raw.strip()

        if not s:
            i += 1
            continue

        if s.startswith("%%"):
            meta.append(s[2:].strip())
            i += 1
            continue

        if s.startswith("# "):
            title = s[2:]
            i += 1
            continue

        if s.startswith("```"):
            lang = s[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1
            cls = f' class="language-{lang}"' if lang else ""
            body.append("<pre><code{}>{}</code></pre>".format(cls, html.escape("\n".join(code))))
            continue

        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
        if m:
            body.append(img_tag(m.group(1), m.group(2)))
            i += 1
            continue

        if s == "---":
            body.append("<hr>")
            i += 1
            continue

        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            rest = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            body.append(f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead><tbody>{rest}</tbody></table></div>')
            continue

        if s.startswith("## "):
            body.append(f"<h2>{inline(s[3:])}</h2>")
            i += 1
            continue

        if s.startswith("### "):
            body.append(f"<h3>{inline(s[4:])}</h3>")
            i += 1
            continue

        if s.startswith("> "):
            q = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                q.append(inline(lines[i].strip()[2:]))
                i += 1
            body.append("<blockquote>" + "".join(f"<p>{x}</p>" for x in q) + "</blockquote>")
            continue

        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(inline(lines[i].strip()[2:]))
                i += 1
            body.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue

        body.append(f"<p>{inline(s)}</p>")
        i += 1

    meta_html = "".join(f'<div>{html.escape(m)}</div>' for m in meta)
    doc = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style></head>
<body><div class="page">
<h1>{inline(title)}</h1>
<div class="meta">{meta_html}</div>
{''.join(body)}
</div></body></html>"""
    DST.write_text(doc, encoding="utf-8")
    print(f"preview: {DST} ({len(doc)//1024} KB)")


if __name__ == "__main__":
    main()
