# 連れ歩きの試験用の状態を作る: 手持ち（最初のピカチュウ＋ほか）で、トキワシティに出る
import sys; sys.path.insert(0,'.')
from lib import *
k=sys.argv[1]; dest=int(sys.argv[2]) if len(sys.argv)>2 else 1
r,s=rom(k); S,BK=loadsym(s)
g=GR(r,state=f'/tmp/claude-0/room2_{k}.st')
P=const('STARTER_PIKACHU') if 0 else 0x54
mons=[mon(0x54,10,30,30,[0x54],[30]), mon(const('BULBASAUR'),10,30,30,[0x21],[30]), mon(const('CHARMANDER'),10,30,30,[0x21],[30]), mon(const('GENGAR'),30,80,80,[0x21],[30])]
set_party(g,S,mons)
for i in range(len(mons)): g.pokes(S['wPartyMon1']+44*i+27,[0x10+i,0x20+i])
g.poke(S['wEventFlags'], g.peek(S['wEventFlags'])[0]|1)  # オーキドの研究所に行った（マサラの北でとめられない）
g.poke(S['wRepelRemainingSteps'],255)  # 野生のポケモンが出ない
g.poke(S['wDestinationMap'],dest)
f=g.peek(S['wStatusFlags6'])[0]; g.poke(S['wStatusFlags6'], f|0x0c)
g.down('R'); g.wait(18); g.up('R')
g.wait(200)
for i in range(3): g.press('B',4,20)
ndown=int(sys.argv[4]) if len(sys.argv)>4 else 2
for i in range(ndown):
    g.down('D'); g.wait(17); g.up('D'); g.wait(40)
print('map', g.peek(S['wCurMap'])[0], 'pika', [hex(x) for x in g.peek(0xc1f0,4)], 'd471', hex(g.peek(S['wd471'])[0]), 'flags', hex(g.peek(S['wPikachuOverworldStateFlags'])[0]), 'spawn', g.peek(S['wPikachuSpawnState'])[0])
tag=sys.argv[3] if len(sys.argv)>3 else 'fol'
g.shot(f'/tmp/claude-0/{tag}_{k}.png'); g.save_state(f'/tmp/claude-0/{tag}_{k}.st')
