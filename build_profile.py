#!/usr/bin/env python3
"""Generate the profile banner/OG images and the profile README for 0-CYBERDYNE-SYSTEMS-0.

Outputs into ./profile/ :
  assets/profile-banner.png   1280x316  (README header)
  assets/og-image.png         1200x620  (link previews)
  README.md                    profile-page README

Repo data comes from live GitHub (or the build_hub.py cache).
"""
import json, re, html, subprocess, sys, pathlib, datetime
from PIL import Image, ImageDraw, ImageFont

SCRATCH = pathlib.Path("/Users/scrimwiggins/.hermes/cache/scratch")
ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "profile"
(OUT / "assets").mkdir(parents=True, exist_ok=True)

ACCENT = (0, 240, 255)
FG = (255, 255, 255)
SUB = (158, 158, 158)
DIM = (142, 142, 142)
BG = (11, 11, 11)
GRID_MINOR = (22, 22, 22)
GRID_MAJOR = (34, 34, 34)
HAIRLINE = (30, 30, 30)
CARD_BORDER = (52, 58, 66)
SEP = (34, 34, 34)

HN = "/System/Library/Fonts/HelveticaNeue.ttc"
MENLO = "/System/Library/Fonts/Menlo.ttc"
def sans(size, weight="regular"):
    idx = {"regular": 0, "bold": 1, "light": 7, "medium": 10}[weight]
    return ImageFont.truetype(HN, size, index=idx)
def mono(size, bold=False):
    return ImageFont.truetype(MENLO, size, index=1 if bold else 0)

# ---------------------------------------------------------------- repo data
CACHE = SCRATCH / "repos_all.json"
if CACHE.exists() and "--fresh" not in sys.argv:
    repos = json.load(open(CACHE))
else:
    out = subprocess.run(["gh", "repo", "list", "0-CYBERDYNE-SYSTEMS-0", "--limit", "400",
                          "--json", "name,description,isPrivate,primaryLanguage,"
                                    "repositoryTopics,pushedAt,stargazerCount"],
                         capture_output=True, text=True, check=True).stdout
    repos = json.loads(out)
    CACHE.write_text(out)
PUB = {r["name"]: r for r in repos if not r["isPrivate"]}
N = len(PUB)

LIVE = [
    ("0-CYBERDYNE-SYSTEMS-0.github.io", "The Index",
     "Hub", "This page's hub — every live site and public repository, filterable."),
    ("farmfriend-landing", "FarmFriend — Environmental Controller",
     "Product landing", "FarmFriend environmental controller — no subscriptions, no wiring. Pricing, FAQ, pre-order."),
    ("desmond-digital", "Desmond Digital",
     "Company site", "Headless autonomous agents that run unattended for days. Manifesto, architecture, pricing."),
    ("farmfriend-page", "FarmFriend Consulting",
     "One-pager", "FarmFriend consulting card — AI &amp; software development, booking, direct links."),
    ("sw33p3r", "sw33p3r — Field Docs",
     "Artifact docs", "Flipper Zero counter-surveillance suite: room-sweep control map and printable field guide."),
]

GROUPS = [
    ("FarmFriend &amp; Agriculture", [
        "FFT_nano", "FarmFriend-Terminal-React", "FF-SmartControl", "FF-Agri-Cal-Pro",
        "ff-land-plan", "ff-roundtable", "FF-Terminal-Skills", "FFT_demo_dash",
        "FFT_model_tune", "FF-Automator", "farm-lead-automation", "farm-lead-generation",
        "clockwork-ai", "visionbrain", "aerial-intelligence-pipeline", "CRS-01",
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
        "qwikNotes", "mlx-audio-tts", "opencodex",
    ]),
    ("Sites &amp; Publications", [
        "0-CYBERDYNE-SYSTEMS-0.github.io", "farmfriend-landing", "farmfriend-page",
        "desmond-digital", "sw33p3r", "ff-article-preview",
    ]),
    ("Meta &amp; Assets", [".github", "0-CYBERDYNE-SYSTEMS-0", "brand-assets",
                           "battleships", "omarchy_", "omarchy_clipboard", "CC_Leak"]),
]
placed = {n for _, names in GROUPS for n in names}
GROUPS[-1][1].extend(sorted(set(PUB) - placed))
assert {n for _, names in GROUPS for n in names} == set(PUB), "category coverage drift"

