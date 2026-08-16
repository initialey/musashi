"""Figma書き出しアセットの代替プレースホルダを生成する。

このセッションの egress ポリシーが figma.com を 403 で遮断しているため
（CONNECT tunnel failed / 組織のネットワークポリシー）、design context が
返す https://www.figma.com/api/mcp/asset/... を取得できない。
レイアウト検証を止めないよう、デザイン実寸と同じジオメトリの
プレースホルダをローカル生成して差し込む。

実アセットが手に入ったら assets/ の同名ファイルを差し替えるだけでよい。
詳細は assets/README.md を参照。
"""

from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# CSS 上の表示サイズ。PNG は 2x で書き出す。
LOGO_W, LOGO_H = 150, 39
HERO_W, HERO_H = 1280, 355
LINE_W, LINE_H = 71, 73

# チャンク1: 写真プレースホルダの実寸（Figma ノード上の width/height）
PHOTO_SPECS = {
    # ファイル名: (幅, 高さ, Figmaノード, 用途)
    "intro.jpg": (838, 540, "945:17634", "イントロ帯の写真"),
    "step1.jpg": (473, 358, "940:17603", "Step1 写真（右）"),
    "step2.jpg": (426, 352, "942:17606", "Step2 写真（左）"),
    "step3.jpg": (465, 411, "841:16282", "Step3 写真（右）"),
    # チャンク2: 社員の声「いいところ」×6（写真ノードが無い7件目=熱中症対策を除く）
    "voice1.jpg": (402, 280, "845:16168", "いいところ1 教育体制"),
    "voice2.jpg": (402, 280, "846:16217", "いいところ2 1日1案件"),
    "voice3.jpg": (402, 280, "846:16218", "いいところ3 車両設備"),
    "voice4.jpg": (402, 280, "846:16219", "いいところ4 休み"),
    "voice5.jpg": (402, 280, "846:16220", "いいところ5 子育て"),
    "voice7.jpg": (402, 280, "1712:27930", "いいところ7 二刀流人材"),
    # チャンク3: レアな仕事 上位3枚（col2/3 は写真ノードを確定できず319x200で仮置き）
    "job-top1.jpg": (319, 200, "1382:47011", "レア1 ビートルズ像"),
    "job-top2.jpg": (319, 200, "1155:25339", "レア2 ハーレー梱包"),
    "job-top3.jpg": (319, 200, "1383:47090", "レア3 大本山の鐘"),
}

# チャンク4: 福利厚生・社内活動（5サブセクション、計22枚）
# 実寸は 319〜322×240〜242 とノードごとに微妙に異なるため
# 320×240(4:3) に正規化。ノードID未特定の col2 は "推定" と付記。
WELFARE_SPECS = {
    "welfare1-1.jpg": "1562:28489 福利厚生サービス",
    "welfare1-2.jpg": "1562:28493(推定) 育休取得実績",
    "welfare1-3.jpg": "1562:28495 年間休日120日",
    "welfare1-4.jpg": "1568:28508 有給取得日数",
    "welfare1-5.jpg": "1568:28516 医療相談サービス",
    "welfare1-6.jpg": "1571:28652 提携ローン",
    "welfare2-1.jpg": "1568:28518 BBQ大会",
    "welfare2-2.jpg": "1568:28522(推定) 忘年会",
    "welfare2-3.jpg": "1568:28530 新入社員歓迎食事会",
    "welfare2-4.jpg": "1568:28524 周年行事",
    "welfare2-5.jpg": "1568:28528(推定) チームビルディング",
    "welfare2-6.jpg": "1568:28532 ビンゴ大会",
    "welfare3-1.jpg": "1571:28644 西武ライオンズ観戦",
    "welfare3-2.jpg": "1568:28569 東京ワイルズ観戦",
    "welfare4-1.jpg": "1568:28557 3110ファイトクラブ",
    "welfare4-2.jpg": "1718:24123 サバゲー部",
    "welfare5-1.jpg": "1568:28602 資格認定証授与式",
    "welfare5-2.jpg": "1568:28579(推定) 社内業績表彰制度",
    "welfare5-3.jpg": "1568:28588 社内勉強会",
    "welfare5-4.jpg": "1568:28581 業務改善提案活動",
    "welfare5-5.jpg": "1568:28586(推定) eラーニング",
    "welfare5-6.jpg": "1568:28591 技術力アップ研修",
}
WELFARE_W, WELFARE_H = 320, 240

SCALE = 2


def _px(v: int) -> int:
    return v * SCALE


