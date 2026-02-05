---
name: release
description: >
  Automate the full release process for any project: discover and bump version numbers
  across project files (package.json, manifest.json, etc.); update CHANGELOG.md with the
  [Unreleased] section contents; run tests and build; create a git tag; and push.
  Use when the user says "release", "cut a release", "bump version", "new version",
  "prepare release", "tag release", or similar release/versioning requests.
---

# Release Skill

Automate project release workflows. All steps run from the project root.

## Version File Discovery

Common files that may contain version numbers:

| File | Field / Pattern | Example |
|------|-----------------|---------|
| `package.json` | `"version": "X.Y.Z"` | `"version": "1.2.3"` |
| `manifest.json` | `"version": "X.Y.Z"` | `"version": "1.2.3"` |
| `pyproject.toml` | `version = "X.Y.Z"` | `version = "1.2.3"` |
| `Cargo.toml` | `version = "X.Y.Z"` | `version = "1.2.3"` |
| `*.md` files | `**Current Version:** X.Y.Z` or similar | varies |
| `version.txt` | Plain version number | `1.2.3` |

**Discovery Process:**
1. Check for `package.json` first (most common)
2. Search for other known version files in the project root
3. Grep for version patterns in markdown files if a project-specific version marker exists
4. Present discovered files to the user for confirmation before proceeding

All discovered version files MUST be updated to the same new version.

## CHANGELOG.md Convention

- Format: [Keep a Changelog](https://keepachangelog.com/)
- The `## [Unreleased]` section accumulates changes between releases.
- On release, rename `[Unreleased]` contents into a new `## [X.Y.Z] - YYYY-MM-DD` section and leave a fresh empty `## [Unreleased]` above it.
- Sections: Added, Changed, Fixed, Removed (only include sections that have entries).
- If no CHANGELOG.md exists, ask the user if they want to create one or skip changelog updates.

## Release Procedure

### 1. Discover version files and current version

Search the project for files containing version numbers:
- Read `package.json`, `manifest.json`, `pyproject.toml`, `Cargo.toml` if they exist
- Check for version markers in markdown files (CLAUDE.md, README.md, etc.)
- Report all discovered version files and their current versions to the user
- If versions are inconsistent across files, warn the user

### 2. Determine the new version

Ask the user which version to release. Follow semver (`MAJOR.MINOR.PATCH`). If the user says "patch", "minor", or "major", calculate the next version from the current one.

### 3. Verify preconditions

```bash
git status          # working tree must be clean (no uncommitted changes)
git branch --show-current   # note the current branch
```

If the tree is dirty, warn the user and ask how to proceed.
Note which branch we're on — user may want to release from main, master, or another branch.

### 4. Bump version in all discovered files

Edit each discovered version file, replacing the old version with the new one. Common patterns:

- **package.json** — `"version": "OLD"` -> `"version": "NEW"`
- **manifest.json** — `"version": "OLD"` -> `"version": "NEW"`
- **pyproject.toml** — `version = "OLD"` -> `version = "NEW"`
- **Cargo.toml** — `version = "OLD"` -> `version = "NEW"`
- **Markdown files** — Update version markers like `**Current Version:** OLD`

### 5. Update CHANGELOG.md (if present)

- Read CHANGELOG.md.
- Move contents under `## [Unreleased]` into a new section `## [NEW_VERSION] - YYYY-MM-DD` (use today's date).
- Leave a fresh empty `## [Unreleased]` section at the top (after the header).
- If `[Unreleased]` is empty, ask the user what to put in the changelog entry.
- If no CHANGELOG.md exists, skip this step or offer to create one.

### 6. Review README.md (optional)

If README.md exists, quickly scan for:
- Version numbers that should be updated
- Feature highlights that may need updating
- Installation instructions referencing the version

Ask the user if README.md needs updates for this release.

### 7. Run tests and build (if applicable)

Detect the project type and run appropriate commands:

- **Node.js** (package.json exists): `npm test && npm run build` (if build script exists)
- **Python** (pyproject.toml exists): `pytest` or project-specific test command
- **Rust** (Cargo.toml exists): `cargo test && cargo build --release`
- **Other**: Ask the user for the test/build commands

Both must pass. If tests fail, stop and report.

### 8. Commit the version bump

Stage all changed version files and commit:

```bash
git add <discovered-version-files> CHANGELOG.md
git commit -m "release: vNEW_VERSION"
```

Use the exact format `release: vX.Y.Z` for the commit message.

### 9. Create an annotated git tag

```bash
git tag -a vNEW_VERSION -m "vNEW_VERSION"
```

Tag format: `vX.Y.Z` (v prefix, semver).

### 10. Push commit and tag

```bash
git push origin <current-branch> && git push origin vNEW_VERSION
```

### 11. Summary

After pushing, print a summary:

```
Release vX.Y.Z complete.
- Version bumped in: <list of files>
- CHANGELOG.md updated (if applicable)
- Tag vX.Y.Z pushed to origin
- Check your CI/CD for any triggered release workflows
```

## Project-Specific Customization

If the project has specific release requirements documented in CLAUDE.md or a similar file, follow those instructions in addition to this general workflow. Common customizations include:

- Additional files to update with version numbers
- Specific test or build commands
- Pre-release or post-release scripts
- Release branch conventions
- npm publish, cargo publish, or other package registry publishing steps
