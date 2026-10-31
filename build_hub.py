#!/usr/bin/env python3
"""Generate the 0-CYBERDYNE-SYSTEMS-0.github.io hub page from live GitHub data."""
import json, html, re, datetime, pathlib, sys, os, subprocess, concurrent.futures, urllib.request

SCRATCH = pathlib.Path(os.environ.get("HUB_CACHE_DIR", "/Users/scrimwiggins/.hermes/cache/scratch"))
OUT_DIR = pathlib.Path(__file__).resolve().parent if (pathlib.Path(__file__).resolve().parent / "index.html").exists() \
    else pathlib.Path.home() / "Documents/Agent-Workspace/deliverables/2026-10/github-pages-hub"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CACHE = SCRATCH / "repos_all.json"
if CACHE.exists() and "--fresh" not in sys.argv:
    repos = json.load(open(CACHE))
else:
    import subprocess
    out = subprocess.run(["gh", "repo", "list", "0-CYBERDYNE-SYSTEMS-0", "--limit", "400",
                          "--json", "name,description,homepageUrl,isPrivate,primaryLanguage,"
                                    "repositoryTopics,pushedAt,stargazerCount,licenseInfo"],
                         capture_output=True, text=True, check=True).stdout
    repos = json.loads(out)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(out)
pub = {r["name"]: r for r in repos if not r["isPrivate"]}

SITE_META = {
    "0-CYBERDYNE-SYSTEMS-0.github.io": (
        "The Index — you are here", "Hub",
        "This page. Links every live site and public repository on the account; filterable, and regenerated from live GitHub data."),
    "split-landing-pages": (
        "Product pages — Quorum, Lucida, Studio", "Product pages",
        "Three product pages built from real screenshots: an LLM roundtable, a page-by-page PDF teacher, and a natural-language creative coding workbench."),
    "ff-land-plan": (
        "FarmFriend Land Plan", "Product page",
        "Draw the beds the way they sit on the ground. One cell is 25 cm; the plan stays on your computer."),
    "farmfriend-landing": (
        "FarmFriend — Environmental Controller", "Product landing",
        "The product page for the FarmFriend environmental controller. Smart plugs from any store, no subscriptions, pricing and pre-order."),
    "desmond-digital": (
        "Desmond Digital", "Company site",
        "The agency site. Headless autonomous agents that run unattended for days. Manifesto, architecture, pricing, services."),
    "farmfriend-page": (
        "FarmFriend Consulting", "One-pager",
        "One-page consulting card: AI and software development, consultation booking, direct links out."),
    "sw33p3r": (
        "sw33p3r — Field Docs", "Artifact docs",
        "The published artifact set for the Flipper Zero counter-surveillance suite: room-sweep control map, printable field guide, hardware alternatives."),
}


