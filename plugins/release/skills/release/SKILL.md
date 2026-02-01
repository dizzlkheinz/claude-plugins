---
name: release
description: >
  Automate the full release process for the ynab-mcpb project: bump version numbers
  across package.json, manifest.json, and CLAUDE.md; update CHANGELOG.md with the
  [Unreleased] section contents; run tests and build; create a git tag; and push.
  Use when the user says "release", "cut a release", "bump version", "new version",
  "prepare release", "tag release", or similar release/versioning requests.
---

# Release Skill

Automate the ynab-mcpb release workflow. All steps run from the project root.

## Files That Contain the Version

| File | Field / Line | Example |
|------|-------------|---------|
| `package.json` | `"version": "X.Y.Z"` | `"version": "0.19.0"` |
| `manifest.json` | `"version": "X.Y.Z"` | `"version": "0.19.0"` |
| `CLAUDE.md` | `**Current Version:** X.Y.Z` | `**Current Version:** 0.19.0` |

All three MUST be updated to the same new version.

## CHANGELOG.md Convention

- Format: [Keep a Changelog](https://keepachangelog.com/)
- The `## [Unreleased]` section accumulates changes between releases.
- On release, rename `[Unreleased]` contents into a new `## [X.Y.Z] - YYYY-MM-DD` section and leave a fresh empty `## [Unreleased]` above it.
- Sections: Added, Changed, Fixed, Removed (only include sections that have entries).

## Release Procedure

### 1. Determine the new version

Ask the user which version to release. Follow semver (`MAJOR.MINOR.PATCH`). If the user says "patch", "minor", or "major", calculate the next version from the current one in `package.json`.

### 2. Verify preconditions

```
git status          # working tree must be clean (no uncommitted changes)
git branch --show-current   # should be on master
```

If the tree is dirty or not on master, warn the user and ask how to proceed.

### 3. Bump version in all files

Edit these three files, replacing the old version with the new one:

- **package.json** — `"version": "OLD"` -> `"version": "NEW"`
- **manifest.json** — `"version": "OLD"` -> `"version": "NEW"`
- **CLAUDE.md** — `**Current Version:** OLD` -> `**Current Version:** NEW`

### 4. Update CHANGELOG.md

- Read CHANGELOG.md.
- Move contents under `## [Unreleased]` into a new section `## [NEW_VERSION] - YYYY-MM-DD` (use today's date).
- Leave a fresh empty `## [Unreleased]` section at the top (after the header).
- If `[Unreleased]` is empty, ask the user what to put in the changelog entry.

### 5. Review README.md

Read `README.md` and verify it is still accurate for this release:

- **Tool count** — line mentioning "N tools" must match the actual number of registered tools.
- **Feature highlights** — any new major feature from the changelog should be mentioned if it's user-facing.
- **Installation instructions** — package name, npx command, and config snippets are correct.
- **Bank presets** — if reconciliation presets were added/removed, update the list.
- **Links** — repo URLs, docs links, and badge URLs are not broken.

If anything is stale, fix it and include `README.md` in the release commit (step 7). If everything looks good, move on.

### 6. Run tests and build

```bash
npm test && npm run build:prod
```

Both must pass. If tests fail, stop and report.

### 7. Commit the version bump

Stage only the changed files and commit:

```bash
git add package.json manifest.json CLAUDE.md CHANGELOG.md
git commit -m "release: vNEW_VERSION"
```

If README.md was updated in step 5, include it:

```bash
git add package.json manifest.json CLAUDE.md CHANGELOG.md README.md
```

Use the exact format `release: vX.Y.Z` for the commit message.

### 8. Create an annotated git tag

```bash
git tag -a vNEW_VERSION -m "vNEW_VERSION"
```

Tag format: `vX.Y.Z` (v prefix, semver).

### 9. Push commit and tag

```bash
git push origin master && git push origin vNEW_VERSION
```

This triggers the GitHub Actions release workflow (`.github/workflows/release.yml`) which builds and publishes the `.mcpb` file.

### 10. Summary

After pushing, print a summary:

```
Release vX.Y.Z complete.
- Version bumped in package.json, manifest.json, CLAUDE.md
- CHANGELOG.md updated
- Tag vX.Y.Z pushed to origin
- GitHub Actions release workflow triggered
```
