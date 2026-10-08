#!/usr/bin/env python3
"""Generate the profile banner/OG images and the profile README for 0-CYBERDYNE-SYSTEMS-0.

Outputs into ./profile/ :
  assets/profile-banner.png   1280x380  (README header)
  assets/og-image.png         1200x630  (link previews)
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
MUTED = (136, 136, 136)
DIM = (102, 102, 102)
BG = (10, 10, 10)
LINE = (26, 26, 26)
DOT = (23, 23, 23)

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
        "farmfriend-landing", "farmfriend-page", "desmond-digital", "sw33p3r",
        "ff-article-preview",
    ]),
    ("Meta &amp; Assets", [".github", "0-CYBERDYNE-SYSTEMS-0", "brand-assets",
                           "battleships", "omarchy_", "omarchy_clipboard", "CC_Leak"]),
]
placed = {n for _, names in GROUPS for n in names}
GROUPS[-1][1].extend(sorted(set(PUB) - placed))
assert {n for _, names in GROUPS for n in names} == set(PUB), "category coverage drift"

# ---------------------------------------------------------------- images
def banner(path, w, h, scale=1.0):
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img, "RGBA")

    for x in range(0, w, 28):
        for y in range(0, h, 28):
            d.point((x, y), fill=DOT + (255,))
    for i in range(240, 0, -6):
        a = int(26 * (i / 240) ** 2.4)
        d.ellipse([w - 210 - i, -150 - i, w - 210 + i, -150 + i], fill=ACCENT + (a,))

    pad = int(w * 0.062)
    d.rectangle([0, h - 3, w, h], fill=ACCENT)
    d.rectangle([0, 0, w, 1], fill=LINE)

    y = int(h * 0.15)
    d.text((pad, y), "INDEX  \u00b7  EVERYTHING PUBLISHED", font=mono(int(15 * scale), True), fill=ACCENT)
    y += int(40 * scale)
    d.text((pad, y), "0-CYBERDYNE-SYSTEMS-0", font=sans(int(54 * scale), "bold"), fill=FG)
    y += int(74 * scale)
    d.text((pad, y), "R. Desmond \u2014 autonomous agents \u00b7 precision agriculture \u00b7 terminal-native interfaces",
           font=sans(int(21 * scale), "light"), fill=MUTED)
    y += int(50 * scale)

    stats = [(str(len(LIVE)), "LIVE SITES"), (str(N), "PUBLIC REPOSITORIES"), ("2023", "BUILDING SINCE")]
    labf = mono(int(11 * scale))
    col = max(int(d.textlength(lab, font=labf)) for _, lab in stats) + int(36 * scale)
    col = min(col, (w - 2 * pad) // len(stats) + int(20 * scale))
    x = pad
    for val, lab in stats:
        d.text((x, y), val, font=mono(int(24 * scale), True), fill=FG)
        d.text((x, y + int(34 * scale)), lab, font=labf, fill=DIM)
        x += col

    d.rectangle([pad, int(h * 0.79), pad + int(10 * scale), int(h * 0.79) + int(10 * scale)],
                fill=ACCENT)
    d.text((pad + int(20 * scale), int(h * 0.78)), "0-cyberdyne-systems-0.github.io",
           font=mono(int(14 * scale)), fill=ACCENT)

    img.save(path, optimize=True)
    return path

banner(OUT / "assets/profile-banner.png", 1280, 330)
banner(OUT / "assets/og-image.png", 1200, 560, scale=1.28)

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

badges = (
    f"[![Live sites](https://img.shields.io/badge/live_sites-{len(LIVE)}-00f0ff?style=flat-square&labelColor=0a0a0a)]"
    f"(https://0-cyberdyne-systems-0.github.io/) "
    f"[![Public repos](https://img.shields.io/badge/public_repos-{N}-00f0ff?style=flat-square&labelColor=0a0a0a)]"
    f"(https://github.com/0-CYBERDYNE-SYSTEMS-0?tab=repositories) "
    f"[![Since](https://img.shields.io/badge/since-2023-00f0ff?style=flat-square&labelColor=0a0a0a)]"
    f"(https://github.com/0-CYBERDYNE-SYSTEMS-0)"
)

README = f"""<img src="https://0-cyberdyne-systems-0.github.io/assets/profile-banner.png" alt="0-CYBERDYNE-SYSTEMS-0 — everything published, in one place" width="100%">

### R. Desmond

AI systems engineer building autonomous agents, precision-agriculture tooling, and terminal-native
interfaces. I work across the stack — from Rust services and TypeScript runtimes to Python agent
frameworks and macOS automation.

{badges}

### **[→ Browse everything: 0-cyberdyne-systems-0.github.io](https://0-cyberdyne-systems-0.github.io/)**

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
