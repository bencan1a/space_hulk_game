"""
End-to-end tests for the demo game CLI.

This test suite validates the complete workflow:
1. Generate/load game content
2. Initialize CLI and engine
3. Run automated playthrough
4. Save/load functionality
5. Error handling

Tests follow the Arrange-Act-Assert pattern and use mocking
to simulate user input without requiring interactive sessions.
"""

import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import tempfile
import shutil
import sys
from io import StringIO

from space_hulk_game.demo_game import (
    DemoGameCLI,
    ColorFormatter,
    main,
)
from space_hulk_game.engine import (
    GameState,
    ContentLoader,
)


class TestColorFormatter(unittest.TestCase):
    """Test the ColorFormatter utility class."""
    
    def test_scene_formatting(self):
        """Test scene text formatting."""
        formatter = ColorFormatter()
        result = formatter.scene("Test scene")
        self.assertIn("Test scene", result)
    
    def test_item_formatting(self):
        """Test item text formatting."""
        formatter = ColorFormatter()
        result = formatter.item("Test item")
        self.assertIn("Test item", result)
    
    def test_npc_formatting(self):
        """Test NPC text formatting."""
        formatter = ColorFormatter()
        result = formatter.npc("Test NPC")
        self.assertIn("Test NPC", result)
    
    def test_warning_formatting(self):
        """Test warning text formatting."""
        formatter = ColorFormatter()
        result = formatter.warning("Warning!")
        self.assertIn("Warning!", result)
    
    def test_success_formatting(self):
        """Test success text formatting."""
        formatter = ColorFormatter()
        result = formatter.success("Success!")
        self.assertIn("Success!", result)
    
    def test_system_formatting(self):
        """Test system text formatting."""
        formatter = ColorFormatter()
        result = formatter.system("System message")
        self.assertIn("System message", result)
    
    def test_prompt_formatting(self):
        """Test prompt text formatting."""
        formatter = ColorFormatter()
        result = formatter.prompt("Enter: ")
        self.assertIn("Enter: ", result)
    
    def test_title_formatting(self):
        """Test title text formatting."""
        formatter = ColorFormatter()
        result = formatter.title("Title")
        self.assertIn("Title", result)


