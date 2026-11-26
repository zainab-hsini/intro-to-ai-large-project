# %% [markdown]
# # Digit Quest – Logic-Based Chatbot
#
# ## 1. Introduction
#
# The purpose of this part of the project is to develop a logic-based chatbot that allows the user to communicate a mission to the robot using natural language.
#
# The chatbot is responsible for identifying the user's intent, extracting the required parameters, and checking whether the given command is valid. If any information is missing, unclear, or invalid, the chatbot asks the user for clarification before allowing the robot to begin its mission.
#
# Our approach is based on the logic-based chatbot introduced in class, using a knowledge base, preprocessing, pattern matching, and predefined logical rules.
#
# Once a valid mission is identified, the chatbot returns a structured goal that will be used by the navigation and collection components of the project.


# %% [markdown]
# ## 2. Mission Definitions
#
# Before developing the chatbot, we first need to define the
# three missions that the robot can perform. Each mission has
# a different objective, success condition, and scoring rule.
#
# ### 2.1 Exact Total
#
# - Intent: `exact_total`
# - Example command: "Reach the exit with exactly 12 points."
# - Required parameter: Target sum.
# - Validation: The target must be a nonnegative integer.
# - Success: The robot reaches the exit with exactly the
#   requested sum.
# - Failure: The robot exceeds the requested sum.
# - Scoring: Among successful runs, fewer moves is better.
#
# ### 2.2 Fewest Steps
#
# - Intent: `fewest_steps`
# - Example command: "Get to the exit in as few steps as possible."
# - Required parameter: None.
# - Success: The robot reaches the exit safely.
# - Collection: No digit collection is required.
# - Scoring: Fewer moves is better.
#
# ### 2.3 Most Copies of a Digit
#
# - Intent: `most_copies`
# - Example command: "Reach the exit collecting as many ones
#   as possible."
# - Required parameter: Requested digit.
# - Validation: The digit must be an integer between 0 and 9.
# - Success: The robot reaches the exit safely.
# - Scoring: Collecting more copies of the requested digit
#   is better, with fewer moves breaking ties.
#
# ### 2.4 General Conditions
#
# All three missions follow the same game rules, including
# the maximum of 40 moves and the safe-movement requirements.
#
# The chatbot must identify the mission and validate its
# parameters before passing the structured goal to the robot.
# If the command is missing information, ambiguous, or invalid,
# the robot must not start.


# %% [markdown]
# ## 3. Knowledge Base (KB)
#
# We first define a knowledge base containing information
# about the three available missions.
#
# For each mission, we store its name, example command,
# required parameter, success condition, and scoring rule.
#
# We use a dictionary to organize this information so that
# once the chatbot identifies the user's intent, it can
# retrieve the corresponding mission information without
# having to redefine it throughout the code.


# %%
# Define the knowledge base for the three missions

KB = {
    "exact_total": {
        "name": "Exact Total",
        "example": "Reach the exit with exactly 12 points.",
        "parameter": "target",
        "success": "Reach the exit with the requested sum.",
        "failure": "Exceeding the requested sum.",
        "scoring": "Fewer moves is better."
    },

    "fewest_steps": {
        "name": "Fewest Steps",
        "example": "Get to the exit in as few steps as possible.",
        "parameter": None,
        "success": "Reach the exit safely.",
        "collection": "No collection is needed.",
        "scoring": "Fewer moves is better."
    },

    "most_copies": {
        "name": "Most Copies of a Digit",
        "example": "Collect as many ones as possible.",
        "parameter": "digit",
        "success": "Reach the exit safely.",
        "scoring": "More copies is better, with fewer moves breaking ties."
    }
}


# %% [markdown]
# ### Testing the Knowledge Base
#
# To check that our knowledge base is working correctly,
# we retrieve the mission information for the exact total
# mission using its corresponding key.


# %%
print("Mission:", KB["exact_total"]["name"])
print("Example:", KB["exact_total"]["example"])
print("Success:", KB["exact_total"]["success"])
print("Scoring:", KB["exact_total"]["scoring"])


