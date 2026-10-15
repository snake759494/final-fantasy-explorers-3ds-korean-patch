import struct
def none_wrap(orig_romfs_bytes,data):
    # BLZ container with an empty compressed region: decoder copies nothing, data used as-is
    hdr=b'blz\0'+orig_romfs_bytes[4:8]
    body=data
    pad=(-len(body))%4
    body+=b'\xff'*pad
    return hdr+body+struct.pack("<II",((8+pad)<<24)|(8+pad),0)
