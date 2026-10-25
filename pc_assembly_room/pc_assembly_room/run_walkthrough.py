"""Standalone tester. Team Hub/control/score integration remains a draft.
Run: python -m pc_assembly_room.run_walkthrough --lang th --difficulty easy
Add --menu to open the local difficulty menu first.
"""
import argparse
from panda3d.core import loadPrcFileData,WindowProperties,Filename
from .room3d import PCAssemblyRoom3D
from .walk import FirstPersonController,FirstPersonPointer
from .scene3d import START_POS
from .strings import make_translator
from .session_ui import ResultPanel,MainMenu
from .round_sequence import RoundSequence

class WalkthroughSession:
    def __init__(self,app,translator,font_path=None,controller_factory=FirstPersonController):
        self.app=app;self.t=translator;self.font_path=font_path
        self.font=app.loader.load_font(Filename.from_os_specific(font_path)) if font_path else None
        self._medium_rounds=RoundSequence()
        self.controller_factory=controller_factory
        self.room=None;self.walker=None;self.panel=None;self.level='easy'
        app.accept('r',self.replay)
        app.accept('escape',self.quit)

    def _cursor(self,visible):
        if self.app.win and hasattr(self.app.win,'request_properties'):
            props=WindowProperties();props.set_cursor_hidden(not visible)
            self.app.win.request_properties(props)

    def _close_panel(self):
        if self.panel:self.panel.destroy();self.panel=None

    def _close_room(self):
        if self.walker:self.walker.destroy();self.walker=None
        if self.room:self.room.exit();self.room=None

    def start(self,level):
        self._close_panel();self._close_room();self.level=level
        self.room=PCAssemblyRoom3D(self.app,FirstPersonPointer(self.app),translator=self.t,
            font_path=self.font_path,on_complete=self.complete,difficulty=level,round_sequence=self._medium_rounds)
        self.room.enter(self.app.render)
        self.walker=self.controller_factory(self.app,start=START_POS,heading=0,
            bounds=self.room.scene.walk_bounds,obstacles=self.room.scene.walk_obstacles)
        self._cursor(False)

    def complete(self,result):
        if self.panel:return
        if self.walker:self.walker.set_enabled(False)
        self._cursor(True)
        self.panel=ResultPanel(self.app,self.t,self.font,result,self.replay,self.show_menu)

    def replay(self):
        if self.room:self.start(self.level)

    def show_menu(self):
        self._close_panel();self._close_room();self._cursor(True)
        self.panel=MainMenu(self.app,self.t,self.font,self.start,self.quit)

    def destroy(self):
        self._close_panel();self._close_room()
        self.app.ignore('r');self.app.ignore('escape');self._cursor(True)

    def quit(self):
        self.destroy();self.app.userExit()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--lang',choices=['th','en'],default='en')
    parser.add_argument('--font',default=None)
    parser.add_argument('--difficulty',choices=['easy','medium'],default='easy')
    parser.add_argument('--menu',action='store_true')
    parser.add_argument('--enhanced',action='store_true',help='Legacy option; this scene uses its standard low-poly palette.')
    args=parser.parse_args()
    loadPrcFileData('','window-title PC Assembly Room\nwin-size 1280 720')
    from direct.showbase.ShowBase import ShowBase
    from .font_support import resolve_font
    app=ShowBase();app.disable_mouse()
    font_path=resolve_font(app.loader,args.font)
    if args.lang=='th' and font_path is None:
        print('Thai font unavailable: using English for this standalone test.')
        args.lang='en'
    app.camLens.set_fov(75);app.camLens.set_near_far(.05,50)
    session=WalkthroughSession(app,make_translator(args.lang),font_path)
    if args.menu:session.show_menu()
    else:session.start(args.difficulty)
    app.run()

if __name__=='__main__':main()
