;==============================================================================
; LET'S GO FOR VROUVES / ΠΑΜΕ ΓΙΑ ΒΡΟΥΒΕΣ
; ZX Spectrum 48K / 128K tower defence.  Assemble with rasm:
;
;   rasm src/main.asm -os build/vrouves.sym -s   -> build/vrouves.bin
;
; The Amstrad CPC game (../VrouvesCPC): its rules, stages, waves, texts and
; music; the picture, the sound, the keys and the tape are the Spectrum's.
;
; Memory:
;   #4000-#5AFF  the screen
;   #5B00-#5FFF  line tables, squares, the banner's colours (built at start)
;   #6000-       the code and its data, loaded from tape (LOAD_BASE)
;   then         entity arrays, dirty lists, variables, the current stage,
;                the playfield's background and work buffers (not on tape)
;   #FCFC        JP int_handler, #FD00 the IM 2 table, the stack below #FCFC
;   On a 128K the ending's picture waits in bank 1 (the loader puts it
;   there); a 48K loads it from the tape when the last stage is won.
;==============================================================================
        ifndef DEBUG
DEBUG       equ 0           ; rasm -DDEBUG=n: rich start at wave n
        endif
        ifndef START_STAGE
START_STAGE equ 1           ; rasm -DSTART_STAGE=n: start at stage n
        endif

LOAD_BASE   equ #6000
LOAD_CLEAR  equ LOAD_BASE-1
TAB_SCR     equ #5B00       ; screen line -> address: low bytes, high a page on
TAB_BG      equ #5D00       ; playfield line -> background buffer
SQUARES     equ #5F00       ; 64 x 16 bit
ban_attr    equ #5F80       ; the banner rows' colours (120 bytes)
IM2_TABLE   equ #FD00
IM2_FILL    equ #FC
IM2_JUMP    equ #FCFC
STACK_TOP   equ IM2_JUMP
STACK_SIZE  equ 160
ATTRS       equ #5800
BANK_0      equ #10         ; 48 BASIC ROM, bank 0 at #C000
BANK_1      equ #11
LD_BYTES    equ #0562       ; the 48K ROM's tape loader, past its setup

PF_X        equ 8           ; the playfield on the screen: 240 x 160
PF_Y        equ 8
PF_COL      equ 1
PF_W        equ 30          ; bytes a line
PF_H        equ 160
NCOL        equ 15          ; cells of 16 x 16: 2 x 2 attribute cells each
NROW        equ 10
TH          equ 16
DL_CAP      equ 63

; colours: ink + 8 * paper + bright
A_TEXT      equ #47         ; bright white on black
A_WHI       equ #47
A_YEL       equ #46
A_RED       equ #42
A_GRN       equ #44
A_CYN       equ #45
A_GRY       equ #07
A_MAG       equ #43
A_BAN1      equ #4e         ; the banner: yellow on blue
A_BAN2      equ #4f         ; white on blue

; keys: half-row * 8 + bit (hw.asm); row 8 the Kempston, row 9 the cursor
; keys, BREAK and DELETE
K_Q         equ 16
K_A         equ 8
K_O         equ 41
K_P         equ 40
K_S         equ 9
K_D         equ 10
K_1         equ 24
K_2         equ 25
K_3         equ 26
K_4         equ 27
K_5         equ 28
K_6         equ 36
K_ENTER     equ 48
K_L         equ 49
K_H         equ 52
K_SPACE     equ 56
K_M         equ 58
K_N         equ 59
J_RIGHT     equ 64
J_LEFT      equ 65
J_DOWN      equ 66
J_UP        equ 67
J_FIRE      equ 68
K_LEFT      equ 72
K_DOWN      equ 73
K_UP        equ 74
K_RIGHT     equ 75
K_ESC       equ 76          ; BREAK
K_DEL       equ 77

        org LOAD_BASE
bin_start:
        include "../build/gen/data.asm"

