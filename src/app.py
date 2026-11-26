import streamlit as st

from board import generate_board, assign_images, load_mnist_test, has_alarm, SIZE, EXIT
from simulator import Simulator


@st.cache_data
def get_mnist():
    """Load MNIST only once (Streamlit re-runs the script on every click)."""
    return load_mnist_test()


def new_game(seed, goal):
    """Build a board + images and start a fresh simulator."""
    prohibited = generate_board(seed)
    mnist_images, mnist_labels = get_mnist()
    images = assign_images(prohibited, mnist_images, mnist_labels, seed)
    st.session_state.sim = Simulator(prohibited, images, goal)
    st.session_state.seen = {}      # {cell: alarm} - only what the robot observed
    remember(st.session_state.sim.observe())


def remember(obs):
    """Store the alarm reading of the cell the robot is standing on."""
    st.session_state.seen[obs["position"]] = obs["alarm"]


def draw_grid(sim, show_hidden):
    """Emoji grid: robot, exit, visited cells (green = no alarm, yellow = alarm)."""
    rows = []
    for r in range(SIZE):
        row = ""
        for c in range(SIZE):
            cell = (r, c)
            if cell == sim.position:
                row += "🤖"
            elif show_hidden and cell in sim._prohibited:   # demo only
                row += "💣"
            elif cell == EXIT:
                row += "🏁"
            elif cell in st.session_state.seen:
                row += "🟨" if st.session_state.seen[cell] else "🟩"
            else:
                row += "⬜"
        rows.append(row)
    st.markdown("<div style='font-size:40px; line-height:1.1'>" + "<br>".join(rows) + "</div>",
                unsafe_allow_html=True)
    st.caption("🟩 visited, no alarm   🟨 visited, alarm   ⬜ unknown")


# Sidebar: game settings
st.title("Digit Quest")

seed = st.sidebar.number_input("Board seed", min_value=0, value=1)
mission = st.sidebar.selectbox("Mission", ["fewest_steps", "exact_total", "most_digit"])
goal = {"mission": mission}
if mission == "exact_total":
    goal["target"] = st.sidebar.number_input("Target total", min_value=0, value=12)
if mission == "most_digit":
    goal["digit"] = st.sidebar.number_input("Digit to collect", min_value=0, max_value=9, value=1)
show_hidden = st.sidebar.checkbox("Show hidden bombs (demo only)")

if st.sidebar.button("New game") or "sim" not in st.session_state:
    new_game(seed, goal)

sim = st.session_state.sim
left, right = st.columns([3, 2])

# Controls (right side) 
with right:
    st.subheader("Controls")
    try:
        c1, c2, c3, c4 = st.columns(4)
        for col, d in zip([c1, c2, c3, c4], ["N", "S", "E", "W"]):
            if col.button(d):
                remember(sim.move(d))

        digit = st.number_input("Digit you see", min_value=0, max_value=9, value=0)
        if st.button("Collect"):
            sim.collect(digit)
        if st.button("Stop early"):
            sim.stop()
    except (ValueError, RuntimeError) as error:
        st.warning(str(error))

    if st.button("Reset (same board)"):
        sim.reset()
        st.session_state.seen = {}
        remember(sim.observe())

    obs = sim.observe()
    st.write("**Status:**", obs["status"])
    st.write("**Moves:**", obs["moves_used"], "/ 40")
    st.write("**Score:**", obs["score"], "  **Collected:**", obs["collected"])
    st.write("**Goal:**", sim.goal)

# Grid + current image (left side)
with left:
    draw_grid(sim, show_hidden)
    if obs["image"] is not None:
        st.image(obs["image"], width=120, caption="Image in this cell")