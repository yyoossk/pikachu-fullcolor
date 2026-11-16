import os, sys; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, R
out={}
for which in 'ab':
    g = GR(R+os.environ.get('BEACH_ROM','summer_beach.gbc')) if which=='a' else GR(R+'xf.gbc', state='/tmp/cmp/talk.st')
    if which=='a': g.wait(60)
    # はじめの画面（イントロ）
    for i in range(400):
        if g.pc().split('bank=')[1].startswith('3e') and g.peek(0xc5d1)[0]==0: break
        g.wait(1)
    g.wait(60); p0=g.pals()
    sync(g); g.wait(100); p1=g.pals()
    sync(g,11,20000); g.wait(30); p2=g.pals()
    out[which]=(p0,p1,p2); g.close()
for i,n in enumerate(['intro','game','results']):
    print(n, 'same' if out['a'][i]==out['b'][i] else 'DIFF\n a '+out['a'][i]+'\n b '+out['b'][i])
