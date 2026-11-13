#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.request
import subprocess

CONFIG_PATH = os.path.expanduser('~/creative-bridge/config.json')
LIB_DIR = os.path.expanduser('~/Zarkhaiz/mascot/library')
CUTOUT_TOOL = os.path.expanduser('~/.video-pipeline/tools/subject_cutout')

with open(CONFIG_PATH) as f:
    config = json.load(f)

TOKEN = config['token']
BASE_URL = f"http://127.0.0.1:{config['port']}"
REF_ID = "img_mwfa9qf37990ed" # source_apose.webp

CHAR_DESC = "Consistent character from reference image: Pakistani young male entrepreneur (black voluminous slicked-back wavy hair, neatly trimmed dark beard and mustache, thin silver aviator eyeglasses, black formal suit jacket, black shirt). 3D Pixar/DreamWorks stylized animated character render with soft studio lighting, sharp focus, plain solid clean white background."

TASKS = [
    # Expressions
    {
        "category": "expressions",
        "name": "talking_open",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: speaking naturally, mouth open mid-sentence in lively conversational delivery, friendly eye contact looking directly at camera, isolated."
    },
    {
        "category": "expressions",
        "name": "talking_wide",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: energetic enthusiastic speaking, mouth open wider emphasizing an important business point, animated face, isolated."
    },
    {
        "category": "expressions",
        "name": "excited",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: genuinely excited and happy, big bright smile, eyes wide with enthusiasm, isolated."
    },
    {
        "category": "expressions",
        "name": "serious",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: serious, focused, and professional, firm direct gaze at the camera, mouth closed in a determined executive expression, isolated."
    },
    {
        "category": "expressions",
        "name": "thinking",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: thoughtful and contemplative, eyes glancing slightly up and to the side, slight curious tilt of the head, isolated."
    },
    {
        "category": "expressions",
        "name": "surprised",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: shocked and surprised, eyes wide in disbelief, mouth slightly open in an 'O' shape, comedic reaction, isolated."
    },
    {
        "category": "expressions",
        "name": "concerned",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: concerned and empathetic, slight furrow of the brow, caring serious look discussing a business problem, isolated."
    },
    {
        "category": "expressions",
        "name": "laughing",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: hearty genuine laugh, eyes crinkled with amusement, mouth open in laughter, authentic joyful expression, isolated."
    },
    {
        "category": "expressions",
        "name": "confident_grin",
        "aspect": "1:1",
        "prompt": f"{CHAR_DESC} Close-up portrait. Facial expression: charming confident smirk and grin, sharp knowing eyes, self-assured leadership expression, isolated."
    },
    # Angles
    {
        "category": "angles",
        "name": "three_quarter_left",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Medium-full shot of the character, turned at a 3/4 angle facing towards the left. Both head and torso angled 45 degrees to the left, looking across with a warm confident speaking expression, isolated."
    },
    {
        "category": "angles",
        "name": "three_quarter_right",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Medium-full shot of the character, turned at a 3/4 angle facing towards the right. Both head and torso angled 45 degrees to the right, looking across with a warm confident speaking expression, isolated."
    },
    {
        "category": "angles",
        "name": "profile_left",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Full side profile view (90 degrees side view) of the character, facing completely to the left. Visible side profile of face with beard, glasses, black suit jacket, isolated."
    },
    {
        "category": "angles",
        "name": "profile_right",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Full side profile view (90 degrees side view) of the character, facing completely to the right. Visible side profile of face with beard, glasses, black suit jacket, isolated."
    },
    # Poses
    {
        "category": "poses",
        "name": "walking_front",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Full body shot of the character walking confidently forward towards the camera with a natural stride, smiling warmly, black tailored suit, black shoes, isolated."
    },
    {
        "category": "poses",
        "name": "seated_desk",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Full body shot of the character seated professionally at a modern executive desk, hands resting on desk, upright confident posture, smiling warmly at camera, isolated."
    },
    {
        "category": "poses",
        "name": "standing_laptop",
        "aspect": "4:5",
        "prompt": f"{CHAR_DESC} Full body shot of the character standing, holding an ultra-thin open sleek laptop in one arm while gesturing with the other hand to explain data, isolated."
    }
]

def make_request(path, data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    req.add_header('Cookie', f"cb_key={TOKEN}")
    if data is not None:
        req.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8')
        resp = urllib.request.urlopen(req, data=body, timeout=30)
    else:
        resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read().decode('utf-8'))

def process_task(task):
    cat = task['category']
    name = task['name']
    target_png = os.path.join(LIB_DIR, cat, f"{name}.png")
    if os.path.exists(target_png):
        print(f"[-] {cat}/{name}.png already exists, skipping.")
        return True

    print(f"\n[+] Enqueuing {cat}/{name}...")
    job_payload = {
        "type": "image",
        "params": {
            "prompt": task['prompt'],
            "aspect": task['aspect'],
            "refAssetIds": [REF_ID]
        },
        "tags": ["mascot", cat, name]
    }
    
    resp = make_request('/api/jobs', job_payload)
    job_id = resp['jobs'][0]['id']
    print(f"    Job ID: {job_id}. Waiting for completion...")

    start_t = time.time()
    while True:
        time.sleep(6)
        status_resp = make_request(f"/api/jobs/{job_id}")
        st = status_resp.get('status')
        elapsed = int(time.time() - start_t)
        sys.stdout.write(f"\r    Status: {st} ({elapsed}s)...")
        sys.stdout.flush()

        if st == 'done':
            print("\n    Job completed!")
            asset_info = status_resp['assets'][0]
            rel_file = asset_info['file'] # e.g. "images/img_xxx.png"
            src_img = os.path.expanduser(f"~/creative-bridge/library/{rel_file}")
            
            # Run cutout tool to get clean transparent PNG
            print(f"    Applying Apple Vision subject_cutout to {src_img} -> {target_png}")
            res = subprocess.run([CUTOUT_TOOL, src_img, target_png], capture_output=True, text=True)
            if res.returncode != 0:
                print(f"    Cutout error: {res.stderr}, copying raw image instead")
                import shutil
                shutil.copyfile(src_img, target_png)
            else:
                print(f"    Cutout successful: {res.stdout.strip()}")
            return True
        elif st in ['failed', 'canceled']:
            print(f"\n    Job {st}: {status_resp.get('error')}")
            return False

def main():
    print(f"Starting mascot asset generation. Total tasks: {len(TASKS)}")
    success_count = 0
    for i, t in enumerate(TASKS, 1):
        print(f"\n--- Task {i}/{len(TASKS)}: {t['category']}/{t['name']} ---")
        ok = process_task(t)
        if ok:
            success_count += 1
        time.sleep(2)
    print(f"\nCompleted {success_count}/{len(TASKS)} tasks.")

if __name__ == '__main__':
    main()
