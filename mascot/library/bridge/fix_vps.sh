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
