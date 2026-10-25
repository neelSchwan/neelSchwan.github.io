# loop {}

An endless, swipeable feed of Rust, coding and system design problems with a built-in editor and test runner.

- **GitHub Pages** (`docs/`): fully static. Rust runs on the public Rust Playground, Python runs in-browser via Pyodide.
- **Self-hosted** (`server.py`): same page, but code runs locally in a bwrap sandbox (no network, 20s, 1GB).
  Needs Python 3, bwrap, systemd (user), and rustup with the `x86_64-unknown-linux-musl` target.

Add or edit problems in `problems/<track>/*.json`, then run `python3 build.py` to regenerate `docs/problems.json`.
