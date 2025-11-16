# Output Auto-Correction System

This module provides automatic correction capabilities for common YAML validation errors in AI agent outputs.

## Overview

The `OutputCorrector` class automatically fixes common validation errors in YAML outputs from AI agents, making the validation system more robust and reducing the need for manual intervention.

## Features

### Automatic Corrections

The corrector can fix:

- **Missing Required Fields**: Adds fields with sensible defaults
- **Invalid ID Formats**: Converts IDs to lowercase, underscores, alphanumeric
- **Short Descriptions**: Extends descriptions to meet minimum length requirements
- **YAML Syntax Errors**: Basic fixes for common syntax issues (where possible)
- **Markdown Fences**: Automatically strips markdown code fences

### Supported Output Types

The corrector supports all five game design output types:

1. **Plot Outline** (`correct_plot`)
2. **Narrative Map** (`correct_narrative_map`)
3. **Puzzle Design** (`correct_puzzle_design`)
4. **Scene Texts** (`correct_scene_texts`)
5. **Game Mechanics** (`correct_game_mechanics`)

## Usage

### Basic Example

```python
from space_hulk_game.validation import OutputCorrector

# Initialize the corrector
corrector = OutputCorrector()

# Attempt to correct invalid YAML
result = corrector.correct_plot(invalid_yaml_string)

# Check if correction succeeded
if result.success:
    print(f"✓ Corrected with {len(result.corrections)} changes")
    # Use the corrected YAML
    with open('output.yaml', 'w') as f:
        f.write(result.corrected_yaml)
else:
    print(f"✗ Correction failed")
    for error in result.validation_result.errors:
        print(f"  - {error}")
```

### CorrectionResult Structure

The `CorrectionResult` dataclass contains:

- `corrected_yaml` (str): The corrected YAML string
- `corrections` (list[str]): List of corrections applied
- `validation_result` (ValidationResult): Result from validating the corrected output
- `success` (bool): Whether correction succeeded and output is now valid

## Correction Strategies

### Plot Outline

Fixes applied:

- Adds missing `title`, `setting`, `themes`, `tone`
- Adds minimal `plot_points` (3 minimum required)
- Adds minimal `characters` and `conflicts`
- Fixes plot point ID formats
- Extends short descriptions to 50+ characters
- Extends short backstories to 50+ characters

### Narrative Map

Fixes applied:

- Adds missing `scenes` dictionary
- Adds missing `start_scene` (uses first scene)
- Fixes scene ID formats (lowercase, underscores)
- Updates `start_scene` if scene ID was fixed
- Adds missing `connections` lists
- Fixes connection target IDs
- Extends short scene descriptions to 50+ characters

### Puzzle Design

Fixes applied:

- Adds missing `puzzles`, `artifacts`, `monsters`, `npcs` lists
- Fixes ID formats for all entity types
- Extends short descriptions to 50+ characters
- Adds default properties/abilities/themes where needed

### Scene Texts

Fixes applied:

- Adds missing `scenes` dictionary
- Fixes scene ID formats
- Extends short descriptions to 100+ characters (scene texts requirement)
- Extends short `atmosphere` fields to 10+ characters
- Extends short `initial_text` fields to 20+ characters
- Adds missing `examination_texts` and `dialogue` fields

### Game Mechanics

Fixes applied:

- Adds missing `game_title`
- Adds all four required game systems:
  - `movement` (with commands and narrative purpose)
  - `inventory` (with capacity, commands, narrative purpose)
  - `combat` (with mechanics and narrative purpose)
  - `interaction` (with commands and narrative purpose)
- Adds `game_state` with tracked variables, win/lose conditions
- Adds `technical_requirements`

## Design Principles

### Conservative Corrections

The corrector follows these principles:

1. **Preserve Intent**: Never remove or significantly alter existing content
2. **Minimal Changes**: Make the smallest possible corrections
3. **Transparent Logging**: Log all corrections with details
4. **Fail Gracefully**: If correction isn't possible, return clear error messages

