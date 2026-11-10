# 回転床（ロケット団のアジト B2F）: ワープの行き先をかえて行き、回転床にのる
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]
g,S=start(k,f'/tmp/claude-0/vir_{k}.st',2)
MAP=int(sys.argv[4],16) if len(sys.argv)>4 else 0xc8
g.pokes(S['wWarpEntries'],[25,23,int(sys.argv[2]) if len(sys.argv)>2 else 0,MAP])
g.down('U')
for i in range(80):
    g.wait(1)
    if pos(g,S)[2]==MAP: break
g.up('U'); g.wait(80)
print('arrive', pos(g,S), fpos(g,S)); g.shot('/tmp/claude-0/sp_0.png')
g.save_state(f'/tmp/claude-0/hide_{k}.st')
fs=['/tmp/claude-0/sp_0.png']; spun=0
for t,d in enumerate((sys.argv[3] if len(sys.argv)>3 else 'DDDDLLLLLLDDDDRRRRUUUULLLLDDDD')):
    g.down(d)
    for i in range(18):
        g.wait(1)
        if g.peek(S['wMovementFlags'])[0]&0x80 or g.peek(S['wJoyIgnore'])[0]: spun+=1
    g.up(d); g.wait(4)
    if t%3==2:
        fn=f'/tmp/claude-0/sp_{t}.png'; g.shot(fn); fs.append(fn)
    print(d, pos(g,S), fpos(g,S), 'spin', spun, g.pc())
strip(fs,f'/tmp/claude-0/sp_strip_{k}.png',scale=1,cols=6)
