# Auto-Release on Push to Main — Design Spec

**Date:** 2026-05-14  
**Status:** Approved

## Goal

Every push to `main` that passes CI automatically creates or updates a public GitHub Release tagged `latest`, with `AndroidTVADBControlCenter.exe` attached as a downloadable asset and a changelog from recent commits.

## Approach

Extend the existing `build-windows.yml` with a second job `release` that runs after `build` succeeds, only on `push` events (not PRs).

## Workflow Structure

```
jobs:
  build:       # existing — no changes
  release:     # new job
    needs: build
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: write
```

## Steps in `release` Job

1. **Checkout** — full history (`fetch-depth: 0`) needed for `git log`
2. **Download artifact** — `actions/download-artifact@v4`, artifact name `AndroidTVADBControlCenter-windows`
3. **Generate changelog** — `git log --oneline HEAD~10..HEAD`, stored in env var
4. **Delete existing `latest` release** — `gh release delete latest --yes --cleanup-tag` (silent if not exists)
5. **Create release** — `gh release create latest <exe> --title "Latest Build ($(date -u +%Y-%m-%d))" --notes "$CHANGELOG" --prerelease`

## Key Decisions

- Tag `latest` is reused and overwritten on every push — single permanent download URL
- Marked `--prerelease` to distinguish from semantic version releases
- Changelog = last 10 commits (`HEAD~10..HEAD`) — simple, no dependency on tags
- `gh` CLI is pre-installed on `ubuntu-latest` GitHub runners; no extra action needed
- `permissions: contents: write` is required at job level for release creation

## Permanent Download URL

```
https://github.com/<owner>/<repo>/releases/download/latest/AndroidTVADBControlCenter.exe
```

## Out of Scope

- Semantic versioning / version bumping
- Release notes beyond git log
- macOS or Linux builds
