#!/usr/bin/env python
"""
Demo Game CLI Interface

A polished command-line interface for the Space Hulk text adventure game.
This module provides:
- Colorized terminal output
- ASCII art title screen
- Save/load menu system
- Help system
- Complete game loop integration

Usage:
    python -m space_hulk_game.demo_game
    # or after install:
    demo_game
    play_game

Example:
    >>> from space_hulk_game.demo_game import DemoGameCLI
    >>> cli = DemoGameCLI()
    >>> cli.run()
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from colorama import Fore, Style
    from colorama import init as colorama_init
except ImportError:
    # Fallback if colorama not available
    class _DummyColor:
        def __getattr__(self, name):
            return ""

    Fore = Style = _DummyColor()

    def colorama_init(**kwargs):
        pass


from .engine import (
    ContentLoader,
    GameData,
    GameState,
    GameValidator,
    TextAdventureEngine,
)
from .engine.persistence import SaveSystem

# Configure logging
logger = logging.getLogger(__name__)


# ASCII Art Title Screen (Warhammer 40K themed)
TITLE_SCREEN = f"""{Fore.RED}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ███████╗██████╗  █████╗  ██████╗███████╗    ██╗  ██╗██╗   ██╗██╗       ║
║   ██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝    ██║  ██║██║   ██║██║       ║
║   ███████╗██████╔╝███████║██║     █████╗      ███████║██║   ██║██║       ║
║   ╚════██║██╔═══╝ ██╔══██║██║     ██╔══╝      ██╔══██║██║   ██║██║       ║
║   ███████║██║     ██║  ██║╚██████╗███████╗    ██║  ██║╚██████╔╝███████╗  ║
║   ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝  ║
║                                                                           ║
║                     A Text-Based Adventure Game                          ║
║                  In the Grim Darkness of the Far Future                  ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""

SUBTITLE = f"""{Fore.YELLOW}
    "In the grim darkness of the far future, there is only war..."

    You are a Space Marine, boarding a derelict Space Hulk.
    Ancient corridors hold forgotten secrets and unspeakable horrors.
    Your mission: Survive. Explore. Uncover the truth.
{Style.RESET_ALL}"""


class ColorFormatter:
    """
    Handles colorized output for different text types.

    This class provides consistent color coding across the game:
    - Scene descriptions: Cyan
    - Item descriptions: Green
    - NPC dialogue: Yellow
    - Warnings: Red
    - Success messages: Green
    - System messages: Magenta
    """

    @staticmethod
    def scene(text: str) -> str:
        """Format scene description text."""
        return f"{Fore.CYAN}{text}{Style.RESET_ALL}"

    @staticmethod
    def item(text: str) -> str:
        """Format item description text."""
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

    @staticmethod
    def npc(text: str) -> str:
        """Format NPC dialogue text."""
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

    @staticmethod
    def warning(text: str) -> str:
        """Format warning text."""
        return f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}"

    @staticmethod
    def success(text: str) -> str:
        """Format success message text."""
        return f"{Fore.GREEN}{Style.BRIGHT}{text}{Style.RESET_ALL}"

    @staticmethod
    def system(text: str) -> str:
        """Format system message text."""
        return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"

    @staticmethod
    def prompt(text: str) -> str:
        """Format input prompt text."""
        return f"{Fore.WHITE}{Style.BRIGHT}{text}{Style.RESET_ALL}"

    @staticmethod
    def title(text: str) -> str:
        """Format title text."""
        return f"{Fore.RED}{Style.BRIGHT}{text}{Style.RESET_ALL}"


