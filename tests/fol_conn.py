# マップのつながり: 方向 d に歩いて、マップがかわる前後のようすをとる
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]; st=sys.argv[2]; slot=int(sys.argv[3]); d=sys.argv[4]; n=int(sys.argv[5]); tag=sys.argv[6]
g,S=start(k,st,slot)
for leg in (sys.argv[7].split(',') if len(sys.argv)>7 else []):
    step(g,leg[0],int(leg[1:]))
g.wait(20); print('start', pos(g,S), fpos(g,S))
m0=pos(g,S)[2]; files=[]; changed=None
g.down(d)
for f in range(n*17):
    g.wait(1)
    p=pos(g,S)
    if p[2]!=m0 and changed is None: changed=f; print('map change at frame', f, p)
    if changed is not None and f-changed<40 or f%4==0:
        if changed is not None and f-changed<40:
            fn=f'/tmp/claude-0/{tag}_{f:03d}.png'; g.shot(fn); files.append(fn)
            print(f, p, fpos(g,S), [x[1:4] for x in follower_oam(g)][:1])
g.up(d); g.wait(30)
g.shot(f'/tmp/claude-0/{tag}_end.png'); print('end', pos(g,S), fpos(g,S))
if files: strip(files[::2][:16], f'/tmp/claude-0/{tag}_strip.png', crop=(40,30,120,110), scale=2, cols=8)
g.save_state(f'/tmp/claude-0/{tag}.st')
