"""
Unit tests for quality metrics modules.

Tests PlotMetrics, NarrativeMetrics, PuzzleMetrics, SceneMetrics, and MechanicsMetrics
to ensure they correctly evaluate generated content.
"""

import os
import sys
import unittest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from space_hulk_game.quality import (
    MechanicsMetrics,
    NarrativeMetrics,
    PlotMetrics,
    PuzzleMetrics,
    SceneMetrics,
)


class TestPlotMetrics(unittest.TestCase):
    """Test PlotMetrics evaluation."""

    def test_from_dict_basic(self):
        """Test creating PlotMetrics from a basic dictionary."""
        data = {
            "title": "Test Adventure",
            "setting": "A dark space hulk",
            "themes": ["horror", "survival"],
            "plot": {
                "prologue": ["Opening scene"],
                "act1": ["First act with Branching Path 1: A) choice 1 B) choice 2"],
                "act2": ["Second act with Branching Path 2: A) option A B) option B"],
            },
            "endings": [
                "Good Ending: Victory",
                "Bad Ending: Defeat",
            ],
        }

        metrics = PlotMetrics.from_dict(data)

        self.assertTrue(metrics.has_title)
        self.assertTrue(metrics.has_clear_setting)
        self.assertTrue(metrics.themes_defined)
        self.assertTrue(metrics.has_prologue)
        self.assertTrue(metrics.has_acts)
        self.assertEqual(metrics.branching_paths_count, 2)
        self.assertEqual(metrics.endings_count, 2)
        self.assertGreater(metrics.word_count, 0)

    def test_passes_threshold_success(self):
        """Test that a good plot passes thresholds."""
        # Create a plot with sufficient content to meet the 500 word minimum
        prologue_text = (
            "A team of elite Space Marines from the Ultramarines chapter receives a distress "
            "signal from a derelict space hulk drifting through the void of space in the Segmentum Obscurus. "
            "The hulk, identified as the ancient vessel 'Emperor's Grace', has been missing for over three "
            "centuries after disappearing into a warp storm during the Horus Heresy. Thought lost forever, "
            "its sudden reappearance has drawn the attention of multiple Imperial factions. The Space Marines "
            "are ordered to board the hulk immediately to investigate the mysterious distress signal, retrieve "
            "any valuable technology or lost relics of the Imperium, and determine whether the vessel can be "
            "salvaged or must be destroyed to prevent it from falling into enemy hands. As the boarding team "
            "breaches the outer hull and enters the dark, twisted corridors of the Emperor's Grace, they quickly "
            "discover signs of a terrible conflict that took place centuries ago between the original Imperial "
            "Navy crew and Chaos cultists who had infiltrated the ship before its disappearance."
        )

        act1_text = (
            "The Space Marines begin their methodical exploration of the docking bay, discovering the frozen "
            "corpses of the original crew still at their stations, perfectly preserved by the void. Ancient "
            "technology hums with an eerie power, and the air is thick with the stench of corruption despite "
            "the vacuum of space. As they venture deeper into the hulk, they must navigate through sections "
            "of zero-gravity where the artificial gravity has failed, avoid deadly traps set by long-dead "
            "defenders, and deal with malfunctioning automated defense systems that still see them as threats. "
            "The team splits up to cover more ground efficiently, with one squad investigating the engineering "
            "sections to locate the source of the mysterious signal, while another secures the command bridge "
            "to access the ship's ancient data archives."
        )

        act2_text = (
            "As the Marines penetrate deeper into the hulk's heart, they encounter the first wave of Genestealers, "
            "a horrifying discovery that the hulk is infested with a full brood of these deadly xenos creatures. "
            "The team must fight for their lives in the narrow, claustrophobic corridors, using their superior "
            "tactics and firepower to overcome the alien threat. During a brief respite after a fierce battle, "
            "they discover that they are not alone - a Dark Angels strike force arrived at the hulk days earlier, "
            "searching for something of great importance to their chapter. The Dark Angels are secretive about "
            "their mission, and the Ultramarines must decide whether to trust their brother chapter and combine "
            "forces against the Genestealer threat, or pursue their own objectives independently, knowing that "
            "the Dark Angels may have ulterior motives that conflict with the Ultramarines' mission parameters."
        )

        data = {
            "title": "Space Hulk: The Emperor's Grace",
            "setting": {
                "location": 'Derelict space hulk "Emperor\'s Grace" drifting in Segmentum Obscurus',
                "time": "M41.998, over 300 years after the ship was lost in the warp",
                "environment": "Hostile vacuum environment, corrupted by Chaos and infested with Genestealers",
            },
            "themes": [
                "survival against overwhelming odds",
                "the horror of Chaos corruption",
                "brotherhood and loyalty to the Emperor",
                "the terrible price of victory",
            ],
            "plot": {
                "prologue": [prologue_text],
                "act1": [
                    act1_text,
                    "Branching Path 1: A) Investigate engine room signal source B) Secure command bridge first",
                ],
                "act2": [
                    act2_text,
                    "Branching Path 2: A) Ally with Dark Angels B) Maintain independence",
                ],
                "act3": ["Final confrontation with the source of corruption deep within the hulk"],
            },
            "endings": [
                "Victory Ending: Successfully purge the hulk and escape with valuable technology",
                "Tragic Ending: Team sacrifices themselves to prevent corruption from spreading",
                "Dark Ending: Some marines succumb to corruption, forcing difficult choices about brotherhood",
            ],
        }

        metrics = PlotMetrics.from_dict(data)

        self.assertTrue(
            metrics.passes_threshold(),
            f"Plot should pass threshold. Failures: {metrics.get_failures()}",
        )
        self.assertEqual(len(metrics.get_failures()), 0)
        self.assertGreaterEqual(metrics.get_score(), 8.0)

    def test_fails_insufficient_content(self):
        """Test that a minimal plot fails thresholds."""
        data = {"title": "Short", "plot": {"act1": ["Brief"]}}

        metrics = PlotMetrics.from_dict(data)

        self.assertFalse(metrics.passes_threshold())
        failures = metrics.get_failures()
        self.assertGreater(len(failures), 0)
        self.assertLess(metrics.get_score(), 5.0)


