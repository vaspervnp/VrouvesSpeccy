;==============================================================================
; hw.asm - the interrupt, the keyboard and the joystick, the AY, the frame pace
;==============================================================================

; IM 2 through a table of 257 bytes IM2_FILL: whatever is on the bus, the
; vector is IM2_JUMP, where a JP to the handler sits.  I >= #80, or a 48K
; shows snow.
hw_init:
        ld hl,IM2_TABLE
        ld de,IM2_TABLE+1
        ld bc,256
        ld (hl),IM2_FILL
        ldir
        ld a,#c3                ; JP nn
        ld (IM2_JUMP),a
        ld hl,int_handler
        ld (IM2_JUMP+1),hl
        ld a,IM2_TABLE>>8
        ld i,a
        im 2
        ei
        call ay_detect
        call kempston_detect
        jp mem_detect

; once a frame, at its start (50 Hz)
int_handler:
        push af
        push bc
        push de
        push hl
        push ix
        push iy
        ld hl,framecnt
        inc (hl)
        call snd_update
        call kbd_scan
        pop iy
        pop ix
        pop hl
        pop de
        pop bc
        pop af
        ei
        reti

; The AY (128K, +2, +3): register reads come back from #FFFD; on a 48K that
; is the floating bus, #FF in the border.
ay_detect:
        halt
        ld bc,#fffd
        xor a
        out (c),a               ; register 0
        ld b,#bf
        ld a,#55
        out (c),a
        ld b,#ff
        in a,(c)
        cp #55
        ret nz
        ld b,#bf
        ld a,#aa
        out (c),a
        ld b,#ff
        in a,(c)
        cp #aa
        ret nz
        ld a,1
        ld (ay_present),a
        ret

; Kempston only if port #1F read like a joystick (none of bits 5-7) for two
; whole frames: with no interface there it is the floating bus.
kempston_detect:
        halt
        ld a,(framecnt)
        add a,2
        ld l,a
        ld h,0
.listen:
        in a,(#1f)
        or h
        ld h,a
        ld a,(framecnt)
        cp l
        jr nz,.listen
        ld a,h
        and #e0
        ret nz
        ld a,1
        ld (kempston_on),a
        ret

; A 128K: bank 1 paged at #C000 is not bank 0.  The test runs from below
; #C000 with the interrupts off (the IM 2 table and the stack are up there).
mem_detect:
        di
        ld hl,#c000
        ld bc,#7ffd
        ld a,BANK_1
        out (c),a
        ld a,(hl)
        cpl
        ld (hl),a               ; bank 1 (or, on a 48K, the one bank)
        ld e,a
        ld a,BANK_0
        out (c),a
        ld a,(hl)
        cp e
        jr z,.k48
        ld a,1
        ld (is_128),a
        ld a,BANK_1             ; bank 1's byte back as it was
        out (c),a
        ld a,e
        cpl
        ld (hl),a
        ld a,BANK_0
        out (c),a
        ei
        ret
.k48:   cpl                     ; a 48K: the byte back as it was
        ld (hl),a
        ei
        ret

; wait for the next frame; on a 48K the beeper plays until then
wait_frame:
        ld a,(ay_present)
        or a
        jp z,beeper_frame
        halt
        ret

; 4 = a steady 12.5 fps, the logic at 25 Hz: two ticks a drawn frame
FRAMES_PER_DRAW equ 4

; wait until FRAMES_PER_DRAW frames have passed since the last call; work
; out how many 25 Hz logic ticks the next frame must run
flip:
.w:     ld a,(last_flip)
        ld b,a
        ld a,(framecnt)
        sub b
        cp FRAMES_PER_DRAW
        jr nc,.go
        call wait_frame
        jr .w
.go:    ld (dbg_el),a
        ld hl,frame_acc
        add a,(hl)
        ld b,a
        and 1
        ld (hl),a
        ld a,b
        srl a
        cp 3                    ; at most two ticks: under a very heavy load the
        jr c,.td                ; game slows down a touch instead of stuttering
        ld a,2
        ld (hl),0
.td:    ld (ticks_due),a
        ld a,(framecnt)
        ld (last_flip),a
        ret

;------------------------------------------------------------------------------
; the keyboard: 8 half-rows (port #FE), the Kempston (row 8) and the keys
; made of two (row 9: the cursor keys, BREAK, DELETE), active low like the
; CPC's matrix.  keys = live, keys+10 = latched presses since the last
; kbd_update.
;------------------------------------------------------------------------------
kbd_scan:
        ld hl,keys
        ld bc,#fefe
.row:   in a,(c)
        or #e0
        ld (hl),a
        inc hl
        rlc b
        jr c,.row
        ld a,(kempston_on)      ; the joystick, active high: inverted
        or a
        ld a,#ff
        jr z,.nk
        in a,(#1f)
        cpl
        or #e0
.nk:    ld (hl),a
        inc hl
        ; CAPS SHIFT with 5-8 is a cursor key (emulators send the PC's arrows
        ; so), with SPACE BREAK, with 0 DELETE: those keys are taken off their
        ; rows and set on row 9
        ld c,#ff
        ld a,(keys+0)
        rra
        jr c,.nocaps
        ld a,(keys+3)           ; 5: left
        bit 4,a
        jr nz,.c6
        res 0,c
        set 4,a
        ld (keys+3),a
.c6:    ld a,(keys+4)
        bit 4,a                 ; 6: down
        jr nz,.c7
        res 1,c
.c7:    bit 3,a                 ; 7: up
        jr nz,.c8
        res 2,c
.c8:    bit 2,a                 ; 8: right
        jr nz,.c0
        res 3,c
.c0:    bit 0,a                 ; 0: delete
        jr nz,.cd
        res 5,c
.cd:    or #1d
        ld (keys+4),a
        ld a,c                  ; a cursor key held: SPACE stays fire
        or #c0
        inc a
        jr nz,.nocaps
        ld a,(keys+7)
        rra
        jr c,.nocaps
        res 4,c                 ; BREAK
        ld a,(keys+7)
        or 1
        ld (keys+7),a
.nocaps:
        ld (hl),c
        ; the latch remembers presses until kbd_update reads it
        ld hl,keys
        ld de,keys+10
        ld b,10
.l:     ld a,(de)
        and (hl)
        ld (de),a
        inc hl
        inc de
        djnz .l
        ret

kbd_update:
        ld hl,kcur
        ld de,kold
        ld bc,10
        ldir
        di
        ld hl,keys+10           ; latched presses since the last update
        ld de,kcur
        ld bc,10
        ldir
        ld hl,keys
        ld de,keys+10
        ld bc,10
        ldir
        ei
        ret

; HL = matrix, A = key code (row*8+bit) -> carry set if pressed
key_test:
        push bc
        ld c,a
        rrca
        rrca
        rrca
        and 15
        add a,l
        ld l,a
        jr nc,.n
        inc h
.n:     ld a,c
        and 7
        inc a
        ld b,a
        ld a,(hl)
.r:     rrca
        djnz .r
        ccf
        pop bc
        ret

key_down:
        push hl
        ld hl,kcur
        call key_test
        pop hl
        ret

; pressed now but not on the previous frame
key_hit:
        push af
        call key_down
        jr nc,.no
        pop af
        push hl
        ld hl,kold
        call key_test
        pop hl
        ccf
        ret
.no:    pop af
        or a
        ret

; any of the "fire" keys hit?
fire_hit:
        ld a,K_SPACE
        call key_hit
        ret c
        ld a,K_ENTER
        call key_hit
        ret c
        ld a,J_FIRE
        jp key_hit
