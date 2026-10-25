
# core/lessons.py

from dataclasses import dataclass


COMMANDS = (
    "FORWARD",
    "TURN_LEFT",
    "TURN_RIGHT",
)


@dataclass(frozen=True)
class Exercise:
    prompt: str
    answer: object
    tokens: tuple = ()
    shown: tuple = ()


LESSONS = {

    # Exercise 1: Arrange programming blocks
    "arrange": [

        Exercise(
            prompt="Move forward twice, then turn left.",
            answer=("FORWARD", "FORWARD", "TURN_LEFT"),
            tokens=("TURN_LEFT", "FORWARD", "FORWARD"),
        ),

        Exercise(
            prompt="Turn right, then move forward twice.",
            answer=("TURN_RIGHT", "FORWARD", "FORWARD"),
            tokens=("FORWARD", "TURN_RIGHT", "FORWARD"),
        ),

        Exercise(
            prompt="Turn left, move forward, then turn right.",
            answer=("TURN_LEFT", "FORWARD", "TURN_RIGHT"),
            tokens=("TURN_RIGHT", "TURN_LEFT", "FORWARD"),
        ),
    ],

    # Exercise 2: Find and fix the incorrect command
    "debug": [

        Exercise(
            prompt="Fix block 2 to move forward twice.",
            answer="FORWARD",
            shown=("FORWARD", "TURN_LEFT"),
        ),

        Exercise(
            prompt="Fix block 1 to turn right, then move.",
            answer="TURN_RIGHT",
            shown=("TURN_LEFT", "FORWARD"),
        ),

        Exercise(
            prompt="Fix block 3 to make a left turn.",
            answer="TURN_LEFT",
            shown=("FORWARD", "FORWARD", "TURN_RIGHT"),
        ),
    ],

    # Exercise 3: Fill the missing command
    "fill": [

        Exercise(
            prompt="Fill the missing LEFT turn.",
            answer="TURN_LEFT",
            shown=("FORWARD", "?", "FORWARD"),
        ),

        Exercise(
            prompt="Turn RIGHT before moving forward.",
            answer="TURN_RIGHT",
            shown=("?", "FORWARD"),
        ),

        Exercise(
            prompt="Move forward a total of two times.",
            answer="FORWARD",
            shown=("FORWARD", "?"),
        ),
    ],
}


def check_answer(category, index, response):
    """
    Return True if the answer is correct.
    """

    if category not in LESSONS:
        return False

    if not 0 <= index < len(LESSONS[category]):
        return False

    correct_answer = LESSONS[category][index].answer

    if category == "arrange":
        return tuple(response) == correct_answer

    return response == correct_answer
