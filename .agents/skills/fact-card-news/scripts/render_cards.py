#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style A [Toss Feed x 14F] Clean News Card Renderer
- Uses NotoSansKR-VF (Black 900 / Bold 700 / Medium 500) with tight negative letter-spacing
- Zero meta fact-check clutter on cards (verification happens silently in the agent background)
- 50%+ negative space, Dark/Light background alternation, Neon highlighter markers, Giant numbers
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
PAD_X = 84


def get_sans(size: int, weight: int = 900):
    f = ImageFont.truetype("C:/Windows/Fonts/NotoSansKR-VF.ttf", size)
    f.set_variation_by_axes([weight])
    return f


def draw_tight_text(draw, x, y, text, font, fill, tracking=-3):
    cur_x = x
    for ch in text:
        draw.text((cur_x, y), ch, font=font, fill=fill)
        adv = draw.textlength(ch, font=font)
        cur_x += adv + tracking
    return cur_x


def measure_tight_text(draw, text, font, tracking=-3):
    total = 0
    for ch in text:
        total += draw.textlength(ch, font=font) + tracking
    return max(0, total - tracking)


def draw_top_and_bottom_chrome(draw, meta, theme, is_dark, slide_no, total_slides, pill_text=None):
    accent = theme["accent"]
    tag_txt = pill_text or meta.get("tag_label", "AI · TECH")
    f_tag = get_sans(26, 900)
    tw = measure_tight_text(draw, tag_txt, f_tag, tracking=0)
    pill_w = tw + 60

    if is_dark:
        draw.rounded_rectangle([PAD_X, 88, PAD_X + pill_w, 142], radius=27, fill=accent)
        draw_tight_text(draw, PAD_X + 30, 95, tag_txt, f_tag, theme["dark_bg"], tracking=0)
        line_col = "#27272A"
        brand_col = accent
        page_col = "#71717A"
    else:
        draw.rounded_rectangle([PAD_X, 88, PAD_X + pill_w, 142], radius=27, fill=theme["dark_bg"])
        draw_tight_text(draw, PAD_X + 30, 95, tag_txt, f_tag, accent, tracking=0)
        line_col = "#D4D4D8"
        brand_col = theme["dark_bg"]
        page_col = theme["dark_bg"]

    draw.line([(PAD_X, H - 130), (W - PAD_X, H - 130)], fill=line_col, width=2)
    brand = meta.get("brand", "__beyondx__")
    draw_tight_text(draw, PAD_X, H - 96, brand, get_sans(26, 900), brand_col, tracking=0)

    arrow = " →" if slide_no < total_slides else ""
    page_str = f"{slide_no:02d} / {total_slides:02d}{arrow}"
    pw = measure_tight_text(draw, page_str, get_sans(26, 700), tracking=0)
    draw_tight_text(draw, W - PAD_X - pw, H - 96, page_str, get_sans(26, 700), page_col, tracking=0)


def render_slide_cover(slide, meta, theme, sno, total):
    """Dark Slide: Giant 3-line hook + Neon highlighter marker + 2-line subcopy."""
    img = Image.new("RGB", (W, H), theme["dark_bg"])
    draw = ImageDraw.Draw(img)
    draw_top_and_bottom_chrome(draw, meta, theme, True, sno, total, slide.get("tag"))

    f_huge = get_sans(90, 900)
    y = 285
    hl_idx = slide.get("highlight_line_index", 1)
    for idx, line in enumerate(slide.get("headline_lines", [])):
        if idx == hl_idx:
            tw = measure_tight_text(draw, line, f_huge, tracking=-4)
            draw.rounded_rectangle([PAD_X - 10, y + 14, PAD_X + tw + 22, y + 114], radius=12, fill=theme["accent"])
            draw_tight_text(draw, PAD_X, y, line, f_huge, theme["dark_bg"], tracking=-4)
        else:
            draw_tight_text(draw, PAD_X, y, line, f_huge, theme["dark_text"], tracking=-4)
        y += 126

    y += 64
    draw.line([(PAD_X, y - 36), (PAD_X + 90, y - 36)], fill=theme["accent"], width=6)

    sub_lines = slide.get("sub_lines", [])
    for idx, sline in enumerate(sub_lines):
        is_last = idx == len(sub_lines) - 1
        f_sub = get_sans(38, 700 if is_last else 500)
        col = "#F4F4F5" if is_last else theme["dark_sub"]
        draw_tight_text(draw, PAD_X, y, sline, f_sub, col, tracking=-2)
        y += 60

    return img


