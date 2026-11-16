"""One edit of a base image through Kie.ai (GPT Image 2, image-to-image): the same job bridge_edit.py does through the
ChatGPT bridge, for sessions where the bridge token is not available. Images only (the user's rule: no video on Kie).

Usage: python3 kie_edit.py <out.png> "<edit instruction>" <base.png> [<second.png> ...]
Cost: 6 Kie credits (about $0.03) per image at 1K. The key comes from $KIE_API_KEY (the user's kie-ai skill sets it);
never write the key into this repository.
"""
import io, json, os, subprocess, sys, time, urllib.request, uuid
from PIL import Image

API = "https://api.kie.ai/api/v1"
UPLOAD = "https://kieai.redpandaai.co/api/file-stream-upload"
MODEL = os.environ.get("KIE_IMAGE_MODEL", "gpt-image-2-image-to-image")


def _key():
    k = os.environ.get("KIE_API_KEY")
    if not k:
        sys.exit("KIE_API_KEY is not set (load the kie-ai skill, it exports the key)")
    return k


def _json(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=120).read())
    if r.get("code") != 200:           # Kie always answers HTTP 200; the real status is the body's code
        raise RuntimeError(f"kie {r.get('code')}: {r.get('msg')}")
    return r["data"]


def upload(path):
    b = io.BytesIO(); Image.open(path).convert("RGB").save(b, "PNG")
    tmp = f"/tmp/kie_{uuid.uuid4().hex}_{os.path.basename(path)}"      # unique: several edits upload the master at once
    open(tmp, "wb").write(b.getvalue())
    out = subprocess.run(["curl", "-sS", "-X", "POST", UPLOAD, "-H", f"Authorization: Bearer {_key()}",
                          "-F", f"file=@{tmp}", "-F", "uploadPath=images/mascot"], capture_output=True, text=True, timeout=180)
    os.remove(tmp)
    r = json.loads(out.stdout)
    if r.get("code") != 200:
        raise RuntimeError(f"upload {r.get('code')}: {r.get('msg')}")
    return r["data"].get("downloadUrl") or r["data"]["fileUrl"]


def edit(out, instruction, images, timeout=600):
    urls = [upload(p) for p in images]
    prompt = ("Image EDIT task. The FIRST image is the base image" + (", the other images are references" if len(urls) > 1 else "")
              + ". " + instruction + " Keep EVERYTHING else exactly as in the base image: the same man, face, head position, "
              "torso, legs, shoes, scale and position in the frame, lighting and the pure white background. Natural "
              "anatomy, five fingers per hand. No text.")
    tid = _json(f"{API}/jobs/createTask", {"model": MODEL, "input": {"prompt": prompt, "input_urls": urls, "aspect_ratio": "2:3"}})["taskId"]
    t0 = time.time()
    while True:
        time.sleep(5)
        d = _json(f"{API}/jobs/recordInfo?taskId={tid}")
        if d["state"] in ("success", "fail"):
            break
        if time.time() - t0 > timeout:
            raise RuntimeError("timeout " + tid)
    if d["state"] == "fail":
        raise RuntimeError(f"fail {d.get('failCode')}: {d.get('failMsg')}")
    url = json.loads(d["resultJson"])["resultUrls"][0]
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "curl/8"}), timeout=180).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.size != (1024, 1536):
        im = im.resize((1024, 1536), Image.LANCZOS)
    im.save(out)
    return tid, d.get("creditsConsumed")


if __name__ == "__main__":
    print(edit(sys.argv[1], sys.argv[2], sys.argv[3:]))
