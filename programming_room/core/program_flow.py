"""Safe block-based IF/ELSE interpreter for robot missions."""

try:
    from ..config import COMMANDS, MAX_COMMANDS
except ImportError:
    from config import COMMANDS, MAX_COMMANDS

MOVEMENT_COMMANDS = ("FORWARD", "TURN_LEFT", "TURN_RIGHT")


class ProgramRunner:
    """Interprets blocks against the current robot state, one action at a time."""

    def __init__(self, commands, require_conditional=False):
        if not isinstance(commands, (tuple, list)) or not commands:
            raise ValueError("Please add commands first")
        if len(commands) > MAX_COMMANDS:
            raise ValueError("Too many commands")
        if any(command not in COMMANDS for command in commands):
            raise ValueError("Unknown block in program")
        if not any(command in MOVEMENT_COMMANDS for command in commands):
            raise ValueError("Add a movement or turning block")
        self.commands = list(commands)
        self.branch = {}
        self.end = {}
        stack = []
        for index, command in enumerate(self.commands):
            if command == "IF_OBSTACLE":
                stack.append([index, None])
            elif command == "ELSE":
                if not stack or stack[-1][1] is not None:
                    raise ValueError("ELSE needs one matching IF")
                stack[-1][1] = index
            elif command == "END_IF":
                if not stack:
                    raise ValueError("END IF needs a matching IF")
                if_index, else_index = stack.pop()
                self.branch[if_index] = else_index if else_index is not None else index
                if else_index is not None:
                    self.end[else_index] = index
        if stack:
            raise ValueError("Add END IF to close your IF block")
        if require_conditional and not any(
            command == "IF_OBSTACLE" for command in self.commands
        ):
            raise ValueError("Hard mode: use an IF / ELSE / END IF block")
        if require_conditional and "ELSE" not in self.commands:
            raise ValueError("Hard mode: include ELSE in your program")
        self.index = 0

    def next_instruction(self, robot):
        """Return next primitive command, or None when program is finished."""
        while self.index < len(self.commands):
            instruction = self.commands[self.index]
            if instruction == "IF_OBSTACLE":
                if robot.obstacle_ahead():
                    self.index += 1
                else:
                    self.index = self.branch[self.index] + 1
            elif instruction == "ELSE":
                self.index = self.end[self.index] + 1
            elif instruction == "END_IF":
                self.index += 1
            else:
                self.index += 1
                return instruction
        return None