# %% [markdown]
# ## 4. Intent Patterns
#
# Since users may express the same mission in different ways,
# we define a set of patterns for each of the three intents.
#
# These patterns contain words and phrases that are commonly
# associated with each mission.
#
# For example, a user requesting the fewest steps mission
# may use phrases such as "shortest path", "minimum steps",
# or "as few steps as possible".
#
# The chatbot will later compare the user's input against
# these patterns to identify the intended mission.


# %%
# Define patterns for each mission

patterns = {
    "exact_total": [
        "exactly",
        "exact total",
        "exact sum",
        "total of",
        "sum of",
        "target sum",
        "points"
    ],

    "fewest_steps": [
        "fewest steps",
        "as few steps as possible",
        "minimum steps",
        "shortest path",
        "fewest moves",
        "minimum moves",
        "as few moves as possible"
    ],

    "most_copies": [
        "as many",
        "most copies",
        "maximum copies",
        "collect as many",
        "maximize copies",
        "most occurrences"
    ]
}


# %% [markdown]
# ### Testing the Intent Patterns
#
# To check that the patterns are stored correctly,
# we display each intent along with its associated patterns.


# %%
for intent in patterns:
    print("Intent:", intent)
    print("Patterns:", patterns[intent])
    print()


# %% [markdown]
# ## 5. Preprocessing
#
# Before identifying the user's intent, we preprocess the
# input to make the comparison with our patterns easier.
#
# The preprocessing function performs three main steps:
#
# - Converts the input to lowercase.
# - Removes unnecessary punctuation.
# - Removes unnecessary spaces.
#
# However, we preserve negative signs and decimal points
# within numbers because they are needed later when
# validating the mission parameters.
#
# For example, we should not accidentally convert a negative
# target of -5 into a valid target of 5.


# %%
import re

# Preprocess the user's input

def normalize(text):

    # Convert to lowercase
    text = text.lower()

    # Remove unnecessary punctuation
    text = re.sub(r"[^\w\s.+-]", " ", text)

    # Remove periods that are not part of a number
    text = re.sub(r"\.(?!\d)", " ", text)

    # Remove unnecessary spaces
    text = " ".join(text.split())

    return text


# %% [markdown]
# ### Testing the Preprocessing Function
#
# We test the function using different commands containing
# capital letters, punctuation, and unnecessary spaces.
#
# We also include negative and decimal values to make sure
# they are preserved for parameter validation.


# %%
test_inputs = [
    "REACH the exit with EXACTLY 12 points!",
    "Get to the exit   in as few steps as possible.",
    "Collect as many ONES as possible!",
    "Reach the exit with exactly -5 points.",
    "Reach the exit with exactly 2.5 points."
]

for text in test_inputs:
    print("Original:", text)
    print("Processed:", normalize(text))
    print()


# %% [markdown]
# ## 6. Pattern Matching and Scoring
#
# After preprocessing the user's input, we compare it
# with the patterns defined for each intent.
#
# Following the approach introduced in class, we use
# two types of matching:
#
# - Word matching: We add 0.5 for each matching word.
# - Exact phrase matching: We add 2 when a complete
#   pattern appears in the user's command.
#
# Each intent starts with a score of zero. We then
# calculate its total score by going through all its
# associated patterns.
#
# These scores will later help us identify which mission
# is most closely related to the user's command.


# %%
# Calculate the matching score for each intent

def calculate_scores(text):

    text = normalize(text)
    words = text.split()

    scores = {}

    for intent in patterns:

        scores[intent] = 0

        for pattern in patterns[intent]:

            pattern_words = pattern.split()

            # Word matching
            for word in pattern_words:
                if word in words:
                    scores[intent] += 0.5

            # Exact phrase matching
            if " " + pattern + " " in " " + text + " ":
                scores[intent] += 2

    return scores