def render_slide_hook(slide, meta, theme, sno, total):
    """Dark Slide: Conversational question/context hook + 1 big quote card."""
    img = Image.new("RGB", (W, H), theme["dark_bg"])
    draw = ImageDraw.Draw(img)
    draw_top_and_bottom_chrome(draw, meta, theme, True, sno, total, slide.get("tag"))

    f_h1 = get_sans(72, 900)
    y = 220
    for line in slide.get("headline_lines", []):
        draw_tight_text(draw, PAD_X, y, line, f_h1, theme["dark_text"], tracking=-3)
        y += 100

    # Quote/Context Card
    y += 45
    draw.rounded_rectangle([PAD_X, y, W - PAD_X, y + 340], radius=32, fill="#141722")
    draw.rectangle([PAD_X, y + 48, PAD_X + 10, y + 292], fill=theme["accent"])

    q_label = slide.get("quote_label", "업계의 흔한 통념")
    draw_tight_text(draw, PAD_X + 52, y + 48, q_label, get_sans(28, 700), theme["accent"], tracking=-1)

    qy = y + 115
    for qline in slide.get("quote_lines", []):
        draw_tight_text(draw, PAD_X + 52, qy, qline, get_sans(44, 700), "#FFFFFF", tracking=-2)
        qy += 68

    # Bottom punchline
    y += 410
    for idx, bline in enumerate(slide.get("bottom_lines", [])):
        is_last = idx == len(slide.get("bottom_lines", [])) - 1
        draw_tight_text(
            draw,
            PAD_X,
            y,
            bline,
            get_sans(42, 900 if is_last else 500),
            theme["accent"] if is_last else theme["dark_sub"],
            tracking=-2,
        )
        y += 62

    return img


def render_slide_big_number(slide, meta, theme, sno, total):
    """Light Slide: Toss-style Giant Big Number + 2-line punchy takeaway."""
    img = Image.new("RGB", (W, H), theme["light_bg"])
    draw = ImageDraw.Draw(img)
    draw_top_and_bottom_chrome(draw, meta, theme, False, sno, total, slide.get("tag"))

    f_h1 = get_sans(68, 900)
    y = 210
    for line in slide.get("headline_lines", []):
        draw_tight_text(draw, PAD_X, y, line, f_h1, theme["light_text"], tracking=-3)
        y += 92

    # Massive Dark Box with Neon Number
    draw.rounded_rectangle([PAD_X, 440, W - PAD_X, 830], radius=36, fill=theme["dark_bg"])
    draw_tight_text(draw, PAD_X + 52, 460, slide.get("big_number", "76%"), get_sans(205, 900), theme["accent"], tracking=-6)
    draw_tight_text(draw, PAD_X + 58, 725, slide.get("number_caption", ""), get_sans(34, 700), "#FFFFFF", tracking=-1)

    y = 910
    b_lines = slide.get("bottom_lines", [])
    for idx, line in enumerate(b_lines):
        is_last = idx == len(b_lines) - 1
        draw_tight_text(
            draw,
            PAD_X,
            y,
            line,
            get_sans(44 if is_last else 40, 900 if is_last else 500),
            theme["light_text"] if is_last else theme["light_sub"],
            tracking=-2,
        )
        y += 64

    return img


