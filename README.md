# loop {}

An endless, swipeable feed of Rust problems (language drills + classic algorithms) and system design questions, with an in-browser editor and test runner.

- **GitHub Pages** (`docs/`): fully static; code runs on the public Rust Playground.
- **Self-hosted** (`server.py`): same page, but code runs in a local bwrap sandbox (no network, 20s, 1GB),
  and your solutions sync to `~/loop-work/<id>/` on the server. Needs Python 3, bwrap, systemd (user),
  and rustup with the `x86_64-unknown-linux-musl` target.

## Work in your own editor

Every problem is a small cargo project: write code in `src/solution.rs`, run `cargo test`.

- **Zed**: on the self-hosted site, press **open in zed** to open `~/loop-work/<id>` over SSH.
  Edits there show up on the website and vice versa.
- **CLI** (any machine on the tailnet):

  ```
  curl -o ~/.local/bin/loop http://bzguru-ram:8090/loop && chmod +x ~/.local/bin/loop
  loop next rust      # fetch a random problem into ./<id>/
  loop test           # cargo test (or on the server if cargo isn't installed)
  loop push           # save to the server; the website shows it
  loop pull           # take the server's copy
  ```

## Problems

Add or edit `problems/<track>/*.json`, then `python3 build.py` to regenerate `docs/problems.json`.
