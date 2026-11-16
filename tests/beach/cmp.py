# サマービーチだけの ROM と、ピカチュウフルカラー（xf）の海の家からのサマービーチを、同じ操作で動かして比べる
import os, sys, random
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
R=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../build/')
def sync(g, want=1, limit=3000):
    for i in range(limit):
        if g.peek(0xc5d1)[0]==want: return i
        g.wait(1)
    raise SystemExit('no sync')
def align(g):
    # 比べるためだけに、乱数・DIV・3フレームごとの入力の位相をそろえる
    g.poke(0xffd3,0); g.poke(0xffd4,0); g.poke(0xffd5,0); g.poke(0xff04,0)
def script(seed, n):
    rnd=random.Random(seed); ev=[]; t=0
    while t<n:
        k=rnd.choice(['L','R','U','D','A','',''])
        d=rnd.randint(4,40); ev.append((t,k,d)); t+=d+rnd.randint(2,20)
    return ev
def play(g, name, seed, frames):
    g.rec(name); t=0
    for (s,k,d) in script(seed, frames):
        if s>t: g.wait(s-t); t=s
        if k: g.down(k)
        g.wait(d); t+=d
        if k: g.up(k)
    if frames>t: g.wait(frames-t)
    g.stop()
if __name__=='__main__':
    seed=int(sys.argv[1]); frames=int(sys.argv[2]); out=sys.argv[3]
    a=GR(R+'summer_beach.gbc'); a.wait(60); ia=sync(a)
    b=GR(R+'xf.gbc', state='/tmp/cmp/talk.st'); ib=sync(b)
    if '--align' in sys.argv: align(a); align(b)
    play(a, out+'_a', seed, frames); play(b, out+'_b', seed, frames)
    for g,nm in ((a,'a'),(b,'b')):
        print(nm, 'routine', g.peek(0xc5d1), 'hp', g.peek(0xc5d6,2), 'rad', g.peek(0xc5da,2), 'total', g.peek(0xc5dc,2), 'hi', g.peek(0xd414,2))
    a.close(); b.close()
