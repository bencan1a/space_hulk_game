"""Service for managing prompt templates."""

import logging
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for loading and rendering prompt templates."""

    def __init__(self, templates_dir: str | None = None):
        """
        Initialize template service.

        Args:
            templates_dir: Directory containing template YAML files.
                          If None, uses ../data/templates relative to this file.
        """
        if templates_dir is None:
            # Default to ../data/templates relative to project root
            # (4 levels up from this file: services -> app -> backend -> root)
            templates_dir = str(
                Path(__file__).parent.parent.parent.parent / "data" / "templates"
            )
        self.templates_dir = Path(templates_dir)
        self._templates_cache: dict[str, dict[str, Any]] = {}
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,  # Disable autoescape for prompt templates
        )

    def list_templates(self) -> list[dict[str, Any]]:
        """
        List all available templates.

        Returns:
            List of template metadata dictionaries

        Raises:
            FileNotFoundError: If templates directory does not exist
        """
        if not self.templates_dir.exists():
            logger.warning(
                f"Templates directory does not exist: {self.templates_dir}"
            )
            raise FileNotFoundError(
                f"Templates directory not found: {self.templates_dir}"
            )

        templates = []
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                template_data = self._load_template_file(template_file)
                templates.append(
                    {
                        "name": template_file.stem,
                        "title": template_data.get("title", template_file.stem),
                        "description": template_data.get("description", ""),
                        "category": template_data.get("category", "general"),
                        "variables": template_data.get("variables", []),
                    }
                )
            except Exception as e:
                logger.error(f"Error loading template {template_file}: {e}")
                continue

        return templates

    def get_template(self, name: str) -> dict[str, Any]:
        """
        Get a specific template by name.

        Args:
            name: Template name (without .yaml extension)

        Returns:
            Template data dictionary

        Raises:
            FileNotFoundError: If template file does not exist
            ValueError: If template file is invalid
        """
        # Check cache first
        if name in self._templates_cache:
            return self._templates_cache[name]

        template_path = self.templates_dir / f"{name}.yaml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {name}")

        template_data = self._load_template_file(template_path)
        self._templates_cache[name] = template_data
        return template_data

    def render_template(self, name: str, context: dict[str, Any]) -> str:
        """
        Render a template with the given context.

        Args:
            name: Template name (without .yaml extension)
            context: Dictionary of variables to substitute in template

        Returns:
            Rendered prompt string

        Raises:
            FileNotFoundError: If template file does not exist
            ValueError: If template is invalid or missing required variables
        """
        template_data = self.get_template(name)

        # Get the prompt template string
        prompt_template = template_data.get("prompt")
        if not prompt_template:
            raise ValueError(f"Template '{name}' missing 'prompt' field")

        # Validate required variables
        required_vars = [
            var["name"]
            for var in template_data.get("variables", [])
            if var.get("required", False)
        ]
        missing_vars = [var for var in required_vars if var not in context]
        if missing_vars:
            raise ValueError(
                f"Missing required variables for template '{name}': {missing_vars}"
            )

        # Render the template
        try:
            template = Template(prompt_template)
            rendered = template.render(**context)
            return rendered
        except Exception as e:
            logger.error(f"Error rendering template '{name}': {e}")
            raise ValueError(f"Failed to render template '{name}': {e}") from e

    def _load_template_file(self, template_path: Path) -> dict[str, Any]:
        """
        Load and validate a template YAML file.

        Args:
            template_path: Path to template file

        Returns:
            Template data dictionary

        Raises:
            ValueError: If template file is invalid
        """
        try:
            with template_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError("Template file must contain a dictionary")

            # Validate required fields
            if "prompt" not in data:
                raise ValueError("Template missing required 'prompt' field")

            return data
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {template_path}: {e}")
            raise ValueError(f"Invalid YAML in template file: {e}") from e
        except Exception as e:
            logger.error(f"Error loading template {template_path}: {e}")
            raise
