from board import START, EXIT, SIZE, MAX_MOVES, MOVES, has_alarm


class Simulator:

    def __init__(self, prohibited, images, goal):
        self._prohibited = prohibited   # hidden from the robot
        self._images = images           # {cell: (image, label)} - labels hidden
        self.goal = goal
        self.reset()

    def reset(self):
        """Retry the same board: hazards and images stay, everything else restarts."""
        self.position = START
        self.moves_used = 0
        self.score = 0
        self.collected = {}   # {cell: digit} for correctly collected digits
        self.status = "running"

    def observe(self):
        """Everything the robot is allowed to know right now."""
        image = None
        if self.position in self._images:
            image = self._images[self.position][0]   # the picture only, not the label
        return {
            "position": self.position,
            "alarm": has_alarm(self.position, self._prohibited),
            "image": image,
            "moves_used": self.moves_used,
            "score": self.score,
            "collected": list(self.collected.values()),
            "status": self.status,
        }

    def move(self, direction):
        """Move one cell: "N", "S", "E" or "W". Costs one move."""
        self._check_running()
        dr, dc = MOVES[direction]
        r, c = self.position[0] + dr, self.position[1] + dc
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            raise ValueError("Cannot move off the grid")

        self.position = (r, c)
        self.moves_used += 1

        if self.position in self._prohibited:
            self.status = "failure: prohibited cell"
        elif self.position == EXIT:
            if self._mission_done():
                self.status = "success"
            else:
                self.status = "failure: mission not completed"
        elif self.moves_used >= MAX_MOVES:
            self.status = "failure: timeout"
        return self.observe()

    def collect(self, prediction):
        """Declare the digit in the current cell. Does not cost a move.
        Correct -> collected and added to score. Wrong -> run fails."""
        self._check_running()
        if self.position not in self._images:
            raise ValueError("There is no digit in this cell")
        if self.position in self.collected:
            raise ValueError("This digit was already collected")

        label = self._images[self.position][1]
        if prediction != label:
            self.status = "failure: wrong digit"
            return self.observe()

        self.collected[self.position] = label
        self.score += label
        if self.goal["mission"] == "exact_total" and self.score > self.goal["target"]:
            self.status = "failure: over target"
        return self.observe()

    def stop(self):
        """Early stop: the robot gives up safely. Counts as a failure."""
        self._check_running()
        self.status = "failure: early stop"
        return self.observe()

    # internal helpers 

    def _mission_done(self):
        """Checked when the robot enters the exit."""
        if self.goal["mission"] == "exact_total":
            return self.score == self.goal["target"]
        return True   # fewest_steps and most_digit only need to reach the exit

    def _check_running(self):
        if self.status != "running":
            raise RuntimeError("The run is over (" + self.status + "). Call reset().")