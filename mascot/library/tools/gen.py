"""Generate the library's raw images, with automatic fallback between providers.

Every job is tried on the providers in order (default: gemini, openai, bridge). When a provider is out of quota or
credits, it is marked exhausted (saved in raw/.providers.json with a cool-down) and the job moves on to the next
provider; later jobs skip it until the cool-down ends. Other errors are retried once on the same provider.

Providers (keys are injected by the network proxy; nothing secret is read, printed or stored here):
  gemini  Gemini API generateContent with the reference images inline. Models tried in order (each has its own
          quota): gemini-3-pro-image, gemini-3.1-flash-image, gemini-2.5-flash-image.
          Needs the key in header x-goog-api-key and billing on the key (the free tier allows 0 image requests).
  openai  OpenAI image edit API, gpt-image-2 then gpt-image-1.5, with the reference images uploaded.
  bridge  ChatGPT bridge on zarkhaiz.duckdns.org (Codex with the ChatGPT plan sign-in and its image_gen tool):
          POST /jobs {"prompt", "images": [{"name", "data": base64}]} -> {"id"}; GET /jobs/<id>;
          GET /jobs/<id>/files/<name>. The bridge currently ignores "images" and cannot fetch URLs, so it has no
          references; it is used only if the bridge accepts images (see mascot/library/README.md) or with
          --bridge-noref.

Usage: python3 gen.py [--providers gemini,openai,bridge] [--only id1,id2] [--par 2] [--redo] [--reset]
Writes raw/<job>.png and raw/<job>.json (prompt, provider, model, ids). An older take is kept as <job>_takeN.png.
"""
import argparse, base64, concurrent.futures as cf, io, json, subprocess, sys, threading, time, urllib.error, \
    urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from jobs import jobs  # noqa: E402

