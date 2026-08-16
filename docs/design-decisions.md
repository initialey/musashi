# Design decisions

デザイン実装で「なぜそうしたか」を残す記録。新しい判断は末尾に追記する。

---

## 2026-08-16 武蔵通商 採用下層ページ / トークン体系の一本化

対象: `mockups/musashi-recruit/`
出典: Figma `9CJMHGoxwmbhJVxc2AvylL` / node `827:52372`「下層ページ（採用　会社を知る）」の Hero 〜 ローカルナビ

### 1. `[A]` / `[B]` の区別を解消し、単一のトークン体系に統合した

初回実装では `tokens.css` を 2 段構えにしていた。

- `[A]` … 指定された正式トークン（5 色 / weight 3 段 / size 5 段 ほか）
- `[B]` … デザインには存在するがトークン定義に無い Figma 実測値

これは「参照側がどちらの層を見ればよいか」が毎回判断になり、
`[B]` が非公式扱いのまま残り続ける。**`[B]` を正式トークンに昇格させ、区別を廃止**した。
`style.css` は `tokens.css` の変数だけを参照し、生値を書かない。

検証: 未定義参照 0 / 未使用トークン 0 / 生の色・font-size・letter-spacing・line-height の残存 0。

昇格した値と確定した名前:

| 旧 `[B]` の値 | 新トークン | 用途 (Figma node) |
|---|---|---|
| `#0f3684` | `--c-brand-navy` | ローカルナビ帯 (`952:25668`) |
| `#3961b0` | `--c-brand-light` | ナビ pill (`952:25642` ほか) |
| `#06c755` | `--c-line-brand` | LINE 応募 CTA (`952:25688`) — 下記 2. 参照 |
| `#5e5e5e` | `--c-hero-base` | hero 下地（写真を multiply）(`841:16191`) |
| `#f4f4f4` | `--c-surface-subtle` | 電話ブロック (`125:11363`) |
| `#454545` | `--c-text-muted` | 営業時間 (`125:11378`) |
| `#7b7b7b` | `--c-border` | パンくず下線 (`93:8882`) |
| `#e7e7e7` | `--c-text-on-dark-muted` | パンくず現在地 (`93:9193`) |
| `rgba(52,52,52,.8)` | `--c-overlay-dark` | グローバルナビ帯 (`125:11385`) |
| `rgba(255,255,255,.5)` | `--c-border-hero` | hero 区切り線 (`848:16285`) |
| `48 / 20 / 18 / 13 / 11 / 10 px` | `--fs-48` ほか | H1・電話番号・LINE CTA・グローバルナビ・パンくず・営業時間 |
| `2% / 6% / 8%` | `--ls-2` / `--ls-6` / `--ls-8` | ナビ pill・営業時間・電話番号 |
| `1.2 / 1.4` | `--lh-tight` / `--lh-snug` | 営業時間・LINE CTA |

あわせて、実装時に生値で書いていた `#fff` / `#000` / ドロワー区切り線 /
角丸 999px / SP 用の 36・28px / `-.09em` もトークン化した
（`--c-text-inverse` `--c-text-strong` `--c-border-drawer` `--radius-round`
`--fs-36` `--fs-28` `--ls-tight`）。

`--ls-0` と `--ls-1` はこの範囲では未使用だが、Figma 変数
「本文（小）(ls=0)」「小見出し01 / リード文中サイズ (ls=1)」に対応するため
スケールの欠番を作らないよう残している。

### 2. LINE の緑は自社パレットと別系統として固定する

`--c-line-brand: #06c755` は LINE ヤフー社のサービスガイドラインで定められた
ブランドカラーで、**自社のブランドパレットとは別系統**。
トーン調整・近似色への置換・ダークモード等での自動変換はいずれも不可。
`tokens.css` に、この制約を明記した固定コメントを付けている。

`--c-brand-*` の系列には入れず、独立したブロックとして定義した。
将来ダークモード対応などでパレットを一括変換する際に、
ここだけ除外すべきことがトークン定義から読み取れるようにするため。

### 3. Figma の `letterSpacing` は px ではなく %

Figma 変数の `本文01: letterSpacing: 4` は px ではなく **%**。
同テキストの design context が `tracking: 0.56px` (= 14px × 4%) を返すことで確認した。
トークンは `em` に換算して保持する（`--ls-4: .04em`）。
px で持つと font-size 変更時に比率が壊れるため。

### 4. font-weight は 400/500/700 に丸める

Figma のグローバルナビは DemiLight(350)、営業時間は Light(300) を使っているが、
指定ルールの 3 段（400/500/700）に合わせて **いずれも 400 に丸めた**。
Noto Sans JP の可変軸を使えば 350/300 も出せるが、
ウェイトを 3 段に固定する方針を優先している。

### 5. 絶対座標は使わず、全幅帯 + `max-width: 1040px` で再構築

