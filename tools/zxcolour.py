"""The Spectrum's colours, and how the CPC's pictures become Spectrum ones.

The CPC game is drawn in 16 pens (art.py) at 160 x 200 Mode 0 pixels, each
twice as wide as it is tall.  Here a map cell of 8 x 12 Mode 0 pixels becomes
12 x 12 Spectrum pixels: every Mode 0 pixel is one or two pixels wide
(WIDEN, symmetric so a mirrored sprite stays the mirror of itself).

The playfield keeps black as the ink of every attribute cell: the sprites
are drawn in ink over it, so they show black on any paper.  A cell's paper is
its most common colour; the other colours become paper or ink by how dark
they are against it, half-way ones a checkerboard of both.
"""
import art

# Spectrum colours: index 0-7, normal and bright
RGB = [[(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215),
        (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)],
       [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),
        (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]]
BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE = range(8)

# CPC pen -> (Spectrum colour, bright)
PEN = {
    'k': (BLACK, 0), 'n': (BLACK, 0),
    'g': (GREEN, 0),        # grass
    'o': (YELLOW, 0),       # the dirt road, sacks, dakos
    'r': (RED, 0),          # dark red / brown
    'e': (WHITE, 0),        # grey stone
    'W': (WHITE, 1),
    'B': (BLUE, 1),
    'c': (CYAN, 1),         # sky blue
    'y': (YELLOW, 1),
    'R': (RED, 1),
    'l': (GREEN, 1),        # toxic green
    's': (MAGENTA, 1),      # skin
    't': (GREEN, 0),        # teal: olive trees, a darker green
    'p': (GREEN, 1),        # pastel green
    'h': (YELLOW, 0),       # khaki
}
PEN_OF = {v: k for k, v in art.CH.items() if k != 'n'}
PEN_OF[15] = 'n'


def lum(rgb):
    r, g, b = rgb
    return 0.30 * r + 0.59 * g + 0.11 * b


# how dark each pen is, 0 (black) .. 255; drives the ink / paper choice
PEN_LUM = {ch: lum(art.PEN_RGB[art.CH[ch]]) for ch in art.CH}
DARK_PENS = set('knrBtgRh')
SHADE = set('knt')               # no vote for a cell's paper
SHADE_V = 0.6                    # and the teal shade: half ink     # sprite pixels that are drawn in ink


