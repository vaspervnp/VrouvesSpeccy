#!/usr/bin/env python3
"""A headless ZX Spectrum for LET'S GO FOR VROUVES (after Sugar Byte's).

Runs the game binary on a bare Z80 (the `z80` module, no ROM), with only
what the game touches: the 50 Hz interrupt (IM 2, the bus reads #FF), the
keyboard's half-rows on port #FE, the border and the beeper, the Kempston
port, and on --model 128 the AY (#FFFD / #BFFD) and the paging (#7FFD).
The 48K ROM's tape loader (LD_BYTES) is trapped: it "loads" the ending
picture from build/ending.scr.  Memory contention is not modelled.

  zxrun.py build/vrouves.bin --sym build/vrouves.sym --script tests/x.txt

Script lines (';' starts a comment):
  run <frames> [key+key...]     hold the keys (or none, '-') for N frames
  tap <key+key> [frames]        press for 2 frames (or N), then release 12
  shot <name>                   save <out>/<name>.png
  expect <addr> <value>         the byte at addr is value (decimal or #hex)
  expectw <addr> <value>        the same for a word
  poke / pokew <addr> <value>   write a byte / a word
  until <addr> <value> [keys] [max frames]   run until the byte equals value
  print <addr> [count]          print bytes
  load <frames>                 the work per frame over N frames (T states)
Addresses: a symbol (+offset), #hex, or *symbol for the word it holds.
Keys: q a o p s d n h l m 1-6 space enter caps break left right up down
(the cursor keys: CAPS SHIFT + 5-8), and kup kdown kleft kright kfire on the
Kempston (--kempston).
"""
import argparse
import os
import sys

import z80
from PIL import Image

MODELS = {'48': (224 * 312, 3_500_000, 32), '128': (228 * 311, 3_546_900, 36)}
SLICE_T = 64

ROWS = ["caps z x c v", "a s d f g", "q w e r t", "1 2 3 4 5",
        "0 9 8 7 6", "p o i u y", "enter l k j h", "space sym m n b"]
KEYS = {}
for _r, _names in enumerate(ROWS):
    for _b, _n in enumerate(_names.split()):
        KEYS[_n] = [(_r, _b)]
KEYS['break'] = KEYS['caps'] + KEYS['space']
KEYS['left'] = KEYS['caps'] + KEYS['5']
KEYS['down'] = KEYS['caps'] + KEYS['6']
KEYS['up'] = KEYS['caps'] + KEYS['7']
KEYS['right'] = KEYS['caps'] + KEYS['8']
KEYS['delete'] = KEYS['caps'] + KEYS['0']
KEMPSTON = {'kright': 1, 'kleft': 2, 'kdown': 4, 'kup': 8, 'kfire': 16}

NORMAL = [(0, 0, 0), (0, 0, 215), (215, 0, 0), (215, 0, 215),
          (0, 215, 0), (0, 215, 215), (215, 215, 0), (215, 215, 215)]
BRIGHT = [(0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),
          (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255)]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_symbols(path):
    syms = {}
    for line in open(path):
        parts = line.split()
        if len(parts) >= 2 and parts[1].startswith('#'):
            syms[parts[0].upper()] = int(parts[1][1:], 16)
    return syms


