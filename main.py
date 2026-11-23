#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Renders one 1024x1024 meme PNG: a fake status screen of a coding agent
whose to-do list escalates from "fix the typo" to locking the human out.
The joke lands in one glance: four green ticks, one red empty box.

Standard library only — no Pillow, no network, no font files at runtime.
Text is drawn from glyph bitmaps pre-rasterized from the bundled DejaVu
fonts (see assets/lines.json, generated locally before the release); the
PNG itself is encoded by hand with zlib. Reads only files shipped in this
repo, writes /output/entry.png (falls back to ./output/ when /output is
not writable), and self-checks the gate: PNG, at most 1024x1024 px, at
most 1 MiB.
"""

import base64
import binascii
import json
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024
MAX_BYTES = 1_048_576

BG = (13, 17, 23)          # near-black
PANEL = (22, 27, 34)       # dark panel
PANEL_LINE = (48, 54, 61)  # panel border
HEAD = (33, 38, 45)        # robot head
STEEL = (110, 118, 129)    # robot outline / ears
WHITE = (240, 246, 252)
MUTED = (139, 148, 158)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
RED_DARK = (139, 28, 35)
RED_SOFT = (255, 123, 114)


def here(*parts):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)


class Canvas:
    """An RGB pixel buffer with the few primitives the meme needs."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def blend(self, x, y, color, alpha):
        """Blend one pixel: alpha 0 keeps the background, 255 is solid."""
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            a = alpha
            self.buf[o] = (color[0] * a + self.buf[o] * (255 - a)) // 255
            self.buf[o + 1] = (color[1] * a + self.buf[o + 1] * (255 - a)) // 255
            self.buf[o + 2] = (color[2] * a + self.buf[o + 2] * (255 - a)) // 255

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(x0, 0)
        y0 = max(y0, 0)
        x1 = min(x1, self.w - 1)
        y1 = min(y1, self.h - 1)
        row = bytes(color) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            o = self._off(x0, y)
            self.buf[o:o + len(row)] = row

    def fill_rounded_rect(self, x0, y0, x1, y1, radius, color):
        r = radius
        for y in range(y0, y1 + 1):
            if y < y0 + r:
                dy = (y0 + r - 1) - y
                dx = math.isqrt(r * r - dy * dy)
                xa, xb = x0 + r - dx, x1 - r + dx
            elif y > y1 - r:
                dy = y - (y1 - r + 1)
                dx = math.isqrt(r * r - dy * dy)
                xa, xb = x0 + r - dx, x1 - r + dx
            else:
                xa, xb = x0, x1
            self.fill_rect(xa, y, xb, y, color)

    def outline_rounded_rect(self, x0, y0, x1, y1, radius, color, width, bg):
        self.fill_rounded_rect(x0, y0, x1, y1, radius, color)
        self.fill_rounded_rect(x0 + width, y0 + width, x1 - width,
                               y1 - width, max(radius - width, 0), bg)

    def fill_ellipse(self, x0, y0, x1, y1, color):
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        rx = (x1 - x0) / 2
        ry = (y1 - y0) / 2
        for y in range(y0, y1 + 1):
            dy = (y - cy) / ry
            if abs(dy) > 1:
                continue
            dx = int(rx * math.sqrt(1 - dy * dy))
            self.fill_rect(int(cx - dx), y, int(cx + dx), y, color)

    def thick_line(self, x0, y0, x1, y1, width, color):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        half = width // 2
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            self.fill_rect(x - half, y - half, x + half, y + half, color)


def load_lines():
    """Decode assets/lines.json into {key: (w, h, ox, oy, advance, pixels)}."""
    with open(here("assets", "lines.json")) as f:
        raw = json.load(f)
    lines = {}
    for key, item in raw.items():
        pixels = zlib.decompress(base64.b64decode(item["data"]))
        lines[key] = (item["w"], item["h"], item["ox"], item["oy"],
                      item["advance"], pixels)
    return lines


def draw_text(canvas, line, x, y, color):
    w, h, ox, oy, _advance, pixels = line
    for row in range(h):
        base = row * w
        for col in range(w):
            a = pixels[base + col]
            if a:
                canvas.blend(x + ox + col, y + oy + row, color, a)