def _pages(repo):
    p = subprocess.run(["gh", "api", f"repos/0-CYBERDYNE-SYSTEMS-0/{repo}/pages"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except Exception:
        return None


def _alive(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "hub-index"})
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status == 200
    except Exception:
        return False


def discover_sites():
    names = sorted(pub)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        pages = dict(zip(names, ex.map(_pages, names)))
    rows = []
    for name in names:
        d = pages.get(name) or {}
        if name != "0-CYBERDYNE-SYSTEMS-0.github.io":
            if not d.get("html_url"):
                continue
            if not _alive(d["html_url"]):
                print("WARN: pages enabled but not serving, skipped:", name, file=sys.stderr)
                continue
        meta = SITE_META.get(name)
        if meta:
            title, kind, blurb = meta
        else:
            title = name.replace("-", " ").replace("_", " ").title()
            kind = "Docs" if (d.get("source") or {}).get("path", "/").strip("/") else "Site"
            blurb = (pub[name].get("description") or "").strip() or "Published site."
        branch = (d.get("source") or {}).get("branch") or "main"
        path = (d.get("source") or {}).get("path") or "/"
        src = branch + (":" + path if path not in ("", "/") else "")
        updated = (pub[name].get("pushedAt") or "")[:10]
        rows.append((title, name, blurb, kind, src, updated))
    def rank(r):
        if r[1] == "0-CYBERDYNE-SYSTEMS-0.github.io": return 0
        if r[1] == "split-landing-pages": return 1
        if r[1] == "ff-land-plan": return 2
        return 3
    rows.sort(key=lambda r: (rank(r), r[0].lower()))
    return rows


LIVE = discover_sites()
pathlib.Path(__file__).with_name("sites.json").write_text(
    json.dumps([{"slug": r[1], "title": r[0], "blurb": r[2], "kind": r[3], "source": r[4], "updated": r[5]} for r in LIVE], indent=1))

GROUPS = [
    ("FarmFriend &amp; Agriculture", [
        "FFT_nano", "FarmFriend-Terminal-React", "FF-SmartControl", "FF-Agri-Cal-Pro",
        "ff-land-plan", "ff-roundtable", "FF-Terminal-Skills", "FFT_demo_dash",
        "FFT_model_tune", "FF-Automator",
        "farm-lead-automation", "farm-lead-generation",
        "clockwork-ai", "visionbrain", "aerial-intelligence-pipeline", "CRS-01",
        "farmfriend-landing", "farmfriend-page",
    ]),
    ("Agents &amp; Harnesses", [
        "ruflo", "qm", "fable-os", "tiny_agent", "auto-experiment", "autonomous-macos-agent",
        "agent-desktop", "agent-deeplink-protocol", "nanoCore_TUI", "octopi-neural-mesh",
        "my-aperant", "OpenSage_TDS", "TDS-Eigent", "make-real-TDS", "vix-tds",
        "free-code", "gajae-code", "claw-code-parity", "ai-claude-start-droid-v2",
        "Brok-Gots", "buzz", "dds-kuse-cowork", "deepseek-oracle-mcp", "expert-prompting-eval",
        "dash",
    ]),
    ("Hermes", [
        "hermes-agent-fork", "hermes-bots", "hermes-esp32-t-embed", "hermes-example-plugins",
        "hermes-hive", "hermes-teams", "herdr-dev-team", "profile-studio",
        "generative-cockpit", "theme-lab", "skill-mechanic-skill",
    ]),
    ("Terminal, Themes &amp; Dev Tools", [
        "macOS-terminal-theme-picker", "terminal-theme-studio", "Terminal-Color-Tool",
        "term-fig", "tui-studio", "shortcut-genius", "MermaidMagic", "wordPlay",
        "qwikNotes", "mlx-audio-tts", "opencodex", "ffmpeg-skill", "rtl-sdr-station",
    ]),
    ("Products &amp; Apps", [
        "quorum", "lucida", "possibility-studio",
    ]),
    ("Sites &amp; Publications", [
        "0-CYBERDYNE-SYSTEMS-0.github.io", "split-landing-pages", "sw33p3r", "ff-article-preview",
    ]),
    ("Meta &amp; Assets", [
        ".github", "0-CYBERDYNE-SYSTEMS-0", "brand-assets", "battleships", "desmond-digital",
        "omarchy_", "omarchy_clipboard", "CC_Leak",
    ]),
]

placed = {n for _, names in GROUPS for n in names}
missing = sorted(set(pub) - placed)
extra = sorted(placed - set(pub))
if extra:
    print("WARN: named but not public:", extra, file=sys.stderr)
if missing:
    print("WARN: unplaced public repos -> Meta:", missing, file=sys.stderr)
    GROUPS[-1][1].extend(missing)

LANG_COLOR = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "Rust": "#dea584", "C": "#555555", "C++": "#f34b7d", "Go": "#00ADD8",
    "Swift": "#F05138", "Kotlin": "#A97BFF", "HTML": "#e34c26", "QML": "#44a51c",
    "Shell": "#89e051", "CSS": "#563d7c", "-": "#666",
}

def esc(s):
    return html.escape((s or "").strip(), quote=True)

