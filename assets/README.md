# assets / 差し替え手順

このディレクトリの画像は **すべてローカル生成のプレースホルダ** です。実アセットではありません。

## なぜプレースホルダなのか

Figma の design context は書き出しアセットを
`https://www.figma.com/api/mcp/asset/...` の URL で返しますが、このセッションの
egress ポリシーが `www.figma.com` / `api.figma.com` を **403 (CONNECT tunnel failed)**
で遮断しているため取得できませんでした。プロキシの診断にも記録されています。

```
$ curl -sS "$HTTPS_PROXY/__agentproxy/status"
"recentRelayFailures": [
  { "kind": "connect_rejected",
    "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
    "host": "www.figma.com:443" }, ...
]
```

これは組織のネットワークポリシーによる遮断なので、回避はしていません
(`/root/.ccr/README.md` の指示どおり、報告のみ)。
レイアウト検証を止めないよう、**デザイン実寸と同じジオメトリ**のプレースホルダを
`tools/make_placeholders.py` で生成して差し込んでいます。

## 差し替え対象

| ファイル | Figma ノード | CSS 上の表示サイズ | object-fit | 備考 |
|---|---|---|---|---|
| `logo.png` | `30:28` (logo) | 150 × 39 | `contain` | 武蔵通商ロゴ。2x (300×78) で書き出し |
| `hero.png` | `841:16191` (Rectangle 396) | 帯いっぱい (1280 × 355) | `cover` / `object-position: bottom` | 下地 `#5e5e5e` の上に `mix-blend-mode: multiply` + `opacity: .8` で重なる |
| `line-brand.png` | `952:25690` (LINE_Brand_icon 2) | 71 × 73 | `contain` | LINE ブランドマーク。2x (142×146) で書き出し |

## 差し替え方法

1. Figma から上記 3 ノードを書き出す（`hero` は写真なので `.jpg` 推奨）
2. このディレクトリの同名ファイルを上書き（拡張子を変える場合は
   `index.html` の `src` も合わせて変更）
3. `python3 tools/shot.py` を再実行してスクリーンショットを更新

ジオメトリは CSS 側で固定してあるので、差し替えてもレイアウトは動きません。

## アイコンについて

アイコン類は Figma の書き出し SVG ではなく、実装ルール
「アイコンは lucide に統一（Iconify 混在は寄せる）」に従って
`index.html` にインライン SVG で直接記述しています（`phone` / `mail` /
`chevron-down` / `chevron-right` / `menu` / `x`）。差し替え不要です。
