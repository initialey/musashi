# 武蔵通商 採用サイト｜下層ページ（会社を知る） Hero 〜 ローカルナビ

Figma `9CJMHGoxwmbhJVxc2AvylL` / node `827:52372`
「下層ページ（採用　会社を知る）」の **Hero 〜 ローカルナビ** を静的HTML+CSSで実装したもの。

> このディレクトリは AI Bet Tracker 本体とは独立したマークアップ検証用です。
> `docs/` は `src/dashboard.py` の生成物なので触れていません。

## ファイル

```
index.html                    マークアップ（lucide アイコンはインライン SVG）
css/tokens.css                デザイントークン
css/style.css                 レイアウト・コンポーネント
assets/                       画像（現状はプレースホルダ / assets/README.md 参照）
tools/make_placeholders.py    プレースホルダ画像の生成
tools/shot.py                 Playwright スクショ + Figma実測値との突き合わせ
shots/                        375 / 768 / 1280 / 375-menu-open
```

## 確認

```
python3 tools/shot.py
```

375 / 768 / 1280 を撮影し、以下を自動チェックする。

- コンテナ幅・ローカルナビ高さ・pill 高さ
- hero 見出し3種のフォントサイズと letter-spacing
- 各幅で横スクロール（はみ出し）が発生しないこと
- 375 でハンバーガードロワーが開くこと

## 実装ルール

- Figma の絶対座標は使わず、**全幅帯 + `max-width: 1040px`** の縦積みで再構築。
  `x=-4` / `width=1281` のような 1px のズレは正規化した。
- カラー・タイポは `css/tokens.css` に集約。`[A]` が指定トークン、
  `[B]` が「デザインには在るがトークン化されていない Figma 実測値」。
- アイコンは lucide に統一（Figma 側は Iconify 混在）。
- SP は自社設計。ローカルナビは 900px 以下で 3 カラム、600px 以下で 2 カラム、
  グローバルナビは 1080px 以下でドロワーへ。

## letter-spacing の単位について

Figma 変数の `letterSpacing: 4` などは **px ではなく %**。
本文01 (14px, ls=4) の design context が `tracking: 0.56px` (= 14 × 4%) を返すことで確認済み。
`tokens.css` では `em` に換算して保持している（`--ls-4: .04em`）。

## 指定トークンから外れた箇所

デザインに存在するがトークン定義に無い値があり、`tokens.css` の `[B]` として
出所（ノードID）付きで分離してある。実装を優先し、トークン側は変更していない。

| 種別 | 値 | 用途 |
|---|---|---|
| color | `#0f3684` / `#3961b0` | ローカルナビ帯 / pill |
| color | `#06c755` | LINE CTA |
| color | `#5e5e5e` / `#f4f4f4` / `#454545` / `#7b7b7b` / `#e7e7e7` | hero下地・電話ブロック・罫線ほか |
| gradient | `linear-gradient(171.34deg, #013df0, #200877)` | ヘッダーCTA |
| font-size | 48 / 20 / 18 / 13 / 11 / 10 px | H1・電話番号・LINE CTA・グローバルナビ・パンくず・営業時間 |
| letter-spacing | 2% / 6% / 8% | ナビpill・営業時間・電話番号 |

font-weight は Figma 側に DemiLight(350) / Light(300) があるが、
指定ルール（400/500/700）に合わせて **400 に丸めている**。
