"""Ask the ChatGPT bridge (Codex image_gen, edit mode) for one edit of a base image.

Usage: python3 bridge_edit.py <out.png> "<edit instruction>" <base.png> [<second.png> ...]
The bridge token is injected by the network proxy. Returns non-zero on a usage limit or a missing image.
"""
import base64, io, json, sys, time, urllib.request
from PIL import Image

BRIDGE = "https://zarkhaiz.duckdns.org"


def edit(out, instruction, images, timeout=1500):
    imgs = []
    for i, p in enumerate(images):
        b = io.BytesIO(); Image.open(p).convert("RGB").save(b, "PNG")
        imgs.append({"name": f"{i}_{p.split('/')[-1]}", "data": base64.b64encode(b.getvalue()).decode()})
    names = ", ".join(f"refs/{m['name']}" for m in imgs)
    prompt = ("Image EDIT task. Do not write code and do not run shell commands. Attached images: " + names + ". "
              "The FIRST attached image is the base image. Call the image generation tool exactly ONCE in edit mode with "
              "the base image as the input image (pass the other attached images as references too), output portrait "
              "1024x1536. " + instruction + " Keep EVERYTHING else exactly as in the base image: the same man, face, "
              "head position, torso, legs, shoes, scale and position in the frame, lighting and the pure white "
              "background. Natural anatomy, five fingers per hand. No text. Save the image in the working directory "
              "and reply with one short line.")
    req = urllib.request.Request(f"{BRIDGE}/jobs", data=json.dumps({"prompt": prompt, "images": imgs}).encode(),
                                 headers={"content-type": "application/json"})
    jid = json.loads(urllib.request.urlopen(req, timeout=120).read())["id"]
    t0 = time.time()
    while True:
        time.sleep(8)
        st = json.loads(urllib.request.urlopen(f"{BRIDGE}/jobs/{jid}", timeout=60).read())
        if st["status"] in ("done", "failed"):
            break
        if time.time() - t0 > timeout:
            raise RuntimeError("timeout")
    txt = st.get("error", "") + st.get("reply", "")
    if "usage limit" in txt:
        raise RuntimeError("USAGE LIMIT: " + txt[-160:])
    files = [f for f in st.get("files", []) if f.lower().endswith((".png", ".jpg", ".webp")) and not f.startswith("refs/")]
    if not files:
        raise RuntimeError("no image: " + txt[-300:])
    data = urllib.request.urlopen(f"{BRIDGE}/jobs/{jid}/files/{files[-1]}", timeout=180).read()
    Image.open(io.BytesIO(data)).convert("RGB").save(out)
    return jid


if __name__ == "__main__":
    print(edit(sys.argv[1], sys.argv[2], sys.argv[3:]))
