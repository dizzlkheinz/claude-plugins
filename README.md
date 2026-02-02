# kdizzl-plugins

A Claude Code plugin marketplace for workflow automation.

## Plugins

### release

Automates the full release process for the [ynab-mcpb](https://github.com/dizzlkheinz/ynab-mcpb) project:

- Bumps version across `package.json`, `manifest.json`, and `CLAUDE.md`
- Updates `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) format
- Reviews `README.md` for accuracy
- Runs tests and builds
- Creates an annotated git tag and pushes to origin

Trigger with `/release` or by saying "cut a release", "bump version", etc.

## Installation

```
/plugin marketplace add dizzlkheinz/claude-plugins
/plugin install release@kdizzl-plugins
```

## Updating

```
/plugin marketplace update kdizzl-plugins
```

## License

MIT
