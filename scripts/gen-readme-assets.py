#!/usr/bin/env python3
"""Generate the README artwork for dsh-hazchem-check.

Outputs (idempotent overwrite), all inside docs/assets/:

  dsh-hazchem-check-hero-{zh,en}-{light,dark}.webp   1440x576 raster hero
  dsh-hazchem-check-flow-v5-{light,dark}.svg         1100x660 vector diagram

The hero is drawn with Pillow: the left column carries the kicker, name,
two value lines, subtitle, meta and footer; the right column carries this
plugin's own semantic object - one hazardous-chemical register row where the
stored quantity (q), the threshold the register itself states (Q) and the
"major hazard source" verdict are read together.  Row 2 says "no" while
620 t >= 500 t, so the verdict contradicts the register's own numbers; that
is exactly what HZ-003 points at.

The structure diagram is hand-written SVG (one function, two skins).  It is
not a row of five boxes: the material channel and the rule-pack channel are
loaded in parallel and merge into runTableCheck; the report then forks into
issues[] and skipped[].  Inside the engine the eight real rules are laid out
with the check kind and the column each one reads.

Only command, configuration and rule tokens are drawn inside the SVGs, so all
five README languages can share the same pair.

Run:      python scripts/gen-readme-assets.py
Requires: Pillow (hero) and the Windows fonts listed in FONT_FILES.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

W, H = 1440, 576

# --- fonts -----------------------------------------------------------------
FONT_FILES = {
    "reg": r"C:\Windows\Fonts\msyh.ttc",
    "bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "monob": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        sys.exit(f"FATAL: missing font {_kind}: {_path}")


@lru_cache(maxsize=None)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


_MEASURE = Image.new("RGBA", (8, 8))
_MDRAW = ImageDraw.Draw(_MEASURE)


def tw(text: str, kind: str, size: int) -> float:
    """Advance width of `text`, used to keep every line inside its column."""
    return _MDRAW.textlength(text, font=font(kind, size))


# --- palettes --------------------------------------------------------------
LIGHT = dict(
    bg1=(249, 246, 253), bg2=(228, 234, 248),
    ink=(26, 32, 51), sub=(88, 99, 130), faint=(139, 148, 174),
    accent=(75, 103, 180), soft=(228, 233, 247),
    card=(255, 255, 255), border=(215, 221, 239),
    amber=(163, 96, 4), amber_soft=(253, 242, 222), amber_border=(232, 195, 137),
    shadow=(23, 30, 53, 30), glow=(75, 103, 180, 34),
)
DARK = dict(
    bg1=(19, 26, 42), bg2=(12, 16, 22),
    ink=(235, 239, 249), sub=(160, 173, 203), faint=(112, 125, 157),
    accent=(132, 150, 245), soft=(34, 45, 74),
    card=(23, 31, 49), border=(45, 56, 84),
    amber=(232, 180, 90), amber_soft=(48, 39, 18), amber_border=(110, 85, 38),
    shadow=(0, 0, 0, 135), glow=(132, 150, 245, 42),
)

COPY = {
    "zh": dict(
        kicker="DSH · CHECKER · 危险化学品台账核对",
        value1="八条规则核对一份危化品台账的齐备与算术。",
        value2="「否」却超过临界量，第 2 行当场点出来。",
        sub1="只读 JSON / YAML · 八条规则一包带走",
        sub2="issues[] 与 skipped[] 一并交付 · 结论留给审核人",
        meta="HZ-001..HZ-008 · GB 18218—2018 · 只核台账自洽，不判合规",
        foot="Apache-2.0 · npm dsh-hazchem-check · 每条发现附条款摘录与修复提示",
        card_title="危险化学品台账",
        card_meta="rows[] · 4 行",
        cols=("品名", "最大储存量", "临界量", "判定"),
        names=("甲醇", "液氨", "苯", "乙醇"),
        qty=("80 t", "620 t", "430 t", "120 t"),
        limit=("500 t", "500 t", "500 t", "500 t"),
        verdict=("否", "否", "否", "否"),
        status_l="1 条 warn · 0 项未执行",
        status_r="HZ-003",
        cmp_big="620 ≥ 500",
        cmp_mid="→ 判定应为「是」",
        cmp_small="台账写「否」，与自己填的两个数字对不上",
        badge="HZ-003 warn",
    ),
    "en": dict(
        kicker="DSH · CHECKER · HAZARDOUS-CHEMICAL REGISTER",
        value1="Eight rules, one register: completeness and arithmetic.",
        value2="A verdict that beats its own threshold gets flagged.",
        sub1="Read-only JSON / YAML · eight rules in one pack",
        sub2="issues[] + skipped[] together · the verdict stays human",
        meta="HZ-001..HZ-008 · GB 18218—2018 · register self-consistency only",
        foot="Apache-2.0 · npm dsh-hazchem-check · every finding cites a clause",
        card_title="HAZCHEM REGISTER",
        card_meta="rows[] · 4 rows",
        cols=("SUBSTANCE", "STORAGE", "THRESHOLD", "VERDICT"),
        names=("Methanol", "Ammonia", "Benzene", "Ethanol"),
        qty=("80 t", "620 t", "430 t", "120 t"),
        limit=("500 t", "500 t", "500 t", "500 t"),
        verdict=("No", "No", "No", "No"),
        status_l="1 warn · 0 skipped",
        status_r="HZ-003",
        cmp_big="620 ≥ 500",
        cmp_mid="→ should read “Yes”",
        cmp_small="The register says “No”, contradicting its own two numbers",
        badge="HZ-003 warn",
    ),
}

LEFT_X = 56
CARD1 = (916, 104, 1384, 444)
CARD2 = (916, 456, 1384, 540)

LEFT_LIMIT = 856 - LEFT_X


def fit(text: str, kind: str, size: int, limit: float, label: str) -> None:
    """Warn loudly when a line would run out of its column."""
    width = tw(text, kind, size)
    if width > limit:
        print(f"WARN {label}: {width:.0f}px > {limit:.0f}px ({text!r})")



def gradient(w: int, h: int, top, bottom) -> Image.Image:
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return strip.resize((w, h), Image.BILINEAR).convert("RGBA")


def rrect_shadow(size, boxes, colour, blur=18, dy=10):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for box, radius in boxes:
        draw.rounded_rectangle((box[0], box[1] + dy, box[2], box[3] + dy),
                               radius, fill=colour)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def tracked(draw, x, y, text, kind, size, fill, tracking):
    f = font(kind, size)
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += draw.textlength(ch, font=f) + tracking


def draw_hero(skin: str, lang: str) -> Image.Image:
    SKIN = LIGHT if skin == "light" else DARK
    t = COPY[lang]
    img = gradient(W, H, SKIN["bg1"], SKIN["bg2"])

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((700, 20, 1500, 600), fill=SKIN["glow"])
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(80)))

    img.alpha_composite(rrect_shadow((W, H), [(CARD1, 22), (CARD2, 18)],
                                     SKIN["shadow"], 18, 10))

    d = ImageDraw.Draw(img)
    d.rounded_rectangle(CARD1, 22, fill=SKIN["card"], outline=SKIN["border"], width=1)
    d.rounded_rectangle(CARD2, 18, fill=SKIN["card"], outline=SKIN["border"], width=1)

    # ---- left column ------------------------------------------------------
    d.rounded_rectangle((LEFT_X, 72, LEFT_X + 46, 77), 2, fill=SKIN["accent"])
    tracked(d, LEFT_X, 106, t["kicker"], "bold", 21, SKIN["accent"], 2.2)

    d.text((LEFT_X, 214), "dsh-hazchem-check", font=font("bold", 82),
           fill=SKIN["ink"], anchor="ls")
    fit("dsh-hazchem-check", "bold", 82, 880 - LEFT_X, "title")

    value_size = 30 if lang == "zh" else 27
    d.text((LEFT_X, 296), t["value1"], font=font("bold", value_size),
           fill=SKIN["ink"], anchor="ls")
    d.text((LEFT_X, 338), t["value2"], font=font("bold", value_size),
           fill=SKIN["accent"], anchor="ls")
    for key in ("value1", "value2"):
        fit(t[key], "bold", value_size, LEFT_LIMIT, key)

    for i, key in enumerate(("sub1", "sub2")):
        d.text((LEFT_X, 392 + i * 32), t[key], font=font("reg", 25),
               fill=SKIN["sub"], anchor="ls")
        fit(t[key], "reg", 25, LEFT_LIMIT, key)

    d.text((LEFT_X, 468), t["meta"], font=font("reg", 20),
           fill=SKIN["accent"], anchor="ls")
    fit(t["meta"], "reg", 20, LEFT_LIMIT, "meta")
    d.line((LEFT_X, 496, 856, 496), fill=SKIN["border"], width=1)
    d.text((LEFT_X, 536), t["foot"], font=font("reg", 17),
           fill=SKIN["faint"], anchor="ls")
    fit(t["foot"], "reg", 17, LEFT_LIMIT, "foot")
    fit(t["kicker"], "bold", 21, LEFT_LIMIT, "kicker")

    # ---- register card ----------------------------------------------------
    name_x, store_x, limit_x, verdict_r = 940, 1052, 1180, 1360
    head = font("bold", 14)
    d.text((name_x, 142), t["card_title"], font=font("bold", 22),
           fill=SKIN["ink"], anchor="ls")
    d.text((verdict_r, 142), t["card_meta"], font=font("reg", 14),
           fill=SKIN["sub"], anchor="rs")
    d.line((name_x, 160, verdict_r, 160), fill=SKIN["border"], width=1)

    for label, x in ((t["cols"][0], name_x), (t["cols"][1], store_x),
                     (t["cols"][2], limit_x)):
        d.text((x, 188), label, font=head, fill=SKIN["sub"], anchor="ls")
    d.text((verdict_r, 188), t["cols"][3], font=head, fill=SKIN["sub"], anchor="rs")
    for label, x in ((t["cols"][1], store_x), (t["cols"][2], limit_x)):
        d.line((x, 195, x + tw(label, "bold", 14), 195), fill=SKIN["accent"], width=2)
    vw = tw(t["cols"][3], "bold", 14)
    d.line((verdict_r - vw, 195, verdict_r, 195), fill=SKIN["accent"], width=2)

    # row 2 is the one HZ-003 points at: 620 t >= 500 t but the verdict says no
    d.rounded_rectangle((928, 256, 1372, 304), 12,
                        fill=SKIN["amber_soft"], outline=SKIN["amber_border"], width=1)

    for i in range(4):
        base = 234 + 52 * i
        hot = i == 1
        d.text((name_x, base), t["names"][i], font=font("reg", 19),
               fill=SKIN["ink"], anchor="ls")
        d.text((store_x, base), t["qty"][i], font=font("mono", 19),
               fill=SKIN["amber"] if hot else SKIN["ink"], anchor="ls")
        d.text((limit_x, base), t["limit"][i], font=font("mono", 19),
               fill=SKIN["ink"], anchor="ls")
        d.text((verdict_r, base), t["verdict"][i], font=font("bold", 19),
               fill=SKIN["amber"] if hot else SKIN["ink"], anchor="rs")
        if hot:
            vw2 = tw(t["verdict"][i], "bold", 19)
            d.line((verdict_r - vw2, base + 5, verdict_r, base + 5),
                   fill=SKIN["amber"], width=2)

    d.line((name_x, 410, verdict_r, 410), fill=SKIN["border"], width=1)
    d.text((name_x, 432), t["status_l"], font=font("reg", 13),
           fill=SKIN["sub"], anchor="ls")
    d.text((verdict_r, 432), t["status_r"], font=font("mono", 13),
           fill=SKIN["accent"], anchor="rs")

    # ---- comparison strip -------------------------------------------------
    d.text((name_x, 492), t["cmp_big"], font=font("monob", 26),
           fill=SKIN["accent"], anchor="ls")
    d.text((1096, 492), t["cmp_mid"], font=font("bold", 14 if lang == "en" else 15),
           fill=SKIN["ink"], anchor="ls")
    d.rounded_rectangle((1262, 472, 1360, 506), 17,
                        fill=SKIN["soft"], outline=SKIN["accent"], width=1)
    d.text((1311, 495), t["badge"], font=font("mono", 12),
           fill=SKIN["accent"], anchor="mm")
    d.text((name_x, 523), t["cmp_small"], font=font("reg", 12),
           fill=SKIN["sub"], anchor="ls")

    return img


# --- SVG structure diagram -------------------------------------------------
SVG_SKIN = {
    "light": dict(
        bg1="#f9f6fd", bg2="#e4eaf8", ink="#1b2135", sub="#5b6584",
        faint="#8a93ad", accent="#4B67B4", soft="#e8edf9", card="#ffffff",
        border="#d8deef", amber="#a8610a", amber_soft="#fdf3e0",
        shadow="#192034",
    ),
    "dark": dict(
        bg1="#131a2a", bg2="#0c1016", ink="#e9edf9", sub="#a3afcb",
        faint="#76839f", accent="#8496f5", soft="#1e2942", card="#161e30",
        border="#2c3752", amber="#e8b45a", amber_soft="#2c2413",
        shadow="#000000",
    ),
}

RULES = [
    ("HZ-001", "presenceAny", "名称 + 危险性类别"),
    ("HZ-002", "number", "储存量可解析为数值"),
    ("HZ-003", "thresholdCompare", "储存量 × 临界量 × 判定"),
    ("HZ-004", "presence", "临界量是否填写"),
    ("HZ-005", "headerPresence", "表头声明辨识依据"),
    ("HZ-006", "conditionalPresence", "有储存量 → SDS 编号"),
    ("HZ-007", "unique", "CAS 号不重复"),
    ("HZ-008", "containsAny", "品名栏占位符"),
]


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def flow_svg(skin: str) -> str:
    c = SVG_SKIN[skin]
    accent, ink, sub, faint = c["accent"], c["ink"], c["sub"], c["faint"]
    card, border, soft = c["card"], c["border"], c["soft"]

    out: list[str] = []
    add = out.append

    add('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
        'viewBox="0 0 1100 660" role="img" aria-labelledby="flowTitle flowDesc">')
    add('<title id="flowTitle">dsh-hazchem-check structure: dual-channel merge</title>')
    add('<desc id="flowDesc">Material channel (JSON/YAML -&gt; parseTable -&gt; rows[]) and '
        'rule channel (rules/hazchem-check.yaml -&gt; loadRulesetFile -&gt; HZ-001..HZ-008) '
        'merge into runTableCheck; the report forks into issues[] and skipped[]; the verdict stays human.</desc>')
    add('<defs>')
    add(f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c["bg1"]}"/><stop offset="1" stop-color="{c["bg2"]}"/></linearGradient>')
    add(f'<radialGradient id="glow" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0" stop-color="{accent}" stop-opacity="0.13"/>'
        f'<stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>')
    add('<marker id="arrowSub" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
        f'markerHeight="6.5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{sub}"/></marker>')
    add('<marker id="arrowAcc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" '
        f'markerHeight="6.5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{accent}"/></marker>')
    add('</defs>')
    add('<style>.t{font-family:"Microsoft YaHei","Noto Sans CJK SC","Source Han Sans SC",sans-serif}'
        '.m{font-family:Consolas,"Cascadia Mono","SFMono-Regular",monospace}</style>')

    add('<rect width="1100" height="660" fill="url(#bg)"/>')
    add('<ellipse cx="560" cy="300" rx="430" ry="270" fill="url(#glow)"/>')

    # ---- header -----------------------------------------------------------
    add(f'<text class="m" x="40" y="49" font-size="22" font-weight="bold" fill="{ink}">'
        'dsh-hazchem-check</text>')
    add(f'<text class="t" x="40" y="75" font-size="12.5" fill="{sub}">'
        '材料通道 × 规则通道并行装载 → 合流执行 → issues[] 与 skipped[] 分流，结论留给审核人</text>')
    add(f'<rect x="920" y="27" width="140" height="28" rx="14" fill="{card}" stroke="{border}"/>')
    add(f'<text class="m" x="990" y="46" font-size="12" fill="{accent}" text-anchor="middle">'
        'ruleset v2026.1</text>')
    add(f'<text class="m" x="1060" y="76" font-size="11.5" fill="{faint}" text-anchor="end">'
        '8 rules · warn / info cap</text>')
    add(f'<line x1="40" y1="89" x2="1060" y2="89" stroke="{border}" stroke-width="1"/>')

    # ---- lane headings ----------------------------------------------------
    add(f'<text class="t" x="40" y="113" font-size="11.5" font-weight="bold" fill="{accent}" '
        f'letter-spacing="1.4">材料通道</text>')
    add(f'<text class="t" x="104" y="113" font-size="11.5" fill="{sub}">只读原件，一行不改</text>')
    add(f'<text class="t" x="810" y="113" font-size="11.5" font-weight="bold" fill="{accent}" '
        f'letter-spacing="1.4">规则通道</text>')
    add(f'<text class="t" x="874" y="113" font-size="11.5" fill="{sub}">规则包是数据，不是代码</text>')

    lane_a = [
        (128, "file | material", "JSON / YAML · 只读", "内联文本或绝对路径"),
        (236, "parseTable", "列名别名归一", "rows | items | chemicals"),
        (344, "rows[]", "规范化行 · 14 列别名", "名称 · 储存量 · 临界量 · 判定"),
    ]
    lane_b = [
        (128, "rules/hazchem-check.yaml", "规则包随包发放", "换掉规则包即换整套检查"),
        (236, "loadRulesetFile", "加载期守卫", "document · clause · excerpt · source"),
        (344, "HZ-001 .. HZ-008", "八条规则逐行执行", "derived-from-principle ≤ warn"),
    ]

    for x0, cards in ((40, lane_a), (810, lane_b)):
        for y0, title, l2, l3 in cards:
            add(f'<rect x="{x0}" y="{y0}" width="250" height="96" rx="16" fill="{card}" '
                f'stroke="{border}"/>')
            add(f'<rect x="{x0}" y="{y0 + 14}" width="3" height="68" rx="1.5" fill="{accent}" opacity="0.65"/>')
            add(f'<text class="m" x="{x0 + 16}" y="{y0 + 30}" font-size="14" font-weight="bold" '
                f'fill="{accent}">{esc(title)}</text>')
            add(f'<text class="t" x="{x0 + 16}" y="{y0 + 53}" font-size="12" fill="{ink}">{esc(l2)}</text>')
            add(f'<text class="t" x="{x0 + 16}" y="{y0 + 74}" font-size="11.5" fill="{sub}">{esc(l3)}</text>')

    # lane step arrows
    for x in (165, 935):
        add(f'<path d="M{x} 224 V236" stroke="{sub}" stroke-width="1.6" marker-end="url(#arrowSub)"/>')
        add(f'<path d="M{x} 332 V344" stroke="{sub}" stroke-width="1.6" marker-end="url(#arrowSub)"/>')

    # merge arrows (both channels enter the engine)
    add(f'<path d="M290 392 H318" stroke="{accent}" stroke-width="2" marker-end="url(#arrowAcc)"/>')
    add(f'<path d="M810 392 H782" stroke="{accent}" stroke-width="2" marker-end="url(#arrowAcc)"/>')

    # ---- engine -----------------------------------------------------------
    add(f'<rect x="318" y="104" width="464" height="352" rx="20" fill="{soft}" stroke="{accent}" '
        f'stroke-opacity="0.45"/>')
    add(f'<text class="m" x="336" y="133" font-size="15" font-weight="bold" fill="{accent}">runTableCheck</text>')
    add(f'<text class="t" x="452" y="133" font-size="12.5" fill="{ink}">检查引擎 · 逐行 × 逐规则</text>')
    add(f'<text class="m" x="764" y="133" font-size="11" fill="{faint}" text-anchor="end">HZ-003 为核心比对</text>')

    for index, (rule_id, kind, field) in enumerate(RULES):
        col, row = index % 2, index // 2
        x = 336 + col * 222
        y = 148 + row * 68
        hot = rule_id == "HZ-003"
        add(f'<rect x="{x}" y="{y}" width="206" height="58" rx="12" '
            f'fill="{c["amber_soft"] if hot else card}" '
            f'stroke="{c["amber"] if hot else border}"/>')
        add(f'<text class="m" x="{x + 13}" y="{y + 24}" font-size="14" font-weight="bold" '
            f'fill="{c["amber"] if hot else accent}">{rule_id}</text>')
        add(f'<text class="m" x="{x + 193}" y="{y + 24}" font-size="11" fill="{sub}" '
            f'text-anchor="end">{kind}</text>')
        add(f'<text class="t" x="{x + 13}" y="{y + 46}" font-size="13" fill="{ink}">{esc(field)}</text>')

    add(f'<text class="t" x="336" y="437" font-size="11.5" fill="{sub}">'
        '执行不了的规则写入 skipped 并写明原因，不静默通过</text>')

    # ---- report -----------------------------------------------------------
    add(f'<path d="M550 456 V478" stroke="{accent}" stroke-width="2" marker-end="url(#arrowAcc)"/>')
    add(f'<rect x="318" y="478" width="464" height="56" rx="16" fill="{card}" stroke="{border}"/>')
    add(f'<text class="m" x="336" y="501" font-size="14" font-weight="bold" fill="{accent}">makeReport</text>')
    add(f'<text class="m" x="430" y="501" font-size="11.5" fill="{sub}">'
        'summary{error,warn,info} · rulesetVersion</text>')
    add(f'<text class="t" x="336" y="522" font-size="11.5" fill="{ink}">'
        'buildView · markdown + reportJson · 免责声明随行</text>')

    # ---- output fork ------------------------------------------------------
    add(f'<path d="M550 534 V543 H290 V552" fill="none" stroke="{accent}" stroke-width="1.8" '
        f'marker-end="url(#arrowAcc)"/>')
    add(f'<path d="M550 534 V543 H810 V552" fill="none" stroke="{accent}" stroke-width="1.8" '
        f'marker-end="url(#arrowAcc)"/>')

    for x0, label, note, l2, l3 in (
        (40, "issues[]", "哪一行 · 哪一栏 · 差什么", "locator{row, column} · found / expected / basis · fix",
         "每条都带条款摘录与修复提示"),
        (560, "skipped[]", "没执行的检查，逐条写明原因", "rule + reason · 缺列 / 禁用 / 未选都进这里",
         "空 issues 不等于没问题"),
    ):
        add(f'<rect x="{x0}" y="552" width="500" height="74" rx="16" fill="{card}" stroke="{border}"/>')
        add(f'<text class="m" x="{x0 + 20}" y="578" font-size="14" '
            f'font-weight="bold" fill="{accent}">{label}</text>')
        add(f'<text class="t" x="{x0 + 96}" y="578" font-size="13" fill="{ink}">{esc(note)}</text>')
        add(f'<text class="m" x="{x0 + 20}" y="600" font-size="11" fill="{sub}">{esc(l2)}</text>')
        add(f'<text class="t" x="{x0 + 20}" y="619" font-size="11.5" '
            f'fill="{c["amber"] if x0 == 560 else sub}">{esc(l3)}</text>')

    # ---- footer -----------------------------------------------------------
    add(f'<text class="m" x="40" y="648" font-size="11.5" fill="{faint}">'
        'config · rulesFile · disabledRules · onlyRules · skipNotes · timeoutMs</text>')
    add(f'<text class="t" x="1060" y="648" font-size="11.5" fill="{sub}" text-anchor="end">'
        '结论留给审核人 · 措辞守卫 + 免责声明</text>')
    add('</svg>')
    return "\n".join(out) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    written = []
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            image = draw_hero(skin, lang)
            path = os.path.join(OUT, f"dsh-hazchem-check-hero-{lang}-{skin}.webp")
            image.convert("RGB").save(path, "WEBP", quality=92, method=6)
            written.append(path)
        svg = flow_svg(skin)
        path = os.path.join(OUT, f"dsh-hazchem-check-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        written.append(path)
    for path in written:
        print(f"wrote {os.path.relpath(path, ROOT)} ({os.path.getsize(path)} B)")


if __name__ == "__main__":
    main()
