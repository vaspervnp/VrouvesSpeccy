#!/usr/bin/env python3
"""The Lyra player and the last three stages, on the headless Spectrum: he
hits walkers and drones (armour counting) and slows only the drones, the
neighbour pairs, the second road of stage 9, no Bride in stage 10.  Builds its
own binaries (rasm -DSTART_STAGE=n) into build/debug.bin, like make debug.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import zxrun  # noqa: E402

E_TYPE, E_HP, E_MAXHP, E_X, E_SLOW, E_GEN = 0, 1, 2, 8, 10, 12
LYRA, YIAYIA, BRIDE = 7, 2, 3


def check(what, got, want):
    print("%-44s %s" % (what, got))
    assert got == want, (what, got, want)


class Game:
    def __init__(self, stage):
        sym = os.path.join(ROOT, 'build', 'debug.sym')
        subprocess.run(['rasm', 'src/main.asm', '-DSTART_STAGE=%d' % stage, '-os', sym, '-s', '-sa'],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        syms = zxrun.load_symbols(sym)
        self.spec = zxrun.Spectrum(open(os.path.join(ROOT, 'build', 'debug.bin'), 'rb').read(),
                                   syms['BIN_START'], syms, '128')
        self.spec.run_frames(60)
        self.tap('space')
        self.spec.run_frames(30)
        self.spec.poke(self.s('funds') + 1, 8)

    def s(self, name):
        return self.spec.resolve(name)

    def peek(self, name, off=0):
        return self.spec.peek(self.s(name) + off)

    def tap(self, key):
        self.spec.set_keys([key])
        self.spec.run_frames(2)
        self.spec.set_keys([])
        self.spec.run_frames(12)

    def build(self, t, c, r):
        self.spec.poke(self.s('cur_c'), c)
        self.spec.poke(self.s('cur_r'), r)
        self.spec.poke(self.s('sel_type'), t)
        self.tap('space')

    def towers(self):
        out = {}
        for i in range(32):
            t = [self.peek('towers', 8 * i + k) for k in range(8)]
            if t[0]:
                out[(t[1], t[2])] = t
        return out

    def enemies(self):
        return [[self.peek('enemies', 16 * i + k) for k in range(16)] for i in range(16)]


def stage8():
    g = Game(8)
    check("stage 8: the defenders", g.peek('stage_unlock'), 0x7f)
    g.tap('7')
    check("  key 7 chooses him", g.peek('sel_type'), LYRA)
    g.build(YIAYIA, 10, 8)
    g.build(LYRA, 11, 8)
    t = g.towers()
    check("  by a Yiayia: +50%", t[(11, 8)][7], 24)
    check("  the Yiayia gets nothing from him", t[(10, 8)][7], 0)
    g.build(LYRA, 11, 9)
    t = g.towers()
    check("  two side by side: -50% for both", (t[(11, 8)][7], t[(11, 9)][7]), (8, 8))
    g.build(LYRA, 9, 4)         # under the drones' way; the first wave is all drones
    g.tap('n')
    drone_hit = drone_slow = note = False
    for _ in range(1500):
        g.spec.run_frames(1)
        for e in g.enemies():
            if e[E_TYPE] == 1 and e[E_HP] < e[E_MAXHP]:
                drone_hit = True
                drone_slow = drone_slow or e[E_SLOW] > 0
        for i in range(8):
            if g.peek('fxs', 4 * i) == 7:
                note = True
        if drone_hit and drone_slow and note:
            break
    check("  drones hit", drone_hit, True)
    check("  and slowed", drone_slow, True)
    check("  notes over them", note, True)


def stage9():
    g = Game(9)
    check("stage 9: a second road", g.peek('stage_unlock', 4) > 0, True)
    g.tap('n')
    starts = {}
    for _ in range(3000):
        g.spec.run_frames(1)
        for e in g.enemies():
            if e[E_TYPE] == 2:
                starts.setdefault(e[E_GEN], e[E_X])
        if len(starts) >= 4:
            break
    left = {x < 30 for x in starts.values()}
    check("  walkers on both", left, {True, False})
    # they reach the press: run on with no defenders
    hp = g.peek('hp')
    for _ in range(4000):
        g.spec.run_frames(5)
        if g.peek('hp') < hp:
            break
    check("  and get through", g.peek('hp') < hp, True)


def stage10():
    g = Game(10)
    check("stage 10: no Bride", g.peek('stage_unlock') & 1 << (BRIDE - 1), 0)
    check("  and the Lyra player", g.peek('stage_unlock') & 1 << (LYRA - 1) != 0, True)
    g.tap('3')
    check("  key 3 chooses nothing", g.peek('sel_type') != BRIDE, True)


if __name__ == '__main__':
    stage8()
    stage9()
    stage10()
    print("lyra: ok")
