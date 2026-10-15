import numpy as np
from PIL import Image
W,H=400,240
def load(p):
    b=np.fromfile(p,np.uint8);Y=b[:W*H].reshape(H,W).astype(float);U=b[W*H:W*H+W*H//4].reshape(H//2,W//2).astype(float);V=b[W*H+W*H//4:].reshape(H//2,W//2).astype(float)
    return Y,U,V
def to_rgb(Y,U,V):
    U=U.repeat(2,0).repeat(2,1)-128;V=V.repeat(2,0).repeat(2,1)-128;Yc=(Y-16)*1.164
    r=Yc+1.596*V;g=Yc-0.392*U-0.813*V;b=Yc+2.017*U
    return np.clip(np.stack([r,g,b],2),0,255).astype(np.uint8)
def img(p): return Image.fromarray(to_rgb(*load(p)))