# %% [markdown]
# ### Testing Pattern Matching and Scoring
#
# To evaluate our scoring function, we use an example
# command from each of the three missions.
#
# We expect the corresponding intent to receive the
# highest score compared to the other two intents.


# %%
test_commands = [
    "Reach the exit with exactly 12 points.",
    "Get to the exit in as few steps as possible.",
    "Collect as many ones as possible."
]

for command in test_commands:

    print("Command:", command)

    scores = calculate_scores(command)

    for intent in scores:
        print(intent, ":", scores[intent])

    print()


# %% [markdown]
# ## 7. Intent Detection
#
# After calculating the matching scores, we need to identify
# which intent represents the user's requested mission.
#
# Following the approach introduced in class, we identify
# the intent with the highest matching score.
#
# However, selecting the highest score alone may lead to
# incorrect results because some patterns share common words.
#
# To avoid this, we introduce additional rules:
#
# - If no complete pattern is matched, the intent is unknown.
# - If complete patterns from multiple missions are matched,
#   the intent is ambiguous.
# - If multiple intents share the highest score, the chatbot
#   asks for clarification.
# - Otherwise, the chatbot accepts the highest-scoring intent
#   if it also has a complete pattern match.
#
# These rules help prevent the robot from starting an
# incorrect mission.


# %%
# Identify the user's intended mission

def detect_intent(text):

    text = normalize(text)
    scores = calculate_scores(text)

    matched_intents = []

    # Check for complete pattern matches
    for intent in patterns:
        for pattern in patterns[intent]:
            if " " + pattern + " " in " " + text + " ":
                matched_intents.append(intent)
                break

    # Rule 1: No recognized mission
    if len(matched_intents) == 0:
        return "unknown"

    # Rule 2: Multiple missions detected
    if len(matched_intents) > 1:
        return "ambiguous"

    # Find the highest score
    highest_score = max(scores.values())

    best_intents = []

    for intent in scores:
        if scores[intent] == highest_score:
            best_intents.append(intent)

    # Rule 3: Multiple intents share the highest score
    if len(best_intents) > 1:
        return "ambiguous"

    # Rule 4: Confirm the highest-scoring intent
    if best_intents[0] in matched_intents:
        return best_intents[0]

    return "ambiguous"


# %% [markdown]
# ### Testing Intent Detection
#
# We test the intent detection function using the three
# mission commands, alternative commands, an unrelated
# command, and a command containing conflicting missions.
#
# The purpose is to check whether the chatbot can identify
# valid missions while also recognizing unknown and
# ambiguous requests.


# %%
intent_tests = [
    "Reach the exit with exactly 12 points.",
    "Get to the exit in as few steps as possible.",
    "Collect as many ones as possible.",
    "Find the shortest path.",
    "Reach a total of 20 points.",
    "Collect as many as you can.",
    "What is the weather today?",
    "Reach exactly 12 points using the shortest path."
]

for command in intent_tests:

    print("Command:", command)
    print("Detected intent:", detect_intent(command))
    print()


# %% [markdown]
# ## 8. Parameter Extraction
#
# After identifying the user's intent, we need to extract
# the numerical parameter required for the mission.
#
# The exact total mission requires a target sum, while
# the most copies mission requires a specific digit.
# The fewest steps mission does not require a parameter.
#
# Since users may express numbers using either numerical
# values or words, we create a dictionary that converts
# written numbers into their corresponding integer values.
#
# We also preserve negative and decimal values so that
# they can be identified and rejected during validation.


# %%
# Dictionary for written numbers

number_words = {
    "zero": 0, "zeros": 0,
    "one": 1, "ones": 1,
    "two": 2, "twos": 2,
    "three": 3, "threes": 3,
    "four": 4, "fours": 4,
    "five": 5, "fives": 5,
    "six": 6, "sixes": 6,
    "seven": 7, "sevens": 7,
    "eight": 8, "eights": 8,
    "nine": 9, "nines": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12
}


