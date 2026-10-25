
# =====================================================
# Programming Lab V6
# Beautiful Soft Cartoon Programming Lesson UI
# =====================================================

from direct.gui.DirectGui import (
    DirectButton,
    DirectFrame,
    DirectLabel,
)

from direct.gui import DirectGuiGlobals as DGG

from core.lessons import (
    COMMANDS,
    LESSONS,
    check_answer,
)


# =====================================================
# Color Palette
# =====================================================

BG = (0.93, 0.96, 1.0, 1)
WHITE = (1.0, 1.0, 1.0, 1)

NAVY = (0.13, 0.25, 0.43, 1)
MUTED = (0.38, 0.48, 0.63, 1)

BLUE = (0.61, 0.79, 1.0, 1)
BLUE_LIGHT = (0.84, 0.92, 1.0, 1)

PURPLE = (0.77, 0.75, 1.0, 1)
PURPLE_LIGHT = (0.92, 0.90, 1.0, 1)

MINT = (0.53, 0.88, 0.69, 1)
MINT_LIGHT = (0.85, 0.97, 0.89, 1)

PINK = (1.0, 0.69, 0.74, 1)
PINK_LIGHT = (1.0, 0.91, 0.93, 1)

YELLOW = (1.0, 0.86, 0.55, 1)


