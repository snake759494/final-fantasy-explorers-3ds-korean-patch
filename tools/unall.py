import os,sys,collections
sys.path.insert(0,os.path.dirname(__file__))
from codeblz import decompress
src,dst=sys.argv[1],sys.argv[2];os.makedirs(dst,exist_ok=True)
c=collections.Counter();ex={}
for n in sorted(os.listdir(src)):
    p=os.path.join(src,n)
    if not os.path.isfile(p): continue
    b=open(p,'rb').read()
    if b[:4]==b'blz\0': b=decompress(b)[8:]
    elif b[:4]==b'none': b=b[8:]
    else: continue
    open(os.path.join(dst,n),'wb').write(b)
    k=b[:4];c[k]+=1;ex.setdefault(k,[]).append((n,len(b)))
for k,v in c.most_common(): print(k,v,ex[k][:3])
