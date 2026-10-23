#!/usr/bin/env python3
"""Generates the Spectrum data of LET'S GO FOR VROUVES from the shared world
(tools/world.py, art.py, font.py, texts.py: the CPC version's):

  build/gen/data.asm   the font, every text (English and Greek, byte-pair
                       packed), the sprites, the tiles of every stage, per
                       stage its packed record (maps, sacks, flag, paths,
                       waves, texts) and attributes, the title page's scene,
                       the music and the sound effects
  build/loading.scr    the loading picture (assets/vrouves.jpeg + the title)
  build/ending.scr     the ending (assets/ending_sceneFinal.png)
  build/preview/*.png  how it all looks on the Spectrum

A map cell is 16 x 16 pixels, 2 x 2 attribute cells: the playfield, 15 x 10
cells (tools/zxworld.py), is 240 x 160, at x = 8, y = 8 of the screen.  See
zxcolour.py for the colours.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, os.path.dirname(__file__))
import art  # noqa: E402
import font  # noqa: E402
import lz  # noqa: E402
import texts  # noqa: E402
import world  # noqa: E402
import zxcolour as zc  # noqa: E402
import zxworld as zw  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
GEN = os.path.join(BUILD, "gen")
PREVIEW = os.path.join(BUILD, "preview")

MW, MH = zw.MW, zw.MH
CW = zw.CS                      # a cell, Spectrum pixels (both ways)
PF_X, PF_Y = 8, 8               # the playfield on the screen
ACOLS, AROWS = 30, 20           # its attribute cells


def db(data, per=16):
    return ["        db " + ",".join("#%02X" % (v & 255) for v in data[i:i + per])
            for i in range(0, len(data), per)]


# ------------------------------------------------------------------ the font
def font_data():
    A = ["; the 3x6 font: 6 rows a glyph, the pixels in bits 7-5"]
    A.append("NUM_GLYPHS equ %d" % len(font.GLYPHS))
    for nm, ch in (("SPACE", " "), ("SLASH", "/"), ("0", "0"), ("PLUS", "+"), ("MINUS", "-"),
                   ("PCT", "%"), ("2", "2"), ("5", "5"), ("A", "A"), ("LEFT", "←"),
                   ("RIGHT", "→"), ("UP", "↑"), ("DOWN", "↓")):
        A.append("G_%s equ %d" % (nm, font.glyph_index(ch)))
    A.append("GLYPH_0 equ G_0")
    A.append("GLYPH_SLASH equ G_SLASH")
    A.append("font:")
    d = []
    for i in range(len(font.GLYPHS)):
        d += [r << 5 for r in font.glyph_rows(i)]
    A += db(d, 12)
    return A


# ------------------------------------------------------------------ texts
# the Spectrum's keys where the CPC's differ
ZX_TEXT = {
    "B_PAUSE2": ("H: CONTINUE    BREAK: QUIT", "H: ΣΥΝΕΧΕΙΑ    BREAK: ΕΞΟΔΟΣ"),
    "T_CTRL": ("MOVE\n\nBUILD\n\nNEXT WAVE\n\nMUSIC",
               "ΚΙΝΗΣΗ\n\nΧΤΙΣΙΜΟ\n\nΝΕΟ ΚΥΜΑ\n\nΜΟΥΣΙΚΗ"),
    "T_CTRL2": ("CHOOSE\n\nSELL\n\nPAUSE\n\nGREEK",
                "ΕΠΙΛΟΓΗ\n\nΠΟΥΛΗΜΑ\n\nΠΑΥΣΗ\n\nΑΓΓΛΙΚΑ"),
}
EXTRA_STRINGS = [
    ("T_KEYS", "←↑↓→ QAOP\n\nSPACE\n\nN\n\nM", None),
    ("T_KEYS2", "1-6\n\nS\n\nH\n\nL", None),
    ("T_HSHDR", "HIGH SCORES", "ΚΑΛΥΤΕΡΑ ΣΚΟΡ"),
    ("T_NEWHS", "NEW HIGH SCORE!", "ΝΕΟ ΡΕΚΟΡ!"),
    ("T_NAME", "ENTER YOUR NAME", "ΓΡΑΨΕ ΤΟ ΟΝΟΜΑ ΣΟΥ"),
    ("T_NAMEKEYS", "UP/DOWN: LETTER    FIRE: NEXT", "ΠΑΝΩ/ΚΑΤΩ: ΓΡΑΜΜΑ   FIRE: ΕΠΟΜΕΝΟ"),
    ("T_DIF0", "'D' DIFFICULTY: MEDIUM - 3 LIVES", "'D' ΔΥΣΚΟΛΙΑ: ΜΕΤΡΙΑ - 3 ΖΩΕΣ"),
    ("T_DIF1", "'D' DIFFICULTY: HARD - 2 LIVES", "'D' ΔΥΣΚΟΛΙΑ: ΔΥΣΚΟΛΗ - 2 ΖΩΕΣ"),
    ("T_DIF2", "'D' DIFFICULTY: HARDEST - NO LIVES", "'D' ΔΥΣΚΟΛΙΑ: ΠΟΛΥ ΔΥΣΚΟΛΗ - 0 ΖΩΕΣ"),
    ("T_DIF3", "'D' DIFFICULTY: EASY - 4 LIVES", "'D' ΔΥΣΚΟΛΙΑ: ΕΥΚΟΛΗ - 4 ΖΩΕΣ"),
    ("T_ENDLOAD", "THE ENDING IS ON THE TAPE: PRESS PLAY\n(SPACE: SKIP IT)",
                  "ΤΟ ΤΕΛΟΣ ΕΙΝΑΙ ΣΤΗΝ ΚΑΣΕΤΑ: ΠΑΤΗΣΤΕ PLAY\n(SPACE: ΠΑΡΑΛΕΙΨΗ)"),
    ("S_SCORE", "SCORE ", "ΣΚΟΡ "),
    ("S_LIVES", "  LIVES ", "  ΖΩΕΣ "),
]
STORY_WIDTH = 60


def enc_text(s):
    out = []
    for n, line in enumerate(s.split("\n")):
        if n:
            out.append(0xFE)
        assert len(line) <= 64, line
        out += font.encode(line)
    return out + [0xFF]


def text_data():
    strings = []
    for sid, en, gr in texts.STRINGS:
        en, gr = ZX_TEXT.get(sid, (en, gr))
        strings.append((sid, en, gr))
    strings.append(("T_STORY", texts.wrap(texts.STORY_EN, STORY_WIDTH),
                    texts.wrap(texts.STORY_GR, STORY_WIDTH)))
    strings += EXTRA_STRINGS
    ids = [sid for sid, _, _ in strings] + list(world.STAGE_STRINGS)
    items, alias, seen = [], [], {}
    for sid, en, gr in strings:
        for lang, t in (("e", en), ("g", gr if gr is not None else en)):
            lbl = "s%s_%s" % (lang, sid)
            d = tuple(enc_text(t))
            if d in seen:
                alias.append((lbl, seen[d]))
            else:
                seen[d] = lbl
                items.append([lbl, list(d)])
    stage_enc = {}
    for k, st in enumerate(world.STAGES):
        for sid in world.STAGE_STRINGS:
            for lang in (0, 1):
                items.append([("stage", k, sid, lang), enc_text(st.strings[sid][lang])])
    NG = len(font.GLYPHS)
    raw = sum(len(d) for _, d in items)
    pairs = []
    code = NG
    while code < 0xFE:
        counts = {}
        for _, d in items:
            for a, b in zip(d, d[1:]):
                if a < 0xFE and b < 0xFE:
                    counts[(a, b)] = counts.get((a, b), 0) + 1
        if not counts:
            break
        best, n = max(counts.items(), key=lambda kv: kv[1])
        if n < 3:
            break
        pairs.append(best)
        for it in items:
            d, out, i = it[1], [], 0
            while i < len(d):
                if i + 1 < len(d) and (d[i], d[i + 1]) == best:
                    out.append(code)
                    i += 2
                else:
                    out.append(d[i])
                    i += 1
            it[1] = out
        code += 1
    T = []
    for i, sid in enumerate(ids):
        T.append("%s equ %d" % (sid, i))
    T.append("pair_table:")
    T += db([v for p in pairs for v in p])
    T.append("strtab_en:")
    T += ["        dw se_" + sid for sid in ids]
    T.append("strtab_gr:")
    T += ["        dw sg_" + sid for sid in ids]
    for a, b in alias:
        T.append("%s equ %s" % (a, b))
    for lbl, d in items:
        if isinstance(lbl, tuple):
            stage_enc[lbl[1:]] = d
        else:
            T.append(lbl + ":")
            T += db(d, 20)
    T.append("name_chars:")
    T += db(font.encode(texts.NAME_CHARS))
    T.append("NAME_NCHARS equ %d" % len(texts.NAME_CHARS))
    T.append("hs_default:            ; 8 x (3 glyphs, score lo, hi)")
    hs = []
    for name, pts in texts.HISCORES:
        hs += font.encode(name) + [pts & 255, pts >> 8]
    T += db(hs, 20)
    packed = sum(len(d) for lbl, d in items if not isinstance(lbl, tuple)) + 2 * len(pairs)
    print("text: %d bytes raw, %d packed (%d pairs)" % (raw, packed, len(pairs)))
    return T, ids, stage_enc


# ------------------------------------------------------------------ sprites
CURSOR_OK = [          # Spectrum pixels: the cursor where a defender can go
    "####......####",
    "#............#",
    "#............#",
    "#............#",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "#............#",
    "#............#",
    "#............#",
    "####......####",
]
CURSOR_OK_B = [         # the other frame of the blinking cursor
    "..............",
    ".####....####.",
    ".#..........#.",
    ".#..........#.",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    ".#..........#.",
    ".#..........#.",
    ".####....####.",
    "..............",
]
CURSOR_BAD = [          # where nothing can be built
    "####......####",
    "#............#",
    "#.#........#.#",
    "...#......#...",
    "....#....#....",
    ".....#..#.....",
    "......##......",
    "......##......",
    ".....#..#.....",
    "....#....#....",
    "...#......#...",
    "#.#........#.#",
    "#............#",
    "####......####",
]
CURSOR_X, CURSOR_Y = 1, 1       # its place in the cell
SMALL = {"spr_bullet", "spr_pistol", "spr_pistol_crit", "spr_laser", "spr_dakos",
         "spr_spark_a", "spr_spark_b"}
NO_HALO = {"spr_flag_a", "spr_flag_b", "spr_puff_a", "spr_puff_b", "spr_poof_b", "spr_boom_b"}


def zx_rows(rows):
    """'#' = ink rows (Spectrum pixels) -> (mask, ink) with a halo, the
    rows padded to 16 x 16 with the cursor's offset"""
    rows = ["." * CURSOR_X + r + "." * (16 - CURSOR_X - len(r)) for r in rows]
    rows = ["." * 16] * CURSOR_Y + rows + ["." * 16] * (16 - CURSOR_Y - len(rows))
    h, w = len(rows), len(rows[0])
    ink = [[1 if rows[y][x] == '#' else 0 for x in range(w)] for y in range(h)]
    mask = [[1 if any(0 <= y + dy < h and 0 <= x + dx < w and ink[y + dy][x + dx]
                      for dy in (-1, 0, 1) for dx in (-1, 0, 1)) else 0
             for x in range(w)] for y in range(h)]
    return mask, ink


