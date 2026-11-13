#!/usr/bin/env python3
"""Render full HD (1080x1920) 30fps showcase reel featuring the new Mascot Asset Library.

Incorporates:
- Multi-angle perspectives (three_quarter_left, three_quarter_right)
- New dynamic poses (walking_front, seated_desk, standing_laptop)
- Classic acting poses (arms_crossed, explain, victory, peace)
- Dynamic tight crop and pixel-perfect framing
- Custom UI cards, progress header, glowing connectors
- Word-synced Roman Urdu captions with gold active chip
- Mixed voiceover + background music + audio effects
"""

import json
import math
import os
import subprocess
import sys
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.expanduser('~/Zarkhaiz')
REEL_DIR = os.path.join(ROOT, 'video/outputdm-reel')
LIB_DIR = os.path.join(ROOT, 'mascot/library')
AUDIO_FILE = '/tmp/founder_reel_audio.aac'
OUTPUT_FILE = os.path.join(REEL_DIR, 'out/outputdm_mascot_library_showcase_v011.mp4')

TL = json.load(open(os.path.join(REEL_DIR, 'timeline.json')))
DUR = TL['dur']
FPS = 30
TOTAL_FRAMES = int(DUR * FPS)

W, H = 1080, 1920

# Colors
C_BG_TOP = (26, 20, 16)
C_BG_BOT = (11, 9, 7)
C_GOLD = (246, 181, 58)
C_GOLD_MUTED = (160, 115, 35)
C_CREAM = (247, 239, 229)
C_MUTED = (185, 171, 156)
C_CARD_BG = (26, 20, 16, 240)
C_CARD_BORDER = (246, 181, 58, 100)
C_GREEN = (37, 211, 102)
C_RED = (235, 60, 65)

# Fonts
FONT_TITLE = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf', 72)
FONT_SUB = ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf', 40)
FONT_HEADING = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 44)
FONT_BODY = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 30, index=0)
FONT_BODY_BOLD = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 30)
FONT_CAP = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 44)
FONT_LABEL = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 24)
FONT_CTA = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 38)

def load_and_crop(rel_path):
    p = os.path.join(LIB_DIR, rel_path)
    if not os.path.exists(p):
        p = os.path.join(ROOT, 'mascot/character/poses', rel_path)
    if os.path.exists(p):
        im = Image.open(p).convert('RGBA')
        bbox = im.getbbox()
        if bbox:
            return im.crop(bbox)
        return im
    print(f"Warning: {rel_path} not found")
    return None

ASSETS = {
    'three_quarter_left': load_and_crop('angles/three_quarter_left.png'),
    'three_quarter_right': load_and_crop('angles/three_quarter_right.png'),
    'profile_left': load_and_crop('angles/profile_left.png'),
    'walking_front': load_and_crop('poses/walking_front.png'),
    'seated_desk': load_and_crop('poses/seated_desk.png'),
    'standing_laptop': load_and_crop('poses/standing_laptop.png'),
    'arms_crossed': load_and_crop('poses/arms_crossed.png'),
    'explain': load_and_crop('poses/explain.png'),
    'victory': load_and_crop('poses/victory.png'),
    'peace': load_and_crop('poses/peace.png'),
    'confident': load_and_crop('poses/confident.png'),
}

# Pre-render static background gradient
BG_BASE = Image.new('RGB', (W, H))
for y in range(H):
    r = int(C_BG_TOP[0] + (C_BG_BOT[0] - C_BG_TOP[0]) * (y / H))
    g = int(C_BG_TOP[1] + (C_BG_BOT[1] - C_BG_TOP[1]) * (y / H))
    b = int(C_BG_TOP[2] + (C_BG_BOT[2] - C_BG_TOP[2]) * (y / H))
    BG_BASE.paste(Image.new('RGB', (W, 1), (r, g, b)), (0, y))

