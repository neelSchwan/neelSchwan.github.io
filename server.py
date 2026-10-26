#!/usr/bin/env python3
"""loop {} — an endless feed of Rust, coding and system design problems."""
import json, os, subprocess, tempfile, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", "8090"))
TOOLCHAIN = os.path.expanduser("~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu")
MAX_CODE = 64 * 1024
MAX_OUT = 32 * 1024
RUN_SLOTS = threading.BoundedSemaphore(4)

PROBLEMS = {p["id"]: p for p in json.load(open(os.path.join(ROOT, "docs", "problems.json")))}
STATIC = {"/": ("index.html", "text/html; charset=utf-8"),
          "/problems.json": ("problems.json", "application/json")}

RUSTC = ("rustc --edition 2021 --target x86_64-unknown-linux-musl "
         "-C linker=rust-lld -C linker-flavor=ld.lld -o t main.rs && ./t")


def run_sandboxed(code, tests=None):
    """tests=None is playground mode: just run the program."""
    with tempfile.TemporaryDirectory(prefix="loop-") as work:
        src = code if tests is None else "#![allow(dead_code)]\n" + code + "\n\n" + tests
        open(os.path.join(work, "main.rs"), "w").write(src)
        cmd = RUSTC if tests is None else RUSTC.replace("rustc ", "rustc --test ", 1)
        # No network, no home dir, only /usr + toolchain visible; cgroup caps memory/tasks/cpu.
        argv = [
            "systemd-run", "--user", "--scope", "--quiet",
            "-p", "MemoryMax=1G", "-p", "MemorySwapMax=0", "-p", "TasksMax=64", "-p", "CPUQuota=200%",
            "timeout", "-s", "KILL", "20",
            "bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
            "--ro-bind", "/usr", "/usr", "--symlink", "usr/bin", "/bin",
            "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64",
            "--ro-bind", TOOLCHAIN, "/rust", "--bind", work, "/w", "--chdir", "/w",
            "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
            "--setenv", "PATH", "/rust/bin:/usr/bin", "--setenv", "HOME", "/w",
            "sh", "-c", cmd,
        ]
        try:
            r = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        except subprocess.TimeoutExpired:
            return False, "timed out"
        out = r.stdout[:MAX_OUT].decode("utf-8", "replace")
        if r.returncode == 124:
            out += "\n[killed: 20s time limit]"
        elif r.returncode == 137:
            out += "\n[killed: memory limit]"
        return r.returncode == 0, out


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        name = STATIC.get(urlparse(self.path).path)
        if not name:
            return self.send(404, {"error": "not found"})
        self.send(200, open(os.path.join(ROOT, "docs", name[0]), "rb").read(), name[1])

    def do_POST(self):
        if self.path != "/api/run":
            return self.send(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_CODE + 1024:
            return self.send(413, {"error": "code too large"})
        try:
            req = json.loads(self.rfile.read(length))
            code = str(req["code"])
            tests = PROBLEMS[req["id"]].get("tests") if req.get("id") else None  # no id: playground
        except (ValueError, KeyError, TypeError):
            return self.send(400, {"error": "bad request"})
        if req.get("id") and not tests:
            return self.send(400, {"error": "nothing to run for this problem"})
        if not RUN_SLOTS.acquire(timeout=30):
            return self.send(503, {"ok": False, "output": "server busy, try again"})
        try:
            ok, out = run_sandboxed(code, tests)
        finally:
            RUN_SLOTS.release()
        self.send(200, {"ok": ok, "output": out})


if __name__ == "__main__":
    print(f"loop {{}} on :{PORT} with {len(PROBLEMS)} problems", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