# %% [markdown]
# ### Extracting Numbers from the User's Command
#
# We define a function called extract_numbers() to identify
# numerical values and written numbers in the user's input.
#
# The extracted values are stored in a list. Using a list
# allows us to identify whether the user provided one
# parameter, multiple parameters, or no parameter at all.
#
# At this stage, we only extract the values. We check
# whether they are valid in the next section.


# %%
# Extract numerical parameters

def extract_numbers(text):

    text = normalize(text)
    numbers = []

    # Identify numerical values and words
    matches = re.findall(
        r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)|[a-z]+",
        text
    )

    for word in matches:

        # Convert written numbers
        if word in number_words:
            numbers.append(number_words[word])

        # Convert integers
        elif re.fullmatch(r"[+-]?\d+", word):
            numbers.append(int(word))

        # Convert decimal values
        elif re.fullmatch(r"[+-]?(?:\d+\.\d+|\.\d+)", word):
            numbers.append(float(word))

    return numbers


# %% [markdown]
# ### Testing Parameter Extraction
#
# We test the extraction function using commands containing
# integers, written numbers, negative values, decimal
# values, missing parameters, and multiple parameters.
#
# This allows us to check that the function extracts
# the information needed for parameter validation.


# %%
parameter_tests = [
    "Reach exactly 12 points.",
    "Collect as many ones as possible.",
    "Collect as many 7s as possible.",
    "Reach exactly -5 points.",
    "Reach exactly 2.5 points.",
    "Collect as many as you can.",
    "Collect as many twos or threes as possible.",
    "Reach exactly 0 points.",
    "Collect as many zeros as possible."
]

for command in parameter_tests:

    print("Command:", command)
    print("Extracted numbers:", extract_numbers(command))
    print()


# %% [markdown]
# ## 9. Parameter Validation
#
# After extracting the numerical parameters, we need to
# check whether they satisfy the requirements of each mission.
#
# We define the following validation rules:
#
# ### Exact Total
# - The user must provide one target value.
# - The target must be an integer greater than or equal to zero.
#
# ### Fewest Steps
# - No numerical parameter is required.
#
# ### Most Copies of a Digit
# - The user must provide one digit.
# - The digit must be an integer between 0 and 9.
#
# If a parameter is missing, ambiguous, or invalid, the
# chatbot generates a clarification message instead of
# allowing the robot to start its mission.


# %%
# Validate the parameters for each mission

def validate_parameters(intent, text):

    # Fewest steps does not require a parameter
    if intent == "fewest_steps":
        return True, None, None

    numbers = extract_numbers(text)

    # Check for missing parameters
    if len(numbers) == 0:

        if intent == "exact_total":
            return False, None, "What exact total should I reach?"

        elif intent == "most_copies":
            return False, None, "Which digit should I collect?"

    # Check for multiple parameters
    if len(numbers) > 1:
        return False, None, "Please provide only one value."

    value = numbers[0]

    # Validate exact total
    if intent == "exact_total":

        if type(value) != int or value < 0:
            return False, None, "Please enter a nonnegative integer."

        return True, value, None

    # Validate requested digit
    elif intent == "most_copies":

        if type(value) != int or not 0 <= value <= 9:
            return False, None, "Please enter a digit from 0 to 9."

        return True, value, None

    return False, None, "Invalid mission."


# %%
validate_parameters("exact_total", "Reach exactly 12 points.")


# %%
validate_parameters("most_copies", "Collect as many 15s as possible.")


# %% [markdown]
# ### Testing Parameter Validation
#
# To check our validation rules, we test different
# commands containing valid, invalid, missing, and
# multiple parameters.
#
# We also test the boundary values of 0 and 9 to
# make sure they are accepted correctly.


