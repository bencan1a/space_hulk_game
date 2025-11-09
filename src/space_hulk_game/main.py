#!/usr/bin/env python
import sys
import warnings
import yaml

from space_hulk_game.crew import SpaceHulkGame

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def getTopic():
    with open('src/space_hulk_game/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
        examples = yaml.safe_load(file)
    return examples['example4_space_hulk']

def run():
    #litellm._turn_on_debug()
    print("## Welcome to the Space Hulk Game Crew")
    print('-------------------------------')

    # with open('src/space_hulk_game/config/gamedesign.yaml', 'r', encoding='utf-8') as file:
    #     examples = yaml.safe_load(file)

    inputs = {
        'game' :  getTopic()
    }
    
    try:
        game= SpaceHulkGame().crew().kickoff(inputs=inputs)
        print("\n\n########################")
        print("## Here is the result")
        print("########################\n")
        print("final code for the game:")
        print(game)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "game": getTopic()
    }
    try:
        SpaceHulkGame().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SpaceHulkGame().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "game": getTopic()
    }
    try:
        SpaceHulkGame().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)  # type: ignore[call-arg]

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
