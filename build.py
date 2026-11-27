# -*- coding: utf-8 -*-
"""ZDR 的笔记 —— 把 notes/<slug>/note.md 编成 docs/ 下的静态站。

用法：
    python build.py            # 生成 docs/
    python build.py --serve    # 生成后本地起一个 http://127.0.0.1:8000

新增一篇笔记：
    notes/<slug>/note.md       （开头是 --- 包起来的 front matter）
    notes/<slug>/images/*.png  （正文里用 images/xxx.png 引用，构建时自动改写路径）
    python build.py && git add -A && git commit -m "新增：xxx" && git push
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTES = ROOT / "notes"
DOCS = ROOT / "docs"
SITE_TITLE = "ZDR 的笔记"
SITE_DESC = "AI 工具、Unity、以及那些「以为换个节点就能解决」的问题。"
SITE_URL = "https://3038665474qq.github.io/zdr-notes/"
ICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'>"
        "<text y='13' font-size='13'>📝</text></svg>")

INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


# ---------------------------------------------------------------- inline / md
def inline(s: str) -> str:
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


def rewrite_images(s: str, slug: str) -> str:
    """images/x.png -> ../assets/<slug>/x.png（笔记页在 docs/notes/ 下）"""
    return re.sub(r'(src=")images/([^"]+)"', rf'\1../assets/{slug}/\2"', s)


def parse_body(lines: list[str], slug: str) -> list[str]:
    body, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("# "):
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
            body.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
            continue
        m = re.match(r"^!\[([^\]]*)\]\((images/[^)]+)\)$", s)
        if m:
            alt, src = m.group(1), rewrite_images(f'src="{m.group(2)}"', slug)
            body.append(f'<figure><img {src} alt="{html.escape(alt)}" loading="lazy">'
                        f"<figcaption>{html.escape(alt)}</figcaption></figure>")
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
            rest = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:]
            )
            body.append(f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead>'
                        f"<tbody>{rest}</tbody></table></div>")
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
    return body


def plain_text(lines: list[str]) -> str:
    """把正文压成一串纯文本，给搜索用。"""
    out = []
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("```") or re.match(r"^!\[.*\]\(.*\)$", s):
            continue
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
        s = re.sub(r"^[#>\-\*\s]+", "", s)
        s = s.replace("**", "").replace("`", "").replace("|", " ")
        out.append(s)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def reading_minutes(lines: list[str]) -> int:
    n = len(re.sub(r"\s", "", plain_text(lines)))
    return max(1, round(n / 400))


def parse_front_matter(text: str) -> tuple[dict, list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines
    meta = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, lines[i + 1:]
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, lines


# ---------------------------------------------------------------- css
CSS = """
:root{--ink:#2f343a;--soft:#59616a;--mute:#8b939c;--line:#e6ebf0;--accent:#0b3d6b;--bg:#f3f5f7;--card:#fff}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);display:flex;flex-direction:column;min-height:100vh;
  font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:17px;line-height:1.9;letter-spacing:.012em;-webkit-font-smoothing:antialiased}
