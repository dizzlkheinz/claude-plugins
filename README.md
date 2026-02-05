# kdizzl-plugins

A Claude Code plugin marketplace for workflow automation.

## Plugins

### release

Automates the full release process for any project:

- Discovers version numbers in `package.json`, `manifest.json`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `Cargo.toml`, `version.txt`
- Updates `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) format
- Reviews `README.md` for accuracy
- Runs project-specific tests and builds
- Creates an annotated git tag and pushes to origin

Trigger with `/release` or by saying "cut a release", "bump version", etc.

### ai-council

Orchestrates multi-AI consultations using available CLI tools and APIs:

- Queries Claude CLI, Gemini CLI, Codex CLI, and Perplexity API in parallel
- Supports multi-round discussions where agents see previous responses
- Gracefully handles unavailable tools
- Pure Python with no external dependencies

Trigger with `/consult` or by saying "ask the council", "consult", "multi-AI discussion", etc.

## Installation

```bash
/plugin marketplace add dizzlkheinz/claude-plugins
/plugin install release@kdizzl-plugins
/plugin install ai-council@kdizzl-plugins
```

## Updating

```bash
/plugin marketplace update kdizzl-plugins
```

## License

MIT
