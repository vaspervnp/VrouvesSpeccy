#!/usr/bin/env python3
"""The pictures of the manuals (docs/img/): the title and the game screen in
English and Greek (the game itself, on tools/zxrun.py), the stages (from
tools/zxdata.py's previews: make first) and the defenders and invaders."""
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import art  # noqa: E402
import zxcolour as zc  # noqa: E402
import zxdata  # noqa: E402
import zxrun  # noqa: E402

IMG = os.path.join(ROOT, "docs", "img")
GREEN = (0, 215, 0)


def icon(name, path, inks, scale=6):
    """the sprite as in the game, on grass: its inks for the top and the bottom
    (black where green would be green on green)"""
    mask, ink = zxdata.sprite_mono(name, dict(art.SPRITES)[name])
    h, w = len(mask), len(mask[0])
    im = Image.new("RGB", (w + 4, h + 4), GREEN)
    for y in range(h):
        for x in range(w):
            if mask[y][x] and ink[y][x]:
                c = inks[0] if y + 2 < 8 else inks[1]
                im.putpixel((x + 2, y + 2), (0, 0, 0) if c == 4 else zc.RGB[0][c])
    im.resize((im.width * scale, im.height * scale), Image.NEAREST).save(path)


def screens():
    syms = zxrun.load_symbols(os.path.join(ROOT, "build", "vrouves.sym"))
    spec = zxrun.Spectrum(open(os.path.join(ROOT, "build", "vrouves.bin"), "rb").read(),
                          syms["BIN_START"], syms, "128")

    def tap(keys):
        spec.set_keys(keys)
        spec.run_frames(2)
        spec.set_keys([])
        spec.run_frames(12)

    def shot(name):
        spec.screenshot(os.path.join(IMG, name + ".png"))
    spec.run_frames(80)
    shot("title_en")
    tap(["l"])
    spec.run_frames(40)
    shot("title_gr")
    tap(["l"])
    tap(["space"])
    spec.run_frames(20)
    S = spec.resolve
    spec.poke(S("funds"), 250)
    for c, r, t in ((9, 2, 1), (11, 2, 4), (2, 2, 1), (5, 4, 4), (9, 6, 1), (12, 8, 1)):
        spec.poke(S("cur_c"), c)
        spec.poke(S("cur_r"), r)
        spec.poke(S("sel_type"), t)
        tap(["space"])
    spec.poke(S("cur_c"), 12)
    spec.poke(S("cur_r"), 4)
    tap(["n"])
    while spec.peek(S("wave_num")) < 3:
        if spec.peek(S("wave_state")) == 0:
            tap(["n"])
        spec.run_frames(25)
        if spec.peek(S("hp")) < 60:
            spec.poke(S("hp"), 100)
    spec.run_frames(150)
    shot("game_en")
    tap(["l"])
    spec.run_frames(30)
    shot("game_gr")


def main():
    os.makedirs(IMG, exist_ok=True)
    # the inks of game.asm's tower_inks and enemy_inks
    for name, spr, inks in (("cretan", "spr_cretan", (2, 1)), ("psssst", "spr_psssst", (5, 6)),
                            ("yiayia", "spr_yiayia", (7, 1)), ("bride", "spr_bride", (6, 7)),
                            ("baker", "spr_baker", (7, 6)), ("cauldron", "spr_cauldron", (4, 2)),
                            ("drone", "spr_drone_a", (3, 3)), ("guard", "spr_guard_a", (1, 1)),
                            ("tank", "spr_tank_va", (2, 2))):
        icon(spr, os.path.join(IMG, name + ".png"), inks)
    for k in range(1, 8):       # the playfield of the previews (3x)
        im = Image.open(os.path.join(ROOT, "build", "preview", "stage%d.png" % k))
        im.crop((24, 24, 24 + 720, 24 + 480)).save(os.path.join(IMG, "stage%d.png" % k))
    screens()
    print("docs/img: written")


if __name__ == "__main__":
    main()
