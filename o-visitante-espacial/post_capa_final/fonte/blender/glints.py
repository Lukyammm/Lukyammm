"""Add light glints to the velvet: Orion (Betelgeuse a little red) plus faint random glints
where the fabric catches the light. Keeps off the book using the outline saved by the render.

usage: python3 glints.py <render.png> <out.png> <A|B> [strength]
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

inp, outp, variant = sys.argv[1:4]
strength = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
with_orion = not (len(sys.argv) > 5 and sys.argv[5] == 'noorion')
img = Image.open(inp).convert('RGB')
W, H = img.size
k = W / 1620.0
a = np.asarray(img).astype(np.float32) / 255.0

# book outline -> mask with a margin
meta = json.load(open(inp + '.json'))
pts = np.array(meta['book_pts'], dtype=np.float64) * (W / meta['w'])


def hull(points):
    p = sorted(map(tuple, points))
    def cross(o, a_, b):
        return (a_[0] - o[0]) * (b[1] - o[1]) - (a_[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in p:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(p):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return lower[:-1] + upper[:-1]


m = Image.new('L', (W, H), 0)
ImageDraw.Draw(m).polygon(hull(pts), fill=255)
m = m.filter(ImageFilter.GaussianBlur(18 * k))
book_mask = np.asarray(m).astype(np.float32) / 255.0 > 0.02

lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
lum_s = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6 * k))).astype(np.float32) / 255.0

layer = np.zeros_like(a)


def gauss(cx, cy, sigma, color, amp):
    r = int(max(3, sigma * 4))
    x0, x1 = int(max(0, cx - r)), int(min(W, cx + r + 1))
    y0, y1 = int(max(0, cy - r)), int(min(H, cy + r + 1))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * sigma * sigma)) * amp
    layer[y0:y1, x0:x1] += g[..., None] * np.array(color, np.float32)


rng = np.random.default_rng(23)


def glint(cx, cy, amp, color, size=1.0):
    """A sparkle from a few fibres: a core, one or two tiny neighbours and a faint halo."""
    fabric = 0.75 + 0.5 * float(np.clip(lum_s[int(cy), int(cx)] / 0.08, 0, 1))
    amp *= fabric * strength
    gauss(cx, cy, 1.25 * k * size, color, amp)
    for _ in range(int(rng.integers(1, 3))):
        ang = rng.uniform(0, 2 * np.pi)
        d = rng.uniform(2.0, 3.6) * k * size
        gauss(cx + d * np.cos(ang), cy + d * np.sin(ang), 0.8 * k * size, color, amp * rng.uniform(0.22, 0.4))
    gauss(cx, cy, 5.0 * k * size, color, amp * 0.1)


# Orion from real coordinates (RA, Dec in degrees, magnitude, tint)
ORION = [
    ('Betelgeuse', 88.79, 7.41, 0.5, (1.0, 0.58, 0.40)),
    ('Rigel', 78.63, -8.20, 0.13, (0.84, 0.9, 1.0)),
    ('Bellatrix', 81.28, 6.35, 1.64, (0.88, 0.92, 1.0)),
    ('Alnilam', 84.05, -1.20, 1.69, (0.9, 0.93, 1.0)),
    ('Alnitak', 85.19, -1.94, 1.77, (0.9, 0.93, 1.0)),
    ('Mintaka', 83.00, -0.30, 2.23, (0.9, 0.93, 1.0)),
    ('Saiph', 86.94, -9.67, 2.06, (0.9, 0.93, 1.0)),
    ('Meissa', 83.78, 9.93, 3.39, (0.95, 0.95, 1.0)),
    ('Hatysa', 83.86, -5.91, 2.77, (0.92, 0.94, 1.0)),
    ('M42', 83.82, -5.39, 4.0, (0.92, 0.94, 1.0)),
]
box_x0, box_w, box_y0 = 0.80, 0.165, 0.06
scale = box_w * W / (88.79 - 78.63)
for name, ra, dec, mag, col in (ORION if with_orion else []):
    x = box_x0 * W + (88.79 - ra) * scale
    y = box_y0 * H + (9.93 - dec) * scale
    if book_mask[int(y), int(x)]:
        print('star over the book:', name)
    amp = 0.40 + 0.40 * (1 - np.clip((mag + 0.2) / 4.4, 0, 1))
    if name == 'Betelgeuse':
        amp *= 1.45     # its red tint reads dimmer than the white stars
    glint(x, y, amp, col, size=1.3 if name == 'Betelgeuse' else 1.15 if name == 'Rigel' else 1.0)

# faint glints where the light catches the pile
prob = np.clip(lum_s, 0, None) ** 1.6
prob[book_mask] = 0
if variant == 'A':
    prob[int(0.45 * H):, :] = 0
else:
    prob[int(0.62 * H):, :] *= 0.4
# keep the Orion area for Orion
if with_orion:
    prob[int(0.03 * H):int(0.36 * H), int(0.78 * W):] *= 0.15
prob = prob.ravel() / prob.sum()
for idx in rng.choice(prob.size, size=int(210), p=prob):
    y, x = divmod(int(idx), W)
    amp = float(rng.uniform(0.04, 0.17)) * (1.8 if rng.random() < 0.06 else 1.0)
    glint(x + rng.uniform(-0.5, 0.5), y + rng.uniform(-0.5, 0.5), amp, (0.86, 0.9, 1.0), size=float(rng.uniform(0.75, 1.0)))

# light spill
spill = np.stack([np.asarray(Image.fromarray(np.clip(layer[..., c] * 255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * k))) for c in range(3)], -1).astype(np.float32) / 255.0
out = 1 - (1 - a) * (1 - np.clip(layer + 0.35 * spill, 0, 1))   # screen blend
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(outp)
print('ok', outp)
