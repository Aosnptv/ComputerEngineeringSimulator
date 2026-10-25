"""Safe, narrow robot-command parser. Never executes user-supplied Python/C."""
import re


COMMAND_EXAMPLES = {
    "Python": {"FORWARD": "robot.move_forward()", "TURN_LEFT": "robot.turn_left()", "TURN_RIGHT": "robot.turn_right()"},
    "C": {"FORWARD": "move_forward();", "TURN_LEFT": "turn_left();", "TURN_RIGHT": "turn_right();"},
}


def parse_instruction(line, language):
    if language not in COMMAND_EXAMPLES:
        raise ValueError("Unknown programming language")
    line = line.strip()
    for command, code in COMMAND_EXAMPLES[language].items():
        if line == code:
            return command
    raise ValueError("Only the displayed robot instructions are allowed")


def parse_program(source, language):
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    if len(lines) > 100:
        raise ValueError("Too many instructions")
    return tuple(parse_instruction(line, language) for line in lines)


def validate_single_code(code, expected, language):
    try:
        return parse_instruction(code, language) == expected
    except ValueError:
        return False
