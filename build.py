# -*- coding: utf-8 -*-
"""
Mtown 連載マンガ アーカイブ  ―  ビルドスクリプト

images/ 内のフォルダを全部スキャンして、
  ・本編PDF   → 画像に変換（images/<フォルダ>/_pages/honpen_XX.jpg）
  ・おまけPDF → 画像に変換（images/<フォルダ>/_pages/omake_XX.jpg）
  ・サムネイル → _pages/_thumb.jpg
  ・一覧データ episodes.js を自動生成
します。

使い方: このフォルダで  更新.bat  をダブルクリック（または `python build.py`）

■ 通常の話
  images/1/           ← フォルダ名は「話数の数字だけ」
    第1話.pdf          ← 本編（ファイル名に「話」か「本編」を含める）
    おまけ.pdf         ← 任意（ファイル名に「おまけ」を含める）
    info.txt           ← 任意（タイトル・掲載月）

■ 特別回（広告など、本編とは別の回）
  images/15-16特別回/   ← 「<前の話>-<次の話><ラベル>」の形。第15話と第16話の
                          あいだに差し込まれる。ラベル（特別回 等）は自由。
    特別回.pdf          ← 本編と同じ扱いのPDF（名前は自由）
    info.txt           ← 任意（タイトル＝表示名、掲載月）
"""

import io
import json
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF が必要です。次を実行してください:  pip install pymupdf pillow")
    sys.exit(1)

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT, "images")

# ---- 画質設定（必要なら変更）---------------------------------
RENDER_DPI = 200
MAX_WIDTH = 1800
JPEG_QUALITY = 82
THUMB_WIDTH = 600
THUMB_QUALITY = 78
# ------------------------------------------------------------

OMAKE_RE = re.compile(r"(おまけ|オマケ|omake|bonus|extra|付録)", re.I)
HONPEN_RE = re.compile(r"(本編|第?\s*\d+\s*話|特別|広告|PR|honpen|main|ep\d+)", re.I)
# 特別回フォルダ:  「15-16特別回」「15_16 PR」「15-16」など
SPECIAL_RE = re.compile(r"^(\d+)\s*[-_〜~ー－]\s*(\d+)\s*(.*)$")


def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "cp932"):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def parse_info(folder):
    info = {"title": "", "date": "", "note": ""}
    p = os.path.join(folder, "info.txt")
    if not os.path.isfile(p):
        return info
    for line in read_text(p).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(タイトル|title|掲載|date|日付|メモ|note)\s*[:：]\s*(.+)$", line, re.I)
        if not m:
            continue
        key, val = m.group(1).lower(), m.group(2).strip()
        if key in ("タイトル", "title"):
            info["title"] = val
        elif key in ("掲載", "date", "日付"):
            info["date"] = normalize_date(val)
        elif key in ("メモ", "note"):
            info["note"] = val
    return info


def normalize_date(s):
    s = s.strip().replace("/", "-").replace(".", "-").replace("年", "-").replace("月", "")
    m = re.match(r"^(\d{4})-(\d{1,2})", s)
    return f"{m.group(1)}-{int(m.group(2)):02d}" if m else s


def classify_folder(name):
    """フォルダ名から (種類, 並び順キー, 付随情報) を返す。対象外なら None"""
    if name.isdigit():
        no = int(name)
        return {"kind": "episode", "no": no, "sort": float(no), "id": str(no)}
    m = SPECIAL_RE.match(name)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        label = (m.group(3).strip() or "特別回")
        return {
            "kind": "special", "between": [a, b], "label": label,
            "sort": a + 0.5, "id": f"s{a}_{b}",
        }
    return None


def classify_pdfs(folder):
    pdfs = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    omake = [f for f in pdfs if OMAKE_RE.search(f)]
    rest = [f for f in pdfs if f not in omake]
    honpen = [f for f in rest if HONPEN_RE.search(f)] or rest
    honpen_file = max(honpen, key=lambda f: os.path.getsize(os.path.join(folder, f))) if honpen else None
    omake_file = omake[0] if omake else None
    return honpen_file, omake_file


def render_pdf(pdf_path, out_dir, prefix):
    doc = fitz.open(pdf_path)
    out_paths = []
    mat = fitz.Matrix(RENDER_DPI / 72.0, RENDER_DPI / 72.0)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        if img.width > MAX_WIDTH:
            h = round(img.height * MAX_WIDTH / img.width)
            img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
        name = f"{prefix}_{i:02d}.jpg"
        img.save(os.path.join(out_dir, name), "JPEG", quality=JPEG_QUALITY, optimize=True)
        out_paths.append(name)
    doc.close()
    return out_paths


def make_thumb(src_img_path, dst_path):
    img = Image.open(src_img_path).convert("RGB")
    if img.width > THUMB_WIDTH:
        h = round(img.height * THUMB_WIDTH / img.width)
        img = img.resize((THUMB_WIDTH, h), Image.LANCZOS)
    img.save(dst_path, "JPEG", quality=THUMB_QUALITY, optimize=True)


