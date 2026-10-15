import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from subs import place,KO
from scipy import ndimage
W,H=400,240
caps=json.load(open('caps.json'))
os.makedirs('tg',exist_ok=True)
for f in os.listdir('tg'): os.remove('tg/'+f)
lay={c:place(c) for c in KO}
frames={}
for c,v in caps.items():
    al={int(k):a for k,a in v['alpha'].items()}
    ks=sorted(al);arr=np.array([al[k] for k in ks])
    for k,a in zip(ks,arr):
        if a>0: frames.setdefault(k,[]).append((c,float(a)))
for i,lst in sorted(frames.items()):
    b=np.fromfile(f'fr/{i:05d}.yuv',np.uint8).astype(float)
    Y=b[:W*H].reshape(H,W);U=b[W*H:W*H*5//4].reshape(H//2,W//2);V=b[W*H*5//4:].reshape(H//2,W//2)
    for c,a in lst:
        fa,sa,x0,y0=lay[c];h,w=fa.shape
        aS=sa*a;aF=fa*a
        reg=Y[y0:y0+h,x0:x0+w]
        reg[:]=reg*(1-aS)+16*aS
        reg[:]=reg*(1-aF)+235*aF
        # chroma: desaturate under text coverage
        cov=np.zeros((H,W));cov[y0:y0+h,x0:x0+w]=np.maximum(aS,aF)
        c2=cov.reshape(H//2,2,W//2,2).mean((1,3))
        U[:]=U*(1-c2)+128*c2;V[:]=V*(1-c2)+128*c2
    out=np.concatenate([Y.ravel(),U.ravel(),V.ravel()])
    np.clip(np.round(out),0,255).astype(np.uint8).tofile(f'tg/{i:05d}.yuv')
print(len(frames),min(frames),max(frames))
