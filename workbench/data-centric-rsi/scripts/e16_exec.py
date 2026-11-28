"""E16: sandboxed execution of stdin/stdout Python programs (competitive-programming style).

Each run: fresh subprocess of the system python3 with -I, empty temp dir as cwd, CPU-time limit, 1 GB address
space, 16 MB file-size limit, minimal environment. A static screen refuses programs that import process,
network or filesystem-manipulation modules or call os.system/exec-style functions (counted as "refused", never run).
Outputs are compared after normalising whitespace (token-wise).
"""
import ast
import os
import resource
import subprocess
import tempfile

PY = "/usr/bin/python3"
BAD_MODS = {"subprocess", "socket", "shutil", "ctypes", "multiprocessing", "threading", "requests", "urllib", "http",
            "ftplib", "smtplib", "webbrowser", "pty", "fcntl", "mmap", "signal", "resource", "importlib", "pickle",
            "asyncio", "tempfile", "glob", "pathlib"}
BAD_OS = {"system", "popen", "remove", "unlink", "rmdir", "removedirs", "rename", "replace", "fork", "kill", "execv",
          "execve", "execl", "execlp", "execvp", "spawnl", "spawnv", "chmod", "chown", "mkdir", "makedirs", "symlink",
          "link", "truncate", "putenv", "chdir"}
BAD_CALLS = {"exec", "eval", "compile", "__import__", "breakpoint", "input_file"}


def screen(code):
    """Return None if the program may run, else a short reason."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "syntax"
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] in BAD_MODS for a in n.names):
            return "module"
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] in BAD_MODS:
            return "module"
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "os" and n.attr in BAD_OS:
            return "os_call"
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in BAD_CALLS:
            return "call"
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open":
            if len(n.args) >= 2 or any(k.arg == "mode" for k in n.keywords):
                return "open_mode"
    return None


def _limits(cpu):
    def f():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
        resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
        resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))
        os.setsid()
    return f


def run(code, stdin, time_limit=2.0):
    """Run one program on one input. Returns (status, stdout); status in ok/tle/re/refused."""
    why = screen(code)
    if why:
        return "refused", why
    cpu = max(1, int(round(2 * time_limit)))
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "prog.py")
        with open(src, "w") as f:
            f.write(code)
        try:
            p = subprocess.run([PY, "-I", src], input=stdin, cwd=d, capture_output=True, text=True,
                               timeout=cpu + 2, preexec_fn=_limits(cpu), env={"PATH": "/usr/bin:/bin"})
        except subprocess.TimeoutExpired:
            return "tle", ""
        except Exception:
            return "re", ""
        if p.returncode != 0:
            return ("tle" if p.returncode in (-9, -24) else "re"), p.stdout[:20000]
        return "ok", p.stdout[:200000]


def same(a, b):
    return a.split() == b.split()