class Spectrum:
    def __init__(self, binary, org, syms, model='48', kempston=False, ending=None):
        self.frame_t, self.hz, self.int_len = MODELS[model]
        self.model = model
        self.syms = syms
        self.m = z80.Z80Machine()
        self.m.set_memory_block(org, binary)
        self.m.pc = syms['START']
        self.m.sp = 0x5CFE
        self.lo, self.hi = 0x4000, 0x10000
        self.code = (org, org + len(binary))
        self.t = 0
        self.border = 0
        self.speaker = 0
        self.beep_log = []
        self.beeps = 0
        self.ay_sel = 0
        self.ay = [0] * 16
        self.ay_log = []
        self.matrix = [0] * 8
        self.kemp = 0
        self.kempston = kempston
        self.banks = {b: bytearray(16384) for b in range(8)}
        self.bank = 0
        self.ending = ending
        self.m.set_output_callback(self.on_out)
        self.m.set_input_callback(self.on_in)
        self.m.set_get_int_vector_callback(lambda: 0xFF)
        self.ld_bytes = syms.get('LD_BYTES', 0x0562)
        self.m.set_breakpoint(self.ld_bytes)
        self.loop = syms.get('GAME_RUN.LOOP')
        self.loop_t = []        # T at each pass of the game loop
        if self.loop:
            self.m.set_breakpoint(self.loop)
        self.busy_t = 0         # T states spent outside wait_frame (load)
        self.int_pending = False
        self.prof = None        # PC samples, when profiling

    def on_out(self, addr, val):
        if not addr & 1:                                    # ULA
            self.border = val & 7
            s = (val >> 4) & 1
            if s != self.speaker:
                self.speaker = s
                self.beep_log.append((self.t, s))
                self.beeps += 1
        if self.model == '128':
            if addr & 0xC002 == 0xC000:                     # #FFFD: select
                self.ay_sel = val & 15
            elif addr & 0xC002 == 0x8000:                   # #BFFD: write
                self.ay[self.ay_sel] = val
                self.ay_log.append((self.t, self.ay_sel, val))
            elif addr & 0x8002 == 0:                        # #7FFD: paging
                b = val & 7
                if b != self.bank:
                    mem = self.m.memory
                    self.banks[self.bank][:] = bytes(mem[0xC000:0x10000])
                    self.m.set_memory_block(0xC000, bytes(self.banks[b]))
                    self.bank = b

    def on_in(self, addr):
        if not addr & 1:
            hi = addr >> 8
            v = 0x1F
            for row in range(8):
                if not hi & (1 << row):
                    v &= ~self.matrix[row] & 0x1F
            return 0xA0 | v
        if addr & 0xFF == 0x1F:
            return self.kemp if self.kempston else 0xFF
        if self.model == '128' and addr & 0xC002 == 0xC000:
            return self.ay[self.ay_sel]
        return 0xFF

    def set_keys(self, names):
        self.matrix = [0] * 8
        self.kemp = 0
        for n in names:
            if n in KEMPSTON:
                self.kemp |= KEMPSTON[n]
                continue
            for row, bit in KEYS[n]:
                self.matrix[row] |= 1 << bit

    def trap_ld_bytes(self):
        """the ROM's LD-BYTES: IX = destination, DE = length; carry = loaded"""
        m = self.m
        data = open(self.ending, 'rb').read() if self.ending else b''
        n = m.de
        if len(data) >= n:
            m.set_memory_block(m.ix, data[:n])
            m.f |= 1
        else:
            m.f &= ~1
        ret = m.memory[m.sp] | m.memory[(m.sp + 1) & 0xFFFF] << 8
        m.sp = (m.sp + 2) & 0xFFFF
        m.pc = ret
        self.t += 3_500_000 * 4         # some seconds of tape

    def run_frames(self, n):
        end = (self.t // self.frame_t + n) * self.frame_t
        m = self.m
        while self.t < end:
            m.ticks_to_stop = SLICE_T
            events = m.run()
            t0 = self.t
            dt = SLICE_T - m.ticks_to_stop
            self.t += dt
            if events & z80.Z80Machine._BREAKPOINT_HIT:
                if m.pc == self.ld_bytes:
                    self.trap_ld_bytes()
                    continue
                if m.pc == self.loop:
                    self.loop_t.append(self.t)
                    m.clear_breakpoint(self.loop)
                    m.ticks_to_stop = 1
                    m.run()
                    self.t += 4
                    m.set_breakpoint(self.loop)
            if self.t // self.frame_t != t0 // self.frame_t:
                self.int_pending = True
            if self.int_pending and self.t % self.frame_t < self.int_len + SLICE_T:
                if m.on_handle_active_int():
                    self.int_pending = False
            elif self.t % self.frame_t >= self.int_len + SLICE_T:
                self.int_pending = False                    # the ULA's INT is short
            pc = m.pc
            if not m.halted:
                self.busy_t += dt
                if self.prof is not None:
                    self.prof[pc] = self.prof.get(pc, 0) + dt
            if not (self.code[0] <= pc < self.code[1] or pc == 0xFCFC):
                raise RuntimeError(f"PC escaped the program: #{pc:04X} at T {self.t}")
            if not 0x5000 <= m.sp <= 0xFD00:
                raise RuntimeError(f"SP out of place: #{m.sp:04X} at PC #{pc:04X}")

    def peek(self, addr):
        return self.m.memory[addr & 0xFFFF]

    def poke(self, addr, value):
        self.m.memory[addr & 0xFFFF] = value & 0xFF

    def resolve(self, expr):
        deref = expr.startswith('*')
        name, _, off = expr.lstrip('*').partition('+')
        addr = int(name[1:], 16) if name.startswith('#') else self.syms[name.upper()]
        if deref:
            addr = self.peek(addr) | (self.peek(addr + 1) << 8)
        return addr + (int(off) if off else 0)

    def screenshot(self, path, scale=2):
        mem = self.m.memory
        bw = 16
        img = Image.new('RGB', (256 + 2 * bw, 192 + 2 * bw), NORMAL[self.border])
        px = img.load()
        for y in range(192):
            base = 0x4000 | ((y & 0xC0) << 5) | ((y & 7) << 8) | ((y & 0x38) << 2)
            for cx in range(32):
                b = mem[base + cx]
                a = mem[0x5800 + (y >> 3) * 32 + cx]
                pal = BRIGHT if a & 0x40 else NORMAL
                ink, paper = pal[a & 7], pal[(a >> 3) & 7]
                for k in range(8):
                    px[bw + cx * 8 + k, bw + y] = ink if b & (0x80 >> k) else paper
        img.resize((img.width * scale, img.height * scale), Image.NEAREST).save(path)


def parse_value(v, spec):
    if v.startswith('#'):
        return int(v[1:], 16)
    if v.lstrip('-').isdigit():
        return int(v)
    return spec.resolve(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('binary')
    ap.add_argument('--sym', required=True)
    ap.add_argument('--model', choices=('48', '128'), default='48')
    ap.add_argument('--kempston', action='store_true')
    ap.add_argument('--script')
    ap.add_argument('--out', default=os.path.join(ROOT, 'build', 'shots'))
    ap.add_argument('--ending', default=os.path.join(ROOT, 'build', 'ending.scr'))
    ap.add_argument('--frames', type=int, default=100)
    args = ap.parse_args()

    syms = load_symbols(args.sym)
    spec = Spectrum(open(args.binary, 'rb').read(), syms['BIN_START'], syms, args.model,
                    args.kempston, args.ending)
    if args.model == '128':     # what the loader puts in bank 1
        spec.banks[1][:6912] = open(args.ending, 'rb').read()
    os.makedirs(args.out, exist_ok=True)
    steps = []
    if args.script:
        for raw in open(args.script):
            line = raw.split(';', 1)[0].strip()
            if line:
                steps.append(line.split())
    else:
        steps = [['run', str(args.frames)], ['shot', 'final']]

    failures = 0
    for st in steps:
        cmd = st[0]
        if cmd == 'run':
            keys = st[2].split('+') if len(st) > 2 and st[2] != '-' else []
            spec.set_keys(keys)
            spec.run_frames(int(st[1]))
        elif cmd == 'tap':
            spec.set_keys(st[1].split('+'))
            spec.run_frames(int(st[2]) if len(st) > 2 else 2)
            spec.set_keys([])
            spec.run_frames(12)
        elif cmd == 'shot':
            path = os.path.join(args.out, st[1] + '.png')
            spec.screenshot(path)
            print(f"shot {path}")
        elif cmd == 'until':
            addr = spec.resolve(st[1])
            want = parse_value(st[2], spec)
            rest = st[3:]
            keys = rest[0].split('+') if rest and rest[0] != '-' else []
            limit = int(rest[1]) if len(rest) > 1 else 3000
            spec.set_keys(keys)
            n = 0
            while spec.peek(addr) != want and n < limit:
                spec.run_frames(1)
                n += 1
            if spec.peek(addr) != want:
                failures += 1
                print(f"FAIL {' '.join(st)}: got {spec.peek(addr)} after {n} frames")
                break
        elif cmd == 'print':
            addr = spec.resolve(st[1])
            count = int(st[2]) if len(st) > 2 else 1
            print(f"{st[1]}: " + ' '.join(f"{spec.peek(addr + i):02x}" for i in range(count)))
        elif cmd == 'loops':        # the game loop's passes since the last 'loops'
            lt = spec.loop_t
            d = [(b - a) / spec.frame_t for a, b in zip(lt, lt[1:])]
            if d:
                print(f"loops: {len(d)}, frames each: min {min(d):.1f} max {max(d):.1f} "
                      f"mean {sum(d) / len(d):.2f}; over 4: {sum(x > 4.05 for x in d)}")
            spec.loop_t = lt[-1:]
        elif cmd == 'profile':      # where the time goes over N frames
            spec.prof = {}
            spec.run_frames(int(st[1]))
            names = sorted((a, n) for n, a in syms.items()
                           if '.' not in n and spec.code[0] <= a < spec.code[1])
            import bisect
            keys = [a for a, _ in names]
            per = {}
            for pc, t in spec.prof.items():
                i = bisect.bisect_right(keys, pc) - 1
                nm = names[i][1] if i >= 0 else '?'
                per[nm] = per.get(nm, 0) + t
            tot = sum(per.values())
            for nm, t in sorted(per.items(), key=lambda kv: -kv[1])[:25]:
                print(f"  {100 * t / tot:5.1f}%  {nm}")
            spec.prof = None
        elif cmd == 'load':
            n = int(st[1])
            spec.busy_t = 0
            spec.run_frames(n)
            print(f"load: {100 * spec.busy_t / (n * spec.frame_t):.0f}% of {n} frames busy")
        elif cmd in ('expect', 'expectw', 'poke', 'pokew'):
            value = parse_value(st[2], spec)
            addr = spec.resolve(st[1])
            if cmd == 'poke':
                spec.poke(addr, value)
                continue
            if cmd == 'pokew':
                spec.poke(addr, value & 0xFF)
                spec.poke(addr + 1, value >> 8)
                continue
            got = spec.peek(addr)
            if cmd == 'expectw':
                got |= spec.peek(addr + 1) << 8
            ok = got == value
            failures += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {st[1]} = {got} (expected {value})")
        else:
            sys.exit(f"unknown script command: {cmd}")
    if failures:
        sys.exit(f"{failures} expectation(s) failed")


if __name__ == '__main__':
    main()
