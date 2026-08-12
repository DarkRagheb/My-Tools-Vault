# Desktop App Architecture

TorBot is CLI-first. The optional desktop experience is provided by
[TorBotApp](https://github.com/KingAkeem/TorBotApp), a separate Electron and
React project.

Keeping the app separate preserves a lightweight Python install for CLI users:

- TorBot owns the Python package, command-line crawler, and library modules.
- TorBotApp owns the desktop UI, Electron packaging, and Node dependency tree.
- Backend crawl services expose the API consumed by TorBotApp.

## Launching from TorBot

The CLI can launch TorBotApp when it is installed locally:

```sh
torbot app
```

Discovery order:

1. `--app-dir /path/to/TorBotApp`
2. `TORBOT_APP_DIR=/path/to/TorBotApp`
3. A sibling `TorBotApp` directory next to this repository

If the app is not found, TorBot prints setup guidance and exits without changing
normal CLI behavior.

## Expected development layout

```text
code/
+-- TorBot/
+-- TorBotApp/
+-- gotor/
```

TorBotApp currently talks to the GoTor job-control API. If this Python package
later grows a compatible `torbot serve` API, TorBotApp can support either
backend without making Electron a required dependency of the CLI.
