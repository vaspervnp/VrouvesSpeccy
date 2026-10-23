"""The Spectrum's stages: 15 x 10 cells of 16 x 16 pixels, each cell exactly
2 x 2 attribute cells, so no cell shares its colours with another.

The maps, roads and the places of the buildings are the Spectrum's own; the
art is the CPC's (world.py): a cell's grass, road, wall, tree... is drawn as
on the CPC (8 x 12 Mode 0 pixels) and doubled across, stretched 4/3 down.
The buildings and their yards are cut from the CPC's stage pictures, as the
Spectrum showed them before (zxcolour.widen: 1.5 across), and put in a block
of cells of their own, where the sacks are drawn a cell each.

Map characters as world.py's: '.' grass, T tree, C cactus, G goat, Y cypress,
W wall, X grave, F the football pitch (buildable), K the building's block.
"""
import art
import world
import zxcolour as zc

MW, MH = 15, 10
CS = 16                         # a cell, Spectrum pixels
PFW, PFH = MW * CS, MH * CS


class Stage:
    def __init__(self, **kw):
        self.__dict__.update(kw)


# block: (x, y) of the crop in the CPC stage's picture as the Spectrum showed
# it (240 x 168, 1.5 across), its size in cells, and the cell it goes to;
# sacks: five cells of the block where the sacks are
STAGES = [
    Stage(map=[
        "T..T....T..C..T",
        "..............T",
        "T...WWWW..G...T",
        "T............Y.",
        ".G..C........T.",
        "KKKKK.......W.T",
        "KKKKK..WW...T..",
        "KKKKK.......G.T",
        "KKKKK.T.C....T.",
        "KKKKK......T..T",
    ], ground=[(12, 0), (12, 1), (1, 1), (1, 3), (11, 3), (11, 5), (6, 5), (6, 7), (10, 7),
               (10, 9), (5, 9)],
        air=[(12, 0), (9, 3), (9, 6), (6, 9), (5, 9)],
        crop=(0, 88), block=(0, 5, 5, 5), sacks=[(0, 9), (1, 9), (2, 9), (3, 9), (4, 9)]),
    Stage(map=[
        "T..Y....T..KKKK",
        ".........C.KKKK",
        "T.G...Y....KKKK",
        "Y....WW....KKKK",
        "T.......T..KKKK",
        "Y..........T..Y",
        "T.....G.......T",
        "T.....C.....T..",
        "Y............TY",
        "T.T.Y.....T..CT",
    ], ground=[(1, 9), (1, 7), (4, 7), (4, 5), (1, 5), (1, 1), (8, 1), (8, 8), (11, 8),
               (11, 6), (13, 6), (13, 5)],
        air=[(1, 9), (5, 5), (13, 5)],
        crop=(176, 0), block=(11, 0, 4, 5), sacks=[(11, 4), (12, 4), (13, 4), (14, 4), (14, 3)]),
    Stage(map=[
        "T..T...C...T..T",
        "..............T",
        "T...WWWW...Y..T",
        "..T......C..T..",
        "T..............",
        "Y....T.....WW.T",
        "T.G......KKKKKK",
        ".........KKKKKK",
        "T........KKKKKK",
        "Y.T.C..Y.KKKKKK",
    ], ground=[(0, 1), (13, 1), (13, 4), (1, 4), (1, 8), (4, 8), (4, 6), (7, 6), (7, 8),
               (8, 8)],
        air=[(0, 1), (7, 8), (8, 8)],
        crop=(144, 104), block=(9, 6, 6, 4), sacks=[(9, 7), (9, 8), (9, 9), (10, 6), (11, 6)]),
    Stage(map=[
        "KKKKK..T...C..T",
        "KKKKK.....Y...T",
        "KKKKK.....WWW.T",
        "KKKKK..T......T",
        "T.C...........Y",
        "Y..WWWW...G...T",
        "T..............",
        "Y..G....T...W.T",
        "T..............",
        "T.T..Y..T..C.YT",
    ], ground=[(14, 8), (1, 8), (1, 6), (13, 6), (13, 4), (6, 4), (6, 2), (5, 2)],
        air=[(14, 8), (11, 8), (5, 2)],
        crop=(0, 0), block=(0, 0, 5, 4), sacks=[(0, 3), (1, 3), (2, 3), (3, 3), (4, 3)]),
    Stage(map=[
        "T..TKKKKKK..T.T",
        "..C.KKKKKK....Y",
        "Y...KKKKKK...T.",
        "T...KKKKKK..Y.T",
        "..T.WWW.....T.T",
        "T............YT",
        "Y.G....C......T",
        "T..............",
        "Y...C....T.....",
        "..............T",
    ], ground=[(0, 9), (13, 9), (13, 7), (1, 7), (1, 5), (11, 5), (11, 2), (10, 2)],
        air=[(0, 9), (3, 9), (10, 2)],
        crop=(72, 0), block=(4, 0, 6, 4), sacks=[(4, 3), (5, 3), (6, 3), (7, 3), (8, 3)]),
    Stage(map=[
        "T.............T",
        "..C..Y.....T...",
        "T...FFFFFFFF..T",
        "Y...FFFFFFFF...",
        "T...FFFFFFFF..T",
        "....FFFFFFFF..Y",
        "T...FFFFFFFF..T",
        "Y...KKKKKKKK..T",
        "T...KKKKKKKK...",
        "T.T.KKKKKKKK.YT",
    ], ground=[(14, 8), (13, 8), (13, 0), (1, 0), (1, 3), (3, 3), (3, 5), (1, 5), (1, 8),
               (3, 8)],
        air=[(14, 8), (12, 6), (5, 6), (3, 8)],
        crop=(56, 120), block=(4, 7, 8, 3), sacks=[(5, 7), (6, 7), (9, 7), (10, 7), (11, 7)]),
    Stage(map=[
        "T..Y...T....Y.T",
        ".........C...YT",
        "T.X.X.X.....Y.T",
        "Y.........KKKKK",
        "T..X.X....KKKKK",
        "Y..X.X....KKKKK",
        "T..X.X...XKKKKK",
        "Y..X.X...X.X..T",
        "T.............T",
        "Y..T..Y..T..Y.T",
    ], ground=[(0, 1), (8, 1), (8, 3), (1, 3), (1, 8), (6, 8), (6, 5), (8, 5), (8, 8),
               (12, 8), (12, 7)],
        air=[(0, 1), (4, 1), (10, 7), (12, 7)],
        crop=(160, 56), block=(10, 3, 5, 4), sacks=[(10, 6), (11, 6), (12, 6), (13, 6), (14, 6)]),
]
for _k, _st in enumerate(STAGES):
    _cpc = world.STAGES[_k]
    _st.cpc = _cpc
    _st.waves = _cpc.waves
    _st.strings = _cpc.strings
    _st.toughness = _cpc.toughness
    assert len(_st.map) == MH and all(len(r) == MW for r in _st.map), _k


