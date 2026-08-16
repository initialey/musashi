# musashi — プロジェクト概要 (for Claude Code)

武蔵通商のサイトのマークアップ。Figma からの design-to-code。
元の Figma ファイルは採用サイトとコーポレート側（サービス紹介・設備・拠点・
事例紹介・お客様の声・会社情報）の両方を含むため、このリポジトリは
武蔵通商案件全体の受け皿として使う。

現在の実装範囲は、採用下層ページ「会社を知る」の **Hero 〜 ローカルナビ** のみ。

- Figma: `9CJMHGoxwmbhJVxc2AvylL` / フレーム `827:52372`
  「下層ページ（採用　会社を知る）」
- スタック: 素の HTML + CSS。ビルドなし、依存なし。`index.html` を開けば動く
- 検証: `python3 tools/shot.py`（Playwright）

```
index.html                    マークアップ（アイコンはインライン SVG）
css/tokens.css                デザイントークン ← 変更時は必ず下記ルールを読む
css/style.css                 レイアウト・コンポーネント
assets/                       画像（現状すべてプレースホルダ）
tools/shot.py                 375/768/1280 撮影 + Figma実測値との突き合わせ
tools/make_placeholders.py    プレースホルダ画像の生成
shots/                        撮影結果（コミット対象）
docs/design-decisions.md      デザイン判断の記録
```

---

## tokens.css の運用ルール

**1. トークンは単一体系。階層を作らない。**
以前は「指定トークン」と「Figma 実測値」を `[A]` / `[B]` に分けていたが、
参照側が毎回どちらを見るか判断する羽目になり `[B]` が非公式のまま残るため廃止した。
デザインに存在する値は全部 `:root` の正式トークンにする。**この 2 段構えに戻さない。**

**2. `style.css` に生値を書かない。**
色・font-size・letter-spacing・line-height・角丸はすべて `var(--*)` 経由。
レイアウトの px（padding / gap / min-height）だけは直値でよい。

チェック方法:

```bash
python3 - <<'PY'
import re, pathlib
tok = pathlib.Path('css/tokens.css').read_text()
sty = pathlib.Path('css/style.css').read_text()
defined = set(re.findall(r'^\s*(--[\w-]+)\s*:', tok, re.M)) | \
          set(re.findall(r'^\s*(--[\w-]+)\s*:', sty, re.M))
used = set(re.findall(r'var\((--[\w-]+)', sty))
print('未定義の参照:', sorted(used - defined) or 'なし')
strip = re.sub(r'/\*.*?\*/', '', sty, flags=re.S)
print('生の色:', re.findall(r'(?<!var\()(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\))', strip) or 'なし')
PY
```

**3. 新しいトークンには出所をコメントで残す。**
Figma のノード ID（`952:25668` 形式）か Figma 変数名（`メイン背景用ブルー` 等）。
後から「この値はどこから来たのか」を追えるようにするため。

**4. `letter-spacing` は `em` で持つ。px にしない。**
Figma の `letterSpacing: 4` は px ではなく **%**。
本文01 (14px, ls=4) の design context が `tracking: 0.56px` (= 14 × 4%) を返すことで確認済み。
px で持つと font-size 変更時に比率が壊れる。

**5. `--c-line-brand` は触らない。**
`#06c755` は LINE ヤフー社のサービスガイドラインで定められた固定値で、
自社パレットとは別系統。トーン調整・近似色への置換・ダークモード等での
自動変換はいずれも不可。`--c-brand-*` の系列に入れず独立ブロックに置いてあるのは、
パレットを一括変換する際にここだけ除外できるようにするため。

**6. font-weight は 400 / 500 / 700 の 3 段のみ。**
Figma には DemiLight(350) / Light(300) もあるが 400 に丸める。

**7. `--ls-0` `--ls-1` は未使用でも消さない。**
Figma 変数「本文（小）(ls=0)」「小見出し01 / リード文中サイズ (ls=1)」に対応する。
未実装セクションで使うのでスケールに欠番を作らない。

---

## docs/design-decisions.md の運用ルール

**「なぜそうしたか」だけを書く。** 何をしたかは commit とコードが持っている。

- **追記のみ。過去のエントリは書き換えない。** 判断が変わったら新しい日付で追記し、
  古いエントリはそのまま残す（当時なぜそう判断したかが分からなくなるため）
- 見出しは `## YYYY-MM-DD 主題`。新しいものを**末尾**に足す
- 記録する対象:
  - Figma と実装が意図的に食い違っている箇所と、その理由
  - トークンの命名・分類の判断
  - 環境制約で妥協した箇所（例: アセットが取得できない）
  - 「既知の差分」— デザインとの差が残っているが許容した箇所と、その定量的な根拠
- 記録しないもの: 手順、TODO、進捗

design-decisions.md に書いた制約とコードが食い違ったら、**コードではなく記録を疑う前に
記録を読む**。過去の判断を知らずに「直した」結果デザインから外れる事故を防ぐため。

---

## 実装ルール

- **Figma の絶対座標は使わない。** Auto Layout がほぼ未使用で全要素が絶対配置、
  かつ `x=-4` `width=1281` `left: 5357.76171875` のような 1px 前後のズレや端数が多い。
  座標は破棄し、**全幅帯 + `max-width: 1040px`**（= 1280 − 左右 120px）の縦積みで組む
- **アイコンは lucide に統一。** Figma 側は Iconify 混在
  （fluent-mdl2 / basil / lucide / ri / icon-park-outline / material-symbols /
  carbon / lsicon / grommet-icons / pinhead）。書き出し SVG は使わず、
  lucide のインライン SVG に寄せる。`currentColor` でテーマ追従させる
- **SP は自社設計。** Figma に SP カンプがないため、3カラム→1カラム、
  横並びは折返しかグリッドに落とす。現状のブレークポイントは
  1080（グローバルナビ→ドロワー）/ 900（ローカルナビ3カラム）/ 768（電話・タグライン畳み）
  / 600（ローカルナビ2カラム）
- **カードは 1 コンポーネントで回す。** 写真カードは `img 321×242` + 見出し + 説明

## アセット

`assets/` の画像は**すべてプレースホルダ**。実アセットではない。
Figma の書き出し URL を取得できない環境で作業したため、
デザイン実寸と同じジオメトリのダミーを `tools/make_placeholders.py` で生成している。
差し替え手順とノード ID は `assets/README.md`。

サイズは CSS 側で固定してあるので、同名で上書きすればレイアウトは動かない。

## 変更後に必ず走らせる

```bash
python3 tools/shot.py
```

375 / 768 / 1280 を撮影し、コンテナ幅・ローカルナビ高さ・pill 高さ・
hero 見出し 3 種の font-size と letter-spacing・横スクロールの有無・
ドロワーの開閉を自動チェックする。**全項目 PASS を確認してからコミットする。**
`shots/` の更新もコミットに含める（レビューで差分が見えるように）。

Chromium が `/opt/pw-browsers/chromium` にある環境ではそれを使う。
別の場所にある場合は `CHROMIUM_PATH` で指定する。

---

## Claude Code の設定

このリポジトリでは **fable-like** の output style を使う。

```
/config → Output style → fable-like → /clear
```

`/clear` まで含めて 1 セット。output style は次のターンから効くため、
切り替え前の文体が残った文脈を持ち越さないように会話をクリアする。

> 補足: この output style は初期セットアップを行った環境には存在せず、
> 名前の検証ができていない。`/config` に出てこない場合は、
> 別名で登録されているか、`~/.claude/output-styles/` への配置が必要。
