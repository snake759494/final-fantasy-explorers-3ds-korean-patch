import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy import ndimage
W,H=400,240
FONT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','NanumSquareNeo-cBd.ttf')
KO=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','translation','movie_subs.json'),encoding='utf-8'))
BOTTOM={'C1':142,'C2':146,'C3':161,'C4':128,'C5':159,'C6':144,'C7':143,'C8':161}
SS=4
def render(text,size=12):
    f=ImageFont.truetype(FONT,size*SS)
    d=ImageDraw.Draw(Image.new('L',(10,10)))
    bb=d.textbbox((0,0),text,font=f,stroke_width=SS*1)
    w=bb[2]-bb[0]+8*SS;h=bb[3]-bb[1]+8*SS
    fill=Image.new('L',(w,h));stroke=Image.new('L',(w,h))
    ImageDraw.Draw(stroke).text((4*SS-bb[0],4*SS-bb[1]),text,font=f,fill=255,stroke_width=int(SS*1.25),stroke_fill=255)
    ImageDraw.Draw(fill).text((4*SS-bb[0],4*SS-bb[1]),text,font=f,fill=255)
    ws,hs=(w+SS-1)//SS,(h+SS-1)//SS
    def down(im):
        c=Image.new('L',(ws*SS,hs*SS));c.paste(im,(0,0));return np.asarray(c.resize((ws,hs),Image.BOX)).astype(float)/255
    return down(fill),down(stroke)
def place(c):
    fa,sa=render(KO[c])
    h,w=fa.shape
    x0=(W-w)//2;y0=BOTTOM[c]+2
    return fa,sa,x0,y0
if __name__=='__main__':
    for c in KO:
        fa,sa,x0,y0=place(c);print(c,fa.shape[1],'px wide', 'OK' if fa.shape[1]<=396 else 'TOO WIDE',x0,y0)
