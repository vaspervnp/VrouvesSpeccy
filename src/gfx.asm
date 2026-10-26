;==============================================================================
; gfx.asm - line tables, draw targets, sprites, tiles, dirty rectangles, text
;
; The playfield (240 x 168, at x = 8, y = 8 of the screen) is drawn in
; WORKBUF, 30 bytes a line, and only what changed is copied to the screen,
; so nothing is ever seen half drawn, and nothing flickers.  A sprite drawn
; there first saves what it covers (SAVEBUF, a stack growing down); each
; frame they are all taken off again, newest first, which leaves the
; background: the tiles, the defenders, the banner.  Changes to those are
; made then too (game.asm: bg_pending), and the new sprites go on.
;==============================================================================

;------------------------------------------------------------------------------
; tables: screen line -> address (TAB_SCR, low bytes then high bytes a page
; on), playfield line -> WORKBUF address (TAB_BG), squares 0..63
;------------------------------------------------------------------------------
build_tables:
        ld hl,TAB_SCR
        ld e,0
.s:     ld a,e                  ; #4000 + (y&#C0)<<5 + (y&7)<<8 + (y&#38)<<2
        and #38
        rlca
        rlca
        ld (hl),a
        ld a,e
        and 7
        ld d,a
        ld a,e
        and #c0
        rrca
        rrca
        rrca
        or d
        or #40
        inc h
        ld (hl),a
        dec h
        inc l
        inc e
        ld a,e
        cp 192
        jr nz,.s
        ld hl,TAB_BG
        ld de,WORKBUF
        ld b,PF_H
.bg:    ld (hl),e
        inc h
        ld (hl),d
        dec h
        inc l
        push hl
        ld hl,PF_W
        add hl,de
        ex de,hl
        pop hl
        djnz .bg
        ld hl,SQUARES           ; squares 0..63
        ld de,0
        ld bc,1
.sq:    ld (hl),e
        inc hl
        ld (hl),d
        inc hl
        ex de,hl
        add hl,bc
        ex de,hl
        inc bc
        inc bc
        ld a,l
        cp lo(SQUARES+128)
        jr nz,.sq
        ret

;------------------------------------------------------------------------------
; draw targets: the screen (screen coordinates) or the playfield's buffer
; (playfield coordinates)
;------------------------------------------------------------------------------
tgt_scr:
        ld a,hi(TAB_SCR)
        jr tgt_set
tgt_bg:
tgt_work:
        ld a,hi(TAB_BG)
tgt_set:
        ld (tgt_tab),a
        ret

; E = line of the target -> HL = its first byte.  Uses A.
row_base:
        ld a,(tgt_tab)
        ld h,a
        ld l,e
        ld a,(hl)
        inc h
        ld h,(hl)
        ld l,a
        ret

; DE = a screen address -> the same column on the next line.  Uses A.
next_scr_line:
        inc d
        ld a,d
        and 7
        ret nz
        ld a,e
        add a,32
        ld e,a
        ret c
        ld a,d
        sub 8
        ld d,a
        ret

; E = line, D = byte column -> HL.  Uses A.
line_addr:
        call row_base
        ld a,l
        add a,d
        ld l,a
        ret nc
        inc h
        ret

;------------------------------------------------------------------------------
; sprites: w (1 or 2 bytes), h, then per row w bytes of mask (1 = keep the
; background) and w bytes of ink.  Drawn at any pixel: each row shifted right
; on the fly into w+1 bytes.
;------------------------------------------------------------------------------
; HL = sprite, D = x (pixels), E = y ; on the work buffer: what it covers
; saved first, its rectangle listed for the screen (skipped when there is no
; room left for either)
draw_sprite:
        push hl
        ld a,d
        rrca
        rrca
        rrca
        and 31
        ld (sv_x),a
        ld c,a
        ld a,(hl)               ; w+1, but not past the right edge
        inc a
        ld b,a
        ld a,PF_W
        sub c
        cp b
        jr c,.cl
        ld a,b
