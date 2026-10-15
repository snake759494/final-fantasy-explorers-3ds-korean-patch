import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from yuv import load
from scipy import ndimage
REF={'C1':240,'C2':400,'C3':540,'C4':720,'C5':840,'C6':1000,'C7':1560,'C8':1730}
RANGES={'C1':(185,330),'C2':(290,480),'C3':(450,640),'C4':(640,770),'C5':(740,960),'C6':(930,1080),'C7':(1503,1660),'C8':(1640,1793)}
def Y(i): return load(f'fr/{i:05d}.yuv')[0].astype(float)
out={}
for c,r in REF.items():
    y=Y(r)
    # text = bright pixels in upper/central area that have dark neighbor (outline/shadow)
    bright=y>215
    dark=ndimage.minimum_filter(y,size=5)<y-60
    m=bright&dark
    m[:20]=False;m[200:]=False
    lab,n=ndimage.label(ndimage.binary_dilation(m,iterations=3))
    # keep components in the central text band: take rows with many hits
    rows=np.where(m.sum(1)>3)[0]
    cols=np.where(m.sum(0)>0)[0]
    bbox=[int(rows.min()),int(rows.max()),int(cols.min()),int(cols.max())]
    ring=ndimage.binary_dilation(m,iterations=2)&~m
    def contrast(i):
        yy=Y(i);return yy[m].mean()-yy[ring].mean()
    full=contrast(r)
    a,b=RANGES[c]
    al={i:round(max(0.0,min(1.0,contrast(i)/full)),3) for i in range(a,b+1)}
    out[c]=dict(ref=r,bbox=bbox,alpha=al,npx=int(m.sum()))
    act=[i for i,v in al.items() if v>0.08]
    print(c,bbox,int(m.sum()),'active',act[0] if act else None,act[-1] if act else None)
json.dump(out,open('caps.json','w'))