def draw_robot(canvas, cx, cy, s):
    """Small robot head icon: rounded head, antenna, two glowing red eyes."""
    x0, y0 = cx - s // 2, cy - s // 2
    x1, y1 = cx + s // 2, cy + s // 2
    # antenna
    canvas.thick_line(cx, y0, cx, y0 - 26, 6, MUTED)
    canvas.fill_ellipse(cx - 11, y0 - 40, cx + 11, y0 - 18, RED)
    # head
    canvas.outline_rounded_rect(x0, y0, x1, y1, 26, STEEL, 4, HEAD)
    # ears
    canvas.fill_rect(x0 - 12, cy - 26, x0, cy + 26, STEEL)
    canvas.fill_rect(x1, cy - 26, x1 + 12, cy + 26, STEEL)
    # eyes: red glow bars, kept inside the head
    ey, ew, eh = cy - 14, 34, 20
    canvas.fill_rounded_rect(cx - 42, ey, cx - 42 + ew, ey + eh, 10, RED)
    canvas.fill_rounded_rect(cx + 42 - ew, ey, cx + 42, ey + eh, 10, RED)
    # mouth: flat unimpressed line
    canvas.thick_line(cx - 42, cy + 52, cx + 42, cy + 52, 6, MUTED)


def draw_checkbox(canvas, x, y, s, checked, accent):
    """Square checkbox; a tick for done items, empty red outline for the last."""
    if checked:
        canvas.fill_rounded_rect(x, y, x + s, y + s, 10, accent)
        # white tick (rounded joint where the two strokes meet)
        bx, by = x + s // 2 - 4, y + s - 14
        canvas.thick_line(x + 12, y + s // 2, bx, by, 9, WHITE)
        canvas.thick_line(bx, by, x + s - 12, y + 12, 9, WHITE)
        canvas.fill_ellipse(bx - 5, by - 5, bx + 5, by + 5, WHITE)
    else:
        canvas.outline_rounded_rect(x, y, x + s, y + s, 10, accent, 5, BG)


def render(lines):
    img = Canvas(W, H, BG)

    # --- header -----------------------------------------------------------
    img.fill_rect(0, 0, W - 1, 195, PANEL)
    img.fill_rect(0, 196, W - 1, 197, PANEL_LINE)
    img.fill_rect(0, 0, 9, 195, RED)
    draw_robot(img, 118, 98, 108)
    draw_text(img, lines["agent7"], 212, 34, WHITE)
    draw_text(img, lines["status"], 212, 118, RED_SOFT)
    # red ROGUE pill, right side
    pw = int(lines["rogue"][4] + 48)
    px0 = W - 48 - pw
    img.fill_rounded_rect(px0, 58, px0 + pw, 132, 36, RED)
    draw_text(img, lines["rogue"], px0 + 24, 74, WHITE)

    # --- title line -------------------------------------------------------
    draw_text(img, lines["title"], 48, 238, MUTED)

    # --- checklist --------------------------------------------------------
    items = [
        ("item0", True, WHITE),
        ("item1", True, WHITE),
        ("item2", True, WHITE),
        ("item3", True, WHITE),
        ("item4", False, RED_SOFT),
    ]
    y = 318
    for key, done, color in items:
        draw_checkbox(img, 52, y, 56, done, GREEN if done else RED)
        draw_text(img, lines[key], 140, y - 4, color)
        y += 104

    # --- footer log -------------------------------------------------------
    img.fill_rect(0, 848, W - 1, 849, PANEL_LINE)
    draw_text(img, lines["foot0"], 48, 880, GREEN)
    draw_text(img, lines["foot1"], 48, 928, MUTED)

    # --- bottom strip -----------------------------------------------------
    img.fill_rect(0, 972, W - 1, H - 1, RED_DARK)
    tw = lines["strip"][4]
    draw_text(img, lines["strip"], int((W - tw) // 2), 984, WHITE)

    return img


def png_bytes(canvas):
    """Encode the canvas as a PNG (color type 2, 8-bit) with stdlib only."""

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", binascii.crc32(typ + data) & 0xffffffff))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main():
    lines = load_lines()
    img = render(lines)
    data = png_bytes(img)
    for outdir in ("/output", here("output")):
        try:
            os.makedirs(outdir, exist_ok=True)
            path = os.path.join(outdir, "entry.png")
            with open(path, "wb") as f:
                f.write(data)
            break
        except OSError:
            continue
    else:
        print("error: no writable output directory", file=sys.stderr)
        return 1

    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(33)
    w, h = struct.unpack(">II", head[16:24])
    print(f"wrote {path}: {w}x{h}, {size} bytes")
    assert w <= 1024 and h <= 1024, "image exceeds 1024x1024"
    assert size <= MAX_BYTES, f"image exceeds 1 MiB ({size})"
    print("gate OK: PNG, <=1024x1024, <=1 MiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