.cl:    ld (sv_w),a
        inc hl
        ld b,(hl)               ; h
        ld c,a
        ld hl,(cl_ptr)          ; room in the copy list?
        ld a,h
        cp hi(CLIST_END)
        jr nc,.full
        xor a                   ; bytes to save: w * h, + 4
        ld h,a
.m:     add a,c
        djnz .m
        ld l,a
        ld bc,4
        add hl,bc
        ex de,hl                ; DE = entry size, HL = x,y
        push hl
        ld hl,(save_ptr)
        or a
        sbc hl,de
        ld bc,SAVEBUF
        push hl
        or a
        sbc hl,bc
        pop hl
        pop de                  ; D,E = x,y again
        jr c,.full
        ld (save_ptr),hl        ; the entry: x, y, w, h, then the bytes
        ld a,(sv_x)
        ld (hl),a
        inc hl
        ld (hl),e
        inc hl
        ld a,(sv_w)
        ld c,a
        ld (hl),a
        inc hl
        ex (sp),hl
        inc hl
        ld b,(hl)               ; h
        dec hl
        ex (sp),hl
        ld (hl),b
        inc hl
        push de
        push hl
        ld a,(sv_x)             ; listed for the screen
        ld d,a
        call cl_add
        pop hl
        pop de
        push de
        ex de,hl                ; DE = the save area, L = the line
        push de
        ld e,l
        call row_base
        ld a,(sv_x)
        add a,l
        ld l,a
        jr nc,.s1
        inc h
.s1:    pop de                  ; HL = the work buffer, DE = the save area
        ld a,PF_W
        sub c
        ld (.sst+1),a
.sv:    push bc                 ; save the rows
        ld b,0
        ldir
.sst:   ld bc,0
        add hl,bc
        pop bc
        djnz .sv
        pop de
        pop hl
        jr draw_sprite_raw
.full:  pop hl
        ret

; D,E,C,B = x,y,w,h: listed to be copied to the screen this frame.
; Preserves everything but A.
cl_add:
dirty_add_both:
        push hl
        ld hl,(cl_ptr)
        ld a,h
        cp hi(CLIST_END)
        jr nc,.full
        ld (hl),d
        inc hl
        ld (hl),e
        inc hl
        ld (hl),c
        inc hl
        ld (hl),b
        inc hl
        ld (cl_ptr),hl
.full:  pop hl
        ret

; HL = sprite, D = x (pixels), E = y ; nothing recorded.  Preserves IX.
draw_sprite_raw:
        push ix
        call .go0
        pop ix
        ret
.go0:   ld a,e
        ld (spr_y),a
        ld c,(hl)               ; w
        inc hl
        ld b,(hl)               ; h
        inc hl
        push hl
        pop ix
        ld a,d
        rrca
        rrca
        rrca
        and 31
        ld (spr_xb),a
        ld a,d
        and 7
        neg
        add a,7                 ; 7 - shift: steps to skip
        ld l,a
        dec c
        jr nz,.w2
        ; one byte wide
        add a,a
        add a,a                 ; 4 bytes a mask step
        ld de,sh1_m
        call .ent
        ld (spr1_row.msk+1),de
        ld a,l
        add a,a
        add a,l                 ; 3 bytes an ink step
        ld de,sh1_i
        call .ent
        ld (spr1_ink+1),de
        ld hl,spr1_row
        jr .go
.w2:    ld a,l
        add a,a
        add a,l
        add a,a                 ; 6 bytes a mask step
        ld de,sh2_m
        call .ent
        ld (spr2_row.msk+1),de
        ld a,l
        add a,a
        add a,a
        add a,l                 ; 5 bytes an ink step
        ld de,sh2_i
        call .ent
        ld (spr2_ink+1),de
        ld hl,spr2_row
