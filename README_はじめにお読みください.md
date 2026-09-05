# Jom! マレーシア！ 連載マンガ アーカイブ  ―  無料ホームページ

週刊情報誌 Mtown の連載マンガを、**サーバー代0円・広告なし**で、
だれでも第1話から続けて読めるようにするための一式です。

---

## 毎週の更新（これだけ）

```
1. images/<話数>/ フォルダ（例: images/4）に PDF を入れる
      第4話.pdf     ← 本編（1枚の大きい画像。ファイル名に「話」か「本編」）
      おまけ.pdf    ← 任意（ファイル名に「おまけ」）
      info.txt      ← 任意（タイトル・掲載月）
2. 「更新.bat」をダブルクリック
      → PDFが画像に変換され、一覧(episodes.js)も作り直される
3. このフォルダごと Cloudflare Pages に再アップロード → 反映（約1分）
```

### 特別回（広告など、本編ではない回）

第15話と第16話のあいだに差し込む特別回は、フォルダ名を
**「15-16特別回」**（＝`<前の話>-<次の話><ラベル>`）にして、その中にPDFを入れます。

```
images/15-16特別回/
    すずらん整体院.pdf   ← PDF1本。★このファイル名が一覧の副見出しに出ます
    info.txt            ← 任意（タイトル／掲載月）
```

- 一覧では第15話の直後・第16話の直前に「特別回」バッジ付きで表示され、
  読書中も 15話 → 特別回 → 16話 の順で自動的につながります。
- **★恒久ルール：特別回の一覧の副見出しには、PDFのファイル名（拡張子なし）を表示する。**
  例）`すずらん整体院.pdf` → 一覧には「すずらん整体院」と表示（「第16話と第17話のあいだ」等は出さない）。
  広告回はスポンサー名をそのままPDFのファイル名にしておくこと。
- ラベル（フォルダ名の「特別回」の部分）は「PR」「広告」など自由に変えられます。

### 空のフォルダは表示されません

`images/` の中に**中身が空のフォルダ**（PDFが入っていないフォルダ）があっても、
サイトには一切表示されません。先に番号フォルダだけ作っておいて、あとからPDFを入れる運用でOKです。

---

## ファイル構成

```
Mtownマンガアーカイブ/
├─ index.html        ← サイト本体（さわらない）
├─ site.js           ← 文言・登場人物リスト（手で編集OK）
├─ episodes.js       ← 話の一覧（自動生成・さわらない）
├─ build.py / 更新.bat        ← PDF→画像＋一覧づくり
├─ scripts/prep_assets.py     ← ロゴ・キャラ画像の加工（下記）
├─ HP素材/           ← ロゴ・キャラの「元画像」を置く場所
├─ assets/           ← prep_assets.py が作る、サイトで使う画像
├─ images/<数字>/     ← 各話のPDFと、変換後の _pages/
└─ README_はじめにお読みください.md
```

---

## ① 各話フォルダ（images/<数字>/）

- フォルダ名は **話数の数字だけ**（`images/1`, `images/2` …）
- 本編PDF … 名前に「話」か「本編」／おまけPDF … 名前に「おまけ」
- `info.txt`（任意・メモ帳で作成、`images/1/info.txt` に見本）:

```
タイトル: 屋台デビューの巻
掲載: 2026-04
```

`タイトル` が無ければ「第N話」と表示。`掲載` は並び替えに使われます。

---

## ② バナー・ロゴ・キャラクター画像（HP素材 → assets）

トップのバナーやロゴ、登場人物の画像は、**HP素材/ に元画像を置き**、
`scripts/prep_assets.py` で加工して `assets/` に書き出します。

```bash
python scripts/prep_assets.py
```

- 使う元画像:
  - `HP素材/PC用バナー.png` … トップのバナー（PC表示）
  - `HP素材/スマホ用バナー.png` … トップのバナー（スマホ表示）
  - `HP素材/Mtownロゴ.jpeg` … ヘッダー・フッターの Mtown ロゴ
  - `HP素材/タカシ.png` `ヌル.png` `ケビン.png` `ハルト.png` `マユミ.png` `ミヤタ.png` `リョウ.png`
    … 各キャラの立ち絵（登場人物タブで使用。右のフルボディを自動で切り出し・背景透過）
- バナー画像を差し替えたら、もう一度 `python scripts/prep_assets.py` を実行するだけ
- 画面の文言は `site.js` で編集:
  - `SITE.about` … タブ「この漫画について」の紹介文・作者
  - `SITE.contact` … タブ「おといあわせ」の連絡先
  - `CHARACTERS` … タブ「登場人物」の名前・肩書き・並び順

---

## ③ 公開について（設定済み）

このプロジェクトは **GitHubリポジトリ `mtown-jom-malaysia` ＋ Cloudflare Pages** で公開されています。

- 本番URL: **https://jom-malaysia.pages.dev/** （Cloudflareのプロジェクト名で決まる。個人名なし）
- GitHubリポジトリはコード置き場。`hanei.bat`（git push）を実行すると Cloudflare が自動で再デプロイする。

### 更新の流れ（毎週）

```
1. 新しい回のPDFを images/<話数>/ に入れる（特別回は images/<前>-<次>特別回/）
2. koushin.bat をダブルクリック（PDF → 画像に変換）
3. hanei.bat をダブルクリック（git push → Cloudflare が1〜2分で反映）
```

### Cloudflare Pages の初期設定（済んでいれば不要）

1. <https://dash.cloudflare.com/sign-up> で無料アカウント作成（氏名は不要）
2. **Workers & Pages → Create → Pages → Connect to Git** → GitHubを認可
3. リポジトリ `mtown-jom-malaysia` を選択
4. Project name = `jom-malaysia`（＝URLになる）／ Production branch = `main`
5. Framework preset = **None** ／ Build command = **空欄** ／ Build output directory = `/`
6. **Save and Deploy** → `https://jom-malaysia.pages.dev/` で公開

---

## サイトの読み味（電子コミックサイト風）

- トップ = バナー＋「第1話から読む」「最新話を読む」ボタン＋話の一覧
- 一覧の下に3つのタブ: **この漫画について / 登場人物 / おといあわせ**
- 話をタップ → 読書画面（本編を大きく表示。おまけがあれば[本編][おまけ]タブ）
- 各話の最後に **「第◯話を読む ›」** ボタン → 一覧に戻らず次の話へ
- 左右キー・スワイプで前後の話へ。スマホ最適化

---

## 更新.bat が動かないとき

初回だけ、変換用の部品が要ります。コマンドプロンプトで:

```
pip install pymupdf pillow
```

Mac は `更新.bat` の代わりに `python3 build.py` / `python3 scripts/prep_assets.py`。

---

## 補足

- `assets/_pages/` `.build_cache.json` は自動生成物（消しても作り直されます）
- キャラ画像の切り出し位置がズレる場合は `scripts/prep_assets.py` の
  `border_flood_transparent` の `tol` / `thresh` や、`do_char` の切り出し比率を調整
- 公開前に、念のため Mtown 編集部へひとこと共有しておくと安全です
