"""Connect the chatbot goal to the grid simulator."""

import runpy
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from board import assign_images, generate_board, load_mnist_test
from simulator import Simulator


def adapt_goal(chatbot_goal):
    """Translate the chatbot goal to the format expected by Simulator."""
    intent = chatbot_goal["intent"]

    if intent == "exact_total":
        return {"mission": "exact_total", "target": chatbot_goal["target"]}
    if intent == "fewest_steps":
        return {"mission": "fewest_steps"}
    if intent == "most_copies":
        return {"mission": "most_digit", "digit": chatbot_goal["digit"]}

    raise ValueError("Unsupported chatbot mission: " + str(intent))


def main():
    # Run the existing chatbot script and get its final structured goal.
    chatbot_state = runpy.run_path(str(ROOT_DIR / "2_chatbot.py"))
    chatbot_goal = chatbot_state["goal"]
    if chatbot_goal is None:
        print("No valid mission was selected. The environment will not start.")
        return

    # Use a fixed seed so the board and image assignment are repeatable.
    seed = 1
    prohibited = generate_board(seed=seed)
    mnist_images, mnist_labels = load_mnist_test()
    images = assign_images(prohibited, mnist_images, mnist_labels, seed=seed)

    # Convert the goal before giving it to the simulator.
    simulator_goal = adapt_goal(chatbot_goal)
    simulator = Simulator(prohibited, images, simulator_goal)
    print("Environment ready:", simulator.observe())


if __name__ == "__main__":
    main()