.go:    ld (.call+1),hl
        ld a,(spr_y)
        ld e,a
        call row_base
        ld a,(spr_xb)
        add a,l
        ld e,a
        adc a,h
        sub e
        ld d,a                  ; DE = the screen or buffer
.row:   push bc
        push de
.call:  call spr2_row
        pop de
        ld a,(tgt_tab)          ; the next line
        cp hi(TAB_SCR)
        jr z,.scr
        ld hl,PF_W
        add hl,de
        ex de,hl
        pop bc
        djnz .row
        ret
.scr:   call next_scr_line
        pop bc
        djnz .row
        ret
.ent:   add a,e                 ; DE += A
        ld e,a
        ret nc
        inc d
        ret

; IX = row (mask, ink), DE = destination ; IX moves on
spr2_row:
        ld h,(ix+0)
        ld l,(ix+1)
        ld a,#ff
.msk:   jp sh2_m
sh2_m:  repeat 7
        scf
        rr h
        rr l
        rra
        rend
        ld b,h
        ld c,l
        ex af,af'
        ld h,(ix+2)
        ld l,(ix+3)
        xor a
spr2_ink:
        jp sh2_i
sh2_i:  repeat 7
        srl h
        rr l
        rra
        rend
        ld (.i2+1),a
        ld a,(de)
        and b
        or h
        ld (de),a
        inc de
        ld a,(de)
        and c
        or l
        ld (de),a
        inc de
        ex af,af'
        ld b,a
        ld a,(de)
        and b
.i2:    or 0
        ld (de),a
        ld bc,4
        add ix,bc
        ret

spr1_row:
        ld h,(ix+0)
        ld a,#ff
.msk:   jp sh1_m
sh1_m:  repeat 7
        scf
        rr h
        rra
        rend
        ld b,h
        ld c,a
        ld h,(ix+1)
        xor a
spr1_ink:
        jp sh1_i
sh1_i:  repeat 7
        srl h
        rra
        rend
        ld l,a
        ld a,(de)
        and b
        or h
        ld (de),a
        inc de
        ld a,(de)
        and c
        or l
        ld (de),a
        inc ix
        inc ix
        ret

;------------------------------------------------------------------------------
; tiles: 16 x 16, two bytes a row
;------------------------------------------------------------------------------
; HL = tile, D = x (pixels, a multiple of 8), E = y ; current target
draw_tile:
        ld a,d
        rrca
        rrca
        rrca
        and 31
        ld (spr_xb),a
        ld b,16
.row:   push bc
        push hl
        call row_base
        ld a,(spr_xb)
        add a,l
        ld c,a
        adc a,h
        sub c
        ld b,a                  ; BC = the line's two bytes
        pop hl
        ld a,(hl)
        ld (bc),a
        inc hl
        inc bc
        ld a,(hl)
        ld (bc),a
        inc hl
        inc e
        pop bc
        djnz .row
        ret

;------------------------------------------------------------------------------
; a frame: the sprites off, the background's changes, the sprites on, the
; changes to the screen
;------------------------------------------------------------------------------
dirty_reset:
        ld hl,SAVE_END
        ld (save_ptr),hl
        ld hl,CLIST
        ld (cl_ptr),hl
        ret

render:
        call tgt_work
        ld hl,(save_ptr)        ; the sprites off, newest first
.u:     ld a,l
        cp lo(SAVE_END)
        jr nz,.ug
        ld a,h
        cp hi(SAVE_END)
        jr z,.ud
.ug:    ld d,(hl)
        inc hl
        ld e,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        inc hl
        call cl_add
        push hl
        call row_base
        ld a,d
        add a,l
        ld e,a
        adc a,h
        sub e
        ld d,a                  ; DE = the work buffer
        ld a,PF_W
        sub c
        ld (.ust+1),a
        pop hl                  ; HL = the saved bytes
.ur:    push bc
        ld b,0
        ldir
.ust:   ld bc,0
        ex de,hl
        add hl,bc
        ex de,hl
        pop bc
        djnz .ur
        jr .u
