"""Room-local procedural lab. Visuals, pick colliders and hints are independent."""
from panda3d.core import (Point3, TextNode, CollisionNode, CollisionBox,
    CollisionRay, CollisionTraverser, CollisionHandlerQueue, TransparencyAttrib, BitMask32)
from .scene import make_box, PICK_MASK, NO_MASK
from .models import make_cylinder,build_part, DEFAULT_TRAY_HPR, TRAY_HPR, HOLD_HPR
from .logic import Kind
from .lab_visuals import (surface_box,stone_texture,technical_texture,material,
                          setup_lights,wire_box,diagnostic_increment)

START_POS=(0,1.5)
ROOM_X=(-4.5,4.5)
ROOM_Y=(0,9)
ROOM_H=3.5
CASE_POS=(-.63,4.7,.98)
CHECK_BUTTON_POS=(1.10,4.43,1.0)
SLOT_LAYOUT3D={
 'psu':((.14,.02,.043),(.15,.14,.086)),
 'motherboard':((.07,.075,.2525),(.244,.02,.305)),
 'storage':((-.14,.085,.07),(.10,.0095,.07)),
 'cpu':((.125,.077,.32),(.045,.01,.045)),
 'cooler':((.125,.042,.32),(.12,.06,.12)),
 'ram':((.04,.065,.32),(.009,.034,.133)),
 'gpu':((.03,.027,.18),(.30,.11,.04))}
BLUE=(.02,.48,1,1)
GREEN=(.10,.95,.42,1)
RED=(1,.16,.18,1)
WHITE=(.87,.90,.94,1)
DARK=(.10,.14,.20,1)
DISPLAY={
 'mobo_lga':(-.65,7.7), 'mobo_am5':(.65,7.7),
 'cpu_intel':(-3.62,2.08), 'cpu_amd':(-3.62,2.85),
 'ram_ddr4':(-3.62,4.28), 'ram_ddr5':(-3.62,5.05),
 'ssd_std':(-3.62,6.85), 'gpu_std':(3.62,2.5),
 'psu_std':(3.62,4.7), 'cooler_std':(3.62,6.85)}
DISPLAY_SCALE={Kind.CPU:4.4,Kind.RAM:2.8,Kind.MOTHERBOARD:1.6,
 Kind.GPU:1.9,Kind.PSU:2.2,Kind.COOLER:2.4,Kind.STORAGE:3.0}

