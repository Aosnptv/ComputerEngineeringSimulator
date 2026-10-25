"""Three-question, single-attempt activity scoring independent of Panda3D."""


class ActivitySession:
    def __init__(self, total_questions=3, points_per_correct=100):
        self.total_questions = total_questions
        self.points_per_correct = points_per_correct
        self.index = 0
        self.answered = False
        self.correct_count = 0
        self.score = 0
        self.results = []

    def submit(self, correct):
        """Answer exactly once. Return False when already answered."""
        if self.answered or self.finished:
            return False
        self.answered = True
        self.results.append(bool(correct))
        if correct:
            self.correct_count += 1
            self.score += self.points_per_correct
        return True

    def advance(self):
        """Advance after a submitted answer. False means summary is due."""
        if not self.answered:
            return True
        self.index += 1
        self.answered = False
        return not self.finished

    @property
    def finished(self):
        return self.index >= self.total_questions