.ud:    ld (save_ptr),hl
        call at_restore         ; the invaders' colours off
        call bg_pending         ; the background's changes
        call draw_enemies
        call draw_projs
        call draw_fx
        call draw_flag
        call draw_cursor
        ld hl,CLIST             ; the changes: work buffer -> screen
.c:     ld de,(cl_ptr)
        ld a,l
        cp e
        jr nz,.cg
        ld a,h
        cp d
        jr z,.cd
.cg:    ld d,(hl)
        inc hl
        ld e,(hl)
        inc hl
        ld c,(hl)
        inc hl
        ld b,(hl)
        inc hl
        push hl
        call copy_rect
        pop hl
        jr .c
.cd:    ld hl,CLIST
        ld (cl_ptr),hl
        ret

; D,E,C,B = x,y,w,h : work buffer -> screen
copy_rect:
        ld a,PF_W
        sub c
        ld (.step+1),a
        ld l,e
        ld h,hi(TAB_BG)
        ld a,(hl)
        inc h
        ld h,(hl)
        add a,d
        ld l,a
        jr nc,.n
        inc h
.n:     push hl                 ; the work buffer
        ld a,e
        add a,PF_Y
        ld l,a
        ld h,hi(TAB_SCR)
        ld a,(hl)
        inc h
        ld h,(hl)
        add a,d
        add a,PF_COL
        ld e,a
        ld d,h                  ; DE = the screen
        pop hl
.row:   push bc
        push de
        ld b,0
        ldir
        pop de
        inc d                   ; the next screen line
        ld a,d
        and 7
        jr nz,.step
        ld a,e
        add a,32
        ld e,a
        jr c,.step
        ld a,d
        sub 8
        ld d,a
.step:  ld bc,0
        add hl,bc
        pop bc
        djnz .row
        ret

; the whole playfield to the screen, with no sprites on it
bg_to_screens:
        ld de,0
        ld bc,PF_H*256+PF_W
        call copy_rect
        jp dirty_reset

; D,E,C,B = x,y,w,h (bytes, lines) ; A = fill byte ; current target
fill_rect:
        ld (fill_val),a
.row:   push bc
        push de
        call line_addr
        pop de
        ld a,(fill_val)
        pop bc
        push bc
        ld b,c
.c:     ld (hl),a
        inc hl
        djnz .c
        pop bc
        inc e
        djnz .row
        ret

; D,E,C,B = column, row, w, h of attribute cells ; A = attribute
attr_rect:
        push af
        ld l,e
        ld h,0
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        add hl,hl
        ld a,d
        add a,l
        ld l,a
        ld a,h
        adc a,hi(ATTRS)
        ld h,a
        pop af
.r:     push bc
        push hl
        ld b,c
.c:     ld (hl),a
        inc hl
        djnz .c
        pop hl
        ld bc,32
        add hl,bc
        pop bc
        djnz .r
        ret

cls:
        ld hl,#4000
        ld de,#4001
        ld bc,6144
        ld (hl),0
        ldir
        ld (hl),A_TEXT
        ld bc,767
        ldir
        ret

;------------------------------------------------------------------------------
; text: 3x6 glyphs in 4x8 cells, 64 columns; or 8x16, double, on even
; columns.  txt_x = column (0-63), txt_y = screen line.  On the screen each
; glyph sets the attribute of its cell (txt_attr); on the background (the
; banner) the attributes are the banner's.
;------------------------------------------------------------------------------
; A = attribute
set_attr:
        ld (txt_attr),a
        ret

; D = column, E = line
set_at:
        ld a,d
        ld (txt_x),a
        ld a,e
        ld (txt_y),a
        ret

text_normal:
        xor a
        ld (txt_big),a
        ret
text_big:
        ld a,1
        ld (txt_big),a
        ret

