;==============================================================================
; title.asm - the title screen: a scene and the keys, the story, the
; defenders, the invaders and the high scores, a page at a time; the name
; for a new high score (the table lasts while the Spectrum is on)
;==============================================================================
TITLE_PAGE_FRAMES equ 450
TITLE_PAGES equ 5
HS_PAGE     equ 4
HS_N        equ 8
TP_Y        equ 24              ; the pages: lines 24-167
TSCENE_Y    equ 32              ; the scene on the first page

title_screen:
        call tgt_scr
        call cls_black
        call cls
        call title_static
        xor a
        ld (tpage),a
        call title_page
        call hs_check           ; a new high score: the name, then the table
        ld hl,0
        ld (ttimer),hl
.loop:  call wait_frame
        call kbd_update
        ld a,K_L
        call key_hit
        jr nc,.nl
        ld a,(lang)
        xor 1
        ld (lang),a
        call title_static
        call title_page
.nl:    ld a,K_D
        call key_hit
        jr nc,.nd
        ld a,(difficulty)
        inc a
        and 3
        ld (difficulty),a
        call title_dif
.nd:    ld a,K_M
        call key_hit
        call c,toggle_music
        ld a,K_RIGHT
        call key_hit
        jr c,.next
        ld a,J_RIGHT
        call key_hit
        jr c,.next
        ld a,K_P
        call key_hit
        jr c,.next
        call fire_hit
        ret c                   ; into the game
        ld hl,(ttimer)
        inc hl
        ld (ttimer),hl
        ld de,TITLE_PAGE_FRAMES
        or a
        sbc hl,de
        jr c,.loop
.next:  ld hl,0
        ld (ttimer),hl
        ld a,(tpage)
        inc a
        cp TITLE_PAGES
        jr c,.p
        xor a
.p:     ld (tpage),a
        call title_page
        jr .loop

; the title, the difficulty, and the lines at the bottom
title_static:
        call tgt_scr
        ld de,0
        ld c,64
        call clear_text
        ld de,8
        ld c,64
        call clear_text
        call text_big
        ld a,A_YEL
        call set_attr
        ld a,S_TITLE            ; in the active language only
        ld e,0
        call print_id_centered
        call text_normal
        ld de,168
        ld c,64
        call clear_text
        ld de,176
        ld c,64
        call clear_text
        ld de,184
        ld c,64
        call clear_text
        ld a,A_YEL
        call set_attr
        ld a,T_START
        ld e,168
        call print_id_centered
        ld a,A_WHI
        call set_attr
        ld a,S_LANGHINT
        ld e,176
        call print_id_centered
        ld a,A_GRY
        call set_attr
        ld a,T_CREDIT
        ld e,184
        call print_id_centered
        ld e,168                ; a line over them, in the colour of the first
        call hline
        ; fall through

; under the title: the difficulty, and its lives, with a line under it
title_dif:
        call tgt_scr
        ld de,16
        ld c,64
        call clear_text
        call text_normal
        ld a,A_CYN
        call set_attr
        ld a,(difficulty)
        add a,T_DIF0
        ld e,16
        call print_id_centered
        ld e,23
; E = line: a line of ink across the screen
hline:
        ld d,0
        call line_addr
        ld b,32
.l:     ld (hl),#ff
        inc hl
        djnz .l
        ret

title_page:
        call page_clear
        call text_normal
        ld a,(tpage)
        cp HS_PAGE
        jp z,hs_show
        or a
        jp z,.keys
        dec a
        jp z,.story
        dec a
        jr z,.def
        ld a,A_RED
        call set_attr
        ld a,T_ENEHDR
        ld e,32
        call print_id_centered
        ld hl,inv_list
        jr .cast
.def:   ld a,A_YEL
        call set_attr
        ld a,T_DEFHDR
        ld e,32
        call print_id_centered
        ld hl,def_list