def render_slide_contrast(slide, meta, theme, sno, total):
    """Dark Slide: Stark 2-block Before/After or Old/New contrast."""
    img = Image.new("RGB", (W, H), theme["dark_bg"])
    draw = ImageDraw.Draw(img)
    draw_top_and_bottom_chrome(draw, meta, theme, True, sno, total, slide.get("tag"))

    f_h1 = get_sans(68, 900)
    y = 210
    for line in slide.get("headline_lines", []):
        draw_tight_text(draw, PAD_X, y, line, f_h1, theme["dark_text"], tracking=-3)
        y += 92

    # Top Box (Muted/Old)
    y = 435
    top_box = slide.get("top_box", {})
    draw.rounded_rectangle([PAD_X, y, W - PAD_X, y + 300], radius=32, fill="#161924")
    draw_tight_text(draw, PAD_X + 48, y + 42, top_box.get("label", ""), get_sans(30, 700), "#9CA3AF", tracking=-1)
    draw_tight_text(draw, PAD_X + 48, y + 100, top_box.get("value", ""), get_sans(88, 900), "#FFFFFF", tracking=-3)
    draw_tight_text(draw, PAD_X + 48, y + 215, top_box.get("desc", ""), get_sans(32, 500), "#9CA3AF", tracking=-1)

    # Bottom Box (Neon Accent Highlight)
    y = 775
    bot_box = slide.get("bottom_box", {})
    draw.rounded_rectangle([PAD_X, y, W - PAD_X, y + 320], radius=32, fill=theme["accent"])
    draw_tight_text(draw, PAD_X + 48, y + 42, bot_box.get("label", ""), get_sans(30, 900), theme["dark_bg"], tracking=-1)
    draw_tight_text(draw, PAD_X + 48, y + 100, bot_box.get("value", ""), get_sans(96, 900), theme["dark_bg"], tracking=-4)
    draw_tight_text(draw, PAD_X + 48, y + 225, bot_box.get("desc", ""), get_sans(34, 700), theme["dark_bg"], tracking=-1)

    return img


def render_slide_insight(slide, meta, theme, sno, total):
    """Light Slide: High-impact editorial insight with 2 clean points."""
    img = Image.new("RGB", (W, H), theme["light_bg"])
    draw = ImageDraw.Draw(img)
    draw_top_and_bottom_chrome(draw, meta, theme, False, sno, total, slide.get("tag"))

    f_h1 = get_sans(68, 900)
    y = 210
    for line in slide.get("headline_lines", []):
        draw_tight_text(draw, PAD_X, y, line, f_h1, theme["light_text"], tracking=-3)
        y += 92

    y = 450
    for pt in slide.get("points", []):
        draw.rounded_rectangle([PAD_X, y, W - PAD_X, y + 310], radius=32, fill="#FFFFFF")
        # Number pill
        draw.rounded_rectangle([PAD_X + 44, y + 40, PAD_X + 124, y + 92], radius=14, fill=theme["dark_bg"])
        draw_tight_text(draw, PAD_X + 66, y + 45, pt.get("num", "01"), get_sans(28, 900), theme["accent"], tracking=0)

        draw_tight_text(draw, PAD_X + 146, y + 40, pt.get("title", ""), get_sans(42, 900), theme["light_text"], tracking=-2)

        by = y + 128
        for bline in pt.get("lines", []):
            draw_tight_text(draw, PAD_X + 44, by, bline, get_sans(36, 500), theme["light_sub"], tracking=-2)
            by += 56
        y += 345

    return img


