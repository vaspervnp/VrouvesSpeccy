"""A small LZ77 packer for src/lz.asm (lz_unpack).

The stream is a run of tokens:
    $00-$7f  n+1 literal bytes follow
    $80-$fe  a copy of n-$7e bytes (2-128) from 'offset' bytes back in the
             output; the offset follows, low byte first (1-65535)
    $ff      the end
"""


def pack(data):
    data = bytes(data)
    n = len(data)
    out = bytearray()
    lit = bytearray()
    heads = {}
    i = 0

    def flush():
        nonlocal lit
        while lit:
            chunk = lit[:128]
            out.append(len(chunk) - 1)
            out.extend(chunk)
            lit = lit[128:]

    while i < n:
        best_len, best_off = 0, 0
        if i + 2 < n:
            key = data[i:i + 3]
            for j in reversed(heads.get(key, [])[-64:]):
                ln = 0
                while ln < 128 and i + ln < n and data[j + ln] == data[i + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_off = ln, i - j
                    if ln == 128:
                        break
        if best_len >= 4 or (best_len == 3 and not lit):
            flush()
            out.append(0x7E + best_len)
            out += bytes([best_off & 255, best_off >> 8])
            step = best_len
        else:
            lit.append(data[i])
            step = 1
        for k in range(i, min(i + step, n - 2)):
            heads.setdefault(data[k:k + 3], []).append(k)
        i += step
    flush()
    out.append(0xFF)
    return bytes(out)


def unpack(stream):
    out = bytearray()
    i = 0
    while True:
        t = stream[i]
        i += 1
        if t == 0xFF:
            return bytes(out)
        if t < 0x80:
            out += stream[i:i + t + 1]
            i += t + 1
        else:
            ln = t - 0x7E
            off = stream[i] | stream[i + 1] << 8
            i += 2
            for _ in range(ln):
                out.append(out[-off])


if __name__ == "__main__":
    import random
    for trial in range(200):
        d = bytes(random.choice(b"aab") for _ in range(random.randint(0, 3000)))
        assert unpack(pack(d)) == d
    print("ok")
