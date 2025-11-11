"""
Unit tests for quality evaluator implementations.

Tests QualityScore, QualityEvaluator base class, and all 5 specific evaluators
(Plot, NarrativeMap, Puzzle, Scene, Mechanics) to ensure they correctly
evaluate generated content and return standardized QualityScore results.
"""

import os
import sys
import unittest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from space_hulk_game.quality import (
    MechanicsEvaluator,
    NarrativeMapEvaluator,
    PlotEvaluator,
    PuzzleEvaluator,
    QualityScore,
    SceneEvaluator,
)


class TestQualityScore(unittest.TestCase):
    """Test QualityScore data class."""

    def test_create_score(self):
        """Test creating a QualityScore."""
        score = QualityScore(
            score=8.5, passed=True, feedback="Good quality", details={"word_count": 650}
        )

        self.assertEqual(score.score, 8.5)
        self.assertTrue(score.passed)
        self.assertEqual(score.feedback, "Good quality")
        self.assertEqual(score.details["word_count"], 650)

    def test_score_validation(self):
        """Test that score is validated to be in range 0-10."""
        # Valid scores
        QualityScore(0.0, True, "Min")
        QualityScore(10.0, True, "Max")
        QualityScore(5.5, False, "Mid")

        # Invalid scores
        with self.assertRaises(ValueError):
            QualityScore(-1.0, False, "Too low")

        with self.assertRaises(ValueError):
            QualityScore(11.0, True, "Too high")

    def test_to_dict(self):
        """Test converting score to dictionary."""
        score = QualityScore(7.5, True, "Good", {"key": "value"})
        d = score.to_dict()

        self.assertEqual(d["score"], 7.5)
        self.assertEqual(d["passed"], True)
        self.assertEqual(d["feedback"], "Good")
        self.assertEqual(d["details"]["key"], "value")

    def test_from_dict(self):
        """Test creating score from dictionary."""
        data = {"score": 6.0, "passed": False, "feedback": "Needs work", "details": {"issues": 3}}
        score = QualityScore.from_dict(data)

        self.assertEqual(score.score, 6.0)
        self.assertFalse(score.passed)
        self.assertEqual(score.feedback, "Needs work")
        self.assertEqual(score.details["issues"], 3)

    def test_get_failures(self):
        """Test extracting failures from details."""
        score = QualityScore(4.0, False, "Failed", {"failures": ["Issue 1", "Issue 2"]})
        failures = score.get_failures()

        self.assertEqual(len(failures), 2)
        self.assertIn("Issue 1", failures)
        self.assertIn("Issue 2", failures)

    def test_get_summary(self):
        """Test getting formatted summary."""
        score = QualityScore(8.0, True, "Good", {"word_count": 500, "failures": []})
        summary = score.get_summary()

        self.assertIn("8.0/10.0", summary)
        self.assertIn("PASS", summary)
        self.assertIn("Good", summary)
        self.assertIn("word_count", summary)


