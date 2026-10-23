"""The world of LET'S GO FOR VROUVES, shared with the Amstrad CPC version:
the stage maps and their renderers (in the CPC's 16 pens, art.py), the enemy
paths, the waves, the music's notes, the sound effects and the first title
page's scene.  Taken from the CPC's tools/gen_assets.py; tools/mkdata64.py
turns it into the C64's data.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import art  # noqa: E402
import font  # noqa: E402

MW, MH = 20, 14          # map size in cells
TW, TH = 8, 12           # cell size: 8 pixels x 12 lines
PFW, PFH = MW * TW, MH * TH

# ------------------------------------------------------------------ maps
# '.' grass, '#' path (carved from the waypoints), T tree, C cactus, G goat,
# Y cypress, W wall, K/P the defended building and its yard (cell type 3)

MAP1 = [
    "T.G..T...T..T.C...TT",
    "T..................T",
    "..........WWWWWW..T.",
    "T...C..........W...T",
    ".G.................T",
    "T...WWWWWW..........",
    "..T........C...TG..T",
    "T..................T",
    "KKKKK.......WWWWWW.T",
    "KKKKK..T...........T",
    "KKKKK...............",
    "KKKKK..WWWW....G...T",
    "PPPPP..............T",
    "PPPPPPT..T.CT..T.G.T",
]
GROUND1 = [(17, 0), (17, 1), (2, 1), (2, 4), (15, 4), (15, 7), (8, 7),
           (8, 10), (17, 10), (17, 12), (5, 12)]
AIR1 = [(17, 0), (12, 5), (12, 8), (8, 12), (5, 12)]
SACKS1 = [(3, 12), (4, 12), (3, 13), (4, 13), (5, 13)]

MAP2 = [
    "T..T..C..T...Y.KKKKK",
    "...............KKKKK",
    "T..............KKKKK",
    "Y..........Y...KKKKK",
    ".....WWWW..T...PPPPP",
    "T.G............PPPPP",
    "Y...........C...Y..T",
    "T........G....WWW..T",
    "T...T..............T",
    "....G........WWWW...",
    "T.......T..........T",
    "T..C........T......T",
    "..T...G...........Y.",
    "T.T..T..Y..T..T..C.T",
]
GROUND2 = [(1, 13), (1, 10), (7, 10), (7, 7), (1, 7), (1, 2), (10, 2), (10, 12),
           (17, 12), (17, 6)]
AIR2 = [(1, 13), (8, 6), (17, 6)]
SACKS2 = [(15, 4), (16, 4), (18, 4), (19, 4), (15, 5)]

MAP3 = [
    "T..T...C...T....T..T",
    "..G.........Y.....T.",
    "..................TT",
    "T...WWWWW....C......",
    "..T.......Y.......T.",
    "T.................YT",
    "T....T.....WWWW....T",
    "....C.....G......T..",
    "T...........Y....T.T",
    "Y.......T...PPPPPPPP",
    "T...G.......PPKKKKKK",
    "T.......Y...PPKKKKKK",
    "..T..C......PPKKKKKK",
    "T.T..T..Y..TPPKKKKKK",
]
GROUND3 = [(0, 2), (17, 2), (17, 5), (2, 5), (2, 11), (6, 11), (6, 8), (10, 8), (10, 12),
           (11, 12)]
AIR3 = [(0, 2), (10, 12), (11, 12)]
SACKS3 = [(12, 10), (13, 10), (13, 11), (12, 13), (13, 13)]

MAP4 = [
    "KKKKKP..T...C...T..T",
    "KKKKKP.......Y.....T",
    "KKKKKP.........WWW.T",
    "KKKKKP.....T........",
    "PPPPPP....WWWW...T.T",
    "..T..........C.....T",
    "T...G..............Y",
    "Y.....T....Y......T.",
    "T..WWWW.......G....T",
    "...................T",
    "T...T.....C.....T...",
    "Y......G......WWWW.T",
    "....................",
    "T.T..Y..T..T.C..T.YT",
]
GROUND4 = [(19, 12), (2, 12), (2, 9), (17, 9), (17, 6), (8, 6), (8, 2), (6, 2)]
AIR4 = [(19, 12), (16, 12), (6, 2)]
SACKS4 = [(5, 1), (5, 3), (1, 4), (3, 4), (5, 4)]

MAP5 = [
    "T..T..TKKKKKK..T...T",
    "..C....KKKKKK.....Y.",
    "Y......KKKKKK..Y...T",
    "T.....PPPPPPPP.....T",
    "..T...PPPPPPPP...Y.T",
    "T..WWW....C.........",
    "T.................TY",
    "....G.....T.....C..T",
    "T..WWWW.......WWW..T",
    "Y..................T",
    "T...C.....T.........",
    "..T....G.....WWWW..T",
    "..................YT",
    "T.T..Y..T..T.C..T..T",
]
GROUND5 = [(0, 12), (17, 12), (17, 9), (2, 9), (2, 6), (16, 6), (16, 3), (14, 3)]
AIR5 = [(0, 12), (5, 12), (14, 3)]
SACKS5 = [(6, 4), (8, 4), (10, 4), (12, 4), (13, 4)]

# 'F' is the football pitch: buildable grass, painted by the stage
MAP6 = [
    "T..T....T......T..T.",
    "..C..Y.............T",
    "T.....G...........T.",
    "T...........C.....YT",
    "T....FFFFFFFFFF....T",
    "Y....FFFFFFFFFF...T.",
    "T....FFFFFFFFFF....Y",
    "...G.FFFFFFFFFF...T.",
    "T....FFFFFFFFFF....T",
    "Y....FFFFFFFFFF...Y.",
    "T....FFFFFFFFFF....T",
    "T....PPPPPPPPPP.C..T",
    "..T..KKKKKKKKKK.....",
    "T.T..KKKKKKKKKK.T.YT",
]
GROUND6 = [(19, 12), (17, 12), (17, 1), (10, 1), (10, 3), (2, 3), (2, 11), (4, 11)]
AIR6 = [(19, 12), (12, 5), (6, 5), (4, 7), (4, 11)]
SACKS6 = [(6, 11), (9, 11), (11, 11), (13, 11), (14, 11)]

# 'X' is a grave
MAP7 = [
    "T..Y...T....Y...T..T",
    "..................YT",
    "T.....C......Y.....T",
    "Y.................YT",
    "T.X.X.X.X.X.X...Y..T",
    "Y...........XXPKKKKK",
    "T.X.X.X.X...XXPKKKKK",
    "Y...........XXPKKKKK",
    "T.X.X.X.X...XXPKKKKK",
    "Y.X.X.X.X.....PPPPPP",
    "T.X...X.....X......T",
    "Y.X.X.X.X........Y.T",
    "T...X...X...X...X..T",
    "Y..T..Y..T..Y..T..YT",
]
GROUND7 = [(0, 1), (17, 1), (17, 3), (2, 3), (2, 7), (10, 7), (10, 11), (16, 11), (16, 10)]
AIR7 = [(0, 1), (6, 1), (6, 2), (14, 10), (16, 10)]
SACKS7 = [(14, 5), (14, 6), (14, 8), (18, 9), (19, 9)]


def carve_path(grid, wps):
    grid = [r.ljust(MW, '.')[:MW] for r in grid]
    cells = set()
    for (a, b) in zip(wps, wps[1:]):
        (c0, r0), (c1, r1) = a, b
        dc = (c1 > c0) - (c1 < c0)
        dr = (r1 > r0) - (r1 < r0)
        c, r = c0, r0
        cells.add((c, r))
        while (c, r) != (c1, r1):
            c += dc
            r += dr
            cells.add((c, r))
    for (c, r) in cells:
        row = list(grid[r])
        row[c] = '#'
        grid[r] = "".join(row)
    return grid


def path_steps(wps):
    pts = []
    for (a, b) in zip(wps, wps[1:]):
        (c0, r0), (c1, r1) = a, b
        n = 12 * max(abs(c1 - c0), abs(r1 - r0))
        for k in range(n):
            c = c0 + (c1 - c0) * k / n
            r = r0 + (r1 - r0) * k / n
            pts.append((int(round(c * 4)), int(round(r * 12))))
    c, r = wps[-1]
    pts.append((c * 4, r * 12))
    while pts[0][1] < 2:
        pts.pop(0)
    return pts


# ------------------------------------------------------------------ background renderer

class Canvas:
    def __init__(self, w, h, fill):
        self.w, self.h = w, h
        self.p = [[fill] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def get(self, x, y):
        return self.p[y][x]

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def blit(self, rows, x0, y0):
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != '.':
                    self.set(x0 + i, y0 + j, art.CH[ch])

    def text(self, s, x0, y0, c):
        for k, ch in enumerate(s):
            g = font.glyph_rows(font.glyph_index(ch))
            for j, bits in enumerate(g):
                for i in range(3):
                    if bits & (4 >> i):
                        self.set(x0 + k * 4 + i, y0 + j, c)


TREE = [
    "..tttt..",
    ".tpptttk"[:8],
    "tppttttt",
    "tpttpttt",
    "tttttttk",
    "ttpttttk",
    "tttttptk",
    "tttttttk",
    ".ttttttk",
    "..ttttk.",
    "...kkk..",
    "........",
]
TREE = [r.ljust(8, '.')[:8] for r in TREE]
TREE2 = [
    "...tt...",
    ".ttpttt.",
    "tppttttk",
    "tpttttpk",
    "ttttpttk",
    ".tttttk.",
    "..tktk..",
    ".ttpttt.",
    "tpttttpk",
    "tttptttk",
    ".ttttkk.",
    "..kkk...",
]
CACTUS = [
    "...y....",
    "..ppt...",
    ".pppptR.",
    ".ppppt..",
    "..ppt.y.",
    "y.tt.ppt",
    "pt.t.pppt"[:8],
    "pppttppt",
    "pppt.tt.",
    ".ptt.t..",
    "..ttt...",
    "........",
]
GOAT_W = [
    "........",
    "..r..r..",
    "...ee...",
    "...WW...",
    "..WWWW..",
    ".WWWWWW.",
    ".WWeWWW.",
    ".WWWWWW.",
    ".WWWWWW.",
    "..WWWW..",
    "..W..W..",
    "...e....",
]
GOAT_B = [
    "........",
    "..e..e..",
    "...rr...",
    "...oo...",
    "..oooo..",
    ".ooWooo.",
    ".oooooo.",
    ".oorooo.",
    ".oooooo.",
    "..oooo..",
    "..o..o..",
    "....r...",
]
CYPRESS = [
    "...t....",
    "...tk...",
    "..ttt...",
    "..tptk..",
    "..tttk..",
    ".ttpttk.",
    ".tpttk..",
    ".ttttk..",
    ".tptttk.",
    "..tttk..",
    "...kr...",
    "........",
]
PRIEST = [
    "..kkk..",
    ".kkkkk.",
    ".kkkkk.",
    "..sss..",
    "..eee..",
    ".keeek.",
    "kkkekkk",
    "kkkykkk",
    "kkyyykk",
    "kkkykkk",
    ".kkkkk.",
    ".kk.kk.",
]
MAYOR = [
    "..eee..",
    ".eeeee.",
    "..sss..",
    "..sss..",
    ".kkWkk.",
    "kkkRkkk",
    "kkkRkkk",
    "kkkkkkk",
    ".kkkkk.",
    ".kk.kk.",
    ".rr.rr.",
]
TEACHER = [
    "..rrr..",
    ".rrrrr.",
    ".rsssr.",
    "..kWk..",
    "..sss..",
    ".BBBBB.",
    "sBBBBBs",
    ".BBBBB.",
    ".BBBBB.",
    "..s.s..",
    "..k.k..",
]
COACH = [
    "..kkk..",
    "..sss..",
    "..sss..",
    ".RRWRR.",
    "sRRRRRs",
    ".RRRRR.",
    ".BBBBB.",
    ".BB.BB.",
    ".BB.BB.",
    ".WW.WW.",
]
GRAVE_A = [
    "........",
    "..kkkk..",
    ".kWWWek.",
    ".kWkWek.",
    ".kkkkek.",
    ".kWkWek.",
    ".kkkkkk.",
    ".keeeek.",
    ".keReyk.",
    ".kyeeRk.",
    ".kkkkkk.",
    "........",
]
GRAVE_B = [
    "...kk...",
    "..kWek..",
    ".kkWekk.",
    ".kWWeek.",
    ".kkWekk.",
    "..kWek..",
    "..kWek..",
    ".kkeekk.",
    ".keRyek.",
    ".keeeek.",
    ".kkkkkk.",
    "........",
]
YIAYIA_BLACK = [
    "..kkk..",
    ".kkkkk.",
    ".kssk..",
    ".kkkkk.",
    "kkkkkkk",
    "skkkkks",
    ".kkkkk.",
    ".kkkkk.",
    ".kkkkk.",
    "..k.k..",
]
TABLE = [
    ".rrr.",
    "rorWr",
    "rrorr",
    ".rrr.",
]
SACK = [
    ".lp.",
    "rpl.",
    ".rr.",
    "oooo",
    "oroo",
    "oooo",
    "oooo",
    "rooo",
    ".rr.",
]
SACK = [r.ljust(4, '.') for r in SACK]


def grass_cell(cv, c, r, v=None):
    x0, y0 = c * TW, r * TH
    cv.rect(x0, y0, x0 + TW - 1, y0 + TH - 1, art.CH['g'])
    if v is None:
        v = (c * 7 + r * 13 + (c * r) % 3) % 5

    def tuft(x, y):
        cv.set(x0 + x, y0 + y, art.CH['t'])
        cv.set(x0 + x + 2, y0 + y, art.CH['t'])
        cv.set(x0 + x + 1, y0 + y + 1, art.CH['t'])

    if v == 0:
        tuft(1, 2); tuft(4, 8)
    elif v == 1:
        tuft(4, 3); cv.set(x0 + 1, y0 + 9, art.CH['y'])
    elif v == 2:
        tuft(1, 6); tuft(5, 1)
    elif v == 3:
        cv.set(x0 + 5, y0 + 6, art.CH['t']); cv.set(x0 + 2, y0 + 10, art.CH['p'])
    else:
        cv.set(x0 + 5, y0 + 4, art.CH['W']); tuft(1, 9)


def is_path(grid, c, r):
    return 0 <= c < MW and 0 <= r < MH and grid[r][c] == '#'


def path_cell(cv, grid, c, r):
    x0, y0 = c * TW, r * TH
    cv.rect(x0, y0, x0 + TW - 1, y0 + TH - 1, art.CH['o'])
    for (x, y) in ((2, 3), (6, 7), (3, 10), (5, 1)):
        cv.set(x0 + x, y0 + y, art.CH['r'])
    for (x, y) in ((1, 7), (6, 2)):
        cv.set(x0 + x, y0 + y, art.CH['y'])
    edge = art.CH['r']
    if not is_path(grid, c, r - 1) and r > 0:
        for x in range(TW):
            cv.set(x0 + x, y0, edge)
    if not is_path(grid, c, r + 1) and r < MH - 1:
        for x in range(TW):
            cv.set(x0 + x, y0 + TH - 1, edge)
    if not is_path(grid, c - 1, r) and c > 0:
        for y in range(TH):
            cv.set(x0, y0 + y, edge)
    if not is_path(grid, c + 1, r) and c < MW - 1:
        for y in range(TH):
            cv.set(x0 + TW - 1, y0 + y, edge)


def wall_cell(cv, grid, c, r):
    grass_cell(cv, c, r, 3)
    x0, y0 = c * TW, r * TH

    def w(cc, rr):
        return 0 <= cc < MW and 0 <= rr < MH and grid[rr][cc] == 'W'
    horiz = w(c - 1, r) or w(c + 1, r)
    vert = w(c, r - 1) or w(c, r + 1)
    if not horiz and not vert:
        horiz = True
    K, E, Wh, T = art.CH['k'], art.CH['e'], art.CH['W'], art.CH['t']
    if horiz:
        xa = 0 if w(c - 1, r) else 1
        xb = TW - 1 if w(c + 1, r) else TW - 2
        for x in range(xa, xb + 1):
            for y in range(3, 9):
                cv.set(x0 + x, y0 + y, E)
            cv.set(x0 + x, y0 + 3, K)
            cv.set(x0 + x, y0 + 8, K)
            cv.set(x0 + x, y0 + 9, T)
            cv.set(x0 + x, y0 + 6, K if (x % 4) in (1, 2) and False else E)
        for x in range(xa, xb + 1):
            if (x + 1) % 4 == 0:
                for y in (4, 5):
                    cv.set(x0 + x, y0 + y, K)
            if (x + 3) % 4 == 0:
                for y in (6, 7):
                    cv.set(x0 + x, y0 + y, K)
            if x % 4 == 0:
                cv.set(x0 + x, y0 + 4, Wh)
            if (x + 2) % 4 == 0:
                cv.set(x0 + x, y0 + 6, Wh)
        if not w(c - 1, r):
            for y in range(3, 9):
                cv.set(x0 + xa, y0 + y, K)
        if not w(c + 1, r):
            for y in range(3, 9):
                cv.set(x0 + xb, y0 + y, K)
    if vert:
        ya = 0 if w(c, r - 1) else 2
        yb = TH - 1 if w(c, r + 1) else TH - 3
        for y in range(ya, yb + 1):
            for x in range(2, 6):
                cv.set(x0 + x, y0 + y, E)
            cv.set(x0 + 2, y0 + y, K)
            cv.set(x0 + 5, y0 + y, K)
            cv.set(x0 + 6, y0 + y, T)
            if y % 4 == 0:
                cv.set(x0 + 3, y0 + y, K)
                cv.set(x0 + 4, y0 + y, K)
            if y % 4 == 1:
                cv.set(x0 + 3, y0 + y, Wh)
        if not w(c, r - 1):
            for x in range(2, 6):
                cv.set(x0 + x, y0 + ya, K)
        if not w(c, r + 1):
            for x in range(2, 6):
                cv.set(x0 + x, y0 + yb, K)


def kafenio(cv):
    K, Wh, E, B, C, R = (art.CH[k] for k in "kWeBcr")
    x0, y0, x1, y1 = 0, 96, 39, 143
    cv.rect(x0, y0, x1, y1, Wh)
    # roof texture
    for y in range(y0 + 4, y1 - 10, 6):
        for x in range(x0 + 3, x1 - 2, 4):
            cv.set(x + (2 if (y // 6) % 2 else 0), y, E)
    # outline and blue parapet
    for x in range(x0, x1 + 1):
        cv.set(x, y0, K)
        cv.set(x, y0 + 1, B)
        cv.set(x, y0 + 2, B)
    for y in range(y0, y1 + 1):
        cv.set(x1, y, K)
        cv.set(x1 - 1, y, B)
        cv.set(x0, y, B)
    cv.set(x0, y0, K)
    # solar water heater
    cv.rect(3, 100, 10, 101, E)
    cv.rect(3, 100, 10, 100, Wh)
    for x in range(3, 11):
        cv.set(x, 102, K)
    cv.rect(3, 103, 10, 109, C)
    for y in range(103, 110, 3):
        for x in range(3, 11):
            cv.set(x, y, art.CH['B'])
    for y in range(103, 110):
        cv.set(6, y, art.CH['B'])
    for x in range(3, 11):
        cv.set(x, 110, K)
    # flag (static part of the pole; the cloth is an animated sprite)
    for y in range(99, 113):
        cv.set(28, y, art.CH['r'])
    cv.set(28, 113, K)
    # chimney
    cv.rect(16, 102, 19, 107, E)
    cv.rect(17, 103, 18, 105, K)
    # sign: white letters on blue
    cv.rect(2, 116, 37, 129, B)
    for x in range(2, 38):
        cv.set(x, 116, K)
        cv.set(x, 129, K)
    for y in range(116, 130):
        cv.set(2, y, K)
        cv.set(37, y, K)
    cv.text("ΚΑΦΕΝΕΙΟ", 4, 120, Wh)
    # awning with blue/white stripes along the porch side
    for y in range(134, 144):
        for x in range(x0, x1 + 1):
            cv.set(x, y, B if (x // 2) % 2 == 0 else Wh)
    for x in range(x0, x1 + 1):
        cv.set(x, 133, K)
        if x % 4 == 1:
            cv.set(x, 143, K)


def porch(cv, with_sacks):
    K, Wh, E = art.CH['k'], art.CH['W'], art.CH['e']
    cells = [(c, 12) for c in range(5)] + [(c, 13) for c in range(6)]
    for (c, r) in cells:
        x0, y0 = c * TW, r * TH
        cv.rect(x0, y0, x0 + TW - 1, y0 + TH - 1, Wh)
        for y in range(TH):
            for x in range(TW):
                gy = (y0 + y) % 6 == 5
                gx = ((x0 + x) + (3 if ((y0 + y) // 6) % 2 else 0)) % 6 == 5
                if gy or gx:
                    cv.set(x0 + x, y0 + y, E)
    # tables with patrons (heads seen from above)
    patrons = [
        ((5, 149), [(1, 148, 'k'), (10, 149, 'e'), (5, 145, 'k')]),
        ((17, 149), [(13, 149, 'e'), (22, 148, 'k')]),
        ((4, 160), [(0, 160, 'e'), (9, 161, 'k'), (5, 165, 'k')]),
        ((16, 160), [(12, 160, 'k'), (21, 161, 'e')]),
    ]
    for (tx, ty), heads in patrons:
        cv.blit(TABLE, tx - 2, ty - 2)
        for (hx, hy, hair) in heads:
            cv.set(hx, hy, art.CH['s'])
            cv.set(hx + 1, hy, art.CH[hair])
            cv.set(hx, hy + 1, art.CH[hair])
            cv.set(hx + 1, hy + 1, art.CH[hair])
            cv.set(hx, hy + 2, art.CH['B'] if hair == 'k' else art.CH['k'])
            cv.set(hx + 1, hy + 2, art.CH['B'] if hair == 'k' else art.CH['k'])
    # a cat
    cv.blit(["y.y", "yyy", ".y.", "yyy", "..y"], 26, 160)
    if with_sacks:
        for (c, r) in SACKS1:
            x0, y0 = c * TW, r * TH
            cv.blit(SACK, x0, y0 + 1)
            cv.blit(SACK, x0 + 4, y0 + 3)


def kafenio_base(cv, with_sacks):
    kafenio(cv)
    porch(cv, with_sacks)


# church and courtyard of Stage 02: cells 15-19 x 0-3 and 15-19 x 4-5
CH_X0, CH_Y0 = 15 * TW, 0
YARD_Y0 = 4 * TH


def church(cv):
    K, Wh, E, B, C, Y, r, G, T = (art.CH[k] for k in "kWeBcyrgt")
    x0, x1, y1 = CH_X0, PFW - 1, YARD_Y0 - 1
    # grass around the church
    cv.rect(x0, 0, x1, y1, G)
    for (x, y) in ((x0 + 2, 3), (x1 - 3, 44), (x0 + 3, 41), (x1 - 2, 4)):
        cv.set(x, y, T)
        cv.set(x + 2, y, T)
        cv.set(x + 1, y + 1, T)
    # nave: whitewashed walls and barrel roof, running east-west
    nx0, nx1, ny0, ny1 = x0 + 8, x1 - 4, 13, 35
    cv.rect(nx0, ny0, nx1, ny1, K)
    cv.rect(nx0 + 1, ny0 + 1, nx1 - 1, ny1 - 1, Wh)
    mid_y = (ny0 + ny1) // 2
    for y in range(mid_y + 2, ny1 - 1):         # the roof curves away from the sun
        for x in range(nx0 + 1, nx1):
            if (y - mid_y) % 3 == 0 or y >= ny1 - 3:
                cv.set(x, y, E)
    for x in range(nx0 + 1, nx1):
        cv.set(x, mid_y, E)
    # apse at the east end
    for y in range(ny0 + 3, ny1 - 2):
        for x in range(nx1, x1 + 1):
            d = math.hypot((x - nx1) * 2, y - (ny0 + ny1) / 2)
            if d <= 7.5:
                cv.set(x, y, K if d > 6.5 else Wh)
    # blue dome in the middle, with a gold cross
    cx, cy = (nx0 + nx1) / 2, mid_y + 0.5
    for y in range(ny0 - 6, ny1 + 6):
        for x in range(nx0, nx1 + 1):
            d = math.hypot((x - cx) * 2, y - cy)
            if d <= 10.5:
                cv.set(x, y, K if d > 9.5 else C if (x - cx) * 2 + (y - cy) < -8 else B)
    mx, my = int(cx), int(cy)
    for (dx, dy) in ((0, -3), (0, -2), (-1, -1), (0, -1), (1, -1), (0, 0), (0, 1), (0, 2)):
        cv.set(mx + dx, my + dy, Y)
    # door to the courtyard, and a stone path
    for y in range(ny1 - 1, y1 + 1):
        for x in range(mx - 2, mx + 3):
            cv.set(x, y, E if y > ny1 else K if x in (mx - 2, mx + 2) else r)
    # bell tower at the west end, the bell in its arch
    bx0, bx1, by0, by1 = x0 + 2, x0 + 9, 9, 39
    cv.rect(bx0, by0, bx1, by1, K)
    cv.rect(bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, Wh)
    cv.rect(bx0 + 2, 20, bx1 - 2, 28, K)
    cv.rect(bx0 + 3, 22, bx1 - 3, 27, Y)
    cv.set(bx0 + 4, 21, r)
    for y in range(by0 + 2, by1 - 1, 4):
        cv.set(bx1 - 1, y, E)
    # flagpole on the tower (the cloth is the animated flag sprite)
    fx, fy = STAGES_FLAG2[0] * 2, STAGES_FLAG2[1]
    for y in range(fy, by0 + 1):
        cv.set(fx, y, r)


def courtyard(cv, with_sacks):
    K, Wh, E, O, Y, B = (art.CH[k] for k in "kWeoyB")
    x0, x1, y0, y1 = CH_X0, PFW - 1, YARD_Y0, YARD_Y0 + 2 * TH - 1
    # pebble mosaic: a white diamond in every cell
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u, v = x % TW, (y - y0) % TH
            d = abs(u - 3.5) * 2 + abs(v - 5.5)
            cv.set(x, y, Wh if 5 <= d < 6.5 else B if d < 1.5 else E)
    # low white wall, with a gate where the road arrives
    gx0, gx1 = 17 * TW, 18 * TW - 1
    for x in range(x0, x1 + 1):
        if not gx0 <= x <= gx1:
            cv.set(x, y1, K)
            cv.set(x, y1 - 1, Wh)
    for y in range(y0, y1 + 1):
        cv.set(x0, y, K)
        cv.set(x0 + 1, y, Wh)
    # candle stand: a tray of sand with candles
    cx0, cy0 = 16 * TW + 1, y0 + TH + 2
    cv.rect(cx0, cy0, cx0 + 5, cy0 + 6, K)
    cv.rect(cx0 + 1, cy0 + 1, cx0 + 4, cy0 + 5, O)
    for (dx, dy) in ((1, 1), (3, 2), (2, 4), (4, 4)):
        cv.set(cx0 + dx, cy0 + dy, Y)
    # the priest
    cv.blit(PRIEST, 19 * TW, y0 + TH - 1)
    if with_sacks:
        for (c, r_) in SACKS2:
            sx, sy = c * TW, r_ * TH
            cv.blit(SACK, sx, sy + 1)
            cv.blit(SACK, sx + 4, sy + 2)


# town hall of Stage 03: cells 14-19 x 10-13; the plaza is 12-13 x 9-13 and
# 14-19 x 9
TH_X0, TH_Y0 = 14 * TW, 10 * TH
PLAZA_Y0 = 9 * TH


def town_hall(cv):
    K, Wh, E, B, O, r, R, Y = (art.CH[k] for k in "kWeBorRy")
    x0, y0, x1, y1 = TH_X0, TH_Y0, PFW - 1, PFH - 1
    # steps and portico facing the plaza
    cv.rect(x0, y0, x1, y0 + 1, Wh)
    cv.rect(x0, y0 + 2, x1, y0 + 2, E)
    cv.rect(x0, y0 + 3, x1, y0 + 10, E)
    for x in range(x0 + 2, x1 - 1, 5):
        cv.rect(x, y0 + 3, x + 1, y0 + 9, Wh)
        cv.set(x + 2, y0 + 4, K)
        cv.set(x + 2, y0 + 8, K)
    cv.rect(x0 + 21, y0 + 4, x0 + 26, y0 + 10, r)      # the door
    cv.rect(x0 + 22, y0 + 5, x0 + 25, y0 + 10, K)
    # sign over the entrance
    cv.rect(x0, y0 + 11, x1, y0 + 20, K)
    cv.rect(x0 + 1, y0 + 12, x1 - 1, y0 + 19, Wh)
    cv.text("ΔΗΜΑΡΧΕΙΟ", x0 + 6, y0 + 13, K)
    # hipped roof of tiles
    ry0 = y0 + 21
    for y in range(ry0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.set(x, y, r if (y - ry0) % 3 == 0 else O)
    mid = (ry0 + y1) // 2
    for y in range(ry0, y1 + 1):          # hips from the corners to the ridge
        d = min(y - ry0, y1 - y)
        for x in (x0 + d * 2, x0 + d * 2 + 1, x1 - d * 2, x1 - d * 2 - 1):
            if x0 <= x <= x1:
                cv.set(x, y, R)
    for x in range(x0 + (mid - ry0) * 2, x1 - (mid - ry0) * 2 + 1):
        cv.set(x, mid, R)
    for y in range(ry0, y1 + 1):
        cv.set(x0, y, K)
    # flagpoles: the Greek flag is the animated sprite; the EU one is painted
    fx, fy = STAGES_FLAG3[0] * 2, STAGES_FLAG3[1]
    for y in range(fy, fy + 15):
        cv.set(fx, y, K if y == fy + 14 else r)
    ex, ey = x0 + 8, fy
    for y in range(ey, ey + 15):
        cv.set(ex, y, K if y == ey + 14 else r)
    cv.rect(ex + 1, ey, ex + 7, ey + 5, B)
    for (dx, dy) in ((4, 0), (2, 1), (6, 1), (1, 3), (7, 3), (2, 5), (6, 5), (4, 5)):
        if ex + dx <= ex + 7 and dy <= 5:
            cv.set(ex + dx, ey + dy, Y)


def plaza(cv, with_sacks):
    K, Wh, E, B, C, r, G, P, L, T = (art.CH[k] for k in "kWeBcrgplt")
    cells = [(c, r_) for c in (12, 13) for r_ in range(9, 14)] + [(c, 9) for c in range(14, 20)]
    for (c, r_) in cells:
        x0, y0 = c * TW, r_ * TH
        for y in range(TH):
            for x in range(TW):
                cv.set(x0 + x, y0 + y, Wh if y in (0, 6) or x == (0 if y < 6 else 4) else E)
    # edge of the plaza against the grass
    for y in range(PLAZA_Y0, PFH):
        cv.set(12 * TW, y, K)
    for x in range(12 * TW, PFW):
        cv.set(x, PLAZA_Y0, K)
    # the old plane tree
    cx, cy = 14 * TW + 7.5, PLAZA_Y0 + 5.5
    for y in range(PLAZA_Y0 - 2, PLAZA_Y0 + TH):
        for x in range(14 * TW - 2, 16 * TW + 2):
            d = math.hypot((x - cx) * 2, y - cy)
            if d <= 9:
                v = (x * 7 + y * 3) % 5
                cv.set(x, y, K if d > 8.2 else P if v == 0 else L if v == 1 else T)
    # fountain
    cx, cy = 17 * TW + 7.5, PLAZA_Y0 + 5.5
    for y in range(PLAZA_Y0, PLAZA_Y0 + TH):
        for x in range(17 * TW, 19 * TW):
            d = math.hypot((x - cx) * 2, y - cy)
            if d <= 6:
                cv.set(x, y, K if d > 5.4 else Wh if d > 4.4 else
                       Wh if d < 1.2 else C if (x + y) % 3 == 0 else B)
    # bench
    cv.rect(19 * TW + 1, PLAZA_Y0 + 3, 19 * TW + 6, PLAZA_Y0 + 4, r)
    cv.rect(19 * TW + 1, PLAZA_Y0 + 6, 19 * TW + 6, PLAZA_Y0 + 7, r)
    # the mayor
    cv.blit(MAYOR, 12 * TW, PLAZA_Y0 + 1)
    if with_sacks:
        for (c, r_) in SACKS3:
            sx, sy = c * TW, r_ * TH
            cv.blit(SACK, sx, sy + 1)
            cv.blit(SACK, sx + 4, sy + 2)


def town_hall_base(cv, with_sacks):
    town_hall(cv)
    plaza(cv, with_sacks)


STAGES_FLAG3 = (74, 141)


def church_base(cv, with_sacks):
    church(cv)
    courtyard(cv, with_sacks)


STAGES_FLAG2 = (62, 1)


# bakery of Stage 04: cells 0-4 x 0-3; the yard is 5 x 0-3 and 0-5 x 4
BK_X1, BK_Y1 = 5 * TW - 1, 4 * TH - 1


def bakery(cv):
    K, Wh, E, O, r, R, Y, B = (art.CH[k] for k in "kWeorRyB")
    x0, y0, x1, y1 = 0, 0, BK_X1, BK_Y1
    # stone walls
    cv.rect(x0, y0, x1, y1, E)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y % 4 == 3 or (x + (y // 4) * 3) % 6 == 0:
                cv.set(x, y, K)
    # tiled roof over the shop
    for y in range(y0, 25):
        for x in range(x0, 25):
            cv.set(x, y, r if y % 3 == 0 else O)
    for y in range(y0, 26):
        cv.set(25, y, K)
    for x in range(x0, 26):
        cv.set(x, 25, K)
    # chimney with a puff of smoke
    cv.rect(16, 6, 21, 11, K)
    cv.rect(17, 7, 20, 10, E)
    cv.rect(18, 8, 19, 9, K)
    for (x, y) in ((20, 3), (21, 2), (22, 3), (23, 1), (21, 4), (24, 2)):
        cv.set(x, y, Wh)
    # the wood-fired oven: a whitewashed dome, its mouth glowing toward the yard
    cx, cy = 32.5, 14.5
    for y in range(0, 32):
        for x in range(26, x1 + 1):
            d = math.hypot((x - cx) * 2, y - cy)
            if d <= 13:
                cv.set(x, y, K if d > 12 else Wh if (x - cx) * 2 + (y - cy) < 6 else E)
    cv.rect(35, 12, x1, 17, K)
    cv.rect(36, 13, x1, 16, R)
    cv.rect(37, 14, x1, 15, Y)
    # sign
    cv.rect(x0 + 1, 28, 34, 38, K)
    cv.rect(x0 + 2, 29, 33, 37, B)
    cv.text("ΦΟΥΡΝΟΣ", x0 + 4, 30, Wh)
    # shop window with loaves
    cv.rect(x0 + 3, 40, 30, y1, K)
    cv.rect(x0 + 4, 41, 29, y1, O)
    for x in range(x0 + 5, 29, 4):
        cv.set(x, 43, r)
        cv.set(x + 1, 43, r)
        cv.set(x + 1, 45, Y)
    # flagpole (the cloth is the animated flag sprite)
    fx, fy = STAGES_FLAG4[0] * 2, STAGES_FLAG4[1]
    for y in range(fy, fy + 15):
        cv.set(fx, y, K if y == fy + 14 else r)


def bake_yard(cv, with_sacks):
    K, Wh, E, O, r, Y, G = (art.CH[k] for k in "kWeoryg")
    cells = [(5, r_) for r_ in range(4)] + [(c, 4) for c in range(6)]
    for (c, r_) in cells:
        x0, y0 = c * TW, r_ * TH
        for y in range(TH):
            for x in range(TW):
                cv.set(x0 + x, y0 + y, K if (x == 7 or y == 11) and (x + y) % 2 else E)
    for y in range(0, 5 * TH):
        cv.set(6 * TW - 1, y, K)
    for x in range(0, 6 * TW):
        cv.set(x, 5 * TH - 1, K)
    # woodpile
    for (lx, ly) in ((1, 50), (4, 50), (2, 53), (5, 53), (1, 56), (4, 56)):
        cv.rect(lx, ly, lx + 2, ly + 2, r)
        cv.set(lx + 1, ly + 1, O)
    # rack of dakos drying in the sun
    cv.rect(17, 49, 30, 58, K)
    cv.rect(18, 50, 29, 57, Wh)
    for (dx, dy) in ((19, 51), (23, 51), (27, 51), (21, 55), (25, 55)):
        cv.rect(dx, dy, dx + 2, dy + 1, O)
        cv.set(dx + 1, dy, r)
    # the baker himself, with his peel
    cv.blit(art.BAKER, 5 * TW, 0)
    if with_sacks:
        for (c, r_) in SACKS4:
            sx, sy = c * TW, r_ * TH
            cv.blit(SACK, sx, sy + 1)
            cv.blit(SACK, sx + 4, sy + 2)


def bakery_base(cv, with_sacks):
    bakery(cv)
    bake_yard(cv, with_sacks)


STAGES_FLAG4 = (1, 1)


# school of Stage 05: cells 7-12 x 0-2; the yard is 6-13 x 3-4
SC_X0, SC_X1, SC_Y1 = 7 * TW, 13 * TW - 1, 3 * TH - 1
YARD5_X0, YARD5_X1, YARD5_Y0, YARD5_Y1 = 6 * TW, 14 * TW - 1, 3 * TH, 5 * TH - 1


def school(cv):
    K, Wh, E, B, C, O, r, R, G = (art.CH[k] for k in "kWeBcorRg")
    x0, x1, y1 = SC_X0, SC_X1, SC_Y1
    # red tiled roof
    for y in range(0, 17):
        for x in range(x0, x1 + 1):
            cv.set(x, y, r if y % 3 == 2 else R)
    for x in range(x0, x1 + 1):
        cv.set(x, 16, K)
    # whitewashed front with blue shutters and the door
    cv.rect(x0, 17, x1, y1, Wh)
    for x in range(x0 + 3, x1 - 3, 8):
        if abs(x - (x0 + x1) // 2) < 5:
            continue
        cv.rect(x, 28, x + 4, 34, K)
        cv.rect(x + 1, 29, x + 3, 33, C)
        cv.set(x + 2, 29, B)
        cv.set(x + 2, 31, B)
        cv.set(x + 2, 33, B)
    mx = (x0 + x1) // 2
    cv.rect(mx - 3, 28, mx + 3, y1, K)
    cv.rect(mx - 2, 29, mx + 2, y1, r)
    cv.set(mx + 1, 32, O)
    # sign
    cv.rect(x0 + 7, 17, x1 - 7, 27, K)
    cv.rect(x0 + 8, 18, x1 - 8, 26, B)
    cv.text("ΣΧΟΛΕΙΟ", x0 + 10, 19, Wh)
    for y in range(0, y1 + 1):
        cv.set(x0, y, K)
        cv.set(x1, y, K)


def schoolyard(cv, with_sacks):
    K, Wh, E, O, r, Y, B = (art.CH[k] for k in "kWeoryB")
    x0, x1, y0, y1 = YARD5_X0, YARD5_X1, YARD5_Y0, YARD5_Y1
    cv.rect(x0, y0, x1, y1, E)
    for (x, y) in ((x0 + 9, y0 + 3), (x0 + 37, y0 + 18), (x0 + 50, y0 + 6), (x0 + 22, y0 + 20)):
        cv.set(x, y, K)
    # a basketball court painted on the asphalt
    cx0, cx1, cy0, cy1 = x0 + 10, x0 + 47, y0 + 1, y0 + 12
    for x in range(cx0, cx1 + 1):
        cv.set(x, cy0, Wh)
        cv.set(x, cy1, Wh)
    for y in range(cy0, cy1 + 1):
        cv.set(cx0, y, Wh)
        cv.set(cx1, y, Wh)
    mx, my = (cx0 + cx1) // 2, (cy0 + cy1) / 2
    for y in range(cy0, cy1 + 1):
        cv.set(mx, y, Wh)
        for x in range(mx - 4, mx + 5):
            if 3.5 <= math.hypot((x - mx) * 2, y - my) < 4.8:
                cv.set(x, y, Wh)
    for hx, d in ((cx0, 1), (cx1, -1)):          # backboards and hoops
        cv.rect(hx - d, int(my) - 3, hx, int(my) + 3, Wh)
        cv.rect(min(hx + d, hx + 3 * d), int(my) - 1, max(hx + d, hx + 3 * d), int(my) + 1, O)
        cv.set(hx + 2 * d, int(my), E)
    cv.blit([".oo.", "oroo", "oooo", ".oo."], cx0 + 8, cy0 + 6)   # the ball
    # the teacher
    cv.blit(TEACHER, x0 + 1, y0)
    # flagpole (the cloth is the animated flag sprite)
    fx, fy = STAGES_FLAG5[0] * 2, STAGES_FLAG5[1]
    for y in range(fy, fy + 15):
        cv.set(fx, y, K if y == fy + 14 else r)
    # the yard's edge
    for x in range(x0, x1 + 1):
        cv.set(x, y1, K)
    for y in range(y0, y1 + 1):
        cv.set(x0, y, K)
        cv.set(x1, y, K)
    if with_sacks:
        for (c, r_) in SACKS5:
            sx, sy = c * TW, r_ * TH
            cv.blit(SACK, sx, sy + 1)
            cv.blit(SACK, sx + 4, sy + 2)


def school_base(cv, with_sacks):
    school(cv)
    schoolyard(cv, with_sacks)


STAGES_FLAG5 = (53, 36)


# the village pitch of Stage 06: pitch cells 5-14 x 4-10, the touchline with
# the bench 5-14 x 11, the stands 5-14 x 12-13
PI_X0, PI_X1, PI_Y0, PI_Y1 = 5 * TW, 15 * TW - 1, 4 * TH, 11 * TH - 1


def pitch(cv):
    K, Wh, G, P, E, O = (art.CH[k] for k in "kWgpeo")
    x0, x1, y0, y1 = PI_X0, PI_X1, PI_Y0, PI_Y1
    for y in range(y0, y1 + 1):              # mowing stripes, a cell wide
        for x in range(x0, x1 + 1):
            cv.set(x, y, G if (x // TW) % 2 else P)
    lx0, lx1, ly0, ly1 = x0 + 2, x1 - 2, y0 + 2, y1 - 1
    for x in range(lx0, lx1 + 1):
        cv.set(x, ly0, Wh)
        cv.set(x, ly1, Wh)
    for y in range(ly0, ly1 + 1):
        cv.set(lx0, y, Wh)
        cv.set(lx1, y, Wh)
        cv.set(10 * TW, y, Wh)                  # halfway line
    cx, cy = 10 * TW, (ly0 + ly1) / 2
    for y in range(ly0, ly1 + 1):
        for x in range(cx - 8, cx + 9):
            if 13 <= math.hypot((x - cx) * 2, y - cy) < 14.2:
                cv.set(x, y, Wh)
    cv.set(cx, int(cy), Wh)
    cv.set(cx - 1, int(cy), Wh)
    # penalty areas and goals with their nets
    gy0, gy1 = int(cy) - 10, int(cy) + 10
    for (gx, d) in ((lx0, 1), (lx1, -1)):
        bx = gx + 9 * d
        for y in range(gy0, gy1 + 1):
            cv.set(bx, y, Wh)
        for x in range(min(gx, bx), max(gx, bx) + 1):
            cv.set(x, gy0, Wh)
            cv.set(x, gy1, Wh)
        for y in range(int(cy) - 5, int(cy) + 6):
            for x in (gx - d, gx - 2 * d):
                cv.set(x, y, Wh if y in (int(cy) - 5, int(cy) + 5) or (x + y) % 2 else E)
    cv.blit([".WW.", "WkWW", "WWkW", ".WW."], cx + 10, int(cy) - 6)    # the ball


def stands(cv, with_sacks):
    K, Wh, E, B, R, Y, s_, r, G, C = (art.CH[k] for k in "kWeBRysrgc")
    # touchline: the bench, the cooler, the coach and the sacks
    y0, y1 = 11 * TH, 12 * TH - 1
    x0, x1 = PI_X0, PI_X1
    cv.rect(x0, y0, x1, y1, G)
    for x in range(x0, x1 + 1):
        cv.set(x, y0, Wh)
    bx0, bx1 = 7 * TW + 1, 9 * TW - 2                  # team bench under a blue shelter
    cv.rect(bx0, y0 + 2, bx1, y0 + 9, K)
    cv.rect(bx0 + 1, y0 + 3, bx1 - 1, y0 + 5, B)
    cv.rect(bx0 + 1, y0 + 6, bx1 - 1, y0 + 8, E)
    for x in range(bx0 + 2, bx1 - 1, 3):
        cv.set(x, y0 + 7, R)
    cv.rect(12 * TW + 2, y0 + 3, 12 * TW + 5, y0 + 9, B)   # water cooler
    cv.rect(12 * TW + 3, y0 + 2, 12 * TW + 4, y0 + 4, C)
    cv.blit(COACH, 5 * TW, y0 + 1)
    if with_sacks:
        for (c, r_) in SACKS6:
            sx, sy = c * TW, r_ * TH
            cv.blit(SACK, sx, sy + 1)
            cv.blit(SACK, sx + 4, sy + 2)
    # the stands: concrete terraces full of villagers
    y0, y1 = 12 * TH, PFH - 1
    cv.rect(x0, y0, x1, y1, E)
    for y in range(y0, y1 + 1, 4):
        for x in range(x0, x1 + 1):
            cv.set(x, y, Wh)
    heads = (s_, K, Y, R, B, Wh, r)
    for row, y in enumerate(range(y0 + 2, y1, 4)):
        for x in range(x0 + 1 + row % 2, x1, 3):
            if (x * 5 + row * 3) % 7 < 5:
                cv.set(x, y, heads[(x + row) % len(heads)])
                cv.set(x, y + 1, heads[(x * 3 + row) % len(heads)])
    for y in range(y0, y1 + 1):
        cv.set(x0, y, K)
        cv.set(x1, y, K)
    # flagpole at the end of the stands (the cloth is the animated flag sprite)
    fx, fy = STAGES_FLAG6[0] * 2, STAGES_FLAG6[1]
    for y in range(fy, fy + 15):
        cv.set(fx, y, K if y == fy + 14 else r)


def pitch_base(cv, with_sacks):
    pitch(cv)
    stands(cv, with_sacks)


STAGES_FLAG6 = (55, 146)


# the cemetery chapel of Stage 07: cells 15-19 x 5-8; the churchyard is
# 14 x 5-8 and 14-19 x 9
CC_X0, CC_Y0, CC_Y1 = 15 * TW, 5 * TH, 9 * TH - 1


def cemetery_chapel(cv):
    K, Wh, E, R, r, O, Y, G, T = (art.CH[k] for k in "kWeRroygt")
    x0, x1, y0, y1 = CC_X0, PFW - 1, CC_Y0, CC_Y1
    cv.rect(x0, y0, x1, y1, G)
    for (x, y) in ((x0 + 1, y0 + 2), (x1 - 3, y1 - 4), (x0 + 2, y1 - 2)):
        cv.set(x, y, T)
        cv.set(x + 2, y, T)
        cv.set(x + 1, y + 1, T)
    # the chapel: stone walls, a tiled gable roof running north-south
    nx0, nx1, ny0, ny1 = x0 + 6, x1 - 6, y0 + 10, y1 - 4
    cv.rect(nx0, ny0, nx1, ny1, K)
    cv.rect(nx0 + 1, ny0 + 1, nx1 - 1, ny1 - 1, Wh)
    mid = (nx0 + nx1) // 2
    for y in range(ny0 + 1, ny1 - 3):
        for x in range(nx0 + 1, nx1):
            cv.set(x, y, (r if y % 3 == 0 else O) if x <= mid else (O if y % 3 == 0 else r))
    for y in range(ny0 + 1, ny1 - 3):
        cv.set(mid, y, K)
    cv.rect(mid - 1, ny1 - 3, mid + 1, ny1 - 1, K)      # the door
    cv.set(mid, ny1 - 2, r)
    # belfry over the gate: a little stone arch with the bell and a cross
    bx0, bx1, by0, by1 = mid - 5, mid + 5, y0 + 1, y0 + 9
    cv.rect(bx0, by0, bx1, by1, K)
    cv.rect(bx0 + 1, by0 + 1, bx1 - 1, by1 - 1, E)
    cv.rect(mid - 2, by0 + 3, mid + 2, by1 - 1, K)
    cv.rect(mid - 1, by0 + 4, mid + 1, by1 - 2, Y)
    for (dx, dy) in ((0, 0), (0, 1), (-1, 1), (1, 1), (0, 2)):
        cv.set(mid + dx, by0 + dy, Y)
    # the ossuary beside it
    cv.rect(x0 + 1, ny0 + 4, x0 + 4, ny0 + 13, K)
    cv.rect(x0 + 2, ny0 + 5, x0 + 3, ny0 + 12, E)
    # flagpole (the cloth is the animated flag sprite)
    fx, fy = STAGES_FLAG7[0] * 2, STAGES_FLAG7[1]
    for y in range(fy, fy + 15):
        cv.set(fx, y, K if y == fy + 14 else r)


def churchyard(cv, with_sacks):
    K, Wh, E, R, Y, r = (art.CH[k] for k in "kWeRyr")
    cells = [(14, r_) for r_ in range(5, 9)] + [(c, 9) for c in range(14, 20)]
    for (c, r_) in cells:
        x0, y0 = c * TW, r_ * TH
        for y in range(TH):
            for x in range(TW):
                cv.set(x0 + x, y0 + y, E if x % 4 == 0 or y % 4 == 0 else Wh)
    # low wall with the gate where the road arrives
    gx0, gx1 = 16 * TW, 17 * TW - 1
    for x in range(14 * TW, PFW):
        if not gx0 <= x <= gx1:
            cv.set(x, 10 * TH - 1, K)
    for y in range(5 * TH, 10 * TH):
        cv.set(14 * TW, y, K)
    # oil lamps on the wall
    for x in (15 * TW + 3, 18 * TW + 3):
        cv.rect(x, 10 * TH - 4, x + 1, 10 * TH - 2, R)
        cv.set(x, 10 * TH - 5, Y)
    cv.blit(PRIEST, 14 * TW, 7 * TH)
    cv.blit(YIAYIA_BLACK, 17 * TW, 9 * TH + 1)
    if with_sacks:
        for (c, r_) in SACKS7:
            sx, sy = c * TW, r_ * TH
            cv.blit(SACK, sx, sy + 1)
            cv.blit(SACK, sx + 4, sy + 2)


def cemetery_base(cv, with_sacks):
    cemetery_chapel(cv)
    churchyard(cv, with_sacks)


STAGES_FLAG7 = (60, 61)


class Stage:
    toughness = 0       # invaders have the health of this many waves later

    def __init__(self, **kw):
        self.__dict__.update(kw)


STAGES = [
    Stage(map=MAP1, ground=GROUND1, air=AIR1, sacks=SACKS1, base=kafenio_base,
          flag=(14, 99), waves="WAVES1",
          strings={
              "B_STAGE": ("STAGE 01: THE KAFENIO", "ΠΙΣΤΑ 01: ΤΟ ΚΑΦΕΝΕΙΟ"),
              "B_WIN": ("KAFENIO SAVED! NOW, TO THE CHURCH!",
                        "ΤΟ ΚΑΦΕΝΕΙΟ ΣΩΘΗΚΕ! ΣΤΗΝ ΕΚΚΛΗΣΙΑ!"),
              "B_LOSE": ("THE KAFENIO HAS FALLEN!", "ΤΟ ΚΑΦΕΝΕΙΟ ΕΠΕΣΕ!"),
          }),
    Stage(map=MAP2, ground=GROUND2, air=AIR2, sacks=SACKS2, base=church_base,
          flag=STAGES_FLAG2, waves="WAVES2",
          strings={
              "B_STAGE": ("STAGE 02: THE VILLAGE CHURCH",
                          "ΠΙΣΤΑ 02: Η ΕΚΚΛΗΣΙΑ ΤΟΥ ΧΩΡΙΟΥ"),
              "B_WIN": ("CHURCH SAVED! NOW, TO THE TOWN HALL!",
                        "Η ΕΚΚΛΗΣΙΑ ΣΩΘΗΚΕ! ΣΤΟ ΔΗΜΑΡΧΕΙΟ!"),
              "B_LOSE": ("THE CHURCH HAS FALLEN!", "Η ΕΚΚΛΗΣΙΑ ΕΠΕΣΕ!"),
          }),
    Stage(map=MAP3, ground=GROUND3, air=AIR3, sacks=SACKS3, base=town_hall_base,
          flag=STAGES_FLAG3, waves="WAVES3", toughness=2,
          strings={
              "B_STAGE": ("STAGE 03: THE TOWN HALL", "ΠΙΣΤΑ 03: ΤΟ ΔΗΜΑΡΧΕΙΟ"),
              "B_WIN": ("TOWN HALL SAVED! NOW, TO THE BAKERY!",
                        "ΤΟ ΔΗΜΑΡΧΕΙΟ ΣΩΘΗΚΕ! ΣΤΟ ΦΟΥΡΝΟ!"),
              "B_LOSE": ("THE TOWN HALL HAS FALLEN!", "ΤΟ ΔΗΜΑΡΧΕΙΟ ΕΠΕΣΕ!"),
          }),
    Stage(map=MAP4, ground=GROUND4, air=AIR4, sacks=SACKS4, base=bakery_base,
          flag=STAGES_FLAG4, waves="WAVES4", toughness=1,
          strings={
              "B_STAGE": ("STAGE 04: THE BAKERY", "ΠΙΣΤΑ 04: Ο ΦΟΥΡΝΟΣ"),
              "B_WIN": ("BAKERY SAVED! NOW, TO THE SCHOOL!",
                        "Ο ΦΟΥΡΝΟΣ ΣΩΘΗΚΕ! ΣΤΟ ΣΧΟΛΕΙΟ!"),
              "B_LOSE": ("THE BAKERY HAS FALLEN!", "Ο ΦΟΥΡΝΟΣ ΕΠΕΣΕ!"),
          }),
    Stage(map=MAP5, ground=GROUND5, air=AIR5, sacks=SACKS5, base=school_base,
          flag=STAGES_FLAG5, waves="WAVES5",
          strings={
              "B_STAGE": ("STAGE 05: THE SCHOOL", "ΠΙΣΤΑ 05: ΤΟ ΣΧΟΛΕΙΟ"),
              "B_WIN": ("SCHOOL SAVED! NOW, TO THE PITCH!",
                        "ΤΟ ΣΧΟΛΕΙΟ ΣΩΘΗΚΕ! ΣΤΟ ΓΗΠΕΔΟ!"),
              "B_LOSE": ("THE SCHOOL HAS FALLEN!", "ΤΟ ΣΧΟΛΕΙΟ ΕΠΕΣΕ!"),
          }),
    Stage(map=MAP6, ground=GROUND6, air=AIR6, sacks=SACKS6, base=pitch_base,
          flag=STAGES_FLAG6, waves="WAVES6",
          strings={
              "B_STAGE": ("STAGE 06: THE VILLAGE PITCH", "ΠΙΣΤΑ 06: ΤΟ ΓΗΠΕΔΟ ΤΟΥ ΧΩΡΙΟΥ"),
              "B_WIN": ("PITCH SAVED! NOW, TO THE CEMETERY!",
                        "ΤΟ ΓΗΠΕΔΟ ΣΩΘΗΚΕ! ΣΤΟ ΝΕΚΡΟΤΑΦΕΙΟ!"),
              "B_LOSE": ("THE PITCH HAS FALLEN!", "ΤΟ ΓΗΠΕΔΟ ΕΠΕΣΕ!"),
          }),
    Stage(map=MAP7, ground=GROUND7, air=AIR7, sacks=SACKS7, base=cemetery_base,
          flag=STAGES_FLAG7, waves="WAVES7",
          strings={
              "B_STAGE": ("STAGE 07: THE CEMETERY CHURCH",
                          "ΠΙΣΤΑ 07: Η ΕΚΚΛΗΣΙΑ ΤΟΥ ΝΕΚΡΟΤΑΦΕΙΟΥ"),
              "B_WIN": ("VICTORY! THE VROUVES ARE SAFE!", "ΝΙΚΗ! ΟΙ ΒΡΟΥΒΕΣ ΣΩΘΗΚΑΝ!"),
              "B_LOSE": ("THE CEMETERY CHURCH HAS FALLEN!",
                         "Η ΕΚΚΛΗΣΙΑ ΤΟΥ ΝΕΚΡΟΤΑΦΕΙΟΥ ΕΠΕΣΕ!"),
          }),
]
STAGE_STRINGS = ["B_STAGE", "B_WIN", "B_LOSE"]

# defenders each stage has (types 1 cretan, 2 yiayia, 3 bride, 4 psssst,
# 5 cauldron, 6 baker) and the two lines of the announcement at its start
UNLOCKS = [
    ({1, 4}, "S_INFO1", "S_INFO4"),
    ({1, 2, 4}, "B_NEWDEF", "S_INFO2"),
    ({1, 2, 3, 4}, "B_NEWDEF", "S_INFO3"),
    ({1, 2, 3, 4, 6}, "B_NEWDEF", "S_INFO6"),
    ({1, 2, 3, 4, 5, 6}, "B_NEWDEF", "S_INFO5"),
]


def render_background(stage, grid, with_sacks=True):
    cv = Canvas(PFW, PFH, art.CH['g'])
    for r in range(MH):
        for c in range(MW):
            t = grid[r][c]
            if t == '#':
                path_cell(cv, grid, c, r)
            elif t == 'W':
                wall_cell(cv, grid, c, r)
            elif t in 'KP':
                pass
            else:
                grass_cell(cv, c, r, None if t == '.' else 3)
                if t == 'T':
                    cv.blit(TREE if (c + r) % 3 else TREE2, c * TW, r * TH)
                elif t == 'C':
                    cv.blit(CACTUS, c * TW, r * TH)
                elif t == 'G':
                    cv.blit(GOAT_W if (c + r) % 2 else GOAT_B, c * TW, r * TH)
                elif t == 'Y':
                    cv.blit(CYPRESS, c * TW, r * TH)
                elif t == 'X':
                    cv.blit(GRAVE_A if (c + r) % 4 < 2 else GRAVE_B, c * TW, r * TH)
    stage.base(cv, with_sacks)
    return cv


# ------------------------------------------------------------------ music

NOTE_IDX = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
            'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def note_period(name):
    n, octv = name[:-1], int(name[-1])
    midi = 12 * (octv + 1) + NOTE_IDX[n]
    f = 440.0 * 2 ** ((midi - 69) / 12)
    return int(round(1000000 / (16 * f)))


MEL_A = """
D4/2 E4/2 F4/2 G4/2 A4/4 G4/2 F4/2 E4/2 F4/2 G4/2 E4/2 D4/8
A4/2 Bb4/2 A4/2 G4/2 F4/2 G4/2 A4/4 G4/2 F4/2 E4/2 F4/2 D4/8
D5/2 C5/2 Bb4/2 A4/2 Bb4/2 A4/2 G4/4 A4/2 G4/2 F4/2 E4/2 F4/4 E4/4
D4/2 E4/2 F4/2 G4/2 A4/2 G4/2 F4/2 E4/2 E4/2 F4/2 E4/2 C#4/2 D4/8
"""
MEL_B = """
A4/1 Bb4/1 A4/1 G4/1 A4/2 D4/2 A4/1 Bb4/1 A4/1 G4/1 A4/2 D4/2
G4/1 A4/1 G4/1 F4/1 G4/2 C4/2 G4/1 A4/1 G4/1 F4/1 E4/4
F4/1 G4/1 F4/1 E4/1 F4/2 A4/2 E4/1 F4/1 E4/1 D4/1 E4/2 G4/2
F4/2 E4/2 D4/2 C#4/2 D4/8
"""
BASS_A = "D D C D Bb F C D Bb G A A D C A D".split()
BASS_B = "D D C A F C A D".split()
BASS_ROOTS = BASS_A + BASS_A + BASS_B
FIFTH = {'D': 'A', 'C': 'G', 'Bb': 'F', 'F': 'C', 'G': 'D', 'A': 'E'}
SIXTEENTH = 6   # frames


def parse_mel(s):
    out = []
    for tok in s.split():
        n, d = tok.split('/')
        out.append((n, int(d) * SIXTEENTH))
    return out


def bass_line():
    out = []
    for root in BASS_ROOTS:
        fifth = FIFTH[root]
        lo = 2 if root in ('D', 'C') else (1 if root in ('Bb', 'A', 'G') else 2)
        if root in ('Bb', 'A', 'G'):
            out += [(root + "2", 3 * SIXTEENTH), ("R", SIXTEENTH),
                    (fifth + ("3" if fifth in ('D', 'E', 'F') else "2"), 3 * SIXTEENTH), ("R", SIXTEENTH)]
        else:
            out += [(root + "2", 3 * SIXTEENTH), ("R", SIXTEENTH),
                    (fifth + "2", 3 * SIXTEENTH), ("R", SIXTEENTH)]
        del lo
    return out


# sound effects: list of (tone period, noise period (0 = none), volume)
SFX = {
    "SFX_RIFLE": [(0, 6, 13), (0, 9, 10), (0, 12, 7), (0, 15, 4)],
    "SFX_PISTOL": [(0, 3, 10), (0, 5, 6), (0, 7, 3)],
    "SFX_LASER": [(30, 0, 12), (45, 0, 11), (60, 0, 10), (80, 0, 9), (100, 0, 7), (130, 0, 5)],
    "SFX_THROW": [(300, 0, 10), (260, 0, 10), (220, 0, 9), (190, 0, 7), (170, 0, 5)],
    "SFX_BASH": [(400, 14, 14), (500, 18, 12), (0, 22, 9), (0, 26, 5)],
    "SFX_PUFF": [(0, 20, 10), (0, 22, 11), (0, 24, 10), (0, 26, 9), (0, 28, 8), (0, 30, 6), (0, 31, 4)],
    "SFX_DIE": [(200, 8, 13), (300, 12, 12), (400, 16, 10), (500, 20, 8), (600, 24, 5)],
    "SFX_HURT": [(900, 0, 15), (1000, 0, 14), (1100, 25, 13), (1200, 28, 11), (1300, 31, 9), (1400, 31, 6)],
    "SFX_BUILD": [(250, 0, 12), (250, 0, 12), (180, 0, 12), (180, 0, 12), (125, 0, 12), (125, 0, 9)],
    "SFX_ERROR": [(700, 0, 12), (700, 0, 12), (700, 0, 0), (700, 0, 12), (700, 0, 12), (700, 0, 6)],
    "SFX_SELL": [(125, 0, 12), (125, 0, 12), (180, 0, 10), (250, 0, 8)],
    "SFX_WAVE": [(213, 0, 13)] * 4 + [(169, 0, 13)] * 4 + [(142, 0, 13)] * 4 + [(106, 0, 13)] * 8 + [(106, 0, 8)] * 4,
    "SFX_CRUSH": [(1500, 10, 15), (1700, 14, 14), (2000, 18, 12), (2200, 24, 10), (2500, 31, 7)],
    "SFX_MOVE": [(80, 0, 6)],
}
SFX_PRIO = {"SFX_MOVE": 0, "SFX_PISTOL": 1, "SFX_RIFLE": 1, "SFX_LASER": 1, "SFX_THROW": 1,
            "SFX_PUFF": 2, "SFX_BASH": 2, "SFX_DIE": 3, "SFX_SELL": 4, "SFX_BUILD": 4,
            "SFX_ERROR": 4, "SFX_CRUSH": 5, "SFX_HURT": 6, "SFX_WAVE": 7}

# ------------------------------------------------------------------ waves
# enemy types: 1 drone, 2 guard, 3 tank.  (type, count, interval in frames)
WAVES1 = [
    [(2, 6, 45)],
    [(1, 8, 28)],
    [(2, 6, 36), (1, 6, 24)],
    [(2, 6, 30), (3, 2, 70)],
    [(1, 12, 18), (2, 5, 30)],
    [(2, 10, 26), (3, 3, 60)],
    [(1, 14, 16), (2, 8, 24), (3, 2, 50)],
    [(3, 5, 50), (2, 10, 22), (1, 8, 16)],
    [(1, 18, 14), (2, 10, 20), (3, 4, 40)],
    [(2, 12, 18), (1, 16, 12), (3, 8, 36)],
]
# the church: a shorter road and a little more in every wave
WAVES2 = [
    [(2, 7, 42)],
    [(1, 10, 26)],
    [(2, 7, 34), (1, 6, 24)],
    [(2, 7, 30), (3, 2, 70)],
    [(1, 12, 18), (2, 6, 28)],
    [(2, 10, 24), (3, 3, 56)],
    [(1, 14, 16), (2, 9, 22), (3, 2, 48)],
    [(3, 5, 46), (2, 11, 20), (1, 10, 14)],
    [(1, 18, 13), (2, 11, 18), (3, 4, 40)],
    [(2, 13, 16), (1, 16, 11), (3, 9, 32)],
]
# the town hall: bigger again, and tougher invaders
WAVES3 = [
    [(2, 9, 38)],
    [(1, 13, 22)],
    [(2, 9, 30), (1, 8, 20)],
    [(2, 9, 26), (3, 4, 58)],
    [(1, 15, 15), (2, 8, 24)],
    [(2, 13, 20), (3, 5, 48)],
    [(1, 17, 14), (2, 12, 18), (3, 4, 40)],
    [(3, 6, 40), (2, 14, 16), (1, 13, 12)],
    [(1, 21, 11), (2, 13, 15), (3, 6, 34)],
    [(2, 15, 13), (1, 18, 9), (3, 11, 26)],
]
# the bakery, the last stand: three lanes close together, so many more invaders
WAVES4 = [
    [(2, 10, 34)],
    [(1, 14, 20), (2, 4, 30)],
    [(2, 11, 26), (1, 10, 18)],
    [(2, 11, 22), (3, 4, 52)],
    [(1, 18, 13), (2, 10, 20)],
    [(2, 16, 16), (3, 6, 40)],
    [(1, 22, 11), (2, 15, 15), (3, 5, 34)],
    [(3, 9, 32), (2, 16, 14), (1, 16, 10)],
    [(1, 24, 9), (2, 17, 13), (3, 9, 28)],
    [(2, 20, 11), (1, 22, 8), (3, 16, 20)],
]
# the school, the very last stand
WAVES5 = [
    [(2, 10, 32)],
    [(1, 15, 18), (2, 5, 28)],
    [(2, 12, 24), (1, 11, 16)],
    [(2, 12, 20), (3, 5, 48)],
    [(1, 20, 12), (2, 11, 18)],
    [(2, 16, 15), (3, 6, 38)],
    [(1, 22, 10), (2, 15, 14), (3, 5, 32)],
    [(3, 10, 28), (2, 17, 12), (1, 18, 9)],
    [(1, 26, 8), (2, 18, 11), (3, 10, 24)],
    [(2, 22, 9), (1, 24, 7), (3, 18, 16)],
]
# the pitch: a short road around the field, so smaller waves
WAVES6 = [
    [(2, 7, 40)],
    [(1, 10, 24)],
    [(2, 7, 32), (1, 6, 22)],
    [(2, 7, 28), (3, 2, 64)],
    [(1, 12, 17), (2, 6, 26)],
    [(2, 10, 22), (3, 3, 54)],
    [(1, 14, 15), (2, 9, 20), (3, 2, 46)],
    [(3, 5, 44), (2, 11, 18), (1, 10, 13)],
    [(1, 17, 12), (2, 11, 17), (3, 4, 40)],
    [(2, 13, 15), (1, 16, 10), (3, 8, 30)],
]
# the cemetery church: the road winds between the graves, the final stand
WAVES7 = [
    [(2, 10, 32)],
    [(1, 15, 18), (2, 5, 28)],
    [(2, 12, 24), (1, 11, 16)],
    [(2, 12, 20), (3, 5, 48)],
    [(1, 20, 12), (2, 11, 18)],
    [(2, 16, 15), (3, 6, 38)],
    [(1, 22, 10), (2, 15, 14), (3, 5, 32)],
    [(3, 10, 28), (2, 17, 12), (1, 18, 9)],
    [(1, 26, 8), (2, 18, 11), (3, 10, 24)],
    [(2, 22, 9), (1, 24, 7), (3, 18, 16)],
]


# ------------------------------------------------------------------ title art
# The first title page: a scene at the Kafenio above the keys, 160 pixels x
# 128 lines (screen lines 40-167); the key labels are printed
# over the black part by the game, in the active language (T_CTRL, T_CTRL2).
TART_SCENE = [
    "KKKKK.T...T.....T..T",
    "KKKKK.......########",
    "KKKKK.......#.......",
    "KKKKK.......#..T....",
    "PPPPP########.......",
    "PPPPPP.T..T....T....",
]
TART_Y0 = 96            # scene lines taken from the map (cell row 8)
TART_ROWS = (108, 124, 140, 156)    # label lines; keys sit around them
ARROWS = {
    "L": ["..k..", ".kk..", "kkkkk", ".kk..", "..k.."],
    "U": ["..k..", ".kkk.", "kkkkk", "..k..", "..k.."],
}
ARROWS["R"] = [r[::-1] for r in ARROWS["L"]]
ARROWS["D"] = ARROWS["U"][::-1]


def keycap(cv, x0, y0, w, label=None, arrow=None):
    E, Wh, K = art.CH['e'], art.CH['W'], art.CH['k']
    for y in range(11):
        for x in range(w):
            if x in (0, w - 1) and y in (0, 10):
                continue
            face = 1 <= x <= w - 2 and 1 <= y <= 8
            cv.set(x0 + x, y0 + y, Wh if face else E)
    if arrow:
        for j, r in enumerate(ARROWS[arrow]):
            for i, ch in enumerate(r):
                if ch == 'k':
                    cv.set(x0 + (w - 5) // 2 + i, y0 + 2 + j, K)
    if label:
        cv.text(label, x0 + (w - (4 * len(label) - 1)) // 2, y0 + 2, K)


def title_art():
    grid = [list("." * MW) for _ in range(MH)]
    for j, r in enumerate(TART_SCENE):
        grid[8 + j] = list(r)
    cv = render_background(STAGES[0], grid, True)
    for rows, c, r, dy in [
            (art.TANK_L_A, 17, 9, 0), (art.GUARD_A, 14, 9, 0), (art.GUARD_B, 12, 10, 4),
            (art.DRONE_A, 8, 8, 4), (art.DRONE_B, 4 + 11, 8, 1),
            (art.CRETAN, 10, 10, 0), (art.YIAYIA, 14, 10, 0), (art.BRIDE, 9, 11, 0),
            (art.PSSSST, 18, 8, 0), (art.CAULDRON, 13, 11, 0), (art.BAKER, 7, 11, 0)]:
        cv.blit(rows, c * TW, r * TH + dy)
    cv.blit(art.BULLET, 12 * TW + 1, 10 * TH + 4)
    cv.blit(art.LASER, 18 * TW - 2, 9 * TH + 3)
    cv.blit(art.LASER, 18 * TW - 4, 9 * TH + 5)
    cv.blit(art.DAKOS, 8 * TW + 2, 10 * TH + 2)
    cv.blit(art.SPARK, 14 * TW + 6, 9 * TH + 2)
    out = Canvas(PFW, 128, art.CH['k'])
    for y in range(64):
        out.p[y] = list(cv.p[TART_Y0 + y])
    # the keys, right-aligned to the label columns (12 and 30)
    r0, r1, r2, r3 = (y - 40 - 2 for y in TART_ROWS)
    for i, a in enumerate("LURD"):
        keycap(out, 4 + 10 * i, r0, 9, arrow=a)
    keycap(out, 4, r1, 39, "SPACE")
    keycap(out, 34, r2, 9, "N")
    keycap(out, 34, r3, 9, "M")
    keycap(out, 92, r0, 9, "1")
    out.rect(102, r0 + 5, 104, r0 + 5, art.CH['W'])
    keycap(out, 107, r0, 9, "6")
    keycap(out, 107, r1, 9, "S")
    keycap(out, 107, r2, 9, "H")
    keycap(out, 107, r3, 9, "L")
    return out
