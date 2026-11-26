# Connection Guide

## What was inspected

- `src/board.py` provides:
  - `generate_board(seed=None)`, which returns a set of prohibited cells.
  - `load_mnist_test()`, which returns the test images and labels.
  - `assign_images(prohibited, mnist_images, mnist_labels, seed=None)`, which
    returns the cell-to-image mapping.
- `src/simulator.py` provides `Simulator(prohibited, images, goal)`. Its
  `observe()` method returns the current position, alarm reading, image (if
  present), move count, score, collected digits, and status.
- `src/app.py` constructs a simulator with a `mission` goal and uses
  `"most_digit"` for the digit-collection mission.
- `src/demo_board.py` demonstrates how the board, images, and simulator work
  together.
- `2_chatbot.py` provides `chatbot()` for interactive dialogue and
  `process_command(command)` for processing a single command. A valid goal
  uses the key `intent`, with `target` for `exact_total` and `digit` for
  `most_copies`. Its embedded demo and test code has been commented out so
  running it through `main.py` does not execute those checks.

No existing files were changed.

## Data flow

```text
Run main.py from the repository root
    |
    v
runpy executes 2_chatbot.py
    |  (one interactive chatbot session; tests are commented out)
    v
Read the final chatbot goal
    |
    +--> translate its intent and parameter names
    |
    +--> generate_board(seed=1)
    +--> load_mnist_test()
    +--> assign_images(board, images, labels, seed=1)
                    |
                    v
       Simulator(prohibited, images, simulator_goal)
                    |
                    v
             simulator.observe()
```

## `main.py` walkthrough

1. **Standard-library imports:** `runpy` executes the existing chatbot script,
   `sys` lets Python find the Task 1 modules, and `Path` builds paths relative
   to `main.py`.
2. **Repository and source paths:** `ROOT_DIR` is the repository root.
   `SRC_DIR` points to its `src/` directory. That directory is added to
   `sys.path` because `simulator.py` imports `board` as a top-level module.
3. **Task 1 imports:** `generate_board`, `load_mnist_test`, and
   `assign_images` create the environment inputs; `Simulator` manages the
   environment state.
4. **`adapt_goal(chatbot_goal)`:** The chatbot returns a dictionary keyed by
   `intent`, while the simulator expects `mission`. This function maps
   `exact_total` and `fewest_steps` directly and maps `most_copies` to the
   simulator's `most_digit` name. It carries across the relevant `target` or
   `digit`. An unsupported intent raises an error rather than being silently
   accepted.
5. **Run the chatbot:** `runpy.run_path()` executes `2_chatbot.py` and returns
   its top-level variables in a dictionary. The script's final `goal` is the
   goal used by `main.py`. If it is `None`, the environment is not started.
6. **Create the environment:** A fixed seed makes board and image assignment
   reproducible. The functions from `board.py` produce the prohibited cells
   and image mapping; these, along with the translated goal, initialize the
   simulator.
7. **Show the initial observation:** `simulator.observe()` confirms that the
   goal and grid environment were connected. The `if __name__ == "__main__"`
   guard runs `main()` when this file is executed directly.

## Running the connection

From the repository root, run:

```bash
python main.py
```

The chatbot's embedded tests are commented out. Running `main.py` starts one
interactive chatbot session; its resulting goal is used to configure the
simulator.
