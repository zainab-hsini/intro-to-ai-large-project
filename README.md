# intro-to-ai-large-project
# Digit Quest: Explore Safely, Read Digits, and Complete the User's Mission

**Course:** Introduction to Artificial Intelligence (IDSC-GH 5040) — NYU Abu Dhabi  
**Instructor:** Prof. Julian Barreiro-Gomez  
**Submission Deadline:** December 7, 2026  

---

## 1. Project Overview
**Digit Quest** is an integrated AI agent system where an autonomous robot interprets a user's mission via a rule-based chatbot, explores a partially observable $6 \times 6$ grid world safely using logical inference, classifies handwritten MNIST digits with confidence-calibrated risk thresholds, and navigates to the exit within a strict **40-move budget**.

### Supported Chatbot Missions
1. **Exact Total:** Reach the exit $(5,5)$ with an exact target sum $N$ without overshooting.
2. **Fewest Steps:** Reach the exit $(5,5)$ safely in as few moves as possible.
3. **Most Copies of a Digit:** Reach the exit $(5,5)$ while collecting as many valid instances of a requested digit $d \in \{0,\dots,9\}$ as possible.

---

## 2. Repository & Submission Structure
The repository is modularized so all five team members can develop and test components in parallel without merge conflicts. Before final submission on Brightspace, the root folder will be packaged as `n1_n2_n3_n4_n5`.

```text
intro-to-ai-large-project/
├── README.md                  # Setup instructions, architecture, and reproducibility guide
├── requirements.txt           # Pinned Python dependencies
├── main.py                    # Master entry point (interactive CLI demo & batch evaluation)
├── config.py                  # Shared global constants (grid size, move cap, random seed)
├── src/
│   ├── __init__.py
│   ├── csp_generator.py       # Member 1: CSP board generation & accepted/rejected board visuals
│   ├── simulator.py           # Member 1: Grid environment, alarm sensors, anti-leakage masking
│   ├── chatbot.py             # Member 2: Logic-based intent parser & parameter clarification
│   ├── classifier.py          # Member 3: MNIST classifier & dev-calibrated confidence policy
│   ├── knowledge_base.py      # Member 4: Propositional hazard inference & unit propagation
│   ├── agent.py               # Member 4: A* pathfinding, collection policy & visible adaptation
│   └── evaluator.py           # Member 5: Multi-mission benchmarking, baselines & result plots
├── models/
│   └── mnist_clf.pkl          # Saved pre-trained digit classifier + calibrated threshold
├── tests/                     # Unit tests per module & anti-leakage integration tests
├── results/                   # Generated figures, CSP board examples, and experiment tables
└── slides/
    └── Digit_Quest_Presentation.pdf  # 5-section team presentation deck (3 mins/section)