def repo_card(name):
    r = pub[name]
    lang = (r.get("primaryLanguage") or {}).get("name", "-")
    color = LANG_COLOR.get(lang, "#666")
    topics = "".join(x["name"] for x in (r.get("repositoryTopics") or []))
    desc = r.get("description") or ""
    desc = re.sub(r"^\s*(Join Discord:\s*\S+\s*/?\s*)", "", desc).strip()
    if not desc:
        desc = "&nbsp;"
    tags = (f'<span class="tag">{lang}</span>' if lang != "-" else "")
    return (
        f'<a class="card repo" href="https://github.com/0-CYBERDYNE-SYSTEMS-0/{esc(name)}" '
        f'target="_blank" rel="noopener" data-t="{esc(name + " " + desc + " " + topics)}">'
        f'<div class="card-h"><span class="dot" style="background:{color}"></span>'
        f'<span class="repo-name">{esc(name)}</span></div>'
        f'<p class="repo-desc">{desc}</p>'
        f'<div class="tags">{tags}</div></a>'
    )

live_cards = ""
for title, repo, blurb, kind, src, built in LIVE:
    href = ("https://0-cyberdyne-systems-0.github.io/" if repo == "0-CYBERDYNE-SYSTEMS-0.github.io"
            else f"https://0-cyberdyne-systems-0.github.io/{repo}/")
    tail = "you are here" if repo == "0-CYBERDYNE-SYSTEMS-0.github.io" else f"{repo}/"
    live_cards += f'''<a class="card live" href="{href}" target="_blank" rel="noopener">
<div class="card-h"><span class="pill">LIVE</span><span class="repo-name">{title}</span></div>
<p class="repo-desc">{blurb}</p>
<div class="meta"><span class="mono">{tail}</span><span class="mono">{src}</span><span class="mono">updated {built}</span></div></a>'''

groups_html = ""
for gname, names in GROUPS:
    names = [n for n in names if n in pub]
    cards = "".join(repo_card(n) for n in sorted(names, key=str.lower))
    groups_html += f'''<section class="group" data-g="{esc(re.sub("&amp;", "and", gname))}">
<h2>{gname} <span class="count">{len(names)}</span></h2>
<div class="grid">{cards}</div></section>'''

