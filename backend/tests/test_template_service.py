"""Tests for template service."""

from pathlib import Path

import pytest
import yaml

from app.services.template_service import TemplateService


@pytest.fixture
def template_service(tmp_path):
    """Create template service with temporary directory."""
    return TemplateService(templates_dir=str(tmp_path))


@pytest.fixture
def valid_template_data():
    """Valid template configuration data."""
    return {
        "title": "Test Template",
        "description": "A test template",
        "category": "test",
        "variables": [
            {
                "name": "test_var",
                "type": "string",
                "required": True,
                "description": "A test variable",
            },
            {
                "name": "optional_var",
                "type": "string",
                "required": False,
                "default": "default_value",
                "description": "An optional variable",
            },
        ],
        "prompt": "This is a test prompt with {{ test_var }} and {{ optional_var }}.",
    }


@pytest.fixture
def template_with_files(tmp_path, valid_template_data):
    """Create a template with files on disk."""
    # Create template.yaml
    template_file = tmp_path / "test_template.yaml"
    with template_file.open("w", encoding="utf-8") as f:
        yaml.dump(valid_template_data, f)

    return tmp_path


class TestTemplateService:
    """Tests for TemplateService class."""

    def test_list_templates_empty(self, tmp_path):
        """Test listing templates in empty directory."""
        service = TemplateService(templates_dir=str(tmp_path))
        templates = service.list_templates()
        assert templates == []

    def test_list_templates_nonexistent_directory(self, tmp_path):
        """Test listing templates when directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent"
        service = TemplateService(templates_dir=str(nonexistent))

        with pytest.raises(FileNotFoundError):
            service.list_templates()

    def test_list_templates_single(self, template_with_files, valid_template_data):
        """Test listing a single template."""
        service = TemplateService(templates_dir=str(template_with_files))
        templates = service.list_templates()

        assert len(templates) == 1
        assert templates[0]["name"] == "test_template"
        assert templates[0]["title"] == valid_template_data["title"]
        assert templates[0]["description"] == valid_template_data["description"]
        assert templates[0]["category"] == valid_template_data["category"]
        assert templates[0]["variables"] == valid_template_data["variables"]

    def test_list_templates_multiple(self, tmp_path):
        """Test listing multiple templates."""
        # Create multiple template files
        for i in range(3):
            template_file = tmp_path / f"template_{i}.yaml"
            data = {
                "title": f"Template {i}",
                "description": f"Description {i}",
                "category": "test",
                "variables": [],
                "prompt": f"Prompt {i}",
            }
            with template_file.open("w", encoding="utf-8") as f:
                yaml.dump(data, f)

        service = TemplateService(templates_dir=str(tmp_path))
        templates = service.list_templates()

        assert len(templates) == 3
        template_names = {t["name"] for t in templates}
        assert template_names == {"template_0", "template_1", "template_2"}

    def test_list_templates_skips_invalid_files(self, tmp_path):
        """Test that invalid template files are skipped."""
        # Create valid template
        valid_file = tmp_path / "valid.yaml"
        with valid_file.open("w", encoding="utf-8") as f:
            yaml.dump({"title": "Valid", "prompt": "Test"}, f)

        # Create invalid template (not a dict)
        invalid_file = tmp_path / "invalid.yaml"
        with invalid_file.open("w", encoding="utf-8") as f:
            yaml.dump(["not", "a", "dict"], f)

        # Create non-YAML file
        text_file = tmp_path / "readme.txt"
        text_file.write_text("This is not YAML")

        service = TemplateService(templates_dir=str(tmp_path))
        templates = service.list_templates()

        # Should only get the valid template
        assert len(templates) == 1
        assert templates[0]["name"] == "valid"

    def test_get_template_success(self, template_with_files, valid_template_data):
        """Test getting a template successfully."""
        service = TemplateService(templates_dir=str(template_with_files))
        template = service.get_template("test_template")

        assert template["title"] == valid_template_data["title"]
        assert template["description"] == valid_template_data["description"]
        assert template["prompt"] == valid_template_data["prompt"]
        assert template["variables"] == valid_template_data["variables"]

    def test_get_template_not_found(self, tmp_path):
        """Test getting a non-existent template."""
        service = TemplateService(templates_dir=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            service.get_template("nonexistent")

    def test_get_template_caching(self, template_with_files):
        """Test that templates are cached after first load."""
        service = TemplateService(templates_dir=str(template_with_files))

        # First call - loads from disk
        template1 = service.get_template("test_template")

        # Second call - should use cache
        template2 = service.get_template("test_template")

        # Should be the same object
        assert template1 is template2
        assert "test_template" in service._templates_cache

    def test_get_template_invalid_yaml(self, tmp_path):
        """Test getting a template with invalid YAML."""
        template_file = tmp_path / "invalid.yaml"
        template_file.write_text("{ invalid yaml: [ not closed")

        service = TemplateService(templates_dir=str(tmp_path))

        with pytest.raises(ValueError, match="Invalid YAML"):
            service.get_template("invalid")

    def test_get_template_missing_prompt(self, tmp_path):
        """Test getting a template without a prompt field."""
        template_file = tmp_path / "no_prompt.yaml"
        with template_file.open("w", encoding="utf-8") as f:
            yaml.dump({"title": "No Prompt", "description": "Missing prompt"}, f)

        service = TemplateService(templates_dir=str(tmp_path))

        with pytest.raises(ValueError, match="missing required 'prompt' field"):
            service.get_template("no_prompt")

    def test_render_template_success(self, template_with_files):
        """Test rendering a template with context."""
        service = TemplateService(templates_dir=str(template_with_files))

        context = {"test_var": "value1", "optional_var": "value2"}
        rendered = service.render_template("test_template", context)

        assert "value1" in rendered
        assert "value2" in rendered
        assert "{{ test_var }}" not in rendered

    def test_render_template_with_defaults(self, tmp_path):
        """Test rendering a template using default values."""
        template_data = {
            "title": "Test",
            "variables": [
                {"name": "required", "type": "string", "required": True},
                {
                    "name": "optional",
                    "type": "string",
                    "required": False,
                    "default": "default_value",
                },
            ],
            "prompt": "Required: {{ required }}, Optional: {{ optional }}",
        }

        template_file = tmp_path / "test.yaml"
        with template_file.open("w", encoding="utf-8") as f:
            yaml.dump(template_data, f)

        service = TemplateService(templates_dir=str(tmp_path))

        # Render with only required variable
        context = {"required": "test"}
        rendered = service.render_template("test", context)

        assert "Required: test" in rendered

    def test_render_template_missing_required_variable(self, template_with_files):
        """Test rendering fails with missing required variable."""
        service = TemplateService(templates_dir=str(template_with_files))

        # Missing required 'test_var'
        context = {"optional_var": "value"}

        with pytest.raises(ValueError, match="Missing required variables"):
            service.render_template("test_template", context)

    def test_render_template_not_found(self, tmp_path):
        """Test rendering a non-existent template."""
        service = TemplateService(templates_dir=str(tmp_path))

        with pytest.raises(FileNotFoundError):
            service.render_template("nonexistent", {})

    def test_render_template_jinja2_error(self, tmp_path):
        """Test rendering with Jinja2 syntax error."""
        template_data = {
            "title": "Bad Template",
            "variables": [],
            "prompt": "{{ undefined_var | bad_filter }}",
        }

        template_file = tmp_path / "bad.yaml"
        with template_file.open("w", encoding="utf-8") as f:
            yaml.dump(template_data, f)

        service = TemplateService(templates_dir=str(tmp_path))

        with pytest.raises(ValueError, match="Failed to render template"):
            service.render_template("bad", {})

    def test_render_template_with_conditionals(self, tmp_path):
        """Test rendering a template with Jinja2 conditionals."""
        template_data = {
            "title": "Conditional Template",
            "variables": [
                {"name": "show_extra", "type": "boolean", "required": False}
            ],
            "prompt": "Base text.{% if show_extra %} Extra text.{% endif %}",
        }

        template_file = tmp_path / "conditional.yaml"
        with template_file.open("w", encoding="utf-8") as f:
            yaml.dump(template_data, f)

        service = TemplateService(templates_dir=str(tmp_path))

        # Render with condition true
        rendered_true = service.render_template("conditional", {"show_extra": True})
        assert "Extra text" in rendered_true

        # Render with condition false
        rendered_false = service.render_template("conditional", {"show_extra": False})
        assert "Extra text" not in rendered_false

    def test_render_template_with_loops(self, tmp_path):
        """Test rendering a template with Jinja2 loops."""
        template_data = {
            "title": "Loop Template",
            "variables": [{"name": "items", "type": "list", "required": True}],
            "prompt": "Items:{% for item in items %} {{ item }},{% endfor %}",
        }

        template_file = tmp_path / "loop.yaml"
        with template_file.open("w", encoding="utf-8") as f:
            yaml.dump(template_data, f)

        service = TemplateService(templates_dir=str(tmp_path))

        context = {"items": ["apple", "banana", "cherry"]}
        rendered = service.render_template("loop", context)

        assert "apple" in rendered
        assert "banana" in rendered
        assert "cherry" in rendered


class TestRealTemplates:
    """Test the actual template files in the project."""

    def test_horror_template_exists(self):
        """Test that horror template exists and is valid."""
        service = TemplateService()
        templates = service.list_templates()
        template_names = {t["name"] for t in templates}
        assert "horror" in template_names

    def test_horror_template_structure(self):
        """Test horror template has correct structure."""
        service = TemplateService()
        template = service.get_template("horror")

        assert template["title"]
        assert template["description"]
        assert template["category"] == "horror"
        assert template["prompt"]
        assert isinstance(template["variables"], list)

        # Check for required variables
        var_names = {v["name"] for v in template["variables"]}
        assert "setting" in var_names
        assert "threat" in var_names

    def test_horror_template_renders(self):
        """Test horror template can be rendered."""
        service = TemplateService()
        context = {
            "setting": "abandoned space station",
            "threat": "alien creatures",
            "atmosphere": "dark and foreboding",
            "duration": "long",
        }

        rendered = service.render_template("horror", context)
        assert "abandoned space station" in rendered
        assert "alien creatures" in rendered

    def test_artifact_hunt_template_exists(self):
        """Test that artifact_hunt template exists and is valid."""
        service = TemplateService()
        templates = service.list_templates()
        template_names = {t["name"] for t in templates}
        assert "artifact_hunt" in template_names

    def test_artifact_hunt_template_structure(self):
        """Test artifact_hunt template has correct structure."""
        service = TemplateService()
        template = service.get_template("artifact_hunt")

        assert template["title"]
        assert template["description"]
        assert template["category"] == "exploration"
        assert template["prompt"]

        # Check for required variables
        var_names = {v["name"] for v in template["variables"]}
        assert "artifact_name" in var_names
        assert "location" in var_names

    def test_artifact_hunt_template_renders(self):
        """Test artifact_hunt template can be rendered."""
        service = TemplateService()
        context = {
            "artifact_name": "Ancient Relic",
            "location": "underground ruins",
            "opposition": "mercenaries",
            "difficulty": "hard",
            "time_pressure": True,
        }

        rendered = service.render_template("artifact_hunt", context)
        assert "Ancient Relic" in rendered
        assert "underground ruins" in rendered

    def test_rescue_template_exists(self):
        """Test that rescue template exists and is valid."""
        service = TemplateService()
        templates = service.list_templates()
        template_names = {t["name"] for t in templates}
        assert "rescue" in template_names

    def test_rescue_template_structure(self):
        """Test rescue template has correct structure."""
        service = TemplateService()
        template = service.get_template("rescue")

        assert template["title"]
        assert template["description"]
        assert template["category"] == "action"
        assert template["prompt"]

        # Check for required variables
        var_names = {v["name"] for v in template["variables"]}
        assert "rescue_target" in var_names
        assert "location" in var_names

    def test_rescue_template_renders(self):
        """Test rescue template can be rendered."""
        service = TemplateService()
        context = {
            "rescue_target": "captured soldier",
            "location": "enemy base",
            "captors": "hostile forces",
            "target_condition": "wounded",
            "extraction_method": "helicopter",
        }

        rendered = service.render_template("rescue", context)
        assert "captured soldier" in rendered
        assert "enemy base" in rendered

    def test_all_templates_valid(self):
        """Test all templates can be loaded and have required fields."""
        service = TemplateService()
        templates = service.list_templates()

        assert len(templates) >= 3  # At least horror, artifact_hunt, rescue

        for template_meta in templates:
            # Can get full template
            template = service.get_template(template_meta["name"])

            # Has required fields
            assert "title" in template
            assert "prompt" in template
            assert isinstance(template.get("variables", []), list)