class TestNarrativeMetrics(unittest.TestCase):
    """Test NarrativeMetrics evaluation."""

    def test_from_dict_basic(self):
        """Test creating NarrativeMetrics from a basic dictionary."""
        data = {
            "narrative_map": {
                "start_scene": "intro",
                "scenes": {
                    "intro": {
                        "name": "Introduction",
                        "description": "The journey begins here.",
                        "connections": [{"target": "scene1", "condition": "Go forward"}],
                    },
                    "scene1": {
                        "name": "First Scene",
                        "description": "A dark corridor.",
                        "connections": [{"target": "scene2"}, {"target": "scene3"}],
                    },
                    "scene2": {
                        "name": "Scene Two",
                        "description": "Left path.",
                        "connections": [{"target": "end"}],
                    },
                    "scene3": {
                        "name": "Scene Three",
                        "description": "Right path.",
                        "connections": [{"target": "end"}],
                    },
                    "end": {"name": "Ending", "description": "The end.", "connections": []},
                },
            }
        }

        metrics = NarrativeMetrics.from_dict(data)

        self.assertTrue(metrics.has_start_scene)
        self.assertEqual(metrics.total_scenes, 5)
        self.assertEqual(metrics.scenes_with_descriptions, 5)
        self.assertEqual(metrics.completeness_percentage, 100.0)
        self.assertTrue(metrics.all_connections_valid)
        self.assertFalse(metrics.has_orphaned_scenes)

    def test_detects_orphaned_scenes(self):
        """Test detection of orphaned scenes."""
        data = {
            "narrative_map": {
                "start_scene": "intro",
                "scenes": {
                    "intro": {"description": "Start", "connections": [{"target": "scene1"}]},
                    "scene1": {"description": "First", "connections": []},
                    "orphan": {"description": "Unreachable", "connections": []},
                },
            }
        }

        metrics = NarrativeMetrics.from_dict(data)

        self.assertTrue(metrics.has_orphaned_scenes)
        self.assertIn("orphan", metrics.orphaned_scenes)
        self.assertFalse(metrics.passes_threshold())

    def test_passes_threshold_success(self):
        """Test that a good narrative map passes."""
        data = {
            "narrative_map": {
                "start_scene": "start",
                "scenes": {
                    "start": {"description": "Beginning", "connections": [{"target": "s1"}]},
                    "s1": {"description": "Scene 1", "connections": [{"target": "s2"}]},
                    "s2": {"description": "Scene 2", "connections": [{"target": "s3"}]},
                    "s3": {"description": "Scene 3", "connections": [{"target": "s4"}]},
                    "s4": {"description": "Scene 4", "connections": [{"target": "end"}]},
                    "end": {"description": "Ending", "connections": []},
                },
            }
        }

        metrics = NarrativeMetrics.from_dict(data)

        self.assertTrue(metrics.passes_threshold())
        self.assertEqual(len(metrics.get_failures()), 0)
        self.assertGreaterEqual(metrics.get_score(), 8.0)