### Default Values

When adding missing fields, the corrector uses:

- **Generic placeholders** that make sense in context
- **Minimal but valid** data structures
- **Extendable descriptions** that indicate need for refinement

Example default plot point:

```yaml
id: "pp_01_opening"
name: "Opening"
description: "The story begins with the initial situation. Additional details and context will be developed further during the narrative design process."
```

## Integration with Validation

The corrector uses the existing `OutputValidator` to:

1. Parse YAML before correction
2. Validate corrected output
3. Return comprehensive validation results

This ensures corrected outputs are guaranteed to be valid (when `success=True`).

## Testing

Comprehensive test coverage includes:

- **20 unit tests** in `tests/test_corrector.py`
- Tests for each correction type
- Tests for each output format
- Edge case testing (empty inputs, malformed YAML, etc.)

Run tests:

```bash
python -m unittest tests.test_corrector -v
```

## Examples

See `examples/corrector_usage.py` for comprehensive usage examples covering all output types and common correction scenarios.

Run examples:

```bash
python examples/corrector_usage.py
```

## API Reference

### OutputCorrector Class

```python
class OutputCorrector:
    def __init__(self):
        """Initialize the output corrector with a validator instance."""

    def correct_plot(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in plot outline YAML."""

    def correct_narrative_map(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in narrative map YAML."""

    def correct_puzzle_design(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in puzzle design YAML."""

    def correct_scene_texts(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in scene texts YAML."""

    def correct_game_mechanics(self, raw_output: str) -> CorrectionResult:
        """Attempt to correct common errors in game mechanics YAML."""
```

### CorrectionResult Dataclass

```python
@dataclass
class CorrectionResult:
    corrected_yaml: str           # The corrected YAML string
    corrections: list[str]        # List of corrections applied
    validation_result: ValidationResult  # Validation result
    success: bool                 # Whether correction succeeded
```

## Logging

The corrector logs all operations at appropriate levels:

- **INFO**: Successful corrections, initialization
- **WARNING**: YAML parsing errors that were fixed
- **ERROR**: Unrecoverable errors

Example log output:

```
INFO: OutputCorrector initialized
INFO: Attempting to correct plot outline YAML
INFO: Added missing 'plot_points' field
INFO: Fixed plot point ID: Plot Point 1! -> plot_point_1
INFO: Extended plot point description from 20 to 50 chars
INFO: Plot correction complete: 3 corrections, valid=True
```

## Limitations

### What the Corrector Cannot Fix

- **Semantic errors**: Wrong content, incorrect logic
- **Complex YAML syntax errors**: Deep structural issues
- **Invalid references**: References to non-existent entities (though it tries to fix ID formats)
- **Quality issues**: Generic content, poor writing quality
- **Domain-specific errors**: Violations of game design principles

### When to Use Manual Intervention

Use the corrector for:

- ✓ Quick fixes during development
- ✓ Handling common AI output errors
- ✓ Batch processing multiple outputs

Manual intervention needed for:

- ✗ Complex validation errors
- ✗ Content quality improvement
- ✗ Fundamental structural issues

## Future Enhancements

Potential improvements:

1. **Smarter description extension**: Use LLM to generate better filler text
2. **Cross-reference validation**: Check that IDs referenced actually exist
3. **Quality scoring**: Rate the quality of corrections applied
4. **Configurable defaults**: Allow custom default values
5. **Batch correction**: Process multiple files at once
6. **Correction reports**: Generate detailed HTML/PDF reports

## Contributing

When adding new correction strategies:

1. Add tests in `tests/test_corrector.py`
2. Update this README
3. Follow existing patterns for consistency
4. Log all corrections transparently
5. Preserve existing content whenever possible

## License

Part of the Space Hulk Game project. See main project LICENSE.
