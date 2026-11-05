import sys
def apply(base, ips):
    d=bytearray(base); p=ips; assert p[:5]==b'PATCH'; i=5
    while True:
        if p[i:i+3]==b'EOF':
            if len(p)>=i+6: n=int.from_bytes(p[i+3:i+6],'big'); del d[n:]
            break
        off=int.from_bytes(p[i:i+3],'big'); sz=int.from_bytes(p[i+3:i+5],'big'); i+=5
        if sz==0:
            rl=int.from_bytes(p[i:i+2],'big'); v=p[i+2]; i+=3; chunk=bytes([v])*rl
        else:
            chunk=p[i:i+sz]; i+=sz
        if off+len(chunk)>len(d): d.extend(b'\0'*(off+len(chunk)-len(d)))
        d[off:off+len(chunk)]=chunk
    return bytes(d)
if __name__=='__main__':
    open(sys.argv[3],'wb').write(apply(open(sys.argv[1],'rb').read(),open(sys.argv[2],'rb').read()))