def sprite_mono(name, rows):
    if name == "spr_cursor_bad":
        return zx_rows(CURSOR_BAD)
    if name == "spr_cursor_ok":
        return zx_rows(CURSOR_OK)
    if name == "spr_cursor_ok_b":
        return zx_rows(CURSOR_OK_B)
    if name in SMALL:       # shots and sparks: all ink
        mask, ink = zc.sprite(rows, halo=True, outline=True, double=True)
        ink = [[1 if c != '.' else 0 for c in r for _ in (0, 1)] for r in rows]
        return mask, ink
    return zc.sprite(rows, halo=name not in NO_HALO, double=True)


def bits_to_bytes(row, nb):
    out = []
    for b in range(nb):
        v = 0
        for i in range(8):
            x = b * 8 + i
            v = v << 1 | (row[x] if x < len(row) else 0)
        out.append(v)
    return out


def sprite_bytes(mask, ink):
    """w (bytes), h, then per row: w bytes of shape (1 = the sprite's, the
    mask inverted), w bytes of ink"""
    h, w = len(mask), len(mask[0])
    nb = (w + 7) // 8
    out = [nb, h]
    for y in range(h):
        out += bits_to_bytes(mask[y], nb) + bits_to_bytes(ink[y], nb)
    return out


def sprite_data():
    A = ["; sprites: w, h, rows of (shape bytes, ink bytes); drawn at any pixel"]
    mono = {}
    for name, rows in art.SPRITES:
        mono[name] = sprite_mono(name, rows)
    for name, rows in art.SPRITES:
        A.append(name + ":")
        A += db(sprite_bytes(*mono[name]))
    # the mirrored enemy frames (walking left)
    for name in ("spr_guard_a", "spr_guard_b", "spr_tank_la", "spr_tank_lb"):
        m, i = mono[name]
        A.append(name + "_m:")
        A += db(sprite_bytes([r[::-1] for r in m], [r[::-1] for r in i]))
    A.append("enemy_sprites:      ; type (drone, guard, tank) x direction (down, left, right) x frame")
    for name, rows, mirrored in art.ENEMY_FRAMES:
        A.append("        dw %s%s" % (name, "_m" if mirrored else ""))
    return A, mono


