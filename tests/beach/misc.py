import os, sys, os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../sameboy-harness/python'))
from gr import GR
from cmp import sync, R
def A(sav=None):
    g=GR(R+os.environ.get('BEACH_ROM','summer_beach.gbc'), sav=sav); g.wait(60); return g
def finish(g, limit=20000):
    # 何も押さずに結果まで、そのあと A
    sync(g,11,limit); g.wait(30); g.shot('/tmp/cmp/m_res.png'); g.press('A',4,10)
def sram(path): d=open(path,'rb').read(); return d[0x3f00:0x3f05].hex()
mode=sys.argv[1]
if mode=='gameover':
    for w in 'ab':
        g = A() if w=='a' else GR(R+'xf.gbc', state='/tmp/cmp/talk.st')
        sync(g); g.wait(50); g.pokes(0xc5d6,[0x10,0]); g.wait(120); g.shot(f'/tmp/cmp/go_{w}1.png')
        print(w,'routine',g.peek(0xc5d1), 'hi',g.peek(0xd414,2))
        g.wait(200); g.press('A',4,200); g.shot(f'/tmp/cmp/go_{w}2.png'); print(w,'after A',g.pc(), g.peek(0xc5d1))
        g.close()
if mode=='ffsav':
    open('/tmp/cmp/ff.sav','wb').write(b'\xff'*0x8000)
    g=A('/tmp/cmp/ff.sav'); g.wait(200); print('hi at boot', g.peek(0xd414,2))
    finish(g); g.wait(200); g.bsave('/tmp/cmp/ff_after.sav'); print('hi', g.peek(0xd414,2), 'sram', sram('/tmp/cmp/ff_after.sav')); g.close()
if mode=='notbest':
    d=bytearray(b'\x00'*0x8000); d[0x3f00:0x3f05]=bytes([0x53,0x42,0x99,0x99,(~(0x99+0x99))&0xff]); open('/tmp/cmp/nb.sav','wb').write(d)
    g=A('/tmp/cmp/nb.sav'); g.wait(200); print('hi at boot', g.peek(0xd414,2))
    finish(g); g.wait(200); g.bsave('/tmp/cmp/nb_after.sav'); print('hi', g.peek(0xd414,2), 'sram', sram('/tmp/cmp/nb_after.sav')); g.close()
if mode=='rounds':
    g=A()
    for i in range(5):
        finish(g); g.wait(300)
        g.bsave('/tmp/cmp/rd.sav'); print('round',i+1,'hi',g.peek(0xd414,2),'sram',sram('/tmp/cmp/rd.sav'), g.pc())
    g.close()
if mode=='reset':
    g=A(); sync(g); g.wait(300)
    for k in 'ABSs': g.down(k)
    g.wait(10)
    for k in 'ABSs': g.up(k)
    g.wait(400); g.shot('/tmp/cmp/reset.png'); print('after reset', g.pc(), g.peek(0xc5d1)); g.close()
if mode=='select':
    g=A(); sync(g); g.wait(100)
    for i in range(5): g.press('s',4,30)
    print('after select', g.peek(0xc5d1), g.pc()); g.shot('/tmp/cmp/select.png'); g.close()
