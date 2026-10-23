;==============================================================================
; game.asm - the game: the CPC's rules, tick for tick (../VrouvesCPC/src/
; game.asm), drawn the Spectrum's way: the playfield in gfx.asm's buffers,
; the HUD and the banner as text
;==============================================================================

        inc de
        mend

; enemy record (16 bytes)
E_TYPE  equ 0
E_HP    equ 1
E_MAXHP equ 2
E_ARM   equ 3
E_SPD   equ 4           ; path steps per frame * 16
E_ACC   equ 5
E_PROG  equ 6           ; 16 bit: steps walked (for "first" targeting)
E_X     equ 8
E_Y     equ 9
E_SLOW  equ 10
E_ANIM  equ 11
E_GEN   equ 12
E_SEG   equ 13
E_REM   equ 14
E_SUB   equ 15
EN_SZ   equ 16
MAX_EN  equ 16

ET_DRONE equ 1
ET_GUARD equ 2
ET_TANK  equ 3

; tower record (8 bytes)
T_TYPE  equ 0
T_COL   equ 1
T_ROW   equ 2
T_CD    equ 3
T_CX    equ 4
T_CY    equ 5
T_DIS   equ 6
T_SYN   equ 7               ; neighbour factor in 16ths, 0 none (syn_update)
TW_SZ   equ 8
MAX_TW  equ 32

TT_CRETAN equ 1
TT_YIAYIA equ 2
TT_BRIDE  equ 3
TT_PSSSST equ 4
TT_CAULDRON equ 5
TT_BAKER  equ 6

; projectile record (10 bytes)
P_TYPE  equ 0
P_X     equ 1           ; Mode 0 pixels
P_Y     equ 2
P_TGT   equ 3
P_DMG   equ 4
P_FLAG  equ 5           ; bit0 critical, bit7 target lost
P_TX    equ 6
P_TY    equ 7
P_GEN   equ 8
PR_SZ   equ 10
MAX_PR  equ 20

PT_BULLET equ 1
PT_PISTOL equ 2
PT_LASER  equ 3
PT_DAKOS  equ 4

; effect record (4 bytes)
F_TYPE  equ 0
F_X     equ 1
F_Y     equ 2
F_T     equ 3
FX_SZ   equ 4
MAX_FX  equ 8
TARGET_BUDGET equ 4
        if FRAMES_PER_DRAW == 4
REP_FIRST equ 4                 ; cursor auto-repeat, in drawn frames
REP_NEXT equ 1
        else
REP_FIRST equ 7
REP_NEXT equ 2
        endif

FX_SPARK equ 1
FX_PUFF  equ 2
FX_BASH  equ 3
FX_POOF  equ 4
FX_BOOM  equ 5
FX_ZAP   equ 6

HUDF_WAVE   equ 1
HUDF_INFO   equ 2
HUDF_STATUS equ 4
HUDF_FUNDS  equ 8
HUDF_HP     equ 16
HUDF_TOP    equ 32

        if DEBUG
START_FUNDS equ 3000
        else
START_FUNDS equ 120
        endif
FIRST_COUNTDOWN equ 45
NEXT_COUNTDOWN equ 15

;------------------------------------------------------------------------------
; data tables
;------------------------------------------------------------------------------
; enemy types: base hp, hp per wave, speed, armour, reward, base damage, air, -
etype_tab:
        db 6,3,20,0,3,4,1,0             ; bio-drone
        db 16,8,9,2,4,8,0,0             ; compliance guard
        db 50,19,7,4,10,20,0,0          ; weed destroyer (tank)