def make_logo() -> None:
    w, h = _px(LOGO_W), _px(LOGO_H)
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6,
                        fill=(232, 235, 240, 255), outline=(180, 188, 200, 255))
    # 「M」のマークだけ模したシルエット（実ロゴの代替であることが分かる程度）
    d.ellipse([8, 10, 8 + h - 20, 10 + h - 20], outline=(26, 53, 101, 255), width=4)
    d.text((h + 2, h // 2 - 9), "LOGO 150x39", fill=(90, 100, 118, 255))
    img.save(ASSETS / "logo.png")


def make_hero() -> None:
    """hero 下地は #5e5e5e、その上に写真を multiply/opacity .8 で重ねる設計。

    プレースホルダは空〜建物を思わせる縦グラデーションにして、
    ブレンド後の見え方がデザインと大きく乖離しないようにする。
    """
    w, h = HERO_W, HERO_H
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    top = (206, 216, 230)
    bottom = (150, 158, 168)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line(
            [(0, y), (w, y)],
            fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    # 右手に建物のシルエット（デザインの写真の構図に合わせる）。
    # multiply 合成後に主張しすぎないよう、コントラストは低めにする。
    d.rectangle([w * 0.52, h * 0.16, w * 0.90, h], fill=(176, 182, 190))
    d.rectangle([w * 0.86, h * 0.10, w * 0.99, h], fill=(160, 166, 175))
    for row in range(4):
        for col in range(9):
            x = w * 0.545 + col * (w * 0.037)
            y = h * 0.26 + row * (h * 0.18)
            d.rectangle([x, y, x + w * 0.018, y + h * 0.10], fill=(163, 169, 178))
    img.save(ASSETS / "hero.png")


def make_logo_white() -> None:
    """フッター用の白抜きロゴプレースホルダ。

    通常ロゴに CSS の brightness(0) invert(1) をかけると、淡いグレーの
    塗りごと単色の白ブロックに潰れてしまう(ロゴ内部の階調が失われる)ため、
    暗い背景でもディテールが残る専用のプレースホルダを別途用意する。
    """
    w, h = _px(LOGO_W), _px(LOGO_H)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, outline=(255, 255, 255, 220), width=2)
    d.ellipse([8, 10, 8 + h - 20, 10 + h - 20], outline=(255, 255, 255, 220), width=4)
    d.text((h + 2, h // 2 - 9), "LOGO 150x39", fill=(255, 255, 255, 220))
    img.save(ASSETS / "logo-white.png")


def make_photo(filename: str, w: int, h: int, node: str, label: str,
                seed: int = 0) -> None:
    """汎用の写真プレースホルダ。実寸ジオメトリを維持し、
    ノードIDと用途をファイル名コメントとして画像内に焼き込む。"""
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # seed で色相を振り、複数枚が並んでも区別しやすくする
    hues = [(214, 224, 234), (222, 214, 202), (210, 222, 214), (226, 216, 226)]
    top = hues[seed % len(hues)]
    bottom = tuple(max(0, c - 46) for c in top)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)],
               fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    # 中央に対角線のプレースホルダー記号
    inset = min(w, h) * 0.08
    d.line([(inset, inset), (w - inset, h - inset)], fill=(255, 255, 255), width=2)
    d.line([(w - inset, inset), (inset, h - inset)], fill=(255, 255, 255), width=2)
    d.rectangle([inset, inset, w - inset, h - inset], outline=(255, 255, 255), width=2)
    text = f"{node}  {w}x{h}"
    d.text((12, 12), text, fill=(255, 255, 255))
    d.text((12, h - 28), label, fill=(255, 255, 255))
    img.save(ASSETS / filename)


def make_all_photos() -> None:
    for i, (filename, (w, h, node, label)) in enumerate(PHOTO_SPECS.items()):
        make_photo(filename, w, h, node, label, seed=i)
    for i, (filename, label) in enumerate(WELFARE_SPECS.items()):
        make_photo(filename, WELFARE_W, WELFARE_H, "", label, seed=i)


def make_line_mark() -> None:
    w, h = _px(LINE_W), _px(LINE_H)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 8
    d.rounded_rectangle([pad, pad, w - pad, h - pad - 12], radius=34,
                        fill=(255, 255, 255, 255))
    # 吹き出しのしっぽ
    d.polygon([(w * 0.36, h - pad - 16), (w * 0.52, h - pad - 16), (w * 0.40, h - 4)],
              fill=(255, 255, 255, 255))
    d.text((w // 2 - 22, h // 2 - 14), "LINE", fill=(6, 199, 85, 255))
    img.save(ASSETS / "line-brand.png")


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    make_logo()
    make_logo_white()
    make_hero()
    make_line_mark()
    make_all_photos()
    for pattern in ("*.png", "*.jpg"):
        for p in sorted(ASSETS.glob(pattern)):
            with Image.open(p) as im:
                print(f"{p.name}: {im.size[0]}x{im.size[1]}")