main{flex:1 0 auto}
a{color:#1f5c99;text-decoration:none}
.wrap{max-width:880px;margin:0 auto;padding:0 24px}

/* ---------- 首页 ---------- */
.site{padding:74px 0 34px}
.site h1{font-size:34px;margin:0 0 12px;letter-spacing:-.4px;color:#111}
.site p{margin:0;color:var(--mute);font-size:15px}
.site .count{display:inline-block;margin-top:14px;font-size:13px;color:var(--mute);
  border:1px solid var(--line);border-radius:999px;padding:3px 12px;background:#fff}
.list{list-style:none;margin:0 0 80px;padding:0}
.list li{margin:0 0 14px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:26px 30px;transition:.18s;box-shadow:0 1px 2px rgba(16,32,48,.03)}
.card:hover{border-color:#cfdae6;box-shadow:0 8px 28px rgba(16,32,48,.08);transform:translateY(-2px)}
.card .meta{font-size:13px;color:var(--mute);margin-bottom:8px;display:flex;gap:10px;flex-wrap:wrap}
.card .meta .tag{color:var(--accent);background:#eef3f9;border-radius:999px;padding:1px 9px}
.card h2{font-size:21px;line-height:1.55;margin:0 0 10px;color:#12171c;letter-spacing:-.2px}
.card p{margin:0;color:var(--soft);font-size:15px;line-height:1.8}
.card .more{display:inline-block;margin-top:14px;font-size:14px;color:var(--accent);font-weight:600}
.card .thumb{float:right;width:132px;height:84px;object-fit:cover;border-radius:8px;margin:2px 0 12px 22px;border:1px solid var(--line)}
.card .meta .rt{color:#a6adb5}

/* ---------- 搜索 / 筛选 ---------- */
.tools{margin:26px 0 18px}
.search{position:relative;display:flex;align-items:center;background:#fff;border:1px solid var(--line);
  border-radius:12px;padding:0 14px;box-shadow:0 1px 2px rgba(16,32,48,.03);transition:.16s}
.search:focus-within{border-color:#b9cadd;box-shadow:0 4px 18px rgba(16,32,48,.08)}
.search svg{width:18px;height:18px;flex:0 0 auto;stroke:#9aa3ad;fill:none;stroke-width:2;
  stroke-linecap:round;margin-right:10px}
.search input{flex:1;border:0;outline:0;background:none;font:inherit;font-size:15px;
  padding:13px 0;color:var(--ink);-webkit-appearance:none}
.search input::-webkit-search-cancel-button{display:none}
.search kbd{font:12px/1 "Cascadia Mono",Consolas,monospace;color:#a6adb5;border:1px solid var(--line);
  border-radius:5px;padding:3px 6px;background:#fafbfc}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.chip{font:inherit;font-size:13.5px;color:#5d6670;background:#fff;border:1px solid var(--line);
  border-radius:999px;padding:5px 13px;cursor:pointer;transition:.14s}
.chip:hover{border-color:#c6d4e2;color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
mark{background:#fff2b8;color:inherit;border-radius:2px;padding:0 1px}
.empty{color:var(--mute);text-align:center;padding:40px 0 60px;font-size:15px}

/* ---------- 笔记页 ---------- */
.back{max-width:880px;margin:0 auto;padding:26px 24px 0;font-size:14px}
.back a{color:var(--mute)}
.back a:hover{color:var(--accent)}
.sheet{max-width:880px;margin:14px auto 70px;background:#fff;border-radius:16px;overflow:hidden;
  box-shadow:0 1px 3px rgba(16,32,48,.05),0 18px 60px rgba(16,32,48,.06)}
.hero{display:block;width:100%;height:auto;border-bottom:1px solid var(--line)}
.note{padding:52px 68px 72px}
.note h1{font-size:31px;line-height:1.45;margin:0 0 14px;letter-spacing:-.3px;color:#12171c}
.note .meta{font-size:13.5px;color:var(--mute);margin:0 0 34px;padding-bottom:24px;
  border-bottom:1px solid var(--line);display:flex;gap:12px;flex-wrap:wrap}
.note .meta .tag{color:var(--accent);background:#eef3f9;border-radius:999px;padding:1px 10px}
.note p{margin:20px 0}
.note h2{font-size:22px;font-weight:700;margin:50px 0 18px;padding-left:14px;position:relative;line-height:1.5;color:#12171c}
.note h2:before{content:"";position:absolute;left:0;top:.26em;bottom:.26em;width:4px;border-radius:2px;background:var(--accent)}
.note h3{font-size:17.5px;font-weight:700;margin:32px 0 8px;color:var(--accent)}
.note strong{color:#0f1419}
.note code{font-family:"Cascadia Mono",Consolas,monospace;font-size:.86em;background:#f3f5f7;
  color:#8a2b2b;padding:2px 6px;border-radius:4px;word-break:break-word}
.note pre{background:#f8fafb;border:1px solid #edf1f4;border-radius:10px;padding:18px 20px;margin:22px 0;
  overflow-x:auto;font-size:13px;line-height:1.7}
.note pre code{background:none;color:#3a424b;padding:0;font-size:13px}
.note blockquote{margin:24px 0;padding:16px 22px;background:#f6f8fa;border-left:3px solid #c9d6e4;
  border-radius:0 8px 8px 0;color:#4c565f;font-size:16px}
.note blockquote p{margin:6px 0}
.note figure{margin:30px 0}
.note figure img{display:block;width:100%;height:auto;border-radius:8px;border:1px solid #e9eef2;background:#fff}
.note figcaption{margin-top:10px;font-size:13px;color:var(--mute);text-align:center}
.note .tablewrap{overflow-x:auto;margin:26px 0}
.note table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.7}
.note th{background:var(--accent);color:#fff;font-weight:600;text-align:left;padding:11px 13px;border:1px solid var(--accent)}
.note td{padding:11px 13px;border:1px solid var(--line);vertical-align:top}
.note tr:nth-child(even) td{background:#f7f9fb}
.note ul,.note ol{margin:18px 0;padding-left:22px}
.note li{margin:9px 0}
.note .attach{margin-top:46px;padding-top:20px;border-top:1px solid var(--line);font-size:14px;color:var(--mute)}

footer.site{border-top:1px solid var(--line);padding:26px 0 50px;font-size:13px;color:var(--mute);margin-top:auto}
footer.site a{color:var(--mute);border-bottom:1px solid var(--line)}

@media (max-width:820px){
  body{font-size:16px}
  .site{padding:44px 0 24px}
  .site h1{font-size:27px}
  .card{padding:20px 20px}
  .card h2{font-size:18.5px}
  .card .thumb{display:none}
  .note{padding:30px 22px 50px}
  .note h1{font-size:24px}
  .note h2{font-size:19.5px;margin-top:38px}
  .sheet{border-radius:0;box-shadow:none;margin:10px 0 40px}
}
"""


# ---------------------------------------------------------------- render
def note_page(meta: dict, body: list[str], slug: str, cover: str | None) -> str:
    title = meta.get("title", slug)
    d = meta.get("date", "")
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    tag_html = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)
    hero = f'<img class="hero" src="../{cover}" alt="封面">' if cover else ""
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · {SITE_TITLE}</title>
<meta name="description" content="{html.escape(meta.get('summary',''))}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta.get('summary',''))}">
<meta name="theme-color" content="#f3f5f7">
<link rel="icon" href="{ICON}">
<link rel="alternate" type="application/atom+xml" title="{SITE_TITLE}" href="../feed.xml">
<style>{CSS}</style></head>
<body>
<div class="back"><a href="../index.html">← {SITE_TITLE}</a></div>
<div class="sheet">
  {hero}
  <div class="note">
    <h1>{html.escape(title)}</h1>
    <div class="meta"><span>{html.escape(d)}</span>{tag_html}</div>
    {''.join(body)}
    <div class="attach">本文也发布在 <a href="https://github.com/3038665474qq/zdr-notes">GitHub</a>，源码与脚本同仓。</div>
  </div>
</div>
<footer class="site"><div class="wrap">© {date.today().year} {SITE_TITLE} · <a href="https://github.com/3038665474qq">GitHub</a></div></footer>
</body></html>"""


def index_page(items: list[dict]) -> str:
    cards = []
    all_tags = []
    for it in items:
        for t in it["tags"]:
            if t not in all_tags:
                all_tags.append(t)
    for it in items:
        tags = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in it["tags"])
        thumb = f'<img class="thumb" src="{it["thumb"]}" alt="" loading="lazy">' if it["thumb"] else ""
        cards.append(
            f"""<li><a class="card" href="notes/{it['slug']}.html"
   data-title="{html.escape(it['title'])}"
   data-summary="{html.escape(it['summary'])}"
   data-tags="{html.escape(','.join(it['tags']))}"
   data-hay="{html.escape(' '.join([it['title'], it['summary'], ' '.join(it['tags'])]))}">
  {thumb}
  <div class="meta"><span>{html.escape(it['date'])}</span><span class="rt">{it['minutes']} 分钟</span>{tags}</div>
  <h2>{html.escape(it['title'])}</h2>
  <p>{html.escape(it['summary'])}</p>
  <span class="more">阅读 →</span>
</a></li>"""
        )

    chips = ['<button class="chip on" data-tag="all">全部</button>']
    chips += [f'<button class="chip" data-tag="{html.escape(t)}">{html.escape(t)}</button>' for t in all_tags]

    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE}</title>
<meta name="description" content="{SITE_DESC}">
<meta name="theme-color" content="#f3f5f7">
<link rel="icon" href="{ICON}">
<link rel="alternate" type="application/atom+xml" title="{SITE_TITLE}" href="feed.xml">
<style>{CSS}</style></head>
<body>
<header class="site"><div class="wrap">
  <h1>{SITE_TITLE}</h1>
  <p>{SITE_DESC}</p>
  <div class="tools">
    <div class="search">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.6-3.6"></path></svg>
      <input id="q" type="search" placeholder="搜索标题、正文、标签　按 / 聚焦" autocomplete="off" spellcheck="false" aria-label="搜索笔记">
      <kbd>/</kbd>
    </div>
    <div class="chips">{''.join(chips)}</div>
  </div>
  <span class="count"><span id="n">{len(items)}</span> 篇笔记<span id="filtered"></span></span>
</div></header>
<main class="wrap">
  <ol class="list">{''.join(cards)}</ol>
  <p class="empty" id="empty" hidden>没有匹配的笔记。换个词，或者按 Esc 清空。</p>
</main>
<footer class="site"><div class="wrap">© {date.today().year} {SITE_TITLE} · <a href="https://github.com/3038665474qq">GitHub</a> · <a href="feed.xml">RSS</a></div></footer>
<script>
(function () {{
  var q = document.getElementById('q');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var lis = cards.map(function (c) {{ return c.parentElement; }});
  var empty = document.getElementById('empty');
  var filtered = document.getElementById('filtered');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var state = {{ kw: '', tag: 'all' }};
  var loaded = false;

  function esc(s) {{
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }}
  function mark(text, kw) {{
    if (!kw) return esc(text);
    var i = text.toLowerCase().indexOf(kw);
    if (i < 0) return esc(text);
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + kw.length)) + '</mark>'
      + esc(text.slice(i + kw.length));
  }}

  function apply() {{
    var kw = state.kw.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (c, i) {{
      var okTag = state.tag === 'all' || (c.dataset.tags || '').split(',').indexOf(state.tag) >= 0;
      var okKw = !kw || (c.dataset.hay || '').toLowerCase().indexOf(kw) >= 0;
      var vis = okTag && okKw;
      lis[i].hidden = !vis;
      if (vis) shown++;
      var h = c.querySelector('h2'), p = c.querySelector('p');
      if (kw && vis) {{
        h.innerHTML = mark(c.dataset.title, kw);
        p.innerHTML = mark(c.dataset.summary, kw);
      }} else {{
        h.textContent = c.dataset.title;
        p.textContent = c.dataset.summary;
      }}
    }});
    empty.hidden = shown > 0;
    filtered.textContent = (kw || state.tag !== 'all') ? ' · 匹配 ' + shown : '';
  }}

  // 首次输入时把正文全文并进 haystack，失败就退化成标题+摘要搜索
  function loadText() {{
    if (loaded) return;
    loaded = true;
    if (!window.fetch) return;
    fetch('search.json').then(function (r) {{ return r.json(); }}).then(function (rows) {{
      var bySlug = {{}};
      rows.forEach(function (r) {{ bySlug[r.slug] = r.text || ''; }});
      cards.forEach(function (c) {{
        var slug = (c.getAttribute('href') || '').replace('notes/', '').replace('.html', '');
        if (bySlug[slug]) c.dataset.hay += ' ' + bySlug[slug];
      }});
      if (state.kw) apply();
    }}).catch(function () {{}});
  }}

  q.addEventListener('input', function () {{ loadText(); state.kw = q.value; apply(); }});
  q.addEventListener('focus', loadText);
  chips.forEach(function (b) {{
    b.addEventListener('click', function () {{
      chips.forEach(function (x) {{ x.classList.remove('on'); }});
      b.classList.add('on');
      state.tag = b.dataset.tag;
      apply();
    }});
  }});
  document.addEventListener('keydown', function (e) {{
    if (e.key === '/' && document.activeElement !== q) {{ e.preventDefault(); q.focus(); }}
    if (e.key === 'Escape' && document.activeElement === q) {{
      q.value = ''; state.kw = ''; apply(); q.blur();
    }}
  }});
}})();
</script>
</body></html>"""


def feed(items: list[dict]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = []
    for it in items[:20]:
        url = f"{SITE_URL}notes/{it['slug']}.html"
        d = it["date"] or "2026-01-01"
        entries.append(f"""  <entry>
    <title>{html.escape(it['title'])}</title>
    <link href="{url}"/>
    <id>{url}</id>
    <updated>{d}T00:00:00Z</updated>
    <summary>{html.escape(it['summary'])}</summary>
  </entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{SITE_TITLE}</title>
  <subtitle>{SITE_DESC}</subtitle>
  <link href="{SITE_URL}feed.xml" rel="self"/>
  <link href="{SITE_URL}"/>
  <id>{SITE_URL}</id>
  <updated>{now}</updated>
  <author><name>ZDR</name></author>
{chr(10).join(entries)}
</feed>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    a = ap.parse_args()

    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "notes").mkdir(parents=True)
    (DOCS / "assets").mkdir()

    items = []
    for d in sorted([p for p in NOTES.iterdir() if p.is_dir()]):
        md = d / "note.md"
        if not md.exists():
            print(f"skip {d.name}: 没有 note.md")
            continue
        slug = d.name
        meta, lines = parse_front_matter(md.read_text(encoding="utf-8"))
        body = parse_body(lines, slug)

        # 图片
        src_img = d / "images"
        cover = None
        if src_img.is_dir():
            dst = DOCS / "assets" / slug
            dst.mkdir(parents=True, exist_ok=True)
            for f in src_img.iterdir():
                if f.is_file():
                    shutil.copy2(f, dst / f.name)
            c = meta.get("cover", "")
            if c.startswith("images/"):
                cover = f"assets/{slug}/{c[7:]}"
                meta["cover"] = cover

        (DOCS / "notes" / f"{slug}.html").write_text(note_page(meta, body, slug, cover), encoding="utf-8")

        items.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "date": meta.get("date", ""),
            "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "summary": meta.get("summary", ""),
            "thumb": f'assets/{slug}/{Path(cover).name}' if cover else None,
            "mtime": md.stat().st_mtime,
            "text": plain_text(lines),
            "minutes": reading_minutes(lines),
            "order": int(meta.get("order", 0) or 0),
        })

    # 排序：order 大的在前（手动置顶/置底），同 order 按日期倒序，同日按修改时间
    items.sort(key=lambda x: (x["order"], x["date"], x["mtime"]), reverse=True)
    (DOCS / "index.html").write_text(index_page(items), encoding="utf-8")

    # 搜索索引：正文全文，供首页过滤用
    (DOCS / "search.json").write_text(
        json.dumps(
            [{k: it[k] for k in ("slug", "title", "date", "tags", "summary", "text")} for it in items],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # Atom feed
    (DOCS / "feed.xml").write_text(feed(items), encoding="utf-8")

    print(f"built {len(items)} note(s):")
    for it in items:
        print(f"  {it['date']}  {it['title']}")

    if a.serve:
        import http.server
        import socketserver
        import os

        os.chdir(DOCS)
        with socketserver.TCPServer(("127.0.0.1", 8000), http.server.SimpleHTTPRequestHandler) as srv:
            print("http://127.0.0.1:8000")
            srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