LIB = Path(__file__).resolve().parents[1]
RAW = LIB / "raw"
STATE = RAW / ".providers.json"
REPO = LIB.parents[1]
REFS = [REPO / "mascot/rig/source.webp"] + [REPO / f"mascot/character/refs/sheet{i}.jpg" for i in (1, 2, 3)]
BRIDGE = "https://zarkhaiz.duckdns.org"
GEMINI = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODELS = ["gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]
OPENAI_MODELS = ["gpt-image-2", "gpt-image-1.5"]
COOLDOWN = {"quota": 6 * 3600, "rate": 120, "unusable": 6 * 3600}
_lock = threading.Lock()


class Exhausted(Exception):
    """The provider (or one model of it) cannot serve requests for a while; kind is quota, rate or unusable."""
    def __init__(self, key, kind, msg):
        super().__init__(msg)
        self.key, self.kind = key, kind


# ---------- provider state ----------
def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def available(key):
    with _lock:
        s = load_state().get(key)
    return not s or s["until"] < time.time()


def mark(key, kind, msg):
    with _lock:
        st = load_state()
        st[key] = {"until": time.time() + COOLDOWN[kind], "kind": kind, "why": msg[:300],
                   "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        STATE.write_text(json.dumps(st, indent=1))
    print(f"  [{key}] {kind}: {msg[:160]}", flush=True)


# ---------- references ----------
_ref_cache = {}


def ref_jpeg(p, maxside=1024):
    if p not in _ref_cache:
        im = Image.open(p).convert("RGB")
        im.thumbnail((maxside, maxside))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=90)
        _ref_cache[p] = b.getvalue()
    return _ref_cache[p]


def post_json(url, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


# ---------- providers ----------
def run_gemini(job):
    ratio = "3:2" if job["size"] == "1536x1024" else "2:3"
    parts = [{"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(ref_jpeg(p)).decode()}}
             for p in REFS]
    parts.append({"text": "The reference images show the character. " + job["prompt"]})
    last = None
    for model in GEMINI_MODELS:
        key = f"gemini:{model}"
        if not available(key):
            continue
        body = {"contents": [{"parts": parts}],
                "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": ratio}}}
        try:
            d = post_json(f"{GEMINI}/{model}:generateContent", body, 300)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code == 429:
                kind = "quota" if ("per day" in msg or "limit: 0" in msg) else "rate"
                mark(key, kind, msg)
                last = Exhausted(key, kind, msg)
                continue
            if e.code in (401, 403, 404):
                mark(key, "unusable", f"HTTP {e.code}: {msg}")
                last = Exhausted(key, "unusable", msg)
                continue
            raise RuntimeError(f"gemini {model} HTTP {e.code}: {msg[:300]}")
        for c in d.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                if "inlineData" in p:
                    return base64.b64decode(p["inlineData"]["data"]), {"provider": "gemini", "model": model}
        raise RuntimeError(f"gemini {model}: no image in response ({str(d)[:300]})")
    raise last or Exhausted("gemini", "cooling down", "all Gemini image models are cooling down")


def run_openai(job):
    last = None
    for model in OPENAI_MODELS:
        key = f"openai:{model}"
        if not available(key):
            continue
        args = ["curl", "-sS", "-m", "600", "https://api.openai.com/v1/images/edits",
                "-H", "Authorization: Bearer sk-placeholder",  # replaced by the proxy
                "-F", f"model={model}", "-F", f"size={job['size']}", "-F", "quality=high",
                "-F", f"prompt={job['prompt']}"]
        for p in REFS:
            args += ["-F", f"image[]=@{p};type=image/{'webp' if p.suffix == '.webp' else 'jpeg'}"]
        d = json.loads(subprocess.run(args, capture_output=True, check=True).stdout)
        if "data" in d:
            return base64.b64decode(d["data"][0]["b64_json"]), {"provider": "openai", "model": model}
        err = d.get("error") or {}
        code = f"{err.get('code')} {err.get('type')}"
        if any(k in code for k in ("insufficient_quota", "credit_balance", "billing")):
            mark("openai", "quota", err.get("message", code))  # credits are per account: skip every model
            raise Exhausted("openai", "quota", err.get("message", code))
        if "rate_limit" in code:
            mark(key, "rate", err.get("message", code))
            last = Exhausted(key, "rate", code)
            continue
        if any(k in code for k in ("model_not_found", "invalid_api_key", "permission")):
            mark(key, "unusable", err.get("message", code))
            last = Exhausted(key, "unusable", code)
            continue
        raise RuntimeError(f"openai {model}: {err}")
    raise last or Exhausted("openai", "cooling down", "all OpenAI image models are cooling down")


def run_bridge(job, noref=False):
    shape = "landscape 1536x1024" if job["size"] == "1536x1024" else "portrait 1024x1536"
    refline = ("No reference images are available; follow the character description exactly." if noref else
               "Use the attached images as references for the character.")
    prompt = ("Image generation task. Do not write code and do not run shell commands. "
              f"{refline} Call the image generation tool exactly ONCE to make ONE image, {shape}. "
              f"Image description: {job['prompt']} Return the generated image file and reply with one short line. "
              "If the reference images are not attached, do NOT generate; reply exactly: NO_REFS")
    if noref:
        prompt = prompt.replace(" If the reference images are not attached, do NOT generate; reply exactly: NO_REFS", "")
    body = {"prompt": prompt}
    if not noref:
        health = json.loads(urllib.request.urlopen(f"{BRIDGE}/health", timeout=30).read())
        if not health.get("images"):
            mark("bridge", "unusable", "bridge /health does not report images support, so it cannot take the "
                 "reference images (see mascot/library/README.md, Bridge upgrade); use --providers bridge-noref "
                 "to generate without references")
            raise Exhausted("bridge", "unusable", "no image upload on the bridge")
        body["images"] = [{"name": p.with_suffix(".jpg").name, "data": base64.b64encode(ref_jpeg(p, 768)).decode()}
                          for p in REFS]
    jid = post_json(f"{BRIDGE}/jobs", body, 120)["id"]
    t0 = time.time()
    while True:
        time.sleep(10)
        st = json.loads(urllib.request.urlopen(f"{BRIDGE}/jobs/{jid}", timeout=60).read())
        if st["status"] in ("done", "failed"):
            break
        if time.time() - t0 > 1500:
            raise RuntimeError(f"bridge job {jid} timed out")
    err, reply = st.get("error", ""), st.get("reply", "")
    if "usage limit" in err or "usage limit" in reply:
        mark("bridge", "quota", (err or reply)[-300:])
        raise Exhausted("bridge", "quota", "ChatGPT plan usage limit")
    if st["status"] == "failed":
        raise RuntimeError(f"bridge failed: {err[-300:]}")
    imgs = [f for f in st.get("files", []) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    if not imgs:
        if "NO_REFS" in reply or "could not be loaded" in reply or "attach" in reply.lower():
            mark("bridge", "unusable", "bridge does not pass reference images to Codex: " + reply)
            raise Exhausted("bridge", "unusable", reply)
        raise RuntimeError(f"bridge: no image returned; reply: {reply[:300]}")
    data = urllib.request.urlopen(f"{BRIDGE}/jobs/{jid}/files/{imgs[0]}", timeout=180).read()
    return data, {"provider": "chatgpt-bridge", "model": "ChatGPT (Codex image_gen)", "bridge_job": jid,
                  "references": not noref, "reply": reply[:300]}


PROVIDERS = {"gemini": run_gemini, "openai": run_openai, "bridge": run_bridge,
             "bridge-noref": lambda j: run_bridge(j, noref=True)}


# ---------- driver ----------
def generate(job, order):
    """Try providers in order; skip exhausted ones; return (bytes, meta)."""
    tried = []
    for name in order:
        if not available(name):
            tried.append(f"{name}: cooling down")
            continue
        for attempt in (1, 2):
            try:
                return PROVIDERS[name](job)
            except Exhausted as e:
                tried.append(f"{name}: {e.kind}")
                break
            except Exception as e:  # noqa: BLE001 - transient errors get one retry
                if attempt == 2:
                    tried.append(f"{name}: error {str(e)[:120]}")
                else:
                    time.sleep(5)
    raise RuntimeError("no provider could make it -> " + "; ".join(tried))


def one(job, order, redo):
    out = RAW / f"{job['id']}.png"
    if out.exists() and not redo:
        return f"skip {job['id']}"
    data, meta = generate(job, order)
    if out.exists():
        n = 1
        while (RAW / f"{job['id']}_take{n}.png").exists():
            n += 1
        out.rename(RAW / f"{job['id']}_take{n}.png")
        if (RAW / f"{job['id']}.json").exists():
            (RAW / f"{job['id']}.json").rename(RAW / f"{job['id']}_take{n}.json")
    Image.open(io.BytesIO(data)).save(out, optimize=True)
    meta.update({k: v for k, v in job.items() if k != "prompt"}, prompt=job["prompt"],
                created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (RAW / f"{job['id']}.json").write_text(json.dumps(meta, indent=1))
    return f"ok {job['id']} via {meta['provider']} {meta['model']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--providers", default="gemini,openai,bridge")
    ap.add_argument("--only", default="")
    ap.add_argument("--par", type=int, default=2)
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--reset", action="store_true", help="forget saved cool-downs")
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    if a.reset and STATE.exists():
        STATE.unlink()
    order = a.providers.split(",")
    todo = [j for j in jobs() if not a.only or j["id"] in a.only.split(",")]
    fails = 0
    with cf.ThreadPoolExecutor(a.par) as ex:
        futs = {ex.submit(one, j, order, a.redo): j["id"] for j in todo}
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print(f"FAIL {futs[f]}: {e}", flush=True)
    print(f"done: {len(todo) - fails} ok/skipped, {fails} failed. Provider state: {STATE}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
