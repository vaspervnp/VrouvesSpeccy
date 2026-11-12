#!/usr/bin/env python3
"""The itch.io page's pictures, in real Spectrum pixels and attributes (each
pixel of the Spectrum is 3 x 3 of the picture):

  assets/itch_background.png   1920 x 1152, tiles in both directions: a village
                               of the game's cells and sprites; the page's
                               column covers the middle, so all happens at the sides
  assets/itch_banner.png       960 x 288, the width of the column: the name on
                               black with the Spectrum's stripes, the road below

    make first (build/ not needed, but the tools are), then tools/make_itch.py
"""
import os
import random
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import art  # noqa: E402
import font  # noqa: E402
import zxcolour as zc  # noqa: E402
import zxdata  # noqa: E402
import zxworld as zw  # noqa: E402

SCALE = 3
CS = 16
SPRITES = dict(art.SPRITES + art.EXTRA_SPRITES)
BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE = range(8)


def block(k):
    """a stage's building, as the game shows it: pen rows"""
    pix, _ = zw.render(k, True)
    bc, br, bw, bh = zw.STAGES[k].block
    return [row[bc * CS:(bc + bw) * CS] for row in pix[br * CS:(br + bh) * CS]], bw, bh


class Picture:
    """cols x rows cells of the game's art, as a bitmap and attributes"""

    def __init__(self, grid, blocks, wrap=False):
        cols, rows = len(grid[0]), len(grid)
        self.cols, self.acols, self.arows = cols, cols * 2, rows * 2
        # a road that leaves at the bottom comes back at the top: a row more
        # each way while its cells are drawn, so it has no edge there
        ext = ([grid[-1]] + grid + [grid[0]]) if wrap else grid
        y0 = 1 if wrap else 0
        zw.MW, zw.MH = cols, len(ext)
        cv = zw.cpc_cells(ext)
        pix = [[zc.PEN_OF[cv.p[(r + y0) * 12 + (y % CS) * 3 // 4][c * 8 + (x % CS) // 2]]
                for x in range(cols * CS) for c in [x // CS]]
               for y in range(rows * CS) for r in [y // CS]]
        free = set()
        for (rows_, bw, bh), c0, r0 in blocks:
            for y in range(bh * CS):
                for x in range(bw * CS):
                    pix[r0 * CS + y][c0 * CS + x] = rows_[y][x]
            free |= {(x, y) for y in range(r0 * 2, (r0 + bh) * 2) for x in range(c0 * 2, (c0 + bw) * 2)}
        self.bits, self.attrs = zc.playfield(pix, self.acols, self.arows, 0, 0, free)

    def sprite(self, name, x, y):
        mask, ink = zxdata.sprite_mono(name, SPRITES[name])
        for j, row in enumerate(mask):
            for i, m in enumerate(row):
                if m and 0 <= y + j < len(self.bits) and 0 <= x + i < len(self.bits[0]):
                    self.bits[y + j][x + i] = ink[j][i]

    def figure(self, name, c, r):
        """a defender or an invader in a cell, as the game draws it: black"""
        self.sprite(name, c * CS, r * CS + 2)

    def image(self):
        h, w = len(self.bits), len(self.bits[0])
        im = Image.new("RGB", (w, h))
        px = im.load()
        for y in range(h):
            for x in range(w):
                a = self.attrs[(y // 8) * self.acols + x // 8]
                pal = zc.RGB[a >> 6 & 1]
                px[x, y] = pal[a & 7] if self.bits[y][x] else pal[a >> 3 & 7]
        return im.resize((w * SCALE, h * SCALE), Image.NEAREST)


def save(im, name):
    path = os.path.join(ROOT, "assets", name)
    im.quantize(colors=16, dither=Image.Dither.NONE).save(path, optimize=True)
    print(path, im.size, os.path.getsize(path), "bytes")


# ------------------------------------------------------------------ background
BG_COLS, BG_ROWS = 40, 24
BG_LEFT = [(7, 0), (7, 4), (2, 4), (2, 11), (7, 11), (7, 23)]
BG_PORCH = [(7, 16), (5, 16)]
BG_RIGHT = [(33, 0), (33, 10), (38, 10), (38, 16), (34, 16), (34, 21), (33, 21), (33, 23)]
BG_GATE = [(37, 10), (37, 8)]
BG_DEFENDERS = [
    ("spr_cretan", 5, 2), ("spr_bride", 6, 2), ("spr_baker", 4, 6), ("spr_lyra", 5, 9),
    ("spr_yiayia", 6, 9), ("spr_psssst", 0, 7), ("spr_cauldron", 9, 14), ("spr_cretan", 9, 19),
    ("spr_cretan", 35, 1), ("spr_baker", 31, 6), ("spr_lyra", 36, 12), ("spr_yiayia", 35, 12),
    ("spr_bride", 36, 18), ("spr_cretan", 37, 18), ("spr_cauldron", 31, 18), ("spr_psssst", 36, 21),
]
BG_INVADERS = [
    ("spr_guard_a", 7, 1), ("spr_tank_la", 4, 4), ("spr_guard_b", 2, 8), ("spr_guard_a", 5, 11),
    ("spr_tank_va", 7, 13), ("spr_guard_b", 7, 21),
    ("spr_guard_b", 33, 2), ("spr_tank_va", 33, 7), ("spr_guard_a", 36, 10), ("spr_guard_b", 38, 13),
    ("spr_tank_la", 36, 16), ("spr_guard_a", 34, 19),
    ("spr_drone_a", 4, 0), ("spr_drone_b", 0, 12), ("spr_drone_a", 3, 21), ("spr_drone_b", 9, 7),
    ("spr_drone_a", 31, 13), ("spr_drone_b", 39, 19), ("spr_drone_a", 37, 22), ("spr_drone_b", 30, 2),
]


def background():
    kafenio, church = block(0), block(1)
    grid = [['.'] * BG_COLS for _ in range(BG_ROWS)]
    for (rows_, bw, bh), c0, r0 in ((kafenio, 0, 14), (church, 35, 3)):
        for r in range(r0, r0 + bh):
            for c in range(c0, c0 + bw):
                grid[r][c] = 'K'
    # the country: more of it at the sides, what the column leaves to be seen
    rnd = random.Random(1987)
    for r in range(BG_ROWS):
        for c in range(BG_COLS):
            if grid[r][c] == '.' and rnd.random() < (0.05 if 11 <= c < 29 else 0.24):
                grid[r][c] = rnd.choice("TTTTTTYYYCGSRR")
    for c0, r0, s in ((1, 0, "WWW"), (36, 1, ""), (10, 12, "WW"), (28, 4, "WWW"), (29, 21, "WW")):
        for i, ch in enumerate(s):
            grid[r0][c0 + i] = ch
    grid = ["".join(r) for r in grid]
    zw.MW, zw.MH = BG_COLS, BG_ROWS
    for road in (BG_LEFT, BG_PORCH, BG_RIGHT, BG_GATE):
        grid = zw.carve_path(grid, road)
    # what stands on the grass: no tree under anyone
    people = BG_DEFENDERS + [p for p in BG_INVADERS if 'drone' in p[0]]
    grid = [list(r) for r in grid]
    for _, c, r in people:
        if grid[r][c] != '#':
            grid[r][c] = '.'
    grid = ["".join(r) for r in grid]
    p = Picture(grid, ((kafenio, 0, 14), (church, 35, 3)), wrap=True)
    for name, c, r in BG_DEFENDERS:
        p.figure(name, c, r)
    for name, c, r in BG_INVADERS:
        p.figure(name, c, r)
    for k, c0, r0 in ((0, 0, 14), (1, 35, 3)):
        bc, br, _, _ = zw.STAGES[k].block
        zw.MW, zw.MH = 15, 10
        fx, fy = zw.flag_xy(k)
        p.sprite("spr_flag_a", fx + (c0 - bc) * CS, fy + (r0 - br) * CS)
    save(p.image(), "itch_background.png")


# ------------------------------------------------------------------ banner
BIG = {
    "V": ["##....##"] * 7 + [".##..##."] * 3 + ["..####.."] * 2 + ["...##..."] * 2,
    "R": ["######..", "#######.", "##...###", "##....##", "##....##", "##...###", "#######.",
          "######..", "##..##..", "##..###.", "##...##.", "##...###", "##....##", "##....##"],
    "O": [".######.", "########"] + ["##....##"] * 10 + ["########", ".######."],
    "U": ["##....##"] * 12 + ["########", ".######."],
    "E": ["########", "########"] + ["##......"] * 4 + ["######..", "######.."] +
         ["##......"] * 4 + ["########", "########"],
    "S": [".#######", "########", "##......", "##......", "##......", "#######.", ".#######",
          "......##", "......##", "......##", "......##", "......##", "########", "#######."],
    "!": ["##"] * 10 + ["..", "..", "##", "##"],
}
SMALL = {
    "L": ["##....", "##....", "##....", "##....", "##....", "##....", "##....", "######", "######"],
    "E": ["######", "######", "##....", "##....", "#####.", "##....", "##....", "######", "######"],
    "T": ["######", "######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "'": ["##", "##", ".#", "..", "..", "..", "..", "..", ".."],
    "S": [".#####", "######", "##....", "#####.", ".#####", "....##", "....##", "######", "#####."],
    "G": [".#####", "######", "##....", "##....", "##.###", "##..##", "##..##", "######", ".####."],
    "O": [".####.", "######", "##..##", "##..##", "##..##", "##..##", "##..##", "######", ".####."],
    "F": ["######", "######", "##....", "##....", "#####.", "#####.", "##....", "##....", "##...."],
    "R": ["#####.", "######", "##..##", "##..##", "#####.", "####..", "##.##.", "##..##", "##..##"],
    " ": ["...."] * 9,
}
BAND_ROWS = 8           # attribute rows of black, for the name


def stretch(rows, w, h, stroke=2):
    """a letter larger: the outer rows and columns stay, the inner are repeated"""
    def index(n, old, new):
        if n < stroke:
            return n
        if n >= new - stroke:
            return old - (new - n)
        return stroke + (n - stroke) * (old - 2 * stroke) // (new - 2 * stroke)
    ow, oh = len(rows[0]), len(rows)
    nw = w if ow > 2 else ow
    return ["".join(rows[index(j, oh, h)][index(i, ow, nw)] for i in range(nw)) for j in range(h)]


def fatten(rows):
    """strokes twice as thick across, for the Spectrum's square pixels"""
    return ["".join(ch * 2 for ch in r) for r in rows]


def vee(w, h, stroke):
    """a V with straight sides"""
    rows = []
    for y in range(h):
        x = y * (w - stroke) // (2 * h)
        rows.append("".join('#' if x <= i < x + stroke or w - x - stroke <= i < w - x else '.'
                            for i in range(w)))
    return rows


def letters(p, text, fnt, y0, gap):
    x = (320 - sum(len(fnt[c][0]) + gap for c in text) + gap) // 2
    for ch in text:
        for j, r in enumerate(fnt[ch]):
            for i, c in enumerate(r):
                if c == '#':
                    p.bits[y0 + j][x + i] = 1
        x += len(fnt[ch][0]) + gap


def small_text(p, text, y0):
    x = (320 - 4 * len(text)) // 2
    for k, ch in enumerate(text):
        for j, bits in enumerate(font.glyph_rows(font.glyph_index(ch))):
            for i in range(3):
                if bits & (4 >> i):
                    p.bits[y0 + j][x + 4 * k + i] = 1


def stripes(p, cols, rows):
    """the Spectrum's stripes across the band's corner: each attribute cell has
    at most two of them, so it is exact"""
    colours = (RED, YELLOW, GREEN, CYAN)
    d0 = 320 + 8 * rows - 8 * cols
    for cy in range(rows):
        for cx in range(40 - cols, 40):
            seen = []
            for y in range(cy * 8, cy * 8 + 8):
                for x in range(cx * 8, cx * 8 + 8):
                    s = (x + y - d0) // 8
                    c = colours[s] if 0 <= s < 4 else BLACK
                    if c not in seen:
                        seen.append(c)
            if seen == [BLACK]:         # no stripe here: what the name has stays
                continue
            # a colour as ink, on the other as paper (black paper if it is alone)
            ink = next((c for c in seen if c != BLACK), BLACK)
            paper = next((c for c in seen if c != ink), BLACK)
            for y in range(cy * 8, cy * 8 + 8):
                for x in range(cx * 8, cx * 8 + 8):
                    s = (x + y - d0) // 8
                    c = colours[s] if 0 <= s < 4 else BLACK
                    p.bits[y][x] = 1 if c == ink and ink != paper else 0
            p.attrs[cy * 40 + cx] = 0x40 | (paper << 3) | ink


def banner():
    grid = [
        "T.Y.T..Y...T..Y..T.Y",
        "T..T..Y...Y...T..Y.T",
        "T.Y...T..Y...T...Y.T",
        "T..Y.T...T..Y..T...T",
        "T..........T.......T",
        "....................",
    ]
    zw.MW, zw.MH = 20, 6
    grid = zw.carve_path(grid, [(0, 5), (19, 5)])
    p = Picture(grid, ())
    # the band: black, the name on it, a colour for each row of attributes
    for y in range(BAND_ROWS * 8):
        p.bits[y] = [0] * 320
    row_inks = (CYAN, CYAN, WHITE, YELLOW, YELLOW, RED, RED, WHITE)
    for cy, ink in enumerate(row_inks):
        for cx in range(40):
            p.attrs[cy * 40 + cx] = 0x40 | ink
    letters(p, "LET'S GO FOR", {c: fatten(stretch(r, 6, 11)) for c, r in SMALL.items()}, 2, 3)
    big = {c: fatten(stretch(r, 13, 30, 3)) if c != '!' else
           fatten(stretch(r, 2, 30, 3)) for c, r in BIG.items()}
    big["V"] = vee(26, 30, 5)
    letters(p, "VROUVES!", big, 17, 4)
    small_text(p, "ΠΑΜΕ ΓΙΑ ΒΡΟΥΒΕΣ - ZX SPECTRUM 48K/128K", 56)
    stripes(p, 7, BAND_ROWS)
    # the village's own, along the road
    for name, c in (("spr_cretan", 2), ("spr_bride", 5), ("spr_yiayia", 9), ("spr_lyra", 12),
                    ("spr_baker", 15), ("spr_cauldron", 17)):
        p.figure(name, c, 4)
    for name, c in (("spr_guard_a", 1), ("spr_tank_la", 4), ("spr_guard_b", 7), ("spr_guard_a", 11),
                    ("spr_tank_lb", 14), ("spr_guard_b", 18)):
        p.figure(name, c, 5)
    save(p.image(), "itch_banner.png")


if __name__ == "__main__":
    background()
    banner()
