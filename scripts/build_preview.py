# -*- coding: utf-8 -*-
"""テスト版プレビュー（1ファイル・全画像埋め込み）を作る。
   出力: scratchpad/mtown-preview.html （Artifactで公開する用）"""
import base64, json, mimetypes, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_preview.html"

def durl(p):
    p = pathlib.Path(p)
    mt = mimetypes.guess_type(p.name)[0] or "image/webp"
    return f"data:{mt};base64," + base64.b64encode(p.read_bytes()).decode()

html = (ROOT / "index.html").read_text(encoding="utf-8")
site_js = (ROOT / "site.js").read_text(encoding="utf-8")
eps = json.loads(re.search(r"window\.EPISODES\s*=\s*(\[.*?\]);",
                           (ROOT / "episodes.js").read_text(encoding="utf-8"), re.S).group(1))

# Artifact は 16MB 上限。全話は入らないので、容量予算内で「先頭の数話＋特別回とその前後」を選ぶ。
BUDGET = 8 * 1024 * 1024
eps.sort(key=lambda e: e.get("sort", e.get("no", 0)))

def esize(e):
    paths = [ROOT / e["thumb"]] + [ROOT / x for x in e["honpen"]] + [ROOT / x for x in e["omake"]]
    return sum(p.stat().st_size for p in paths if p.exists())

must = set()  # 優先で入れる index（特別回とその前後の話）
for i, e in enumerate(eps):
    if e.get("kind") == "special":
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(eps):
                must.add(j)

order = list(must) + [i for i in range(len(eps)) if i not in must]
used, keep_idx = 0, set()
for i in order:
    s = esize(eps[i])
    if keep_idx and used + s > BUDGET and i not in must:
        continue
    used += s
    keep_idx.add(i)

kept = []
for i, e in enumerate(eps):
    if i not in keep_idx:
        continue
    e["thumb"] = durl(ROOT / e["thumb"])
    e["honpen"] = [durl(ROOT / x) for x in e["honpen"]]
    e["omake"] = [durl(ROOT / x) for x in e["omake"]]
    kept.append(e)
trimmed = len(eps) - len(kept)
eps = kept
if trimmed:
    print(f"※ テスト版は容量の都合で {len(eps)} 話分のみ埋め込み（残り {trimmed} 話は省略）")

# assets を data URI マップに
amap = {f"assets/{p.name}": durl(p) for p in (ROOT / "assets").glob("*.webp")}

# HTML中の静的な assets 参照（バナーの <source srcset> / ロゴ <img> 等）を直接置換
for k, v in amap.items():
    html = html.replace(k, v)

shim = (
    "<script>window.__A__=" + json.dumps(amap) + ";"
    "(function(){var M=window.__A__;"
    "function fix(i){var s=i.getAttribute&&i.getAttribute('src');if(s&&M[s])i.src=M[s];}"
    "new MutationObserver(function(ms){ms.forEach(function(m){[].forEach.call(m.addedNodes,function(n){"
    "if(n.nodeType!==1)return;if(n.tagName==='IMG')fix(n);"
    "n.querySelectorAll&&[].forEach.call(n.querySelectorAll('img'),fix);});});})"
    ".observe(document.documentElement,{childList:true,subtree:true});"
    "document.addEventListener('DOMContentLoaded',function(){[].forEach.call(document.querySelectorAll('img'),fix);});"
    "[].forEach.call(document.querySelectorAll('img'),fix);})();</script>"
)

site_js = site_js.replace('title: "Jom! マレーシア！ 連載マンガ アーカイブ"',
                          'title: "Jom! マレーシア！ 連載マンガ アーカイブ（テスト版）"')

inline = shim + "\n<script>\n" + site_js + "\nwindow.EPISODES=" + json.dumps(eps, ensure_ascii=False) + ";\n</script>"
html = html.replace('<script src="site.js"></script>\n<script src="episodes.js"></script>', inline)

OUT.write_text(html, encoding="utf-8")
print(OUT, f"{OUT.stat().st_size/1024/1024:.2f} MB")
