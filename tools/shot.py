"""Playwright で 375 / 768 / 1280 のスクリーンショットを撮り、
Figma 実測値との差分を自己確認するスクリプト。

  python3 tools/shot.py

出力: shots/{width}.png と、計測値の一覧を標準出力へ。
"""

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "index.html").as_uri()
SHOTS = ROOT / "shots"

# 実行環境に Chromium が同梱されている場合はそれを使う
# (playwright install を走らせずに済ませるため)。
_PREINSTALLED = Path("/opt/pw-browsers/chromium")
CHROMIUM = os.environ.get("CHROMIUM_PATH") or (
    str(_PREINSTALLED) if _PREINSTALLED.exists() else None
)

WIDTHS = (375, 768, 1280)

# Figma(1280幅)の実測値。1280 のときだけ突き合わせる。
EXPECTED_1280 = {
    "container width": (1040, 0),
    "localnav min-height": (87, 1),
    "localnav pill height": (46, 1),
    "hero label font-size": (24, 0),
    "hero title font-size": (48, 0),
    "hero lead font-size": (21, 0),
    "hero title letter-spacing": (1.92, 0.05),   # 48px x 4%
    "hero label letter-spacing": (0.72, 0.05),   # 24px x 3%
    "hero lead letter-spacing": (0.63, 0.05),    # 21px x 3%
    "navpill font-size": (16, 0),
    "gnav font-size": (13, 0),
    "breadcrumb font-size": (11, 0),
    "header top min-height": (53, 1),
    # -- チャンク1 --
    "section-head title font-size": (24, 0),
    "step title font-size": (24, 0),
    "step label font-size": (16, 0),
    "step body font-size": (14, 0),
    "feature font-size": (12, 0),
    # -- チャンク2 --
    "voice count": (7, 0),
    "voice bubble font-size": (16, 0),
    "voice body font-size": (14, 0),
    "voice media width": (402, 0),
    # -- チャンク3 --
    "stat card count": (6, 0),
    "stat value font-size": (48, 0),
    "job card count": (3, 0),
    "job row count": (11, 0),
    "job tag font-size": (11, 0),
}

MEASURE_JS = """
() => {
  const px = v => parseFloat(v);
  const cs = el => getComputedStyle(el);
  const q = s => document.querySelector(s);

  const pill = q('.localnav__link');
  const localnav = q('.localnav__inner');
  const container = q('.hero__body');

  return {
    'container width': container.getBoundingClientRect().width,
    'localnav min-height': localnav.getBoundingClientRect().height,
    'localnav pill height': pill.getBoundingClientRect().height,
    'hero label font-size': px(cs(q('.hero__label')).fontSize),
    'hero title font-size': px(cs(q('.hero__title')).fontSize),
    'hero lead font-size': px(cs(q('.hero__lead')).fontSize),
    'hero title letter-spacing': px(cs(q('.hero__title')).letterSpacing),
    'hero label letter-spacing': px(cs(q('.hero__label')).letterSpacing),
    'hero lead letter-spacing': px(cs(q('.hero__lead')).letterSpacing),
    'navpill font-size': px(cs(pill).fontSize),
    'gnav font-size': px(cs(q('.gnav__link')).fontSize),
    'breadcrumb font-size': px(cs(q('.breadcrumb__list')).fontSize),
    'header top min-height': q('.header-top').getBoundingClientRect().height,
    'section-head title font-size': px(cs(q('.section-head__title')).fontSize),
    'step title font-size': px(cs(q('.step__title')).fontSize),
    'step label font-size': px(cs(q('.step__label')).fontSize),
    'step body font-size': px(cs(q('.step__body')).fontSize),
    'feature font-size': px(cs(q('.feature p')).fontSize),
    'voice count': document.querySelectorAll('.voice').length,
    'voice bubble font-size': px(cs(q('.voice__bubble')).fontSize),
    'voice body font-size': px(cs(q('.voice__body')).fontSize),
    'voice media width': q('.voice__media').getBoundingClientRect().width,
    'stat card count': document.querySelectorAll('.stat-card').length,
    'stat value font-size': px(cs(q('.stat-card__value')).fontSize),
    'job card count': document.querySelectorAll('.job-card').length,
    'job row count': document.querySelectorAll('.job-row').length,
    'job tag font-size': px(cs(q('.job-row .job-tag')).fontSize),
    '_font': cs(document.body).fontFamily,
    '_fontLoaded': document.fonts.check('700 48px "Noto Sans JP"'),
    '_docScrollW': document.documentElement.scrollWidth,
    '_clientW': document.documentElement.clientWidth,
  };
}
"""


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    failures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--font-render-hinting=none"],
        )
        for width in WIDTHS:
            page = browser.new_page(viewport={"width": width, "height": 900},
                                    device_scale_factor=2)
            page.goto(PAGE, wait_until="networkidle")
            page.wait_for_timeout(400)

            out = SHOTS / f"{width}.png"
            page.screenshot(path=str(out), full_page=True)

            m = page.evaluate(MEASURE_JS)
            print(f"\n=== {width}px -> {out.name} ===")
            print(f"  font-family : {m['_font']}")
            print(f"  Noto loaded : {m['_fontLoaded']}")

            # 横スクロール(はみ出し)は全幅で許さない
            if m["_docScrollW"] > m["_clientW"]:
                failures.append(
                    f"{width}px: 横スクロール発生 "
                    f"(scrollW={m['_docScrollW']} > clientW={m['_clientW']})"
                )
                print(f"  ! 横はみ出し {m['_docScrollW']} > {m['_clientW']}")
            else:
                print("  overflow-x  : none")

            if width == 1280:
                print("  -- Figma 突き合わせ --")
                for key, (want, tol) in EXPECTED_1280.items():
                    got = m[key]
                    ok = abs(got - want) <= tol
                    print(f"  [{'OK' if ok else 'NG'}] {key:<28} "
                          f"want={want} got={round(got, 2)}")
                    if not ok:
                        failures.append(f"1280px: {key} want={want} got={round(got, 2)}")

            page.close()

        # ドロワー開状態も 1 枚撮っておく
        page = browser.new_page(viewport={"width": 375, "height": 900},
                                device_scale_factor=2)
        page.goto(PAGE, wait_until="networkidle")
        page.click(".nav-toggle")
        page.wait_for_timeout(250)
        page.screenshot(path=str(SHOTS / "375-menu-open.png"), full_page=True)
        expanded = page.get_attribute(".nav-toggle", "aria-expanded")
        drawer_visible = page.is_visible("#global-drawer")
        print(f"\n=== 375px drawer ===\n  aria-expanded={expanded} "
              f"drawer visible={drawer_visible}")
        if expanded != "true" or not drawer_visible:
            failures.append("375px: ドロワーが開かない")
        page.close()

        browser.close()

    print("\n" + "=" * 46)
    if failures:
        print(f"FAIL ({len(failures)})")
        for f in failures:
            print("  - " + f)
        return 1
    print("PASS - 全チェック通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
