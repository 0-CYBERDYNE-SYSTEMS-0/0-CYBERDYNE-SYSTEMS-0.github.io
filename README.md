# 0-CYBERDYNE-SYSTEMS-0 — Index

Source for **<https://0-cyberdyne-systems-0.github.io/>** — the hub that indexes every live site
and public repository on this account.

Static, single file, no build step, no runtime dependencies: `index.html` + `favicon.svg`,
served by GitHub Pages from `main`.

## Contents

- **Live sites** — every GitHub Pages site on this account, discovered from the Pages API.
- **Public repositories** — all public repos, grouped by project family, with client-side
  filter and search.

## Regenerating

Repo cards are generated from live GitHub data, so adding a public repo and re-running keeps
the hub current:

```sh
python3 build_hub.py            # uses the cached gh output
python3 build_hub.py --fresh    # re-queries the GitHub API first
```

Requires `gh` authenticated as `0-CYBERDYNE-SYSTEMS-0`. The live-site list is not hardcoded:
it probes `GET /repos/{owner}/{repo}/pages` for every public repo, so a new Pages site appears on
the next run without editing this file.

## Automatic refresh

`.github/workflows/refresh.yml` runs the generator daily at 06:17 UTC, on pushes to `main` that
are not index updates, and on manual dispatch. It commits `index.html` only when the generated
output actually changed.

## Not published here

Pages on this account is on the GitHub Free plan, which allows Pages in **public repositories
only**. Static sites that already exist in private repos (`twodogseeds.com`, `dds.com`,
`pii-guard-website`, `farmfriend-website`) cannot be served until they are made public or the
account is upgraded to Pro.
