;==============================================================================
; sound.asm - the CPC's player: two music channels (A melody, B bass) and the
; effects on channel C, stepped by the 50 Hz interrupt into psg_shadow.  On a
; 128K the shadow goes to the AY (its clock is 1.7734 MHz, the CPC's 1 MHz:
; tools/zxdata.py scales the periods); on a 48K the beeper plays from it in
; whatever time a frame leaves (beeper_frame): the effect, else the melody.
;==============================================================================
C_PTR   equ 0
C_START equ 2
C_DUR   equ 4
C_VOL   equ 5
C_PREG  equ 6
C_VREG  equ 7
C_VSTART equ 8
C_VMIN  equ 9
C_NOTES equ 10
C_SIZE  equ 12

snd_init:
        di
        xor a
        ld (sfx_active),a
        ld hl,psg_shadow
        ld b,14
.c:     ld (hl),a
        inc hl
        djnz .c
        ld hl,chan_init
        ld de,chan_a
        ld bc,C_SIZE*2
        ldir
        ld a,1
        ld (chan_a+C_DUR),a
        ld (chan_b+C_DUR),a
        ld a,7
        ld c,#3c
        call psg_write
        ld hl,#ace1
        ld (noise_seed),hl
        ei
        ret

chan_init:
        dw music_a,music_a
        db 1,0,0,8,13,9
        dw music_a_notes
        dw music_b,music_b
        db 1,0,2,9,12,7
        dw music_b_notes

; A = register, C = value: into the shadow.  Uses A, B.
psg_write:
        push hl
        ld hl,psg_shadow
        add a,l
        ld l,a
        jr nc,.n
        inc h
.n:     ld (hl),c
        pop hl
        ret

; in the interrupt
snd_update:
        ld a,(mus_on)
        or a
        jr nz,.mus
        ld a,8
        ld c,0
        call psg_write
        ld a,9
        ld c,0
        call psg_write
        jr .fx
.mus:   ld iy,chan_a
        call mus_chan
        ld iy,chan_b
        call mus_chan
.fx:    call sfx_update
        ld a,(ay_present)
        or a
        ret z
        ld hl,psg_shadow        ; registers 0-10 to the AY
        ld de,#bfff
        xor a
.w:     ld bc,#fffd
        out (c),a
        ld b,d
        ld e,(hl)
        out (c),e
        inc hl
        inc a
        cp 11
        jr c,.w
        ret

mus_chan:
        dec (iy+C_DUR)
        jr nz,.decay
        ld l,(iy+C_PTR)
        ld h,(iy+C_PTR+1)
        ld a,(hl)
        cp #ff
        jr nz,.got
        ld l,(iy+C_START)
        ld h,(iy+C_START+1)
        ld a,(hl)
.got:   inc hl
        ld (iy+C_PTR),l
        ld (iy+C_PTR+1),h
        ld c,a                  ; note in high nibble, duration index in low
        and 15
        ld e,a
        ld d,0
        ld hl,music_durs
        add hl,de
        ld a,(hl)
        ld (iy+C_DUR),a
        ld a,c
        rrca
        rrca
        rrca
        rrca
        and 15
        jr z,.rest
        add a,a
        ld e,a
        ld d,0
        ld l,(iy+C_NOTES)
        ld h,(iy+C_NOTES+1)
        add hl,de
        ld e,(hl)
        inc hl
        ld d,(hl)
        ld a,(iy+C_PREG)
        ld c,e
        call psg_write
        ld a,(iy+C_PREG)
        inc a
        ld c,d
        call psg_write
        ld a,(iy+C_VSTART)
        ld (iy+C_VOL),a
        jr .setvol
.rest:  xor a
        ld (iy+C_VOL),a
        jr .setvol
.decay: ld a,(framecnt)
        and 3
        ret nz
        ld a,(iy+C_VOL)
        cp (iy+C_VMIN)
        ret z
        ret c
        dec a
        ld (iy+C_VOL),a
.setvol:
        ld c,(iy+C_VOL)
        ld a,(iy+C_VREG)
        jp psg_write

; A = effect number
sfx_play:
        push hl
        push de
        push bc
        ld e,a
        ld d,0
        ld hl,sfx_prio
        add hl,de
        ld c,(hl)
        ld a,(sfx_active)
        or a
        jr z,.ok
        ld a,(sfx_cur_prio)
        cp c
        jr z,.ok
        jr nc,.skip