def render_slide_outro(slide, meta, theme, sno, total):
    """Dark Slide: Final 1-sentence conclusion + subtle primary source footnote."""
    img = Image.new("RGB", (W, H), theme["dark_bg"])
    draw = ImageDraw.Draw(img)
    draw_top_and_bottom_chrome(draw, meta, theme, True, sno, total, slide.get("tag"))

    f_huge = get_sans(84, 900)
    y = 270
    hl_idx = slide.get("highlight_line_index", 1)
    for idx, line in enumerate(slide.get("headline_lines", [])):
        if idx == hl_idx:
            tw = measure_tight_text(draw, line, f_huge, tracking=-4)
            draw.rounded_rectangle([PAD_X - 10, y + 14, PAD_X + tw + 22, y + 108], radius=12, fill=theme["accent"])
            draw_tight_text(draw, PAD_X, y, line, f_huge, theme["dark_bg"], tracking=-4)
        else:
            draw_tight_text(draw, PAD_X, y, line, f_huge, theme["dark_text"], tracking=-4)
        y += 118

    y += 50
    for sline in slide.get("summary_lines", []):
        draw_tight_text(draw, PAD_X, y, sline, get_sans(38, 500), "#D4D4D8", tracking=-2)
        y += 60

    # Subtle source caption box at bottom
    sy = 960
    draw.rounded_rectangle([PAD_X, sy, W - PAD_X, sy + 185], radius=24, fill="#141722")
    draw_tight_text(draw, PAD_X + 36, sy + 28, "SOURCE & REFERENCE", get_sans(22, 900), theme["accent"], tracking=1)
    cy = sy + 72
    for src_line in slide.get("sources_short", []):
        draw_tight_text(draw, PAD_X + 36, cy, src_line, get_sans(24, 500), "#9CA3AF", tracking=-1)
        cy += 38

    return img


def generate_preview_html(storyboard: dict, theme: dict, out_dir: Path):
    meta = storyboard.get("meta", {})
    slides = storyboard.get("slides", [])
    cards_html = "".join(
        f'<div class="card"><img src="slides/slide_{s.get("slide_no", i+1):02d}.png" alt="Slide {i+1}" /></div>'
        for i, s in enumerate(slides)
    )
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <title>{meta.get("title", "Card News Preview")}</title>
  <style>
    body {{ background: #050608; color: #fff; font-family: sans-serif; padding: 40px 24px; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ font-size: 24px; margin-bottom: 24px; color: {theme["accent"]}; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }}
    .card img {{ width: 100%; border-radius: 14px; display: block; box-shadow: 0 16px 40px rgba(0,0,0,0.6); }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{meta.get("title", "")}</h1>
    <div class="grid">{cards_html}</div>
  </div>
</body>
</html>"""
    p = out_dir / "preview.html"
    p.write_text(html, encoding="utf-8")
    return p


def render_storyboard(storyboard_path: Path):
    script_dir = Path(__file__).resolve().parent
    domains_cfg = json.loads((script_dir.parent / "config" / "domains.json").read_text(encoding="utf-8"))
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))

    meta = storyboard.get("meta", {})
    domain_id = meta.get("domain", "ai-tech")
    theme = domains_cfg["domains"].get(domain_id, domains_cfg["domains"]["ai-tech"])["theme"]

    out_dir = storyboard_path.resolve().parent
    slides_dir = out_dir / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    slides = storyboard.get("slides", [])
    total = len(slides)

    for s in slides:
        sno = s.get("slide_no", 1)
        layout = s.get("layout", "cover")
        if layout == "cover":
            img = render_slide_cover(s, meta, theme, sno, total)
        elif layout == "hook":
            img = render_slide_hook(s, meta, theme, sno, total)
        elif layout == "big_number":
            img = render_slide_big_number(s, meta, theme, sno, total)
        elif layout == "contrast":
            img = render_slide_contrast(s, meta, theme, sno, total)
        elif layout == "insight":
            img = render_slide_insight(s, meta, theme, sno, total)
        else:
            img = render_slide_outro(s, meta, theme, sno, total)

        out_png = slides_dir / f"slide_{sno:02d}.png"
        img.save(out_png, format="PNG", optimize=True)
        print(f"[OK] Rendered Slide {sno:02d} -> {out_png}")

    preview_path = generate_preview_html(storyboard, theme, out_dir)
    print(f"[OK] Generated Preview -> {preview_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_cards.py <path/to/storyboard.json>")
        sys.exit(1)
    render_storyboard(Path(sys.argv[1]))