start:
        di
        ld sp,STACK_TOP
        ld hl,bss_start
        ld de,bss_start+1
        ld bc,bss_end-bss_start-1
        ld (hl),0
        ldir
        ld hl,keys              ; keyboard buffers: nothing pressed
        ld de,keys+1
        ld bc,40-1
        ld (hl),#ff
        ldir
        xor a
        out (#fe),a
        call build_tables
        call dirty_reset
        call hw_init
        ld hl,#a5f3
        ld (seed),hl
        ld a,1
        ld (mus_on),a
        ld (mus_title),a
        call snd_init
        call hs_init
.main:  ld a,(mus_title)
        ld (mus_on),a
        call title_screen
        ld a,(framecnt)
        ld hl,seed
        xor (hl)
        ld (hl),a
        call rt_start
        ld a,(mus_on)           ; a 48K plays the game without the tune: the
        ld (mus_title),a        ; beeper would only have the time left over
        ld a,(ay_present)       ; from each frame (M turns it on)
        or a
        jr nz,.tune
        ld (mus_on),a
.tune:  ld a,START_STAGE-1
.stage: ld (stage),a
        call stage_load
.play:  call game_run
        call rt_retry           ; lost with a life left: the same stage again
        jr nc,.play
        ld a,(game_over)        ; won: on to the next stage
        dec a
        jr nz,.main
        ld a,(stage)
        inc a
        cp NUM_STAGES
        jr c,.stage
        call ending_show        ; all stages won: the feast at the school
        jr .main

;------------------------------------------------------------------------------
; the stages
;------------------------------------------------------------------------------
; A = stage: its record to STAGE_AREA, its tile list
stage_load:
        call stage_entry
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        inc hl
        inc hl
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ld (stage_tl),hl
        ex de,hl
        ld de,STAGE_AREA
        jp lz_unpack

; -> HL = the current stage's entry in stage_tab
stage_entry:
        ld a,(stage)
        ld l,a
        add a,a
        add a,l
        add a,a
        ld l,a
        ld h,0
        ld de,stage_tab
        add hl,de
        ret

; the stage's colours onto the playfield (unpacked into the work buffer),
; the banner rows' kept in ban_attr
stage_attrs:
        call stage_entry
        inc hl
        inc hl
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ld de,WORKBUF
        call lz_unpack
        ld hl,WORKBUF
        ld de,ATTRS+32+PF_COL
        ld b,PF_H/8
.r:     push bc
        ld bc,PF_W
        ldir
        ex de,hl
        ld bc,32-PF_W
        add hl,bc
        ex de,hl
        pop bc
        djnz .r
        ld hl,WORKBUF+(BAN_AROW-1)*PF_W
        ld de,ban_attr
        ld bc,4*PF_W
        ldir
        ret

;------------------------------------------------------------------------------
; the ending: the village feast in front of the school.  On a 128K the
; picture is in bank 1; a 48K reads it from the tape, straight onto the
; screen (SPACE skips it).
;------------------------------------------------------------------------------
ending_show:
        call snd_off
        ld a,(is_128)
        or a
        jr z,.tape
        call cls_black
        di
        ld a,BANK_1
        ld bc,#7ffd
        out (c),a
        ld hl,#c000
        ld de,#4000
        ld bc,6912
        ldir
        ld a,BANK_0
        ld bc,#7ffd
        out (c),a
        ei
        jr .wait
.tape:  call cls
        call tgt_scr
        call text_normal
        ld a,A_YEL
        call set_attr
        ld a,T_ENDLOAD
        ld e,88
        call print_id_centered
        ld a,1
        call wait_frames
.ld:    di                      ; the data block (not its header: tried again)
        ld ix,#4000
        ld de,6912
        ld a,#ff
        scf
        inc d                   ; as LD-BYTES does on entry
        ex af,af'
        dec d
        ld a,#0f
        out (#fe),a
        call LD_BYTES
        jr c,.ok
        ld a,#7f                ; SPACE: no ending
        in a,(#fe)
        rra
        jr c,.ld
.ok:    xor a
        out (#fe),a
        ei
.wait:  call kbd_update
        ld a,25
        call wait_frames
.k:     call wait_frame
        call kbd_update
        call fire_hit
        jr nc,.k
        ret

; A = frames to wait
wait_frames:
        push af
        call wait_frame
        pop af
        dec a
        jr nz,wait_frames
        ret

; a black screen (attributes black on black)
cls_black:
        ld hl,ATTRS
        ld de,ATTRS+1
        ld bc,767
        ld (hl),0
        ldir
        ret

        include "lz.asm"
        include "hw.asm"
        include "sound.asm"
        include "gfx.asm"
        include "game.asm"
        include "title.asm"

code_end:
        if DEBUG || START_STAGE > 1
        save "build/debug.bin",bin_start,code_end-bin_start
        else
        save "build/vrouves.bin",bin_start,code_end-bin_start
        endif

;------------------------------------------------------------------------------
; variables (not on the tape, cleared at start)
;------------------------------------------------------------------------------
        nocode
        org (code_end+255)&#ff00
ENT_START:
enemies:    defs 256        ; 16 x 16
towers:     defs 256        ; 32 x 8
projs:      defs 200        ; 20 x 10
fxs:        defs 32         ; 8 x 4
ENT_END:
        defs 24
CLIST:      defs 512        ; rectangles to copy to the screen this frame
CLIST_END:
bss_start:
framecnt:   defs 1
score:      defs 2
last_flip:  defs 1
keys:       defs 20         ; live state, then latch
kcur:       defs 10
kold:       defs 10         ; keys..kold: 40 bytes, set to #FF at start
mus_on:     defs 1
mus_title:  defs 1          ; the music on the title (mus_on in the game)
chan_a:     defs C_SIZE
chan_b:     defs C_SIZE
sfx_active: defs 1
sfx_ptr:    defs 2
sfx_cur_prio: defs 1
sfx_noise:  defs 1
psg_shadow: defs 14
noise_seed: defs 2
ay_present: defs 1
kempston_on: defs 1
is_128:     defs 1
tgt_tab:    defs 1
spr_xb:     defs 1
spr_y:      defs 1
tl_odd:     defs 1
save_ptr:   defs 2
cl_ptr:     defs 2
sv_x:       defs 1
sv_w:       defs 1
fill_val:   defs 1
txt_attr:   defs 1
txt_x:      defs 1
txt_y:      defs 1
txt_x0:     defs 1
txt_big:    defs 1
gl_ptr:     defs 2
gl_keep:    defs 1
pn_cnt:     defs 1
pn_nz:      defs 1
pn_zero:    defs 1
lang:       defs 1
seed:       defs 2
tpage:      defs 1
ttimer:     defs 2
tmp_i:      defs 1
tmp_y:      defs 1
stage:      defs 1
stage_tl:   defs 2
difficulty: defs 1          ; 0 medium, 1 hard, 2 hardest, 3 easy
rt_lives:   defs 1
rt_chk:     defs 2
hs_table:   defs 40         ; 8 x (3 glyphs, score)
hs_new:     defs 1
hs_pos:     defs 1
hs_idx:     defs 3
hs_score:   defs 2

; cleared by game_init
game_vars:
funds:      defs 2
hp:         defs 1
wave_num:   defs 1
wave_state: defs 1
cd_sec:     defs 1
cd_sub:     defs 1
sp_ptr:     defs 2
sp_left:    defs 1
sp_timer:   defs 1
sp_type:    defs 1
sp_iv:      defs 1
en_count:   defs 1
gen_ctr:    defs 1
game_over:  defs 1
quit:       defs 1
paused:     defs 1
cur_c:      defs 1
cur_r:      defs 1
sel_type:   defs 1
rep_t:      defs 1
hud_flags:  defs 1
hud_flags_b: defs 1         ; must follow hud_flags
hud_cur:    defs 1
hud_aff:    defs 1
ban_on:     defs 1
ban_id1:    defs 1
ban_id2:    defs 1
ban_timer:  defs 1
msg_on:     defs 1
msg_id1:    defs 1
msg_id2:    defs 1
msg_timer:  defs 1
msg_alt:    defs 1
msg_alt_t:  defs 1
msg_fits:   defs 1
sacks_gone: defs 1
tmp_cost:   defs 1
tmp_idx:    defs 1
tr_range:   defs 1
tr_range2:  defs 2
tr_cd:      defs 1
tr_dmg:     defs 1
tr_flags:   defs 1
tr_proj:    defs 1
tr_sfx:     defs 1
best_prog:  defs 2
best_ix:    defs 2
sp_ptype:   defs 1
sp_pdmg:    defs 1
sp_pflag:   defs 1
end_wait:   defs 1
cell_qn:    defs 1
cell_q:     defs 2*64
ban_req:    defs 1          ; 1 draw the banner, 2 take it off (bg_pending)
syn_cnt:    defs 1          ; defenders with a neighbour bonus (syn_update)
syn_pass:   defs 1
tr_budget:  defs 1
ticks_due:  defs 1
frame_acc:  defs 1
dbg_el:     defs 1
game_vars_end:
STAGE_AREA: defs STAGE_SIZE
bss_end:
SAVEBUF:    defs 2048       ; what the sprites cover (gfx.asm)
SAVE_END:
WORKBUF:    defs PF_W*PF_H
            defs 2          ; a sprite's last byte may fall just past it
work_end:
        code

        assert lo(enemies) == 0 && EN_SZ*MAX_EN == 256 && lo(projs) == 0
        assert lo(CLIST) == 0
        assert work_end <= STACK_TOP-STACK_SIZE
        assert (SQUARES+128) <= ban_attr && ban_attr+4*PF_W <= LOAD_BASE

        print "code+data: ",{hex}bin_start,"-",{hex}code_end," (",code_end-bin_start," bytes)"
        print "variables to ",{hex}bss_end,", buffers to ",{hex}work_end,", free ",STACK_TOP-STACK_SIZE-work_end
