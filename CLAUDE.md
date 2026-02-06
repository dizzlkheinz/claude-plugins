# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Claude Code Plugin Marketplace** - a distribution system for reusable skills and plugins. Plugins are documentation-driven; Claude Code instances read SKILL.md files to understand how to execute workflows.

## Architecture

```
claude-plugins/
├── .claude-plugin/marketplace.json    # Central plugin registry
├── CLAUDE.md
├── README.md
├── plugins/
│   ├── release/                       # Release automation plugin
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/release/SKILL.md
│   └── ai-council/                    # Multi-AI consultation plugin
│       ├── .claude-plugin/plugin.json
│       ├── scripts/consult.py
│       └── skills/ai-council/SKILL.md
```

**Key Pattern**: Each plugin lives in `/plugins/<name>/` and is registered in `marketplace.json`. Skills expose their behavior through `SKILL.md` files with YAML frontmatter defining triggers.

## Plugins

### Release Plugin
Automates release workflows for any project type (Node.js, Python, Rust, etc.):
- Discovers version in package.json, manifest.json, pyproject.toml, Cargo.toml, version.txt
- Updates CHANGELOG.md `[Unreleased]` section
- Creates annotated git tags and pushes

Trigger: `/release` or "cut a release", "bump version"

### AI Council Plugin
Orchestrates multi-AI consultations via CLI tools:
- Agents: Claude CLI, Gemini CLI, Codex CLI, Perplexity API
- Multi-round discussions with parallel execution
- Pure Python with no external dependencies

Trigger: `/consult` or "ask the council", "multi-AI discussion"

## Development

**No build system** - this is a plugin distribution repository. Scripts use only standard library tools.

### Adding a New Plugin
1. Create `/plugins/<name>/` directory
2. Add `SKILL.md` with YAML frontmatter (name, description, triggers)
3. Register in `.claude-plugin/marketplace.json`
4. Optional: Add executable scripts in `/plugins/<name>/scripts/`

### Plugin Installation (for users)
```bash
/plugin marketplace add dizzlkheinz/claude-plugins
/plugin install release@kdizzl-plugins
/plugin install ai-council@kdizzl-plugins
```

## Conventions

- **Documentation-first**: Always start with SKILL.md when understanding a plugin
- **Zero dependencies**: Scripts use only stdlib for cross-platform compatibility
- **Natural language triggers**: Skills respond to phrases, not just slash commands
- **Version consistency**: Release plugin enforces matching versions across all config files
