"""Generate the library's raw images.

Backends (keys are injected by the network proxy; nothing secret is read or stored here):
  bridge  ChatGPT bridge on zarkhaiz.duckdns.org: POST /jobs {"prompt"} -> {"id"};
          GET /jobs/<id> -> {"status": queued|running|done|failed, "reply", "files"};
          GET /jobs/<id>/files/<name> downloads an output. It runs Codex with the ChatGPT plan sign-in and
          its image_gen tool. It takes no uploads, so the reference images are given as public raw GitHub URLs.
  openai  OpenAI image edit API (gpt-image-2) with the reference images uploaded.

Usage: python3 gen.py [--backend bridge|openai] [--only id1,id2] [--par 2] [--redo]
Writes mascot/library/raw/<job>.png and <job>.json (prompt, backend, model, job id).
"""
import argparse, base64, concurrent.futures as cf, json, os, subprocess, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jobs import jobs, REFS  # noqa: E402

LIB = Path(__file__).resolve().parents[1]
RAW = LIB / "raw"
BRIDGE = "https://zarkhaiz.duckdns.org"
REPO = LIB.parents[1]
LOCAL_REFS = [REPO / "mascot/rig/source.webp"] + [REPO / f"mascot/character/refs/sheet{i}.jpg" for i in (1, 2, 3)]


def http(url, data=None, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                                 headers={"content-type": "application/json"})
    return urllib.request.urlopen(req, timeout=timeout).read()


def bridge_prompt(job):
    refs = "\n".join(f"- {u}" for u in REFS)
    return (
        "Image generation task. Do not write code and do not run shell commands.\n"
        f"1. Open and look at these reference images of the character (public URLs):\n{refs}\n"
        "2. Call the image generation tool exactly ONCE, passing those reference images as references, to make ONE "
        f"image, {'landscape 1536x1024' if job['size'] == '1536x1024' else 'portrait 1024x1536'}.\n"
        f"Image description: {job['prompt']}\n"
        "3. Return the generated image file. Reply with one short line only."
    )


def run_bridge(job):
    jid = json.loads(http(f"{BRIDGE}/jobs", {"prompt": bridge_prompt(job)}))["id"]
    t0 = time.time()
    while True:
        time.sleep(10)
        st = json.loads(http(f"{BRIDGE}/jobs/{jid}"))
        if st["status"] in ("done", "failed"):
            break
        if time.time() - t0 > 1200:
            raise RuntimeError(f"{job['id']}: bridge job {jid} timed out")
    if st["status"] == "failed":
        raise RuntimeError(f"{job['id']}: bridge failed: {st.get('error', '')[-300:]}")
    imgs = [f for f in st.get("files", []) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    if not imgs:
        raise RuntimeError(f"{job['id']}: no image returned; reply: {st.get('reply', '')[:300]}")
    data = urllib.request.urlopen(f"{BRIDGE}/jobs/{jid}/files/{imgs[0]}", timeout=120).read()
    return data, {"backend": "chatgpt-bridge", "model": "ChatGPT (Codex image_gen)", "bridge_job": jid,
                  "reply": st.get("reply", "")[:500]}


def run_openai(job):
    args = ["curl", "-sS", "-m", "600", "https://api.openai.com/v1/images/edits",
            "-H", "Authorization: Bearer sk-placeholder",  # replaced by the proxy
            "-F", "model=gpt-image-2", "-F", f"size={job['size']}", "-F", "quality=high",
            "-F", f"prompt={job['prompt']}"]
    for p in LOCAL_REFS:
        args += ["-F", f"image[]=@{p}"]
    d = json.loads(subprocess.run(args, capture_output=True, check=True).stdout)
    if "data" not in d:
        raise RuntimeError(f"{job['id']}: {d.get('error')}")
    return base64.b64decode(d["data"][0]["b64_json"]), {"backend": "openai", "model": "gpt-image-2"}


def one(job, backend, redo):
    out = RAW / f"{job['id']}.png"
    if out.exists() and not redo:
        return f"skip {job['id']}"
    data, meta = (run_bridge if backend == "bridge" else run_openai)(job)
    if out.exists():  # keep the earlier take
        n = 1
        while (RAW / f"{job['id']}_take{n}.png").exists():
            n += 1
        out.rename(RAW / f"{job['id']}_take{n}.png")
    out.write_bytes(data)
    meta.update({k: job[k] for k in job if k != "prompt"}, prompt=job["prompt"],
                created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (RAW / f"{job['id']}.json").write_text(json.dumps(meta, indent=1))
    return f"ok {job['id']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="bridge")
    ap.add_argument("--only", default="")
    ap.add_argument("--par", type=int, default=2)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    todo = [j for j in jobs() if not a.only or j["id"] in a.only.split(",")]
    with cf.ThreadPoolExecutor(a.par) as ex:
        futs = {ex.submit(one, j, a.backend, a.redo): j["id"] for j in todo}
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # keep going; report at the end
                print(f"FAIL {futs[f]}: {e}", flush=True)


if __name__ == "__main__":
    main()