class TestPuzzleMetrics(unittest.TestCase):
    """Test PuzzleMetrics evaluation."""

    def test_from_dict_basic(self):
        """Test creating PuzzleMetrics from a basic dictionary."""
        data = {
            "puzzles": [
                {
                    "name": "Door Puzzle",
                    "description": "A locked door requiring a key",
                    "solution": "Find the key in the adjacent room and unlock",
                    "difficulty": "medium",
                    "location": "Main corridor",
                },
                {
                    "name": "Code Lock",
                    "description": "A numerical code lock with hints scattered around",
                    "how_to_solve": "Collect the three numbers and enter them in order",
                    "difficulty": "hard",
                },
            ],
            "artifacts": ["Ancient Key", "Power Cell"],
            "monsters": ["Genestealer"],
            "npcs": ["Wounded Marine"],
        }

        metrics = PuzzleMetrics.from_dict(data)

        self.assertEqual(metrics.total_puzzles, 2)
        self.assertEqual(metrics.puzzles_with_solutions, 2)
        self.assertEqual(metrics.puzzles_with_difficulty, 2)
        self.assertEqual(metrics.puzzles_with_narrative_ties, 2)
        self.assertTrue(metrics.has_artifacts)
        self.assertTrue(metrics.has_monsters)
        self.assertTrue(metrics.has_npcs)

    def test_passes_threshold_success(self):
        """Test that good puzzle design passes."""
        data = {
            "puzzles": [
                {
                    "name": "Puzzle 1",
                    "description": "A complex challenge",
                    "solution": "Use the artifact to unlock the door",
                    "difficulty": "medium",
                },
                {
                    "name": "Puzzle 2",
                    "description": "Another challenge",
                    "solution": "Defeat the monster to proceed",
                    "difficulty": "hard",
                },
            ]
        }

        metrics = PuzzleMetrics.from_dict(data)

        self.assertTrue(metrics.passes_threshold())
        self.assertGreaterEqual(metrics.get_score(), 6.0)


class TestSceneMetrics(unittest.TestCase):
    """Test SceneMetrics evaluation."""

    def test_from_dict_basic(self):
        """Test creating SceneMetrics from a basic dictionary."""
        vivid_desc = (
            "The ancient corridor stretches before you, its twisted metal walls "
            "covered in dark corrosion and flickering with the pale light of failing "
            "lumen strips. Shadows dance across the ominous bulkheads, and the echoing "
            "silence is broken only by the distant screaming of tortured metal and the "
            "whispering of unseen terrors. You can smell the decay and blood-scent "
            "that permeates the stale air."
        )

        data = {
            "scenes": {
                "scene1": {"name": "Corridor", "description": vivid_desc, "tone": "dark horror"},
                "scene2": {
                    "name": "Chamber",
                    "description": vivid_desc + ' "Stay alert," the captain says.',
                    "tone": "dark horror",
                },
                "scene3": {"name": "Bridge", "description": vivid_desc, "tone": "dark horror"},
                "scene4": {"name": "Engine Room", "description": vivid_desc, "tone": "dark horror"},
                "scene5": {"name": "Ending", "description": vivid_desc, "tone": "dark horror"},
            }
        }

        metrics = SceneMetrics.from_dict(data)

        self.assertEqual(metrics.total_scenes, 5)
        self.assertGreater(metrics.scenes_with_vivid_descriptions, 0)
        self.assertGreater(metrics.average_description_length, 50)
        self.assertTrue(metrics.has_sensory_details)

    def test_passes_threshold_success(self):
        """Test that good scene texts pass."""
        long_desc = " ".join(["A dark and twisted ancient corridor with flickering lights"] * 10)

        data = {
            "scenes": {f"scene{i}": {"description": long_desc, "tone": "horror"} for i in range(6)}
        }

        metrics = SceneMetrics.from_dict(data)

        self.assertTrue(metrics.passes_threshold())
        self.assertGreaterEqual(metrics.get_score(), 5.0)