class LessonScreen:

    def __init__(self, app):

        self.app = app

        self.category = None
        self.question_index = 0

        self.used_tokens = []
        self.selected = None

        self.feedback = ""
        self.solved = False

        self.score = 0

        # Main lesson screen
        self.root = DirectFrame(
            parent=app.aspect2d,
            frameSize=(-1.48, 1.48, -0.87, 0.84),
            frameColor=BG,
            relief=DGG.FLAT,
        )

        self.widgets = []
        self.root.hide()

    # =================================================
    # UI Helpers
    # =================================================

    def clear(self):

        for widget in self.widgets:
            widget.destroy()

        self.widgets.clear()

    def panel(self, x, z, width, height, color):

        widget = DirectFrame(
            parent=self.root,
            pos=(x, 0, z),
            frameSize=(
                -width / 2,
                width / 2,
                -height / 2,
                height / 2,
            ),
            frameColor=color,
            relief=DGG.FLAT,
        )

        self.widgets.append(widget)

        return widget

    def label(
        self,
        text,
        x,
        z,
        size=0.05,
        color=NAVY,
    ):

        widget = DirectLabel(
            parent=self.root,
            text=text,
            pos=(x, 0, z),
            scale=size,
            frameColor=(0, 0, 0, 0),
            text_fg=color,
            text_align=0,
        )

        self.widgets.append(widget)

        return widget

    def button(
        self,
        text,
        x,
        z,
        callback,
        color=BLUE_LIGHT,
        width=0.55,
        height=0.13,
        text_size=0.044,
    ):

        widget = DirectButton(
            parent=self.root,
            text=text,
            pos=(x, 0, z),
            scale=1,
            frameSize=(
                -width / 2,
                width / 2,
                -height / 2,
                height / 2,
            ),
            frameColor=color,
            relief=DGG.FLAT,
            text_scale=text_size,
            text_pos=(0, -0.015),
            text_fg=NAVY,
            pressEffect=1.02,
            command=callback,
        )

        self.widgets.append(widget)

        return widget

    # =================================================
    # Open / Close Screen
    # =================================================

    def open_page(self):

        self.app.show_overlay()

        # Hide original menu overlay
        self.app.overlay.hide()

        self.app.current_scene = "lessons"

        self.root.show()
        self.clear()

    def hide(self):
        self.root.hide()

    # =================================================
    # Header
    # =================================================

    def draw_header(self, title):

        # Decorative top bar
        self.panel(
            0, 0.63,
            2.68, 0.28,
            BLUE_LIGHT,
        )

        # Small accent on the left
        self.panel(
            -1.25, 0.63,
            0.055, 0.28,
            PURPLE,
        )

        self.label(
            title,
            0, 0.66,
            0.085,
            NAVY,
        )

        self.label(
            "PROGRAMMING LAB",
            0, 0.53,
            0.034,
            MUTED,
        )

    # =================================================
    # Lesson Selection Menu
    # =================================================

    def show_menu(self):

        self.open_page()

        self.draw_header("CODING CHALLENGES")

        self.label(
            "Choose your learning challenge",
            0, 0.34,
            0.052,
            MUTED,
        )

        # Arrange card
        self.panel(
            -0.82, 0.02,
            0.78, 0.38,
            WHITE,
        )

        self.button(
            "ARRANGE BLOCKS",
            -0.82, 0.08,
            lambda: self.start("arrange"),
            PURPLE_LIGHT,
            width=0.70,
            height=0.14,
            text_size=0.039,
        )

        self.label(
            "Put code in order",
            -0.82, -0.07,
            0.037,
            MUTED,
        )

        # Debug card
        self.panel(
            0, 0.02,
            0.78, 0.38,
            WHITE,
        )

        self.button(
            "FIND THE BUG",
            0, 0.08,
            lambda: self.start("debug"),
            PINK_LIGHT,
            width=0.70,
            height=0.14,
            text_size=0.039,
        )

        self.label(
            "Fix wrong commands",
            0, -0.07,
            0.037,
            MUTED,
        )

        # Fill card
        self.panel(
            0.82, 0.02,
            0.78, 0.38,
            WHITE,
        )

        self.button(
            "FILL THE BLOCK",
            0.82, 0.08,
            lambda: self.start("fill"),
            MINT_LIGHT,
            width=0.70,
            height=0.14,
            text_size=0.039,
        )

        self.label(
            "Complete the code",
            0.82, -0.07,
            0.037,
            MUTED,
        )

        # Session score
        self.panel(
            0, -0.36,
            1.38, 0.15,
            YELLOW,
        )

        self.label(
            f"SESSION SCORE: {self.score}",
            0, -0.37,
            0.047,
            NAVY,
        )

        self.button(
            "BACK TO MAIN MENU",
            0, -0.69,
            self.app.show_main_menu,
            BLUE_LIGHT,
            width=0.72,
        )

    # =================================================
    # Start Category
    # =================================================

    def start(self, category):

        self.category = category
        self.question_index = 0

        self.reset_answer()

        self.show_question()

    def reset_answer(self):

        self.used_tokens = []
        self.selected = None

        self.feedback = ""
        self.solved = False

    # =================================================
    # Arrange Blocks
    # =================================================

    def add_token(self, token_index):

        if self.solved:
            return

        if token_index in self.used_tokens:
            return

        self.used_tokens.append(token_index)
        self.feedback = ""

        self.show_question()

    def undo_token(self):

        if self.solved:
            return

        if self.used_tokens:
            self.used_tokens.pop()

        self.feedback = ""
        self.show_question()

    def clear_tokens(self):

        if self.solved:
            return

        self.used_tokens = []
        self.feedback = ""

        self.show_question()

    # =================================================
    # Choose Command
    # =================================================

    def choose(self, command):

        if self.solved:
            return

        self.selected = command
        self.feedback = ""

        self.show_question()

    # =================================================
    # Check Answer
    # =================================================

    def check(self):

        exercise = LESSONS[
            self.category
        ][
            self.question_index
        ]

        if self.category == "arrange":

            response = tuple(
                exercise.tokens[i]
                for i in self.used_tokens
            )

        else:
            response = self.selected

        correct = check_answer(
            self.category,
            self.question_index,
            response,
        )

        if correct:

            if not self.solved:
                self.score += 100

            self.solved = True
            self.feedback = "CORRECT! +100 POINTS"

        else:
            self.feedback = "TRY AGAIN!"

        self.show_question()

    # =================================================
    # Next Question
    # =================================================

    def next_question(self):

        self.question_index += 1

        if self.question_index >= len(
            LESSONS[self.category]
        ):

            self.show_menu()
            return

        self.reset_answer()
        self.show_question()

    # =================================================
    # Question Interface
    # =================================================

    def show_question(self):

        self.open_page()

        exercise = LESSONS[
            self.category
        ][
            self.question_index
        ]

        titles = {
            "arrange": "ARRANGE BLOCKS",
            "debug": "FIND THE BUG",
            "fill": "FILL MISSING BLOCK",
        }

        self.draw_header(
            titles[self.category]
        )

        # -----------------------------------------
        # Progress display
        # -----------------------------------------

        self.panel(
            0, 0.35,
            2.35, 0.13,
            WHITE,
        )

        self.label(
            f"QUESTION {self.question_index + 1} / 3",
            -0.67, 0.34,
            0.044,
            MUTED,
        )

        self.label(
            f"SCORE: {self.score}",
            0.70, 0.34,
            0.044,
            NAVY,
        )

        # -----------------------------------------
        # Question card
        # -----------------------------------------

        self.panel(
            0, 0.15,
            2.35, 0.20,
            PURPLE_LIGHT,
        )

        self.label(
            exercise.prompt,
            0, 0.14,
            0.050,
            NAVY,
        )

        # -----------------------------------------
        # Arrange Blocks
        # -----------------------------------------

        if self.category == "arrange":

            self.label(
                "SELECT BLOCKS IN THE CORRECT ORDER",
                0, -0.035,
                0.038,
                MUTED,
            )

            for i, command in enumerate(
                exercise.tokens
            ):

                if i not in self.used_tokens:

                    self.button(
                        command,
                        -0.73 + i * 0.73,
                        -0.17,
                        lambda n=i: self.add_token(n),
                        BLUE_LIGHT,
                        width=0.65,
                        height=0.13,
                        text_size=0.039,
                    )

            answer = "  >  ".join(
                exercise.tokens[i]
                for i in self.used_tokens
            )

            self.panel(
                0, -0.36,
                2.30, 0.15,
                WHITE,
            )

            self.label(
                answer or "Your selected blocks appear here",
                0, -0.375,
                0.043,
                NAVY if answer else MUTED,
            )

            self.button(
                "UNDO",
                -0.69, -0.52,
                self.undo_token,
                YELLOW,
                width=0.30,
                height=0.10,
                text_size=0.038,
            )

            self.button(
                "CLEAR",
                -0.34, -0.52,
                self.clear_tokens,
                PINK_LIGHT,
                width=0.30,
                height=0.10,
                text_size=0.038,
            )

        # -----------------------------------------
        # Debug / Missing Block
        # -----------------------------------------

        else:

            self.panel(
                0, -0.035,
                2.35, 0.14,
                WHITE,
            )

            self.label(
                "  >  ".join(exercise.shown),
                0, -0.045,
                0.052,
                NAVY,
            )

            self.label(
                "CHOOSE THE CORRECT COMMAND",
                0, -0.17,
                0.038,
                MUTED,
            )

            for i, command in enumerate(COMMANDS):

                selected = self.selected == command

                self.button(
                    command,
                    -0.73 + i * 0.73,
                    -0.31,
                    lambda c=command: self.choose(c),
                    MINT if selected else BLUE_LIGHT,
                    width=0.65,
                    height=0.14,
                    text_size=0.041,
                )

        # -----------------------------------------
        # Feedback
        # -----------------------------------------

        if self.feedback:

            feedback_color = (
                MINT_LIGHT
                if self.solved
                else PINK_LIGHT
            )

            self.panel(
                0, -0.54,
                1.20, 0.105,
                feedback_color,
            )

            self.label(
                self.feedback,
                0, -0.552,
                0.039,
                NAVY,
            )

        # -----------------------------------------
        # Footer buttons
        # -----------------------------------------

        self.button(
            "LESSON MENU",
            -0.53, -0.72,
            self.show_menu,
            BLUE_LIGHT,
            width=0.62,
            height=0.13,
        )

        if self.solved:

            self.button(
                "NEXT QUESTION",
                0.53, -0.72,
                self.next_question,
                MINT,
                width=0.66,
                height=0.13,
            )

        else:

            self.button(
                "CHECK ANSWER",
                0.53, -0.72,
                self.check,
                MINT,
                width=0.66,
                height=0.13,
            )
