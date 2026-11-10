# クリスタルで出た不具合を、ピカチュウ版で確かめる
import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]; H=17 if k=='v' else 9
def walk(g,S,d,n):
    for i in range(n):
        p0=pos(g,S); g.down(d); t=0
        while pos(g,S)==p0 and t<40: g.wait(1); t+=1
        g.up(d); g.wait(2)
# 1. 主人公の絵: 上へ歩いたあと、主人公のタイル（$8000〜$80BF, $8800〜$88BF）がピカチュウのときと同じか
res={}
for slot in (None,2):
    g,S=start(k,f'/tmp/claude-0/pal_{k}.st',slot)
    walk(g,S,'R',5); walk(g,S,'U',4); g.wait(20)
    res[slot]=(g.vpeek(0,0x8000,0xc0)+g.vpeek(0,0x8800,0xc0), g.vpeek(1,0x8000,0xc0))
print('1 主人公のタイル 同じ:', res[None][0]==res[2][0])
# 11. ★: 開きなおしても赤いまま（状態異常のポケモンもいる）
g,S=start(k,f'/tmp/claude-0/pal_{k}.st')
g.poke(S['wPartyMon1']+44*2+4, 0x08)  # ヒトカゲ どく
g.poke(S['wPartyMon1']+44*1+4, 0x40)  # フシギダネ まひ
cols=[]
for rep in range(3):
    g.press('S',4,60); g.press('A',4,90)
    if rep==0: g.press('D',4,15); g.press('D',4,15); g.press('s',4,40)
    g.wait(30); o=g.oam(); star=o[39*4:39*4+4]
    pal=g.pals().split('OB:')[1][7*16:7*16+16]
    g.shot(f'/tmp/claude-0/cr11_{rep}.png')
    cols.append((star.hex(), pal))
    g.press('B',4,60); g.press('B',4,60); g.wait(30)
print('11 ★（OAM, OBJパレット7）:', cols)
strip([f'/tmp/claude-0/cr11_{i}.png' for i in range(3)],'/tmp/claude-0/cr11.png',scale=1,cols=3)