# Draw warm ambient glow at top center
glow = Image.new('RGBA', (700, 700), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
gdraw.ellipse([50, 50, 650, 650], fill=(246, 181, 58, 35))
glow = glow.filter(ImageFilter.GaussianBlur(80))
BG_BASE.paste(glow, (W // 2 - 350, -100), glow)

# Draw floor horizon
HORIZON_Y = 1350
draw_bg = ImageDraw.Draw(BG_BASE)
draw_bg.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(246, 181, 58, 60), width=2)
# Grid lines on floor
for i in range(-6, 16):
    x_top = W // 2 + i * 42
    x_bot = W // 2 + i * 165
    draw_bg.line([(x_top, HORIZON_Y), (x_bot, H)], fill=(246, 181, 58, 20), width=1)
for hy in range(HORIZON_Y + 45, H, 65):
    draw_bg.line([(0, hy), (W, hy)], fill=(246, 181, 58, 18), width=1)

def draw_shadow(target_layer, cx, cy, rx, ry, alpha=150):
    shadow = Image.new('RGBA', (rx * 2, ry * 2), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([0, 0, rx * 2, ry * 2], fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    target_layer.alpha_composite(shadow, (cx - rx, cy - ry))

def draw_card(draw, rect, title, lines, badge=None):
    x0, y0, x1, y1 = rect
    draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=C_CARD_BG, outline=C_CARD_BORDER, width=2)
    cy = y0 + 32
    if badge:
        bw = len(badge) * 14 + 28
        draw.rounded_rectangle([x0 + 32, cy, x0 + 32 + bw, cy + 32], radius=10, fill=(246, 181, 58, 40), outline=(246, 181, 58, 160), width=1)
        draw.text((x0 + 44, cy + 5), badge, fill=C_GOLD, font=FONT_LABEL)
        cy += 48
    if title:
        draw.text((x0 + 32, cy), title, fill=C_CREAM, font=FONT_HEADING)
        cy += 56
    for l in lines:
        draw.text((x0 + 32, cy), l, fill=C_MUTED, font=FONT_BODY)
        cy += 42

def place_character(layer, asset_name, target_h, align='right', custom_cx=None, feet_y=1660, bob=0):
    m = ASSETS.get(asset_name)
    if not m:
        return
    tw = int(m.width * (target_h / m.height))
    scaled = m.resize((tw, target_h), Image.Resampling.LANCZOS)

    if align == 'right':
        rx = 1010
        lx = rx - tw
        cx = lx + tw // 2
    elif align == 'center':
        cx = custom_cx if custom_cx is not None else W // 2
        lx = cx - tw // 2
    else: # left
        lx = 60
        cx = lx + tw // 2

    ty = int(feet_y - target_h + bob)
    draw_shadow(layer, cx, feet_y, int(tw * 0.35), 32)
    layer.alpha_composite(scaled, (lx, ty))

def render_frame(t):
    frame = BG_BASE.copy()
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Header & Progress
    draw.text((64, 75), "OUTPUTDM", fill=C_GOLD, font=FONT_LABEL)
    draw.text((W - 360, 75), "MASCOT SHOWCASE v011", fill=C_MUTED, font=FONT_LABEL)
    draw.line([(64, 110), (W - 64, 110)], fill=(246, 181, 58, 40), width=1)

    # Progress bar dots (9 scenes)
    scenes_t = [0.0, 4.1, 7.6, 13.9, 17.1, 21.8, 27.6, 31.3, 36.1, 38.75]
    cur_scene = 0
    for s_idx, st in enumerate(scenes_t[:-1]):
        if t >= st:
            cur_scene = s_idx
    dot_spacing = (W - 128) // 8
    for i in range(9):
        dx = 64 + i * dot_spacing
        dy = 132
        if i < cur_scene:
            draw.ellipse([dx - 6, dy - 6, dx + 6, dy + 6], fill=C_GOLD)
        elif i == cur_scene:
            pulse = 1.0 + 0.25 * math.sin(t * 8)
            r = int(8 * pulse)
            draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=C_GOLD, outline=C_CREAM, width=2)
        else:
            draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(55, 42, 34), outline=(100, 80, 65), width=1)
        if i < 8:
            nx = 64 + (i + 1) * dot_spacing
            draw.line([(dx + 10, dy), (nx - 10, dy)], fill=(246, 181, 58, 120 if i < cur_scene else 35), width=2)

    # Subtle breathing motion
    bob = math.sin(t * 3.5) * 4

    # Scene specific layouts
    if t < 4.1:  # Scene 1: Problem / Hook
        draw.text((70, 185), "MARKETING LEAK?", fill=(246, 181, 58, 25), font=FONT_TITLE)
        draw_card(draw, [64, 280, 520, 680], "Ad Spend Audit", [
            "• Monthly ad budget active",
            "• CAC rising every quarter",
            "• Website conversion flat",
            "• Why are leads leaking?",
            "• Audit your pipeline now."
        ], badge="DIAGNOSIS")
        place_character(layer, 'three_quarter_left', target_h=1160, align='right', bob=bob)

    elif t < 7.6:  # Scene 2: Founder Entrance
        draw.text((70, 185), "FOUNDER INTRO", fill=(246, 181, 58, 25), font=FONT_TITLE)
        # Mascot walking forward with smooth camera dolly
        prog = (t - 4.1) / 3.5
        th = int(1120 + 70 * min(1.0, prog))
        place_character(layer, 'walking_front', target_h=th, align='center', feet_y=int(1670 + prog * 10), bob=bob)
        draw_card(draw, [64, 250, 480, 480], "Muhammad Zarkhaiz", [
            "Founder, OutputDM",
            "Growth & Tech Partner",
            "Lahore, Pakistan"
        ], badge="LEADERSHIP")

    elif t < 13.9:  # Scene 3: Since 2018
        draw.text((70, 185), "SINCE 2018", fill=(246, 181, 58, 25), font=FONT_TITLE)
        draw_card(draw, [64, 270, 530, 720], "Proven Expertise", [
            "• Active Since 2018",
            "• Strategic HQ: Lahore",
            "• Scaling Pakistan & UAE",
            "• D2C E-Commerce & B2B",
            "• Proven ROAS & Retention",
            "• High-Growth Architecture"
        ], badge="TRACK RECORD")
        place_character(layer, 'standing_laptop', target_h=1180, align='right', bob=bob)

    elif t < 17.1:  # Scene 4: 3 Growth Leaks
        draw.text((70, 185), "3 MAJOR LEAKS", fill=(246, 181, 58, 25), font=FONT_TITLE)
        draw_card(draw, [64, 290, 540, 700], "The 3 Profit Drains", [
            "Most businesses lose customers",
            "at three identical stages:",
            "",
            "1. Discovery (Invisible)",
            "2. Retention (High Drop-off)",
            "3. Conversion (Zero Nurture)"
        ], badge="CRITICAL AUDIT")
        place_character(layer, 'explain', target_h=1160, align='right', bob=bob)

    elif t < 21.8:  # Scene 5: Detail of Leaks
        draw.text((70, 185), "WHERE CUSTOMERS LEAK", fill=(246, 181, 58, 25), font=FONT_TITLE)
        # 3 structured warning cards
        cards_y = [270, 420, 570]
        titles = ["1. Discovery Fail", "2. Bounce Friction", "3. Zero Follow-Up"]
        descs = ["Log dhoond hi nahi paate", "Website par rukte nahi", "Leads ka follow-up nahi hota"]
        for cy, tit, desc in zip(cards_y, titles, descs):
            draw.rounded_rectangle([64, cy, 540, cy + 125], radius=16, fill=C_CARD_BG, outline=C_RED, width=2)
            draw.text((90, cy + 22), f"[!] {tit}", fill=C_CREAM, font=FONT_BODY_BOLD)
            draw.text((90, cy + 68), desc, fill=C_MUTED, font=FONT_BODY)

        place_character(layer, 'three_quarter_right', target_h=1160, align='right', bob=bob)

    elif t < 27.6:  # Scene 6: One Unified System
        draw.text((70, 185), "ONE UNIFIED ENGINE", fill=(246, 181, 58, 25), font=FONT_TITLE)
        # 5 interconnected pills
        pills = ["1. Creative Content", "2. Targeted Ads", "3. Modern Website", "4. Organic SEO", "5. CRM Automation"]
        py = 260
        for idx, p in enumerate(pills):
            p_on = (t - 21.8) > (idx * 0.9)
            col_bg = (246, 181, 58, 85) if p_on else C_CARD_BG
            col_border = C_GOLD if p_on else (90, 70, 55)
            draw.rounded_rectangle([64, py, 450, py + 68], radius=34, fill=col_bg, outline=col_border, width=2)
            draw.text((94, py + 18), p, fill=C_CREAM if p_on else C_MUTED, font=FONT_BODY_BOLD)
            if idx < 4:
                draw.line([(257, py + 68), (257, py + 88)], fill=C_GOLD if p_on else (70, 55, 40), width=3)
            py += 88

        draw_card(draw, [475, 300, 680, 540], "Synced", [
            "All channels work",
            "as one engine.",
            "Maximum ROI."
        ], badge="SCALE")
        place_character(layer, 'victory', target_h=1170, align='right', bob=bob)

    elif t < 31.3:  # Scene 7: Only What You Need
        draw.text((70, 185), "CUSTOM ROADMAP", fill=(246, 181, 58, 25), font=FONT_TITLE)
        draw_card(draw, [64, 280, 540, 710], "Tailored Strategy", [
            "• Zero cookie-cutter retainers",
            "• No useless fluff services",
            "• Sirf wohi action items jo",
            "  aapke business ko waqai",
            "  chahiye agle level ke liye.",
            "• Clear revenue accountability."
        ], badge="OUR PROMISE")
        place_character(layer, 'arms_crossed', target_h=1180, align='right', bob=bob)

    elif t < 36.1:  # Scene 8: Call to Action (Seated at Desk)
        draw.text((70, 185), "BOOK REVIEW", fill=(246, 181, 58, 25), font=FONT_TITLE)
        # Seated desk mascot centered
        place_character(layer, 'seated_desk', target_h=1140, align='center', feet_y=1660, bob=bob * 0.4)

        # WhatsApp CTA Pill
        pulse = 1.0 + 0.04 * math.sin(t * 9)
        btn_w, btn_h = int(720 * pulse), int(105 * pulse)
        bx0 = (W - btn_w) // 2
        by0 = 245
        draw.rounded_rectangle([bx0, by0, bx0 + btn_w, by0 + btn_h], radius=52, fill=C_GREEN, outline=C_CREAM, width=2)
        draw.text((bx0 + 55, by0 + 32), "WhatsApp: +92 344 4441724", fill=(12, 35, 18), font=FONT_CTA)

        draw_card(draw, [bx0, by0 + btn_h + 18, bx0 + btn_w, by0 + btn_h + 150], None, [
            "Claim your complimentary 1-on-1 Digital Growth Review."
        ], badge="EXCLUSIVE AUDIT")

    else:  # Scene 9: Outro & Peace
        draw.text((70, 185), "OUTPUTDM", fill=(246, 181, 58, 25), font=FONT_TITLE)
        place_character(layer, 'peace', target_h=1180, align='center', feet_y=1660, bob=bob)

        # Brand outro box
        draw.rounded_rectangle([W // 2 - 260, 240, W // 2 + 260, 400], radius=24, fill=C_CARD_BG, outline=C_GOLD, width=3)
        draw.text((W // 2 - 180, 265), "OutputDM.com", fill=C_GOLD, font=FONT_TITLE)
        draw.text((W // 2 - 170, 345), "Digital Growth Partner", fill=C_CREAM, font=FONT_SUB)

    # Word-synced Dynamic Captions Layer
    cur_chunk = None
    for c in TL.get('chunks', []):
        if c['t0'] <= t < c['t1']:
            cur_chunk = c
            break

    if cur_chunk:
        words = cur_chunk['words']
        word_boxes = []
        total_w = 0
        spacing = 16
        for w_obj in words:
            w_text = w_obj['w'].replace('.', '').replace(',', '')
            bbox = FONT_CAP.getbbox(w_text)
            ww = bbox[2] - bbox[0]
            wh = bbox[3] - bbox[1]
            word_boxes.append((w_obj, w_text, ww, wh))
            total_w += ww + spacing
        total_w -= spacing

        cap_y = 1430
        start_x = (W - total_w) // 2

        # Draw caption backdrop pill
        draw.rounded_rectangle([start_x - 26, cap_y - 12, start_x + total_w + 26, cap_y + 60],
                               radius=18, fill=(18, 14, 11, 230), outline=(246, 181, 58, 80), width=1)

        curr_x = start_x
        for w_obj, w_text, ww, wh in word_boxes:
            is_active = (w_obj['t0'] <= t < w_obj['t1'])
            if is_active:
                # Golden highlight chip on current spoken word
                draw.rounded_rectangle([curr_x - 8, cap_y - 4, curr_x + ww + 8, cap_y + wh + 10],
                                       radius=8, fill=C_GOLD)
                draw.text((curr_x, cap_y), w_text, fill=(20, 14, 10), font=FONT_CAP)
            else:
                draw.text((curr_x, cap_y), w_text, fill=C_CREAM, font=FONT_CAP)
            curr_x += ww + spacing

    # Watermark at bottom
    draw.text((W // 2 - 170, 1790), "outputdm.com • Lahore", fill=(247, 239, 229, 90), font=FONT_LABEL)

    frame.paste(layer, (0, 0), layer)
    return frame

def main():
    print("=" * 60)
    print("OUTPUTDM SHOWCASE REEL RENDERER (v011 Mascot Library)")
    print("=" * 60)
    print(f"Target duration: {DUR:.2f}s | FPS: {FPS} | Total frames: {TOTAL_FRAMES}")
    print(f"Output path: {OUTPUT_FILE}")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-s', f"{W}x{H}",
        '-r', str(FPS),
        '-i', '-',
        '-i', AUDIO_FILE,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '256k',
        '-shortest',
        OUTPUT_FILE
    ]

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    t_start = time.time()
    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        img = render_frame(t)
        p.stdin.write(img.tobytes())

        if frame_idx % 60 == 0 or frame_idx == TOTAL_FRAMES - 1:
            pct = (frame_idx + 1) / TOTAL_FRAMES * 100
            fps_actual = (frame_idx + 1) / (time.time() - t_start + 1e-6)
            sys.stdout.write(f"\rProgress: {frame_idx + 1}/{TOTAL_FRAMES} ({pct:.1f}%) | {fps_actual:.1f} fps")
            sys.stdout.flush()

    p.stdin.close()
    p.wait()

    total_time = time.time() - t_start
    print(f"\n\nRender Complete in {total_time:.1f}s! ({TOTAL_FRAMES / total_time:.1f} avg fps)")
    print(f"Output saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