class TestMechanicsMetrics(unittest.TestCase):
    """Test MechanicsMetrics evaluation."""

    def test_from_dict_basic(self):
        """Test creating MechanicsMetrics from a basic dictionary."""
        data = {
            "mechanics": {
                "systems": {
                    "combat": {
                        "description": "Turn-based combat with dice rolls and modifiers",
                        "rules": "Roll 1d20 + modifiers vs target difficulty",
                        "examples": "Attack: 1d20 + 5 vs AC 15",
                    },
                    "movement": {
                        "description": "Grid-based movement with action points",
                        "rules": "Each character has 4 movement points per turn",
                    },
                    "inventory": {
                        "description": "Limited carry capacity with weight system",
                        "rules": "Max 20kg capacity, items have weight values",
                    },
                    "progression": {
                        "description": "XP-based leveling system",
                        "rules": "Gain XP from combat and puzzles, level up at thresholds",
                    },
                },
                "balance": "Difficulty scales moderately, ensuring fair challenge",
            }
        }

        metrics = MechanicsMetrics.from_dict(data)

        self.assertTrue(metrics.has_combat_system)
        self.assertTrue(metrics.has_movement_system)
        self.assertTrue(metrics.has_inventory_system)
        self.assertTrue(metrics.has_progression_system)
        self.assertGreaterEqual(metrics.total_systems, 4)
        self.assertTrue(metrics.has_balance_notes)

    def test_passes_threshold_success(self):
        """Test that good mechanics pass."""
        data = {
            "mechanics": {
                "combat_system": {
                    "description": "Detailed combat with multiple phases and special abilities. "
                    "Players roll dice to determine hits and damage. "
                    "Critical hits occur on natural 20s.",
                    "rules": "Must roll higher than enemy AC to hit. Damage is weapon die + strength modifier.",
                },
                "movement_system": {
                    "description": "Characters can move and take actions. Movement is measured in grid squares.",
                    "rules": "Standard move is 6 squares per turn. Difficult terrain costs double.",
                },
                "inventory_system": {
                    "description": "Limited slots for carrying items. Each item has a weight and size.",
                    "rules": "Maximum 10 item slots. Heavy items take 2 slots.",
                },
                "health_system": {
                    "description": "Hit points determine survivability. Healing is available via items.",
                    "rules": "Start with 20 HP. Medkits restore 1d6+2 HP.",
                },
            }
        }

        metrics = MechanicsMetrics.from_dict(data)

        self.assertTrue(metrics.passes_threshold())
        self.assertGreaterEqual(metrics.get_score(), 7.0)


class TestMetricsIntegration(unittest.TestCase):
    """Test metrics integration and common patterns."""

    def test_to_dict_all_metrics(self):
        """Test that all metrics can be converted to dict."""
        metrics_classes = [
            PlotMetrics,
            NarrativeMetrics,
            PuzzleMetrics,
            SceneMetrics,
            MechanicsMetrics,
        ]

        for metrics_class in metrics_classes:
            metrics = metrics_class()
            result = metrics.to_dict()

            # All metrics should have these keys
            self.assertIn("passes_threshold", result)
            self.assertIn("score", result)
            self.assertIn("failures", result)

            # Check types
            self.assertIsInstance(result["passes_threshold"], bool)
            self.assertIsInstance(result["score"], float)
            self.assertIsInstance(result["failures"], list)

    def test_score_range(self):
        """Test that scores are always in valid range."""
        metrics_classes = [
            PlotMetrics,
            NarrativeMetrics,
            PuzzleMetrics,
            SceneMetrics,
            MechanicsMetrics,
        ]

        for metrics_class in metrics_classes:
            metrics = metrics_class()
            score = metrics.get_score()

            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 10.0)


if __name__ == "__main__":
    unittest.main()