class TestPlotEvaluator(unittest.TestCase):
    """Test PlotEvaluator implementation."""

    def setUp(self):
        """Set up test evaluator."""
        self.evaluator = PlotEvaluator(pass_threshold=6.0)

    def test_evaluator_initialization(self):
        """Test evaluator initializes correctly."""
        self.assertEqual(self.evaluator.pass_threshold, 6.0)

    def test_evaluate_good_plot(self):
        """Test evaluating a good quality plot."""
        # Create comprehensive plot YAML with sufficient word count
        plot_yaml = """
title: "Space Hulk: The Emperor's Grace"
setting:
  location: "Derelict space hulk drifting in Segmentum Obscurus"
  time: "M41.998, over 300 years after the ship was lost"
  environment: "Dark, twisted corridors filled with ancient technology and corruption"
themes:
  - horror
  - survival
  - duty
plot:
  prologue: |
    A team of elite Space Marines from the Ultramarines chapter receives a distress
    signal from a derelict space hulk. The hulk, identified as the ancient vessel
    'Emperor's Grace', has been missing for over three centuries after disappearing
    into a warp storm during the Horus Heresy. The Space Marines are ordered to board
    the hulk immediately to investigate the mysterious distress signal and retrieve
    any valuable technology or lost relics of the Imperium.
  act1: |
    The Space Marines begin their methodical exploration of the docking bay, discovering
    the frozen corpses of the original crew still at their stations. Ancient technology
    hums with an eerie power, and the air is thick with the stench of corruption. As they
    venture deeper into the hulk, they must navigate through sections of zero-gravity where
    the artificial gravity has failed, avoid deadly traps set by long-dead defenders, and
    deal with malfunctioning automated defense systems.

    Branching Path 1:
    A) Split the team - one squad investigates engineering, another secures the bridge
    B) Keep the team together for maximum firepower and safety
  act2: |
    As the Marines penetrate deeper into the hulk's heart, they encounter the first wave
    of Genestealers, a horrifying discovery that the hulk is infested with a full brood
    of these deadly xenos creatures. The team must fight for their lives in the narrow,
    claustrophobic corridors. During a brief respite after a fierce battle, they discover
    that they are not alone - a Dark Angels strike force arrived at the hulk days earlier.

    Branching Path 2:
    A) Trust the Dark Angels and combine forces against the Genestealer threat
    B) Pursue objectives independently, suspicious of Dark Angels' ulterior motives
endings:
  - name: "Victory"
    description: "The Space Marines successfully purge the Genestealer infestation and recover ancient technology"
    type: "victory"
  - name: "Pyrrhic Victory"
    description: "The team destroys the hulk but at great cost, with many casualties"
    type: "victory"
  - name: "Defeat"
    description: "Overwhelmed by Genestealers, the team is lost"
    type: "defeat"
"""

        result = self.evaluator.evaluate(plot_yaml)

        self.assertIsInstance(result, QualityScore)
        self.assertGreaterEqual(result.score, 6.0)
        self.assertTrue(result.passed)
        self.assertIn("details", result.to_dict())

    def test_evaluate_poor_plot(self):
        """Test evaluating a poor quality plot."""
        plot_yaml = """
title: "Test"
plot:
  act1: "Something happens"
"""

        result = self.evaluator.evaluate(plot_yaml)

        self.assertIsInstance(result, QualityScore)
        self.assertLess(result.score, 6.0)
        self.assertFalse(result.passed)
        self.assertGreater(len(result.get_failures()), 0)

    def test_evaluate_invalid_yaml(self):
        """Test evaluating invalid YAML."""
        invalid_yaml = "{ invalid yaml: [unclosed"

        result = self.evaluator.evaluate(invalid_yaml)

        self.assertEqual(result.score, 0.0)
        self.assertFalse(result.passed)
        self.assertIn("error", result.details)

    def test_evaluate_yaml_with_colon_in_value(self):
        """Test evaluating YAML with unquoted colons in values (common LLM output)."""
        plot_yaml = """title: Space Hulk: Derelict of the Damned
setting:
  location: A derelict Space Hulk
  time: Unknown
themes:
  - Horror
  - Action
plot:
  prologue:
    - Opening scene
  act1:
    - Branching Path 1: A) Split team B) Stay together
  act2:
    - Branching Path 2: A) Trust allies B) Go alone
endings:
  - name: Victory
    type: victory
  - name: Defeat
    type: defeat
"""

        # Should successfully parse after automatic fix
        result = self.evaluator.evaluate(plot_yaml)

        self.assertIsInstance(result, QualityScore)
        self.assertGreater(result.score, 0.0)  # Should not be 0 (parse error)
        self.assertTrue(result.details.get("has_title"))
        self.assertEqual(result.details.get("branching_paths_count"), 2)

    def test_generate_detailed_feedback(self):
        """Test generating detailed feedback."""
        plot_yaml = """
title: "Test Plot"
setting: "A dark place"
themes: ["horror"]
plot:
  prologue: "The story begins with a dark and stormy night in the derelict space hulk."
"""

        feedback = self.evaluator.generate_detailed_feedback(plot_yaml)

        self.assertIsInstance(feedback, str)
        self.assertIn("Quality Score", feedback)
        self.assertIn("Status", feedback)