# ------------------------------------------------------------------ stages
class TileSet:
    """Spectrum tiles (16 x 16 bits, 32 bytes) shared by every stage"""

    def __init__(self):
        self.index, self.tiles = {}, []

    def add(self, bits, c, r):
        t = tuple(tuple(bits[r * CW + y][c * CW:c * CW + CW]) for y in range(CW))
        if t not in self.index:
            self.index[t] = len(self.tiles)
            self.tiles.append(t)
        return self.index[t]

    def bytes(self):
        out = []
        for t in self.tiles:
            for row in t:
                out += bits_to_bytes(row, 2)
        return out


def path_data(wps):
    """the path as the game walks it: x (4 pixels a unit), y, the step in
    the cell (x moves every fourth), steps left, then (dx, dy, steps)..."""
    segs = []
    for (a_, b_) in zip(wps, wps[1:]):
        (c0, r0), (c1, r1) = a_, b_
        dc, dr = c1 - c0, r1 - r0
        assert dc == 0 or dr == 0 or abs(dc) == abs(dr)
        n = CW * max(abs(dc), abs(dr))
        assert n < 256
        segs.append(((dc > 0) - (dc < 0), (dr > 0) - (dr < 0), n))
    c0, r0 = wps[0]
    data = [c0 * 4, r0 * CW, 0, segs[0][2]]
    for (dx, dy, n) in segs:
        data += [dx & 0xFF, dy & 0xFF, n]
    return data + [0, 0, 0]