Figma は Auto Layout をほぼ使っておらず全要素が絶対配置。
座標には `x=-4` `width=1281` `left: 5357.76171875` のような
1280 グリッドから 1px 前後ずれた値や端数が多数含まれる。
これを再現すると responsive にならないため、座標は破棄し、
全幅帯 + `max-width: 1040px`（= 1280 − 左右 120px）の縦積みで組み直した。

### 6. アイコンは lucide に統一

Figma 側は Iconify の複数セット混在（fluent-mdl2 / basil / lucide / ri /
icon-park-outline / material-symbols / carbon / lsicon / grommet-icons / pinhead）。
書き出し SVG をそのまま使わず、**lucide のインライン SVG に寄せた**
（`phone` / `mail` / `chevron-down` / `chevron-right` / `menu` / `x`）。
外部リクエストが発生せず、`currentColor` でテーマに追従できる。

### 7. 画像アセットは未取得（環境要因）

`www.figma.com` / `api.figma.com` が egress ポリシーで **403 (CONNECT tunnel failed)**
のため、design context が返す書き出し URL に到達できない。
組織のネットワークポリシーによる遮断なので回避はしていない。

ロゴ・hero 写真・LINE マークの 3 点は、**デザイン実寸と同じジオメトリ**の
プレースホルダを同梱し、サイズは CSS 側で固定してある。
実ファイルを同名で上書きすればレイアウトは動かない。
手順とノード ID は `mockups/musashi-recruit/assets/README.md`。

### 既知の差分

ローカルナビの `RECRUIT` の字送りを **0.36px → 0.48px** に変更した。
Figma は親ブロックに `0.36px` を絶対値で当てており、
24px と 12px の 2 サイズに同じ px 値がかかっている。
`em` ベースのスケールに載せ替えた結果、12px 側は `--ls-3` (.03em = 0.36px) で
完全一致、24px 側は `--ls-2` (.02em = 0.48px) となり 0.12px/字ぶん広い。
`RECRUIT` 7 文字で合計 0.84px の差で、視認できる差ではないと判断した。
厳密一致が必要なら `--ls-1_5: .015em` を足す。

---

## 2026-08-16 専用リポジトリ `initialey/musashi` への切り出し

### 経緯

このマークアップは当初、別プロジェクト（AI Bet Tracker）のリポジトリ内に
`mockups/musashi-recruit/` として同居していた。クライアント名を含む成果物が
無関係なリポジトリの履歴に残る状態だったため、専用の private リポジトリへ分離した。

`git filter-repo` で該当パスのコミットだけを抽出し、履歴を保持したまま root に配置している。

```
git filter-repo --force \
  --path mockups/musashi-recruit/ \
  --path docs/design-decisions.md \
  --path-rename mockups/musashi-recruit/:
```

`--subdirectory-filter` ではなく `--path` を並べたのは、`docs/design-decisions.md` が
`mockups/` の外にあり、`--subdirectory-filter` だと落ちてしまうため。
この記録自体もクライアント案件の判断ログなので、コードと一緒に移す必要があった。

### パスの読み替え

上の 2026-08-16「トークン体系の一本化」エントリは同居していた頃に書いたもので、
`mockups/musashi-recruit/...` 表記が残っている。**このリポジトリでは
`mockups/musashi-recruit/` を root に読み替える**（例: `mockups/musashi-recruit/assets/README.md`
→ `assets/README.md`）。

過去エントリを書き換えていないのは、`CLAUDE.md` の運用ルール
「追記のみ。過去のエントリは書き換えない」に従ったため。
当時の記述をそのまま残し、現在地は新しいエントリで示す。

### リポジトリ名を `musashi-recruit` ではなく `musashi` にした理由

元の Figma ファイルは採用サイトだけでなくコーポレート側
（サービス紹介・設備・拠点・事例紹介・お客様の声・会社情報）も含む。
`-recruit` を付けると、コーポレート側のページを起こしたときに名前が実態からずれるため、
武蔵通商案件全体の傘として `musashi` にした。

### 分離元に残した措置

AI Bet Tracker 側では、クライアント名を含むコミットが乗っていたのは
作業用フィーチャーブランチのみで、既定ブランチ `master` には一度も入っていなかった。
そのためリポジトリ全体の履歴書き換え（`filter-repo` + master の force-push）は行わず、
**フィーチャーブランチの削除**で対応した。

`master` は 30 分おきに bot コミットが積まれる稼働中のリポジトリで、
全 SHA を書き換えると実行中のワークフローと競合する実害があるため。
到達可能な履歴からクライアント名入りのコミットが消えるという結果は同じ。

なお force-push / ブランチ削除の後も、コミットは一定期間 SHA 指定で
GitHub API から到達可能。完全消去が要件なら GitHub Support への purge 依頼が必要になる。
