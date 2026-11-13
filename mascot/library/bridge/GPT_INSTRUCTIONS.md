# ChatGPT bridge upgrade: instructions for the assistant working on the VPS

You are working on the user's VPS, where the "ChatGPT bridge" runs: a small Python HTTP server in
`/home/zarkhaiz_asr/chatgpt-bridge`, served at `https://zarkhaiz.duckdns.org`. It runs `codex exec` (Codex CLI,
signed in with the user's ChatGPT plan) for every job. Its API today:

- `GET /health` → `{"ok": true, "login": "..."}`
- `POST /jobs` with JSON `{"prompt": "..."}` → `{"id": "..."}` (requests need the bridge token in `Authorization`)
- `GET /jobs/<id>` → `{"status": "queued|running|done|failed", "reply": "...", "files": [...], "error": "..."}`
- `GET /jobs/<id>/files/<name>` downloads an output file
- Each job runs in `/home/zarkhaiz_asr/chatgpt-bridge/jobs/<id>/` with
  `sandbox: workspace-write [workdir, /tmp, $TMPDIR]`.

A cloud Claude session uses this bridge to generate a mascot image library. It has two problems:

1. **Codex's shell crashes on every job:** `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`
   (and the warning "Codex could not find bubblewrap on PATH ... will use the bundled bubblewrap").
   Codex's workspace-write sandbox builds a private network namespace when network access is off, and this VPS
   kernel refuses to set up its loopback. With `[sandbox_workspace_write] network_access = true` Codex skips that
   step (tested with Codex 0.169: the shell works, curl reaches GitHub, writes stay limited to the job folder).
2. **The bridge cannot take reference images.** It accepts only `{"prompt"}` (large bodies get HTTP 400), and
   Codex cannot open image URLs without a working shell. Image generation then has no references and the
   character's face drifts.

Do Part A (required). Part B is recommended. Then run Part C and report the results to the user.
Do not change the bridge token, its URL, its port or the existing API fields. Never print or share the token or
the ChatGPT login files (`~/.codex/auth.json`).

---

## Part A (required): fix the Codex sandbox (config change only, no code)

Run this as the user that runs the bridge (`zarkhaiz_asr`), **not as root**:

```bash
curl -fsSL https://raw.githubusercontent.com/marjanash/zarkhaiz/ccr-e371ce1b-168zzm/mascot/library/bridge/fix_vps.sh | bash
```

If the VPS cannot reach GitHub, save the script below as `~/fix_vps.sh` and run `bash ~/fix_vps.sh`.
It is safe to run twice. It keeps a backup of `config.toml`, never touches a config that does not parse, and
checks the new config before saving it.

```bash
#!/usr/bin/env bash
# Fix the ChatGPT bridge's Codex sandbox so Codex can run commands and download the character reference images.
#
# Run it ON THE VPS, as the user that runs the bridge (zarkhaiz_asr), not as root:
#   curl -fsSL https://raw.githubusercontent.com/marjanash/zarkhaiz/ccr-e371ce1b-168zzm/mascot/library/bridge/fix_vps.sh | bash
#
# What it does (safe to run twice):
#  1. Installs the system bubblewrap package if sudo is available without a password prompt
#     (Codex warned "could not find bubblewrap on PATH" and used its bundled copy).
#  2. Sets network_access = true under [sandbox_workspace_write] in Codex's config.toml (a backup is kept).
#     Codex's shell failed on every job with "bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted":
#     that error comes from building an offline network namespace, which this VPS kernel does not allow.
#     With network access on, Codex skips that step, its shell works again, and it can curl the reference images.
#     Writes stay limited to the job folder and /tmp.
# Nothing else changes: the bridge code, its token and its service are untouched, and no restart is needed
# (Codex reads its config on every job).
set -u
CH="${CODEX_HOME:-$HOME/.codex}"
CFG="$CH/config.toml"
echo "== user: $(whoami)   Codex config: $CFG"
if [ "$(id -u)" = "0" ]; then
  echo "!! You are root. Run this as the user that runs the bridge (for example: sudo -u zarkhaiz_asr bash fix_vps.sh)."
  exit 1
fi

echo "== 1. bubblewrap"
if command -v bwrap >/dev/null 2>&1; then
  echo "   already installed: $(command -v bwrap)"
elif command -v apt-get >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  sudo apt-get install -y bubblewrap >/dev/null && echo "   installed: $(command -v bwrap)"
else
  echo "   skipped (needs root). Optional: as root run  apt-get install -y bubblewrap"
fi

echo "== 2. Codex sandbox network access"
mkdir -p "$CH"
[ -f "$CFG" ] && cp "$CFG" "$CFG.bak-$(date +%Y%m%d%H%M%S)" && echo "   backup: $CFG.bak-*"
python3 - "$CFG" <<'PY' || { echo "!! Codex config not changed (error above)."; exit 1; }
import re, sys
from pathlib import Path
try:
    import tomllib
except ImportError:  # Python < 3.11: no check available
    tomllib = None


def check(text, what):
    if tomllib is None:
        return
    try:
        cfg = tomllib.loads(text)
    except Exception as e:
        print(f"!! {what} does not parse: {e}")
        sys.exit(1)
    return cfg


p = Path(sys.argv[1])
s = p.read_text() if p.exists() else ""
check(s, "the current config.toml")  # never touch a config that is already broken
head = re.search(r"(?m)^\[sandbox_workspace_write\][ \t]*$", s)
if not head:
    s = s.rstrip("\n") + ("\n\n" if s.strip() else "") + "[sandbox_workspace_write]\nnetwork_access = true\n"
else:
    rest = s[head.end():]
    nxt = re.search(r"(?m)^[ \t]*\[", rest)
    sec, tail = (rest[:nxt.start()], rest[nxt.start():]) if nxt else (rest, "")
    if re.search(r"(?m)^[ \t]*network_access[ \t]*=", sec):
        sec = re.sub(r"(?m)^[ \t]*network_access[ \t]*=.*$", "network_access = true", sec)
    else:
        sec = "\nnetwork_access = true" + sec
    s = s[:head.end()] + sec + tail
cfg = check(s, "the new config.toml")
if cfg is not None and cfg.get("sandbox_workspace_write", {}).get("network_access") is not True:
    print("!! could not set network_access; config not changed")
    sys.exit(1)
p.write_text(s)  # written only after the new text was checked
print("   [sandbox_workspace_write] network_access = true (config.toml checked and saved)")
PY

echo "== done. Tell Claude: \"VPS fix ho gaya\" - it will test the bridge and start the library."
```

If the bridge sets its own `CODEX_HOME`, or starts `codex exec` with `-c sandbox_workspace_write.network_access=false`,
run the script with that `CODEX_HOME` (`CODEX_HOME=/path bash fix_vps.sh`) and remove that flag.
Optional, as root: `apt-get install -y bubblewrap`.

No restart is needed: Codex reads its config on every job.

---

## Part B (recommended): accept reference images, and switch ChatGPT accounts when one runs out

Read the bridge's code first and keep its style. Change only what is listed here.

### B1. `POST /jobs` accepts images

New optional field: `"images": [{"name": "ref0_source.jpg", "data": "<base64>"}, ...]`.

- Raise the request body limit to 8 MB (the client sends 4 JPEGs of about 100 KB each).
- Save the images in a `refs/` subfolder of the job folder, and do not list `refs/` in the job's `files`
  (the client downloads the first image listed in `files`, so it must be Codex's output).
- Pass each image to Codex with its own `-i` flag. `-i/--image` takes several values, so put `--` before the
  prompt argument; otherwise Codex reads the prompt as one more image file. If the prompt is sent on stdin, that
  is fine as is.

Helper code (standard library only):

```python
import base64, binascii, os, re

MAX_BODY = 8 * 1024 * 1024        # use this where the handler reads Content-Length
MAX_IMAGES, MAX_IMAGE_BYTES = 8, 3 * 1024 * 1024

def save_images(job_dir, images):
    """Save the request's images into <job_dir>/refs/ and return their paths. Raise ValueError on bad input."""
    if not images:
        return []
    if not isinstance(images, list) or len(images) > MAX_IMAGES:
        raise ValueError("images must be a list of at most 8 items")
    ref_dir = os.path.join(job_dir, "refs")
    os.makedirs(ref_dir, exist_ok=True)
    paths = []
    for i, im in enumerate(images):
        name = os.path.basename(str(im.get("name") or f"ref{i}.jpg"))
        name = re.sub(r"[^A-Za-z0-9._-]", "_", name)[:64] or f"ref{i}.jpg"
        try:
            data = base64.b64decode(im["data"], validate=True)
        except (KeyError, TypeError, binascii.Error):
            raise ValueError(f"image {i}: data must be base64")
        if len(data) > MAX_IMAGE_BYTES:
            raise ValueError(f"image {i}: larger than 3 MB")
        if not data.startswith((b"\xff\xd8", b"\x89PNG", b"RIFF")):
            raise ValueError(f"image {i}: not a JPEG, PNG or WebP")
        path = os.path.join(ref_dir, f"{i}_{name}")
        with open(path, "wb") as f:
            f.write(data)
        paths.append(path)
    return paths

def image_args(paths):
    """Arguments to add to the codex exec command, before '--' and the prompt."""
    out = []
    for p in paths:
        out += ["-i", p]
    return out
```

In the `POST /jobs` handler: the body must still contain a non-empty `"prompt"`. Call `save_images()` after the job
folder exists and answer HTTP 400 with `{"error": "<message>"}` on `ValueError`. Then build the command as
`[...existing codex exec flags..., *image_args(paths), "--", prompt]` (or keep sending the prompt on stdin).

### B2. `GET /health` reports it

Add `"images": true`. The client sends images only when it sees this; otherwise it asks Codex to download the
references from GitHub itself (which works after Part A).

### B3. Several ChatGPT accounts (optional)

Each account is a separate Codex home. Sign in a second account once:

```bash
mkdir -p ~/.codex2 && cp ~/.codex/config.toml ~/.codex2/ && CODEX_HOME=~/.codex2 codex login --device-auth
```

(`--device-auth` prints a code to enter on another device. Part A's `network_access` setting must also be in
`~/.codex2/config.toml`: the `cp` above takes care of it.)

In the bridge, read the list from an environment variable such as `CODEX_HOMES=/home/zarkhaiz_asr/.codex:/home/zarkhaiz_asr/.codex2`
(default: `~/.codex` only). Run each job with `env["CODEX_HOME"] = <first home>`. If Codex's output contains
"usage limit", run the same job again with the next home. Remember a home that hit its limit (for example for one
hour) and skip it for the next jobs. Add `"account": <index>` to the job status and `"accounts": <count>` to
`/health`. Keep the error text of the last attempt in `"error"` when all homes are out, so the client still sees
"usage limit".

Restart the bridge service after B1-B3 (find it with `systemctl --user list-units | grep -i bridge`,
`systemctl list-units | grep -i bridge` or `ps aux | grep -i bridge`).

---

## Part C: tests (run on the VPS and report each result)

1. Sandbox shell and network (does not use ChatGPT quota):
   ```bash
   cd /tmp && codex sandbox -c sandbox_mode='"workspace-write"' -- sh -c 'echo SHELL_OK; curl -sS -o /dev/null -w "%{http_code}\n" https://raw.githubusercontent.com/marjanash/zarkhaiz/ccr-e371ce1b-168zzm/mascot/character/refs/sheet1.jpg'
   ```
   Expected: `SHELL_OK` and `200`. Before Part A this crashed with the `RTM_NEWADDR` error.
2. One real Codex job with a shell command (uses a little quota):
   ```bash
   cd /tmp && codex exec --skip-git-repo-check -s workspace-write "Run: echo hi > hello.txt && ls -la. Reply with the listing."
   ```
   Expected: the listing with `hello.txt`, no bwrap error.
3. If Part B was done: `curl -s https://zarkhaiz.duckdns.org/health` (with the token header, as the bridge requires)
   shows `"images": true`. Run one job with a small image and a prompt like "Describe the attached image in five
   words". The reply must describe the image, and `files` must not list the uploaded image.

## Part D: tell the user

Report in short Roman Urdu: what you changed (files, config, service restart), the backup path of `config.toml`,
the result of each test in Part C, and anything you could not do. The user will tell the Claude session
"VPS fix ho gaya", and it will test the bridge from its side and start generating the library.
