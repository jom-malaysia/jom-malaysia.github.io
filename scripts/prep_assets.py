# -*- coding: utf-8 -*-
"""HP素材/ の元画像を、サイト用の軽量WebPに加工して assets/ へ書き出す。
   - バナー(PC/スマホ)・Mtownロゴ・作者アイコン・登場人物7名
   バナーやキャラ画像を差し替えたら、これを実行するだけ。
   使い方: python scripts/prep_assets.py
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "HP素材")
OUT = os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)


def border_flood_transparent(im, tol=32, thresh=238):
    """画像の四辺から白っぽい領域を塗りつぶして透過にする"""
    im = im.convert("RGBA")
    w, h = im.size
    # 一時的にRGBへ（floodfillはRGBA可だが基準色扱いを単純化）
    rgb = im.convert("RGB")
    seen_key = (255, 0, 255)
    px = rgb.load()
    seeds = []
    step = max(4, w // 120)
    for x in range(0, w, step):
        seeds.append((x, 0)); seeds.append((x, h - 1))
    for y in range(0, h, step):
        seeds.append((0, y)); seeds.append((w - 1, y))
    for s in seeds:
        r, g, b = px[s]
        if r >= thresh and g >= thresh and b >= thresh:
            ImageDraw.floodfill(rgb, s, seen_key, thresh=tol)
    key_px = rgb.load()
    out = im.copy()
    op = out.load()
    for y in range(h):
        for x in range(w):
            if key_px[x, y] == seen_key:
                op[x, y] = (0, 0, 0, 0)
    return out


def autocrop(im, pad=12):
    bbox = im.split()[3].getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l = max(0, l - pad); t = max(0, t - pad)
    r = min(im.width, r + pad); b = min(im.height, b + pad)
    return im.crop((l, t, r, b))


def resize_w(im, w):
    if im.width <= w:
        return im
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def save(im, name, w=None, q=82):
    """name の拡張子が .webp なら軽量WebP（透過対応）で書き出す"""
    if w:
        im = resize_w(im, w)
    p = os.path.join(OUT, name)
    if name.lower().endswith(".webp"):
        im.save(p, "WEBP", quality=q, method=6)
    else:
        im.save(p)
    print(f"  {name}  {im.size}  {os.path.getsize(p)//1024}KB")


def do_logo(src_name, out_name, w):
    im = Image.open(os.path.join(SRC, src_name))
    im = border_flood_transparent(im, tol=40, thresh=232)
    im = autocrop(im, pad=6)
    save(im, out_name, w, q=88)


def do_banner(src_name, out_name, w):
    """バナー画像はそのまま（背景透過なし）縮小してWebP化"""
    im = Image.open(os.path.join(SRC, src_name)).convert("RGB")
    save(im, out_name, w, q=82)


def do_square(src_name, out_name, w, q=84):
    """中央を正方形に切り出して縮小（作者アイコン等）"""
    im = Image.open(os.path.join(SRC, src_name)).convert("RGB")
    s = min(im.size)
    l = (im.width - s) // 2
    t = (im.height - s) // 2
    save(im.crop((l, t, l + s, t + s)), out_name, w, q=q)


# --- 登場人物: HP素材/HP用/<名前>.png（正方形カード）をそのまま縮小して使う ---
HP_CHAR_DIR = os.path.join(SRC, "HP用")
CHAR_SLUG = {
    "タカシ": "takashi", "ヌル": "nur", "ケビン": "kevin",
    "ミヤタ": "miyata", "マユミ": "mayumi", "ハルト": "haruto", "リョウ": "ryo",
}


def do_hpchar(jp, slug):
    for ext in (".png", ".PNG", ".jpeg", ".jpg"):
        p = os.path.join(HP_CHAR_DIR, jp + ext)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            save(im, f"char-{slug}.webp", 560, q=80)
            return
    print(f"  （見つからず）HP用/{jp}.png")


if __name__ == "__main__":
    print("バナー:")
    do_banner("PC用バナー.png", "banner-pc.webp", 1500)
    do_banner("スマホ用バナー.png", "banner-sp.webp", 960)
    print("ロゴ:")
    do_logo("Mtownロゴ.jpeg", "mtown-logo.webp", 560)
    print("作者:")
    do_square("しまだなおき.png", "author.webp", 220, q=82)
    print("登場人物:")
    for jp, slug in CHAR_SLUG.items():
        do_hpchar(jp, slug)
    print("完了 → assets/")
