from pathlib import Path

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel


def ui_font(loader):
    """Load a font with Thai glyphs when it is available on the host."""
    font_file = Path("C:/Windows/Fonts/tahoma.ttf")
    if font_file.exists():
        try:
            font = loader.loadFont("/c/Windows/Fonts/tahoma.ttf")
            if font.getNumPages() == 0:
                font.setPixelSize(96)
                font.setPixelsPerUnit(96)
                font.setPageSize(1024, 1024)
            return font
        except OSError:
            pass
    return None


class IntroScreen:
    def __init__(self, app, on_done, font):
        self.app = app
        self.on_done = on_done
        self.finished = False
        self.frame = DirectFrame(
            frameSize=(-2, 2, -1, 1),
            frameColor=(0.018, 0.05, 0.1, 1),
        )
        for x in (-1.55, 1.55):
            DirectFrame(parent=self.frame, pos=(x, 0, 0),
                        frameSize=(-0.008, 0.008, -0.65, 0.65),
                        frameColor=(0.06, 0.37, 0.52, 1))
        DirectFrame(
            parent=self.frame,
            frameSize=(-0.54, 0.54, -0.44, 0.44),
            frameColor=(0.09, 0.73, 0.86, 1),
            pos=(0, 0, 0.22),
        )
        DirectFrame(
            parent=self.frame,
            frameSize=(-0.52, 0.52, -0.42, 0.42),
            frameColor=(0.03, 0.13, 0.24, 1),
            pos=(0, 0, 0.22),
        )
        DirectLabel(
            parent=self.frame,
            text="CPE",
            text_font=font,
            text_fg=(0.78, 0.97, 1, 1),
            text_shadow=(0, 0.04, 0.1, 1),
            scale=0.31,
            pos=(0, 0, 0.1),
            frameColor=(0, 0, 0, 0),
        )
        DirectLabel(
            parent=self.frame,
            text="COMPUTER ENGINEERING LAB",
            text_font=font,
            text_fg=(0.9, 0.97, 1, 1),
            scale=0.085,
            pos=(0, 0, -0.45),
            frameColor=(0, 0, 0, 0),
        )
        DirectLabel(
            parent=self.frame,
            text="EXPLORE  /  LEARN  /  BUILD",
            text_font=font,
            text_fg=(0.45, 0.77, 0.85, 1),
            scale=0.046,
            pos=(0, 0, -0.56),
            frameColor=(0, 0, 0, 0),
        )
        DirectButton(
            parent=self.frame,
            text="SKIP  >",
            text_font=font,
            scale=0.065,
            pos=(1.46, 0, -0.84),
            frameSize=(-1.8, 1.8, -0.6, 0.8),
            frameColor=(0.07, 0.47, 0.64, 1),
            text_fg=(1, 1, 1, 1),
            command=self.finish,
        )
        self.app.taskMgr.doMethodLater(3.5, self._auto_finish, "intro_finish")

    def _auto_finish(self, task):
        self.finish()
        return task.done

    def finish(self):
        if self.finished:
            return
        self.finished = True
        self.app.taskMgr.remove("intro_finish")
        self.frame.destroy()
        self.on_done()


class LanguageScreen:
    def __init__(self, app, on_select, font):
        self.on_select = on_select
        self.frame = DirectFrame(
            frameSize=(-2, 2, -1, 1),
            frameColor=(0.018, 0.05, 0.1, 1),
        )
        DirectFrame(parent=self.frame, pos=(0, 0, -0.02),
                    frameSize=(-1.16, 1.16, -0.55, 0.6),
                    frameColor=(0.035, 0.11, 0.21, 1))
        DirectFrame(parent=self.frame, pos=(0, 0, 0.56),
                    frameSize=(-1.12, 1.12, -0.006, 0.006),
                    frameColor=(0.08, 0.75, 0.88, 1))
        DirectLabel(
            parent=self.frame,
            text="Choose your language / เลือกภาษา",
            text_font=font,
            text_fg=(0.93, 0.98, 1, 1),
            scale=0.078,
            pos=(0, 0, 0.36),
            frameColor=(0, 0, 0, 0),
        )
        DirectLabel(parent=self.frame, text="SELECT YOUR EXPERIENCE",
                    text_font=font, scale=0.039,
                    pos=(0, 0, 0.22),
                    text_fg=(0.46, 0.76, 0.86, 1),
                    frameColor=(0, 0, 0, 0))
        for language, label, x in (
            ("th", "ภาษาไทย", -0.52),
            ("en", "English", 0.52),
        ):
            DirectButton(
                parent=self.frame,
                text=label,
                text_font=font,
                text_fg=(0.92, 0.98, 1, 1),
                scale=0.095,
                pos=(x, 0, -0.12),
                frameSize=(-4, 4, -0.75, 0.9),
                frameColor=(0.08, 0.39, 0.56, 1),
                command=self.select,
                extraArgs=[language],
            )

    def select(self, language):
        self.frame.destroy()
        self.on_select(language)
