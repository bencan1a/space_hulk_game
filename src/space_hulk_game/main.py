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
    with open('src/space_hulk_game/config/gamedesign.yaml', encoding='utf-8') as file:
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
        raise Exception(f"An error occurred while running the crew: {e}") from e


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
        raise Exception(f"An error occurred while training the crew: {e}") from e

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SpaceHulkGame().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}") from e

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
        raise Exception(f"An error occurred while testing the crew: {e}") from e


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Space Hulk Game Crew')
    parser.add_argument('--inputs', type=str, help='Input in format key:value (e.g., prompt:Your prompt here)')
    parser.add_argument('command', nargs='?', choices=['run', 'train', 'replay', 'test'],
                       help='Command to execute')

    args = parser.parse_args()

    # If --inputs is provided, parse it and run the crew
    if args.inputs:
        # Parse the inputs format "key:value"
        if ':' in args.inputs:
            key, value = args.inputs.split(':', 1)
            inputs = {key: value}
        else:
            print("Error: --inputs must be in format key:value")
            sys.exit(1)

        # Run the crew with custom inputs
        try:
            print("## Welcome to the Space Hulk Game Crew")
            print('-------------------------------')
            game = SpaceHulkGame().crew().kickoff(inputs=inputs)
            print("\n\n########################")
            print("## Here is the result")
            print("########################\n")
            print("final code for the game:")
            print(game)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}") from e

    # Otherwise, use the command-based approach
    elif args.command == 'train':
        train()
    elif args.command == 'replay':
        replay()
    elif args.command == 'test':
        test()
    else:
        # Default behavior: run with default inputs
        run()
