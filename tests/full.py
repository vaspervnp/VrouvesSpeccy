#!/usr/bin/env python3
"""Plays a whole game on the headless Spectrum (tools/zxrun.py): every
stage, with defenders built next to the road (the funds topped up), the
waves called early, then the ending and back to the title; a high score
name on the way.  Screenshots of each stage go to build/shots/full<model>/.

  tests/full.py [--model 48|128]
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import world  # noqa: E402
import zxrun  # noqa: E402


def tap(spec, keys, hold=2, gap=12):
    spec.set_keys(keys)
    spec.run_frames(hold)
    spec.set_keys([])
    spec.run_frames(gap)


def cells_by_road(k):
    st = world.STAGES[k]
    grid = world.carve_path(st.map, st.ground)
    out = []
    for r in range(world.MH):
        for c in range(world.MW):
            if grid[r][c] in '.F' and any(
                    0 <= r + dr < world.MH and 0 <= c + dc < world.MW and grid[r + dr][c + dc] == '#'
                    for dr in (-1, 0, 1) for dc in (-1, 0, 1)):
                out.append((c, r))
    return out[::2][:22]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='48')
    ap.add_argument('--bin', default=os.path.join(ROOT, 'build', 'vrouves.bin'))
    ap.add_argument('--sym', default=os.path.join(ROOT, 'build', 'vrouves.sym'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'shots'))
    args = ap.parse_args()
    syms = zxrun.load_symbols(args.sym)
    spec = zxrun.Spectrum(open(args.bin, 'rb').read(),
                          syms['BIN_START'], syms, args.model,
                          ending=os.path.join(ROOT, 'build', 'ending.scr'))
    end = open(os.path.join(ROOT, 'build', 'ending.scr'), 'rb').read()
    if args.model == '128':
        spec.banks[1][:6912] = end
    out = os.path.join(args.out, 'full' + args.model)
    os.makedirs(out, exist_ok=True)
    S = lambda n: spec.resolve(n)       # noqa: E731
    spec.run_frames(60)
    tap(spec, ['space'])
    spec.run_frames(30)
    for k in range(len(world.STAGES)):
        assert spec.peek(S('stage')) == k, (k, spec.peek(S('stage')))
        unlock = spec.peek(S('stage_unlock'))
        types = [t for t in range(1, 7) if unlock >> (t - 1) & 1]
        spec.poke(S('funds'), 0x10)
        spec.poke(S('funds') + 1, 0x27)
        for i, (c, r) in enumerate(cells_by_road(k)):
            spec.poke(S('cur_c'), c)
            spec.poke(S('cur_r'), r)
            spec.poke(S('sel_type'), types[i % len(types)])
            tap(spec, ['space'])
        built = sum(1 for i in range(32) if spec.peek(S('towers') + 8 * i))
        spec.screenshot(os.path.join(out, 'stage%d_built.png' % (k + 1)))
        frames = 0
        while spec.peek(S('game_over')) == 0 and frames < 40000:
            if spec.peek(S('wave_state')) == 0:
                tap(spec, ['n'])
                frames += 14
            spec.run_frames(25)
            frames += 25
            if spec.peek(S('hp')) < 50:             # the flow is tested here,
                spec.poke(S('hp'), 100)             # not the balance
            if spec.peek(S('wave_num')) == 6 and k == 0 and not os.path.exists(
                    os.path.join(out, 'battle.png')):
                spec.screenshot(os.path.join(out, 'battle.png'))
        go = spec.peek(S('game_over'))
        print("stage %d: %d defenders, game_over %d, hp %d, score %d, after %d frames"
              % (k + 1, built, go, spec.peek(S('hp')),
                 spec.peek(S('score')) | spec.peek(S('score') + 1) << 8, frames))
        assert go == 1, "stage %d lost" % (k + 1)
        spec.run_frames(200)            # the banner waits 40 passes for fire
        spec.screenshot(os.path.join(out, 'stage%d_won.png' % (k + 1)))
        tap(spec, ['space'])
        spec.run_frames(60)
    # the ending
    spec.run_frames(100)
    spec.screenshot(os.path.join(out, 'ending.png'))
    shown = bytes(spec.m.memory[0x4000:0x4000 + 6912])
    assert shown == end, "the ending is not on the screen"
    print("ending shown")
    tap(spec, ['space'])
    spec.run_frames(100)
    # a high score: the name, three letters
    spec.screenshot(os.path.join(out, 'hiscore_name.png'))
    for _ in range(3):
        tap(spec, ['space'])
    spec.run_frames(50)
    spec.screenshot(os.path.join(out, 'hiscore.png'))
    assert spec.peek(S('tpage')) == 4, "not on the high score page"
    print("high score entered, title page", spec.peek(S('tpage')))


if __name__ == '__main__':
    main()
