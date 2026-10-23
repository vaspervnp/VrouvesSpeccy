;==============================================================================
; lz.asm - unpacks what tools/lz.py packed:
;   #00-#7F  n+1 bytes follow as they are
;   #80-#FE  a copy of n-#7E bytes (2-128) from 'offset' bytes back in the
;            output; the offset follows, low byte first
;   #FF      the end
;==============================================================================
; HL = packed, DE = destination
lz_unpack:
        ld a,(hl)
        inc hl
        cp #ff
        ret z
        cp #80
        jr nc,.copy
        inc a
        ld c,a
        ld b,0
        ldir
        jr lz_unpack
.copy:  sub #7e
        ld c,a
        ld b,0
        ld a,(hl)
        inc hl
        push hl
        ld h,(hl)
        ld l,a                  ; HL = offset
        push de
        ex de,hl
        or a
        sbc hl,de               ; HL = destination - offset
        pop de
        ldir
        pop hl
        inc hl
        jr lz_unpack