def widths(n):
    """Spectrum pixels for each of n Mode 0 pixels (n even): 1, 2, 1, 2...
    on the left half, mirrored on the right; 3/2 n in all"""
    if n == 2:
        return [2, 1]
    half = [1 + (i & 1) for i in range(n // 2)]
    w = half + half[::-1]
    assert sum(w) * 2 == 3 * n, n
    return w


def widen(rows, tile=8):
    """rows of pens / characters, widened tile by tile"""
    out = []
    for r in rows:
        o = []
        for x0 in range(0, len(r), tile):
            seg = r[x0:x0 + tile]
            for v, w in zip(seg, widths(len(seg))):
                o += [v] * w
        out.append(o)
    return out


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def playfield(pix, cw, ch, x_org=0, y_org=0, free=()):
    """pix: rows of pen characters (Spectrum resolution), cw x ch attribute
    cells (8 x 8, the first at x_org, y_org of the screen for the dither).
    Cells in free (cx, cy) take any two colours (the building, where the
    sprites hardly go).  -> (bitmap rows of 0/1, 1 = ink, attribute per cell)"""
    h, w = len(pix), len(pix[0])
    bits = [[0] * w for _ in range(h)]
    attrs = []
    for cy in range(ch):
        for cx in range(cw):
            if (cx, cy) in free:
                cols = [rgb_of(pix[y][x]) for y in range(cy * 8, cy * 8 + 8)
                        for x in range(cx * 8, cx * 8 + 8)]
                ink, paper, br = nearest_pair(cols)
                ci, cp = RGB[br][ink], RGB[br][paper]
                for y in range(cy * 8, cy * 8 + 8):
                    for x in range(cx * 8, cx * 8 + 8):
                        c = rgb_of(pix[y][x])
                        bits[y][x] = 1 if dist(c, ci) < dist(c, cp) else 0
                attrs.append((br << 6) | (paper << 3) | ink)
                continue
            cnt = {}
            for y in range(cy * 8, cy * 8 + 8):
                for x in range(cx * 8, cx * 8 + 8):
                    p = pix[y][x]
                    if p in SHADE:
                        continue
                    cnt[p] = cnt.get(p, 0) + 1
            # the paper: the colour most pixels have (shades do not vote)
            votes = {}
            for p, n in cnt.items():     # stone counts double: walls stay grey
                votes[PEN[p]] = votes.get(PEN[p], 0) + n * (2 if p == 'e' else 1)
            if votes:
                (pc, pb) = max(votes.items(), key=lambda kv: (kv[1], kv[0]))[0]
                ppen = max((p for p in cnt if PEN[p] == (pc, pb)), key=lambda p: cnt[p])
            else:
                pc, pb, ppen = GREEN, 0, 'g'
            plum = PEN_LUM[ppen]
            for y in range(cy * 8, cy * 8 + 8):
                for x in range(cx * 8, cx * 8 + 8):
                    p = pix[y][x]
                    if p in 'kn':
                        b = 1
                    elif PEN[p] == (pc, pb) and p not in SHADE:
                        b = 0
                    else:
                        v = SHADE_V if p in SHADE else PEN_LUM[p] / max(plum, 1)
                        if v >= 0.85:
                            b = 0
                        elif v <= 0.45:
                            b = 1
                        else:   # half-way: some ink, the darker the more
                            t = (0.85 - v) / 0.40 * 16
                            b = 1 if BAYER[(y + y_org) & 3][(x + x_org) & 3] < t else 0
                    bits[y][x] = b
            attrs.append((pb << 6) | (pc << 3) | BLACK)
    return bits, attrs


def rgb_of(p):
    c, b = PEN[p]
    return RGB[b][c]


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def nearest_pair(colours):
    """colours: list of (r, g, b) -> best (ink, paper, bright) for them"""
    best = None
    for br in (0, 1):
        pal = RGB[br]
        for i in range(8):
            for j in range(i, 8):
                err = 0
                for c in colours:
                    di = sum((a - b) ** 2 for a, b in zip(c, pal[i]))
                    dj = sum((a - b) ** 2 for a, b in zip(c, pal[j]))
                    err += min(di, dj)
                if best is None or err < best[0]:
                    best = (err, i, j, br)
    return best[1:]


def picture(img, levels=4):
    """img: a 256 x 192 RGB PIL image -> (6144 bitmap bytes in screen order,
    768 attributes).  Per cell the two colours (and brightness) that, mixed
    in steps of 1/levels, come nearest to its pixels; then an ordered
    (Bayer) dither of the two."""
    W, H = 256, 192
    px = [[img.getpixel((x, y)) for x in range(W)] for y in range(H)]
    bits = [[0] * W for _ in range(H)]
    attrs = []
    for cy in range(24):
        for cx in range(32):
            cols = [px[y][x] for y in range(cy * 8, cy * 8 + 8) for x in range(cx * 8, cx * 8 + 8)]
            best = None
            for br in (0, 1):
                pal = RGB[br]
                for i in range(8):
                    for j in range(i, 8):
                        mix = [tuple(pal[i][k] * t / levels + pal[j][k] * (levels - t) / levels
                                     for k in range(3)) for t in range(levels + 1)]
                        err = 0
                        for c in cols:
                            err += min(dist(c, m) for m in mix)
                        if best is None or err < best[0]:
                            best = (err, i, j, br, mix)
            _, ink, paper, br, mix = best
            for y in range(cy * 8, cy * 8 + 8):
                for x in range(cx * 8, cx * 8 + 8):
                    c = px[y][x]
                    t = min(range(levels + 1), key=lambda t: dist(c, mix[t]))
                    bits[y][x] = 1 if BAYER[y & 3][x & 3] < t * 16 // levels else 0
            attrs.append((br << 6) | (paper << 3) | ink)
    return screen_bytes(bits), attrs


def screen_addr(x, y):
    """offset into the 6144-byte bitmap of byte column x, line y"""
    return ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2) | x


def screen_bytes(bits):
    out = bytearray(6144)
    for y in range(192):
        for xb in range(32):
            v = 0
            for i in range(8):
                v = v << 1 | bits[y][xb * 8 + i]
            out[screen_addr(xb, y)] = v
    return out


def render(bitmap, attrs, scale=2):
    """a SCREEN$ (6144 + 768 bytes) -> PIL image"""
    from PIL import Image
    im = Image.new("RGB", (256, 192))
    for y in range(192):
        for x in range(256):
            a = attrs[(y // 8) * 32 + x // 8]
            br = (a >> 6) & 1
            on = bitmap[screen_addr(x // 8, y)] >> (7 - (x & 7)) & 1
            im.putpixel((x, y), RGB[br][a & 7] if on else RGB[br][(a >> 3) & 7])
    return im.resize((256 * scale, 192 * scale), Image.NEAREST)


def sprite(rows, halo=True, outline=True, double=False):
    """CPC sprite rows ('.' clear) -> (mask rows, ink rows) of 0/1 at the
    Spectrum's width: ink where the pen is dark, and round the edge of the
    shape (outline); the mask also takes a ring of paper round it (halo), so
    the sprite stands out from the background's ink."""
    if double:              # a Mode 0 pixel, two of ours
        wide = [[ch for ch in r for _ in (0, 1)] for r in rows]
    else:
        wide = widen([list(r) for r in rows], tile=len(rows[0]))
    h, w = len(wide), len(wide[0])
    shape = [[1 if wide[y][x] != '.' else 0 for x in range(w)] for y in range(h)]

    def on(y, x):
        return 0 <= y < h and 0 <= x < w and shape[y][x]
    ink = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if not shape[y][x]:
                continue
            p = wide[y][x]
            edge = not all(on(y + dy, x + dx) for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))
            ink[y][x] = 1 if p in DARK_PENS or (outline and edge) else 0
    if halo:
        mask = [[1 if any(on(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) else 0
                 for x in range(w)] for y in range(h)]
    else:
        mask = shape
    return mask, ink