; E = screen line, A = column -> HL = byte of the target (screen, or the
; background with the playfield's offset).  Uses A, BC, D.
text_addr:
        rra                     ; byte column
        and 31
        ld d,a
        ld a,(tgt_tab)
        cp hi(TAB_SCR)
        jp z,line_addr
        dec d                   ; the background: playfield coordinates
        ld a,e
        sub PF_Y
        ld e,a
        call line_addr
        ld a,e
        add a,PF_Y
        ld e,a
        ret

; A = glyph
put_glyph:
        ld l,a
        ld h,0
        ld d,h
        ld e,l
        add hl,hl
        add hl,de
        add hl,hl
        ld de,font
        add hl,de
        ld (gl_ptr),hl
        ld a,(tgt_tab)          ; on the screen: the cell's colour
        cp hi(TAB_SCR)
        call z,glyph_attr
        ld a,(txt_y)
        ld e,a
        ld a,(txt_big)
        or a
        jr nz,.big
        ld a,(txt_x)            ; the first line's byte, then a line at a time:
        push af                 ; +256 on the screen (a text line is a
        call text_addr          ; character row), +30 on the playfield
        ld de,256
        ld a,(tgt_tab)
        cp hi(TAB_SCR)
        jr z,.st
        ld de,PF_W
.st:    pop af
        rra
        ld bc,#0f04             ; even column: the high half, as it is
        jr nc,.ev
        ld bc,#f000             ; odd: the low half, the glyph moved down 4
.ev:    ld a,c
        ld (.sh+1),a
        ld c,b                  ; C = what to keep
        ld b,8
        push ix
        ld ix,(gl_ptr)
.g:     ld a,b                  ; the first and last lines are blank
        cp 8
        jr z,.z
        dec a
        jr z,.z
        ld a,(ix+0)
        inc ix
.sh:    jr .r4                  ; patched: 0 or 4 RRCAs skipped
.r4:    rrca
        rrca
        rrca
        rrca
        jr .put
.z:     xor a
.put:   push af
        ld a,(hl)
        and c
        ld (hl),a
        pop af
        or (hl)
        ld (hl),a
        add hl,de
        djnz .g
.done:  pop ix
        ld hl,txt_x
        inc (hl)
        ret
.big:   ld b,2
.b0:    push bc
        xor a
        call big_line
        pop bc
        djnz .b0
        ld b,6
.b1:    push bc
        ld hl,(gl_ptr)
        ld a,(hl)
        inc hl
        ld (gl_ptr),hl
        push af
        call big_line
        pop af
        call big_line
        pop bc
        djnz .b1
        ld b,2
.b2:    push bc
        xor a
        call big_line
        pop bc
        djnz .b2
        ld hl,txt_x
        inc (hl)
        inc (hl)
        ret

; A = glyph row (bits 7-5), E = line (moved on)
glyph_line:
        ld c,a
        push de
        ld a,(txt_x)
        call text_addr
        pop de
        ld a,(gl_keep)
        cp #0f
        ld a,c
        jr z,.ev
        rrca
        rrca
        rrca
        rrca
.ev:    ld c,a
        ld a,(gl_keep)
        and (hl)
        or c
        ld (hl),a
        inc e
        ret

; A = glyph row (bits 7-5): each pixel two wide, in a whole byte
big_line:
        rlca
        rlca
        rlca
        and 7
        ld hl,big_bits
        add a,l
        ld l,a
        jr nc,.n
        inc h
.n:     ld c,(hl)
        push de
        ld a,(txt_x)
        call text_addr
        pop de
        ld (hl),c
        inc e
        ret
big_bits:
        db #00,#0c,#30,#3c,#c0,#cc,#f0,#fc

; the attribute of the glyph's cell (and the one below, when big)
glyph_attr:
        ld a,(txt_y)
        and #f8
        ld l,a
        ld h,0
        add hl,hl
        add hl,hl               ; (y/8)*32
        ld a,(txt_x)
        rra
        and 31
        add a,l
        ld l,a
        ld a,h
        adc a,hi(ATTRS)
        ld h,a
        ld a,(txt_big)
        or a
        ld a,(txt_attr)
        ld (hl),a
        ret z
        ld de,32
        add hl,de
        ld (hl),a
        ret

; HL = string (#FE newline, #FF end; codes >= NUM_GLYPHS are byte pairs)
print_str:
        ld a,(txt_x)
        ld (txt_x0),a
.l:     ld a,(hl)
        inc hl
        cp #ff
        ret z
        cp #fe
        jr nz,.c
        ld a,(txt_x0)
        ld (txt_x),a
        ld a,(txt_big)
        or a
        ld a,(txt_y)
        jr z,.s
        add a,8
.s:     add a,8
        ld (txt_y),a
        jr .l
.c:     push hl
        call print_code
        pop hl
        jr .l

print_code:
        cp NUM_GLYPHS
        jp c,put_glyph
        call pair_ptr
        ld a,(hl)
        inc hl
        push hl
        call print_code
        pop hl
        ld a,(hl)
        jr print_code

; A = pair code -> HL
pair_ptr:
        sub NUM_GLYPHS
        ld l,a
        ld h,0
        add hl,hl
        ld de,pair_table
        add hl,de
        ret

; A = string id -> HL
get_str:
        ld l,a
        ld h,0
        add hl,hl
        ld a,(lang)
        or a
        ld de,strtab_en
        jr z,.e
        ld de,strtab_gr
.e:     add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        ret

print_id:
        call get_str
        jp print_str

; A = string id ; E = line : print centred (by its first line)
print_id_centered:
        push de
        call get_str
        pop de
; HL = string, E = line
print_centered:
        push hl
        call str_len
        ld a,(txt_big)
        or a
        ld a,64
        jr z,.n
        ld a,c                  ; double: twice as wide
        add a,a
        ld c,a
        ld a,64
.n:     sub c
        srl a
        ld d,a
        ld a,(txt_big)
        or a
        ld a,d
        jr z,.n2
        and #fe                 ; on an even column
.n2:    ld (txt_x),a
        ld a,e
        ld (txt_y),a
        pop hl
        jp print_str

; HL = string -> C = length of its first line
str_len:
        push de
        push hl
        ld c,0
.l:     ld a,(hl)
        inc hl
        cp #fe
        jr nc,.d
        push hl
        call len_code
        pop hl
        jr .l
.d:     pop hl
        pop de
        ret

len_code:
        cp NUM_GLYPHS
        jr nc,.p
        inc c
        ret
.p:     call pair_ptr
        ld a,(hl)
        inc hl
        push hl
        call len_code
        pop hl
        ld a,(hl)
        jr len_code

; HL = value, A = digits ; pn_zero != 0 pads with zeros
print_num:
        ld (pn_cnt),a
        ld e,a
        ld a,5
        sub e
        add a,a
        ld e,a
        ld d,0
        ld ix,pow10
        add ix,de
        ld a,(pn_zero)
        ld (pn_nz),a
.d:     ld e,(ix+0)
        ld d,(ix+1)
        inc ix
        inc ix
        ld c,0
.s:     or a
        sbc hl,de
        jr c,.u
        inc c
        jr .s
.u:     add hl,de
        ld a,(pn_cnt)
        cp 1
        jr z,.show
        ld a,c
        or a
        jr nz,.show
        ld a,(pn_nz)
        or a
        jr nz,.show
        xor a
        jr .put
.show:  ld a,1
        ld (pn_nz),a
        ld a,c
        add a,GLYPH_0
.put:   push hl
        push ix
        call put_glyph
        pop ix
        pop hl
        ld a,(pn_cnt)
        dec a
        ld (pn_cnt),a
        jr nz,.d
        ret

pow10:  dw 10000,1000,100,10,1

; D = first column (even), C = columns (even), E = line : blank 8 lines of
; text on the screen
clear_text:
        call tgt_scr
        srl d
        srl c
        ld b,8
        xor a
        jp fill_rect
