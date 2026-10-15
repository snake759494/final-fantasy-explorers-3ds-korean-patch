import struct
def parse(b):
    assert b[:4]==b'darc'
    hl,ver,fsize,tabo,tabl,datao=struct.unpack_from('<HIIIII',b,6)
    n=struct.unpack_from('<I',b,tabo+8)[0]
    ents=[struct.unpack_from('<III',b,tabo+i*12) for i in range(n)]
    nt=tabo+n*12
    def nm(o):
        e=b.find(b'\0\0',nt+o);
        while (e-(nt+o))%2: e=b.find(b'\0\0',e+1)
        return b[nt+o:e].decode('utf-16le')
    res=[];stack=[]
    path=['']*64
    for i,(no,a,c) in enumerate(ents):
        isdir=no>>24;name=nm(no&0xffffff)
        res.append((i,isdir,name,a,c))
    return res