def path_steps(wps):
    """pixel positions along a path (the previews)"""
    pts = []
    for (a_, b_) in zip(wps, wps[1:]):
        (c0, r0), (c1, r1) = a_, b_
        n = CW * max(abs(c1 - c0), abs(r1 - r0))
        for k in range(n):
            pts.append((round((c0 + (c1 - c0) * k / n) * CW), round((r0 + (r1 - r0) * k / n) * CW)))
    return pts


def unlock_data(k, ids):
    if k < len(world.UNLOCKS):
        types, l1, l2 = world.UNLOCKS[k]
        ann = [ids.index(l1), ids.index(l2)]
    else:
        types, ann = {1, 2, 3, 4, 5, 6}, [0xFF, 0xFF]
    return [sum(1 << (t - 1) for t in types)] + ann + [world.STAGES[k].toughness]


def stage_data(ids, stage_enc, ts):
    built = []
    for k, st in enumerate(zw.STAGES):
        full, grid = zw.render(k, True)
        empty, _ = zw.render(k, False)
        bits, attrs = zc.playfield(full, ACOLS, AROWS, PF_X, PF_Y, zw.free_cells(k))
        ebits, _ = zc.playfield(empty, ACOLS, AROWS, PF_X, PF_Y, zw.free_cells(k))
        local, tlist, tmap, cmap = {}, [], [], []

        def lid(g):
            if g not in local:
                local[g] = len(tlist)
                tlist.append(g)
            return local[g]
        for r in range(MH):
            for c in range(MW):
                tmap.append(lid(ts.add(bits, c, r)))
                t = grid[r][c]
                cmap.append(0 if t in '.F' else 1 if t == '#' else 3 if t == 'K' else 2)
        sacks = []
        for (c, r) in st.sacks:
            f = tmap[r * MW + c]
            e = lid(ts.add(ebits, c, r))
            assert f != e, (k, c, r)
            sacks += [c, r, f, e]
        assert len(tlist) < 256
        waves = getattr(world, st.waves)
        assert len(waves) == len(world.WAVES1)
        built.append(dict(tmap=tmap, cmap=cmap, sacks=sacks, flag=zw.flag_xy(k), tlist=tlist,
                          pg=path_data(st.ground), pa=path_data(st.air), attrs=attrs,
                          waves=[[v for (t, n, iv) in w for v in (t, n, iv)] + [0] for w in waves],
                          unlock=unlock_data(k, ids), grid=grid, bits=bits))
    # the record of a stage, unpacked to STAGE_AREA: every section as big as
    # the biggest stage's
    sections = [("tilemap", MW * MH), ("cellmap", MW * MH), ("sack_cells", 20), ("stage_flag", 2),
                ("stage_unlock", 4),
                ("path_ground", max(len(b["pg"]) for b in built)),
                ("path_air", max(len(b["pa"]) for b in built)),
                ("wave_table", len(world.WAVES1)),
                ("wave_data", max(sum(len(w) for w in b["waves"]) for b in built))]
    for sid in world.STAGE_STRINGS:
        for lang in (0, 1):
            sections.append(("s%s_%s" % ("eg"[lang], sid),
                             max(len(stage_enc[(k, sid, lang)]) for k in range(len(built)))))
    off, o = {}, 0
    for name, n in sections:
        off[name] = o
        o += n
    S = ["NUM_STAGES equ %d" % len(built), "NUM_SACKS equ 5",
         "NUM_WAVES equ %d" % len(world.WAVES1), "STAGE_SIZE equ %d" % o]
    for name, n in sections:
        S.append("%s equ STAGE_AREA+%d" % (name, off[name]))
    S.append("stage_tab:          ; per stage: record, attributes, tile list")
    for k in range(len(built)):
        S.append("        dw st%d_rec,st%d_attr,st%d_tiles" % (k, k, k))
    total = 0
    for k, b in enumerate(built):
        img = bytearray(o)

        def put(name, data):
            assert len(data) <= dict(sections)[name], name
            img[off[name]:off[name] + len(data)] = bytes(v & 0xFF for v in data)
        put("tilemap", b["tmap"])
        put("cellmap", b["cmap"])
        put("sack_cells", b["sacks"])
        put("stage_flag", list(b["flag"])[::-1])     # y, x (pixels): LD DE,(nn) gives D = x
        put("stage_unlock", b["unlock"])
        put("path_ground", b["pg"])
        put("path_air", b["pa"])
        ptrs, wd = [], []
        for w in b["waves"]:
            ptrs.append(len(wd))
            wd += w
        put("wave_table", ptrs)
        put("wave_data", wd)
        for sid in world.STAGE_STRINGS:
            for lang in (0, 1):
                put("s%s_%s" % ("eg"[lang], sid), stage_enc[(k, sid, lang)])
        rec = lz.pack(img)
        att = lz.pack(bytes(b["attrs"]))
        S.append("st%d_rec:" % k)
        S += db(rec)
        S.append("st%d_attr:" % k)
        S += db(att)
        S.append("st%d_tiles:          ; %d tiles" % (k, len(b["tlist"])))
        S += ["        dw " + ",".join("tiles+%d" % (32 * g) for g in b["tlist"][i:i + 8])
              for i in range(0, len(b["tlist"]), 8)]
        total += len(rec) + len(att) + 2 * len(b["tlist"])
    print("stages: %d bytes of records, attributes and tile lists" % total)
    return S, built


