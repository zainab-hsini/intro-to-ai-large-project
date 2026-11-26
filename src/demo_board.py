from board import generate_board, broken_rules, print_board, assign_images, load_mnist_test
from simulator import Simulator


def show(title, prohibited):
    print("\n" + title)
    print_board(prohibited)
    problems = broken_rules(prohibited)
    if problems == []:
        print("-> ACCEPTED (all 3 rules pass)")
    else:
        print("-> REJECTED:", problems)


# 1) One accepted layout and two rejected layouts
board = generate_board(seed=1)
show("Accepted layout (seed=1):", board)
show("Rejected layout A:", {(0, 1), (3, 3), (4, 2)})   # (0,1) touches the start
show("Rejected layout B:", {(2, 0), (2, 2), (2, 4)})   # row 2 blocks every path

# 2) Tests
print("\nTests:")

for seed in range(1000):
    assert broken_rules(generate_board(seed)) == []
print("PASS: 1000 random boards are all valid")

mnist_images, mnist_labels = load_mnist_test()
images = assign_images(board, mnist_images, mnist_labels, seed=1)
assert len(images) == 31
print("PASS: 31 cells have an image")

sim = Simulator(board, images, {"mission": "fewest_steps"})   # X at (0,4), (1,2), (2,4)
obs = sim.observe()
assert "label" not in obs and obs["image"] is None            # start has no image
sim.move("E")                        # (0,1)
obs = sim.move("E")                  # (0,2) is next to X at (1,2)
assert obs["alarm"] == True
assert obs["image"].shape == (28, 28)
print("PASS: alarm rule works and the robot sees the image")

obs = sim.move("S")                  # (1,2) is prohibited
assert obs["status"] == "failure: prohibited cell"
print("PASS: stepping on a prohibited cell fails")

try:
    sim.move("S")
    assert False
except RuntimeError:
    print("PASS: cannot move after the run is over")

sim.reset()
for d in "SSSSEEEEES":               # a safe route to the exit
    obs = sim.move(d)
assert obs["status"] == "success"
print("PASS: robot reaches the exit in", obs["moves_used"], "moves")

# Collecting (tests may peek at the true label; the robot never can)
sim.reset()
sim.move("S")                        # (1,0)
true_label = images[(1, 0)][1]
obs = sim.collect(true_label)
assert obs["score"] == true_label and obs["moves_used"] == 1
print("PASS: correct digit is collected and costs no move")

sim.reset()
sim.move("S")
obs = sim.collect((true_label + 1) % 10)
assert obs["status"] == "failure: wrong digit"
print("PASS: wrong digit ends the run")

# Exact total: reaching the exit with the wrong total fails
sim = Simulator(board, images, {"mission": "exact_total", "target": 100})
for d in "SSSSEEEEES":
    obs = sim.move(d)
assert obs["status"] == "failure: mission not completed"
print("PASS: exact-total mission needs the exact score at the exit")

# Exact total: going over the target fails immediately
sim = Simulator(board, images, {"mission": "exact_total", "target": 0})
sim.move("S")
label = images[(1, 0)][1]
if label > 0:
    obs = sim.collect(label)
    assert obs["status"] == "failure: over target"
    print("PASS: going over the target ends the run")

sim.reset()
obs = sim.stop()
assert obs["status"] == "failure: early stop"
print("PASS: early stop is recorded as a failure")


# """
# demo_board.py - Shows accepted/rejected layouts and tests the simulator.
# Run from the src folder:  python3 demo_board.py
# """

# from board import generate_board, broken_rules, print_board, Simulator


# def show(title, prohibited):
#     print("\n" + title)
#     print_board(prohibited)
#     problems = broken_rules(prohibited)
#     if problems == []:
#         print("-> ACCEPTED (all 3 rules pass)")
#     else:
#         print("-> REJECTED:", problems)


# # 1) One accepted layout and two rejected layouts
# board = generate_board(seed=1)
# show("Accepted layout (seed=1):", board)
# show("Rejected layout A:", {(0, 1), (3, 3), (4, 2)})   # (0,1) touches the start
# show("Rejected layout B:", {(2, 0), (2, 2), (2, 4)})   # row 2 blocks every path

# # 2) Tests
# print("\nTests:")

# for seed in range(1000):
#     assert broken_rules(generate_board(seed)) == []
# print("PASS: 1000 random boards are all valid")

# sim = Simulator(board)               # seed=1 board: X at (0,4), (1,2), (2,4)
# sim.move("E")                        # (0,1)
# obs = sim.move("E")                  # (0,2) is next to X at (1,2)
# assert obs["alarm"] == True
# print("PASS: alarm rule works")

# obs = sim.move("S")                  # (1,2) is prohibited
# assert obs["status"] == "failure: prohibited cell"
# print("PASS: stepping on a prohibited cell fails")

# sim.reset()
# for d in "SSSSEEEEES":               # a safe route to the exit
#     obs = sim.move(d)
# assert obs["status"] == "reached exit"
# print("PASS: robot reaches the exit in", obs["moves_used"], "moves")
