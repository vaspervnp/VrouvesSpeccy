"""Pixel art for LET'S GO FOR VROUVES (Mode 0, 16 pens).

Sprites are drawn as strings; one character per Mode 0 pixel.
'.' is transparent.
"""

# pen -> firmware colour
PALETTE_FW = [
    0,   # 0 k black
    9,   # 1 g green (grass)
    15,  # 2 o orange (dirt path, sacks, dakos)
    3,   # 3 r dark red/brown
    13,  # 4 e grey (stone)
    26,  # 5 W bright white
    2,   # 6 B bright blue
    11,  # 7 c sky blue
    24,  # 8 y bright yellow
    6,   # 9 R bright red
    18,  # 10 l bright green (toxic)
    16,  # 11 s pink (skin)
    10,  # 12 t cyan / dark teal (olive tree)
    22,  # 13 p pastel green
    12,  # 14 h khaki / olive drab
    0,   # 15 K black (sprite black; pen 0 is transparent in sprites)
]

CH = {'k': 0, 'g': 1, 'o': 2, 'r': 3, 'e': 4, 'W': 5, 'B': 6, 'c': 7,
      'y': 8, 'R': 9, 'l': 10, 's': 11, 't': 12, 'p': 13, 'h': 14, 'n': 15}

# firmware colour -> gate array value (with bit 6 set)
FW_TO_HW = [0x54, 0x44, 0x55, 0x5C, 0x58, 0x5D, 0x4C, 0x45, 0x4D, 0x56, 0x46,
            0x57, 0x5E, 0x40, 0x5F, 0x4E, 0x47, 0x4F, 0x52, 0x42, 0x53, 0x5A,
            0x59, 0x5B, 0x4A, 0x43, 0x4B]


def fw_rgb(n):
    g, r, b = n // 9, (n // 3) % 3, n % 3
    lv = (0, 128, 255)
    return (lv[r], lv[g], lv[b])


PEN_RGB = [fw_rgb(c) for c in PALETTE_FW]


def mirror(rows):
    return [r[::-1] for r in rows]


# ---------------------------------------------------------------- defenders
CRETAN = [
    "..kkkk..",
    ".kkkkkk.",
    "k.ssss.k",
    "..sksk..",
    "..kkkk..",
    ".kkkkk..",
    "skkkkrre",
    ".kkkks..",
    ".kkkkk..",
    ".rr.rr..",
    ".kk.kk..",
    ".kk.kk..",
]

YIAYIA = [
    "..kkk..r",
    ".kkkkk.r",
    ".kesek.r",
    ".ksksk.r",
    "..kkkksr",
    ".kkkkk.r",
    "kkkkkk.r",
    "kkkkkk.r",
    "lp.pl..r",
    "keeeek.r",
    "kllplk.r",
    ".kkkk...",
]

BRIDE = [
    "..WWWR..",
    ".WWWWWW.",
    ".WssssW.",
    ".WskskW.",
    ".WsRssW.",
    "..WWWW..",
    "WWWWWWse",
    "WWWWWW.k",
    ".WWWWW..",
    ".WWWWWW.",
    "WWWWWWWW",
    ".WWWWWW.",
]

PSSSST = [
    "ce....ec",
    "eke..eke",
    "..kyyk..",
    ".kyyyyk.",
    "kyyrryyk",
    "eyrrrrye",
    "eyrrrrye",
    "kyyrryyk",
    ".kyyyyk.",
    "..kyyk..",
    "eke..eke",
    "ce....ec",
]

CAULDRON = [
    "..p...l.",
    ".l..p...",
    "..kkkk..",
    ".keeeek.",
    "kellplek",
    "kelpllek",
    "kepllpek",
    "kellllek",
    ".keeeek.",
    "..kkkk..",
    ".RyRyR..",
    "..R.R...",
]

CAULDRON_CRUSHED = [
    "........",
    "........",
    "..kk....",
    ".keek...",
    "keeeekk.",
    "keekeek.",
    ".kekeek.",
    "..kkkllp",
    "....lplp",
    "...plll.",
    "....pl..",
    "........",
]

BAKER = [
    ".WWWW...",
    "WWWWWW..",
    "WWWWWW..",
    ".eeee...",
    ".ssss...",
    ".sksk...",
    ".skks.o.",
    "WWWWWoRo",
    "sWWWWsoo",
    ".WWWW...",
    ".WWWW...",
    ".kk.kk..",
]

# ---------------------------------------------------------------- enemies
DRONE_A = [
    "cc....cc",
    "cn....nc",
    ".n.nn.n.",
    "..nnnn..",
    ".nnllnn.",
    "nnlRRlnn",
    ".nnllnn.",
    "..nnnn..",
    ".n.nn.n.",
    "cn....nc",
    "cc....cc",
    "........",
]
DRONE_B = [
    ".c....c.",
    "cnc..cnc",
    ".n.nn.n.",
    "..nnnn..",
    ".nnllnn.",
    "nnlRRlnn",
    ".nnllnn.",
    "..nnnn..",
    ".n.nn.n.",
    "cnc..cnc",
    ".c....c.",
    "........",
]

