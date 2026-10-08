# 0-CYBERDYNE-SYSTEMS-0 — Index

Source for **<https://0-cyberdyne-systems-0.github.io/>** — the hub that indexes every live site
and public repository on this account.

Static, single file, no build step, no runtime dependencies: `index.html` + `favicon.svg`,
served by GitHub Pages from `main`.

## Contents

- **Live sites** — the four published GitHub Pages sites on this account.
- **Public repositories** — all public repos, grouped by project family, with client-side
  filter and search.

## Regenerating

Repo cards are generated from live GitHub data, so adding a public repo and re-running keeps
the hub current:

```sh
python3 build_hub.py            # uses the cached gh output
python3 build_hub.py --fresh    # re-queries the GitHub API first
```

Requires `gh` authenticated as `0-CYBERDYNE-SYSTEMS-0`.

## Not published here

Pages on this account is on the GitHub Free plan, which allows Pages in **public repositories
only**. Static sites that already exist in private repos (`twodogseeds.com`, `dds.com`,
`pii-guard-website`, `farmfriend-website`) cannot be served until they are made public or the
account is upgraded to Pro.