class DemoGameCLI:
    """
    Command-line interface for the Space Hulk demo game.

    This class provides a complete, polished CLI experience including:
    - Title screen and menus
    - Save/load functionality
    - Colorized output
    - Help system
    - Integration with TextAdventureEngine

    Attributes:
        game_dir: Directory containing game YAML files.
        save_dir: Directory for save game files.
        loader: ContentLoader instance.
        save_system: SaveSystem instance.
        engine: TextAdventureEngine instance (set after loading).
        game_data: Loaded GameData instance.
        formatter: ColorFormatter for output styling.

    Examples:
        Run the demo game:
        >>> cli = DemoGameCLI()
        >>> cli.run()

        Run with custom game directory:
        >>> cli = DemoGameCLI(game_dir="path/to/game")
        >>> cli.run()
    """

    def __init__(
        self,
        game_dir: Optional[str] = None,
        save_dir: Optional[str] = None,
    ):
        """
        Initialize the demo game CLI.

        Args:
            game_dir: Directory containing game YAML files.
                     Defaults to "tests/fixtures" for demo.
            save_dir: Directory for save files.
                     Defaults to "saves/" in current directory.
        """
        # Initialize colorama for cross-platform color support
        colorama_init(autoreset=True)

        # Set up directories
        if game_dir is None:
            # Default to test fixtures for demo
            game_dir = str(Path(__file__).parent.parent.parent / "tests" / "fixtures")

        self.game_dir = Path(game_dir)
        self.save_dir = Path(save_dir or "saves")
        self.save_dir.mkdir(exist_ok=True)

        # Initialize components
        self.loader = ContentLoader()
        self.save_system = SaveSystem(str(self.save_dir))
        self.formatter = ColorFormatter()

        # Game state (initialized later)
        self.engine: Optional[TextAdventureEngine] = None
        self.game_data: Optional[GameData] = None

        logger.info(f"DemoGameCLI initialized (game_dir={self.game_dir})")

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def print_title_screen(self) -> None:
        """Display the ASCII art title screen."""
        self.clear_screen()
        print(TITLE_SCREEN)
        print(SUBTITLE)
        print()

    def print_separator(self, char: str = "=", length: int = 79) -> None:
        """Print a separator line."""
        print(self.formatter.system(char * length))

    def show_main_menu(self) -> str:
        """
        Display the main menu and get user choice.

        Returns:
            User's menu choice as a string.
        """
        self.print_separator()
        print(self.formatter.title("\n                          MAIN MENU\n"))
        print(f"  {self.formatter.prompt('1.')} New Game")
        print(f"  {self.formatter.prompt('2.')} Load Game")
        print(f"  {self.formatter.prompt('3.')} Help")
        print(f"  {self.formatter.prompt('4.')} Quit")
        print()
        self.print_separator()

        choice = input(self.formatter.prompt("\nEnter your choice (1-4): ")).strip()
        return choice

    def show_help(self) -> None:
        """Display help information."""
        self.clear_screen()
        self.print_separator()
        print(self.formatter.title("\n                          HELP\n"))
        self.print_separator()
        print()
        print(self.formatter.scene("BASIC COMMANDS:"))
        print(f"  {self.formatter.prompt('look')}              - Examine your surroundings")
        print(
            f"  {self.formatter.prompt('go <direction>')}   - Move in a direction (north, south, east, west)"
        )
        print(f"  {self.formatter.prompt('take <item>')}      - Pick up an item")
        print(f"  {self.formatter.prompt('drop <item>')}      - Drop an item from inventory")
        print(f"  {self.formatter.prompt('use <item>')}       - Use an item")
        print(f"  {self.formatter.prompt('inventory')}        - View your inventory")
        print(f"  {self.formatter.prompt('i')}                - Short for inventory")
        print()
        print(self.formatter.scene("INTERACTION:"))
        print(f"  {self.formatter.prompt('talk to <npc>')}    - Speak with an NPC")
        print(f"  {self.formatter.prompt('examine <thing>')}  - Look at something closely")
        print()
        print(self.formatter.scene("GAME CONTROL:"))
        print(f"  {self.formatter.prompt('help')}             - Show this help")
        print(f"  {self.formatter.prompt('save')}             - Save your game")
        print(f"  {self.formatter.prompt('quit')}             - Quit the game")
        print(f"  {self.formatter.prompt('exit')}             - Exit the game")
        print()
        print(self.formatter.scene("TIPS:"))
        print("  - Read scene descriptions carefully for clues")
        print("  - Talk to NPCs to learn about your surroundings")
        print("  - Examine items before using them")
        print("  - Save frequently!")
        print()
        self.print_separator()
        input(self.formatter.prompt("\nPress Enter to continue..."))

    def load_game_data(self) -> bool:
        """
        Load game data from YAML files.

        Returns:
            True if successful, False otherwise.
        """
        try:
            print(self.formatter.system(f"\nLoading game from: {self.game_dir}"))
            self.game_data = self.loader.load_game(str(self.game_dir))
            print(self.formatter.success(f"✓ Loaded: {self.game_data.title}"))
            print(self.formatter.system(f"  Scenes: {len(self.game_data.scenes)}"))
            print(self.formatter.system(f"  Starting at: {self.game_data.starting_scene}"))

            # Validate game content for playability issues
            print(self.formatter.system("\nValidating game content..."))
            validator = GameValidator(strict_mode=False)
            result = validator.validate_game(self.game_data)

            if result.is_valid():
                print(self.formatter.success("✓ Game validation passed"))
            else:
                print(self.formatter.warning("\n⚠ Warning: Game validation found issues:"))
                print(self.formatter.warning("=" * 79))
                # Display validation summary with proper formatting
                summary_lines = result.get_summary().split("\n")
                for line in summary_lines:
                    if line.strip():
                        print(self.formatter.warning(line))
                print(self.formatter.warning("=" * 79))
                print(self.formatter.warning("\nThe game may not be fully playable."))
                print(self.formatter.system("You can still try to play, but expect issues.\n"))

                response = input(self.formatter.prompt("Continue anyway? (y/n): ")).strip().lower()
                if response not in ["y", "yes"]:
                    print(self.formatter.system("Game loading cancelled."))
                    return False

            return True
        except FileNotFoundError as e:
            print(self.formatter.warning("\n✗ Error: Game files not found"))
            print(self.formatter.warning(f"  {e}"))
            logger.error(f"Game files not found: {e}")
            return False
        except Exception as e:
            print(self.formatter.warning(f"\n✗ Error loading game: {e}"))
            logger.exception("Failed to load game data")
            return False

    def start_new_game(self) -> bool:
        """
        Start a new game.

        Returns:
            True if game started successfully, False otherwise.
        """
        print()
        self.print_separator()
        print(self.formatter.title("\n                       NEW GAME\n"))
        self.print_separator()

        # Load game data if not already loaded
        if self.game_data is None:
            if not self.load_game_data():
                return False

        # Create initial game state
        try:
            initial_state = GameState(
                current_scene=self.game_data.starting_scene,
                visited_scenes={self.game_data.starting_scene},
            )

            # Create engine with custom I/O
            # Extract victory/defeat conditions from game_rules if available
            victory_conditions = set()
            defeat_conditions = set()

            if self.game_data.game_rules:
                victory_conditions = set(self.game_data.game_rules.get("victory_flags", []))
                defeat_conditions = set(self.game_data.game_rules.get("defeat_flags", []))

            self.engine = TextAdventureEngine(
                game_state=initial_state,
                scenes=self.game_data.scenes,
                victory_conditions=victory_conditions,
                defeat_conditions=defeat_conditions,
                output_func=self._colorized_output,
            )

            print(self.formatter.success("\n✓ Game initialized!"))
            print()
            return True

        except Exception as e:
            print(self.formatter.warning(f"\n✗ Error starting game: {e}"))
            logger.exception("Failed to start new game")
            return False

    def show_save_menu(self) -> Optional[str]:
        """
        Show save game menu and get save slot.

        Returns:
            Save slot name or None if cancelled.
        """
        print()
        self.print_separator()
        print(self.formatter.title("\n                       SAVE GAME\n"))
        self.print_separator()

        # List existing saves
        saves = self.save_system.list_saves()
        if saves:
            print(self.formatter.system("\nExisting saves:"))
            for i, save_name in enumerate(saves, 1):
                print(f"  {i}. {save_name}")
            print()

        save_name = input(self.formatter.prompt("Enter save name (or 'cancel'): ")).strip()

        if save_name.lower() in ["cancel", "c", ""]:
            return None

        return save_name

    def show_load_menu(self) -> Optional[str]:
        """
        Show load game menu and get save slot.

        Returns:
            Save slot name or None if cancelled.
        """
        print()
        self.print_separator()
        print(self.formatter.title("\n                       LOAD GAME\n"))
        self.print_separator()

        # List available saves
        saves = self.save_system.list_saves()
        if not saves:
            print(self.formatter.warning("\nNo saved games found."))
            input(self.formatter.prompt("\nPress Enter to continue..."))
            return None

        print(self.formatter.system("\nAvailable saves:"))
        for i, save_name in enumerate(saves, 1):
            print(f"  {i}. {save_name}")
        print()

        choice = input(self.formatter.prompt("Enter save number or name (or 'cancel'): ")).strip()

        if choice.lower() in ["cancel", "c", ""]:
            return None

        # Handle numeric choice
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(saves):
                return saves[idx]

        # Handle name choice
        if choice in saves:
            return choice

        print(self.formatter.warning(f"\nInvalid choice: {choice}"))
        input(self.formatter.prompt("Press Enter to continue..."))
        return None

    def load_saved_game(self) -> bool:
        """
        Load a saved game from file.

        Returns:
            True if loaded successfully, False otherwise.
        """
        save_name = self.show_load_menu()
        if save_name is None:
            return False

        try:
            # Load game data if not already loaded
            if self.game_data is None:
                if not self.load_game_data():
                    return False

            # Load saved state
            print(self.formatter.system(f"\nLoading save: {save_name}..."))
            saved_state = self.save_system.load(save_name)

            # Create engine with loaded state
            # Extract victory/defeat conditions from game_rules if available
            victory_conditions = set()
            defeat_conditions = set()

            if self.game_data.game_rules:
                victory_conditions = set(self.game_data.game_rules.get("victory_flags", []))
                defeat_conditions = set(self.game_data.game_rules.get("defeat_flags", []))

            self.engine = TextAdventureEngine(
                game_state=saved_state,
                scenes=self.game_data.scenes,
                victory_conditions=victory_conditions,
                defeat_conditions=defeat_conditions,
                output_func=self._colorized_output,
            )

            print(self.formatter.success(f"✓ Loaded save: {save_name}"))
            print()
            return True

        except FileNotFoundError:
            print(self.formatter.warning(f"\n✗ Save file not found: {save_name}"))
            input(self.formatter.prompt("Press Enter to continue..."))
            return False
        except Exception as e:
            print(self.formatter.warning(f"\n✗ Error loading save: {e}"))
            logger.exception("Failed to load saved game")
            input(self.formatter.prompt("Press Enter to continue..."))
            return False

    def save_game(self) -> None:
        """Save the current game state."""
        if self.engine is None:
            print(self.formatter.warning("\nNo game in progress to save!"))
            return

        save_name = self.show_save_menu()
        if save_name is None:
            print(self.formatter.system("\nSave cancelled."))
            return

        try:
            self.save_system.save(self.engine.game_state, save_name)
            print(self.formatter.success(f"\n✓ Game saved as: {save_name}"))
        except Exception as e:
            print(self.formatter.warning(f"\n✗ Error saving game: {e}"))
            logger.exception("Failed to save game")

    def _colorized_output(self, text: str) -> None:
        """
        Custom output function with colorization.

        Args:
            text: Text to output.
        """
        # Apply color based on content type (simple heuristic)
        if text.startswith("You"):
            print(self.formatter.scene(text))
        elif "says:" in text.lower() or '"' in text:
            print(self.formatter.npc(text))
        elif text.startswith("✓") or "success" in text.lower():
            print(self.formatter.success(text))
        elif text.startswith("✗") or "error" in text.lower() or "cannot" in text.lower():
            print(self.formatter.warning(text))
        else:
            print(text)

    def run_game_loop(self) -> None:
        """Run the main game loop with custom handling."""
        if self.engine is None:
            print(self.formatter.warning("\nNo game loaded!"))
            return

        # Override some engine output for better formatting
        original_display_welcome = self.engine._display_welcome

        def custom_welcome():
            """Custom welcome message."""
            print()
            self.print_separator()
            print(self.formatter.title(f"\n    {self.game_data.title}"))
            print(self.formatter.scene(f"\n    {self.game_data.description}"))
            print()
            self.print_separator()
            print()

        self.engine._display_welcome = custom_welcome

        # Intercept save commands
        original_input = self.engine.input_func

        def custom_input():
            """Custom input handler for save commands."""
            command = original_input()
            if command.strip().lower() == "save":
                self.save_game()
                return ""  # Return empty to skip engine processing
            return command

        self.engine.input_func = custom_input

        # Run the game
        try:
            self.engine.run()
        except KeyboardInterrupt:
            print(self.formatter.system("\n\nGame interrupted."))
        except Exception as e:
            print(self.formatter.warning(f"\n✗ Game error: {e}"))
            logger.exception("Game loop error")
        finally:
            # Restore original functions
            self.engine._display_welcome = original_display_welcome
            self.engine.input_func = original_input

    def run(self) -> int:
        """
        Run the demo game CLI.

        This is the main entry point for the CLI. It displays the title screen,
        shows the main menu, and handles user choices.

        Returns:
            Exit code (0 for success, 1 for error).
        """
        try:
            # Show title screen
            self.print_title_screen()
            input(self.formatter.prompt("Press Enter to continue..."))

            # Main menu loop
            while True:
                self.clear_screen()
                choice = self.show_main_menu()

                if choice == "1":  # New Game
                    if self.start_new_game():
                        self.run_game_loop()
                    else:
                        input(self.formatter.prompt("\nPress Enter to continue..."))

                elif choice == "2":  # Load Game
                    if self.load_saved_game():
                        self.run_game_loop()
                    # Error handling done in load_saved_game

                elif choice == "3":  # Help
                    self.show_help()

                elif choice == "4":  # Quit
                    print(self.formatter.system("\nThanks for playing!"))
                    print(self.formatter.scene("In the grim darkness of the far future..."))
                    print()
                    return 0

                else:
                    print(self.formatter.warning(f"\nInvalid choice: {choice}"))
                    input(self.formatter.prompt("Press Enter to continue..."))

        except KeyboardInterrupt:
            print(self.formatter.system("\n\nGoodbye!"))
            return 0
        except Exception as e:
            print(self.formatter.warning(f"\n✗ Fatal error: {e}"))
            logger.exception("Fatal error in demo game")
            return 1


def main(args: Optional[list[str]] = None) -> int:
    """
    Main entry point for the demo game.

    Args:
        args: Command-line arguments (for testing).

    Returns:
        Exit code.

    Examples:
        Run from command line:
        $ python -m space_hulk_game.demo_game

        Run with custom game directory:
        $ python -m space_hulk_game.demo_game --game-dir path/to/game
    """
    parser = argparse.ArgumentParser(
        description="Space Hulk Text Adventure Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run with default demo game
  %(prog)s --game-dir game-config/  # Run with custom game directory
  %(prog)s --save-dir my_saves/     # Use custom save directory
  %(prog)s --verbose                # Enable debug logging

For more information, visit: https://github.com/bencan1a/space_hulk_game
        """,
    )

    parser.add_argument(
        "--game-dir",
        type=str,
        help="Directory containing game YAML files (default: tests/fixtures)",
    )

    parser.add_argument(
        "--save-dir",
        type=str,
        help="Directory for save files (default: ./saves)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )

    parsed_args = parser.parse_args(args)

    # Configure logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the game
    cli = DemoGameCLI(
        game_dir=parsed_args.game_dir,
        save_dir=parsed_args.save_dir,
    )

    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
