
import os
import random
from collections import deque

import numpy as np

SIZE = 6
START = (0, 0)
EXIT = (5, 5)
MAX_MOVES = 40
MOVES = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

# The MNIST file lives in the "data" folder next to "src"
MNIST_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mnist.npz")


# Grid helpers 

def neighbors(cell):
    """Cells directly up, down, left, right of `cell` (inside the grid)."""
    r, c = cell
    result = []
    for dr, dc in MOVES.values():
        if 0 <= r + dr < SIZE and 0 <= c + dc < SIZE:
            result.append((r + dr, c + dc))
    return result


def has_alarm(cell, prohibited):
    """A cell has an alarm if any of its neighbors is prohibited."""
    for n in neighbors(cell):
        if n in prohibited:
            return True
    return False


#  CSP board generation 

def safe_path_exists(prohibited):
    """BFS from START to EXIT using only cells that are safe and have no alarm."""
    visited = {START}
    queue = deque([START])
    while queue:
        cell = queue.popleft()
        if cell == EXIT:
            return True
        for n in neighbors(cell):
            if n not in visited and n not in prohibited and not has_alarm(n, prohibited):
                visited.add(n)
                queue.append(n)
    return False


def broken_rules(prohibited):
    """Return a list of the CSP rules this layout breaks (empty list = valid)."""
    broken = []
    # Rule 1: exactly 3 prohibited cells
    if len(prohibited) != 3:
        broken.append("Rule 1: must have exactly 3 prohibited cells")
    # Rule 2: start, exit, and their neighbors must be safe
    protected = [START, EXIT] + neighbors(START) + neighbors(EXIT)
    for cell in protected:
        if cell in prohibited:
            broken.append("Rule 2: start/exit or a neighbor is prohibited")
            break
    # Rule 3: a safe, alarm-free route from start to exit must exist
    if not safe_path_exists(prohibited):
        broken.append("Rule 3: no safe alarm-free path from start to exit")
    return broken


def generate_board(seed=None):
    """Pick 3 random cells until the layout breaks no rules."""
    rng = random.Random(seed)   # same seed -> same board
    all_cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    while True:
        prohibited = set(rng.sample(all_cells, 3))
        if broken_rules(prohibited) == []:
            return prohibited


# Handwritten digit images 

def load_mnist_test():
    """Load the 10,000 MNIST *test* images (28x28) and their labels.
    The classifier trains on the training images, so these are never seen before."""
    data = np.load(MNIST_FILE)
    return data["x_test"], data["y_test"]


def assign_images(prohibited, mnist_images, mnist_labels, seed=None):
    """Give one random MNIST image to every cell except start, exit and prohibited.
    Returns {cell: (image, label)}. Same seed -> same images."""
    rng = random.Random(seed)
    cells = []
    for r in range(SIZE):
        for c in range(SIZE):
            cell = (r, c)
            if cell != START and cell != EXIT and cell not in prohibited:
                cells.append(cell)
    picks = rng.sample(range(len(mnist_labels)), len(cells))   # 31 different images
    images = {}
    for cell, i in zip(cells, picks):
        images[cell] = (mnist_images[i], int(mnist_labels[i]))
    return images


# Printing (demo only) 

def print_board(prohibited):
    """Show the full board (for demos only - the robot must not see this)."""
    for r in range(SIZE):
        row = ""
        for c in range(SIZE):
            cell = (r, c)
            if cell in prohibited:
                row += "X "
            elif cell == START:
                row += "S "
            elif cell == EXIT:
                row += "E "
            elif has_alarm(cell, prohibited):
                row += "! "
            else:
                row += ". "
        print(row)



# import random
# from collections import deque

# SIZE = 6
# START = (0, 0)
# EXIT = (5, 5)
# MAX_MOVES = 40
# MOVES = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}


# def neighbors(cell):
#     """Cells directly up, down, left, right of `cell` (inside the grid)."""
#     r, c = cell
#     result = []
#     for dr, dc in MOVES.values():
#         if 0 <= r + dr < SIZE and 0 <= c + dc < SIZE:
#             result.append((r + dr, c + dc))
#     return result


# def has_alarm(cell, prohibited):
#     """A cell has an alarm if any of its neighbors is prohibited."""
#     for n in neighbors(cell):
#         if n in prohibited:
#             return True
#     return False


# def safe_path_exists(prohibited):
#     """BFS from START to EXIT using only cells that are safe and have no alarm."""
#     visited = {START}
#     queue = deque([START])
#     while queue:
#         cell = queue.popleft()
#         if cell == EXIT:
#             return True
#         for n in neighbors(cell):
#             if n not in visited and n not in prohibited and not has_alarm(n, prohibited):
#                 visited.add(n)
#                 queue.append(n)
#     return False


# def broken_rules(prohibited):
#     """Return a list of the CSP rules this layout breaks (empty list = valid)."""
#     broken = []
#     # Rule 1: exactly 3 prohibited cells
#     if len(prohibited) != 3:
#         broken.append("Rule 1: must have exactly 3 prohibited cells")
#     # Rule 2: start, exit, and their neighbors must be safe
#     protected = [START, EXIT] + neighbors(START) + neighbors(EXIT)
#     for cell in protected:
#         if cell in prohibited:
#             broken.append("Rule 2: start/exit or a neighbor is prohibited")
#             break
#     # Rule 3: a safe, alarm-free route from start to exit must exist
#     if not safe_path_exists(prohibited):
#         broken.append("Rule 3: no safe alarm-free path from start to exit")
#     return broken


# def generate_board(seed=None):
#     """Pick 3 random cells until the layout breaks no rules."""
#     rng = random.Random(seed)   # same seed -> same board
#     all_cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
#     while True:
#         prohibited = set(rng.sample(all_cells, 3))
#         if broken_rules(prohibited) == []:
#             return prohibited


# def print_board(prohibited):
#     """Show the full board (for demos only - the robot must not see this)."""
#     for r in range(SIZE):
#         row = ""
#         for c in range(SIZE):
#             cell = (r, c)
#             if cell in prohibited:
#                 row += "X "
#             elif cell == START:
#                 row += "S "
#             elif cell == EXIT:
#                 row += "E "
#             elif has_alarm(cell, prohibited):
#                 row += "! "
#             else:
#                 row += ". "
#         print(row)


# class Simulator:
#     """Plays the game. The robot can only use observe() and move()."""

#     def __init__(self, prohibited):
#         self._prohibited = prohibited   # hidden from the robot
#         self.reset()

#     def reset(self):
#         """Retry the same board from the start."""
#         self.position = START
#         self.moves_used = 0
#         self.status = "running"

#     def observe(self):
#         """What the robot is allowed to know."""
#         return {
#             "position": self.position,
#             "alarm": has_alarm(self.position, self._prohibited),
#             "moves_used": self.moves_used,
#             "status": self.status,
#         }

#     def move(self, direction):
#         """Move one cell: "N", "S", "E" or "W"."""
#         dr, dc = MOVES[direction]
#         r, c = self.position[0] + dr, self.position[1] + dc
#         if not (0 <= r < SIZE and 0 <= c < SIZE):
#             raise ValueError("Cannot move off the grid")

#         self.position = (r, c)
#         self.moves_used += 1

#         if self.position in self._prohibited:
#             self.status = "failure: prohibited cell"
#         elif self.position == EXIT:
#             self.status = "reached exit"
#         elif self.moves_used >= MAX_MOVES:
#             self.status = "failure: timeout"
#         return self.observe()


