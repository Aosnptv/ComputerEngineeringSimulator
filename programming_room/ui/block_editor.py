"""Block editor: click to add; drag a listed block to reorder it."""

from direct.gui.DirectGui import DirectButton, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
try:
    from ..config import COMMANDS, MAX_COMMANDS
except ImportError:
    from config import COMMANDS, MAX_COMMANDS


class BlockEditor:
    def __init__(self, parent, on_change=None):
        self.parent = parent
        self.on_change = on_change
        self.commands = []
        self.widgets = []
        self.item_widgets = []
        self.offset = 0
        self.drag_index = None
        self.app = parent.getPythonTag("app")
        self.create_interface()

    def button(self, text, x, z, color, callback):
        widget = DirectButton(
            parent=self.parent, text=text, pos=(x, 0, z),
            scale=0.046, frameColor=color, text_fg=(0.12, 0.23, 0.4, 1),
            command=callback,
        )
        self.widgets.append(widget)
        return widget

    def create_interface(self):
        title = DirectLabel(
            parent=self.parent, text="PROGRAMMING", pos=(0, 0, 0.49),
            scale=0.058, frameColor=(0, 0, 0, 0),
            text_fg=(0.15, 0.26, 0.43, 1),
        )
        self.widgets.append(title)
        for i, cmd in enumerate(COMMANDS):
            x = -0.145 if i % 2 == 0 else 0.145
            z = 0.34 - 0.115 * (i // 2)
            caption = "+ " + cmd.replace("_", " ")
            widget = DirectButton(
                parent=self.parent,
                text=caption,
                pos=(x, 0, z), scale=0.032,
                frameSize=(-4.15, 4.15, -0.65, 0.65),
                frameColor=(0.72, 0.86, 1, 1) if i < 3 else (0.79, 0.72, 0.98, 1),
                text_fg=(0.12, 0.23, 0.4, 1),
                command=lambda c=cmd: self.add_command(c),
            )
            self.widgets.append(widget)

        hint = DirectLabel(
            parent=self.parent, text="IF: BLOCKED? | ELSE: CLEAR PATH",
            pos=(0, 0, -0.055), scale=0.028,
            frameColor=(0, 0, 0, 0), text_fg=(0.25, 0.35, 0.52, 1),
        )
        self.widgets.append(hint)

        self.button("<", -0.17, -0.63, (0.8, 0.87, 1, 1), self.previous_page)
        self.button(">", 0.17, -0.63, (0.8, 0.87, 1, 1), self.next_page)
        self.button("UNDO", -0.13, -0.70, (1, 0.79, 0.54, 1), self.undo)
        self.button("CLEAR", 0.14, -0.70, (1, 0.63, 0.67, 1), self.clear)
        self.refresh()

    def add_command(self, command):
        if command not in COMMANDS or len(self.commands) >= MAX_COMMANDS:
            return
        self.commands.append(command)
        self.offset = max(0, len(self.commands) - 7)
        self.refresh()

    def undo(self):
        if self.commands:
            self.commands.pop()
        self.offset = min(self.offset, max(0, len(self.commands) - 7))
        self.refresh()

    def clear(self):
        self.commands.clear()
        self.offset = 0
        self.refresh()

    def previous_page(self):
        self.offset = max(0, self.offset - 7)
        self.refresh()

    def next_page(self):
        self.offset = min(max(0, len(self.commands) - 7), self.offset + 7)
        self.refresh()

    def get_commands(self):
        return list(self.commands)

    def start_drag(self, index, event=None):
        self.drag_index = index

    def finish_drag(self):
        if self.drag_index is None or not self.app.mouseWatcherNode.hasMouse():
            self.drag_index = None
            return
        mouse_y = self.app.mouseWatcherNode.getMouse().getY()
        local_y = mouse_y - self.parent.getZ()
        slot = round((-0.17 - local_y) / 0.057)
        target = max(0, min(len(self.commands) - 1, self.offset + slot))
        source = self.drag_index
        self.drag_index = None
        if target != source:
            moved = self.commands.pop(source)
            self.commands.insert(target, moved)
            self.refresh()

    def refresh(self):
        for item in self.item_widgets:
            item.destroy()
        self.item_widgets.clear()
        if not self.commands:
            empty = DirectLabel(
                parent=self.parent, text="YOUR PROGRAM: (EMPTY)",
                pos=(0, 0, -0.20), scale=0.030,
                frameColor=(0, 0, 0, 0),
                text_fg=(0.45, 0.42, 0.52, 1),
            )
            self.item_widgets.append(empty)
        for row, index in enumerate(range(self.offset, min(len(self.commands), self.offset + 7))):
            button = DirectButton(
                parent=self.parent, text=f"{index + 1}. {self.commands[index].replace('_', ' ')}",
                pos=(0, 0, -0.17 - row * 0.057),
                scale=0.029, frameColor=(0.82, 0.92, 1.0, 1),
                text_fg=(0.12, 0.23, 0.4, 1),
            )
            button.bind(DGG.B1PRESS, self.start_drag, [index])
            self.item_widgets.append(button)
        if self.on_change:
            self.on_change()

    def destroy(self):
        for widget in self.item_widgets + self.widgets:
            widget.destroy()