class TestNarrativeMapEvaluator(unittest.TestCase):
    """Test NarrativeMapEvaluator implementation."""

    def setUp(self):
        """Set up test evaluator."""
        self.evaluator = NarrativeMapEvaluator(pass_threshold=6.0)

    def test_evaluate_good_narrative(self):
        """Test evaluating a good quality narrative map."""
        narrative_yaml = """
scenes:
  scene_1:
    title: "Docking Bay Alpha"
    description: "A vast, dimly lit docking bay with frozen corpses at their stations"
    connections:
      - target: scene_2
        description: "North corridor to engineering"
  scene_2:
    title: "Engineering Deck"
    description: "Humming machinery and flickering lights"
    connections:
      - target: scene_3
        description: "Upper level to bridge"
  scene_3:
    title: "Command Bridge"
    description: "Ancient control systems still operational"
    connections:
      - target: scene_4
        description: "Lower decks"
  scene_4:
    title: "Crew Quarters"
    description: "Abandoned living spaces"
    connections:
      - target: scene_5
        description: "Maintenance tunnels"
  scene_5:
    title: "Generator Room"
    description: "Massive power generators"
    connections:
      - target: scene_1
        description: "Return to docking bay"
"""

        result = self.evaluator.evaluate(narrative_yaml)

        self.assertIsInstance(result, QualityScore)
        self.assertGreaterEqual(result.score, 6.0)
        self.assertTrue(result.passed)

    def test_evaluate_orphaned_scenes(self):
        """Test detecting orphaned scenes."""
        narrative_yaml = """
scenes:
  scene_1:
    title: "Start"
    description: "Starting location"
    connections:
      - target: scene_2
  scene_2:
    title: "Middle"
    description: "Connected scene"
    connections: []
  scene_3:
    title: "Orphan"
    description: "Unreachable scene"
    connections: []
"""

        result = self.evaluator.evaluate(narrative_yaml)

        # May not pass due to orphaned scene
        self.assertIn("orphaned_scenes", result.details)


class TestPuzzleEvaluator(unittest.TestCase):
    """Test PuzzleEvaluator implementation."""

    def setUp(self):
        """Set up test evaluator."""
        self.evaluator = PuzzleEvaluator(pass_threshold=6.0)

    def test_evaluate_good_puzzles(self):
        """Test evaluating good quality puzzles."""
        puzzle_yaml = """
puzzles:
  - id: "puzzle_1"
    name: "Access Code Terminal"
    description: "Ancient terminal requires access code"
    solution: "Code found in captain's log dataslate"
    narrative_tie: "Unlocks access to bridge systems"
    difficulty: "medium"
  - id: "puzzle_2"
    name: "Power Routing"
    description: "Reroute power to life support"
    solution: "Use engineering panel to redirect power flow"
    narrative_tie: "Restores breathable atmosphere"
    difficulty: "hard"
"""

        result = self.evaluator.evaluate(puzzle_yaml)

        self.assertIsInstance(result, QualityScore)
        self.assertGreaterEqual(result.score, 6.0)
        self.assertTrue(result.passed)


class TestSceneEvaluator(unittest.TestCase):
    """Test SceneEvaluator implementation."""

    def setUp(self):
        """Set up test evaluator."""
        self.evaluator = SceneEvaluator(pass_threshold=6.0)

    def test_evaluate_good_scenes(self):
        """Test evaluating good quality scene texts."""
        scene_yaml = """
scenes:
  scene_1:
    description: |
      The docking bay stretches before you, a vast cathedral of rust and shadows.
      Ancient machinery looms overhead, covered in frost and grime. The air tastes
      of metal and decay. Frozen corpses stand at their stations like grotesque
      statues, their faces locked in eternal screams. Warning lights flicker red
      across the walls, casting everything in a hellish glow.
  scene_2:
    description: |
      You enter the engineering deck, where massive generators pulse with eerie
      green light. The sound of humming machinery fills your ears. Strange symbols
      glow on the control panels, pulsing in rhythm with your heartbeat. The floor
      vibrates beneath your feet. A cold wind blows from the ventilation shafts.
  scene_3:
    description: |
      The command bridge is a monument to lost glory. Throne-like command chairs
      face cracked viewscreens showing only static. Dust covers every surface.
      Your footsteps echo in the silence. Ancient cogitators click and whir,
      processing data from centuries past.
  scene_4:
    description: |
      Crew quarters line both sides of the corridor. Personal effects scatter
      the floor - photos, medals, prayer beads. The smell of decay permeates
      everything. Bunks are still made, waiting for crew that will never return.
  scene_5:
    description: |
      The generator room thrums with power. Massive turbines spin endlessly,
      their purpose long forgotten. Coolant pipes hiss and drip. Control panels
      display warnings in dead languages. The heat is oppressive, making you sweat.
  scene_6:
    description: |
      A maintenance tunnel winds through the ship's skeleton. Exposed wiring
      crackles with electricity. The walls press in close. You must crouch to
      move forward. Distant sounds echo - metallic screeches, inhuman howls.
"""

        result = self.evaluator.evaluate(scene_yaml)

        self.assertIsInstance(result, QualityScore)
        # Should pass with vivid descriptions and sensory details
        self.assertGreaterEqual(result.score, 5.0)


