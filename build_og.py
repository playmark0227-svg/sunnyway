#!/usr/bin/env python3
"""Generate a branded 1200x630 Open Graph share card for Sunnyway."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 1200, 630

# Brand palette
CREAM   = (255, 250, 243)
CREAM2  = (255, 243, 230)
ORANGE  = (242, 107, 31)
ORANGE_S= (255, 140, 66)
PEACH   = (255, 217, 194)
CORAL   = (255, 107, 125)
PINK    = (255, 182, 200)
YELLOW  = (255, 212, 59)
GREEN_S = (184, 224, 122)
INK     = (26, 26, 46)
INK2    = (90, 90, 110)

# --- Background: soft vertical cream gradient ---
bg = Image.new("RGB", (W, H), CREAM)
top, bot = CREAM, CREAM2
for y in range(H):
    t = y / H
    r = int(top[0] + (bot[0]-top[0])*t)
    g = int(top[1] + (bot[1]-top[1])*t)
    b = int(top[2] + (bot[2]-top[2])*t)
    for x in range(W):
        pass
# faster: paint rows
px = bg.load()
for y in range(H):
    t = y / H
    r = int(top[0] + (bot[0]-top[0])*t)
    g = int(top[1] + (bot[1]-top[1])*t)
    b = int(top[2] + (bot[2]-top[2])*t)
    for x in range(W):
        px[x, y] = (r, g, b)

# --- Decorative soft blobs ---
def soft_circle(canvas, cx, cy, rad, color, alpha):
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx-rad, cy-rad, cx+rad, cy+rad], fill=color+(alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(rad*0.32))
    canvas.alpha_composite(layer)

bg = bg.convert("RGBA")
soft_circle(bg, 1080, 120, 230, PEACH, 150)
soft_circle(bg, 980, 540, 200, PINK, 110)
soft_circle(bg, 120, 560, 180, GREEN_S, 90)
soft_circle(bg, 60, 80, 150, YELLOW, 70)

# --- Mascot on the right ---
try:
    mascot = Image.open("assets/mascot.png").convert("RGBA")
    target_h = 410
    ratio = target_h / mascot.height
    mascot = mascot.resize((int(mascot.width*ratio), target_h), Image.LANCZOS)
    # subtle drop shadow
    shadow = Image.new("RGBA", (W, H), (0,0,0,0))
    sm = mascot.split()[3].point(lambda a: int(a*0.30))
    shsrc = Image.new("RGBA", mascot.size, (26,26,46,255))
    shsrc.putalpha(sm)
    mx = 838
    my = H - target_h - 48
    shadow.paste(shsrc, (mx+14, my+20), shsrc)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    bg.alpha_composite(shadow)
    bg.alpha_composite(mascot, (mx, my))
except Exception as e:
    print("mascot skip:", e)

draw = ImageDraw.Draw(bg)

# --- Fonts ---
def font(path, size):
    return ImageFont.truetype(path, size)

HELV = "/System/Library/Fonts/Helvetica.ttc"
HIRA = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
HIRA_W8 = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
import os
if not os.path.exists(HIRA):
    HIRA = "/System/Library/Fonts/Hiragino Sans GB.ttc"
if not os.path.exists(HIRA_W8):
    HIRA_W8 = HIRA

f_brand   = font(HELV, 116)   # Sunnyway wordmark (Helvetica Bold via index)
try:
    f_brand = ImageFont.truetype(HELV, 116, index=1)  # Bold
except Exception:
    f_brand = font(HELV, 116)
f_eyebrow = font(HELV, 26)
f_jp_big  = font(HIRA_W8, 44)
f_jp_sub  = font(HIRA, 27)

# --- Eyebrow pill ---
eye_text = "K-BEAUTY  ×  JAPAN MARKETING"
ex, ey = 90, 96
pad_x, pad_y = 26, 14
tb = draw.textbbox((0,0), eye_text, font=f_eyebrow)
tw, th = tb[2]-tb[0], tb[3]-tb[1]
draw.rounded_rectangle([ex, ey, ex+tw+pad_x*2, ey+th+pad_y*2+8], radius=40, fill=ORANGE)
draw.text((ex+pad_x, ey+pad_y), eye_text, font=f_eyebrow, fill=(255,255,255))

# --- Wordmark ---
wy = ey + th + pad_y*2 + 52
draw.text((86, wy), "Sunnyway", font=f_brand, fill=INK)
# orange dot accent
bb = draw.textbbox((86, wy), "Sunnyway", font=f_brand)
draw.ellipse([bb[2]+10, bb[3]-34, bb[2]+40, bb[3]-4], fill=ORANGE)

# --- JP headline ---
jy = bb[3] + 30
draw.text((90, jy), "韓国の素敵を、日本に届ける。", font=f_jp_big, fill=INK)

# --- JP sub ---
sy = jy + 64
draw.text((92, sy), "インフルエンサーキャスティング ／ SNS運用 ／ ブランドPR", font=f_jp_sub, fill=INK2)

# --- bottom accent bar ---
draw.rectangle([0, H-12, W, H], fill=ORANGE)
# multi-color ticks
cols = [ORANGE, CORAL, PINK, YELLOW, GREEN_S]
seg = W // (len(cols))
for i, c in enumerate(cols):
    draw.rectangle([i*seg, H-12, (i+1)*seg, H], fill=c)

bg.convert("RGB").save("assets/og-card.png", "PNG", optimize=True)
print("OG card written: assets/og-card.png", bg.size)