; towers: cost, range, cooldown, damage, flags (bit0 hits air), projectile, sfx, sell
; (the ranges, in pixels, are the CPC's 4/3: a cell is 16 lines, not 12)
ttype_tab:
        db 35,40,18,6,1,PT_BULLET,SFX_RIFLE,17          ; cretan
        db 50,24,22,14,0,0,SFX_BASH,25                  ; yiayia
        db 70,37,6,4,1,PT_PISTOL,SFX_PISTOL,35          ; bride
        db 80,48,10,5,1,PT_LASER,SFX_LASER,40           ; psssst
        db 110,29,32,8,0,0,SFX_PUFF,55                  ; cauldron
        db 60,45,36,16,1,PT_DAKOS,SFX_THROW,30          ; baker

tower_sprites:
        dw spr_cretan,spr_yiayia,spr_bride,spr_psssst,spr_cauldron,spr_baker


proj_sprites:
        dw spr_bullet,spr_pistol,spr_laser,spr_dakos
; x speed (2 pixels), y speed (lines): the CPC's 4/3
proj_speed:
        db 8,12, 9,13, 13,20, 4,7

; effects: frame a, frame b, lifetime (8 bytes each)
fx_tab:
        dw spr_spark_a,spr_spark_b
        db 6,0,0,0
        dw spr_puff_a,spr_puff_b
        db 12,0,0,0
        dw spr_bash_a,spr_bash_b
        db 8,0,0,0
        dw spr_poof_a,spr_poof_b
        db 10,0,0,0
        dw spr_boom_a,spr_boom_b
        db 12,0,0,0
        dw spr_zap_a,spr_spark_b
        db 6,0,0,0

sel_keys:
        db K_1,K_2,K_3,K_4,K_5,K_6

;------------------------------------------------------------------------------
; main game loop
;------------------------------------------------------------------------------
game_run:
        call game_init
.loop:  call kbd_update
        call handle_input
        ld a,(quit)
        or a
        ret nz
        ld a,(paused)
        or a
        jr nz,.draw
        ld a,(ticks_due)        ; logic always runs at 25 Hz: one tick per
.t:     push af                 ; two frames that passed since the last draw
        call game_tick
        pop af
        ld b,a
        ld a,(game_over)
        or a
        jr nz,.draw
        ld a,b
        dec a
        jr nz,.t
.draw:  call hud_refresh
        call render
        call flip
        ld a,(game_over)
        or a
        jr z,.loop
        jp end_game

game_tick:
        ld a,TARGET_BUDGET
        ld (tr_budget),a
        call wave_update
        call update_enemies
        call update_towers
        call update_projs
        call update_fx
        jp banner_tick


game_init:
        call cls
        ; put the sacks back and take the towers off the map
        ld hl,sack_cells
        ld b,NUM_SACKS
.sk:    push bc
        ld d,(hl)
        inc hl
        ld e,(hl)
        inc hl
        ld a,(hl)
        inc hl
        inc hl
        push hl
        push af
        call cell_offset
        ld bc,tilemap
        add hl,bc
        pop af
        ld (hl),a
        pop hl
        pop bc
        djnz .sk
        ld hl,cellmap
        ld bc,NCOL*NROW
.cm:    bit 7,(hl)
        jr z,.cn
        ld a,(hl)
        and #40                 ; a hovering psssst sat on a blocked cell
        jr z,.c0
        ld a,2
.c0:    ld (hl),a
.cn:    cpi
        jp pe,.cm
        ; clear all entity arrays and game variables
        ld hl,ENT_START
        ld de,ENT_START+1
        ld bc,ENT_END-ENT_START-1
        ld (hl),0
        ldir
        ld hl,game_vars
        ld de,game_vars+1
        ld bc,game_vars_end-game_vars-1
        ld (hl),0
        ldir
        ld hl,START_FUNDS
        ld (funds),hl
        ld a,100
        ld (hp),a
        ld a,FIRST_COUNTDOWN
        ld (cd_sec),a
        ld a,25
        ld (cd_sub),a
        ld a,9                  ; on the grass in every stage
        ld (cur_c),a
        ld a,2
        ld (cur_r),a
        ld a,1
        ld (sel_type),a
        ld (ticks_due),a
        call stage_attrs        ; (unpacked in the work buffer: first)
        call dirty_reset
        xor a
        ld (cell_qn),a
        ld (ban_req),a
        ; background
        call tgt_bg
        ld e,0
.r:     ld d,0
.c:     push de
        call draw_tile_bg
        pop de
        inc d
        ld a,d
        cp NCOL
        jr nz,.c
        inc e
        ld a,e
        cp NROW
        jr nz,.r
        call bg_to_screens
        ld a,B_STAGE
        ld c,B_CALL
        call msg_show
        if DEBUG
        ld a,DEBUG-1            ; -DDEBUG=n starts at wave n
        ld (wave_num),a
        ld a,#3f                ; and has every defender
        ld (stage_unlock),a
        else
        ld hl,(stage_unlock+1)  ; the defenders this stage brings
        ld a,l
        cp #ff
        jr z,.na
        ld c,h
        call banner_show
        ld a,125                ; for five seconds
        ld (ban_timer),a
.na:
        endif
        jp hud_full

end_game:
        ld hl,enemies           ; no walkers, shots or effects on top of the
        xor a                   ; banner: their old places are restored
.c1:    ld (hl),a
        inc l
        jr nz,.c1
        ld h,hi(projs)          ; projectiles and effects: #BE00-#BEFF
.c2:    ld (hl),a
        inc l
        jr nz,.c2
        call kbd_update
        ld a,(game_over)
        cp 1
        ld a,B_WIN
        jr z,.w
        ld a,B_LOSE
.w:     ld c,B_SPACE
        call banner_show
        ld a,SFX_WAVE
        call sfx_play
        ld a,40
        ld (end_wait),a
.l:     call kbd_update
        call hud_refresh        ; the last changes reach the screen
        call render
        call flip
        ld a,(end_wait)
        or a
        jr z,.k
        dec a
        ld (end_wait),a
        jr .l
.k:     call fire_hit
        jr nc,.l
        ret


;------------------------------------------------------------------------------
; input
;------------------------------------------------------------------------------
handle_input:
        ld hl,kcur              ; nothing pressed now or last frame: no work
        ld b,20
        ld a,#ff
.any:   and (hl)
        inc hl
        djnz .any
        inc a
        jr nz,.keys
        ld (rep_t),a            ; keys released: reset the cursor repeat
        ret
.keys:  ld a,K_L
        call key_hit
        call c,toggle_lang
        ld a,K_M
        call key_hit
        call c,toggle_music
        ld a,K_H
        call key_hit
        call c,toggle_pause
        ld a,K_ESC
        call key_hit
        jr nc,.ne
        ld a,(paused)
        or a
        jr z,.pz
        ld a,1                  ; ESC while paused: back to the title
        ld (quit),a
        ret
.pz:    call toggle_pause
.ne:    ld a,(paused)
        or a
        ret nz
        call cursor_input
        ld hl,sel_keys
        ld bc,#0601
.sk:    ld a,(hl)
        call key_hit
        jr nc,.nk
        push bc                 ; only defenders this stage has
        ld b,c
        ld a,(stage_unlock)
.ul:    rrca
        djnz .ul
        pop bc
        jr nc,.nk
        ld a,c
        ld (sel_type),a
        ld a,HUDF_INFO
        call hud_set
.nk:    inc hl
        inc c
        djnz .sk
        call fire_hit
        call c,try_build
        ld a,K_S
        call key_hit
        call c,try_sell
        ld a,K_DEL
        call key_hit
        call c,try_sell
        ld a,K_N
        call key_hit
        call c,call_wave_now
        ret

toggle_lang:
        ld a,(lang)
        xor 1
        ld (lang),a
        call hud_full
        ld a,(ban_on)
        or a
        ret z
        jp banner_draw

toggle_music:
        ld a,(mus_on)
        xor 1
        ld (mus_on),a
        ret

toggle_pause:
        ld a,(paused)
        xor 1
        ld (paused),a
        jr z,.resume
        ld a,B_PAUSE
        ld c,B_PAUSE2
        call banner_show
        jr .st
.resume:
        call banner_clear
.st:    ld a,HUDF_STATUS
        jp hud_set

cursor_input:
        ld c,0
        ld a,K_UP
        call key_down
        jr nc,.k1
        set 0,c
.k1:     ld a,J_UP
        call key_down
        jr nc,.k2
        set 0,c
.k2:     ld a,K_DOWN
        call key_down
        jr nc,.k3
        set 1,c
.k3:     ld a,J_DOWN
        call key_down
        jr nc,.k4
        set 1,c
.k4:     ld a,K_LEFT
        call key_down
        jr nc,.k5
        set 2,c
.k5:     ld a,J_LEFT
        call key_down
        jr nc,.k6
        set 2,c
.k6:     ld a,K_RIGHT
        call key_down
        jr nc,.k7
        set 3,c
.k7:     ld a,J_RIGHT
        call key_down
        jr nc,.k8
        set 3,c
.k8:     ld a,K_Q
        call key_down
        jr nc,.q1
        set 0,c
.q1:    ld a,K_A
        call key_down
        jr nc,.q2
        set 1,c
.q2:    ld a,K_O
        call key_down
        jr nc,.q3
        set 2,c
.q3:    ld a,K_P
        call key_down
        jr nc,.q4
        set 3,c
.q4:    ld a,c
        or a
        jr nz,.held
        ld (rep_t),a
        ret
.held:  ld a,(rep_t)
        or a
        jr z,.first
        dec a
        ld (rep_t),a
        ret nz
        ld a,REP_NEXT
        jr .go
.first: ld a,REP_FIRST
.go:    ld (rep_t),a
        bit 0,c
        jr z,.nu
        ld a,(cur_r)
        or a
        jr z,.nu
        dec a
        ld (cur_r),a
.nu:    bit 1,c
        jr z,.nd
        ld a,(cur_r)
        cp NROW-1
        jr z,.nd
        inc a
        ld (cur_r),a
.nd:    bit 2,c
        jr z,.nl
        ld a,(cur_c)
        or a
        jr z,.nl
        dec a
        ld (cur_c),a
.nl:    bit 3,c
        jr z,.nr
        ld a,(cur_c)
        cp NCOL-1
        jr z,.nr
        inc a
        ld (cur_c),a
.nr:    ld a,HUDF_INFO
        call hud_set
        ld a,SFX_MOVE
        jp sfx_play

; carry if the selected defender cannot go on the cursor cell
can_build:
        call cur_cell
        ld a,(hl)
        or a
        ret z
        cp 2
        scf
        ret nz
        ld a,(sel_type)
        cp TT_PSSSST
        ret z
        scf
        ret

; D,E = cursor col,row ; HL = cellmap entry
cur_cell:
        ld a,(cur_c)
        ld d,a
        ld a,(cur_r)
        ld e,a
        jp cell_ptr

try_build:
        call can_build
        jr c,.err
        ld a,(sel_type)
        call ttype_ptr
        ld a,(hl)
        ld (tmp_cost),a
        ld c,a
        ld b,0
        ld hl,(funds)
        or a
        sbc hl,bc
        jr c,.err
        ld iy,towers
        ld e,0
.f:     ld a,(iy+T_TYPE)
        or a
        jr z,.got
        ld bc,TW_SZ
        add iy,bc
        inc e
        ld a,e
        cp MAX_TW
        jr nz,.f
.err:   ld a,SFX_ERROR
        jp sfx_play
.got:   ld a,e
        ld (tmp_idx),a
        ld a,(sel_type)
        ld (iy+T_TYPE),a
        ld a,(cur_c)
        ld (iy+T_COL),a
        add a,a
        add a,a
        add a,2
        ld (iy+T_CX),a
        ld a,(cur_r)
        ld (iy+T_ROW),a
        call mul16
        add a,8
        ld (iy+T_CY),a
        ld (iy+T_CD),8
        ld (iy+T_DIS),0
        ld (iy+T_SYN),0
        call cur_cell
        ld a,(hl)               ; 2 = blocked cell (only psssst hovers there)
        and 2
        rrca
        rrca
        rrca
        ld c,a                  ; #40 marks it
        ld a,(tmp_idx)
        or #80
        or c
        ld (hl),a
        call sc_build       ; pay for it, and its damage as points
        call syn_update
        call cur_cell
        call redraw_cell
        ld a,SFX_BUILD
        call sfx_play
        ld a,HUDF_FUNDS+HUDF_INFO+HUDF_TOP
        jp hud_set

try_sell:
        call cur_cell
        ld a,(hl)
        bit 7,a
        ret z
        ld c,0
        bit 6,a
        jr z,.s0
        ld c,2
.s0:    ld (hl),c
        and #1f
        call tower_ptr
        push hl
        pop iy
        ld a,(iy+T_TYPE)
        call ttype_ptr
        call sc_sell        ; half its price back, its points taken away
        ld (iy+T_TYPE),0
        call syn_update
        call cur_cell
        call redraw_cell
        ld a,SFX_SELL
        call sfx_play
        ld a,HUDF_FUNDS+HUDF_INFO+HUDF_TOP
        jp hud_set

; after a defender is built or sold: each one's neighbour factor, into
; T_SYN.  Penalties always count; bonuses go to three defenders at most:
; those that have one keep it while they still qualify, then the others in
; table order while there is room.
SYN_MAX equ 3
syn_update:
        xor a
        ld (syn_cnt),a
        dec a                   ; pass 1: those with a bonus now
        call .pass
        xor a                   ; pass 2: the rest
.pass:  ld (syn_pass),a
        ld iy,towers
        ld b,MAX_TW
.t:     push bc
        ld a,(iy+T_TYPE)
        or a
        jr z,.n
        ld a,(iy+T_SYN)
        cp 17                   ; NC: a bonus
        ccf
        sbc a,a                 ; #FF with a bonus, 0 without
        ld hl,syn_pass
        cp (hl)
        jr nz,.n
        ld a,(iy+T_TYPE)
        ld d,(iy+T_COL)
        ld e,(iy+T_ROW)
        call syn_find
        ld a,0
        jr z,.set               ; no partner next door
        inc hl
        ld a,(hl)
        cp 17
        jr c,.set               ; a penalty
        ld c,a
        ld hl,syn_cnt
        ld a,(hl)
        cp SYN_MAX
        ld a,0
        jr nc,.set              ; no room for another bonus
        inc (hl)
        ld a,c
.set:   ld (iy+T_SYN),a
.n:     ld bc,TW_SZ
        add iy,bc
        pop bc
        djnz .t
        ret

; syn_hud: A = the factor a new defender would get.  Carry: show it (a
; penalty, or a bonus with room for one).  Preserves A.
syn_room:
        cp 17
        ret c
        ld b,a
        ld a,(syn_cnt)
        cp SYN_MAX
        ld a,b
        ret

call_wave_now:                  ; early call: half the seconds left become vrouves
        ld a,(wave_state)
        or a
        ret nz
        ld a,(cd_sec)
        ld e,a                  ; points: every second left
        srl a
        ld c,a
        call pay
        ld a,HUDF_FUNDS+HUDF_TOP
        call hud_set
        jp start_wave

;------------------------------------------------------------------------------
; helpers
;------------------------------------------------------------------------------
; C = vrouves earned, E = points
pay:
        ld b,0
        ld hl,(funds)
        add hl,bc
        ld (funds),hl
        ld c,e
        ld b,0
; BC = points, added to the score (it stops at 65535)
score_add:
        ld hl,(score)
        add hl,bc
        jr nc,.s
        ld hl,#ffff
.s:     ld (score),hl
        ret

; A * 16 (A < 16)
mul16:
        add a,a
        add a,a
        add a,a
        add a,a
        ret

; D,E = col,row -> HL = row*15+col.  Preserves DE.
cell_offset:
        push de
        ld a,e
        add a,a
        add a,a
        add a,a
        add a,a
        sub e
        ld l,a
        ld h,0
        ld e,d
        ld d,0
        add hl,de
        pop de
        ret

cell_ptr:
        call cell_offset
        ld bc,cellmap
        add hl,bc
        ret

; A = tower type -> HL = stats
ttype_ptr:
        dec a
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld bc,ttype_tab
        add hl,bc
        ret

; A = enemy type -> HL = stats
etype_ptr:
        dec a
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld bc,etype_tab
        add hl,bc
        ret

; A = tower index -> HL
tower_ptr:
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld bc,towers
        add hl,bc
        ret

; A (0..63) -> HL = A*A.  Preserves DE.
sq:
        push de
        add a,a
        ld e,a
        ld d,0
        ld hl,SQUARES
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        pop de
        ret

rand:
        push hl
        ld hl,(seed)
        ld a,h
        rra
        ld a,l
        rra
        xor h
        ld h,a
        ld a,l
        rra
        ld a,h
        rra
        xor l
        ld l,a
        xor h
        ld h,a
        ld (seed),hl
        pop hl
        ret

hud_set:                        ; A = flags: HUD parts to draw again
        push bc
        ld hl,hud_flags
        ld c,a
        or (hl)
        ld (hl),a
        inc hl
        ld a,c
        or (hl)
        ld (hl),a
        pop bc
        ret


;------------------------------------------------------------------------------
; background cells
;------------------------------------------------------------------------------
; D,E = col,row : the cell's tile into the current target (the background)
draw_tile_bg:
        push de
        call cell_offset
        ld bc,tilemap
        add hl,bc
        ld l,(hl)
        ld h,0
        add hl,hl
        ld bc,(stage_tl)
        add hl,bc
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        pop de
        push de
        call cell_xy
        call draw_tile
        pop de
        ret

; D,E = col,row -> D,E = x,y of the cell (pixels)
cell_xy:
        ld a,d
        call mul16
        ld d,a
        ld a,e
        call mul16
        ld e,a
        ret

; D,E = col,row : tile + defender into the background, no dirty marking
redraw_cell_nd:
        push de
        call tgt_bg
        call draw_tile_bg
        pop de
        push de
        call cell_ptr
        ld a,(hl)
        bit 7,a
        jr z,.done
        and #1f
        call tower_ptr
        ld a,(hl)
        ld bc,T_DIS
        add hl,bc
        ld c,(hl)
        cp TT_CAULDRON
        jr nz,.ns
        inc c
        dec c
        jr z,.ns
        ld hl,spr_cauldron_x
        jr .dr
.ns:    dec a
        add a,a
        ld l,a
        ld h,0
        ld bc,tower_sprites
        add hl,bc
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
.dr:    pop de
        push de
        call cell_xy
        inc e                   ; 12 lines high, in a cell of 16
        inc e
        call draw_sprite_raw
.done:  pop de
        ret

; D,E = col,row : the cell to be drawn again, at the next frame (with the
; sprites off the playfield: bg_pending).  Preserves DE.
redraw_cell:
        ld hl,cell_qn
        ld a,(hl)
        cp CELL_QMAX
        ret nc
        inc (hl)
        add a,a
        ld hl,cell_q
        add a,l
        ld l,a
        jr nc,.n
        inc h
.n:     ld (hl),d
        inc hl
        ld (hl),e
        ret
CELL_QMAX equ 64

; at the frame, with the sprites off: the cells, then the banner
bg_pending:
        ld a,(cell_qn)
        or a
        jr z,.ban
        ld b,a
        ld hl,cell_q
.q:     push bc
        ld d,(hl)
        inc hl
        ld e,(hl)
        inc hl
        push hl
        call redraw_cell_nd
        ld a,(ban_on)           ; keep a banner on top of its rows
        or a
        jr z,.nb
        ld a,e
        sub BAN_ROW
        cp 2
        jr nc,.nb
        ld a,1
        ld (ban_req),a
.nb:    sla d                   ; x byte: 2 a cell
        ld a,e
        call mul16
        ld e,a
        ld bc,#1002             ; 2 bytes x 16 lines
        call dirty_add_both
        pop hl
        pop bc
        djnz .q
        xor a
        ld (cell_qn),a
.ban:   ld a,(ban_req)
        or a
        ret z
        ld b,a
        xor a
        ld (ban_req),a
        dec b
        jp nz,ban_do_clear
        jp ban_do_draw

;------------------------------------------------------------------------------
; waves
;------------------------------------------------------------------------------
wave_update:
        ld a,(hp)
        or a
        jr nz,.alive
        ld a,2
        ld (game_over),a
        ret
.alive: ld a,(wave_state)
        or a
        jr nz,.active
        ld a,(cd_sub)
        or a
        jr nz,.sub
        ld a,(cd_sec)
        or a
        jp z,start_wave
        dec a
        ld (cd_sec),a
        ld a,25
        ld (cd_sub),a
        ld a,HUDF_STATUS
        call hud_set
.sub:   ld hl,cd_sub
        dec (hl)
        ret
.active:
        call spawn_tick
        ld a,(sp_left)
        or a
        ret nz
        ld a,(en_count)
        or a
        ret nz
        ; wave cleared: bonus 15 + 3*wave
        ld a,(wave_num)
        ld c,a
        add a,a
        add a,c
        add a,15
        ld c,a
        ld b,0
        ld hl,(funds)
        add hl,bc
        ld (funds),hl
        ld a,HUDF_FUNDS+HUDF_STATUS
        call hud_set
        ld a,(wave_num)
        cp NUM_WAVES
        jr nz,.more
        ld bc,(funds)           ; stage won: the vrouves left are points
        call score_add
        ld a,1
        ld (game_over),a
        ret
.more:  xor a
        ld (wave_state),a
        ld a,NEXT_COUNTDOWN
        ld (cd_sec),a
        ld a,25
        ld (cd_sub),a
        ld a,B_CLEAR
        ld c,B_NEXT
        call msg_show
        ld a,SFX_SELL
        jp sfx_play

start_wave:
        ld a,(ban_timer)        ; the announcement makes way for the wave
        or a
        call nz,banner_clear
        ld a,(wave_num)
        cp NUM_WAVES
        ret nc
        ld l,a
        ld h,0
        ld de,wave_table
        add hl,de
        ld l,(hl)               ; an offset into wave_data
        ld h,0
        ld de,wave_data
        add hl,de
        ld (sp_ptr),hl
        ld a,(wave_num)
        inc a
        ld (wave_num),a
        ld a,1
        ld (wave_state),a
        call load_group
        ld a,10
        ld (sp_timer),a
        ld a,(wave_num)
        cp NUM_WAVES
        jr nz,.nf
        ld a,B_FINAL
        ld c,#ff
        call msg_show
        ld a,100
        ld (msg_timer),a
        jr .s
.nf:    call msg_clear
.s:     ld a,SFX_WAVE
        call sfx_play
        ld a,HUDF_WAVE+HUDF_STATUS
        jp hud_set

load_group:
        ld hl,(sp_ptr)
        ld a,(hl)
        or a
        jr z,.end
        ld (sp_type),a
        inc hl
        ld a,(hl)
        ld (sp_left),a
        inc hl
        ld a,(hl)
        ld (sp_iv),a
        ld (sp_timer),a
        inc hl
        ld (sp_ptr),hl
        ret
.end:   xor a
        ld (sp_left),a
        ret

spawn_tick:
        ld a,(sp_left)
        or a
        ret z
        ld hl,sp_timer
        dec (hl)
        ret nz
        ld a,(sp_type)
        call spawn_enemy
        jr c,.ok
        ld a,1
        ld (sp_timer),a
        ret
.ok:    ld a,(sp_iv)
        ld (sp_timer),a
        ld hl,sp_left
        dec (hl)
        ret nz
        jp load_group

;------------------------------------------------------------------------------
; enemies
;------------------------------------------------------------------------------
; A = type -> carry if spawned
spawn_enemy:
        ld c,a
        ld ix,enemies
        ld b,MAX_EN
        ld de,EN_SZ
.f:     ld a,(ix+E_TYPE)
        or a
        jr z,.got
        add ix,de
        djnz .f
        or a
        ret
.got:   ld (ix+E_TYPE),c
        ld a,c
        call etype_ptr
        ld a,(wave_num)         ; hp: base + per wave * (wave + stage toughness)
        ld b,a
        ld a,(stage_unlock+3)
        add a,b
        ld b,a
        ld a,(hl)
        inc hl
        ld e,(hl)
        inc hl
.m:     add a,e
        jr nc,.k
        ld a,255
.k:     djnz .m
        ld (ix+E_HP),a
        ld (ix+E_MAXHP),a
        ld a,(hl)
        inc hl
        ld (ix+E_SPD),a
        ld a,(hl)
        ld (ix+E_ARM),a
        xor a
        ld (ix+E_ACC),a
        ld (ix+E_PROG),a
        ld (ix+E_PROG+1),a
        ld (ix+E_SLOW),a
        ld (ix+E_SEG),a
        call rand
        ld (ix+E_ANIM),a
        ld a,(gen_ctr)
        inc a
        ld (gen_ctr),a
        ld (ix+E_GEN),a
        call enemy_path
        ld a,(hl)
        ld (ix+E_X),a
        inc hl
        ld a,(hl)
        ld (ix+E_Y),a
        inc hl
        ld a,(hl)
        ld (ix+E_SUB),a
        inc hl
        ld a,(hl)
        ld (ix+E_REM),a
        ld hl,en_count
        inc (hl)
        scf
        ret

; IX = enemy -> HL = its path header
enemy_path:
        ld a,(ix+E_TYPE)
        cp ET_DRONE
        ld hl,path_ground
        ret nz
        ld hl,path_air
        ret

; IX = enemy -> HL = current segment (dx, dy, n)
enemy_seg:
        call enemy_path
        ld a,(ix+E_SEG)
        ld c,a
        add a,a
        add a,c
        add a,4
        ld c,a
        ld b,0
        add hl,bc
        ret

update_enemies:
        ld ix,enemies
        ld b,MAX_EN
.l:     push bc
        ld a,(ix+E_TYPE)
        or a
        call nz,enemy_move
        ld de,EN_SZ
        add ix,de
        pop bc
        djnz .l
        ret

enemy_move:
        ld c,(ix+E_SPD)
        ld a,(ix+E_SLOW)
        or a
        jr z,.ns
        dec (ix+E_SLOW)
        srl c
.ns:    ld a,(ix+E_ACC)
        add a,c
        ld c,a
        and 15
        ld (ix+E_ACC),a
        ld a,c
        rrca
        rrca
        rrca
        rrca
        and 15
        jr z,.anim
        ld b,a
.st:    push bc
        call enemy_step
        pop bc
        jr c,.arrived
        djnz .st
.anim:  inc (ix+E_ANIM)
        ld a,(ix+E_TYPE)
        cp ET_TANK
        ret nz
        ld a,(ix+E_ANIM)
        and 7
        ret nz
        jp tank_crush
.arrived:
        ld a,(ix+E_TYPE)
        call etype_ptr
        ld de,5
        add hl,de
        ld a,(hl)
        ld (ix+E_TYPE),0
        ld hl,en_count
        dec (hl)
        jp base_hit

; one step along the path -> carry if the kafenio was reached
enemy_step:
        call enemy_seg
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld a,(ix+E_Y)
        add a,b
        ld (ix+E_Y),a
        ld a,(ix+E_SUB)
        inc a
        cp 4                    ; x moves every fourth step (a cell is 16)
        jr c,.s
        ld a,(ix+E_X)
        add a,c
        ld (ix+E_X),a
        xor a
.s:     ld (ix+E_SUB),a
        inc (ix+E_PROG)
        jr nz,.p
        inc (ix+E_PROG+1)
.p:     or a
        dec (ix+E_REM)
        ret nz
        inc (ix+E_SEG)
        call enemy_seg
        inc hl
        inc hl
        ld a,(hl)
        or a
        jr z,.end
        ld (ix+E_REM),a
        ret
.end:   scf
        ret

; A = damage to the kafenio
base_hit:
        ld c,a
        ld a,(hp)
        sub c
        jr nc,.ok
        xor a
.ok:    ld (hp),a
        ld a,HUDF_HP
        call hud_set
        ld a,SFX_HURT
        call sfx_play
        ; fall through
update_sacks:
        ld a,(sacks_gone)
        cp NUM_SACKS
        ret nc
        ld b,a
        ld a,80
        inc b
        jr .t
.th:    sub 20
.t:     djnz .th
        ld c,a
        ld a,(hp)
        cp c
        jr z,.rm
        ret nc
.rm:    ld a,(sacks_gone)
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld bc,sack_cells
        add hl,bc
        ld d,(hl)
        inc hl
        ld e,(hl)
        inc hl
        inc hl
        ld a,(hl)
        push af
        call cell_offset
        ld bc,tilemap
        add hl,bc
        pop af
        ld (hl),a
        call redraw_cell
        ld hl,sacks_gone
        inc (hl)
        jr update_sacks

; IX = enemy ; A = damage ; C bit0 = ignore armour
damage_enemy:
        ld b,a
        bit 0,c
        jr nz,.na
        sub (ix+E_ARM)
        jr c,.min
        jr z,.min
        ld b,a
        jr .na
.min:   ld b,1
.na:    ld a,(ix+E_HP)
        sub b
        jr c,kill_enemy
        jr z,kill_enemy
        ld (ix+E_HP),a
        ret

kill_enemy:
        ld a,(ix+E_TYPE)
        push af
        call etype_ptr
        ld de,4
        add hl,de
        ld c,(hl)               ; the reward
        inc hl
        ld e,(hl)               ; points: the damage it would have done
        call pay
        ld (ix+E_TYPE),0
        ld hl,en_count
        dec (hl)
        pop af
        cp ET_TANK
        ld a,FX_BOOM
        jr z,.b
        ld a,FX_POOF
.b:     ld d,(ix+E_X)
        ld e,(ix+E_Y)
        call spawn_fx
        ld a,SFX_DIE
        call sfx_play
        ld a,HUDF_FUNDS+HUDF_TOP
        jp hud_set

; tanks dent cauldrons next to the road
tank_crush:
        ld a,(ix+E_X)
        add a,2
        rrca
        rrca
        and 63
        ld d,a
        ld a,(ix+E_Y)
        add a,8
        ld e,0
.dv:    sub 16
        jr c,.dd
        inc e
        jr .dv
.dd:    dec d
        call crush_at
        inc d
        inc d
        call crush_at
        dec d
        dec e
        call crush_at
        inc e
        inc e
        jp crush_at

crush_at:
        ld a,d
        cp NCOL
        ret nc
        ld a,e
        cp NROW
        ret nc
        push de
        call cell_ptr
        ld a,(hl)
        bit 7,a
        jr z,.o
        and #1f
        call tower_ptr
        ld a,(hl)
        cp TT_CAULDRON
        jr nz,.o
        push hl
        pop iy
        ld a,(iy+T_DIS)
        or a
        jr nz,.o
        ld (iy+T_DIS),125
        pop de
        push de
        call redraw_cell
        ld a,SFX_CRUSH
        call sfx_play
.o:     pop de
        ret

;------------------------------------------------------------------------------
; towers
;------------------------------------------------------------------------------
update_towers:
        ld iy,towers
        ld b,MAX_TW
.l:     push bc
        ld a,(iy+T_TYPE)
        or a
        call nz,tower_think
        ld de,TW_SZ
        add iy,de
        pop bc
        djnz .l
        ret

tower_think:
        ld a,(iy+T_DIS)
        or a
        jr z,.en
        dec (iy+T_DIS)
        ret nz
        ld d,(iy+T_COL)
        ld e,(iy+T_ROW)
        jp redraw_cell
.en:    ld a,(iy+T_CD)
        or a
        jr z,.rdy
        dec (iy+T_CD)
        ret
.rdy:   ld a,(tr_budget)        ; only a few towers look for a target per tick
        or a
        ret z
        dec a
        ld (tr_budget),a
        ld a,(iy+T_TYPE)
        call ttype_ptr
        inc hl
        ld a,(hl)
        ld (tr_range),a
        push hl
        call sq
        ld (tr_range2),hl
        pop hl
        inc hl
        ld a,(hl)
        ld (tr_cd),a
        inc hl
        call syn_dmg            ; the damage, with the neighbour bonus
        inc hl
        ld a,(hl)
        ld (tr_flags),a
        inc hl
        ld a,(hl)
        ld (tr_proj),a
        inc hl
        ld a,(hl)
        ld (tr_sfx),a
        call find_target
        jr c,.fire
        ld (iy+T_CD),4          ; nobody in range: look again later
        ret
.fire:  ld a,(tr_cd)
        ld (iy+T_CD),a
        ld a,(tr_sfx)
        call sfx_play
        ld a,(iy+T_TYPE)
        cp TT_YIAYIA
        jp z,fire_yiayia
        cp TT_CAULDRON
        jp z,fire_cauldron
        ld a,(tr_dmg)
        ld c,a
        ld b,0
        ld a,(iy+T_TYPE)
        cp TT_BRIDE
        jr nz,.nc
        call rand
        cp 64
        jr nc,.nc
        ld a,c
        add a,a
        add a,c
        ld c,a
        ld b,1
.nc:    ld a,(tr_proj)
        jp spawn_proj

; IY = tower -> carry and IX = the enemy furthest along within range
find_target:
        ld hl,0
        ld (best_prog),hl
        ld ix,enemies
        ld b,MAX_EN
.l:     push bc
        ld a,(ix+E_TYPE)
        or a
        jr z,.n
        cp ET_DRONE
        jr nz,.gnd
        ld a,(tr_flags)
        and 1
        jr z,.n
.gnd:   call in_range
        jr nc,.n
        ld l,(ix+E_PROG)
        ld h,(ix+E_PROG+1)
        inc hl
        ld de,(best_prog)
        push hl
        or a
        sbc hl,de
        pop hl
        jr c,.n
        jr z,.n
        ld (best_prog),hl
        ld (best_ix),ix
.n:     ld de,EN_SZ
        add ix,de
        pop bc
        djnz .l
        ld hl,(best_prog)
        ld a,h
        or l
        ret z
        ld ix,(best_ix)
        scf
        ret

; IX = enemy, IY = tower -> carry if within tr_range
in_range:
        ld a,(ix+E_X)
        add a,2
        sub (iy+T_CX)
        jr nc,.p1
        neg
.p1:    add a,a                 ; 4 pixels a unit
        add a,a
        ld c,a
        ld a,(tr_range)
        cp c
        jr c,.no
        ld a,(ix+E_Y)
        add a,8
        sub (iy+T_CY)
        jr nc,.p2
        neg
.p2:    ld e,a
        ld a,(tr_range)
        cp e
        jr c,.no
        ld a,c
        call sq
        push hl
        ld a,e
        call sq
        pop de
        add hl,de
        ex de,hl
        ld hl,(tr_range2)
        or a
        sbc hl,de
        ccf
        ret
.no:    or a
        ret

; slows every walker in reach and whacks the target
fire_yiayia:
        push ix
        ld ix,enemies
        ld b,MAX_EN
.l:     push bc
        ld a,(ix+E_TYPE)
        or a
        jr z,.n
        cp ET_DRONE
        jr z,.n
        call in_range
        jr nc,.n
        ld (ix+E_SLOW),40
.n:     ld de,EN_SZ
        add ix,de
        pop bc
        djnz .l
        pop ix
        ld d,(ix+E_X)
        ld e,(ix+E_Y)
        ld a,FX_BASH
        call spawn_fx
        ld a,(tr_dmg)
        ld c,0
        jp damage_enemy

; toxic cloud: hurts (ignoring armour) and slows every walker in reach
fire_cauldron:
        ld a,2                  ; draw at most two clouds per throw
        ld (tmp_idx),a
        ld ix,enemies
        ld b,MAX_EN
.l:     push bc
        ld a,(ix+E_TYPE)
        or a
        jr z,.n
        cp ET_DRONE
        jr z,.n
        call in_range
        jr nc,.n
        ld (ix+E_SLOW),30
        ld a,(tmp_idx)
        or a
        jr z,.nofx
        dec a
        ld (tmp_idx),a
        ld d,(ix+E_X)
        ld e,(ix+E_Y)
        ld a,FX_PUFF
        call spawn_fx
.nofx:  ld a,(tr_dmg)
        ld c,1
        call damage_enemy
.n:     ld de,EN_SZ
        add ix,de
        pop bc
        djnz .l
        ret

;------------------------------------------------------------------------------
; projectiles
;------------------------------------------------------------------------------
; A = type, C = damage, B = flags, IX = target, IY = tower
spawn_proj:
        ld (sp_ptype),a
        ld a,c
        ld (sp_pdmg),a
        ld a,b
        ld (sp_pflag),a
        ld hl,projs
        ld de,PR_SZ
        ld b,MAX_PR
.f:     ld a,(hl)
        or a
        jr z,.got
        add hl,de
        djnz .f
        ret
.got:   ld a,(sp_ptype)
        ld (hl),a
        inc hl
        ld a,(iy+T_CX)
        add a,a
        ld (hl),a
        inc hl
        ld a,(iy+T_CY)
        sub 6
        ld (hl),a
        inc hl
        push hl
        push ix
        pop hl
        ld de,enemies
        or a
        sbc hl,de
        ld a,l
        rrca
        rrca
        rrca
        rrca
        and 15
        pop hl
        ld (hl),a
        inc hl
        ld a,(sp_pdmg)
        ld (hl),a
        inc hl
        ld a,(sp_pflag)
        ld (hl),a
        inc hl
        ld a,(ix+E_X)
        add a,2
        add a,a
        ld (hl),a
        inc hl
        ld a,(ix+E_Y)
        add a,8
        ld (hl),a
        inc hl
        ld a,(ix+E_GEN)
        ld (hl),a
        ret

update_projs:
        ld iy,projs
        ld b,MAX_PR
.l:     push bc
        ld a,(iy+P_TYPE)
        or a
        call nz,proj_step
        ld de,PR_SZ
        add iy,de
        pop bc
        djnz .l
        ret

proj_step:
        ld a,(iy+P_TGT)
        add a,a
        add a,a
        add a,a
        add a,a
        ld e,a
        ld d,0
        ld ix,enemies
        add ix,de
        ld a,(ix+E_TYPE)
        or a
        jr z,.lost
        ld a,(ix+E_GEN)
        cp (iy+P_GEN)
        jr nz,.lost
        ld a,(ix+E_X)
        add a,2
        add a,a
        ld (iy+P_TX),a
        ld a,(ix+E_Y)
        add a,8
        ld (iy+P_TY),a
        jr .mv
.lost:  set 7,(iy+P_FLAG)
.mv:    ld a,(iy+P_TYPE)
        dec a
        add a,a
        ld e,a
        ld d,0
        ld hl,proj_speed
        add hl,de
        ld c,(hl)
        inc hl
        ld b,(hl)
        ld e,0
        ld a,(iy+P_TX)
        sub (iy+P_X)
        jr c,.xl
        cp c
        jr nc,.xr
        ld c,a
        set 0,e
.xr:    ld a,(iy+P_X)
        add a,c
        ld (iy+P_X),a
        jr .y
.xl:    neg
        cp c
        jr nc,.xl2
        ld c,a
        set 0,e
.xl2:   ld a,(iy+P_X)
        sub c
        ld (iy+P_X),a
.y:     ld a,(iy+P_TY)
        sub (iy+P_Y)
        jr c,.yu
        cp b
        jr nc,.yd
        ld b,a
        set 1,e
.yd:    ld a,(iy+P_Y)
        add a,b
        ld (iy+P_Y),a
        jr .chk
.yu:    neg
        cp b
        jr nc,.yu2
        ld b,a
        set 1,e
.yu2:   ld a,(iy+P_Y)
        sub b
        ld (iy+P_Y),a
.chk:   ld a,e
        cp 3
        ret nz
        ; impact
        ld a,(iy+P_TYPE)
        ld (iy+P_TYPE),0
        cp PT_DAKOS
        jr z,.splash
        push af
        ld a,(iy+P_X)
        srl a
        dec a
        ld d,a
        ld a,(iy+P_Y)
        sub 2
        ld e,a
        pop af
        push af
        cp PT_LASER
        ld a,FX_ZAP
        jr z,.z
        ld a,FX_SPARK
.z:     call spawn_fx
        pop af
        bit 7,(iy+P_FLAG)
        ret nz
        cp PT_LASER
        jr nz,.d
        ld a,(ix+E_ARM)
        or a
        jr z,.d
        dec (ix+E_ARM)
.d:     ld a,(iy+P_DMG)
        ld c,0
        jp damage_enemy
.splash:
        ld a,(iy+P_X)
        srl a
        sub 2
        ld d,a
        ld a,(iy+P_Y)
        sub 6
        ld e,a
        ld a,FX_BASH
        call spawn_fx
        ld ix,enemies
        ld b,MAX_EN
.sl:    push bc
        ld a,(ix+E_TYPE)
        or a
        jr z,.sn
        ld a,(iy+P_X)
        srl a
        ld c,a
        ld a,(ix+E_X)
        add a,2
        sub c
        jr nc,.sp
        neg
.sp:    cp 5
        jr nc,.sn
        ld a,(ix+E_Y)
        add a,8
        sub (iy+P_Y)
        jr nc,.sq
        neg
.sq:    cp 17
        jr nc,.sn
        ld a,(iy+P_DMG)
        ld c,0
        call damage_enemy
.sn:    ld de,EN_SZ
        add ix,de
        pop bc
        djnz .sl
        ret

;------------------------------------------------------------------------------
; effects
;------------------------------------------------------------------------------
; A = type, D,E = x,y (clamped to the playfield).  Preserves IX, IY.
spawn_fx:
        push hl
        push bc
        ld c,a
        ld hl,fxs
        ld b,MAX_FX
.f:     ld a,(hl)
        or a
        jr z,.got
        inc hl
        inc hl
        inc hl
        inc hl
        djnz .f
        jr .out
.got:   ld (hl),c
        inc hl
        ld a,d
        cp 128
        jr c,.x1
        xor a
.x1:    cp 57
        jr c,.x2
        ld a,56
.x2:    ld (hl),a
        inc hl
        ld a,e
        cp 200
        jr c,.y1
        xor a
.y1:    cp 149
        jr c,.y2
        ld a,148
.y2:    ld (hl),a
        inc hl
        push hl
        ld a,c
        call fx_ptr
        ld de,4
        add hl,de
        ld a,(hl)
        pop hl
        ld (hl),a
.out:   pop bc
        pop hl
        ret

; A = effect type -> HL = fx_tab entry
fx_ptr:
        dec a
        add a,a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld de,fx_tab
        add hl,de
        ret

update_fx:
        ld hl,fxs
        ld b,MAX_FX
.l:     ld a,(hl)
        or a
        jr z,.n
        inc hl
        inc hl
        inc hl
        dec (hl)
        dec hl
        dec hl
        dec hl
        jr nz,.n
        ld (hl),0
.n:     inc hl
        inc hl
        inc hl
        inc hl
        djnz .l
        ret


;------------------------------------------------------------------------------
; drawing the sprites into the work buffer (render, gfx.asm, calls these)
;------------------------------------------------------------------------------
draw_enemies:
        ld ix,enemies
        ld b,MAX_EN
.l:     push bc
        ld a,(ix+E_TYPE)
        or a
        jr z,.n
        call enemy_sprite_idx
        ld l,a
        ld h,0
        add hl,hl
        ld de,enemy_sprites
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ld a,(ix+E_X)           ; x 4 pixels a unit
        add a,a
        add a,a
        ld d,a
        ld a,(ix+E_Y)           ; 12 lines high, in a cell of 16
        add a,2
        ld e,a
        call draw_sprite
.n:     ld de,EN_SZ
        add ix,de
        pop bc
        djnz .l
        ret

enemy_sprite_idx:
        call enemy_seg
        ld a,(hl)
        or a
        jr z,.dn
        ld a,1
        jp m,.dn
        inc a
.dn:    ld e,a
        ld a,(ix+E_TYPE)
        dec a
        ld d,a
        add a,a
        add a,d
        add a,e
        add a,a
        ld e,a
        ld a,(ix+E_ANIM)
        rrca
        rrca
        and 1
        add a,e
        ret

; after the restore

draw_projs:
        ld iy,projs
        ld b,MAX_PR
.l:     push bc
        ld a,(iy+P_TYPE)
        or a
        jr z,.n
        dec a
        add a,a
        ld e,a
        ld d,0
        ld hl,proj_sprites
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        bit 0,(iy+P_FLAG)
        jr z,.s
        ld hl,spr_pistol_crit
.s:     ld a,(iy+P_X)           ; Mode 0 pixels: two of ours
        add a,a
        ld d,a
        ld e,(iy+P_Y)
        call draw_sprite
.n:     ld de,PR_SZ
        add iy,de
        pop bc
        djnz .l
        ret

draw_fx:
        ld iy,fxs
        ld b,MAX_FX
.l:     push bc
        ld a,(iy+F_TYPE)
        or a
        jr z,.n
        call fx_ptr
        bit 2,(iy+F_T)
        jr z,.a
        inc hl
        inc hl
.a:     ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ld a,(iy+F_X)
        add a,a
        add a,a
        ld d,a
        ld e,(iy+F_Y)
        call draw_sprite
.n:     ld de,FX_SZ
        add iy,de
        pop bc
        djnz .l
        ret

draw_flag:
        ld hl,spr_flag_a
        ld a,(framecnt)
        and 16
        jr z,.a
        ld hl,spr_flag_b
.a:     ld de,(stage_flag)      ; x, y (pixels)
        jp draw_sprite

draw_cursor:
        ld a,(game_over)        ; not over the end banner
        or a
        ret nz
        call cur_cell
        bit 7,(hl)
        jr nz,.ok
        call can_build
        jr c,.bad
        ld a,(sel_type)
        call ttype_ptr
        ld c,(hl)
        ld b,0
        ld hl,(funds)
        or a
        sbc hl,bc
        jr c,.bad
.ok:    ld hl,spr_cursor_ok
        ld a,(framecnt)
        and 8
        jr z,.d
        ld hl,spr_cursor_ok_b
        jr .d
.bad:   ld hl,spr_cursor_bad
.d:     push hl
        ld a,(cur_c)
        ld d,a
        ld a,(cur_r)
        ld e,a
        call cell_xy
        pop hl
        jp draw_sprite

;------------------------------------------------------------------------------
; banner messages (drawn into the background, cell rows 4-5: attribute rows
; 9-12 of the screen)
;------------------------------------------------------------------------------
BAN_ROW equ 4                   ; cell rows 4-5
BAN_Y equ BAN_ROW*16
BAN_H equ 32
BAN_AROW equ (PF_Y+BAN_Y)/8

; A = first string, C = second string (#FF none)
banner_show:
        ld (ban_id1),a
        ld a,c
        ld (ban_id2),a
        ld a,1
        ld (ban_on),a
        xor a
        ld (ban_timer),a
banner_draw:                    ; at the next frame
        ld a,1
        ld (ban_req),a
        ret

ban_do_draw:
        push de
        call tgt_bg
        ld de,BAN_Y
        ld bc,BAN_H*256+PF_W
        xor a
        call fill_rect
        call text_normal
        ld a,(ban_id1)
        ld e,PF_Y+BAN_Y+8
        call print_id_centered
        ld a,(ban_id2)
        cp #ff
        jr z,.m
        ld e,PF_Y+BAN_Y+16
        call print_id_centered
.m:     ld de,BAN_Y             ; the frame: top and bottom lines...
        ld bc,1*256+PF_W
        ld a,#ff
        call fill_rect
        ld de,BAN_Y+BAN_H-1
        ld bc,1*256+PF_W
        ld a,#ff
        call fill_rect
        ld b,BAN_H              ; ...and the sides
        ld e,BAN_Y
.sd:    push bc
        ld d,0
        call line_addr
        set 7,(hl)
        ld bc,PF_W-1
        add hl,bc
        set 0,(hl)
        inc e
        pop bc
        djnz .sd
        ld de,PF_COL*256+BAN_AROW
        ld bc,1*256+PF_W
        ld a,A_BAN1
        call attr_rect
        ld de,PF_COL*256+BAN_AROW+1
        ld bc,1*256+PF_W
        ld a,A_BAN1
        call attr_rect
        ld de,PF_COL*256+BAN_AROW+2
        ld bc,2*256+PF_W
        ld a,A_BAN2
        call attr_rect
        ld de,BAN_Y
        ld bc,BAN_H*256+PF_W
        call dirty_add_both
        pop de
        ret

banner_clear:
        ld a,(ban_on)
        or a
        ret z
        xor a
        ld (ban_on),a
        ld (ban_timer),a
        ld a,2                  ; at the next frame
        ld (ban_req),a
        ret

ban_do_clear:
        ld e,BAN_ROW
.r:     ld d,0
.c:     push de
        call redraw_cell_nd
        pop de
        inc d
        ld a,d
        cp NCOL
        jr nz,.c
        inc e
        ld a,e
        cp BAN_ROW+2
        jr nz,.r
        ld hl,ban_attr          ; the stage's colours back
        ld de,ATTRS+BAN_AROW*32+PF_COL
        ld b,4
.a:     push bc
        ld bc,PF_W
        ldir
        ex de,hl
        ld bc,32-PF_W
        add hl,bc
        ex de,hl
        pop bc
        djnz .a
        ld de,BAN_Y
        ld bc,BAN_H*256+PF_W
        jp dirty_add_both

banner_tick:                    ; the stage's announcement goes after a while
        ld a,(ban_timer)
        or a
        jr z,.m
        dec a
        ld (ban_timer),a
        call z,banner_clear
.m:     ld a,(msg_on)           ; two lines that do not fit side by side in
        or a                    ; the top bar take turns, two seconds each
        jr z,.t
        ld hl,msg_alt_t
        dec (hl)
        jr nz,.t
        ld (hl),50
        ld a,(msg_alt)
        xor 1
        ld (msg_alt),a
        ld a,(msg_fits)
        or a
        ld a,HUDF_TOP
        call z,hud_set
.t:     ld a,(msg_timer)        ; timed messages in the top bar
        or a
        ret z
        dec a
        ld (msg_timer),a
        ret nz
        ; fall through
msg_clear:
        ld a,(msg_on)
        or a
        ret z
        xor a
        ld (msg_on),a
        ld a,HUDF_TOP
        jp hud_set

; A = first string, C = second string (#FF none): shown in the top bar,
; away from the playfield
msg_show:
        ld (msg_id1),a
        ld a,c
        ld (msg_id2),a
        ld a,1
        ld (msg_on),a
        xor a
        ld (msg_timer),a
        ld (msg_alt),a
        ld a,50
        ld (msg_alt_t),a
        ld a,HUDF_TOP
        jp hud_set

;------------------------------------------------------------------------------
; HUD: the top bar (line 0) and two lines under the playfield (176, 184)
;------------------------------------------------------------------------------
HUD_Y1 equ 176
HUD_Y2 equ 184

hud_full:
        call tgt_scr
        ld de,0                 ; the HUD's three rows: black
        ld bc,1*256+32
        ld a,A_TEXT
        call attr_rect
        ld de,22
        ld bc,2*256+32
        ld a,A_TEXT
        call attr_rect
        call hud_top
        ld de,HUD_Y1
        ld c,64
        call clear_text
        call hud_labels
        call hud_wave
        call hud_funds
        call hud_hp
        call hud_info
        jp hud_status

; the pending HUD changes, straight to the screen
hud_refresh:
        ld a,(hud_flags)
        bit 3,a                 ; funds changed: did the selection become (un)affordable?
        jr z,.k0
        call sel_affordable
        ld hl,hud_aff
        cp (hl)
        jr z,.k0
        ld (hl),a
        ld a,HUDF_INFO
        call hud_set
.k0:    ld hl,hud_flags
        ld a,(hl)
        or a
        ret z
        ld (hl),0
        ld (hud_cur),a
        call tgt_scr
        ld hl,hud_jobs
        ld b,6
.k1:    ld a,(hud_cur)
        and (hl)
        inc hl
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        jr z,.k2
        push hl
        push bc
        ex de,hl
        call call_hl
        pop bc
        pop hl
.k2:    djnz .k1
        ret

call_hl:
        jp (hl)

hud_jobs:
        db HUDF_TOP
        dw hud_top
        db HUDF_WAVE
        dw hud_wave
        db HUDF_FUNDS
        dw hud_funds
        db HUDF_HP
        dw hud_hp
        db HUDF_INFO
        dw hud_info
        db HUDF_STATUS
        dw hud_status

; A = 1 if the selected defender can be paid for
sel_affordable:
        ld a,(sel_type)
        call ttype_ptr
        ld c,(hl)
        ld b,0
        ld hl,(funds)
        or a
        sbc hl,bc
        ld a,0
        ccf
        rla
        ret

hud_top:
        ld de,0
        ld c,64
        call clear_text
        call text_normal
        ld a,(msg_on)
        or a
        jr z,.title
        ; a message: the first line on the left, the second on the right,
        ; or by turns when they do not fit
        ld a,(msg_id1)
        call get_str
        call str_len
        ld b,c
        ld c,0
        ld a,(msg_id2)
        cp #ff
        jr z,.l2
        push bc
        call get_str
        call str_len
        pop de
        ld b,d                  ; B = first, C = second length
.l2:    ld a,b
        add a,c
        add a,2
        cp 65
        ld a,0
        jr nc,.nf
        inc a
.nf:    ld (msg_fits),a
        ld a,c
        ld (tmp_y),a
        ld a,(msg_fits)
        or a
        jr nz,.one
        ld a,(msg_id2)
        cp #ff
        jr z,.one
        ld a,(msg_alt)
        or a
        jr nz,.two
.one:   ld a,A_YEL
        call set_attr
        ld de,0
        call set_at
        ld a,(msg_id1)
        call print_id
        ld a,(msg_fits)
        or a
        ret z
        ld a,(msg_id2)
        cp #ff
        ret z
        ld a,(tmp_y)            ; the second, right-aligned (an even column)
        neg
        add a,64
        and #fe
        ld d,a
        jr .w
.two:   ld d,0
.w:     ld a,A_WHI
        call set_attr
        ld e,0
        call set_at
        ld a,(msg_id2)
        jp print_id
.title: ld a,A_YEL
        call set_attr
        ld de,0
        call set_at
        ld a,S_TITLE
        call print_id
        ld a,A_WHI              ; the score and the lives
        call set_attr
        ld de,44*256
        call set_at
        ld a,S_SCORE
        call print_id
        ld hl,(score)
        ld a,5
        ld (pn_zero),a
        call print_num
        xor a
        ld (pn_zero),a
        ld a,S_LIVES
        call print_id
        ld a,(rt_lives)
        ld l,a
        ld h,0
        ld a,1
        jp print_num

hud_wave:
        ld de,HUD_Y1
        ld c,12
        call clear_text
        call text_normal
        ld a,A_WHI
        call set_attr
        ld de,HUD_Y1
        call set_at
        ld a,S_WAVE
        call print_id
        ld a,A_YEL
        call set_attr
        ld de,6*256+HUD_Y1
        call set_at
        ld a,1
        ld (pn_zero),a
        ld a,(wave_num)
        ld l,a
        ld h,0
        ld a,2
        call print_num
        ld a,GLYPH_SLASH
        call put_glyph
        ld hl,NUM_WAVES
        ld a,2
        call print_num
        xor a
        ld (pn_zero),a
        ret

hud_labels:
        call text_normal
        ld a,A_WHI
        call set_attr
        ld de,14*256+HUD_Y1
        call set_at
        ld a,S_FUNDS
        call print_id
        ld de,30*256+HUD_Y1
        call set_at
        ld a,S_HP
        jp print_id

hud_funds:
        call text_normal
        ld a,A_YEL
        call set_attr
        ld de,22*256+HUD_Y1
        call set_at
        ld hl,(funds)
        ld a,4
        jp print_num

hud_hp:
        call text_normal
        ld a,(hp)
        cp 30
        ld a,A_YEL
        jr nc,.hc
        ld a,A_RED
.hc:    call set_attr
        ld de,34*256+HUD_Y1
        call set_at
        ld a,(hp)
        ld l,a
        ld h,0
        ld a,3
        jp print_num

hud_status:
        ld de,42*256+HUD_Y1
        ld c,8
        call clear_text
        call text_normal
        ld de,42*256+HUD_Y1
        call set_at
        ld a,(paused)
        or a
        jr z,.np
        ld a,A_RED
        call set_attr
        ld a,S_PAUSE
        jp print_id
.np:    ld a,(wave_state)
        or a
        jr z,.wait
        ld a,A_GRN
        call set_attr
        ld a,S_GO
        jp print_id
.wait:  ld a,A_CYN
        call set_attr
        ld a,S_NEXT
        call print_id
        ld a,1
        ld (pn_zero),a
        ld a,(cd_sec)
        ld l,a
        ld h,0
        ld a,2
        call print_num
        xor a
        ld (pn_zero),a
        ret

hud_info:
        ld de,HUD_Y2
        ld c,64
        call clear_text
        call text_normal
        ld de,HUD_Y2
        call set_at
        call cur_cell
        ld a,(hl)
        bit 7,a
        jr z,.build
        and #1f
        call tower_ptr
        ld a,(hl)
        push af
        add a,S_NAME1-1
        push af
        ld a,A_WHI
        call set_attr
        pop af
        call print_id
        ld a,A_YEL
        call set_attr
        ld de,22*256+HUD_Y2
        call set_at
        ld a,S_SELL
        call print_id
        pop af
        call ttype_ptr
        ld de,7
        add hl,de
        ld l,(hl)
        ld h,0
        ld a,3
        jp print_num
.build: call sel_affordable
        ld (hud_aff),a
        or a
        ld a,A_YEL
        jr nz,.aff
        ld a,A_GRY
.aff:   call set_attr
        ld a,(sel_type)
        add a,S_INFO1-1
        call print_id
        jp syn_hud              ; and the neighbour bonus here


;------------------------------------------------------------------------------
; the neighbour bonus: a defender hits harder or softer when one of its
; partner type sits right next to it (left, right, above or below):
;   a Bride next to a Cretan       +50%
;   a Yiayia next to a Baker       +20%
;   a Baker next to a Cretan       -50%
;   Psssst next to a Cretan        -20%
; Only three defenders at a time get a bonus (syn_update); the penalties
; always count.  Before a defender is built, the bonus it would get there
; shows at the end of the info line, green or red.
;------------------------------------------------------------------------------
; per defender type: partner type (0: none), damage factor in 16ths, its text
syn_tab:
        db 0,0
        dw 0                                    ; cretan
        db TT_BAKER,19
        dw syn_t20p                             ; yiayia
        db TT_CRETAN,24
        dw syn_t50p                             ; bride
        db TT_CRETAN,13
        dw syn_t20m                             ; psssst
        db 0,0
        dw 0                                    ; cauldron
        db TT_CRETAN,8
        dw syn_t50m                             ; baker
syn_t50p: db G_PLUS,G_5,G_0,G_PCT,#ff
syn_t20p: db G_PLUS,G_2,G_0,G_PCT,#ff
syn_t50m: db G_MINUS,G_5,G_0,G_PCT,#ff
syn_t20m: db G_MINUS,G_2,G_0,G_PCT,#ff

; A = type, D,E = col,row -> NZ and HL = its syn_tab entry when a partner
; is next door, Z when not.  Uses A, BC.
syn_find:
        dec a
        add a,a
        add a,a
        ld l,a
        ld h,0
        ld bc,syn_tab
        add hl,bc
        ld a,(hl)
        or a
        ret z
        ld (syn_loop+2),a       ; the partner, into the CP below
        push hl
        ld hl,towers
        ld b,MAX_TW
syn_loop:
        ld a,(hl)               ; T_TYPE
        cp 0
        jr nz,.n
        inc hl
        ld a,(hl)               ; T_COL
        inc hl
        ld c,(hl)               ; T_ROW
        dec hl
        dec hl
        sub d
        jr z,.col               ; same column: the rows one apart
        inc a                   ; else the columns one apart...
        and #fd
        jr nz,.n
        ld a,c                  ; ...on the same row
        cp e
        jr z,.hit
        jr .n
.col:   ld a,c
        sub e
        inc a
        and #fd
        jr z,.hit
.n:     ld a,l                  ; the towers fill one page
        add a,TW_SZ
        ld l,a
        djnz syn_loop
        pop hl
        xor a
        ret
.hit:   pop hl
        or 1
        ret

; tower_think, instead of ld a,(hl) / ld (tr_dmg),a: HL = the damage in the
; tower's stats, IY = tower, with its factor from syn_update.  Preserves HL;
; uses A, BC, DE.
syn_dmg:
        ld a,(hl)
        ld (tr_dmg),a
        ld b,(iy+T_SYN)
        inc b
        dec b
        ret z
        push hl
        ld e,a                  ; damage * factor / 16, rounded
        ld d,0
        ld hl,8
.m:     add hl,de
        djnz .m
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld a,h
        ld (tr_dmg),a
        pop hl
        ret

; hud_info, after the selected defender's line: the bonus it would get on
; the cursor cell
syn_hud:
        call cur_cell
        ld a,(sel_type)
        call syn_find
        ret z
        inc hl
        ld a,(hl)               ; factor: above 16 a bonus, below a penalty
        call syn_room
        ret nc                  ; a bonus, but three defenders have one
        inc hl
        ld c,(hl)
        inc hl
        ld h,(hl)
        ld l,c
        push hl
        cp 17
        ld a,A_GRN
        jr nc,.c
        ld a,A_RED
.c:     call set_attr
        ld de,56*256+HUD_Y2
        call set_at
        pop hl
        jp print_str

;------------------------------------------------------------------------------
; the score: the damage an invader would have done, for each one stopped; the
; damage of each defender built (taken away again when it is sold); the
; seconds left when a wave is called early; the vrouves left after a stage
;------------------------------------------------------------------------------
; try_build: the defender's price paid, its damage as points
sc_build:
        ld a,(tmp_cost)
        ld c,a
        ld b,0
        ld hl,(funds)
        or a
        sbc hl,bc
        ld (funds),hl
        ld a,(sel_type)
        call ttype_ptr
        inc hl
        inc hl
        inc hl
        ld c,(hl)               ; its damage
        ld b,0
        jp score_add

; try_sell, HL = the defender's stats: half its price back, its points gone
sc_sell:
        push hl
        ld de,7
        add hl,de
        ld c,(hl)
        ld b,0
        ld hl,(funds)
        add hl,bc
        ld (funds),hl
        pop hl
        inc hl
        inc hl
        inc hl
        ld c,(hl)
        ld hl,(score)
        or a
        sbc hl,bc
        jr nc,.s
        ld hl,0
.s:     ld (score),hl
        ret

;------------------------------------------------------------------------------
; the lives of the difficulty chosen on the title (Easy 4, Medium 3, Hard 2,
; Hardest none): a stage lost with a life left is played again, with the
; score as it was when the stage began
;------------------------------------------------------------------------------
; after game_run.  Carry: on as before (won, quit, or lost with no life
; left); no carry: lost, a life gone, play the stage again.
rt_retry:
        ld hl,(score)
        ld a,(game_over)
        cp 2
        jr z,.lost
        ld (rt_chk),hl          ; won (or quit): the score to go back to
        scf
        ret
.lost:  ld a,(rt_lives)
        sub 1
        ret c
        ld (rt_lives),a
        ld hl,(rt_chk)
        ld (score),hl
        ret

; as the title hands over to the game: a new score, the lives
rt_start:
        ld hl,0
        ld (score),hl
        ld (rt_chk),hl
        ld hl,dif_lives
        ld a,(difficulty)
        add a,l
        ld l,a
        jr nc,.d
        inc h
.d:     ld a,(hl)
        ld (rt_lives),a
        ret

dif_lives: db 3,2,0,4