today = datetime.date.today().isoformat()
n_pub = len(pub)

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>0-CYBERDYNE-SYSTEMS-0 — Index</title>
<meta name="description" content="Index of everything published by 0-CYBERDYNE-SYSTEMS-0 — live sites and {n_pub} public repositories. FarmFriend, Desmond Digital, Hermes tooling.">
<meta property="og:type" content="website">
<meta property="og:title" content="0-CYBERDYNE-SYSTEMS-0 — Index">
<meta property="og:description" content="Live sites and {n_pub} public repositories. FarmFriend, Desmond Digital, Hermes tooling.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#0a0a0a; --panel:#0d0d0d; --panel2:#111; --line:#1a1a1a; --line2:#262626;
    --fg:#ffffff; --muted:#888; --dim:#666; --accent:#00f0ff;
    --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); font-family:var(--sans);
         font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width:1140px; margin:0 auto; padding:0 24px 96px; }}
  .mono {{ font-family:var(--mono); font-size:11.5px; letter-spacing:.02em; }}
  a {{ color:inherit; text-decoration:none; }}

  header {{ padding:72px 0 40px; border-bottom:1px solid var(--line); }}
  .kicker {{ font-family:var(--mono); font-size:11.5px; color:var(--accent);
            text-transform:uppercase; letter-spacing:.18em; margin:0 0 18px; }}
  h1 {{ font-size:clamp(30px,5vw,50px); line-height:1.05; margin:0 0 16px;
       font-weight:800; letter-spacing:-.03em; }}
  h1 .thin {{ font-weight:300; color:var(--dim); }}
  .lede {{ color:var(--muted); max-width:62ch; margin:0 0 30px; font-weight:300; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:34px; }}
  .stat b {{ display:block; font-family:var(--mono); font-size:22px; color:var(--fg); font-weight:500; }}
  .stat span {{ font-family:var(--mono); font-size:11px; color:var(--dim);
               text-transform:uppercase; letter-spacing:.12em; }}
  .toplinks {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:32px; }}
  .toplinks a {{ font-family:var(--mono); font-size:11.5px; padding:8px 14px;
                border:1px solid var(--line2); border-radius:5px; color:var(--muted);
                transition:.15s; }}
  .toplinks a:hover {{ color:var(--accent); border-color:var(--accent); }}

  section {{ padding-top:56px; }}
  h2 {{ font-size:13px; font-family:var(--mono); text-transform:uppercase;
       letter-spacing:.14em; color:var(--muted); margin:0 0 20px; font-weight:500;
       display:flex; align-items:center; gap:12px; }}
  h2 .count {{ color:var(--dim); font-size:11px;
              border:1px solid var(--line2); border-radius:20px; padding:1px 8px; }}
  .grid {{ display:grid; gap:14px; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); }}

  .card {{ display:flex; flex-direction:column; background:var(--panel);
          border:1px solid var(--line); border-radius:8px; padding:18px;
          transition:border-color .15s, background .15s, transform .15s; }}
  .card:hover {{ border-color:var(--accent); background:var(--panel2); transform:translateY(-2px); }}
  .card-h {{ display:flex; align-items:center; gap:9px; margin-bottom:9px; }}
  .dot {{ width:9px; height:9px; border-radius:50%; flex:none; }}
  .repo-name {{ font-weight:600; font-size:14.5px; letter-spacing:-.01em;
               overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .repo-desc {{ color:var(--muted); font-size:13.2px; font-weight:300; margin:0;
               flex:1; }}
  .tags {{ margin-top:14px; display:flex; gap:7px; }}
  .tag {{ font-family:var(--mono); font-size:10.5px; color:var(--dim);
         border:1px solid var(--line2); border-radius:4px; padding:2px 7px; }}
  .pill {{ font-family:var(--mono); font-size:9.5px; letter-spacing:.14em;
          color:#0a0a0a; background:var(--accent); border-radius:3px;
          padding:2px 6px; font-weight:500; flex:none; }}
  .card.live .repo-name {{ color:var(--fg); }}
  .card.live .meta {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:14px;
                     color:var(--dim); }}
  .card.live:hover .meta .mono:first-child {{ color:var(--accent); }}

  .tools {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center;
           margin:0 0 8px; position:sticky; top:0; z-index:5;
           background:linear-gradient(180deg,var(--bg) 70%,transparent); padding:14px 0; }}
  #q {{ flex:1; min-width:200px; background:var(--panel); border:1px solid var(--line2);
       color:var(--fg); font-family:var(--mono); font-size:12.5px; padding:10px 13px;
       border-radius:6px; outline:none; }}
  #q:focus {{ border-color:var(--accent); }}
  #q::placeholder {{ color:#555; }}
  .chip {{ font-family:var(--mono); font-size:11px; color:var(--muted);
          border:1px solid var(--line2); background:var(--panel); border-radius:20px;
          padding:7px 13px; cursor:pointer; transition:.15s; user-select:none; }}
  .chip:hover {{ color:var(--fg); }}
  .chip.on {{ color:#0a0a0a; background:var(--accent); border-color:var(--accent); }}
  .empty {{ color:var(--dim); font-family:var(--mono); font-size:12.5px;
           padding:30px 0; display:none; }}

  footer {{ margin-top:76px; padding-top:28px; border-top:1px solid var(--line);
           display:flex; flex-wrap:wrap; gap:14px; justify-content:space-between;
           color:var(--dim); font-family:var(--mono); font-size:11.5px; }}
  footer a:hover {{ color:var(--accent); }}
  @media (max-width:560px) {{ header {{ padding-top:52px; }} .stats {{ gap:22px; }} }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <p class="kicker">Index</p>
  <h1>0-CYBERDYNE-SYSTEMS-0<br><span class="thin">Everything published, in one place.</span></h1>
  <p class="lede">The live sites that matter, plus every public repository on the account.
  Product pages, field docs, and the tooling behind them.</p>
  <div class="stats">
    <div class="stat"><b>{len(LIVE)}</b><span>Live sites</span></div>
    <div class="stat"><b>{n_pub}</b><span>Public repos</span></div>
    <div class="stat"><b>2023</b><span>Building since</span></div>
  </div>
  <div class="toplinks">
    <a href="#live">All {len(LIVE)} live sites &darr;</a>
    <a href="https://0-cyberdyne-systems-0.github.io/split-landing-pages/" target="_blank" rel="noopener">Product pages &rarr;</a>
    <a href="https://0-cyberdyne-systems-0.github.io/sw33p3r/" target="_blank" rel="noopener">Field docs &rarr;</a>
    <a href="https://github.com/0-CYBERDYNE-SYSTEMS-0" target="_blank" rel="noopener">GitHub &rarr;</a>
    <a href="#repos">Browse repositories &rarr;</a>
  </div>
</header>

<section id="live">
  <h2>Live sites <span class="count">{len(LIVE)}</span></h2>
  <div class="grid">{live_cards}</div>
</section>

<section id="repos">
  <h2>Public repositories <span class="count">{n_pub}</span></h2>
  <div class="tools">
    <input id="q" type="search" placeholder="Filter repositories…" autocomplete="off">
    <div class="chip on" data-f="all">All</div>
    <div class="chip" data-f="FarmFriend and Agriculture">FarmFriend</div>
    <div class="chip" data-f="Agents and Harnesses">Agents</div>
    <div class="chip" data-f="Hermes">Hermes</div>
    <div class="chip" data-f="Terminal, Themes and Dev Tools">Terminal</div>
    <div class="chip" data-f="Products and Apps">Products</div>
    <div class="chip" data-f="Sites and Publications">Sites</div>
    <div class="chip" data-f="Meta and Assets">Meta</div>
  </div>
  <p class="empty" id="empty">Nothing matches that filter.</p>
  {groups_html}
</section>

<footer>
  <span>0-CYBERDYNE-SYSTEMS-0 &middot; R. Desmond &middot; index generated {today}</span>
  <span>Hosted on GitHub Pages &middot; <a href="https://github.com/0-CYBERDYNE-SYSTEMS-0/0-CYBERDYNE-SYSTEMS-0.github.io" target="_blank" rel="noopener">source</a></span>
</footer>

</div>
<script>
  var q = document.getElementById('q'),
      chips = [].slice.call(document.querySelectorAll('.chip')),
      groups = [].slice.call(document.querySelectorAll('.group')),
      cards = [].slice.call(document.querySelectorAll('.repo')),
      empty = document.getElementById('empty'),
      filter = 'all';

  function apply() {{
    var term = q.value.trim().toLowerCase(), shown = 0;
    groups.forEach(function (g) {{
      var gOK = (filter === 'all' || g.dataset.g === filter), vis = 0;
      [].slice.call(g.querySelectorAll('.repo')).forEach(function (c) {{
        var ok = gOK && (!term || c.dataset.t.toLowerCase().indexOf(term) > -1);
        c.style.display = ok ? '' : 'none';
        if (ok) vis++;
      }});
      g.style.display = vis ? '' : 'none';
      g.querySelector('.count').textContent = vis;
      shown += vis;
    }});
    empty.style.display = shown ? 'none' : 'block';
  }}
  q.addEventListener('input', apply);
  chips.forEach(function (c) {{
    c.addEventListener('click', function () {{
      chips.forEach(function (x) {{ x.classList.remove('on'); }});
      c.classList.add('on');
      filter = c.dataset.f;
      apply();
    }});
  }});
  apply();
</script>
</body>
</html>
'''

favicon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#0a0a0a"/>
<circle cx="32" cy="32" r="18" fill="none" stroke="#00f0ff" stroke-width="3"/>
<circle cx="32" cy="32" r="6" fill="#00f0ff"/>
<path d="M32 8v10M32 46v10M8 32h10M46 32h10" stroke="#00f0ff" stroke-width="3" stroke-linecap="round"/>
</svg>
'''

_unused_readme = f'''# 0-CYBERDYNE-SYSTEMS-0 — Index

Source for <https://0-cyberdyne-systems-0.github.io/> — the hub that indexes every live site
and public repository on this account.

Single file, no build step, no dependencies: `index.html` plus `favicon.svg`.
Repository cards are generated from live GitHub data (`build_hub.py` in the workspace).

Deployed by GitHub Pages from `main` (legacy branch build).
'''

for name, body in (("index.html", HTML), ("favicon.svg", favicon), (".nojekyll", "")):
    (OUT_DIR / name).write_text(body, encoding="utf-8")
    print("wrote", OUT_DIR / name, len(body), "bytes")
print("repos in hub:", n_pub, "| groups:", len(GROUPS))
