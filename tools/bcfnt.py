import struct
def read(b):
    fi=0x14
    ftype,lf,alt=struct.unpack_from('<BBH',b,fi+8)
    dl,dg,dc,enc=struct.unpack_from('<bBBB',b,fi+12)
    tg,cw,cm=struct.unpack_from('<III',b,fi+16)
    h,w,asc=struct.unpack_from('<BBB',b,fi+28)
    t=tg-8
    cw_,ch,bl,mw,ss,ns,fmt,cols,rows,sw,sh,so=struct.unpack_from('<BBBBIHHHHHHI',b,t+8)
    sheets=[b[so+i*ss:so+(i+1)*ss] for i in range(ns)]
    widths={}
    o=cw
    while o:
        s,e,nx=struct.unpack_from('<HHI',b,o);
        for i in range(s,e+1): widths[i]=struct.unpack_from('<bBB',b,o+8+3*(i-s))
        o=nx
    cmap={}
    o=cm
    while o:
        cs,ce,mt,_,nx=struct.unpack_from('<HHHHI',b,o)
        if mt==0:
            off=struct.unpack_from('<H',b,o+12)[0]
            for c in range(cs,ce+1): cmap[c]=off+c-cs
        elif mt==1:
            for c in range(cs,ce+1):
                v=struct.unpack_from('<H',b,o+12+2*(c-cs))[0]
                if v!=0xffff: cmap[c]=v
        else:
            n=struct.unpack_from('<H',b,o+12)[0]
            for k in range(n):
                c,v=struct.unpack_from('<HH',b,o+14+4*k);cmap[c]=v
        o=nx
    return dict(ftype=ftype,lf=lf,alt=alt,dw=(dl,dg,dc),enc=enc,h=h,w=w,asc=asc,cw=cw_,ch=ch,bl=bl,mw=mw,ss=ss,fmt=fmt,cols=cols,rows=rows,sw=sw,sh=sh,sheets=sheets,widths=widths,cmap=cmap)
