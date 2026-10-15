import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from moflex import parse,frames
from mux import groups,mux
from apply import readtc
src,dst=sys.argv[1],sys.argv[2]
rep={}
for t in sys.argv[3:]: rep.update(readtc(t))
b=open(src,'rb').read()
gs=groups(parse(b))
vi=0
for g in gs:
    for f in g['frames']:
        if f[0]==0:
            if vi in rep: f[2]=rep[vi]
            vi+=1
m,sp=mux(gs)
# fix index (group 0 stream-2 packet)
d=bytearray(gs[0]['frames'][0][2]);n=struct.unpack_from('<I',d,0)[0]
assert n==len(sp)-1
for k in range(n):
    kf,ts,off=struct.unpack_from('<QQQ',d,16+24*k)
    struct.pack_into('<QQQ',d,16+24*k,kf,ts,sp[k+1])
gs[0]['frames'][0][2]=bytes(d)
m2,sp2=mux(gs)
assert sp2==sp
open(dst,'wb').write(m2)
print('frames',vi,'replaced',len(rep),'size',len(b),'->',len(m2))