# the first title page's scene: the bottom half of the first stage
TSCENE_R0 = 5


def title_scene(ts, built):
    bits, attrs = built[0]["bits"], built[0]["attrs"]
    rows = MH - TSCENE_R0
    local, tlist, tmap = {}, [], []
    for r in range(TSCENE_R0, MH):
        for c in range(MW):
            g = ts.add(bits, c, r)
            if g not in local:
                local[g] = len(tlist)
                tlist.append(g)
            tmap.append(local[g])
    att = attrs[TSCENE_R0 * 2 * ACOLS:]
    A = ["TSCENE_ROWS equ %d" % rows, "tscene:             ; tile map, then attributes (packed)"]
    A += db(lz.pack(bytes(tmap + att)))
    A.append("tscene_tiles:")
    A += ["        dw " + ",".join("tiles+%d" % (32 * g) for g in tlist[i:i + 8])
          for i in range(0, len(tlist), 8)]
    return A


# ------------------------------------------------------------------ sound
AYF = 1.7734            # the Spectrum's AY clock / the CPC's


def sound_data():
    A = []
    mel = world.parse_mel(world.MEL_A) + world.parse_mel(world.MEL_A) + world.parse_mel(world.MEL_B)
    bass = world.bass_line()
    durs = sorted({d for _, d in mel + bass})
    assert len(durs) <= 15
    A.append("music_durs:")
    A += db(durs)

    def period(n):
        return min(4095, int(round(world.note_period(n) * AYF)))

    def chan(name, seq):
        notes = sorted({n for n, _ in seq if n != 'R'}, key=world.note_period, reverse=True)
        assert len(notes) <= 14, notes
        A.append("%s_notes:" % name)
        A.append("        dw " + ",".join(str(v) for v in [0] + [period(n) for n in notes]))
        out = []
        for n, d in seq:
            out.append(((0 if n == 'R' else notes.index(n) + 1) << 4) | durs.index(d))
        A.append("%s:" % name)
        A.extend(db(out + [0xFF]))
    assert sum(d for _, d in mel) == sum(d for _, d in bass)
    chan("music_a", mel)
    chan("music_b", bass)
    names = list(world.SFX.keys())
    for i, n in enumerate(names):
        A.append("%s equ %d" % (n, i))
    A.append("sfx_table:")
    A += ["        dw sfx_%d" % i for i in range(len(names))]
    A.append("sfx_prio:")
    A += db([world.SFX_PRIO[n] for n in names])
    for i, n in enumerate(names):
        A.append("sfx_%d:               ; %s: volume, noise, tone period" % (i, n))
        data = []
        for (p, nz, v) in world.SFX[n]:
            p = min(4095, int(round(p * AYF)))
            nz = min(31, int(round(nz * AYF)))
            data += [v, nz, p & 0xFF, p >> 8]
        A += db(data + [0xFF])
    return A