# %%
validation_tests = [
    ("exact_total", "Reach exactly 12 points."),
    ("exact_total", "Reach exactly 0 points."),
    ("exact_total", "Reach exactly -5 points."),
    ("exact_total", "Reach exactly 2.5 points."),
    ("exact_total", "Reach the exact total."),
    ("fewest_steps", "Find the shortest path."),
    ("most_copies", "Collect as many ones as possible."),
    ("most_copies", "Collect as many zeros as possible."),
    ("most_copies", "Collect as many 9s as possible."),
    ("most_copies", "Collect as many 12s as possible."),
    ("most_copies", "Collect as many as you can."),
    ("most_copies", "Collect as many twos or threes as possible.")
]

for intent, command in validation_tests:

    valid, value, message = validate_parameters(intent, command)

    print("Command:", command)
    print("Intent:", intent)
    print("Valid:", valid)
    print("Parameter:", value)
    print("Message:", message)
    print()


# %%
expected_results = [
    True, True, False, False, False, True,
    True, True, True, False, False, False
]

passed = 0

for i, (intent, command) in enumerate(validation_tests):

    valid, value, message = validate_parameters(intent, command)

    if valid == expected_results[i]:
        passed += 1

print("Tests passed:", passed, "/", len(validation_tests))


# %% [markdown]
# ## 10. Logical Rules and Structured Goals
#
# Once the user's intent and parameters have been validated,
# we need to convert the command into a structured goal
# that can be used by the other components of the project.
#
# We use the following logical rules:
#
# - If the intent is exact_total, the goal contains
#   the intent and the requested target sum.
#
# - If the intent is fewest_steps, the goal contains
#   only the intent, since no parameter is required.
#
# - If the intent is most_copies, the goal contains
#   the intent and the requested digit.
#
# - If the intent or parameter is invalid, no structured
#   goal is generated.
#
# By using a dictionary, we provide a consistent output
# that can be accessed by the navigation and collection
# components without having to process the original
# user command again.


# %%
# Generate a structured goal for the robot

def generate_goal(intent, value=None):

    # Mission 1: Exact total
    if intent == "exact_total":

        if type(value) == int and value >= 0:
            return {
                "intent": intent,
                "target": value
            }

    # Mission 2: Fewest steps
    elif intent == "fewest_steps":

        if value is None:
            return {
                "intent": intent
            }

    # Mission 3: Most copies
    elif intent == "most_copies":

        if type(value) == int and 0 <= value <= 9:
            return {
                "intent": intent,
                "digit": value
            }

    # No valid goal
    return None


# %% [markdown]
# ### Testing Structured Goal Generation
#
# We test the function using valid and invalid mission
# parameters to make sure the correct dictionary is
# generated for each mission.
#
# We also check that invalid inputs return None,
# preventing an invalid goal from being passed to
# the robot.


# %%
goal_tests = [
    ("exact_total", 12),
    ("fewest_steps", None),
    ("most_copies", 1),
    ("exact_total", 0),
    ("most_copies", 9),
    ("exact_total", -5),
    ("most_copies", 15),
    ("unknown", None)
]

for intent, value in goal_tests:

    print("Intent:", intent)
    print("Parameter:", value)
    print("Structured goal:", generate_goal(intent, value))
    print()


# %% [markdown]
# ## 11. Main Chatbot Implementation
#
# Now that we have defined and tested the individual
# functions, we combine them into one chatbot function.
#
# The chatbot follows the following process:
#
# 1. Receives a command from the user.
# 2. Identifies the user's intent.
# 3. Checks whether the intent is recognized.
# 4. Extracts and validates the required parameter.
# 5. Asks for clarification if necessary.
# 6. Generates a structured goal.
# 7. Displays the mission information and scoring rule.
# 8. Returns the structured goal to the robot.
#
# The chatbot remembers the selected mission when asking
# for a missing or invalid parameter. This means the user
# does not need to repeat the entire command.
#
# The user can also end the conversation without starting
# a mission by entering "quit" or "bye".


# %%
# Main chatbot function

