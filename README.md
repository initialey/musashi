# 武蔵通商 採用サイト｜下層ページ（会社を知る） Hero 〜 ローカルナビ

Figma `9CJMHGoxwmbhJVxc2AvylL` / node `827:52372`
「下層ページ（採用　会社を知る）」の **Hero 〜 ローカルナビ** を静的HTML+CSSで実装したもの。

## ファイル

```
index.html                    マークアップ（lucide アイコンはインライン SVG）
css/tokens.css                デザイントークン
css/style.css                 レイアウト・コンポーネント
assets/                       画像（現状はプレースホルダ / assets/README.md 参照）
tools/make_placeholders.py    プレースホルダ画像の生成
tools/shot.py                 Playwright スクショ + Figma実測値との突き合わせ
shots/                        375 / 768 / 1280 / 375-menu-open
docs/design-decisions.md      デザイン判断の記録
CLAUDE.md                     Claude Code 向けの運用ルール
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
- カラー・タイポ・角丸は `css/tokens.css` に集約した単一のトークン体系。
  `style.css` は変数だけを参照し、生値は書かない。
- アイコンは lucide に統一（Figma 側は Iconify 混在）。
- SP は自社設計。ローカルナビは 900px 以下で 3 カラム、600px 以下で 2 カラム、
  グローバルナビは 1080px 以下でドロワーへ。

## letter-spacing の単位について

Figma 変数の `letterSpacing: 4` などは **px ではなく %**。
本文01 (14px, ls=4) の design context が `tracking: 0.56px` (= 14 × 4%) を返すことで確認済み。
`tokens.css` では `em` に換算して保持している（`--ls-4: .04em`）。

## トークンについて

当初は「指定トークン」と「Figma 実測値」を 2 段構えで分けていたが、
**すべて正式トークンに統合**して区別を廃止した。各トークンには出所（Figma ノードID
または Figma 変数名）をコメントで残してある。

LINE の緑 `--c-line-brand: #06c755` だけは LINE ヤフー社のガイドラインで定められた
**固定値**で、自社パレットとは別系統。トーン調整・置換は不可（`tokens.css` に明記）。

font-weight は Figma 側に DemiLight(350) / Light(300) があるが、
指定ルール（400/500/700）に合わせて **400 に丸めている**。

統合の経緯と既知の差分は [`docs/design-decisions.md`](docs/design-decisions.md) を参照。
