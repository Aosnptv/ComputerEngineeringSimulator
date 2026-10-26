"""
Programming Lab V8.1
Interactive Programming Screen
"""

from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton,
    DirectEntry,
)
from direct.gui import DirectGuiGlobals as DGG

try:
    from ..core.lessons import COMMANDS, LESSONS, check_answer
    from ..core.code_runner import COMMAND_EXAMPLES, validate_single_code
    from ..core.scoring import Attempt
    from ..core.activity_session import ActivitySession
    from ..ui.text_layout import fitted_scale
except ImportError:
    from core.lessons import COMMANDS, LESSONS, check_answer
    from core.code_runner import COMMAND_EXAMPLES, validate_single_code
    from core.scoring import Attempt
    from core.activity_session import ActivitySession
    from ui.text_layout import fitted_scale


class VRProgrammingPanel:

    BG = (0.88, 0.94, 1.0, 1)
    TEXT = (0.12, 0.24, 0.43, 1)

    BLUE = (0.67, 0.82, 1.0, 1)
    PURPLE = (0.78, 0.71, 1.0, 1)
    PINK = (1.0, 0.74, 0.84, 1)
    GREEN = (0.60, 0.90, 0.73, 1)
    ORANGE = (1.0, 0.83, 0.60, 1)

    def __init__(self, app):
        self.app = app

        self.active = False
        self.category = None
        self.index = 0

        self.used = []
        self.choice = None
        self.solved = False
        self.feedback = ""
        self.difficulty = "Easy"
        self.language = "Python"
        self.input_mode = "BLOCK"
        self.attempt = Attempt()
        self.last_stars = 0
        self.code_draft = ""
        self.activity_session = None
        self.last_correct = False
        self.advance_task_name = "activity_advance_" + str(id(self))

        # Scores for the three programming activities
        self.category_scores = {
            "arrange": 0,
            "debug": 0,
            "fill": 0,
        }

        self.widgets = []

        self.root = DirectFrame(
            parent=app.aspect2d,
            frameSize=(-1.20, 1.20, -0.75, 0.75),
            frameColor=self.BG,
            relief=DGG.RAISED,
        )
        self.root.hide()

        app.accept("backspace", self.close)

    # ==================================================
    # SCORES
    # ==================================================

    @property
    def score(self):
        return sum(self.category_scores.values())

    def robot_score(self):
        return sum(self.app.mission_scores.values())

    def total_score(self):
        return self.score + self.robot_score()

    # ==================================================
    # OPEN / CLOSE
    # ==================================================

    def open(self):
        if self.active:
            return

        self.app.stop_animation()
        self.app.hide_overlay()
        self.app.classroom.disable()

        # Hide classroom while using the screen
        self.app.room.hide()
        self.app.mission_scene.hide()
        self.app.mission_ui.hide()
        self.app.puzzle_ui.hide()
        self.app.demo_button.hide()
        self.app.score_label.hide()
        self.app.room_button.hide()
        self.app.mission_button.hide()
        self.app.status_label.hide()

        self.app.current_scene = "computer"

        self.active = True
        self.root.show()
        self.menu()

    def close(self, silent=False):
        if not self.active:
            return

        self.active = False
        self.app.taskMgr.remove(self.advance_task_name)
        self.root.hide()

        if not silent:
            self.app.show_room()

    # ==================================================
    # UI HELPERS
    # ==================================================

    def clear(self):
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def label(self, text, x, z, scale=0.05, color=None, max_width=1.85):
        if color is None:
            color = self.TEXT

        scale = fitted_scale(text, scale, max_width)

        widget = DirectLabel(
            parent=self.root,
            text=text,
            pos=(x, 0, z),
            scale=scale,
            frameColor=(0, 0, 0, 0),
            text_fg=color,
        )
        self.widgets.append(widget)
        return widget

    def button(
        self,
        text,
        x,
        z,
        callback,
        color=None,
        width=0.75,
        height=0.075,
        scale=0.05
    ):
        if color is None:
            color = self.BLUE

        scale = fitted_scale(text, scale, width * 1.55, min_scale=0.028)

        widget = DirectButton(
            parent=self.root,
            text=text,
            pos=(x, 0, z),
            scale=scale,
            frameSize=(
                -width / scale,
                width / scale,
                -height / scale,
                height / scale
            ),
            frameColor=color,
            text_fg=self.TEXT,
            relief=DGG.RAISED,
            command=callback,
        )

        def hover(event, btn=widget, base=color):
            btn["frameColor"] = (
                min(1.0, base[0] + 0.12),
                min(1.0, base[1] + 0.12),
                min(1.0, base[2] + 0.10),
                1
            )

        def leave(event, btn=widget, base=color):
            btn["frameColor"] = base

        widget.bind(DGG.ENTER, hover)
        widget.bind(DGG.EXIT, leave)

        self.widgets.append(widget)
        return widget

    def base(self, title):
        self.clear()

        # Keep the title below the white bevel instead of touching its edge.
        self.label(title, 0, 0.53, 0.066, max_width=1.65)

        self.label(
            "PROGRAMMING LAB V8.1",
            0, 0.43, 0.034
        )

    # ==================================================
    # ACTIVITY MENU
    # ==================================================

    def menu(self):
        self.app.taskMgr.remove(self.advance_task_name)
        self.category = None
        self.base("PROGRAMMING LAB")

        self.button(
            "LEVEL: " + self.difficulty, -0.60, 0.33,
            self.cycle_difficulty, self.PURPLE,
            width=0.26, height=0.034, scale=0.034
        )
        self.button(
            "LANG: " + self.language, 0.62, 0.33,
            self.cycle_language, self.GREEN,
            width=0.25, height=0.034, scale=0.034
        )

        activities = (
            ("ARRANGE BLOCKS", "arrange", self.PURPLE, 0.17),
            ("FIND THE BUG", "debug", self.PINK, 0.00),
            ("FILL MISSING BLOCK", "fill", self.GREEN, -0.17),
        )

        for title, category, color, z in activities:
            self.button(
                title,
                -0.34,
                z,
                lambda c=category: self.start(c),
                color,
                width=0.47
            )

            self.label(
                f"{self.category_scores[category]} pts",
                0.69,
                z,
                0.044
            )

        self.button(
            "ROBOT MISSION",
            -0.34,
            -0.34,
            self.app.show_level_select,
            self.ORANGE,
            width=0.47
        )

        self.label(
            f"{self.robot_score()} pts",
            0.69,
            -0.34,
            0.044
        )

        self.label(
            f"TOTAL SCORE: {self.total_score()}",
            0,
            -0.49,
            0.061,
            (0.08, 0.50, 0.30, 1)
        )

        self.button(
            "EXIT TO CLASSROOM",
            0,
            -0.65,
            self.close,
            self.BLUE,
            width=0.55,
            height=0.055,
            scale=0.041
        )

    # ==================================================
    # EXERCISE STATE
    # ==================================================

    def reset_answer(self):
        self.used = []
        self.choice = None
        self.solved = False
        self.feedback = ""
        self.last_stars = 0
        self.attempt.reset()
        self.code_draft = ""
        self.last_correct = False

    def cycle_difficulty(self):
        choices = ("Easy", "Medium", "Hard")
        self.difficulty = choices[(choices.index(self.difficulty) + 1) % len(choices)]
        self.input_mode = "CODE" if self.difficulty == "Hard" else "BLOCK"
        self.menu()

    def cycle_language(self):
        self.language = "C" if self.language == "Python" else "Python"
        self.menu()

    def toggle_input_mode(self):
        if self.solved:
            return
        self.input_mode = "CODE" if self.input_mode == "BLOCK" else "BLOCK"
        self.feedback = ""
        self.question()

    def start(self, category):
        self.app.taskMgr.remove(self.advance_task_name)
        self.category = category
        self.index = 0
        self.activity_session = ActivitySession(len(LESSONS[category]))
        self.category_scores[category] = 0
        self.app.completed_lessons = {
            pair for pair in self.app.completed_lessons if pair[0] != category
        }
        self.reset_answer()
        self.question()

    def select_token(self, index):
        if self.solved or index in self.used:
            return

        self.used.append(index)
        self.feedback = ""
        self.question()

    def undo(self):
        if not self.solved and self.used:
            self.used.pop()
            self.feedback = ""
            self.question()

    def choose(self, command):
        if not self.solved:
            self.choice = command
            self.feedback = ""
            self.question()

    # ==================================================
    # CHECK ANSWER
    # ==================================================

    def check(self):
        if self.category is None or self.solved:
            return

        exercise = LESSONS[self.category][self.index]

        if self.category == "arrange":
            answer = tuple(
                exercise.tokens[i] for i in self.used
            )
            correct = check_answer(self.category, self.index, answer)
        elif self.input_mode == "CODE":
            text = self.code_entry.get() if hasattr(self, "code_entry") else ""
            self.code_draft = text
            correct = validate_single_code(text, exercise.answer, self.language)
        else:
            answer = self.choice
            correct = check_answer(self.category, self.index, answer)

        if not self.activity_session.submit(correct):
            return
        self.solved = True
        self.last_correct = correct
        if correct:
            self.category_scores[self.category] = self.activity_session.score
            self.app.record_lesson(self.category, self.index)
            self.feedback = "+100 POINTS - CORRECT! NEXT QUESTION..."
        else:
            self.attempt.error()
            self.feedback = "INCORRECT - 0 POINTS. NEXT QUESTION..."

        self.question()
        self.app.taskMgr.doMethodLater(
            1.0, self._advance_automatically, self.advance_task_name
        )

    def _advance_automatically(self, task):
        if not self.active or self.category is None:
            return task.done
        self.next()
        return task.done

    def next(self):
        if not self.solved:
            return

        has_more = self.activity_session.advance()
        self.index = self.activity_session.index
        if not has_more:
            self.activity_summary()
        else:
            self.reset_answer()
            self.question()

    def activity_summary(self):
        category = self.category
        result = self.activity_session
        title = {
            "arrange": "ARRANGE BLOCKS",
            "debug": "FIND THE BUG",
            "fill": "FILL MISSING BLOCK",
        }[category]
        self.base("ACTIVITY COMPLETE")
        self.label(title, 0, 0.30, 0.053)
        self.label(f"CORRECT: {result.correct_count}/{result.total_questions}", 0, 0.10, 0.056)
        self.label(f"ACTIVITY SCORE: {result.score}", 0, -0.06, 0.067, self.GREEN)
        self.label(f"TOTAL SCORE: {self.total_score()}", 0, -0.22, 0.052)
        self.button("PLAY AGAIN", -0.52, -0.56,
                    lambda c=category: self.start(c), self.ORANGE, width=0.30)
        self.button("BACK TO MENU", 0.50, -0.56,
                    self.menu, self.BLUE, width=0.34)

    # ==================================================
    # EXERCISE SCREEN
    # ==================================================

    def question(self):
        exercise = LESSONS[self.category][self.index]

        titles = {
            "arrange": "ARRANGE BLOCKS",
            "debug": "FIND THE BUG",
            "fill": "FILL MISSING BLOCK",
        }

        self.base(titles[self.category])

        total = len(LESSONS[self.category])

        self.label(
            f"QUESTION {self.index + 1}/{total}",
            0, 0.32, 0.044
        )

        self.label(
            f"{self.difficulty}  |  {self.language}  |  {self.input_mode}",
            0, 0.26, 0.030
        )

        self.label(
            exercise.prompt,
            0, 0.16, 0.041
        )

        if self.category == "arrange":
            for i, token in enumerate(exercise.tokens):
                if i not in self.used:
                    self.button(
                        token,
                        -0.63 + i * 0.63,
                        -0.03,
                        lambda n=i: self.select_token(n),
                        self.PURPLE,
                        width=0.27,
                        height=0.055,
                        scale=0.037
                    )

            selected = " > ".join(
                exercise.tokens[i] for i in self.used
            )

            self.label(
                selected or "SELECT BLOCKS IN ORDER",
                0, -0.22, 0.040, max_width=1.65
            )

            self.button(
                "UNDO",
                -0.65,
                -0.38,
                self.undo,
                self.ORANGE,
                width=0.22,
                height=0.052,
                scale=0.04
            )

        else:
            self.label(
                " > ".join(exercise.shown),
                0, 0.02, 0.049, max_width=1.65
            )

            if self.input_mode == "CODE":
                self.code_entry = DirectEntry(
                    parent=self.root, text="", initialText=self.code_draft,
                    pos=(-0.65, 0, -0.17), scale=0.045,
                    width=27, numLines=1,
                    frameColor=(1, 1, 1, 1),
                    text_fg=self.TEXT, focus=0,
                )
                self.widgets.append(self.code_entry)
                self.label(
                    "e.g. " + COMMAND_EXAMPLES[self.language]["FORWARD"],
                    0, -0.28, 0.031
                )
            else:
                for i, command in enumerate(COMMANDS):
                    color = self.GREEN if self.choice == command else self.BLUE
                    self.button(
                        command, -0.63 + i * 0.63, -0.16,
                        lambda c=command: self.choose(c),
                        color, width=0.27, height=0.055, scale=0.037
                    )
            if self.difficulty == "Medium":
                self.button(
                    "MODE: " + self.input_mode,
                    0, -0.34, self.toggle_input_mode,
                    self.ORANGE, width=0.27, height=0.036, scale=0.031
                )

        feedback_color = (
            (0.08, 0.55, 0.30, 1)
            if self.last_correct
            else (0.78, 0.24, 0.34, 1)
        )

        self.label(
            self.feedback,
            0, -0.48, 0.037,
            feedback_color, max_width=1.78
        )

        self.button(
            "BACK",
            -0.60,
            -0.63,
            self.menu,
            self.BLUE,
            width=0.25,
            height=0.055,
            scale=0.042
        )

        if not self.solved:
            self.button(
                "CHECK",
                0.60,
                -0.63,
                self.check,
                self.GREEN,
                width=0.25,
                height=0.055,
                scale=0.042
            )
        else:
            self.label("NEXT QUESTION...", 0.60, -0.63, 0.035)