def chatbot():

    print("Bot: Welcome to Digit Quest!")
    print("Bot: What mission would you like to complete?")

    while True:

        command = input("User: ")

        # Allow the user to exit
        if normalize(command) in ["quit", "bye"]:
            print("Bot: Goodbye!")
            return None

        # Identify the mission
        intent = detect_intent(command)

        if intent == "unknown":
            print("Bot: I could not recognize your mission.")
            print("Bot: Please try another command.")
            continue

        if intent == "ambiguous":
            print("Bot: Please select only one mission.")
            continue

        # Validate the required parameter
        valid, value, message = validate_parameters(
            intent, command
        )

        # Ask for clarification until the parameter is valid
        while not valid:

            print("Bot:", message)

            answer = input("User: ")

            if normalize(answer) in ["quit", "bye"]:
                print("Bot: Goodbye!")
                return None

            valid, value, message = validate_parameters(
                intent, answer
            )

        # Generate the structured goal
        goal = generate_goal(intent, value)

        if goal is None:
            print("Bot: Unable to generate a valid goal.")
            continue

        # Display the accepted mission
        print("Bot: Mission accepted!")
        print("Mission:", KB[intent]["name"])
        print("Success:", KB[intent]["success"])
        print("Scoring:", KB[intent]["scoring"])

        return goal


# %% [markdown]
# ### Running the Chatbot
#
# We now call the chatbot function to test the complete
# interaction between the user and the chatbot.
#
# The returned structured goal is stored in a variable
# called goal, which will later be used to connect the
# chatbot to the other components of the project.


# %%
goal = chatbot()

print("Structured goal:", goal)


# %% [markdown]
# ## 12. Testing and Evaluation
#
# After combining the individual functions, we test the
# complete chatbot process using different user commands.
#
# We include valid commands, alternative wording, missing
# parameters, invalid parameters, unknown commands, and
# commands containing multiple missions.
#
# For each test, we compare the generated structured goal
# with the expected output to evaluate whether the chatbot
# behaves as intended.


# %%
# Test the complete command-processing process

def process_command(command):

    intent = detect_intent(command)

    if intent in ["unknown", "ambiguous"]:
        return None

    valid, value, message = validate_parameters(intent, command)

    if not valid:
        return None

    return generate_goal(intent, value)


# %%
# Test commands and their expected outputs

complete_tests = [
    (
        "Reach exactly 12 points.",
        {"intent": "exact_total", "target": 12}
    ),
    (
        "Find the shortest path.",
        {"intent": "fewest_steps"}
    ),
    (
        "Collect as many ones as possible.",
        {"intent": "most_copies", "digit": 1}
    ),
    (
        "Reach a total of 20 points.",
        {"intent": "exact_total", "target": 20}
    ),
    (
        "Collect as many 7s as possible.",
        {"intent": "most_copies", "digit": 7}
    ),
    ("Reach exactly -5 points.", None),
    ("Reach exactly 2.5 points.", None),
    ("Collect as many 15s as possible.", None),
    ("Collect as many as you can.", None),
    ("Reach the exact total.", None),
    ("What is the weather today?", None),
    ("Reach exactly 12 points using the shortest path.", None)
]

passed = 0

for command, expected in complete_tests:

    result = process_command(command)

    if result == expected:
        passed += 1
        print("PASS:", command)
    else:
        print("FAIL:", command)
        print("Expected:", expected)
        print("Received:", result)

print()
print("Tests passed:", passed, "/", len(complete_tests))


# %% [markdown]
# ## 13. Clarification Dialogue
#
# In this section, we test how the chatbot responds when
# the user provides a command with missing or invalid
# information.
#
# Instead of rejecting the entire mission, the chatbot
# asks the user to provide the required parameter.
#
# The selected intent is maintained throughout the
# clarification process until a valid parameter is provided.
#
# This allows the user to correct their input without
# having to repeat the original mission command.


# %%
# Test the interactive clarification dialogue

goal = chatbot()

print("Final structured goal:", goal)