GUARD_A = [
    "..kkkk..",
    ".kkkkkk.",
    ".keeeek.",
    ".kceeck.",
    "..keek..",
    "lkkkkkkl",
    "lknnnnkl",
    ".kkkkkke",
    ".kkkkk.e",
    ".kk.kk.e",
    ".kk..k.e",
    "kk...kee",
]
GUARD_B = [
    "..kkkk..",
    ".kkkkkk.",
    ".keeeek.",
    ".kceeck.",
    "..keek..",
    "lkkkkkkl",
    "lknnnnkl",
    ".kkkkkke",
    ".kkkkk.e",
    ".kk.kk.e",
    ".k..kk.e",
    ".k..kkee",
]

TANK_V_A = [
    "kehhhhek",
    "ekhhhhke",
    "kekkkkek",
    "ekkhhkke",
    "kekhhkek",
    "ekkhhkke",
    "kekkkkek",
    "ekhkkhke",
    "kehkkhek",
    "ekhkkhke",
    "...kk...",
    "...ee...",
]
TANK_V_B = [
    "ekhhhhke",
    "kehhhhek",
    "ekkkkkke",
    "kekhhkek",
    "ekkhhkke",
    "kekhhkek",
    "ekkkkkke",
    "kehkkhek",
    "ekhkkhke",
    "kehkkhek",
    "...kk...",
    "...ee...",
]
TANK_L_A = [
    "ekekekek",
    "kekekeke",
    "hhhhhhhh",
    "hhhkkkkh",
    "hhkhhhkh",
    "kkkhhhkh",
    "eekhhhkh",
    "hhkhhhkh",
    "hhhkkkkh",
    "hhhhhhhh",
    "ekekekek",
    "kekekeke",
]
TANK_L_B = [
    "kekekeke",
    "ekekekek",
    "hhhhhhhh",
    "hhhkkkkh",
    "hhkhhhkh",
    "kkkhhhkh",
    "eekhhhkh",
    "hhkhhhkh",
    "hhhkkkkh",
    "hhhhhhhh",
    "kekekeke",
    "ekekekek",
]

# ---------------------------------------------------------------- projectiles
BULLET = ["yW", "Wy"]
PISTOL = ["WW", "WW"]
PISTOL_CRIT = ["RR", "Ry"]
LASER = ["cW", "Wc", "cW", "Wc"]
DAKOS = [".oo.", "oRWo", "oWRo", ".oo."]

# ---------------------------------------------------------------- effects
SPARK = [
    "y..y",
    ".Wy.",
    ".yW.",
    "y..y",
]
SPARK_B = [
    ".y..",
    "yWWy",
    "yWWy",
    "..y.",
]
PUFF_A = [
    "........",
    "...p....",
    "..plp.p.",
    ".pllllp.",
    "pllpllp.",
    ".plllllp",
    "pllplllp",
    ".pllllp.",
    "..plplp.",
    "...p.p..",
    "........",
    "........",
]
PUFF_B = [
    "..p..p..",
    ".plp....",
    "pll.p.p.",
    ".p.lpllp",
    "pl.p.lp.",
    ".p.l.p.p",
    "lp.p..lp",
    ".p..l.p.",
    "p.l...p.",
    ".p..p..p",
    "........",
    "........",
]
BASH_A = [
    "........",
    "...y....",
    "y..y..y.",
    ".y.W.y..",
    "..yWy...",
    "yyWWWyy.",
    "..yWy...",
    ".y.W.y..",
    "y..y..y.",
    "...y....",
    "........",
    "........",
]
BASH_B = [
    "........",
    "........",
    "........",
    "...y....",
    "..yWy...",
    ".yWWWy..",
    "..yWy...",
    "...y....",
    "........",
    "........",
    "........",
    "........",
]
POOF_A = [
    "........",
    "........",
    "..e.....",
    ".eWe.e..",
    "eWWWeWe.",
    ".eWWWWe.",
    "eWWeWWe.",
    ".eeWWe..",
    "..e.e...",
    "........",
    "........",
    "........",
]
POOF_B = [
    "........",
    ".e...e..",
    "e.e.e.e.",
    ".e.W..e.",
    "..W.W...",
    "e..e..e.",
    ".W..W...",
    "e.e..e.e",
    ".e..e...",
    "e....e..",
    "........",
    "........",
]
BOOM_A = [
    "........",
    "..R..R..",
    ".RyRRyR.",
    "RyyWWyyR",
    "RyWWWWyR",
    ".RyWWyR.",
    "RyyWWyyR",
    ".RyyyyR.",
    "..RyyR..",
    ".R.RR.R.",
    "........",
    "........",
]
BOOM_B = [
    "R..R...R",
    ".R.y.R..",
    "..RyR..R",
    "R.yRy.R.",
    ".yR.Ry..",
    "y.R..R.y",
    ".yR.Ry..",
    "R.yRy.R.",
    "..RyR..R",
    ".R.y.R..",
    "R..R...R",
    "........",
]
ZAP_A = [
    "....c...",
    "...cW...",
    "..cWc...",
    ".cWWWc..",
    "...cWc..",
    "...Wc...",
    "..Wc....",
    "..c.....",
    "........",
    "........",
    "........",
    "........",
]

