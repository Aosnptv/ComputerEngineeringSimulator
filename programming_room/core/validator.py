# core/validator.py

from config import COMMANDS, MAX_COMMANDS
from core.mission import RobotMission
from core.program_flow import ProgramRunner


class CommandValidator:

    @staticmethod
    def validate(commands, require_conditional=False):

        if not isinstance(commands, (list, tuple)):
            return False, "Commands must be a list"

        if not commands:
            return False, "Please add commands first"

        if len(commands) > MAX_COMMANDS:
            return False, "Too many commands"

        for index, command in enumerate(commands):

            if command not in COMMANDS:
                return (
                    False,
                    f"Invalid command at position {index + 1}"
                )

        try:
            ProgramRunner(commands, require_conditional=require_conditional)
        except ValueError as exc:
            return False, str(exc)

        return True, "Commands are valid"

    @staticmethod
    def simulate(commands, level_index=0, difficulty="Classic"):
        valid, message = CommandValidator.validate(
            commands, require_conditional=difficulty == "Hard"
        )

        if not valid:
            return False, message, None

        mission = RobotMission(level_index, difficulty=difficulty)
        program = ProgramRunner(commands)

        for index in range(MAX_COMMANDS + 1):
            command = program.next_instruction(mission)
            if command is None:
                break
            if not mission.execute(command):
                return (
                    False,
                    f"Step {index + 1}: {mission.get_status()}",
                    mission.state,
                )

            if mission.state.completed:
                break

        if mission.state.completed:
            return True, "MISSION COMPLETE!", mission.state

        return (
            False,
            "Mission incomplete: collect batteries and reach goal",
            mission.state,
        )


class MissingBlockPuzzle:

    QUESTION = [
        "FORWARD",
        "FORWARD",
        None,
        "FORWARD",
    ]

    ANSWER = "TURN_LEFT"

    @classmethod
    def check_answer(cls, command):
        return command == cls.ANSWER

    @classmethod
    def get_question(cls):
        return list(cls.QUESTION)