.ok:    ld a,c
        ld (sfx_cur_prio),a
        ld hl,sfx_table
        add hl,de
        add hl,de
        ld a,(hl)
        inc hl
        ld h,(hl)
        ld l,a
        di
        ld (sfx_ptr),hl
        ld a,1
        ld (sfx_active),a
        ei
.skip:  pop bc
        pop de
        pop hl
        ret

sfx_update:
        ld a,(sfx_active)
        or a
        jr z,.silent
        ld hl,(sfx_ptr)
        ld a,(hl)
        cp #ff
        jr z,.end
        inc hl
        ld c,a
        ld a,10
        call psg_write
        ld a,(hl)
        inc hl
        ld (sfx_noise),a
        or a
        jr z,.nn
        ld c,a
        ld a,6
        call psg_write
.nn:    ld e,(hl)
        inc hl
        ld d,(hl)
        inc hl
        ld (sfx_ptr),hl
        ld c,e
        ld a,4
        call psg_write
        ld c,d
        ld a,5
        call psg_write
        ld c,#38
        ld a,d
        or e
        jr nz,.t
        set 2,c
.t:     ld a,(sfx_noise)
        or a
        jr z,.m
        res 5,c
.m:     ld a,7
        jp psg_write
.end:   xor a
        ld (sfx_active),a
.silent:
        ld c,0
        ld a,10
        call psg_write
        ld c,#3c
        ld a,7
        jp psg_write

; silence on the AY (before a tape load, at the ending)
snd_off:
        di
        xor a
        ld (mus_on),a
        ld (sfx_active),a
        ld hl,psg_shadow+8
        ld (hl),a
        inc hl
        ld (hl),a
        inc hl
        ld (hl),a
        ei
        ret

;------------------------------------------------------------------------------
; The 48K's beeper: until the next interrupt it plays channel C (the effect)
; or, when that is quiet, channel A (the melody) from psg_shadow.  Half a
; square wave is the AY period x 15.8 T; noise flips the level at random every
; noise period x 31.6 T.  Below BEEP_MIN the channel is silent.  The border
; keeps its colour (black).
;------------------------------------------------------------------------------
BEEP_MIN equ 4

beeper_frame:
        ld a,(psg_shadow+10)    ; the effect
        cp BEEP_MIN
        jr c,.music
        ld a,(psg_shadow+7)
        bit 5,a                 ; 0 = noise on C
        jr z,.noise
        ld hl,(psg_shadow+4)
        jr .tone
.music: ld a,(psg_shadow+8)     ; the melody (0 when the music is off)
        cp BEEP_MIN
        jr c,.quiet
        ld hl,(psg_shadow+0)
.tone:  ld a,h
        or l
        jr z,.quiet
        ld d,h                  ; counter = P * 5/8: its loop is 26 T
        ld e,l
        srl d
        rr e
        ld h,d
        ld l,e
        srl d
        rr e
        srl d
        rr e
        add hl,de
        ex de,hl                ; DE = counter
        ld c,0
        ld a,(framecnt)
        ld b,a
.cycle: ld a,c
        xor #10
        ld c,a
        out (#fe),a
        ld h,d
        ld l,e
.d:     dec hl
        ld a,h
        or l
        jr nz,.d
        ld a,(framecnt)
        cp b
        jr z,.cycle
        ret
.noise: ld a,(psg_shadow+6)     ; noise period 1-31: counter 5/4 of it
        and 31
        jr nz,.np
        inc a
.np:    ld e,a
        srl a
        srl a
        add a,e
        ld e,a                  ; E = counter (loop 16 T: djnz + nop)
        ld a,(framecnt)
        ld d,a
        ld hl,(noise_seed)
.nstep: add hl,hl               ; LFSR: a random bit in the carry
        sbc a,a
        ld c,a
        jr nc,.n0
        ld a,l
        xor #2d
        ld l,a
.n0:    ld a,c
        and #10
        out (#fe),a
        ld b,e
.nd:    nop
        djnz .nd
        ld a,(framecnt)
        cp d
        jr z,.nstep
        ld (noise_seed),hl
        ret
.quiet: halt
        ret