class RoomScene3D:
 def __init__(self,parent,render,parts,slots,translator,font=None,enhanced=False):
  diagnostic_increment('room_scene')
  self.root=parent.attach_new_node('pc_lab')
  self._stone=stone_texture();self._blueprint=technical_texture()
  self._materials={}
  self._metal=material("powder_coated_metal",30)
  self._white=material("laminate",55)
  self.level="easy"
  self._preview_np=None;self._held_id=None
  setup_lights(self.root,render)
  self._render=render; self._t=translator; self._font=font
  self._labels=[];self._parts={p.id:p for p in parts}
  self._part_np={};self._part_pick={};self._part_label={};self._tray_pos={}
  self._part_kind={};self._installed_at={};self._slot_ghost={};self._slot_pick={};self._pad_pick={}
  self._pad={};self._pad_label={};self._part_plinth={};self._arrows={}
  self._slot_ids=[s.id for s in slots]
  self.walk_bounds=(-4.18,4.18,.35,8.65);self.walk_obstacles=[]
  self._build_room();self._build_furniture();self._build_case()
  for i,s in enumerate(slots):self._build_slot(i,s)
  for p in parts:self._build_part(p)
  self._build_check_button();self._build_picker()

 def _box(self,size,pos,color,parent=None,texture=None):
  np=(parent if parent is not None else self.root).attach_new_node(surface_box(size,color,texture))
  np.set_pos(*pos);np.set_two_sided(True)
  if color not in self._materials:self._materials[color]=material('surface',35,color)
  np.set_material(self._materials[color])
  if texture:np.set_texture(texture)
  if pos[2]>3.4 and size[2]<.15:np.hide(BitMask32.bit(2))
  # Emissive trims and screens; conventional materials elsewhere.
  if color in (BLUE,GREEN,RED) or color==(1,1,1,1):np.set_light_off()
  return np

 def _text(self,key,pos,scale=.08,parent=None,hpr=None,width=25):
  diagnostic_increment('text_node')
  tn=TextNode(key);tn.set_text(self._t(key));tn.set_align(TextNode.A_center)
  tn.set_text_color(.9,.96,1,1);tn.set_wordwrap(width)
  if self._font is not None:tn.set_font(self._font)
  np=(parent if parent is not None else self.root).attach_new_node(tn)
  np.set_pos(*pos);np.set_scale(scale);np.set_light_off()
  if hpr is None:np.set_billboard_point_eye()
  else:np.set_hpr(*hpr)
  self._labels.append((tn,key));return np

 def _pick_box(self,np,size,center,tag):
  diagnostic_increment('collision_node')
  cn=CollisionNode(tag);cn.add_solid(CollisionBox(Point3(*center),*(v/2 for v in size)))
  cn.set_from_collide_mask(NO_MASK);cn.set_into_collide_mask(PICK_MASK)
  cnp=np.attach_new_node(cn);cnp.set_tag('pick',tag);return cn

 def _cabinet(self,x,y,w,d):
  self._box((w-.10,d-.10,.12),(x,y,.06),(.055,.065,.08,1))
  self._box((w,d,.78),(x,y,.49),(.11,.125,.15,1))
  self._box((w+.08,d+.08,.07),(x,y,.925),(.90,.91,.93,1),texture=self._stone)
  # Blue trims, cabinet doors and a raised sign rail.
  for z in (.11,.88):self._box((w+.03,d+.03,.012),(x,y,z),BLUE)
  for xx in (-w/4,w/4):
   self._box((w/2-.025,.015,.64),(x+xx,y-d/2-.01,.45),(.15,.20,.27,1))
  self.walk_obstacles.append((x-w/2-.25,x+w/2+.25,y-d/2-.25,y+d/2+.25))

 def _build_room(self):
  self._box((9.2,9.2,.1),(0,4.5,-.05),(.74,.76,.79,1),texture=self._stone)
  self._box((9.2,9.2,.08),(0,4.5,3.54),(.85,.88,.92,1))
  for x in (-4.55,4.55):
   self._box((.1,9.2,3.5),(x,4.5,1.75),(.78,.82,.88,1))
   self._box((.06,9,.12),(x*.98,4.5,.08),DARK)
  for y in (-.05,9.05):self._box((9,.1,3.5),(0,y,1.75),(.80,.84,.89,1))
  for x in range(-4,5):self._box((.012,9,.002),(x,4.5,.002),(.52,.54,.57,1))
  for y in range(1,9):self._box((9,.012,.002),(0,y,.002),(.52,.54,.57,1))
  for x in (-3.7,0,3.7):
   self._box((.24,7.8,.035),(x,4.5,3.46),DARK)
   self._box((.10,7.6,.04),(x,4.5,3.43),(1,1,1,1))
  for y in (.025,8.975):
   self._box((1.65,.08,2.6),(0,y,1.3),DARK)
   for x in (-.72,.72):self._box((.035,.11,2.35),(x,y,1.3),BLUE)
   self._box((.018,.10,2.25),(0,y,1.3),(.48,.56,.65,1))
   for x in (-.12,.12):self._box((.025,.13,.55),(x,y,1.25),WHITE)
  self._box((3.6,.04,.38),(0,8.90,2.97),DARK)
  self._text('lab.name',(0,8.83,2.93),.18,hpr=(0,0,0))
  # Diagram panels on the side walls, plus readable labels above each category.
  for x in (-4.46,4.46):
   self._box((.03,6.6,.95),(x,4.5,2.52),(1,1,1,1),texture=self._blueprint)
   for y in (1.35,7.65):self._box((.04,.025,.97),(x*.998,y,2.52),BLUE)
  self._text('lab.components',(-4.38,4.5,2.95),.09,hpr=(90,0,0),width=60)
  self._text('lab.guide',(4.38,4.5,2.95),.09,hpr=(-90,0,0),width=60)
  for x in (-4.36,4.36):
   for y in (2.5,4.7,6.85):
    self._box((.07,.70,.05),(x,y,2.35),BLUE)
    self._box((.07,.04,.34),(x,y-.27,2.35),(.35,.67,.85,1))
  # Simplified motherboard/PC diagrams on both wall panels.
  for x in (-4.38,4.38):
   self._box((.03,.65,.58),(x,2.50,2.36),(.16,.31,.43,1))
   self._box((.04,.53,.46),(x*.998,2.50,2.36),(.04,.12,.21,1))
   self._box((.06,.18,.18),(x*.995,2.48,2.40),(.28,.65,.88,1))
   for y in (2.69,2.76):self._box((.065,.035,.30),(x*.995,y,2.37),(.45,.72,.82,1))
   for z in (2.16,2.22):self._box((.065,.30,.025),(x*.995,2.45,z),(.4,.68,.82,1))
  # Potted plants near the rear doors.
  import math
  for x in (-2.1,2.1):
   pot=self.root.attach_new_node(make_cylinder('ceramic_pot',.20,.36,WHITE,24))
   pot.set_pos(x,8.35,.18)
   self._box((.07,.07,.68),(x,8.35,.66),(.12,.28,.16,1))
   for i in range(16):
    angle=i*math.pi*.77
    px=x+math.cos(angle)*.13;py=8.35+math.sin(angle)*.13
    leaf=self._box((.42,.045,.10),(px,py,.60+(i%5)*.09),(.12,.32+(i%3)*.035,.18,1))
    leaf.set_hpr(math.degrees(angle),18+(i%4)*8,12)

 def _build_furniture(self):
  self._cabinet(0,4.65,2.95,1.55)
  # Category cabinets left CPU/RAM/SSD, right GPU/PSU/cooler.
  cats=[('lab.cpu',-3.62,2.5),('lab.ram',-3.62,4.7),('lab.ssd',-3.62,6.85),
        ('lab.gpu',3.62,2.5),('lab.psu',3.62,4.7),('lab.cooler',3.62,6.85)]
  for key,x,y in cats:
   self._cabinet(x,y,1.10,1.80)
   side=-1 if x<0 else 1
   # Raised white back and slanted display wings, matching the reference consoles.
   self._box((.12,1.86,.42),(x+side*.48,y,1.14),WHITE)
   self._box((.055,1.72,.25),(x+side*.40,y,1.40),DARK)
   self._text(key,(x+side*.365,y,1.40),.10,hpr=(90 if x<0 else -90,0,0),width=20)
   for dy in (-.85,.85):
    wing=self._box((1.12,.045,.20),(x,y+dy,1.05),WHITE)
    wing.set_r(side*12)
  self._cabinet(0,7.7,2.7,1.0)
  self._text('lab.motherboard',(0,7.98,1.42),.105)
  # Monitor and keyboard on the right side of the assembly desk.
  self._box((.3,.22,.025),(.67,5.05,.98),DARK)
  self._box((.04,.05,.24),(.67,5.05,1.10),DARK)
  self._box((.86,.055,.50),(.67,5.05,1.39),DARK)
  self._box((.78,.01,.42),(.67,5.013,1.39),(.025,.14,.25,1))
  self._text('lab.monitor',(.67,4.99,1.46),.045,hpr=(0,0,0),width=17)
  self._box((.53,.17,.025),(.67,4.70,.98),DARK)
  for i in range(10):self._box((.025,.12,.004),(.44+i*.047,4.70,.997),(.37,.46,.55,1))
  self._box((.07,.11,.04),(1.07,4.70,.99),DARK)

 def _build_case(self):
  self.case=self.root.attach_new_node('case');self.case.set_pos(*CASE_POS);self.case.set_scale(2.0)
  for size,pos in [((.45,.01,.46),(0,.1,.23)),((.45,.21,.01),(0,0,.005)),
                   ((.45,.21,.01),(0,0,.455)),((.01,.21,.46),(-.22,0,.23)),
                   ((.01,.21,.46),(.22,0,.23))]:self._box(size,pos,(.13,.17,.23,1),self.case)
  for x in (-.20,.20):
   self._box((.006,.006,.42),(x,-.108,.23),BLUE,self.case)
   for z in (.02,.44):self._box((.014,.008,.014),(x,-.11,z),(.62,.65,.70,1),self.case)
  for z in (.06,.10,.14,.18,.22,.26,.30,.34,.38,.42):
   self._box((.008,.12,.003),(-.227,.01,z),(.34,.37,.41,1),self.case)

 def _build_slot(self,i,slot):
  pos,size=SLOT_LAYOUT3D[slot.id]
  # Pick volumes never live under hidden hint geometry.
  anchor=self.case.attach_new_node('socket_'+slot.id);anchor.set_pos(*pos)
  hit=tuple(max(v,.055) for v in size)
  self._slot_pick[slot.id]=self._pick_box(anchor,hit,(0,-.025,0),'slot:'+slot.id)
  glow=self._box(size,(0,-.035,0),GREEN,anchor)
  edge=glow.attach_new_node(wire_box(size));edge.set_light_off()
  glow.set_transparency(TransparencyAttrib.M_alpha);glow.set_color_scale(1,1,1,.36)
  glow.set_depth_write(False);glow.hide();self._slot_ghost[slot.id]=glow
  # Large separated installation pads are an accessible alternative to tiny sockets.
  x=-1.17+i*.39;y=4.02
  pad=self._box((.34,.30,.035),(x,y,.99),(.16,.24,.34,1))
  self._pad_pick[slot.id]=self._pick_box(pad,(.36,.34,.12),(0,0,.035),'pad:'+slot.id)
  self._pad[slot.id]=pad
  self._pad_label[slot.id]=self._text('short.'+slot.id,(x,y-.035,1.12),.054,width=8)
  self._slot_pick[slot.id].set_into_collide_mask(NO_MASK)
  arrow=self._text('play.arrow',(x,y,1.34),.13,width=3)
  arrow.node().set_text_color(*GREEN);arrow.hide();self._arrows[slot.id]=arrow

 def _build_part(self,part):
  model=build_part(part);model.reparent_to(self.root)
  self._part_np[part.id]=model;self._part_kind[part.id]=part.kind
  x,y=DISPLAY[part.id]
  self._tray_pos[part.id]=(x,y)
  plinth=self._box((.65,.55,.09),(x,y,1.00),(.23,.31,.41,1));self._part_plinth[part.id]=plinth
  # One visible hit box over every display plinth, including tiny CPU/RAM models.
  self._part_pick[part.id]=self._pick_box(plinth,(.69,.60,.60),(0,0,.31),'part:'+part.id)
  self._part_label[part.id]=self._text('part.'+part.id,(x,y-.30,1.20),.049,width=15)
  self._to_tray(part.id)

 def _to_tray(self,pid):
  model=self._part_np[pid];model.reparent_to(self.root);model.set_scale(DISPLAY_SCALE[self._parts[pid].kind])
  model.set_hpr(*TRAY_HPR.get(self._parts[pid].kind,DEFAULT_TRAY_HPR))
  # Bounds after rotation and scale: the entire object rests ABOVE the display.
  model.set_pos(0,0,0);bounds=model.get_tight_bounds(self.root)
  x,y=self._tray_pos[pid];model.set_pos(x,y,1.06-bounds[0].z)
  self._part_pick[pid].set_into_collide_mask(PICK_MASK)
  self._part_label[pid].show();self._installed_at.pop(pid,None)

 def _build_check_button(self):
  x,y,z=CHECK_BUTTON_POS
  self._box((.44,.36,.035),(x,y,z-.025),DARK)
  self._check_button=self._box((.36,.28,.065),(x,y,z),GREEN)
  self._pick_box(self._check_button,(.44,.36,.24),(0,0,.07),'button:check')
  self._check_label=self._text('ui.check',(x,y,1.22),.065,width=15)
  self._check_arrow=self._text('play.arrow',(x,y,1.43),.15,width=3)
  self._check_arrow.node().set_text_color(*GREEN)
  self._check_arrow.hide()

 def set_check_ready(self,ready):
  if ready:self._check_arrow.show()
  else:self._check_arrow.hide()

 def show_auto_hint(self,sid,parts):
  for pid,plinth in self._part_plinth.items():
   plinth.set_color_scale(*((.4,1.6,1.0,1) if pid in parts else (1,1,1,1)))

 def configure_level(self,level):
  self.level=level
  for sid in self._slot_ids:
   if level=='medium':
    self._pad[sid].hide();self._pad_label[sid].hide()
    self._pad_pick[sid].set_into_collide_mask(NO_MASK)
    point=self._render.get_relative_point(self.case,Point3(*SLOT_LAYOUT3D[sid][0]))
    self._arrows[sid].set_pos(point.x,point.y-.12,point.z+.15)
   else:
    self._pad[sid].show();self._pad_label[sid].show()
    self._pad_pick[sid].set_into_collide_mask(PICK_MASK)

 def show_held_target(self,sid,valid):
  color=GREEN if valid else RED
  if self._held_id:
   self._preview_np=build_part(self._parts[self._held_id])
   self._preview_np.reparent_to(self.case)
   self._preview_np.set_pos(*SLOT_LAYOUT3D[sid][0])
   self._preview_np.set_color(*color)
   self._preview_np.set_color_scale(1,1,1,.35)
   self._preview_np.set_transparency(TransparencyAttrib.M_alpha)
   self._preview_np.set_depth_write(False)
   self._preview_np.set_light_off()
  self._pad[sid].set_color(*color)
  self._slot_ghost[sid].set_color(*color)
  self._slot_ghost[sid].show()
  if valid:
   self._arrows[sid].node().set_text_color(*GREEN)
   self._arrows[sid].show()


 def _build_picker(self):
  self._trav=CollisionTraverser('lab_picker');self._queue=CollisionHandlerQueue();self._ray=CollisionRay()
  cn=CollisionNode('lab_ray');cn.add_solid(self._ray);cn.set_from_collide_mask(PICK_MASK);cn.set_into_collide_mask(NO_MASK)
  self._ray_np=self.root.attach_new_node(cn);self._trav.add_collider(self._ray_np,self._queue)

 def pick(self,origin,direction,max_dist=3,preferred_slot=None):
  o=self.root.get_relative_point(self._render,origin);self._ray.set_origin(o)
  self._ray.set_direction(self.root.get_relative_vector(self._render,direction))
  self._queue.clear_entries();self._trav.traverse(self.root);self._queue.sort_entries()
  hits=[]
  for i in range(self._queue.get_num_entries()):
   e=self._queue.get_entry(i)
   if (e.get_surface_point(self.root)-o).length()<=max_dist:
    hits.append(e.get_into_node_path().get_net_tag('pick'))
  # Pads remain unambiguous; overlapping real sockets prefer the held part's socket.
  if hits and hits[0].startswith('pad:'):return 'slot:'+hits[0][4:]
  if preferred_slot and 'slot:'+preferred_slot in hits:return 'slot:'+preferred_slot
  return ('slot:'+hits[0][4:] if hits[0].startswith('pad:') else hits[0]) if hits else None

 def pickup(self,pid,hold_pos,heading):
  self._held_id=pid
  self._part_np[pid].reparent_to(self.root);self._part_np[pid].set_scale(1.5)
  self._part_pick[pid].set_into_collide_mask(NO_MASK);self._part_label[pid].hide()
  self._installed_at.pop(pid,None);self.update_held(pid,hold_pos,heading)

 def update_held(self,pid,hold_pos,heading):
  np=self._part_np[pid];np.set_pos(hold_pos)
  h,p,r=HOLD_HPR.get(self._parts[pid].kind,(0,0,0));np.set_hpr(heading+h,p,r)

 def set_targets(self,state,level,verdicts=None,hover=None):
  if self._preview_np is not None:self._preview_np.remove_node();self._preview_np=None
  verdicts=verdicts or {}
  for sid in self._slot_ids:
   occupied=state.part_in(sid) is not None
   color=(.12,.45,.30,1) if occupied else (.16,.24,.34,1)
   show=False
   if state.selected is not None:
    self._slot_pick[sid].set_into_collide_mask(NO_MASK if occupied else PICK_MASK)
    if level=='easy':
     valid=verdicts[sid].ok
     color=GREEN if valid else RED
     show=not occupied and valid
   else:self._slot_pick[sid].set_into_collide_mask(PICK_MASK if level=='medium' and occupied else NO_MASK)
   self._pad[sid].set_color(*color)
   if level=='easy' and state.selected and verdicts[sid].ok:self._arrows[sid].show()
   else:self._arrows[sid].hide()
   glow=self._slot_ghost[sid]
   if show:glow.show()
   else:glow.hide()
  if hover and hover.startswith('slot:') and level=='easy' and state.selected:
   sid=hover[5:];self._pad[sid].set_color(*(GREEN if verdicts[sid].ok else RED))

 def install(self,pid,sid):
  self._held_id=None
  model=self._part_np[pid];model.reparent_to(self.case);model.set_scale(1)
  model.set_pos(*SLOT_LAYOUT3D[sid][0]);model.set_hpr(0,0,0)
  self._part_pick[pid].set_into_collide_mask(NO_MASK);self._part_label[pid].hide();self._installed_at[pid]=sid

 def drop_to_table(self,pid):
  self._held_id=None
  self._to_tray(pid)
 def reset_visuals(self):
  self._held_id=None
  for pid in self._part_np:self._to_tray(pid)
  for glow in self._slot_ghost.values():glow.hide()
 def set_translator(self,translator):
  self._t=translator
  for tn,key in self._labels:tn.set_text(self._t(key))
 def destroy(self):self._trav.clear_colliders();self.root.remove_node()
