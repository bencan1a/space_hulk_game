"""Tests for template API endpoints."""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import app
from app.services.template_service import TemplateService

client = TestClient(app)


@pytest.fixture
def mock_templates_dir(tmp_path, monkeypatch):
    """Create a temporary templates directory with test templates."""
    # Create test templates
    templates = {
        "test1": {
            "title": "Test Template 1",
            "description": "First test template",
            "category": "test",
            "variables": [
                {"name": "var1", "type": "string", "required": True},
            ],
            "prompt": "Test prompt with {{ var1 }}",
        },
        "test2": {
            "title": "Test Template 2",
            "description": "Second test template",
            "category": "test",
            "variables": [],
            "prompt": "Simple prompt",
        },
    }

    for name, data in templates.items():
        template_file = tmp_path / f"{name}.yaml"
        with template_file.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)

    # Patch TemplateService to use tmp directory
    def mock_template_service():
        return TemplateService(templates_dir=str(tmp_path))

    monkeypatch.setattr(
        "app.api.routes.templates.get_template_service", mock_template_service
    )

    return tmp_path


class TestListTemplates:
    """Tests for GET /api/v1/templates endpoint."""

    def test_list_templates_empty(self, tmp_path, monkeypatch):
        """Test listing templates when directory is empty."""

        def mock_template_service():
            return TemplateService(templates_dir=str(tmp_path))

        monkeypatch.setattr(
            "app.api.routes.templates.get_template_service", mock_template_service
        )

        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data
        assert data["templates"] == []
        assert data["total"] == 0

    def test_list_templates_success(self, mock_templates_dir):
        """Test listing templates successfully."""
        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 2
        assert len(data["templates"]) == 2

        template_names = {t["name"] for t in data["templates"]}
        assert "test1" in template_names
        assert "test2" in template_names

        # Check template structure
        for template in data["templates"]:
            assert "name" in template
            assert "title" in template
            assert "description" in template
            assert "category" in template
            assert "variables" in template

    def test_list_templates_includes_metadata(self, mock_templates_dir):
        """Test that list includes template metadata."""
        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()

        test1 = next(t for t in data["templates"] if t["name"] == "test1")
        assert test1["title"] == "Test Template 1"
        assert test1["description"] == "First test template"
        assert test1["category"] == "test"
        assert len(test1["variables"]) == 1
        assert test1["variables"][0]["name"] == "var1"

    def test_list_templates_directory_not_found(self, tmp_path, monkeypatch):
        """Test error when templates directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent"

        def mock_template_service():
            return TemplateService(templates_dir=str(nonexistent))

        monkeypatch.setattr(
            "app.api.routes.templates.get_template_service", mock_template_service
        )

        response = client.get("/api/v1/templates")

        assert response.status_code == 500
        assert "not found" in response.json()["detail"].lower()


class TestGetTemplate:
    """Tests for GET /api/v1/templates/{name} endpoint."""

    def test_get_template_success(self, mock_templates_dir):
        """Test getting a template successfully."""
        response = client.get("/api/v1/templates/test1")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "test1"
        assert data["title"] == "Test Template 1"
        assert data["description"] == "First test template"
        assert data["category"] == "test"
        assert data["prompt"] == "Test prompt with {{ var1 }}"
        assert len(data["variables"]) == 1

    def test_get_template_not_found(self, mock_templates_dir):
        """Test getting a non-existent template."""
        response = client.get("/api/v1/templates/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_template_includes_prompt(self, mock_templates_dir):
        """Test that get includes the full prompt."""
        response = client.get("/api/v1/templates/test2")

        assert response.status_code == 200
        data = response.json()

        assert data["prompt"] == "Simple prompt"

    def test_get_template_includes_variables(self, mock_templates_dir):
        """Test that get includes variable definitions."""
        response = client.get("/api/v1/templates/test1")

        assert response.status_code == 200
        data = response.json()

        assert len(data["variables"]) == 1
        assert data["variables"][0]["name"] == "var1"
        assert data["variables"][0]["type"] == "string"
        assert data["variables"][0]["required"] is True

    def test_get_template_invalid_yaml(self, tmp_path, monkeypatch):
        """Test getting a template with invalid YAML."""
        template_file = tmp_path / "invalid.yaml"
        template_file.write_text("{ invalid yaml: [ not closed")

        def mock_template_service():
            return TemplateService(templates_dir=str(tmp_path))

        monkeypatch.setattr(
            "app.api.routes.templates.get_template_service", mock_template_service
        )

        response = client.get("/api/v1/templates/invalid")

        assert response.status_code == 500
        assert "invalid" in response.json()["detail"].lower()


class TestRealTemplatesAPI:
    """Test the actual template files through the API."""

    def test_real_templates_list(self):
        """Test listing real templates."""
        response = client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 3
        template_names = {t["name"] for t in data["templates"]}
        assert "horror" in template_names
        assert "artifact_hunt" in template_names
        assert "rescue" in template_names

    def test_get_horror_template(self):
        """Test getting the horror template."""
        response = client.get("/api/v1/templates/horror")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "horror"
        assert data["title"] == "Gothic Horror"
        assert data["category"] == "horror"
        assert "prompt" in data
        assert len(data["variables"]) > 0

        # Check for expected variables
        var_names = {v["name"] for v in data["variables"]}
        assert "setting" in var_names
        assert "threat" in var_names

    def test_get_artifact_hunt_template(self):
        """Test getting the artifact_hunt template."""
        response = client.get("/api/v1/templates/artifact_hunt")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "artifact_hunt"
        assert data["title"] == "Artifact Hunt"
        assert data["category"] == "exploration"
        assert "prompt" in data

        # Check for expected variables
        var_names = {v["name"] for v in data["variables"]}
        assert "artifact_name" in var_names
        assert "location" in var_names

    def test_get_rescue_template(self):
        """Test getting the rescue template."""
        response = client.get("/api/v1/templates/rescue")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "rescue"
        assert data["title"] == "Rescue Mission"
        assert data["category"] == "action"
        assert "prompt" in data

        # Check for expected variables
        var_names = {v["name"] for v in data["variables"]}
        assert "rescue_target" in var_names
        assert "location" in var_names

    def test_all_real_templates_accessible(self):
        """Test that all listed templates can be retrieved."""
        # Get list of templates
        list_response = client.get("/api/v1/templates")
        assert list_response.status_code == 200
        templates = list_response.json()["templates"]

        # Get each template individually
        for template_meta in templates:
            template_response = client.get(f"/api/v1/templates/{template_meta['name']}")
            assert template_response.status_code == 200

            template = template_response.json()
            assert template["name"] == template_meta["name"]
            assert template["title"] == template_meta["title"]
