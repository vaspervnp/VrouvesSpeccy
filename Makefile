# LET'S GO FOR VROUVES - ZX Spectrum 48K/128K.  Build with rasm
# (https://github.com/EdouardBERGE/rasm) and Python 3 (+ Pillow, the `z80`
# module for the tests).
#
#   make              the game on tape (.tap and .tzx) and as snapshots (.z80,
#                     48K and 128K)
#   make run          the tape in FBZX
#   make test         the scripts of tests/ on tools/zxrun.py, 48K and 128K,
#                     and a whole game played through (tests/full.py)
#   make check        the tape loaded through the real 48K and 128K ROMs
#   make debug        build/debug.bin: rich, at wave 9, every defender
#   make pictures     the loading screen and the ending again (slow)
#   make release      the tape, the snapshots and the manuals in release/
#   make clean

SHELL  := /bin/bash
RASM   ?= rasm
PYTHON ?= python3
FBZX   ?= fbzx
B      := build

.PHONY: all run test check debug pictures release clean

all: $(B)/vrouves.tap $(B)/vrouves48.z80 $(B)/vrouves128.z80

$(B):
	mkdir -p $(B)

# --- the data: the stages, sprites, texts, music (tools/zxdata.py, from the
# CPC's world in tools/world.py, art.py, font.py, texts.py) ------------------
TOOLS := tools/zxdata.py tools/zxcolour.py tools/world.py tools/art.py tools/font.py \
         tools/texts.py tools/lz.py

$(B)/gen/data.asm: $(TOOLS) | $(B)
	$(PYTHON) tools/zxdata.py

# the pictures take a while: made once, or by make pictures
$(B)/loading.scr $(B)/ending.scr: | $(B)/gen/data.asm
	$(PYTHON) tools/zxdata.py --pictures

pictures:
	$(PYTHON) tools/zxdata.py --pictures

# --- the game ------------------------------------------------------------------
SRC := $(wildcard src/*.asm) $(B)/gen/data.asm

$(B)/vrouves.bin $(B)/vrouves.sym &: $(SRC)
	$(RASM) src/main.asm -os $(B)/vrouves.sym -s -sa 2>&1 | sed 's/\x1b\[[0-9;]*m//g' \
		| grep -Ei "error|warning|code\+data|free" ; test -s $(B)/vrouves.sym

debug: $(SRC)
	$(RASM) src/main.asm -DDEBUG=9 -os $(B)/debug.sym -s -sa 2>&1 | sed 's/\x1b\[[0-9;]*m//g' \
		| grep -Ei "error|warning" ; test -s $(B)/debug.sym

# the tape: the BASIC loader, the loading screen, the code, and the ending
# (a 128K's loader puts it in bank 1; a 48K reads it at the end of the game)
$(B)/vrouves.tap: $(B)/vrouves.bin $(B)/vrouves.sym $(B)/loading.scr $(B)/ending.scr \
		src/loader.bas tools/mktap.py
	$(PYTHON) tools/mktap.py $@ --sym $(B)/vrouves.sym --tzx $(B)/vrouves.tzx \
		--basic src/loader.bas VROUVES --screen $(B)/loading.scr VROUVESSCR \
		--code $(B)/vrouves.bin VROUVESBIN BIN_START \
		--code $(B)/ending.scr VROUVESEND 49152

$(B)/vrouves48.z80: $(B)/vrouves.bin $(B)/vrouves.sym $(B)/loading.scr tools/mkz80.py
	$(PYTHON) tools/mkz80.py $(B)/vrouves.bin $(B)/vrouves.sym $(B)/loading.scr $@ --model 48

$(B)/vrouves128.z80: $(B)/vrouves.bin $(B)/vrouves.sym $(B)/loading.scr $(B)/ending.scr tools/mkz80.py
	$(PYTHON) tools/mkz80.py $(B)/vrouves.bin $(B)/vrouves.sym $(B)/loading.scr $@ \
		--model 128 --bank1 $(B)/ending.scr

run: $(B)/vrouves.tap
	$(FBZX) $<

# --- checks ----------------------------------------------------------------------
test: $(B)/vrouves.bin $(B)/vrouves.sym $(B)/ending.scr
	@set -e; for m in 48 128; do for t in tests/*.txt; do \
	  case $$t in tests/stress.txt) continue;; esac; \
	  echo "== $$t ($$m K)"; \
	  out=$$($(PYTHON) tools/zxrun.py $(B)/vrouves.bin --sym $(B)/vrouves.sym --model $$m \
	    --kempston --script $$t --out $(B)/shots/$$m); \
	  printf '%s\n' "$$out" | grep -v '^shot' || true; \
	done; done
	@for m in 48 128; do echo "== a whole game ($$m K)"; \
	  $(PYTHON) tests/full.py --model $$m || exit 1; done

check: $(B)/vrouves.tap
	@for m in 48 128; do \
		echo "=== the tape through the real ROM, $$m K ==="; \
		blocks=6; [ $$m = 128 ] && blocks=8; \
		$(PYTHON) tools/zxcheck.py $(B)/vrouves.tap --sym $(B)/vrouves.sym \
			--bin $(B)/vrouves.bin --blocks $$blocks --model $$m \
			--loading $(B)/loading.scr --ending $(B)/ending.scr --png $(B)/check$$m.png; r=$$?; \
		if [ $$r = 2 ]; then echo "    skipped (no emulator or ROM)"; \
		elif [ $$r != 0 ]; then exit 1; fi; done

RELEASE := $(B)/vrouves.tap $(B)/vrouves.tzx $(B)/vrouves48.z80 $(B)/vrouves128.z80

release: all
	rm -rf release
	mkdir -p release
	cp $(RELEASE) release/
	cp -r docs/MANUAL.md docs/MANUAL_GR.md docs/img release/
	cd release && sha256sum *.* > SHA256SUMS
	ls -l release

clean:
	rm -rf $(B)
