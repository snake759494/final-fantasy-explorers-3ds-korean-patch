import os, sys, re, json, struct, glob
sys.path.insert(0, os.path.dirname(__file__))
from msg import parse as mparse, build as mbuild
from darc import parse as dparse
from pack import none_wrap
from mkfont import build as fbuild
from build import build as rbuild

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
GAME = os.path.join(B, '')
ROM = GAME + 'Final Fantasy Explorers (Japan).3ds'
OUT = GAME + 'Final Fantasy Explorers (Korean).3ds'
TTF = GAME + 'NanumSquareNeo-dEb.ttf'
R = os.path.join(B, 'work', 'ext', 'romfs')
D = os.path.join(B, 'work', 'dec')
JP = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')


def unesc(s):
    return re.sub(r'\{([0-9A-F]{2})\}', lambda m: chr(int(m.group(1), 16)), s)


# ---- message table
alljp = json.load(open(os.path.join(B, 'translation', 'all_jp.json'), encoding='utf-8'))
ko = {}
for f in glob.glob(os.path.join(B, 'translation', 'out', '*.json')):
    for k, v in json.load(open(f, encoding='utf-8')).items():
        ko[int(k)] = v.replace('·', '・')
tmap = {unesc(alljp[i]): unesc(v) for i, v in ko.items()}
print('translated', len(tmap), '/', len(alljp))

repl = {}
used = set()


def put(n, data):
    repl[n] = none_wrap(open(os.path.join(R, n), 'rb').read(8), data)


for n in ('0641427059', '3985733386'):
    b = open(os.path.join(D, n), 'rb').read()
    e, o = mparse(b)
    ne = []
    for h, s in e:
        t = tmap.get(s, s)
        used.update(t)
        ne.append((h, t))
    put(n, mbuild(ne) + b[o:])

# ---- layouts (in-place txt1 edit)
lay = json.load(open(os.path.join(B, 'translation', 'layout_ko.json'), encoding='utf-8'))
ph = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')
nl = 0
for n in sorted(os.listdir(D)):
    p = os.path.join(D, n)
    b = bytearray(open(p, 'rb').read())
    if b[:4] != b'darc':
        continue
    changed = False
    for i, isdir, name, a, c in dparse(bytes(b)):
        if isdir or not name.endswith('.bclyt'):
            continue
        hs = struct.unpack_from('<H', b, a + 6)[0]
        nb = struct.unpack_from('<I', b, a + 0x10)[0]
        o = a + hs
        for k in range(nb):
            m = bytes(b[o:o + 4]); sz = struct.unpack_from('<I', b, o + 4)[0]
            if m == b'txt1':
                ln, rl = struct.unpack_from('<HH', b, o + 0x4c)
                to = struct.unpack_from('<I', b, o + 0x58)[0]
                if ln:
                    t = bytes(b[o + to:o + to + ln]).decode('utf-16le').rstrip('\0')
                    if JP.search(t):
                        nt = lay.get(t)
                        if nt is None:
                            nt = ph.sub('가', t)
                        maxc = ln // 2 - 1
                        if len(nt) > maxc:
                            print('  trunc', repr(t), '->', repr(nt[:maxc]))
                            nt = nt[:maxc]
                        used.update(nt)
                        enc = nt.encode('utf-16le') + b'\0\0'
                        b[o + to:o + to + ln] = enc + b'\0' * (ln - len(enc))
                        struct.pack_into('<H', b, o + 0x4c, len(enc))
                        changed = True; nl += 1
            o += sz
    if changed:
        put(n, bytes(b))
print('layout texts', nl)

# ---- fonts
hang = [ord(c) for c in used if 0xac00 <= ord(c) <= 0xd7a3]
fm, nc, ns = fbuild(os.path.join(D, '2620443203'), TTF, 12, hang, (1, 11, 1, 11))
put('2620443203', fm); print('main font', nc, ns)
fs, nc2, ns2 = fbuild(os.path.join(D, '0520038286'), TTF, 15, hang, (2, 15, 1, 14))
put('0520038286', fs); print('sub font', nc2, ns2)

# ---- code.bin greeting
code = bytearray(open(os.path.join(B, 'work', 'ext', 'code.bin'), 'rb').read())
g = 'よろしくおねがいします'.encode('utf-16le') + b'\0\0'
i = code.find(g)
if i >= 0:
    ng = '잘 부탁합니다'.encode('utf-16le') + b'\0\0'
    code[i:i + len(g)] = ng + b'\0' * (len(g) - len(ng))
repl['movie/op_00.moflex'] = open(os.path.join(B, 'work', 'op_00_ko.moflex'), 'rb').read()
rbuild(ROM, OUT, repl, newcode=bytes(code))
print('built', OUT, os.path.getsize(OUT))