class TestMechanicsEvaluator(unittest.TestCase):
    """Test MechanicsEvaluator implementation."""

    def setUp(self):
        """Set up test evaluator."""
        self.evaluator = MechanicsEvaluator(pass_threshold=6.0)

    def test_evaluate_good_mechanics(self):
        """Test evaluating good quality game mechanics."""
        mechanics_yaml = """
health_system:
  description: |
    Players have health points representing physical condition. Health ranges
    from 0 (dead) to 100 (full health). Taking damage reduces health. Healing
    items and rest restore health. At 0 health, the game ends in defeat.
inventory_system:
  description: |
    Players can carry up to 10 items. Items include weapons, tools, keycards,
    and consumables. Items can be picked up from scenes and used to solve
    puzzles or overcome obstacles. Some items are required to progress.
combat_system:
  description: |
    Combat is turn-based. Players choose actions: attack, defend, use item, or
    flee. Enemies have health and attack values. Success depends on weapon type
    and player choices. Defeating enemies may yield items or access to new areas.
movement_system:
  description: |
    Players navigate between connected scenes. Each scene has a description,
    available items, NPCs, and exits. Some areas are locked until puzzles are
    solved or items are found. The map reveals as players explore.
"""

        result = self.evaluator.evaluate(mechanics_yaml)

        self.assertIsInstance(result, QualityScore)
        self.assertGreaterEqual(result.score, 6.0)
        self.assertTrue(result.passed)


class TestEvaluatorIntegration(unittest.TestCase):
    """Integration tests for evaluator system."""

    def test_all_evaluators_return_quality_score(self):
        """Test that all evaluators return QualityScore instances."""
        # Minimal valid content for each type
        plot_yaml = "title: Test\nsetting: Place\nthemes: [horror]\nplot: {act1: story}\nendings: [{name: end, type: victory}]"
        narrative_yaml = "scenes:\n  s1:\n    description: desc\n    connections: []"
        puzzle_yaml = (
            "puzzles:\n  - id: p1\n    solution: yes\n    narrative_tie: yes\n    difficulty: easy"
        )
        scene_yaml = "scenes:\n  s1:\n    description: A vivid description"
        mechanics_yaml = "systems:\n  combat:\n    description: How combat works"

        evaluators = [
            PlotEvaluator(),
            NarrativeMapEvaluator(),
            PuzzleEvaluator(),
            SceneEvaluator(),
            MechanicsEvaluator(),
        ]

        contents = [plot_yaml, narrative_yaml, puzzle_yaml, scene_yaml, mechanics_yaml]

        for evaluator, content in zip(evaluators, contents, strict=False):
            result = evaluator.evaluate(content)
            self.assertIsInstance(result, QualityScore)
            self.assertTrue(0.0 <= result.score <= 10.0)
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.feedback, str)
            self.assertIsInstance(result.details, dict)

    def test_evaluators_handle_markdown_wrapped_yaml(self):
        """Test that evaluators handle markdown-wrapped YAML."""
        plot_yaml = """```yaml
title: "Test Plot"
setting: "A place"
themes: ["horror"]
plot:
  act1: "Something happens"
endings:
  - name: "End"
    type: "victory"
```"""

        evaluator = PlotEvaluator()
        result = evaluator.evaluate(plot_yaml)

        # Should parse successfully
        self.assertIsInstance(result, QualityScore)
        self.assertNotIn("error", result.details)


if __name__ == "__main__":
    unittest.main()