# %% [markdown]
# ## 14. Team Integration
#
# The chatbot is developed as an independent component
# that communicates with the other parts of the project
# through a structured goal.
#
# The chatbot does not directly access the grid, classify
# digits, calculate paths, or control the robot's movement.
#
# Once a valid mission is accepted, the structured goal
# can be passed to the navigation and collection components.
#
# ### Structured Goal Format
#
# | Intent | Parameter | Description |
# |---|---|---|
# | exact_total | target | Requested total sum |
# | fewest_steps | None | Minimum number of moves |
# | most_copies | digit | Digit to be collected |
#
# The other components can access the selected mission
# using goal["intent"] and retrieve the corresponding
# parameter when required.
#
# If the chatbot returns None, the robot should not
# start its mission.


# %% [markdown]
# ### Connecting the Other Components
#
# The following components will be connected during
# the integration of the complete project.
#
# #### Grid and Simulator
#
# The grid component provides the environment, starting
# position, exit position, obstacles, and digit locations.
#
# #### Digit Classification
#
# The classification component identifies the digits
# that the robot encounters in the environment.
#
# #### Navigation and Collection
#
# The navigation component receives the structured goal
# and determines the appropriate path and collection
# strategy based on the selected mission.
#
# It is also responsible for checking whether the mission
# is achievable within the game constraints.
#
# #### Mission Evaluation
#
# The final result is evaluated according to the success
# conditions and scoring rules of the selected mission.


# %%
# Integration with the other project components

if goal is not None:

    mission = goal["intent"]

    print("Selected mission:", mission)

    if mission == "exact_total":

        target = goal["target"]
        print("Target sum:", target)

    elif mission == "fewest_steps":

        print("Objective: Minimize moves")

    elif mission == "most_copies":

        digit = goal["digit"]
        print("Requested digit:", digit)

    # ---------------------------------------
    # INSERT GRID AND SIMULATOR CONNECTION HERE
    # ---------------------------------------


    # ---------------------------------------
    # INSERT DIGIT CLASSIFIER CONNECTION HERE
    # ---------------------------------------


    # ---------------------------------------
    # INSERT NAVIGATION AND COLLECTION HERE
    # ---------------------------------------


    # ---------------------------------------
    # INSERT MISSION EVALUATION HERE
    # ---------------------------------------

else:

    print("No valid mission. Robot will not start.")


# %% [markdown]
# ## 15. Limitations and Conclusion
#
# ### Limitations
#
# Although the chatbot successfully recognizes and
# processes the three available missions, there are
# some limitations to the current implementation.
#
# - Intent detection depends on predefined patterns
#   and may not recognize unfamiliar expressions.
#
# - Similar words across different missions may
#   result in ambiguous intent detection.
#
# - The chatbot supports individual missions rather
#   than multiple missions within the same command.
#
# - During clarification, the chatbot assumes the
#   user is providing the requested parameter rather
#   than selecting a different mission.
#
# - Complex numerical expressions are not fully supported.
#
# - The chatbot validates the requested parameters but
#   does not determine whether the mission is achievable
#   within the grid.
#
# - Grid interaction, digit classification, navigation,
#   and mission execution require integration with
#   the other project components.


# %% [markdown]
# ### Conclusion
#
# In this part of the project, we developed a rule-based
# chatbot that allows the user to communicate with the
# robot using natural language commands.
#
# The chatbot uses a knowledge base, text normalization,
# intent matching, parameter extraction, validation,
# and logical rules to understand the user's mission.
#
# We also implemented a clarification dialogue to handle
# missing or incorrect information without requiring
# the user to repeat the entire command.
#
# The command-processing function passed all 12
# evaluation tests, and interactive testing demonstrated
# the chatbot's clarification behavior.
#
# The final output is a structured goal that provides
# a consistent connection between the chatbot and
# the other components of the Digit Quest project.


# %%
edge_tests = [
    "Reach exactly 0 points.",
    "Collect as many zeros as possible.",
    "Collect as many nines as possible.",
    "Collect as many twos or threes as possible.",
    "Reach exactly 2.5 points.",
    ""
]

for command in edge_tests:
    print("Command:", command)
    print("Result:", process_command(command))
    print()
