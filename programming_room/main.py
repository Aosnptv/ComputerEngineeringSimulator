"""
Programming Room
Main Game Controller
"""

import json
import math
from pathlib import Path

from panda3d.core import (
    loadPrcFileData,
    AmbientLight,
    DirectionalLight,
    Vec4,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
)

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import (
    DirectButton,
    DirectFrame,
    DirectLabel,
)

from config import ANIMATION_DELAY
from core.scoring import Attempt
from core.program_flow import ProgramRunner
from core.levels import LEVELS
from core.mission import RobotMission
from core.validator import (
    CommandValidator,
    MissingBlockPuzzle,
)

from scenes.programming_room import ProgrammingRoom
from scenes.robot_mission import RobotMissionScene
from scenes.classroom_controller import ClassroomController
from scenes.vr_panel import VRProgrammingPanel
from scenes.main_hub import MainHub, HubController
from ui.block_editor import BlockEditor


loadPrcFileData(
    "",
    "window-title Programming Room\n"
    "win-size 1280 800\n"
    "sync-video true\n"
    "show-frame-rate-meter false"
)


class ProgrammingLab(ShowBase):

    def __init__(self):
        super().__init__()

        self.disableMouse()
        self.setBackgroundColor(0.78, 0.88, 1.0, 1)

        self.mission = RobotMission()
        self.validator = CommandValidator()

        self.progress_path = Path(__file__).with_name(
            "progress.json"
        )

        # New session: all stars start gray.
        self.progress = {
            "unlocked": len(LEVELS),
            "best_stars": {}
        }

        self.completed_lessons = set()
        self.mission_scores = {}

        self.running = False
        self.tutorial_shown = False
        self.mission_attempt = Attempt()
        self.command_index = 0
        self.active_commands = []
        self.current_scene = "room"

        self.create_lighting()

        self.room = ProgrammingRoom(self)
        self.mission_scene = RobotMissionScene(self)

        self.create_interface()

        self.classroom = ClassroomController(
            self,
            self.room
        )

        self.vr_panel = VRProgrammingPanel(self)
        self.hub = MainHub(self)
        self.hub_controller = HubController(
            self,
            self.hub
        )

        self.accept(
            "escape",
            self.show_pause_screen
        )

        self.accept(
            "r",
            self.reset_mission
        )

        self.accept(
            "mouse1-up",
            self.finish_block_drag
        )

        # Start game at Main Hub.
        self.show_main_hub()

    # ==================================================
    # LIGHTING
    # ==================================================

    def create_lighting(self):

        ambient = AmbientLight("AmbientLight")

        ambient.setColor(
            Vec4(0.68, 0.68, 0.72, 1)
        )

        node = self.render.attachNewNode(ambient)

        self.render.setLight(node)

        sunlight = DirectionalLight("Sunlight")

        sunlight.setColor(
            Vec4(0.65, 0.65, 0.65, 1)
        )

        node = self.render.attachNewNode(sunlight)

        node.setHpr(-35, -55, 0)

        self.render.setLight(node)

    # ==================================================
    # INTERFACE
    # ==================================================

    def create_interface(self):

        self.title = DirectLabel(
            text="Programming Room",
            pos=(0, 0, 0.91),
            scale=0.065,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.12, 0.24, 0.43, 1),
        )

        self.room_button = DirectButton(
            text="BACK TO CLASSROOM",
            pos=(-1.05, 0, 0.76),
            scale=0.05,
            frameColor=(0.71, 0.85, 1, 1),
            command=self.show_room,
        )

        self.mission_button = DirectButton(
            text="SELECT LEVEL",
            pos=(-0.58, 0, 0.76),
            scale=0.05,
            frameColor=(0.59, 0.88, 0.70, 1),
            command=self.show_level_select,
        )

        self.status_label = DirectLabel(
            text="Explore the classroom!",
            pos=(0, 0, -0.89),
            scale=0.042,
            frameColor=(0.95, 0.97, 1, 0.93),
            text_fg=(0.13, 0.26, 0.44, 1),
        )

        self.help_button = DirectButton(
            text="? HOW TO PLAY",
            pos=(-1.04, 0, 0.63),
            scale=0.051,
            frameColor=(1, 0.88, 0.57, 1),
            text_fg=(0.12, 0.24, 0.43, 1),
            command=self.show_mission_tutorial,
        )

        self.help_button.hide()

        # Robot Mission tutorial.
        self.tutorial_frame = DirectFrame(
            parent=self.aspect2d,
            pos=(0, 0, 0.04),
            frameSize=(-0.82, 0.82, -0.59, 0.59),
            frameColor=(0.94, 0.97, 1, 0.99),
        )

        DirectLabel(
            parent=self.tutorial_frame,
            text="HOW TO PLAY - ROBOT MISSION",
            pos=(0, 0, 0.44),
            scale=0.062,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.12, 0.25, 0.43, 1),
        )

        DirectLabel(
            parent=self.tutorial_frame,
            text=(
                "1. CLICK + FORWARD / + TURN to add blocks.\n"
                "2. YOUR PROGRAM appears in the right panel.\n"
                "3. PRESS RUN to watch the robot move.\n"
                "4. USE UNDO / CLEAR / RESET to try again.\n"
                "5. IF OBSTACLE / ELSE / END IF checks the front cell."
            ),
            pos=(0, 0, 0.03),
            scale=0.041,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.12, 0.25, 0.43, 1),
        )

        DirectButton(
            parent=self.tutorial_frame,
            text="GOT IT - START PLAYING",
            pos=(0, 0, -0.43),
            scale=0.052,
            frameColor=(0.55, 0.88, 0.69, 1),
            command=self.hide_mission_tutorial,
        )

        self.tutorial_frame.hide()

        self.score_label = DirectLabel(
            text="Score: 0",
            pos=(0.15, 0, 0.76),
            scale=0.046,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.12, 0.24, 0.42, 1),
        )

        # Programming panel on the right.
        self.mission_ui = DirectFrame(
            pos=(1.20, 0, 0.08),
            frameSize=(-0.30, 0.30, -0.90, 0.67),
            frameColor=(0.95, 0.97, 1, 0.97),
        )

        self.mission_ui.setPythonTag(
            "app",
            self
        )

        self.block_editor = BlockEditor(
            self.mission_ui,
            on_change=self.update_command_count,
        )

        self.run_button = DirectButton(
            parent=self.mission_ui,
            text="RUN",
            pos=(-0.14, 0, -0.80),
            scale=0.055,
            frameColor=(0.47, 0.86, 0.62, 1),
            command=self.run_program,
        )

        self.reset_button = DirectButton(
            parent=self.mission_ui,
            text="RESET",
            pos=(0.15, 0, -0.80),
            scale=0.055,
            frameColor=(1, 0.75, 0.56, 1),
            command=self.reset_mission,
        )

        self.demo_button = DirectButton(
            text="LOAD DEMO",
            pos=(-1.08, 0, -0.08),
            scale=0.052,
            frameColor=(1, 0.88, 0.54, 1),
            command=self.load_demo,
        )

        self.puzzle_ui = DirectFrame(
            pos=(-1.05, 0, -0.43),
            frameSize=(-0.37, 0.37, -0.39, 0.37),
            frameColor=(0.95, 0.96, 1, 0.96),
        )

        self.puzzle_title = DirectLabel(
            parent=self.puzzle_ui,
            text="FILL THE MISSING BLOCK",
            pos=(0, 0, 0.28),
            scale=0.039,
            frameColor=(0, 0, 0, 0),
        )

        self.puzzle_question = DirectLabel(
            parent=self.puzzle_ui,
            text="FORWARD > FORWARD\n? > FORWARD",
            pos=(0, 0, 0.13),
            scale=0.037,
            frameColor=(0, 0, 0, 0),
        )

        self.puzzle_feedback = DirectLabel(
            parent=self.puzzle_ui,
            text="Choose the missing block",
            pos=(0, 0, -0.31),
            scale=0.036,
            frameColor=(0, 0, 0, 0),
        )

        self.puzzle_buttons = []

        for i, command in enumerate(
            ("FORWARD", "TURN_LEFT", "TURN_RIGHT")
        ):

            button = DirectButton(
                parent=self.puzzle_ui,
                text=command,
                pos=(0, 0, 0.015 - i * 0.105),
                scale=0.038,
                frameColor=(0.71, 0.86, 1, 1),
                command=self.check_puzzle,
                extraArgs=[command],
            )

            self.puzzle_buttons.append(button)

        self.overlay = DirectFrame(
            frameSize=(-1.4, 1.4, -0.82, 0.82),
            frameColor=(0.94, 0.97, 1, 0.97),
        )

        self.overlay_widgets = []
        self.star_nodes = []

    # ==================================================
    # OVERLAY
    # ==================================================

    def clear_overlay(self):

        for widget in self.overlay_widgets:
            widget.destroy()

        self.overlay_widgets.clear()

        for node in self.star_nodes:
            node.removeNode()

        self.star_nodes.clear()

    def overlay_label(
        self,
        text,
        z,
        scale=0.07
    ):

        widget = DirectLabel(
            parent=self.overlay,
            text=text,
            pos=(0, 0, z),
            scale=scale,
            frameColor=(0, 0, 0, 0),
            text_fg=(0.14, 0.27, 0.46, 1),
        )

        self.overlay_widgets.append(widget)

        return widget

    def overlay_button(
        self,
        text,
        x,
        z,
        callback,
        color=(0.70, 0.86, 1, 1)
    ):

        widget = DirectButton(
            parent=self.overlay,
            text=text,
            pos=(x, 0, z),
            scale=0.06,
            frameColor=color,
            text_fg=(0.12, 0.25, 0.40, 1),
            command=callback,
        )

        self.overlay_widgets.append(widget)

        return widget

    def show_overlay(self):

        self.stop_animation()
        self.hide_mission_tutorial()
        self.help_button.hide()

        if hasattr(self, "vr_panel"):
            self.vr_panel.close(silent=True)

        if hasattr(self, "classroom"):
            self.classroom.disable()

        if hasattr(self, "hub_controller"):
            self.hub_controller.disable()

        if hasattr(self, "hub"):
            self.hub.hide()

        self.room.hide()
        self.mission_scene.hide()
        self.mission_ui.hide()
        self.puzzle_ui.hide()
        self.demo_button.hide()
        self.score_label.hide()
        self.room_button.hide()
        self.mission_button.hide()
        self.status_label.hide()

        self.overlay.show()
        self.clear_overlay()

    def hide_overlay(self):

        self.overlay.hide()
        self.status_label.show()

    # ==================================================
    # DRAW GOLD / GRAY STAR
    # ==================================================

    def draw_star(
        self,
        x,
        z,
        radius=0.043,
        earned=True
    ):

        data = GeomVertexData(
            "Star",
            GeomVertexFormat.getV3(),
            Geom.UHStatic
        )

        vertices = GeomVertexWriter(
            data,
            "vertex"
        )

        vertices.addData3f(0, 0, 0)

        for i in range(10):

            angle = (
                math.pi / 2
                + i * math.pi / 5
            )

            r = (
                1.0
                if i % 2 == 0
                else 0.45
            )

            vertices.addData3f(
                math.cos(angle) * r,
                0,
                math.sin(angle) * r
            )

        triangles = GeomTriangles(
            Geom.UHStatic
        )

        for i in range(10):

            triangles.addVertices(
                0,
                i + 1,
                ((i + 1) % 10) + 1
            )

        triangles.closePrimitive()

        geom = Geom(data)
        geom.addPrimitive(triangles)

        node = GeomNode("GoldStar")
        node.addGeom(geom)

        star = self.overlay.attachNewNode(node)

        star.setPos(
            x,
            -0.1,
            z
        )

        star.setScale(radius)

        star.setDepthTest(False)
        star.setDepthWrite(False)

        if earned:

            star.setColor(
                1.0,
                0.72,
                0.16,
                1
            )

        else:

            star.setColor(
                0.72,
                0.77,
                0.84,
                1
            )

        self.star_nodes.append(star)

        return star

    def draw_star_rating(
        self,
        stars,
        z,
        x=0.66
    ):

        stars = max(
            0,
            min(3, int(stars))
        )

        for i in range(3):

            self.draw_star(
                x + i * 0.12,
                z,
                radius=0.045,
                earned=i < stars
            )

    # ==================================================
    # CLASSROOM
    # ==================================================

    def show_room(self):

        self.stop_animation()
        self.hide_mission_tutorial()
        self.help_button.hide()

        if hasattr(self, "vr_panel"):
            self.vr_panel.close(silent=True)

        self.hide_overlay()

        self.current_scene = "room"

        if hasattr(self, "hub_controller"):
            self.hub_controller.disable()
            self.hub.hide()

        self.room.show()
        self.mission_scene.hide()
        self.mission_ui.hide()
        self.puzzle_ui.hide()
        self.demo_button.hide()
        self.score_label.hide()
        self.room_button.hide()
        self.mission_button.hide()

        self.classroom.enable()

    def show_main_hub(self):

        self.stop_animation()
        self.hide_mission_tutorial()
        self.help_button.hide()

        self.vr_panel.close(silent=True)
        self.classroom.disable()

        self.current_scene = "hub"

        self.hide_overlay()

        self.room.hide()
        self.mission_scene.hide()

        for widget in (
            self.mission_ui,
            self.puzzle_ui,
            self.demo_button,
            self.score_label,
            self.room_button,
            self.mission_button,
            self.status_label
        ):
            widget.hide()

        self.hub.show()
        self.hub_controller.enable()

    def enter_programming_room(self):

        self.show_room()

    def show_locked_room(self, name):

        print(
            "Room unavailable:",
            name
        )

    def open_computer(self):

        if self.current_scene == "room":
            self.vr_panel.open()

    def open_computer_from_menu(self):

        self.vr_panel.open()

    def record_lesson(
        self,
        category,
        index
    ):

        self.completed_lessons.add(
            (category, index)
        )

    # ==================================================
    # LEVEL SELECTION
    # ==================================================

    def show_level_select(self):

        self.current_scene = "level_select"

        self.show_overlay()

        self.overlay_label(
            "SELECT ROBOT MISSION",
            0.55,
            0.085
        )

        self.overlay_label(
            "EASY: FEWER WALLS | MEDIUM: MORE WALLS | HARD: IF/ELSE REQUIRED",
            0.43,
            0.030
        )

        for i, level in enumerate(LEVELS):

            stars = self.progress[
                "best_stars"
            ].get(
                str(i),
                0
            )

            z = (
                0.31
                - i * 0.18
            )

            unlocked = True

            if unlocked:

                self.overlay_button(
                    f"{i + 1}. {level.title}",
                    -0.12,
                    z,
                    lambda n=i: self.start_level(n)
                )

                self.draw_star_rating(
                    stars,
                    z,
                    0.62
                )

            else:

                self.overlay_label(
                    f"{i + 1}. LOCKED",
                    z,
                    0.05
                )

        self.overlay_button(
            "BACK TO COMPUTER",
            -0.55,
            -0.66,
            self.open_computer_from_menu
        )

        self.overlay_button(
            "CLASSROOM",
            0.58,
            -0.66,
            self.show_room,
            (0.60, 0.88, 0.70, 1)
        )

        self.overlay_button(
            "LEVEL: " + self.vr_panel.difficulty,
            0,
            -0.79,
            self.cycle_mission_difficulty,
            (0.79, 0.71, 1, 1)
        )

    def cycle_mission_difficulty(self):

        self.vr_panel.cycle_difficulty()

        self.show_level_select()

    # ==================================================
    # ROBOT MISSION
    # ==================================================

    def start_level(self, index):

        if not 0 <= index < len(LEVELS):
            return

        self.stop_animation()

        self.mission.set_level(
            index,
            self.vr_panel.difficulty
        )

        self.mission_attempt.reset()

        # Reset stars for the new attempt.
        self.progress[
            "best_stars"
        ][str(index)] = 0

        self.mission_scores[index] = 0

        self.mission_scene.root.removeNode()

        self.mission_scene = RobotMissionScene(
            self
        )

        self.block_editor.clear()

        self.show_mission()

        self.status_label["text"] = (
            f"{self.vr_panel.difficulty} | "
            f"Level {index + 1}: "
            f"{self.mission.level.title}"
        )

        if not self.tutorial_shown:

            self.show_mission_tutorial()

            self.tutorial_shown = True

    def show_mission_tutorial(self):

        if self.current_scene != "mission":
            return

        self.tutorial_frame.show()

    def hide_mission_tutorial(self):

        self.tutorial_frame.hide()

    def show_mission(self):

        self.stop_animation()
        self.classroom.disable()

        if hasattr(self, "vr_panel"):
            self.vr_panel.close(silent=True)

        self.hide_overlay()

        self.current_scene = "mission"

        self.room.hide()
        self.mission_scene.show()

        self.mission_ui.show()
        self.help_button.show()

        # Hide old puzzle from Robot Mission.
        self.puzzle_ui.hide()

        if self.vr_panel.difficulty == "Easy":

            self.demo_button.show()

        else:

            self.demo_button.hide()

        self.score_label.show()
        self.room_button.show()
        self.mission_button.hide()

        self.camera.setPos(
            2,
            -5,
            13
        )

        self.camera.lookAt(
            2,
            2,
            0
        )

        self.mission_scene.update_robot(
            self.mission.state
        )

        self.update_score()

        self.status_label["text"] = (
            f"{self.vr_panel.difficulty}: "
            "Build blocks | "
            "IF OBSTACLE ... ELSE ... END IF"
        )

    # ==================================================
    # MISSION RESULT
    # ==================================================

    def show_result(self):

        index = self.mission.level_index

        used = len(
            self.active_commands
        )

        elapsed = self.mission_attempt.elapsed
        mistakes = self.mission_attempt.mistakes

        stars = self.mission_attempt.stars(
            self.vr_panel.difficulty
        )

        score = self.mission.get_score()

        old_score = self.mission_scores.get(
            index,
            0
        )

        self.mission_scores[index] = max(
            old_score,
            score
        )

        self.progress[
            "best_stars"
        ][str(index)] = max(
            stars,
            self.progress["best_stars"].get(
                str(index),
                0
            )
        )

        self.progress["unlocked"] = max(
            self.progress["unlocked"],
            min(
                len(LEVELS),
                index + 2
            )
        )

        self.current_scene = "result"

        self.show_overlay()

        self.overlay_label(
            "MISSION COMPLETE!",
            0.51,
            0.09
        )

        self.draw_star_rating(
            stars,
            0.30,
            x=-0.12
        )

        self.overlay_label(
            f"Level: {self.mission.level.title}",
            0.10,
            0.052
        )

        self.overlay_label(
            f"Score: {score} | Blocks: {used}",
            -0.06,
            0.055
        )

        self.overlay_label(
            f"Time: {int(elapsed // 60):02d}:"
            f"{int(elapsed % 60):02d} | "
            f"Mistakes: {mistakes}",
            -0.17,
            0.048
        )

        self.overlay_button(
            "RETRY",
            -0.35,
            -0.31,
            lambda: self.start_level(index)
        )

        if index + 1 < len(LEVELS):

            self.overlay_button(
                "NEXT LEVEL",
                0.36,
                -0.31,
                lambda: self.start_level(
                    index + 1
                ),
                (0.54, 0.88, 0.68, 1)
            )

        self.overlay_button(
            "LEVEL SELECT",
            -0.48,
            -0.55,
            self.show_level_select
        )

        self.overlay_button(
            "CLASSROOM",
            0.48,
            -0.55,
            self.show_room,
            (0.54, 0.88, 0.68, 1)
        )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    def show_end_screen(self):

        if self.current_scene != "room":
            return

        self.current_scene = "end"

        self.show_overlay()

        lesson_score = self.vr_panel.score

        robot_score = sum(
            self.mission_scores.values()
        )

        total_score = (
            lesson_score
            + robot_score
        )

        completed = len(
            self.completed_lessons
        )

        completed_levels = sum(
            1
            for i in range(len(LEVELS))
            if self.progress[
                "best_stars"
            ].get(str(i), 0) > 0
        )

        self.overlay_label(
            "PROGRAMMING LAB COMPLETE!",
            0.54,
            0.085
        )

        self.overlay_label(
            f"Lessons: {completed}/9",
            0.31,
            0.055
        )

        self.overlay_label(
            f"Robot Missions: {completed_levels}/5",
            0.17,
            0.055
        )

        self.overlay_label(
            f"Programming Score: {lesson_score}",
            0.03,
            0.055
        )

        self.overlay_label(
            f"Robot Score: {robot_score}",
            -0.11,
            0.055
        )

        self.overlay_label(
            f"TOTAL SCORE: {total_score}",
            -0.28,
            0.073
        )

        self.overlay_button(
            "BACK TO CLASSROOM",
            -0.49,
            -0.55,
            self.show_room,
            (0.70, 0.86, 1, 1)
        )

        self.overlay_button(
            "MAIN HUB",
            0,
            -0.70,
            self.show_main_hub,
            (0.73, 0.88, 1, 1)
        )

        self.overlay_button(
            "FINISH GAME",
            0.49,
            -0.55,
            self.userExit,
            (0.55, 0.88, 0.69, 1)
        )

    # ==================================================
    # PAUSE
    # ==================================================

    def show_pause_screen(self):

        if self.current_scene == "hub":
            return

        if self.current_scene != "room":

            self.show_room()
            return

        self.current_scene = "pause"

        self.show_overlay()

        self.overlay_label(
            "PAUSED",
            0.40,
            0.095
        )

        self.overlay_button(
            "CONTINUE",
            0,
            0.02,
            self.show_room
        )

    # ==================================================
    # PROGRESS
    # ==================================================

    def load_progress(self):

        default = {
            "unlocked": 1,
            "best_stars": {}
        }

        try:

            data = json.loads(
                self.progress_path.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(
                data,
                dict
            ):
                return default

            unlocked = int(
                data.get(
                    "unlocked",
                    1
                )
            )

            scores = data.get(
                "best_stars",
                {}
            )

            if not isinstance(
                scores,
                dict
            ):
                scores = {}

            best_stars = {}

            for i in range(len(LEVELS)):

                key = str(i)

                try:

                    stars = int(
                        scores.get(
                            key,
                            0
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    stars = 0

                best_stars[key] = max(
                    0,
                    min(
                        3,
                        stars
                    )
                )

            return {
                "unlocked": max(
                    1,
                    min(
                        len(LEVELS),
                        unlocked
                    )
                ),
                "best_stars": best_stars
            }

        except (
            OSError,
            ValueError,
            TypeError
        ):

            return default

    def save_progress(self):

        try:

            self.progress_path.write_text(
                json.dumps(
                    self.progress,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

        except OSError:

            print(
                "WARNING: Cannot save progress."
            )

    # ==================================================
    # ROBOT CONTROLS
    # ==================================================

    def update_score(self):

        score = self.mission.get_score()

        collected = len(
            self.mission.state.collected
        )

        total = len(
            self.mission.level.batteries
        )

        self.score_label["text"] = (
            f"Score: {score} | "
            f"Batteries: {collected}/{total}"
        )

    def update_command_count(self):

        if (
            not hasattr(
                self,
                "block_editor"
            )
            or self.running
        ):
            return

        count = len(
            self.block_editor.get_commands()
        )

        if count:

            self.status_label["text"] = (
                f"STEP 2: {count} BLOCK(S) ADDED "
                "- PRESS RUN"
            )

        else:

            self.status_label["text"] = (
                "STEP 1: CLICK + FORWARD / "
                "+ TURN IN THE RIGHT PANEL"
            )

        self.status_label["text_fg"] = (
            0.12,
            0.28,
            0.45,
            1
        )

    def stop_animation(self):

        self.taskMgr.remove(
            "robot_animation"
        )

        self.taskMgr.remove(
            "show_mission_result"
        )

        self.running = False

    def reset_mission(
        self,
        restart_timer=True
    ):

        if self.current_scene != "mission":
            return

        self.stop_animation()

        self.mission.reset()

        if restart_timer:
            self.mission_attempt.reset()

        self.command_index = 0
        self.active_commands = []

        self.mission_scene.reset(
            self.mission.state
        )

        self.update_score()

        self.status_label["text"] = (
            "Mission reset. Ready to play!"
        )

    def load_demo(self):

        if (
            self.current_scene != "mission"
            or self.running
            or self.vr_panel.difficulty != "Easy"
        ):
            return

        self.block_editor.commands = list(
            self.mission.level.demo
        )

        self.block_editor.refresh()

        self.status_label["text"] = (
            "Demo loaded! Press RUN."
        )

    def run_program(self):

        if (
            self.current_scene != "mission"
            or self.running
        ):
            return

        commands = (
            self.block_editor.get_commands()
        )

        valid, message = (
            self.validator.validate(
                commands,
                require_conditional=(
                    self.vr_panel.difficulty
                    == "Hard"
                )
            )
        )

        if not valid:

            self.mission_attempt.error()

            if not commands:

                self.status_label["text"] = (
                    "NO BLOCKS: CLICK + FORWARD "
                    "ON THE RIGHT, THEN RUN"
                )

            else:

                self.status_label["text"] = (
                    "CHECK YOUR BLOCKS: "
                    + message
                )

            self.status_label["text_fg"] = (
                0.75,
                0.16,
                0.24,
                1
            )

            return

        self.reset_mission(
            restart_timer=False
        )

        self.active_commands = list(
            commands
        )

        self.program_runner = ProgramRunner(
            commands
        )

        self.command_index = 0
        self.running = True

        self.status_label["text"] = (
            "Robot is running..."
        )

        self.status_label["text_fg"] = (
            0.09,
            0.51,
            0.30,
            1
        )

        self.taskMgr.doMethodLater(
            ANIMATION_DELAY,
            self.animation_step,
            "robot_animation"
        )

    def animation_step(self, task):

        if not self.running:
            return task.done

        command = (
            self.program_runner.next_instruction(
                self.mission
            )
        )

        if command is None:

            self.running = False

            if not self.mission.state.completed:
                self.mission_attempt.error()

            self.status_label["text"] = (
                self.mission.get_status()
            )

            return task.done

        success = self.mission.execute(
            command
        )

        self.command_index += 1

        self.mission_scene.update_robot(
            self.mission.state
        )

        self.update_score()

        if not success:

            self.running = False
            self.mission_attempt.error()

            self.status_label["text"] = (
                f"Block {self.command_index}: "
                f"{self.mission.get_status()}"
            )

            return task.done

        if self.mission.state.completed:

            self.running = False

            self.status_label["text"] = (
                "MISSION COMPLETE! GREAT JOB!"
            )

            self.taskMgr.doMethodLater(
                0.8,
                self.open_result_task,
                "show_mission_result"
            )

            return task.done

        self.status_label["text"] = (
            f"Executing block "
            f"{self.command_index}"
        )

        return task.again

    def open_result_task(self, task):

        if (
            self.current_scene == "mission"
            and self.mission.state.completed
        ):

            self.show_result()

        return task.done

    def finish_block_drag(self):

        if (
            not self.running
            and self.current_scene == "mission"
        ):

            self.block_editor.finish_drag()

    def check_puzzle(self, command):

        correct = (
            MissingBlockPuzzle.check_answer(
                command
            )
        )

        if correct:

            self.puzzle_feedback["text"] = (
                "CORRECT! GREAT JOB!"
            )

            self.puzzle_feedback["text_fg"] = (
                0.12,
                0.63,
                0.28,
                1
            )

        else:

            self.puzzle_feedback["text"] = (
                "TRY AGAIN!"
            )

            self.puzzle_feedback["text_fg"] = (
                0.85,
                0.23,
                0.29,
                1
            )


if __name__ == "__main__":

    game = ProgrammingLab()

    game.run()