def carve_path(grid, wps):
    saved = world.MW, world.MH
    world.MW, world.MH = MW, MH
    try:
        return world.carve_path(grid, wps)
    finally:
        world.MW, world.MH = saved


def double(rows):
    """CPC sprite rows -> twice as wide (a Mode 0 pixel is two of ours)"""
    return ["".join(ch * 2 for ch in r) for r in rows]


def cpc_cells(grid):
    """the cells' own art, on a CPC canvas of MW x MH cells of 8 x 12"""
    saved = world.MW, world.MH
    world.MW, world.MH = MW, MH
    try:
        cv = world.Canvas(MW * world.TW, MH * world.TH, art.CH['g'])
        for r in range(MH):
            for c in range(MW):
                t = grid[r][c]
                if t == '#':
                    world.path_cell(cv, grid, c, r)
                elif t == 'W':
                    world.wall_cell(cv, grid, c, r)
                elif t == 'F':          # the pitch: mowing stripes, a cell wide
                    cv.rect(c * 8, r * 12, c * 8 + 7, r * 12 + 11,
                            art.CH['g'] if c % 2 else art.CH['p'])
                    if r == 2 or (r > 2 and grid[r - 1][c] != 'F'):
                        cv.rect(c * 8, r * 12 + 1, c * 8 + 7, r * 12 + 1, art.CH['W'])
                    if c == 0 or grid[r][c - 1] != 'F':
                        cv.rect(c * 8 + 1, r * 12, c * 8 + 1, r * 12 + 11, art.CH['W'])
                    if c == MW - 1 or grid[r][c + 1] != 'F':
                        cv.rect(c * 8 + 6, r * 12, c * 8 + 6, r * 12 + 11, art.CH['W'])
                elif t == 'K':
                    pass
                else:
                    world.grass_cell(cv, c, r, None if t == '.' else 3)
                    x0, y0 = c * 8, r * 12
                    if t == 'T':
                        cv.blit(world.TREE if (c + r) % 3 else world.TREE2, x0, y0)
                    elif t == 'C':
                        cv.blit(world.CACTUS, x0, y0)
                    elif t == 'G':
                        cv.blit(world.GOAT_W if (c + r) % 2 else world.GOAT_B, x0, y0)
                    elif t == 'Y':
                        cv.blit(world.CYPRESS, x0, y0)
                    elif t == 'X':
                        cv.blit(world.GRAVE_A if (c + r) % 4 < 2 else world.GRAVE_B, x0, y0)
        return cv
    finally:
        world.MW, world.MH = saved


def render(k, with_sacks=True):
    """stage k -> rows of pen characters, PFW x PFH"""
    st = STAGES[k]
    grid = carve_path(st.map, st.ground)
    cv = cpc_cells(grid)
    pix = [[zc.PEN_OF[cv.p[r * 12 + (y % CS) * 3 // 4][c * 8 + (x % CS) // 2]]
            for x in range(PFW) for c in [x // CS]]
           for y in range(PFH) for r in [y // CS]]
    # the building and its yard, from the CPC's stage with no sacks
    cgrid = world.carve_path(st.cpc.map, st.cpc.ground)
    full = world.render_background(st.cpc, cgrid, False)
    wide = zc.widen([[zc.PEN_OF[v] for v in row] for row in full.p])
    cx, cy = st.crop
    bc, br, bw, bh = st.block
    for y in range(bh * CS):
        for x in range(bw * CS):
            pix[br * CS + y][bc * CS + x] = wide[cy + y][cx + x]
    if with_sacks:
        sack = double(world.SACK)
        for (c, r) in st.sacks:
            for (dx, dy) in ((1, 2), (7, 5)):
                for j, row in enumerate(sack):
                    for i, ch in enumerate(row):
                        if ch != '.':
                            pix[r * CS + dy + j][c * CS + dx + i] = ch
    return pix, grid


def flag_xy(k):
    """the flag's place, pixels: the CPC's, as the block moved it"""
    st = STAGES[k]
    fx, fy = st.cpc.flag
    cx, cy = st.crop
    bc, br, _, _ = st.block
    return fx * 3 - cx + bc * CS, fy - cy + br * CS


def free_cells(k):
    """the block's attribute cells: any two colours there"""
    bc, br, bw, bh = STAGES[k].block
    return {(x, y) for y in range(br * 2, (br + bh) * 2) for x in range(bc * 2, (bc + bw) * 2)}
