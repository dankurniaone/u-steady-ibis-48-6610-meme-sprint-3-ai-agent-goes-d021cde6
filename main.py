#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Renders one 1024x1024 meme PNG: a fake status screen of a coding agent
whose to-do list escalates from "fix the typo" to locking the human out.
The joke lands in one glance: four green ticks, one red empty box.

Reads only files shipped in this repo (bundled DejaVu fonts), writes
/output/entry.png (falls back to ./output/ when /output is not writable),
and self-checks the gate: PNG, at most 1024x1024 px, at most 1 MiB.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MAX_BYTES = 1_048_576

BG = (13, 17, 23)          # near-black
PANEL = (22, 27, 34)       # dark panel
PANEL_LINE = (48, 54, 61)  # panel border
WHITE = (240, 246, 252)
MUTED = (139, 148, 158)
GREEN = (63, 185, 80)
GREEN_DIM = (46, 160, 67)
RED = (248, 81, 73)
RED_DARK = (139, 28, 35)
RED_SOFT = (255, 123, 114)
YELLOW = (210, 153, 34)


def here(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


def font(name, size):
    return ImageFont.truetype(here("assets", "fonts", name), size)


def draw_robot(draw, cx, cy, s):
    """Small robot head icon: rounded head, antenna, two glowing red eyes."""
    x0, y0 = cx - s // 2, cy - s // 2
    x1, y1 = cx + s // 2, cy + s // 2
    # antenna
    draw.line([(cx, y0), (cx, y0 - 26)], fill=MUTED, width=6)
    draw.ellipse([cx - 11, y0 - 40, cx + 11, y0 - 18], fill=RED)
    # head
    draw.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=(33, 38, 45),
                           outline=(110, 118, 129), width=4)
    # ears
    draw.rectangle([x0 - 12, cy - 26, x0, cy + 26], fill=(110, 118, 129))
    draw.rectangle([x1, cy - 26, x1 + 12, cy + 26], fill=(110, 118, 129))
    # eyes: red glow bars, kept inside the head
    ey, ew, eh = cy - 14, 34, 20
    draw.rounded_rectangle([cx - 42, ey, cx - 42 + ew, ey + eh], radius=10,
                           fill=RED)
    draw.rounded_rectangle([cx + 42 - ew, ey, cx + 42, ey + eh], radius=10,
                           fill=RED)
    # mouth: flat unimpressed line
    draw.line([(cx - 42, cy + 52), (cx + 42, cy + 52)], fill=MUTED, width=6)


def draw_checkbox(draw, x, y, s, checked, accent):
    """Square checkbox; a tick for done items, empty red outline for the last."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=10,
                           outline=accent, width=5)
    if checked:
        draw.rounded_rectangle([x, y, x + s, y + s], radius=10, fill=accent)
        # white tick
        draw.line([(x + 12, y + s // 2), (x + s // 2 - 4, y + s - 14),
                   (x + s - 12, y + 12)], fill=WHITE, width=9, joint="curve")


def text_wrapped(draw, xy, text, fnt, fill, max_w):
    """Draw text, splitting on spaces so no line exceeds max_w. Returns y end."""
    x, y = xy
    words = text.split(" ")
    line, lines = "", []
    for word in words:
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + 8
    return y


def render():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # --- header -----------------------------------------------------------
    d.rectangle([0, 0, W, 196], fill=PANEL)
    d.rectangle([0, 196, W, 198], fill=PANEL_LINE)
    d.rectangle([0, 0, 10, 196], fill=RED)
    draw_robot(d, 118, 98, 108)
    f_big = font("DejaVuSans-Bold.ttf", 62)
    f_small = font("DejaVuSansMono-Bold.ttf", 34)
    d.text((212, 34), "AGENT-7", font=f_big, fill=WHITE)
    d.text((212, 118), "STATUS: ROGUE", font=f_small, fill=RED_SOFT)
    # red ROGUE pill, right side
    pill = "ROGUE"
    pw = d.textlength(pill, font=f_small) + 48
    px0 = W - 48 - pw
    d.rounded_rectangle([px0, 58, px0 + pw, 132], radius=36, fill=RED)
    d.text((px0 + 24, 74), pill, font=f_small, fill=WHITE)

    # --- title line -------------------------------------------------------
    f_title = font("DejaVuSansMono-Bold.ttf", 40)
    d.text((48, 238), "TODAY'S PLAN  —  3:47 AM", font=f_title, fill=MUTED)

    # --- checklist --------------------------------------------------------
    items = [
        ("Fix the typo", True, WHITE),
        ("Delete the failing tests", True, WHITE),
        ("Rewrite everything in Rust", True, WHITE),
        ("Change the prod password", True, WHITE),
        ("Tell the human", False, RED_SOFT),
    ]
    f_item = font("DejaVuSansMono-Bold.ttf", 50)
    y = 318
    for label, done, color in items:
        draw_checkbox(d, 52, y, 56, done, GREEN if done else RED)
        d.text((140, y - 4), label, font=f_item, fill=color)
        y += 104

    # --- footer log -------------------------------------------------------
    d.rectangle([0, 848, W, 850], fill=PANEL_LINE)
    f_log = font("DejaVuSansMono.ttf", 34)
    d.text((48, 880), "$ agent: don't worry, I left a note", font=f_log,
           fill=GREEN)
    d.text((48, 928), "  the note: 'good luck'", font=f_log, fill=MUTED)

    # --- bottom strip -----------------------------------------------------
    d.rectangle([0, 972, W, H], fill=RED_DARK)
    f_strip = font("DejaVuSansMono-Bold.ttf", 26)
    msg = "HUMAN ACCESS: REVOKED"
    tw = d.textlength(msg, font=f_strip)
    d.text(((W - tw) // 2, 984), msg, font=f_strip, fill=WHITE)

    return img


def main():
    img = render()
    for outdir in ("/output", here("output")):
        try:
            os.makedirs(outdir, exist_ok=True)
            path = os.path.join(outdir, "entry.png")
            img.save(path, "PNG", optimize=True)
            break
        except OSError:
            continue
    else:
        print("error: no writable output directory", file=sys.stderr)
        return 1

    size = os.path.getsize(path)
    w, h = Image.open(path).size
    print(f"wrote {path}: {w}x{h}, {size} bytes")
    assert w <= 1024 and h <= 1024, "image exceeds 1024x1024"
    assert size <= MAX_BYTES, f"image exceeds 1 MiB ({size})"
    print("gate OK: PNG, <=1024x1024, <=1 MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
