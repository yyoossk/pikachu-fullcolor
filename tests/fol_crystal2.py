import sys; sys.path.insert(0,'.')
from fol_lib import *
k=sys.argv[1]
def walk(g,S,d,n,run=False):
    if run: g.down('B')
    for i in range(n):
        p0=pos(g,S); g.down(d); t=0
        while pos(g,S)==p0 and t<40: g.wait(1); t+=1
        g.up(d); g.wait(1)
    if run: g.up('B')
def offs(g):
    o=g.oam(); pl=[(o[i*4],o[i*4+1]) for i in range(40) if 0<o[i*4]<160 and o[i*4+2]<0x0c and o[i*4+3]&7==1]
    fo=[(o[i*4],o[i*4+1]) for i in range(40) if 0<o[i*4]<160 and (o[i*4+2]&0x7f)-0x0c in range(12) and not o[i*4+3]&8]
    if not pl or not fo: return None
    return (min(y for y,x in fo)-min(y for y,x in pl), min(x for y,x in fo)-min(x for y,x in pl))
# 2. ドアから出たすぐあと、主人公の足もとに連れ歩きが見えないか（家に入って出る）
g,S=start(k,f'/tmp/claude-0/pal_{k}.st',2)
walk(g,S,'U',1)
for i in range(60):
    g.wait(1)
    if pos(g,S)[2]!=0: break
g.wait(60); walk(g,S,'D',1); walk(g,S,'D',1)
same=0
for f in range(90):
    g.wait(1); p=pos(g,S); fp=fpos(g,S)
    if p[2]==0 and (fp[0],fp[1])==(p[0],p[1]) and fp[3]!=255 and offs(g)==(0,0): same+=1
print('2 外に出たあと、主人公と同じ場所に見えたフレーム:', same, pos(g,S), fpos(g,S))
g.shot('/tmp/claude-0/c2.png')
# 5. B ダッシュでつながりをこえたあと、絵が4ドットずれないか（マサラ→1ばんどうろ）
for slot in (None,2):
    g,S=start(k,f'/tmp/claude-0/pal_{k}.st',slot)
    walk(g,S,'R',5,run=True); walk(g,S,'U',10,run=True); g.wait(40)
    print('5 ダッシュでつながり', 'pika' if slot is None else 'kit', pos(g,S), fpos(g,S), '連れ歩きと主人公の絵のずれ(y,x)', offs(g))
    g.shot(f'/tmp/claude-0/c5_{slot}.png')
# 6. となりのマップに入ったとき、人の絵が主人公の絵などにならないか（人のタイルがピカチュウのときと同じか）＋ 色
vr={}
for slot in (None,2):
    g,S=start(k,f'/tmp/claude-0/pal_{k}.st',slot)
    walk(g,S,'R',5); walk(g,S,'U',12); g.wait(40)
    v=g.vpeek(0,0x8000,0x1000)
    v=v[:0xc0]+v[0x180:0x8c0]+v[0x980:]  # 連れ歩きの所をのぞく
    vr[slot]=v; g.shot(f'/tmp/claude-0/c6_{slot}.png')
    print('6', 'pika' if slot is None else 'kit', pos(g,S), 'pal6', g.pals().split('OB:')[1][96:112])
print('6 人のタイル 同じ:', vr[None]==vr[2])
# 9. つながり（下へ）で、連れ歩きの向きが一瞬ちがう向きにならないか
g,S=start(k,f'/tmp/claude-0/pal_{k}.st',2)
walk(g,S,'R',5); walk(g,S,'U',9)   # 1ばんどうろへ
print('9 start', pos(g,S))
walk(g,S,'D',1); g.wait(10)
faces=[]; m0=pos(g,S)[2]
g.down('D')
for f in range(60):
    g.wait(1); faces.append((pos(g,S)[2], g.peek(0xc1f9)[0], g.peek(0xc1f2)[0]))
g.up('D')
print('9 下へのつながり (マップ,向き,絵):', sorted(set(faces)))
# 9b. 横のつながり（シオンタウン ⇔ 8ばんどうろ）
for d in 'LR':
    g,S=start(k,f'/tmp/claude-0/lav_{k}.st',2)
    walk(g,S,'D',2)
    if d=='R': walk(g,S,'L',5); walk(g,S,'L',1)
    print('9b start', pos(g,S))
    faces=[]; g.down(d)
    for f in range(120):
        g.wait(1); faces.append((pos(g,S)[2], g.peek(0xc1f9)[0]))
    g.up(d); g.wait(20)
    print('9b', d, '(マップ,向き):', sorted(set(faces)), pos(g,S), fpos(g,S), 'ずれ', offs(g))
