"""Ask the ChatGPT bridge (Codex image_gen, edit mode) for one edit of a base image.

Usage: python3 bridge_edit.py <out.png> "<edit instruction>" <base.png> [<second.png> ...]
Returns non-zero on a usage limit, a missing image or references that were not used.

Bridge (Nov 25, after the VPS fix): the canonical base is https://zarkhaiz.duckdns.org/muse-bridge/accounts/chatgpt
(override with BRIDGE_URL). The network proxy of the "AI Tools" environment injects X-Muse-Bridge-Token on that path:
never send or print an Authorization header here. API: POST /jobs {"prompt"} -> {"id"}; GET /jobs/<id>;
GET /jobs/<id>/files/<name>. The bridge has NO upload of reference files, so the references travel as URLs:
the prompt asks Codex to download them from the public GitHub repo (raw.githubusercontent.com, this branch) and to
report each file's sha256. The reply is checked against the local files' sha256: a job whose reply does not show
the base image's sha256 is treated as "references not used" and its image is rejected (it would be drawn from text
alone and the figure would drift). If GET /health reports "images": true, the files are also sent in "images".
"""
import base64, hashlib, io, json, os, sys, time, urllib.request
from pathlib import Path
from PIL import Image

BRIDGE = os.environ.get("BRIDGE_URL", "https://zarkhaiz.duckdns.org/muse-bridge/accounts/chatgpt").rstrip("/")
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_BASE = os.environ.get("BRIDGE_REF_BASE",
                          "https://raw.githubusercontent.com/MarjanAsh/Zarkhaiz/ccr-e371ce1b-168zzm")


def _get(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "application/json"}), timeout=timeout).read()


def health():
    return json.loads(_get(f"{BRIDGE}/health", 30))


def edit(out, instruction, images, timeout=1500):
    refs = []
    for i, p in enumerate(images):
        p = Path(p).resolve()
        rel = p.relative_to(REPO_ROOT).as_posix()
        refs.append({"url": f"{RAW_BASE}/{rel}", "name": f"{i}_{p.name}", "sha": hashlib.sha256(p.read_bytes()).hexdigest()})
    body = {}
    try:
        if health().get("images"):
            body["images"] = []
            for r, p in zip(refs, images):
                b = io.BytesIO(); Image.open(p).convert("RGB").save(b, "PNG")
                body["images"].append({"name": r["name"], "data": base64.b64encode(b.getvalue()).decode()})
    except Exception:
        pass
    dl = " && ".join(f'curl -fsSL -o refs/{r["name"]} "{r["url"]}"' for r in refs)
    body["prompt"] = (
        "Image EDIT task. Do not write code other than the commands below.\n"
        "Step 1. Download the reference images with one shell command:\n"
        f"  mkdir -p refs && {dl} && sha256sum refs/*\n"
        "Step 2. Put the full sha256sum output in your reply. If any download fails, do NOT generate an image; reply "
        "exactly NO_REFS and the error.\n"
        f"Step 3. refs/{refs[0]['name']} is the BASE image. Call the image generation tool exactly ONCE in edit mode with "
        "the base image as the input image (pass the other downloaded images as references too), output portrait "
        "1024x1536. " + instruction + " Keep EVERYTHING else exactly as in the base image: the same man, face, head "
        "position, torso, legs, shoes, scale and position in the frame, lighting and the pure white background. "
        "Natural anatomy, five fingers per hand. No text.\n"
        "Step 4. Save the generated image in the working directory as edit.png (not inside refs/) and reply with the "
        "sha256sum output and one short line.")
    req = urllib.request.Request(f"{BRIDGE}/jobs", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "Accept": "application/json"})
    jid = json.loads(urllib.request.urlopen(req, timeout=120).read())["id"]
    t0 = time.time()
    while True:
        time.sleep(8)
        st = json.loads(_get(f"{BRIDGE}/jobs/{jid}"))
        if st.get("status") in ("done", "failed", "error"):
            break
        if time.time() - t0 > timeout:
            raise RuntimeError(f"timeout (job {jid})")
    txt = (st.get("error") or "") + (st.get("reply") or "")
    if "usage limit" in txt.lower():
        raise RuntimeError("USAGE LIMIT: " + txt[-160:])
    if "NO_REFS" in txt or refs[0]["sha"] not in txt:
        raise RuntimeError(f"references not used (job {jid}): " + txt[-300:])
    files = [f for f in st.get("files", []) if f.lower().endswith((".png", ".jpg", ".webp")) and not f.startswith("refs/")]
    if not files:
        raise RuntimeError(f"no image (job {jid}): " + txt[-300:])
    data = urllib.request.urlopen(urllib.request.Request(f"{BRIDGE}/jobs/{jid}/files/{files[-1]}"), timeout=180).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.save(out)
    return f"{jid} {files[-1]} {im.size[0]}x{im.size[1]}"


if __name__ == "__main__":
    if sys.argv[1:] == ["--health"]:
        print(json.dumps(health()))
    else:
        print(edit(sys.argv[1], sys.argv[2], sys.argv[3:]))
