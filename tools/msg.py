import struct
def parse(b):
    if len(b)<4 or b[0]!=0 or b[1]!=0x10: return None
    n=struct.unpack_from('<H',b,2)[0];o=4;out=[]
    try:
        for i in range(n):
            h=struct.unpack_from('<I',b,o)[0];o+=4;e=o
            while b[e:e+2]!=b'\0\0': 
                e+=2
                if e>len(b): return None
            out.append((h,b[o:e].decode('utf-16le')));o=e+2
    except Exception: return None
    return out,o
def build(entries):
    o=bytearray(struct.pack('<BBH',0,0x10,len(entries)))
    for h,s in entries: o+=struct.pack('<I',h)+s.encode('utf-16le')+b'\0\0'
    return bytes(o)
