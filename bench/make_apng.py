"""Assemble the frames saved by the player's captureRun() into an animated PNG (APNG). Standard library only.

  python make_apng.py <frames dir name under results/.frames> <output path> [speed]

Each captured frame stands for `dt` ms of board time; `speed` (default 3) is the playback speed-up.
Frames store only the rectangle that changed (with its x, y offset); frames that did not change at all
were not stored, and their `hold` count becomes a longer delay.
"""
import json
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIG = b"\x89PNG\r\n\x1a\n"


def chunks(data):
    assert data[:8] == SIG, "not a PNG"
    i = 8
    while i < len(data):
        n = struct.unpack(">I", data[i:i + 4])[0]
        yield data[i + 4:i + 8], data[i + 8:i + 8 + n]
        i += 12 + n


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def main():
    name, out = sys.argv[1], sys.argv[2]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    d = os.path.join(ROOT, "results", ".frames", name)
    meta = json.load(open(os.path.join(d, "frames.json"), encoding="utf-8"))
    frames = meta["frames"]
    fmt, parts = None, []
    for f in frames:
        idat, size = b"", None
        for kind, body in chunks(open(os.path.join(d, f["name"] + ".png"), "rb").read()):
            if kind == b"IHDR":
                size = struct.unpack(">II", body[:8])
                if fmt is None:
                    fmt = body[8:]
                assert body[8:] == fmt, "pixel format differs: " + f["name"]
            elif kind == b"IDAT":
                idat += body
        parts.append((size, idat))
    w, h = parts[0][0]
    assert (frames[0].get("x", 0), frames[0].get("y", 0)) == (0, 0), "first frame must be the full canvas"
    delay = lambda f: min(4000, max(40, int(round(meta["dt"] * f["hold"] / speed))))
    res = [SIG, chunk(b"IHDR", struct.pack(">II", w, h) + fmt), chunk(b"acTL", struct.pack(">II", len(frames), 0))]
    # If the player saved poster.png (the finished board), use it as the PNG's default image: viewers that
    # do not animate show the finished board instead of an empty one. It is not part of the animation.
    poster = os.path.join(d, "poster.png")
    has_poster = os.path.exists(poster)
    if has_poster:
        pidat = b""
        for kind, body in chunks(open(poster, "rb").read()):
            if kind == b"IHDR":
                assert struct.unpack(">II", body[:8]) == (w, h) and body[8:] == fmt, "poster size or format differs"
            elif kind == b"IDAT":
                pidat += body
        res.append(chunk(b"IDAT", pidat))
    seq = 0
    for i, (f, (size, idat)) in enumerate(zip(frames, parts)):
        # dispose_op 0 (leave the frame in place), blend_op 0 (replace the rectangle)
        res.append(chunk(b"fcTL", struct.pack(">IIIIIHHBB", seq, size[0], size[1], f.get("x", 0), f.get("y", 0), delay(f), 1000, 0, 0)))
        seq += 1
        if i == 0 and not has_poster:
            res.append(chunk(b"IDAT", idat))
        else:
            res.append(chunk(b"fdAT", struct.pack(">I", seq) + idat))
            seq += 1
    res.append(chunk(b"IEND", b""))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    blob = b"".join(res)
    open(out, "wb").write(blob)
    print("%s: %d frames, %dx%d, %.1f s loop, %.2f MB" % (out, len(frames), w, h, sum(delay(f) for f in frames) / 1000, len(blob) / 1e6))


if __name__ == "__main__":
    main()