# ------------------------------------------------------------------ pictures
def title_text(px, text, y0, colour, shadow, scale=2):
    """the title in the game's font, scale x scale pixels a dot, with a shadow"""
    w = 4 * len(text) * scale
    x0 = (256 - w) // 2
    for dx, dy, col in ((scale, scale, shadow), (0, 0, colour)):
        for k, ch in enumerate(text):
            g = font.glyph_rows(font.glyph_index(ch))
            for j, bits in enumerate(g):
                for i in range(3):
                    if bits & (4 >> i):
                        for yy in range(scale):
                            for xx in range(scale):
                                px.putpixel((x0 + (4 * k + i) * scale + xx + dx,
                                             y0 + j * scale + yy + dy), col)


def load_fit(path, w, h):
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    s = max(w / sw, h / sh)
    im = im.resize((int(sw * s + 0.5), int(sh * s + 0.5)), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def loading_screen():
    im = load_fit(os.path.join(ROOT, "assets", "vrouves.jpeg"), 256, 192)
    im = ImageEnhance.Color(im).enhance(1.5)
    im = ImageEnhance.Contrast(im).enhance(1.2)
    bmp, attrs = zc.picture(im)
    # the title on a band of black, in bright yellow
    shot = Image.new("RGB", (256, 192))
    title_text(shot, "LET'S GO FOR VROUVES", 6, (255, 255, 0), (215, 0, 0))
    for cy in range(0, 3):
        for cx in range(32):
            attrs[cy * 32 + cx] = 0x40 | 6     # bright yellow on black
            for y in range(cy * 8, cy * 8 + 8):
                v = 0
                for i in range(8):
                    v = v << 1 | (1 if shot.getpixel((cx * 8 + i, y)) == (255, 255, 0) else 0)
                bmp[zc.screen_addr(cx, y)] = v
    for cx in range(32):            # the shadow, in red
        attrs[1 * 32 + cx] = 0x40 | 6
    return bytes(bmp) + bytes(attrs)


def ending_screen():
    im = load_fit(os.path.join(ROOT, "assets", "ending_scene.png"), 256, 192)
    im = ImageEnhance.Color(im).enhance(1.4)
    bmp, attrs = zc.picture(im)
    return bytes(bmp) + bytes(attrs)


# ------------------------------------------------------------------ previews
def preview_stage(k, b, mono, path):
    im = Image.new("RGB", (256, 192))
    bits, attrs = b["bits"], b["attrs"]
    PH = MH * CW
    for y in range(PH):
        for x in range(MW * CW):
            a = attrs[(y // 8) * ACOLS + x // 8]
            br = a >> 6 & 1
            col = zc.RGB[br][a & 7] if bits[y][x] else zc.RGB[br][a >> 3 & 7]
            im.putpixel((PF_X + x, PF_Y + y), col)

    def put(name, x, y):
        mask, ink = mono[name]
        for j in range(len(mask)):
            for i in range(len(mask[0])):
                if mask[j][i] and 0 <= x + i < MW * CW and 0 <= y + j < PH:
                    a = attrs[((y + j) // 8) * ACOLS + (x + i) // 8]
                    br = a >> 6 & 1
                    im.putpixel((PF_X + x + i, PF_Y + y + j),
                                zc.RGB[br][a & 7] if ink[j][i] else zc.RGB[br][a >> 3 & 7])
    gp = path_steps(zw.STAGES[k].ground)
    ap = path_steps(zw.STAGES[k].air)
    for name, (x, y) in (("spr_guard_a", gp[len(gp) // 5]), ("spr_tank_la", gp[len(gp) // 2]),
                         ("spr_drone_a", ap[len(ap) // 2]), ("spr_guard_b", gp[3 * len(gp) // 4])):
        put(name, x, y + 2)
    placed = 0
    for r in range(MH):
        for c in range(MW):
            if b["cmap"][r * MW + c] == 0 and (c * 7 + r * 3) % 11 == 0 and placed < 6:
                put(("spr_cretan", "spr_yiayia", "spr_bride", "spr_psssst", "spr_cauldron",
                     "spr_baker")[placed], c * CW, r * CW + 2)
                placed += 1
    fx, fy = b["flag"]
    put("spr_flag_a", fx, fy)
    put("spr_cursor_ok", 7 * CW, 3 * CW)
    put("spr_cursor_bad", 8 * CW, 3 * CW)
    im.resize((768, 576), Image.NEAREST).save(path)


def main():
    os.makedirs(GEN, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    T, ids, stage_enc = text_data()
    ts = TileSet()
    S, built = stage_data(ids, stage_enc, ts)
    TS = title_scene(ts, built)
    SP, mono = sprite_data()
    tb = ts.bytes()
    print("tiles: %d, %d bytes" % (len(ts.tiles), len(tb)))
    A = ["; generated by tools/zxdata.py - do not edit", ""]
    # what is read every frame (the sprites) last: above #8000, out of the
    # memory the ULA slows down
    A += font_data() + [""] + T + [""]
    A += ["NUM_TILES equ %d" % len(ts.tiles), "tiles:"] + db(tb, 16) + [""]
    A += S + [""] + TS + [""] + sound_data() + [""] + SP
    with open(os.path.join(GEN, "data.asm"), "w") as f:
        f.write("\n".join(A) + "\n")
    for k, b in enumerate(built):
        preview_stage(k, b, mono, os.path.join(PREVIEW, "stage%d.png" % (k + 1)))
    if "--pictures" in sys.argv or not os.path.exists(os.path.join(BUILD, "loading.scr")):
        for name, scr in (("loading", loading_screen()), ("ending", ending_screen())):
            with open(os.path.join(BUILD, name + ".scr"), "wb") as f:
                f.write(scr)
            zc.render(scr[:6144], scr[6144:], 2).save(os.path.join(PREVIEW, name + ".png"))


if __name__ == "__main__":
    main()