CURSOR_OK = [
    "WWW..WWW",
    "W......W",
    "W......W",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "W......W",
    "W......W",
    "WWW..WWW",
]
CURSOR_OK_B = [
    "yyy..yyy",
    "y......y",
    "y......y",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "y......y",
    "y......y",
    "yyy..yyy",
]
CURSOR_BAD = [
    "RRR..RRR",
    "R......R",
    "R......R",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "R......R",
    "R......R",
    "RRR..RRR",
]

FLAG_A = [
    "rBWBBBBB",
    "rWWWWWWW",
    "rBWBBBBB",
    "rWWWWWWW",
    "rBBBBBBB",
    "rWWWWWWW",
    "r.......",
    "r.......",
]
FLAG_B = [
    "r.BWBBBB",
    "rBWWWWWW",
    "rWBWBBBB",
    "rBWWWWWW",
    "rWBBBBBB",
    "r.WWWWWW",
    "r.......",
    "r.......",
]

SPRITES = [
    # name, rows
    ("spr_cretan", CRETAN),
    ("spr_yiayia", YIAYIA),
    ("spr_bride", BRIDE),
    ("spr_psssst", PSSSST),
    ("spr_cauldron", CAULDRON),
    ("spr_baker", BAKER),
    ("spr_cauldron_x", CAULDRON_CRUSHED),
    ("spr_drone_a", DRONE_A),
    ("spr_drone_b", DRONE_B),
    ("spr_guard_a", GUARD_A),
    ("spr_guard_b", GUARD_B),
    ("spr_tank_va", TANK_V_A),
    ("spr_tank_vb", TANK_V_B),
    ("spr_tank_la", TANK_L_A),
    ("spr_tank_lb", TANK_L_B),
    ("spr_bullet", BULLET),
    ("spr_pistol", PISTOL),
    ("spr_pistol_crit", PISTOL_CRIT),
    ("spr_laser", LASER),
    ("spr_dakos", DAKOS),
    ("spr_spark_a", SPARK),
    ("spr_spark_b", SPARK_B),
    ("spr_puff_a", PUFF_A),
    ("spr_puff_b", PUFF_B),
    ("spr_bash_a", BASH_A),
    ("spr_bash_b", BASH_B),
    ("spr_poof_a", POOF_A),
    ("spr_poof_b", POOF_B),
    ("spr_boom_a", BOOM_A),
    ("spr_boom_b", BOOM_B),
    ("spr_zap_a", ZAP_A),
    ("spr_cursor_ok", CURSOR_OK),
    ("spr_cursor_ok_b", CURSOR_OK_B),
    ("spr_cursor_bad", CURSOR_BAD),
    ("spr_flag_a", FLAG_A),
    ("spr_flag_b", FLAG_B),
]


# mirrored enemy sprites, built by the game into the unused tail of each 2K
# block of the #C000 screen (never displayed)
MIRRORS = [("spr_guard_a", 0xC7D0), ("spr_guard_b", 0xCFD0),
           ("spr_tank_la", 0xD7D0), ("spr_tank_lb", 0xDFD0)]
# per enemy type, per direction (down, left, right), two frames: (sprite, mirrored)
ENEMY_FRAMES = [
    ("spr_drone_a", DRONE_A, None), ("spr_drone_b", DRONE_B, None),
    ("spr_drone_a", DRONE_A, None), ("spr_drone_b", DRONE_B, None),
    ("spr_drone_a", DRONE_A, None), ("spr_drone_b", DRONE_B, None),
    ("spr_guard_a", GUARD_A, None), ("spr_guard_b", GUARD_B, None),
    ("spr_guard_a", GUARD_A, 0xC7D0), ("spr_guard_b", GUARD_B, 0xCFD0),
    ("spr_guard_a", GUARD_A, None), ("spr_guard_b", GUARD_B, None),
    ("spr_tank_va", TANK_V_A, None), ("spr_tank_vb", TANK_V_B, None),
    ("spr_tank_la", TANK_L_A, None), ("spr_tank_lb", TANK_L_B, None),
    ("spr_tank_la", TANK_L_A, 0xD7D0), ("spr_tank_lb", TANK_L_B, 0xDFD0),
]
