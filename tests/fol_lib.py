# 連れ歩きの試験の道具
import sys; sys.path.insert(0,'/home/claude/pk/fc/tests')
from lib import *
from PIL import Image
def start(k, st, slot=None):
    r,s=rom(k); S,BK=loadsym(s)
    g=GR(r,state=st); g.wait(2)
    if slot is not None: choose(g,S,slot)
    return g,S
def choose(g,S,slot):
    base=S['wPartyMon1']+44*slot
    otid=g.peek(base+12,2); dv=g.peek(base+27,2)
    g.poke(0xd3f5,1); g.pokes(0xd3f6,[otid[0],otid[1],dv[0]]); g.poke(0xd3f3,dv[1]); g.wait(10)
def pos(g,S): return g.peek(S['wXCoord'])[0], g.peek(S['wYCoord'])[0], g.peek(S['wCurMap'])[0]
def fpos(g,S):
    # 連れ歩きのマップの場所（MapY, MapX は 4 足してある）と向き・絵
    y,x=g.peek(0xc2f4,2); return x-4,y-4,g.peek(0xc1f9)[0],g.peek(0xc1f2)[0]
def step(g,d,n=1,hold=17,after=6):
    for i in range(n):
        g.down(d); g.wait(hold); g.up(d); g.wait(after)
def strip(files, out, crop=None, scale=2, cols=8):
    ims=[Image.open(f).convert('RGB') for f in files]
    if crop: ims=[im.crop(crop) for im in ims]
    ims=[im.resize((im.width*scale,im.height*scale),Image.NEAREST) for im in ims]
    w,h=ims[0].size; rows=(len(ims)+cols-1)//cols
    W=Image.new('RGB',(w*min(cols,len(ims)),h*rows))
    for i,im in enumerate(ims): W.paste(im,((i%cols)*w,(i//cols)*h))
    W.save(out)
def follower_oam(g):
    o=g.oam(); return [(i,o[i*4],o[i*4+1],o[i*4+2],o[i*4+3]) for i in range(40) if 0<o[i*4]<160 and (o[i*4+2]&0x7f)-0x0c in range(12)]