.cast:  ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,d
        or e
        ret z
        ld a,(hl)
        inc hl
        ld (tmp_i),a
        ld a,(hl)
        inc hl
        ld (tmp_y),a
        ld c,(hl)               ; the inks, top and bottom (as in the game)
        inc hl
        ld b,(hl)
        inc hl
        push hl
        push de
        push bc
        ld a,(tmp_y)            ; a patch of grass behind the sprite
        rrca
        rrca
        rrca
        and 31
        ld e,a
        ld d,2
        ld a,A_GRASS
        or c
        ld bc,1*256+2
        push de
        call attr_rect
        pop de
        inc e
        pop bc
        ld a,A_GRASS
        or b
        ld bc,1*256+2
        call attr_rect
        pop hl
        ld a,(tmp_y)
        add a,2
        ld e,a
        ld d,16
        call draw_sprite_raw
        ld a,(tmp_y)
        ld e,a
        ld d,8
        call set_at
        ld a,A_WHI
        call set_attr
        ld a,(tmp_i)
        call print_id
        pop hl
        jr .cast
.story: ld a,A_WHI
        call set_attr
        ld de,2*256+32
        call set_at
        ld a,T_STORY
        jp print_id
.keys:  call title_scene
        ld a,A_YEL
        call set_attr
        ld de,4*256+112
        call set_at
        ld a,T_KEYS
        call print_id
        ld de,36*256+112
        call set_at
        ld a,T_KEYS2
        call print_id
        ld a,A_WHI
        call set_attr
        ld de,16*256+112
        call set_at
        ld a,T_CTRL
        call print_id
        ld de,44*256+112
        call set_at
        ld a,T_CTRL2
        jp print_id

; the page area: blank, white on black
page_clear:
        call tgt_scr
        ld de,TP_Y
        ld bc,144*256+32
        xor a
        call fill_rect
        ld de,TP_Y/8
        ld bc,18*256+32
        ld a,A_TEXT
        jp attr_rect

; the first page's scene: a corner of the Kafenio, the defenders at work
title_scene:
        ld hl,tscene            ; its tile map and colours, into the work buffer
        ld de,WORKBUF
        call lz_unpack
        ld hl,WORKBUF
        ld e,TSCENE_Y
        ld b,TSCENE_ROWS
.r:     push bc
        ld d,PF_X
        ld b,NCOL
.c:     push bc
        push hl
        push de
        ld l,(hl)
        ld h,0
        add hl,hl
        ld bc,tscene_tiles
        add hl,bc
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        call draw_tile
        pop de
        pop hl
        inc hl
        ld a,d
        add a,16
        ld d,a
        pop bc
        djnz .c
        ld a,e
        add a,16
        ld e,a
        pop bc
        djnz .r
        ld de,ATTRS+(TSCENE_Y/8)*32+PF_COL
        ld b,TSCENE_ROWS*2
.a:     push bc
        ld bc,PF_W
        ldir
        ex de,hl
        ld bc,32-PF_W
        add hl,bc
        ex de,hl
        pop bc
        djnz .a
        ld hl,tscene_cast
.s:     ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld a,d
        or e
        ret z
        ld a,(hl)
        inc hl
        ld c,(hl)
        inc hl
        push hl
        ex de,hl
        add a,PF_X
        ld d,a
        ld a,c
        add a,TSCENE_Y
        ld e,a
        call draw_sprite_raw
        pop hl
        jr .s