# ---------------------------------------------------------------- images
def tracked(d, xy, text, font, fill, spacing=0.0):
    """Draw text with extra letter-spacing (Pillow has none built in)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing
    return x


def banner(path, w, h, scale=1.0):
    """Dark header card: subtle grid texture, top-right glow, name, stats, bottom rule."""
    layer = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(layer, "RGBA")

    # --- texture grid (minor every cell, major every 4th line)
    cell = max(16, int(32 * scale))
    for x in range(0, w + 1, cell):
        c = GRID_MAJOR if (x // cell) % 4 == 0 else GRID_MINOR
        d.line([(x, 0), (x, h)], fill=c + (255,))
    for y in range(0, h + 1, cell):
        c = GRID_MAJOR if (y // cell) % 4 == 0 else GRID_MINOR
        d.line([(0, y), (w, y)], fill=c + (255,))

    # --- glow spilling in from the top-right corner (stays above the stats row)
    R = int(w * 0.36)
    cx, cy = int(w * 1.02), int(-h * 0.34)
    for i in range(R, 0, -3):
        a = int(40 * (1 - i / R) ** 1.8)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=ACCENT + (a,))

    # --- accent rule along the bottom of the card
    d.rectangle([0, h - 3, w, h], fill=ACCENT)

    pad = int(w * 0.050)

    # --- kicker
    y = int(h * 0.132)
    d.text((pad, y), "INDEX  \u00b7  EVERYTHING PUBLISHED", font=mono(int(15 * scale), True), fill=ACCENT)

    # --- title (slightly loosened tracking so the hyphens don't clog)
    y = int(h * 0.252)
    tracked(d, (pad, y), "0-CYBERDYNE-SYSTEMS-0", sans(int(52 * scale), "bold"), FG,
            spacing=1.2 * scale)

    # --- subtitle
    y = int(h * 0.478)
    d.text((pad, y), "R. Desmond \u2014 autonomous agents \u00b7 precision agriculture \u00b7 terminal-native interfaces",
           font=sans(int(21 * scale), "light"), fill=SUB)

    # --- rule: more air above than below so it groups with the stats row
    ry = int(h * 0.655)
    d.line([(pad, ry), (w - pad, ry)], fill=SEP + (255,))

    # --- stats band: flow-laid with equal gutters, URL as the 4th rightmost anchor
    labf = mono(int(11 * scale))
    urlf = mono(int(14 * scale))
    numf = mono(int(25 * scale), True)
    url = "0-cyberdyne-systems-0.github.io"
    y = int(h * 0.712)
    stats = [(str(len(LIVE)), "LIVE SITES"), (str(N), "PUBLIC REPOSITORIES"), ("2023", "BUILDING SINCE")]
    widths = [max(int(d.textlength(v, font=numf)), int(d.textlength(l, font=labf)))
              for v, l in stats]
    urlw = max(int(d.textlength(url, font=urlf)), int(d.textlength("INDEX", font=labf)))
    gutter = ((w - 2 * pad) - sum(widths) - urlw) // len(stats)
    x = pad
    for (val, lab), cw in zip(stats, widths):
        d.text((x, y), val, font=numf, fill=FG)
        d.text((x, y + int(33 * scale)), lab, font=labf, fill=DIM)
        x += cw + gutter
    d.text((x, y), url, font=urlf, fill=ACCENT)
    d.text((x, y + int(34 * scale)), "HUB", font=labf, fill=DIM)

    r = max(4, int(13 * scale))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(layer, (0, 0), mask)
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=r,
                                          outline=CARD_BORDER + (255,), width=1)
    img.save(path, optimize=True)
    return path

banner(OUT / "assets/profile-banner.png", 1280, 316)
banner(OUT / "assets/og-image.png", 1200, 620, scale=1.30)

# ---------------------------------------------------------------- README
def esc(s):
    return html.escape((s or "").strip(), quote=True)

def short(name, limit=118):
    t = re.sub(r"^\s*(Join Discord:\s*\S+\s*/?\s*)", "", PUB[name].get("description") or "").strip()
    if not t:
        return "\u2014"
    t = t.replace("|", "/")
    return t if len(t) <= limit else t[:limit - 1].rstrip() + "\u2026"

def live_url(slug):
    return ("https://0-cyberdyne-systems-0.github.io/"
            if slug == "0-CYBERDYNE-SYSTEMS-0.github.io"
            else f"https://0-cyberdyne-systems-0.github.io/{slug}/")

live_rows = "\n".join(
    f"| [**{title}**]({live_url(slug)}) | `{kind}` | {blurb} |"
    for slug, title, kind, blurb in LIVE)

group_blocks = ""
for i, (gname, names) in enumerate(GROUPS):
    names = sorted([n for n in names if n in PUB], key=str.lower)
    rows = "\n".join(f"| [**{esc(n)}**](https://github.com/0-CYBERDYNE-SYSTEMS-0/{esc(n)}) | {short(n)} |"
                     for n in names)
    group_blocks += f"""