def process_folder(name, cache):
    """1フォルダを処理して episodes.js 用の dict を返す（不可なら None）。cache は更新される。"""
    meta = classify_folder(name)
    if not meta:
        return None
    folder = os.path.join(IMAGES_DIR, name)
    if not os.path.isdir(folder):
        return None
    tag = f"[第{meta['no']}話]" if meta["kind"] == "episode" else f"[{meta['label']}({meta['between'][0]}-{meta['between'][1]})]"

    # 中身が空のフォルダは「表示しない」= 何も出さず静かにスキップ
    contents = [f for f in os.listdir(folder) if not f.startswith(".") and f != "_pages"]
    if not contents:
        return None

    honpen_file, omake_file = classify_pdfs(folder)
    if not honpen_file:
        print(f"{tag} PDFが見つかりません → スキップ（表示しません）")
        return None

    honpen_path = os.path.join(folder, honpen_file)
    omake_path = os.path.join(folder, omake_file) if omake_file else None
    info = parse_info(folder)
    pages_dir = os.path.join(folder, "_pages")

    sig = {
        "honpen": [honpen_file, os.path.getmtime(honpen_path), os.path.getsize(honpen_path)],
        "omake": ([omake_file, os.path.getmtime(omake_path), os.path.getsize(omake_path)] if omake_path else None),
        "settings": [RENDER_DPI, MAX_WIDTH, JPEG_QUALITY],
    }
    info_p = os.path.join(folder, "info.txt")
    info_mtime = os.path.getmtime(info_p) if os.path.isfile(info_p) else 0

    cached = cache.get(name)
    up_to_date = (
        cached and cached.get("sig") == sig and os.path.isdir(pages_dir)
        and cached.get("info_mtime") == info_mtime
        and all(os.path.exists(os.path.join(pages_dir, n)) for n in cached.get("honpen_imgs", []))
    )

    if up_to_date:
        honpen_imgs = cached["honpen_imgs"]
        omake_imgs = cached["omake_imgs"]
        print(f"{tag} 変更なし（スキップ）")
    else:
        os.makedirs(pages_dir, exist_ok=True)
        for old in os.listdir(pages_dir):
            if old.lower().endswith((".jpg", ".png")):
                os.remove(os.path.join(pages_dir, old))
        print(f"{tag} 変換中: {honpen_file}" + (f" + {omake_file}" if omake_file else ""))
        honpen_imgs = render_pdf(honpen_path, pages_dir, "honpen")
        omake_imgs = render_pdf(omake_path, pages_dir, "omake") if omake_path else []
        if honpen_imgs:
            make_thumb(os.path.join(pages_dir, honpen_imgs[0]), os.path.join(pages_dir, "_thumb.jpg"))

    cache[name] = {"sig": sig, "info_mtime": info_mtime,
                   "honpen_imgs": honpen_imgs, "omake_imgs": omake_imgs}

    rel = f"images/{name}/_pages"
    entry = {
        "kind": meta["kind"],
        "id": meta["id"],
        "sort": meta["sort"],
        "date": info["date"],
        "note": info["note"],
        "thumb": f"{rel}/_thumb.jpg",
        "honpen": [f"{rel}/{n}" for n in honpen_imgs],
        "omake": [f"{rel}/{n}" for n in omake_imgs],
    }
    if meta["kind"] == "episode":
        entry["no"] = meta["no"]
        entry["title"] = info["title"] or f"第{meta['no']}話"
    else:
        entry["label"] = meta["label"]
        entry["between"] = meta["between"]
        # 一覧の副見出しは PDF のファイル名（拡張子なし）＝広告主名などを表示する
        entry["sponsor"] = os.path.splitext(honpen_file)[0]
        entry["title"] = info["title"] or meta["label"]
    return entry


def main():
    if not os.path.isdir(IMAGES_DIR):
        print("images フォルダが見つかりません")
        sys.exit(1)

    cache_path = os.path.join(ROOT, ".build_cache.json")
    try:
        cache = json.load(open(cache_path, encoding="utf-8")) if os.path.isfile(cache_path) else {}
    except Exception:
        cache = {}

    names = [d for d in os.listdir(IMAGES_DIR)
             if os.path.isdir(os.path.join(IMAGES_DIR, d)) and classify_folder(d)]
    names.sort(key=lambda n: (classify_folder(n)["sort"], n))
    if not names:
        print("images/ の中に対象フォルダがありません。")
        print("例:  images/1/第1話.pdf  /  images/15-16特別回/特別回.pdf")
        sys.exit(0)

    new_cache = {}
    episodes = []
    for name in names:
        entry = process_folder(name, new_cache)
        if entry:
            episodes.append(entry)
        # 途中で止めても再変換しなくて済むよう、1フォルダごとにキャッシュを保存
        json.dump(new_cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    episodes.sort(key=lambda e: e["sort"])

    out = (
        "/* ===================================================================\n"
        "   このファイルは build.py（更新.bat）が自動生成します。手で編集しない。\n"
        "   通常の話 : images/<番号>/ に 第N話.pdf（＋任意の おまけ.pdf / info.txt）\n"
        "   特別回   : images/<前>-<次>ラベル/ に PDF（例 images/15-16特別回/）\n"
        "   入れて 更新.bat を実行するだけ。\n"
        "   =================================================================== */\n"
        "window.EPISODES = "
        + json.dumps(episodes, ensure_ascii=False, indent=2)
        + ";\n"
    )
    with open(os.path.join(ROOT, "episodes.js"), "w", encoding="utf-8") as f:
        f.write(out)

    n_ep = sum(1 for e in episodes if e["kind"] == "episode")
    n_sp = sum(1 for e in episodes if e["kind"] == "special")
    n_omake = sum(1 for e in episodes if e["omake"])
    print("-" * 48)
    print(f"完了: 本編 {n_ep} 話 ／ 特別回 {n_sp} ／ おまけ付き {n_omake}")
    print("episodes.js を更新しました。")
    print("次: このフォルダを Cloudflare Pages に再アップロードしてください。")


if __name__ == "__main__":
    main()
