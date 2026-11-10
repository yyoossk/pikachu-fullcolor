# 全151匹: 2番めの手持ちの種類をかえて連れ歩き、下・上・横の絵を画面からとる（色・下じきの確認）
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]
g,S=start(k,f'/tmp/claude-0/pal_{k}.st',1)
for d in 'RL': step(g,d,1)
g.wait(20)
r_,s_=rom(k); rom_=open(r_,'rb').read()
b,a=[l.split()[0] for l in open(s_) if l.split()[1:]==['PokedexOrder']][0].split(':')
off=int(b,16)*0x4000+int(a,16)-0x4000
dex2int={}
for i in range(190):
    d=rom_[off+i]
    if 1<=d<=151 and d not in dex2int: dex2int[d]=i+1
W=Image.new('RGB',(16*3*2*10+20, 20*2*16))
for d in range(1,152):
    g.poke(S['wPartySpecies']+1, dex2int[d]); g.poke(S['wPartyMon1']+44, dex2int[d])
    g.wait(30)
    for j,face in enumerate((0,4,8)):
        g.poke(0xc1f9,face); g.poke(0xc1f2,face); g.wait(4)
        o=g.oam(); ent=[(o[i*4],o[i*4+1]) for i in range(40) if 0<o[i*4]<160 and (o[i*4+2]&0x7f)-0x0c in range(12) and o[i*4+3]&7==6]
        g.shot('/tmp/claude-0/am.png'); im=Image.open('/tmp/claude-0/am.png').convert('RGB')
        if ent:
            y=min(e[0] for e in ent)-16; x=min(e[1] for e in ent)-8
            c=im.crop((x-2,y-2,x+18,y+18)).resize((40,40),Image.NEAREST)
            i=d-1; W.paste(c,((i%10)*(40*3+4)+j*40,(i//10)*40))
    if d%30==0: print(d, flush=True)
W.save(f'/tmp/claude-0/allmons_{k}.png')