; sprite, x, y in the scene (the first stage's bottom half)
tscene_cast:
        dw spr_flag_a
        db 42,11
        dw spr_guard_a
        db 128,34
        dw spr_guard_b
        db 160,50
        dw spr_tank_la
        db 144,66
        dw spr_drone_a
        db 192,18
        dw spr_drone_b
        db 216,50
        dw spr_cretan
        db 80,18
        dw spr_yiayia
        db 144,18
        dw spr_psssst
        db 112,16
        dw spr_bride
        db 112,50
        dw spr_cauldron
        db 176,34
        dw spr_baker
        db 192,66
        dw spr_bullet
        db 100,30
        dw spr_laser
        db 120,26
        dw spr_laser
        db 124,30
        dw spr_dakos
        db 180,58
        dw spr_spark_a
        db 136,36
        dw 0

A_GRASS equ #20                 ; black on green

; sprite, text, y, inks (game.asm's, black for green on the grass)
def_list:
        dw spr_cretan
        db T_CAST1,48,A_RED&7,A_BLU&7
        dw spr_yiayia
        db T_CAST2,64,A_WHI&7,A_BLU&7
        dw spr_bride
        db T_CAST3,80,A_YEL&7,A_WHI&7
        dw spr_psssst
        db T_CAST4,96,A_CYN&7,A_YEL&7
        dw spr_cauldron
        db T_CAST5,112,0,A_RED&7
        dw spr_baker
        db T_CAST6,128,A_WHI&7,A_YEL&7
        dw 0

inv_list:
        dw spr_drone_a
        db T_ENE1,56,A_MAG&7,A_MAG&7
        dw spr_guard_a
        db T_ENE2,88,A_BLU&7,A_BLU&7
        dw spr_tank_va
        db T_ENE3,120,A_RED&7,A_RED&7
        dw 0

;------------------------------------------------------------------------------
; the high scores: 8 x (3 glyphs, score), in hs_table
;------------------------------------------------------------------------------
hs_init:
        ld hl,hs_default
        ld de,hs_table
        ld bc,HS_N*5
        ldir
        ld a,#ff
        ld (hs_new),a
        ret

; with the title on screen: a game just ended with a score for the table?
hs_check:
        ld a,#ff
        ld (hs_new),a
        ld de,(score)
        ld hl,0
        ld (score),hl           ; looked at once only
        ld hl,(hs_table+(HS_N-1)*5+3)
        or a
        sbc hl,de               ; carry: better than the last one
        ret nc
        ld (hs_score),de
        call hs_name
        call hs_insert
        ld a,HS_PAGE
        ld (tpage),a
        jp title_page

; the name, three letters: UP / DOWN pick, FIRE / RIGHT next, LEFT back
hs_name:
        xor a
        ld (hs_pos),a
        ld hl,hs_idx
        ld (hl),a
        inc hl
        ld (hl),a
        inc hl
        ld (hl),a
        call page_clear
        call text_normal
        ld a,A_YEL
        call set_attr
        ld a,T_NEWHS
        ld e,40
        call print_id_centered
        call text_big
        ld a,A_WHI
        call set_attr
        ld de,26*256+56
        call set_at
        ld hl,(hs_score)
        ld a,5
        call print_num
        call text_normal
        ld a,A_WHI
        call set_attr
        ld a,T_NAME
        ld e,88
        call print_id_centered
        ld a,A_CYN
        call set_attr
        ld a,T_NAMEKEYS
        ld e,144
        call print_id_centered
.draw:  call text_big
        ld b,0                  ; the three letters, the one being picked in yellow
.d:     push bc
        ld a,b
        add a,a
        add a,a
        add a,26
        ld d,a
        ld e,104
        call set_at
        pop bc
        push bc
        ld a,(hs_pos)
        cp b
        ld a,A_WHI
        jr nz,.w
        ld a,A_YEL
.w:     call set_attr
        pop bc
        push bc
        ld hl,hs_idx
        ld a,l
        add a,b
        ld l,a
        jr nc,.i
        inc h
.i:     ld a,(hl)
        call name_glyph
        call put_glyph
        pop bc
        inc b
        ld a,b
        cp 3
        jr nz,.d
        call text_normal
.l:     call wait_frame
        call kbd_update
        ld a,K_UP
        call key_hit
        jr c,.up
        ld a,J_UP
        call key_hit
        jr c,.up
        ld a,K_Q
        call key_hit
        jr c,.up
        ld a,K_DOWN
        call key_hit
        jr c,.dn
        ld a,J_DOWN
        call key_hit
        jr c,.dn
        ld a,K_A
        call key_hit
        jr c,.dn
        ld a,K_LEFT
        call key_hit
        jr c,.lf
        ld a,J_LEFT
        call key_hit
        jr c,.lf
        ld a,K_O
        call key_hit
        jr c,.lf
        ld a,K_RIGHT
        call key_hit
        jr c,.nx
        ld a,J_RIGHT
        call key_hit
        jr c,.nx
        ld a,K_P
        call key_hit
        jr c,.nx
        call fire_hit
        jr nc,.l
.nx:    ld a,SFX_BUILD
        call sfx_play
        ld hl,hs_pos
        inc (hl)
        ld a,(hl)
        cp 3
        jp nz,.draw
        ret
.lf:    ld hl,hs_pos
        ld a,(hl)
        or a
        jr z,.l
        dec (hl)
        jp .draw
.up:    call .cur
        dec (hl)
        jp p,.snd
        ld (hl),NAME_NCHARS-1
        jr .snd
.dn:    call .cur
        inc (hl)
        ld a,(hl)
        cp NAME_NCHARS
        jr c,.snd
        ld (hl),0
.snd:   ld a,SFX_MOVE
        call sfx_play
        jp .draw
.cur:   ld hl,hs_idx            ; HL = the letter being picked
        ld a,(hs_pos)
        add a,l
        ld l,a
        ret nc
        inc h
        ret

; A = index into name_chars -> A = glyph
name_glyph:
        ld hl,name_chars
        add a,l
        ld l,a
        jr nc,.n
        inc h
.n:     ld a,(hl)
        ret

; the new entry into the table, the ones below it down a place
hs_insert:
        ld hl,hs_table+3        ; find its place: before the first lower score
        ld b,0
.f:     ld e,(hl)
        inc hl
        ld d,(hl)
        push hl
        ld hl,(hs_score)
        or a
        sbc hl,de               ; NC: not lower than this one... carry: lower
        pop hl
        jr z,.n                 ; a tie stays below
        jr nc,.got
.n:     inc hl
        inc hl
        inc hl
        inc hl
        inc b
        ld a,b
        cp HS_N
        jr nz,.f
        ret
.got:   ld a,b
        ld (hs_new),a
        ld c,a                  ; DE = its entry
        add a,a
        add a,a
        add a,c
        ld e,a
        ld d,0
        ld hl,hs_table
        add hl,de
        push hl
        ld a,HS_N-1             ; move (HS_N-1-place) entries down by 5
        sub b
        jr z,.put
        ld b,a                  ; bytes = entries * 5
        add a,a
        add a,a
        add a,b
        ld c,a
        ld b,0
        ld hl,hs_table+(HS_N-1)*5-1
        ld de,hs_table+HS_N*5-1
        lddr
.put:   pop de
        ld hl,hs_idx
        ld b,3
.p:     ld a,(hl)
        push hl
        call name_glyph
        pop hl
        ld (de),a
        inc hl
        inc de
        djnz .p
        ld hl,(hs_score)
        ex de,hl
        ld (hl),e
        inc hl
        ld (hl),d
        ret

; the title page with the table; the newest entry in yellow
hs_show:
        ld a,A_YEL
        call set_attr
        ld a,T_HSHDR
        ld e,32
        call print_id_centered
        ld hl,hs_table
        ld b,0
.r:     push bc
        push hl
        ld a,(hs_new)
        cp b
        ld a,A_WHI
        jr nz,.c
        ld a,A_YEL
.c:     call set_attr
        pop hl
        pop bc
        push bc
        push hl
        ld a,b                  ; the line: 48 + 16 * place
        add a,a
        add a,a
        add a,a
        add a,a
        add a,48
        ld e,a
        ld d,24
        push de
        call set_at
        pop de
        pop hl
        pop bc
        push bc
        push de
        push hl
        ld l,b                  ; the place
        inc l
        ld h,0
        ld a,1
        call print_num
        ld a,G_SPACE
        call put_glyph
        pop hl
        pop de
        ld b,3                  ; the name
.n:     ld a,(hl)
        inc hl
        push bc
        push hl
        call put_glyph
        pop hl
        pop bc
        djnz .n
        call put_glyph_sp
        call put_glyph_sp
        ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        push hl
        ex de,hl
        ld a,5
        ld (pn_zero),a
        call print_num
        xor a
        ld (pn_zero),a
        pop hl
        pop bc
        inc b
        ld a,b
        cp HS_N
        jr nz,.r
        ret

put_glyph_sp:
        push hl
        ld a,G_SPACE
        call put_glyph
        pop hl
        ret
