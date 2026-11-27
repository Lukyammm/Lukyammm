"""Compose the 3D book render over a lighter studio background, with an optional wet-floor reflection.

usage: python3 compose_bg.py <book_alpha.png> <reflect.png> <out.png> <palette> <reflection 0/1>
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

PALETTES = {
    # (light pool behind the book, mid, edges/corners, floor tint at the bottom)
    'slate': ((86, 98, 130), (48, 56, 82), (24, 28, 43), (30, 35, 52)),
    'ardosia_clara': ((112, 124, 152), (66, 75, 103), (33, 38, 56), (40, 46, 66)),
    'pedra': ((150, 139, 124), (96, 88, 78), (48, 44, 40), (62, 57, 51)),
    'crepusculo': ((92, 92, 128), (52, 52, 82), (22, 24, 40), (70, 42, 48)),
}


def background(w, h, pal, cx, cy):
    c0, c1, c2, floor = [np.array(c, np.float32) for c in PALETTES[pal]]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    # elliptical light pool, a bit wider than tall
    d = np.sqrt(((x - cx) / (w * 0.62)) ** 2 + ((y - cy) / (h * 0.55)) ** 2)
    t1 = np.clip(d / 0.55, 0, 1)
    t2 = np.clip((d - 0.55) / 0.75, 0, 1)
    s1 = t1 * t1 * (3 - 2 * t1)
    s2 = t2 * t2 * (3 - 2 * t2)
    img = c0 * (1 - s1)[..., None] + c1 * s1[..., None]
    img = img * (1 - s2)[..., None] + c2 * s2[..., None]
    # the lower part reads as floor: blend slowly towards the floor tint
    tf = np.clip((y - h * 0.80) / (h * 0.20), 0, 1)[..., None]
    img = img * (1 - 0.55 * tf) + floor * (0.55 * tf)
    # fine grain so the gradient does not band on Instagram
    rng = np.random.default_rng(3)
    img += rng.normal(0, 2.2, img.shape).astype(np.float32)
    return img


def reflection_layer(refl, opacity=0.30, length=520, blur=3.0, amp=2.5, wave=22.0):
    r = refl.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(r).astype(np.float32)
    h, w = a.shape[:2]
    # ripple: shift each row a little, like a film of water
    out = np.zeros_like(a)
    for yy in range(h):
        s = int(round(amp * np.sin(2 * np.pi * yy / wave) + 0.6 * amp * np.sin(2 * np.pi * yy / (wave * 2.7) + 1.3)))
        out[yy] = np.roll(a[yy], s, axis=0)
    alpha = out[..., 3] / 255.0
    # fade per column, starting where the reflection starts (the contact line)
    has = alpha > 0.02
    start = np.where(has.any(axis=0), has.argmax(axis=0), h).astype(np.float32)
    # smooth the start line so the fade has no steps
    k = 41
    pad = np.pad(start, (k // 2, k // 2), mode='edge')
    start = np.convolve(pad, np.ones(k) / k, mode='valid')
    yy = np.arange(h, dtype=np.float32)[:, None]
    f = np.clip(1 - (yy - start[None, :]) / length, 0, 1) ** 1.6
    alpha = alpha * f * opacity
    return out[..., :3], alpha


def main():
    book_p, refl_p, out_p, pal, use_refl = sys.argv[1:6]
    book = Image.open(book_p).convert('RGBA')
    w, h = book.size
    bg = background(w, h, pal, cx=w * 0.52, cy=h * 0.40)
    if use_refl == '1':
        rgb, alpha = reflection_layer(Image.open(refl_p).convert('RGBA'))
        bg = bg * (1 - alpha[..., None]) + rgb * alpha[..., None]
    b = np.asarray(book).astype(np.float32)
    ba = b[..., 3:4] / 255.0
    comp = bg * (1 - ba) + b[..., :3] * ba
    Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8)).save(out_p)


if __name__ == '__main__':
    main()
