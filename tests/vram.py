import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]
r,s=rom(k); S,BK=loadsym(s)
for st in sys.argv[2:]:
    g=GR(r,state=st); g.wait(2)
    for bank in (0,1):
        d=g.vpeek(bank,0x8800,0x1000)
        empty=[i for i in range(256) if not any(d[i*16:(i+1)*16])]
        # tile index: 8800-8fff => $80-$ff, 9000-97ff => $00-$7f
        idx=[(t+0x80)&0xff for t in empty]
        print(st.split('/')[-1], 'bank',bank, 'empty', len(idx), ' '.join(f'{x:02x}' for x in sorted(idx)))
    g.close()
