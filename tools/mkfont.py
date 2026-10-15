import sys,struct,os,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from bcfnt import read
from tex import untile,tile,untile4,tile4
from PIL import Image,ImageDraw,ImageFont
def ksx1001():
    s=[]
    for hi in range(0xb0,0xc9):
        for lo in range(0xa1,0xff):
            try: s.append(bytes([hi,lo]).decode('euc-kr'))
            except: pass
    return s
def isideo(c): return 0x3400<=c<=0x9fff or 0xf900<=c<=0xfaff
def build(src,ttf,size,extra_chars,box,keep_ideo=False):
    b=open(src,'rb').read();f=read(b)
    cw,ch=f['cw'],f['ch'];px,py=cw+1,ch+1
    cols,rows,sw,sh=f['cols'],f['rows'],f['sw'],f['sh'];per=cols*rows
    a4=f['fmt']==11
    if a4: ims=[untile4(s,sw,sh) for s in f['sheets']]
    else: ims=[untile(s,sw,sh,2)[:,:,0] for s in f['sheets']]
    def getcell(i):
        s=i//per;r=i%per;y=(r//cols)*py;x=(r%cols)*px;return ims[s][y:y+ch,x:x+cw]
    glyphs={}
    for c,i in f['cmap'].items():
        if isideo(c) and not keep_ideo: continue
        glyphs[c]=(getcell(i),f['widths'].get(i,f['dw']))
    font=ImageFont.truetype(ttf,size)
    y0,y1,x0,x1=box;bw=x1-x0+1;bh=y1-y0+1
    # vertical: align all hangul using a common reference (the '가' bbox doesn't vary much); use font ascent-based fixed position
    ref=ImageDraw.Draw(Image.new('L',(64,64))).textbbox((0,0),'한',font=font)
    hw=None
    for c in sorted(set(ord(x) for x in ksx1001())|set(extra_chars)):
        if c in glyphs: continue
        chs=chr(c)
        im=Image.new('L',(cw,ch));d=ImageDraw.Draw(im)
        bb=d.textbbox((0,0),chs,font=font)
        w=bb[2]-bb[0]
        if 0xac00<=c<=0xd7a3 or 0x3131<=c<=0x318e:
            ox=x0+(bw-w)//2-bb[0];oy=y0+(bh-(ref[3]-ref[1]))//2-ref[1]
            d.text((ox,oy),chs,font=font,fill=255)
            glyphs[c]=(np.array(im),(0,cw,f['widths'][f['cmap'][0x3042]][2]) if 0x3042 in f['cmap'] else (0,cw,cw))
        else:
            continue
    codes=sorted(glyphs)
    nsheets=(len(codes)+per-1)//per
    sheets=[]
    for s in range(nsheets):
        img=np.zeros((sh,sw),np.uint8)
        for k,c in enumerate(codes[s*per:(s+1)*per]):
            y=(k//cols)*py;x=(k%cols)*px;img[y:y+ch,x:x+cw]=glyphs[c][0]
        if a4: sheets.append(tile4(img))
        else:
            la=np.stack([img,np.where(img>0,255,0).astype(np.uint8)],2);sheets.append(tile(la))
    # assemble
    fi=0x14;tg_off=0x34
    finf=bytearray(b[fi:fi+0x20])
    tglp=bytearray(b[tg_off:tg_off+0x20])
    so=struct.unpack_from('<I',b,tg_off+0x1c)[0]
    hdrpad=b'\0'*(so-(tg_off+0x20))
    struct.pack_into('<H',tglp,0x10,nsheets)
    sheetdata=b''.join(sheets)
    struct.pack_into('<I',tglp,4,0x20+len(hdrpad)+len(sheetdata))
    cwdh_off=so+len(sheetdata)
    cwdh=bytearray(b'CWDH'+b'\0'*4+struct.pack('<HHI',0,len(codes)-1,0))
    for c in codes: cwdh+=struct.pack('<bBB',*glyphs[c][1])
    while len(cwdh)%4: cwdh+=b'\0'
    struct.pack_into('<I',cwdh,4,len(cwdh))
    cmap_off=cwdh_off+len(cwdh)
    cmap=bytearray(b'CMAP'+b'\0'*4+struct.pack('<HHHHI',codes[0],codes[-1],2,0,0)+struct.pack('<H',len(codes)))
    for k,c in enumerate(codes): cmap+=struct.pack('<HH',c,k)
    while len(cmap)%4: cmap+=b'\0'
    struct.pack_into('<I',cmap,4,len(cmap))
    # FINF pointers (point to block data = block+8)
    struct.pack_into('<III',finf,0x10,tg_off+8,cwdh_off+8,cmap_off+8)
    # alt char: '?' index
    alt=codes.index(0x30fb) if 0x30fb in codes else codes.index(ord('?'))
    struct.pack_into('<H',finf,0xa,alt)
    hdr=bytearray(b[:0x14])
    total=cmap_off+len(cmap)
    struct.pack_into('<I',hdr,0xc,total);struct.pack_into('<I',hdr,0x10,4)
    out=bytes(hdr)+bytes(finf)+bytes(tglp)+hdrpad+sheetdata+bytes(cwdh)+bytes(cmap)
    assert len(out)==total
    return out,len(codes),nsheets
if __name__=='__main__':
    pass
