"""Desktop room module. Local draft API; no shared-system changes."""
from time import monotonic
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectWaitBar
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Filename, TextNode
from .data import SLOTS,RULES
from .logic import AssemblyState,Code
from .difficulty import available_parts,initial_parts
from .scene3d import RoomScene3D,GREEN,RED
from .strings import make_translator
from .hints import next_hint,preview_part
from .round_sequence import RoundSequence

REACH=3.0
ORDER=('motherboard','cpu','ram','storage','cooler','gpu','psu')

class PCAssemblyRoom3D(DirectObject):
 def __init__(self,base,pointer,translator=None,font_path=None,on_complete=None,enhanced=False,difficulty='easy',round_sequence=None):
  super().__init__()
  self.base=base;self._pointer=pointer;self._t=translator or make_translator('en')
  self._font_path=font_path;self._font=None;self._on_complete=on_complete
  self._round_sequence=round_sequence if round_sequence is not None else RoundSequence()
  self.round_target=None
  self.difficulty=difficulty;self._parts=available_parts(difficulty);self._enhanced=enhanced
  self._entered=False;self.scene=None;self.state=None;self._task=None
  self._ui={};self._panels=[];self._completed=False;self._carried=None
  self._elapsed=0;self._timer_text=None;self._hover_key=None;self._verdicts={}
  self._hint_slot=None;self._hint_parts=()

 def enter(self,parent):
  if self._entered:return
  if self._font_path:self._font=self.base.loader.load_font(Filename.from_os_specific(self._font_path))
  self.state=AssemblyState(self._parts,SLOTS,RULES)
  self.scene=RoomScene3D(parent,self.base.render,self._parts,SLOTS,self._t,self._font,self._enhanced)
  self.scene.configure_level(self.difficulty)
  self._entered=True;self._completed=False;self._carried=None
  for a,b in ((.82,1),(-1,-.65)):
   self._panels.append(DirectFrame(parent=self.base.aspect2d,frameColor=(.025,.05,.09,.93),frameSize=(-2.5,2.5,a,b)))
  kw=dict(parent=self.base.aspect2d,fg=(.94,.97,1,1),font=self._font,mayChange=True,align=TextNode.A_center,wordwrap=65)
  positions={'hint':(.967,.028),'status':(.916,.032),'progress':(.855,.032),
             'hover':(-.855,.032),'held':(-.913,.029),'timer':(-.97,.029)}
  for key,(y,scale) in positions.items():self._ui[key]=OnscreenText(text='',pos=(0,y),scale=scale,**kw)
  self._hint_panel=DirectFrame(parent=self.base.aspect2d,frameColor=(.025,.07,.11,.95),frameSize=(-1.4,1.4,-1,-.65))
  self._hint_panel.hide()
  self._ui['step_list']=OnscreenText(text='',pos=(0,.65),scale=.032,**kw)
  self._ui['hint_detail']=OnscreenText(text='',pos=(0,-.709),scale=.033,**kw)
  self._ui['hint_help']=OnscreenText(text='',pos=(0,-.71),scale=.031,**kw)
  self._ui['cross']=OnscreenText(text='+',pos=(0,-.012),scale=.065,**kw)
  self._ui['hint'].setText(self._t('ui.hint_walk'))
  self._ui['counter']=OnscreenText(text='',pos=(1.10,.93),scale=.062,**kw)
  self._progress_bar=DirectWaitBar(parent=self.base.aspect2d,range=7,value=0,
      pos=(1.10,0,.86),scale=.32,barColor=(.08,.90,.45,1),
      frameColor=(.12,.20,.28,1),frameSize=(-1,1,-.06,.06))
  self._prepare_round()
  self.accept(self._pointer.activate_event,self._on_click)
  if getattr(self._pointer,'cancel_event',None):self.accept(self._pointer.cancel_event,self._on_cancel)
  self._task=self.base.task_mgr.add(self._update,'pc_lab_update_'+str(id(self)))

 def exit(self):
  if not self._entered:return
  self.ignore_all()
  if self._task is not None:self._task.remove();self._task=None
  for ui in self._ui.values():ui.destroy()
  for panel in self._panels:panel.destroy()
  self._progress_bar.destroy()
  self._hint_panel.destroy()
  self._panels=[];self._ui={};self.scene.destroy();self.scene=None;self.state=None
  self._carried=None;self._entered=False

 def reset(self):
  if not self._entered:return
  self.state.reset();self.scene.reset_visuals();self._prepare_round()

 def _prepare_round(self):
  self.round_target=self._round_sequence.next_target() if self.difficulty=='medium' else None
  required=self.round_target.required_parts if self.round_target else {}
  self.state=AssemblyState(self._parts,SLOTS,RULES,required_parts=required)
  self._completed=False;self._carried=None;self._elapsed=0;self._hover_key=None;self._timer_text=None
  self._hint_slot=None;self._hint_parts=()
  self._hint_panel.hide();self._ui['hint_detail'].setText('')
  for sid,pid in initial_parts(self.difficulty):
   self.state.select(pid);result=self.state.place(sid)
   if not result.ok:raise RuntimeError('Invalid initial parts')
   self.scene.install(pid,sid)
  self._started=monotonic()
  self._ui['status'].setFg((.94,.97,1,1))
  self._ui['status'].setText(self._t('play.goal'))
  self._ui['hover'].setText('');self._ui['cross'].setFg((1,1,1,1))
  self._refresh()

 @property
 def mistakes(self):return self.state.mistakes if self.state else 0

 def _preferred_slot(self):
  if self._carried is None:return None
  kind=next(p.kind for p in self._parts if p.id==self._carried)
  return next(s.id for s in SLOTS if s.kind==kind)

 def _current_key(self):
  origin,direction=self._pointer.get_ray()
  return self.scene.pick(origin,direction,REACH,self._preferred_slot())

 def _refresh(self):
  self._verdicts={s.id:self.state.preview_place(s.id) for s in SLOTS} if self._carried else {}
  self.scene.set_targets(self.state,self.difficulty,self._verdicts,self._hover_key)
  if self.difficulty=='medium' and not self._completed:
   self._update_hint_content()
   self._hint_panel.hide()
   self.scene.show_auto_hint(self._hint_slot,self._hint_parts)
   if self._carried:
    sid=self._preferred_slot()
    self.scene.show_held_target(sid,self._verdicts[sid].ok)
  else:
   self._hint_panel.hide();self._ui['hint_detail'].setText('')
  self._progress();self._timer_text=None
  if self._carried:
   self._ui['held'].setText(self._t('play.held',part=self._t('part.'+self._carried)))
  else:self._ui['held'].setText(self._t('play.empty_hands'))
  self._hover_key=None

 def _progress(self):
  text=self._t('ui.progress',n=len(self.state.installed),level=self._t('level.'+self.difficulty))
  if self.round_target:text+=' | '+self._t('round.target',build=self._t('round.'+self.round_target.id))
  if self.difficulty=='easy' and not self._completed:
   sid=next((sid for sid in ORDER if self.state.part_in(sid) is None),None)
   text+=' | '+(self._t('ui.next',slot=self._t('slot.'+sid)) if sid else self._t('play.press_check'))
   for pid,plinth in self.scene._part_plinth.items():
    kind=next(p.kind for p in self._parts if p.id==pid)
    wanted=next(s.kind for s in SLOTS if s.id==sid) if sid else None
    plinth.set_color_scale(*( (.4,1.6,1.0,1) if kind==wanted and pid not in self.scene._installed_at else (1,1,1,1)))
  self._ui['step_list'].setText('')
  self._ui['hint_help'].setText('')
  if self.difficulty=='medium' and self._hint_slot:
   text+=' | '+self._t('ui.next',slot=self._t('slot.'+self._hint_slot))
  self._ui['progress'].setText(text)
  n=len(self.state.installed)
  self._ui['counter'].setText(self._t('play.counter',n=n))
  self._progress_bar['value']=n
  ready=self.state.check().complete
  self.scene.set_check_ready(ready and not self._completed)
  if ready and not self._completed:
   self._ui['status'].setText(self._t('play.ready_check'))
   self._ui['status'].setFg(GREEN)

 def _result_text(self,result,ok_key='msg.ok_place'):
  kw={}
  if result.part:kw['part']=self._t('part.'+result.part)
  if result.slot:kw['slot']=self._t('slot.'+result.slot)
  if result.code is Code.WRONG_BUILD and self.round_target:
   kw['expected']=self._t('part.'+self.round_target.required_parts[result.slot])
  return self._t(ok_key if result.ok else 'msg.'+result.code.value,**kw)

 def _update(self,task):
  if not self._completed:self._elapsed=monotonic()-self._started
  stamp=int(self._elapsed)
  if stamp!=self._timer_text:
   self._timer_text=stamp
   self._ui['timer'].setText(self._t('ui.time',minutes=stamp//60,seconds=stamp%60)+' | '+self._t('ui.mistakes',n=self.mistakes))
  if self._carried:
   pos,heading=self._pointer.get_hold_pose();self.scene.update_held(self._carried,pos,heading)
  key=self._current_key()
  if key!=self._hover_key:
   self._hover_key=key;self._ui['cross'].setFg((1,1,1,1))
   text=self._t('medium.aim' if self.difficulty=='medium' else 'play.aim') if self._carried else self._t('play.pick_hint')
   if key:
    kind,ident=key.split(':',1)
    if kind=='part':
     text=self._t('part.'+ident)+' | '+self._t('play.click_pick')
     if self.difficulty=='medium' and not self._carried:
      result=preview_part(self.state,ident,self._parts)
      text+=' | '+(self._t('auto.compatible') if result.ok else self._result_text(result))
      self._ui['cross'].setFg(GREEN if result.ok else RED)
    elif kind=='slot':
     text=self._t('ui.hover_place',slot=self._t('slot.'+ident))
     if self._carried and (self.difficulty=='easy' or self._hint_slot is not None):
      result=self._verdicts[ident];self._ui['cross'].setFg(GREEN if result.ok else RED)
      text=self._t('play.valid') if result.ok else self._result_text(result)
      text+=' | '+self._t('short.'+ident)
     elif not self._carried and self.state.part_in(ident):text+=' | '+self._t('play.click_remove')
    elif kind=='button':text=self._t('ui.check')+' | '+self._t('play.click')
   if self._completed:text=self._t('play.finished')
   self._ui['hover'].setText(text)
  return task.cont

 def _on_click(self):
  if self._completed:return
  key=self._current_key()
  if not key:
   self._ui['status'].setText(self._t('play.move_closer'));return
  kind,ident=key.split(':',1)
  if kind=='button':self._click_check()
  elif self._carried:
   if kind=='slot':self._place(ident)
   else:self._ui['status'].setText(self._t('msg.hands_full'))
  elif kind=='part':self._pickup(ident)
  elif kind=='slot':
   pid=self.state.part_in(ident)
   if pid:self._pickup(pid)
   else:self._ui['status'].setText(self._t('play.pick_hint'))

 def _pickup(self,pid):
  sid=self.state.slot_of(pid)
  if (sid,pid) in initial_parts(self.difficulty):
   self._ui['status'].setText(self._t('msg.preinstalled'));return
  if sid:
   result=self.state.remove(sid)
   if not result.ok:self._ui['status'].setText(self._result_text(result));return
  result=self.state.select(pid)
  if not result.ok:self._ui['status'].setText(self._result_text(result));return
  self._carried=pid;pos,heading=self._pointer.get_hold_pose();self.scene.pickup(pid,pos,heading)
  self._ui['status'].setText(self._t('play.carry_easy') if self.difficulty=='easy' else self._t('play.carry'))
  self._refresh()

 def _place(self,sid):
  result=self.state.place(sid)
  if result.ok:
   self.scene.install(result.part,sid);self._carried=None
   if sid==self._hint_slot:
    self._hint_slot=None;self._hint_parts=()
    self._hint_panel.hide();self._ui['hint_detail'].setText('')
  self._ui['status'].setText(self._result_text(result));self._ui['status'].setFg(GREEN if result.ok else RED)
  self._refresh()

 def _on_cancel(self):
  if self._carried is None:return
  self.scene.drop_to_table(self._carried);self.state.deselect();self._carried=None
  self._ui['status'].setText(self._t('msg.returned'));self._refresh()

 def _update_hint_content(self):
  sid,parts=next_hint(self.state,self._parts)
  self._hint_slot=sid;self._hint_parts=parts
  board=self.state.part_in('motherboard')
  if board:
   values=next(p.specs for p in self._parts if p.id==board)
   specs=values.get('socket','')+' / '+values.get('ram_type','')
  else:specs=self._t('part.'+self.round_target.motherboard) if self.round_target else self._t('auto.no_board')
  if sid is None:
   detail=self._t('play.ready_check')
  elif parts:
   detail=self._t('auto.detail',board=specs,slot=self._t('slot.'+sid),part=self._t('part.'+parts[0]))
  else:
   detail=self._t('hint.unavailable',slot=self._t('slot.'+sid))
  if self._carried:
   result=self._verdicts[self._preferred_slot()]
   if not result.ok:detail=self._result_text(result)+'\n'+self._t('auto.return_part')
  self._ui['hint_detail'].setText(detail)

 def _click_check(self):
  if self._completed:return
  result=self.state.check()
  if result.complete:
   self._elapsed=monotonic()-self._started;self._completed=True
   self._ui['status'].setText(self._t('msg.check_complete'));self._ui['status'].setFg(GREEN)
   self._refresh()
   if self._on_complete:self._on_complete({'mistakes':self.mistakes,'elapsed_seconds':self._elapsed,'difficulty':self.difficulty})
  else:self._ui['status'].setText(self._t('msg.check_incomplete',n=len(result.missing)+len(result.conflicts)))

 def set_translator(self,translator):
  self._t=translator
  if self._entered:
   self.scene.set_translator(translator);self._ui['hint'].setText(self._t('ui.hint_walk'));self._refresh()