<details{' open' if i < 2 else ''}>
<summary><b>{gname}</b> &nbsp;<code>{len(names)}</code></summary>
<br>

| Repository | About |
|---|---|
{rows}

</details>
"""

stats_line = (f"**{len(LIVE)}** live sites &nbsp;·&nbsp; **{N}** public repositories "
              f"&nbsp;·&nbsp; building since **2023**")

README = f"""<img src="https://0-cyberdyne-systems-0.github.io/assets/profile-banner.png" alt="0-CYBERDYNE-SYSTEMS-0 — everything published, in one place" width="100%">

### R. Desmond

AI systems engineer building autonomous agents, precision-agriculture tooling, and terminal-native
interfaces. I work across the stack — from Rust services and TypeScript runtimes to Python agent
frameworks and macOS automation.

{stats_line}

### [**\u2192 Browse everything: 0-cyberdyne-systems-0.github.io**](https://0-cyberdyne-systems-0.github.io/)

Live sites and all {N} public repositories, filterable. Everything below is on that page too.

---

## Live sites

| Site | Kind | What it is |
|---|---|---|
{live_rows}

---

## Public repositories &nbsp;<code>{N}</code>

{group_blocks}
---

## Stack

**Agent & LLM** — OpenAI, Anthropic, Google, DeepSeek, OpenRouter, Ollama, LM Studio, MiniMax

**Frontend** — React 18, TypeScript, Tailwind, shadcn/ui, Vite

**Backend** — Express, PostgreSQL + Drizzle, WebSocket, Go + Wails

**Systems** — Rust, Python, Node, Docker, SSH-based distribution

---

## Current focus

- Autonomous agent swarms for distributed computing
- Precision-agriculture AI — drone imagery, crop monitoring, field ops
- Terminal-native AI interfaces with multi-provider fallback
- macOS automation that stays on-device and offline-first

---

## Contact

- **Email**: [craigs.seller.sixx@gmail.com](mailto:craigs.seller.sixx@gmail.com)
- **Twitter / X**: [@twodogseeds](https://x.com/twodogseeds)
- **Web**: [farm-friend.com](https://farm-friend.com) &nbsp;·&nbsp; [desmond.digital](https://desmond.digital)

<sub>Index generated {datetime.date.today().isoformat()} · {N} public repositories · regenerate with <code>build_profile.py</code></sub>
"""

(OUT / "README.md").write_text(README, encoding="utf-8")
print("wrote", OUT / "README.md", len(README), "bytes")
print("wrote", OUT / "assets/profile-banner.png")
print("wrote", OUT / "assets/og-image.png")
print(f"live sites: {len(LIVE)} | public repos: {N} | groups: {len(GROUPS)}")