class TestDemoGameCLI(unittest.TestCase):
    """Test the DemoGameCLI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use test fixtures directory
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        
        # Create temporary save directory
        self.temp_dir = tempfile.mkdtemp()
        self.save_dir = Path(self.temp_dir) / "saves"
        
        # Create CLI instance
        self.cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test CLI initialization."""
        self.assertIsNotNone(self.cli.loader)
        self.assertIsNotNone(self.cli.save_system)
        self.assertIsNotNone(self.cli.formatter)
        self.assertEqual(self.cli.game_dir, self.fixtures_dir)
        self.assertTrue(self.cli.save_dir.exists())
    
    def test_load_game_data_success(self):
        """Test successful game data loading."""
        result = self.cli.load_game_data()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.cli.game_data)
        self.assertGreater(len(self.cli.game_data.scenes), 0)
        self.assertIsNotNone(self.cli.game_data.starting_scene)
    
    def test_load_game_data_missing_directory(self):
        """Test loading from missing directory."""
        cli = DemoGameCLI(
            game_dir="/nonexistent/directory",
            save_dir=str(self.save_dir),
        )
        
        # ContentLoader is lenient and creates a default game even with missing files
        result = cli.load_game_data()
        # It should succeed but with minimal content
        self.assertTrue(result)
        self.assertIsNotNone(cli.game_data)
        # Should have at least the default start scene
        self.assertGreater(len(cli.game_data.scenes), 0)
    
    def test_start_new_game_success(self):
        """Test starting a new game."""
        result = self.cli.start_new_game()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.cli.engine)
        self.assertIsNotNone(self.cli.game_data)
        self.assertEqual(
            self.cli.engine.game_state.current_scene,
            self.cli.game_data.starting_scene
        )
    
    def test_start_new_game_no_data(self):
        """Test starting new game with missing data."""
        cli = DemoGameCLI(
            game_dir="/nonexistent/directory",
            save_dir=str(self.save_dir),
        )
        
        # ContentLoader is lenient, so this should succeed with default game
        result = cli.start_new_game()
        self.assertTrue(result)
        self.assertIsNotNone(cli.engine)
    
    def test_save_game_no_engine(self):
        """Test saving without an active game."""
        with patch('builtins.input', return_value='test_save'):
            self.cli.save_game()
        
        # Should not crash, just warn
        saves = self.cli.save_system.list_saves()
        self.assertEqual(len(saves), 0)
    
    def test_save_and_load_game(self):
        """Test save and load functionality."""
        # Start a new game
        self.cli.start_new_game()
        
        # Modify game state
        self.cli.engine.game_state.game_flags["test_flag"] = True
        self.cli.engine.game_state.game_flags["test_var_42"] = True  # Use flag instead of variable
        
        # Save the game
        save_name = "test_save"
        with patch('builtins.input', return_value=save_name):
            self.cli.save_game()
        
        # Verify save exists
        saves = self.cli.save_system.list_saves()
        self.assertIn(save_name, saves)
        
        # Create new CLI and load the save
        new_cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        with patch('builtins.input', return_value=save_name):
            result = new_cli.load_saved_game()
        
        self.assertTrue(result)
        self.assertIsNotNone(new_cli.engine)
        self.assertTrue(new_cli.engine.game_state.game_flags.get("test_flag"))
        self.assertTrue(new_cli.engine.game_state.game_flags.get("test_var_42"))
    
    def test_show_main_menu(self):
        """Test main menu display."""
        with patch('builtins.input', return_value='1'):
            choice = self.cli.show_main_menu()
        
        self.assertEqual(choice, '1')
    
    def test_show_help(self):
        """Test help display."""
        with patch('builtins.input', return_value=''):
            # Should not crash
            self.cli.show_help()
    
    def test_colorized_output(self):
        """Test colorized output function."""
        # Test different text types
        test_cases = [
            "You are in a room",
            "The NPC says: Hello",
            "✓ Success!",
            "✗ Error!",
            "Regular text",
        ]
        
        for text in test_cases:
            # Should not crash
            self.cli._colorized_output(text)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_title_screen(self, mock_stdout):
        """Test title screen printing."""
        self.cli.print_title_screen()
        output = mock_stdout.getvalue()
        
        # Check for text content in the ASCII art (contains both words)
        # Note: ANSI codes may be present, so check for the actual text
        self.assertIn("Adventure", output)
        self.assertIn("Future", output)
    
    def test_show_save_menu_cancel(self):
        """Test cancelling save menu."""
        with patch('builtins.input', return_value='cancel'):
            result = self.cli.show_save_menu()
        
        self.assertIsNone(result)
    
    def test_show_save_menu_with_name(self):
        """Test save menu with name input."""
        with patch('builtins.input', return_value='my_save'):
            result = self.cli.show_save_menu()
        
        self.assertEqual(result, 'my_save')
    
    def test_show_load_menu_no_saves(self):
        """Test load menu with no saves."""
        with patch('builtins.input', return_value=''):
            result = self.cli.show_load_menu()
        
        self.assertIsNone(result)
    
    def test_show_load_menu_with_saves(self):
        """Test load menu with existing saves."""
        # Create a save first
        self.cli.start_new_game()
        save_name = "test_save"
        with patch('builtins.input', return_value=save_name):
            self.cli.save_game()
        
        # Test loading by name
        with patch('builtins.input', return_value=save_name):
            result = self.cli.show_load_menu()
        
        self.assertEqual(result, save_name)
    
    def test_show_load_menu_numeric_choice(self):
        """Test load menu with numeric choice."""
        # Create a save
        self.cli.start_new_game()
        save_name = "test_save"
        with patch('builtins.input', return_value=save_name):
            self.cli.save_game()
        
        # Test loading by number
        with patch('builtins.input', return_value='1'):
            result = self.cli.show_load_menu()
        
        self.assertEqual(result, save_name)
    
    def test_show_load_menu_invalid_choice(self):
        """Test load menu with invalid choice."""
        # Create a save
        self.cli.start_new_game()
        with patch('builtins.input', return_value='test_save'):
            self.cli.save_game()
        
        # Test invalid choice
        with patch('builtins.input', return_value='invalid'):
            result = self.cli.show_load_menu()
        
        self.assertIsNone(result)


