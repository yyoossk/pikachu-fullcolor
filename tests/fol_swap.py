# 手持ち: SELECT でえらんだあと、ならびかえても★がそのポケモンについていくか。たたかいの手持ちでは SELECT がきかないか
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]
g,S=start(k,f'/tmp/claude-0/pal_{k}.st')
fs=[]
def shot(n):
    fn=f'/tmp/claude-0/sw_{n}.png'; g.shot(fn); fs.append(fn)
    print(n, 'mode', g.peek(0xd3f5)[0], 'species', g.peek(S['wPartySpecies'],4), 'oam39', g.oam()[39*4:39*4+4].hex())
g.press('S',4,40); g.press('A',4,90)
g.press('D',4,15); g.press('D',4,15); g.press('s',4,40); shot('sel2')
g.press('A',4,40); shot('sub')
g.press('D',4,15); g.press('A',4,40); shot('swapmode')
g.press('U',4,15); g.press('U',4,15); g.press('A',4,90); shot('swapped')
g.press('s',4,30); shot('sel_in_swap?')
for i in range(3): g.press('B',4,40)
g.wait(60); shot('map')
print('follower species ok?', g.wpeek(7,0xd010,3))
strip(fs,'/tmp/claude-0/sw_strip.png',scale=1,cols=6)
