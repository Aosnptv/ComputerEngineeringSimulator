"""Standalone-only menus and result overlay; no extra ShowBase or shared UI."""
import math
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from panda3d.core import Geom,GeomNode,GeomTriangles,GeomVertexData,GeomVertexFormat,GeomVertexWriter
from .score_policy import trial_stars,TRIAL_THRESHOLDS,clock_text


def star(parent,x,z,earned):
    data=GeomVertexData('star',GeomVertexFormat.get_v3(),Geom.UH_static)
    writer=GeomVertexWriter(data,'vertex');writer.add_data3(0,0,0)
    for i in range(10):
        angle=math.pi/2+i*math.pi/5
        radius=.135 if i%2==0 else .061
        writer.add_data3(math.cos(angle)*radius,0,math.sin(angle)*radius)
    tris=GeomTriangles(Geom.UH_static)
    for i in range(10):tris.add_vertices(0,i+1,(i+1)%10+1)
    geom=Geom(data);geom.add_primitive(tris);node=GeomNode('star');node.add_geom(geom)
    np=parent.attach_new_node(node);np.set_pos(x,-.04,z);np.set_two_sided(True)
    np.set_light_off();np.set_color((1,.76,.15,1) if earned else (.22,.28,.36,1))
    return np

class Panel:
    def __init__(self,base,t,font=None,parent=None):
        self.t=t;self.font=font
        self.root=DirectFrame(parent=parent or base.aspect2d,frameColor=(.015,.025,.05,.98),frameSize=(-3,3,-2,2))
        self.card=DirectFrame(parent=self.root,frameColor=(.045,.085,.14,1),frameSize=(-1.18,1.18,-.89,.89))
        self.buttons={}
    def label(self,text,z,scale=.06,color=(.94,.97,1,1)):
        return DirectLabel(parent=self.card,text=text,text_font=self.font,text_scale=scale,
            text_fg=color,text_wordwrap=35,frameColor=(0,0,0,0),pos=(0,-.05,z))
    def button(self,key,text,x,z,command):
        button=DirectButton(parent=self.card,text=text,text_font=self.font,text_scale=.055,
            text_fg=(1,1,1,1),frameColor=(.07,.35,.52,1),frameSize=(-.45,.45,-.085,.085),
            pos=(x,-.08,z),command=command,pressEffect=1)
        self.buttons[key]=button
        return button
    def destroy(self):self.root.destroy()

class ResultPanel(Panel):
    def __init__(self,base,t,font,result,on_replay,on_menu,parent=None):
        super().__init__(base,t,font,parent)
        self.result=dict(result)
        self.stars=trial_stars(result['difficulty'],result['elapsed_seconds'],result['mistakes'])
        self.label(t('result.title'),.70,.085,(.18,1,.58,1))
        self.label(t('result.message'),.56,.045)
        self.star_nodes=[star(self.card,x,.33,i<self.stars) for i,x in enumerate((-.36,0,.36))]
        self.label(f'{self.stars}/3',.12,.06,(1,.80,.26,1))
        self.label(t('result.time',time=clock_text(result['elapsed_seconds'])),-.02,.065)
        self.label(t('result.errors',n=result['mistakes']),-.15,.065)
        self.label(t('result.draft'),-.28,.035,(.65,.76,.86,1))
        t3,e3,t2,e2=TRIAL_THRESHOLDS[result['difficulty']]
        self.label(t('result.policy',t3=clock_text(t3),e3=e3,t2=clock_text(t2),e2=e2),-.37,.033,(.65,.76,.86,1))
        self.button('replay',t('result.replay'),-.53,-.71,on_replay)
        self.button('menu',t('result.menu'),.53,-.71,on_menu)

class MainMenu(Panel):
    def __init__(self,base,t,font,on_start,on_quit,parent=None,exit_key='menu.quit'):
        super().__init__(base,t,font,parent)
        self.label(t('menu.title'),.64,.085)
        self.label(t('menu.subtitle'),.43,.05)
        for level,z in [('easy',.10),('medium',-.18)]:
            self.button(level,t('level.'+level),0,z,lambda value=level:on_start(value))
        self.label(t('menu.note'),-.53,.035,(.65,.76,.86,1))
        self.button('quit',t(exit_key),0,-.72,on_quit)