class TestDemoGameIntegration(unittest.TestCase):
    """Integration tests for complete game workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.temp_dir = tempfile.mkdtemp()
        self.save_dir = Path(self.temp_dir) / "saves"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_game_workflow(self):
        """
        Test complete workflow: load → play → save → load → continue.
        
        This is the critical end-to-end test that validates the entire system.
        """
        # Step 1: Create CLI and load game
        cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        success = cli.start_new_game()
        self.assertTrue(success, "Failed to start new game")
        self.assertIsNotNone(cli.engine)
        
        # Step 2: Simulate some game actions
        starting_scene = cli.engine.game_state.current_scene
        
        # Look around
        from space_hulk_game.engine.actions import LookAction
        look_action = LookAction(target=None)
        cli.engine._execute_action(look_action)
        
        # Check inventory
        from space_hulk_game.engine.actions import InventoryAction
        inv_action = InventoryAction()
        cli.engine._execute_action(inv_action)
        
        # Add some state changes
        cli.engine.game_state.game_flags["explored_starting_area"] = True
        cli.engine.game_state.game_flags["turn_count_5"] = True  # Use flag instead of variable
        
        # Step 3: Save the game
        save_name = "integration_test_save"
        with patch('builtins.input', return_value=save_name):
            cli.save_game()
        
        # Verify save exists
        saves = cli.save_system.list_saves()
        self.assertIn(save_name, saves, "Save file not created")
        
        # Step 4: Create new CLI instance and load the save
        new_cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        with patch('builtins.input', return_value=save_name):
            load_success = new_cli.load_saved_game()
        
        self.assertTrue(load_success, "Failed to load saved game")
        self.assertIsNotNone(new_cli.engine)
        
        # Step 5: Verify loaded state matches saved state
        self.assertEqual(
            new_cli.engine.game_state.current_scene,
            starting_scene,
            "Loaded scene doesn't match saved scene"
        )
        self.assertTrue(
            new_cli.engine.game_state.game_flags.get("explored_starting_area"),
            "Loaded flags don't match saved flags"
        )
        self.assertTrue(
            new_cli.engine.game_state.game_flags.get("turn_count_5"),
            "Loaded flags don't match saved flags"
        )
        
        # Step 6: Continue playing with loaded game
        # Execute more actions to ensure engine still works
        look_action = LookAction(target=None)
        new_cli.engine._execute_action(look_action)
        
        # Verify engine is functional
        self.assertIsNotNone(new_cli.engine.game_state)
        self.assertTrue(len(new_cli.engine.scenes) > 0)
    
    def test_automated_playthrough(self):
        """
        Test automated playthrough of the demo game.
        
        This simulates a complete game session with predefined commands.
        """
        cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        # Start new game
        cli.start_new_game()
        
        # Define command sequence for automated playthrough
        commands = [
            "look",
            "inventory",
            "help",
        ]
        
        # Add movement commands based on available exits
        current_scene = cli.engine.scenes[cli.engine.game_state.current_scene]
        if current_scene.exits:
            first_exit = next(iter(current_scene.exits.keys()))
            commands.append(f"go {first_exit}")
            commands.append("look")
        
        # Mock input to return commands in sequence, then quit
        with patch.object(cli.engine, 'input_func', side_effect=commands + ['quit']):
            # Mock confirm quit to return True
            with patch.object(cli.engine, '_confirm_quit', return_value=True):
                # Run the engine (should process all commands then quit)
                cli.engine.run()
        
        # Verify game ran successfully
        self.assertIsNotNone(cli.engine.game_state)
        # Should have visited starting scene
        self.assertTrue(len(cli.engine.game_state.visited_scenes) > 0)
    
    def test_game_with_items_and_npcs(self):
        """Test game interactions with items and NPCs."""
        cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        cli.start_new_game()
        
        current_scene = cli.engine.scenes[cli.engine.game_state.current_scene]
        
        # Test item interactions if available
        if current_scene.items:
            first_item = current_scene.items[0]
            
            # Try to take the item
            from space_hulk_game.engine.actions import TakeAction
            take_action = TakeAction(item_id=first_item.id)
            cli.engine._execute_action(take_action)
            
            # Verify item handling works
            self.assertIsNotNone(cli.engine.game_state)
        
        # Test NPC interactions if available
        if current_scene.npcs:
            first_npc = current_scene.npcs[0]
            
            # Try to talk to NPC
            from space_hulk_game.engine.actions import TalkAction
            talk_action = TalkAction(npc_id=first_npc.id, topic=None)
            cli.engine._execute_action(talk_action)
            
            # Verify NPC handling works
            self.assertIsNotNone(cli.engine.game_state)


class TestMainFunction(unittest.TestCase):
    """Test the main entry point function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.temp_dir = tempfile.mkdtemp()
        self.save_dir = Path(self.temp_dir) / "saves"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_main_help(self):
        """Test main function with --help."""
        with self.assertRaises(SystemExit) as cm:
            main(['--help'])
        
        self.assertEqual(cm.exception.code, 0)
    
    def test_main_with_custom_dirs(self):
        """Test main function with custom directories."""
        # Mock the CLI.run method to immediately return
        with patch.object(DemoGameCLI, 'run', return_value=0):
            exit_code = main([
                '--game-dir', str(self.fixtures_dir),
                '--save-dir', str(self.save_dir),
            ])
        
        self.assertEqual(exit_code, 0)
    
    def test_main_verbose(self):
        """Test main function with verbose logging."""
        with patch.object(DemoGameCLI, 'run', return_value=0):
            exit_code = main([
                '--verbose',
                '--game-dir', str(self.fixtures_dir),
                '--save-dir', str(self.save_dir),
            ])
        
        self.assertEqual(exit_code, 0)
    
    def test_main_quit_immediately(self):
        """Test quitting immediately from main menu."""
        # Simulate user choosing quit (option 4)
        with patch('builtins.input', side_effect=['', '4']):
            exit_code = main([
                '--game-dir', str(self.fixtures_dir),
                '--save-dir', str(self.save_dir),
            ])
        
        self.assertEqual(exit_code, 0)
    
    def test_main_keyboard_interrupt(self):
        """Test handling keyboard interrupt."""
        # Simulate Ctrl+C during title screen
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            exit_code = main([
                '--game-dir', str(self.fixtures_dir),
                '--save-dir', str(self.save_dir),
            ])
        
        self.assertEqual(exit_code, 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the demo game."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.temp_dir = tempfile.mkdtemp()
        self.save_dir = Path(self.temp_dir) / "saves"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_nonexistent_save(self):
        """Test loading a non-existent save file."""
        cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        # Start game to load game data
        cli.start_new_game()
        
        # Try to load non-existent save
        with patch('builtins.input', return_value='nonexistent_save'):
            result = cli.load_saved_game()
        
        self.assertFalse(result)
    
    def test_save_with_permission_error(self):
        """Test handling save permission errors."""
        cli = DemoGameCLI(
            game_dir=str(self.fixtures_dir),
            save_dir=str(self.save_dir),
        )
        
        cli.start_new_game()
        
        # Mock save_system.save to raise PermissionError
        with patch.object(cli.save_system, 'save', side_effect=PermissionError("Access denied")):
            with patch('builtins.input', return_value='test_save'):
                # Should handle error gracefully
                cli.save_game()
        
        # Should not crash
        self.assertIsNotNone(cli.engine)
    
    def test_corrupted_game_data(self):
        """Test handling corrupted game data."""
        # Create CLI with invalid directory
        cli = DemoGameCLI(
            game_dir="/nonexistent",
            save_dir=str(self.save_dir),
        )
        
        # ContentLoader is lenient and creates default game
        result = cli.load_game_data()
        self.assertTrue(result)
        self.assertIsNotNone(cli.game_data)


if __name__ == '__main__':
    unittest.main()
