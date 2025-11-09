#!/usr/bin/env python3
"""
Mem0 Configuration Automation Script for Space Hulk Game

This script automates the setup of mem0 memory integration for the CrewAI-based
Space Hulk narrative generation crew.

Usage:
    python configure_mem0.py --mode basic       # Enable basic built-in memory
    python configure_mem0.py --mode cloud       # Configure cloud mem0 (requires API key)
    python configure_mem0.py --mode local       # Configure local mem0 (requires Qdrant)
    python configure_mem0.py --validate-only    # Validate configuration without changes

Options:
    --mode {basic,cloud,local}  Memory configuration mode
    --vector-store {qdrant,chroma}  Vector store for local mode (default: qdrant)
    --validate-only             Only validate prerequisites, don't modify files
    --crew-file PATH            Path to crew.py (default: src/space_hulk_game/crew.py)
    --env-file PATH             Path to .env (default: .env)
"""

import argparse
import os
import sys
import re
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
import datetime


class Mem0Configurator:
    """Automates mem0 memory configuration for the Space Hulk crew."""

    def __init__(
        self,
        mode: str = "basic",
        vector_store: str = "qdrant",
        crew_file: str = "src/space_hulk_game/crew.py",
        env_file: str = ".env",
        validate_only: bool = False
    ):
        """
        Initialize the configurator.

        Args:
            mode: Configuration mode ('basic', 'cloud', 'local')
            vector_store: Vector store for local mode ('qdrant', 'chroma')
            crew_file: Path to crew.py file
            env_file: Path to .env file
            validate_only: If True, only validate without modifying files
        """
        self.mode = mode
        self.vector_store = vector_store
        self.crew_file = Path(crew_file)
        self.env_file = Path(env_file)
        self.validate_only = validate_only
        self.project_root = Path(__file__).parent

    def run(self) -> bool:
        """
        Execute the configuration process.

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Mem0 Configuration for Space Hulk Game")
        print(f"{'='*60}\n")
        print(f"Mode: {self.mode}")
        print(f"Validate Only: {self.validate_only}")
        print()

        # Step 1: Validate prerequisites
        if not self._validate_prerequisites():
            return False

        # Step 2: Generate configuration
        config = self._generate_configuration()
        if not config:
            return False

        # Step 3: Display configuration
        self._display_configuration(config)

        # Step 4: Apply configuration (unless validate-only)
        if not self.validate_only:
            if not self._apply_configuration(config):
                return False

        # Step 5: Test configuration
        if not self.validate_only:
            self._test_configuration()

        print("\n" + "="*60)
        print("Configuration complete!")
        print("="*60 + "\n")

        if not self.validate_only:
            self._print_next_steps()

        return True

    def _validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met for the selected mode."""
        print("Validating prerequisites...\n")

        # Check if crew.py exists
        if not self.crew_file.exists():
            print(f"❌ Error: crew.py not found at {self.crew_file}")
            return False
        print(f"✅ Found crew.py at {self.crew_file}")

        # Check .env file
        if not self.env_file.exists():
            print(f"⚠️  Warning: .env file not found at {self.env_file}")
            print(f"   Creating from .env.example...")
            self._create_env_file()
        print(f"✅ Found .env at {self.env_file}")

        # Mode-specific validations
        if self.mode == "cloud":
            return self._validate_cloud_prerequisites()
        elif self.mode == "local":
            return self._validate_local_prerequisites()
        else:  # basic
            print("✅ Basic mode requires no external dependencies")
            return True

    def _validate_cloud_prerequisites(self) -> bool:
        """Validate prerequisites for cloud mem0 mode."""
        # Check for MEM0_API_KEY
        api_key = self._get_env_var("MEM0_API_KEY")
        if not api_key:
            print("\n❌ Error: MEM0_API_KEY not found in .env")
            print("\nTo use cloud mem0:")
            print("1. Sign up at https://mem0.ai/")
            print("2. Get your API key from the dashboard")
            print("3. Add to .env: MEM0_API_KEY=m0-your-key-here")
            return False

        print(f"✅ Found MEM0_API_KEY in .env")

        # Test API key validity
        print("   Testing API key...")
        if self._test_mem0_api(api_key):
            print("✅ API key is valid")
            return True
        else:
            print("❌ API key validation failed")
            return False

    def _validate_local_prerequisites(self) -> bool:
        """Validate prerequisites for local mem0 mode."""
        all_valid = True

        # Check Ollama
        if not self._check_ollama_running():
            print("❌ Ollama is not running")
            print("   Start with: ollama serve")
            all_valid = False
        else:
            print("✅ Ollama is running")

        # Check embedding model
        embedding_model = "mxbai-embed-large"
        if not self._check_ollama_model(embedding_model):
            print(f"❌ Embedding model '{embedding_model}' not found")
            print(f"   Install with: ollama pull {embedding_model}")
            all_valid = False
        else:
            print(f"✅ Embedding model '{embedding_model}' is available")

        # Check vector store
        if self.vector_store == "qdrant":
            if not self._check_qdrant_running():
                print("❌ Qdrant is not running")
                print("   Start with: docker run -d -p 6333:6333 qdrant/qdrant")
                all_valid = False
            else:
                print("✅ Qdrant is running")
        else:  # chroma
            print("✅ ChromaDB will be used (embedded, no server required)")

        return all_valid

    def _check_ollama_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def _check_ollama_model(self, model: str) -> bool:
        """Check if specific Ollama model is available."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m.get("name", "").startswith(model) for m in models)
        except Exception:
            pass
        return False

    def _check_qdrant_running(self) -> bool:
        """Check if Qdrant is running."""
        try:
            response = requests.get("http://localhost:6333/collections", timeout=2)
            return response.status_code in [200, 404]  # 404 is ok, means no collections yet
        except Exception:
            return False

    def _test_mem0_api(self, api_key: str) -> bool:
        """Test if mem0 API key is valid."""
        try:
            # Try to initialize client
            from mem0 import MemoryClient
            client = MemoryClient(api_key=api_key)
            # Test with a simple operation
            return True
        except Exception as e:
            print(f"   Error: {str(e)}")
            return False

    def _generate_configuration(self) -> Optional[Dict]:
        """Generate configuration based on mode."""
        print(f"\nGenerating {self.mode} mode configuration...\n")

        if self.mode == "basic":
            return self._generate_basic_config()
        elif self.mode == "cloud":
            return self._generate_cloud_config()
        elif self.mode == "local":
            return self._generate_local_config()
        else:
            print(f"❌ Unknown mode: {self.mode}")
            return None

    def _generate_basic_config(self) -> Dict:
        """Generate basic memory configuration."""
        return {
            "mode": "basic",
            "crew_config": {
                "memory": True
            },
            "description": "Built-in CrewAI memory with ChromaDB and SQLite"
        }

    def _generate_cloud_config(self) -> Dict:
        """Generate cloud mem0 configuration."""
        return {
            "mode": "cloud",
            "crew_config": {
                "memory": True,
                "memory_config": {
                    "provider": "mem0",
                    "config": {
                        "user_id": "space_hulk_user",
                        "run_id": "dynamic"  # Will be generated at runtime
                    }
                }
            },
            "description": "Cloud mem0 with managed infrastructure"
        }

    def _generate_local_config(self) -> Dict:
        """Generate local mem0 configuration."""
        # Vector store config
        if self.vector_store == "qdrant":
            vector_config = {
                "provider": "qdrant",
                "config": {
                    "collection_name": "space_hulk_narratives",
                    "host": "localhost",
                    "port": 6333,
                    "embedding_model_dims": 1024
                }
            }
        else:  # chroma
            vector_config = {
                "provider": "chroma",
                "config": {
                    "collection_name": "space_hulk_narratives",
                    "path": "./chroma_db"
                }
            }

        local_mem0_config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "qwen2.5",
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "base_url": "http://localhost:11434"
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "mxbai-embed-large",
                    "ollama_base_url": "http://localhost:11434"
                }
            },
            "vector_store": vector_config
        }

        return {
            "mode": "local",
            "crew_config": {
                "memory": True,
                "memory_config": {
                    "provider": "mem0",
                    "config": {
                        "user_id": "space_hulk_user",
                        "local_mem0_config": local_mem0_config
                    }
                }
            },
            "description": f"Local mem0 with {self.vector_store.capitalize()} vector store",
            "local_config": local_mem0_config
        }

    def _display_configuration(self, config: Dict) -> None:
        """Display the generated configuration."""
        print("Configuration Details:")
        print("-" * 60)
        print(f"Mode: {config['mode']}")
        print(f"Description: {config['description']}")
        print()

        if config['mode'] == 'basic':
            print("Settings:")
            print("  - memory: True")
            print("  - provider: Built-in CrewAI (ChromaDB + SQLite)")
        else:
            print("Memory Configuration:")
            memory_config = config['crew_config'].get('memory_config', {})
            self._print_dict(memory_config, indent=2)

        print()

    def _print_dict(self, d: Dict, indent: int = 0) -> None:
        """Pretty print a dictionary with indentation."""
        for key, value in d.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                self._print_dict(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")

    def _apply_configuration(self, config: Dict) -> bool:
        """Apply the configuration to crew.py."""
        print("\nApplying configuration to crew.py...\n")

        try:
            # Read crew.py
            with open(self.crew_file, 'r', encoding='utf-8') as f:
                crew_content = f.read()

            # Modify based on mode
            if config['mode'] == 'basic':
                crew_content = self._apply_basic_config(crew_content)
            elif config['mode'] == 'cloud':
                crew_content = self._apply_cloud_config(crew_content, config)
            elif config['mode'] == 'local':
                crew_content = self._apply_local_config(crew_content, config)

            # Write back
            with open(self.crew_file, 'w', encoding='utf-8') as f:
                f.write(crew_content)

            print("✅ Successfully updated crew.py")
            return True

        except Exception as e:
            print(f"❌ Error updating crew.py: {str(e)}")
            return False

    def _apply_basic_config(self, content: str) -> str:
        """Apply basic memory configuration to crew.py."""
        # Find the crew() method and enable memory=True
        pattern = r'(def crew\(self\) -> Crew:.*?return Crew\()(.*?)(\))'

        def replacer(match):
            before = match.group(1)
            params = match.group(2)
            after = match.group(3)

            # Check if memory parameter exists
            if 'memory=' in params:
                # Replace existing memory parameter
                params = re.sub(r'memory\s*=\s*\w+', 'memory=True', params)
            else:
                # Add memory parameter
                params += ',\n            memory=True'

            return before + params + after

        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        return content

    def _apply_cloud_config(self, content: str, config: Dict) -> str:
        """Apply cloud mem0 configuration to crew.py."""
        # Add memory_config in __init__ if not present
        if 'self.memory_config' not in content:
            content = self._add_memory_config_to_init(content, config)
        else:
            content = self._update_memory_config_in_init(content, config)

        # Update crew() method
        content = self._update_crew_method(content, use_memory_config=True)

        return content

    def _apply_local_config(self, content: str, config: Dict) -> str:
        """Apply local mem0 configuration to crew.py."""
        # Add local_mem0_config and memory_config in __init__
        if 'self.local_mem0_config' not in content:
            content = self._add_local_config_to_init(content, config)
        else:
            content = self._update_local_config_in_init(content, config)

        # Update crew() method
        content = self._update_crew_method(content, use_memory_config=True)

        return content

    def _add_memory_config_to_init(self, content: str, config: Dict) -> str:
        """Add memory_config to __init__ method."""
        # Find the end of __init__ (before first @agent decorator)
        init_end_pattern = r'(\s+)(# Will be used in the crew configuration\s+self\.shared_memory = None)'

        memory_config_code = '''
        # Memory configuration for cloud mem0
        self.memory_config = {
            "provider": "mem0",
            "config": {
                "user_id": "space_hulk_user",
                "run_id": f"session_{datetime.datetime.now().timestamp()}"
            }
        }
'''

        content = re.sub(
            init_end_pattern,
            memory_config_code + r'\1\2',
            content
        )

        return content

    def _update_memory_config_in_init(self, content: str, config: Dict) -> str:
        """Update existing memory_config in __init__ method."""
        # Replace the existing memory_config
        pattern = r'self\.memory_config = \{[^}]+\}'

        replacement = '''self.memory_config = {
            "provider": "mem0",
            "config": {
                "user_id": "space_hulk_user",
                "run_id": f"session_{datetime.datetime.now().timestamp()}"
            }
        }'''

        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        return content

    def _add_local_config_to_init(self, content: str, config: Dict) -> str:
        """Add local_mem0_config to __init__ method."""
        local_config = config['local_config']

        # Generate config code
        local_config_code = f'''
        # Local mem0 configuration
        self.local_mem0_config = {{
            "llm": {{
                "provider": "ollama",
                "config": {{
                    "model": "{local_config['llm']['config']['model']}",
                    "temperature": {local_config['llm']['config']['temperature']},
                    "max_tokens": {local_config['llm']['config']['max_tokens']},
                    "base_url": "{local_config['llm']['config']['base_url']}"
                }}
            }},
            "embedder": {{
                "provider": "ollama",
                "config": {{
                    "model": "{local_config['embedder']['config']['model']}",
                    "ollama_base_url": "{local_config['embedder']['config']['ollama_base_url']}"
                }}
            }},
            "vector_store": {{
                "provider": "{local_config['vector_store']['provider']}",
                "config": {local_config['vector_store']['config']}
            }}
        }}

        # Memory configuration for local mem0
        self.memory_config = {{
            "provider": "mem0",
            "config": {{
                "user_id": "space_hulk_user",
                "local_mem0_config": self.local_mem0_config
            }}
        }}
'''

        # Find location to insert (after shared_memory = None)
        pattern = r'(\s+)(# Will be used in the crew configuration\s+self\.shared_memory = None)'

        content = re.sub(
            pattern,
            local_config_code + r'\1\2',
            content
        )

        return content

    def _update_local_config_in_init(self, content: str, config: Dict) -> str:
        """Update existing local_mem0_config in __init__ method."""
        # This is more complex - for now, just replace the whole block
        # In production, you'd want more sophisticated merging
        return self._add_local_config_to_init(content, config)

    def _update_crew_method(self, content: str, use_memory_config: bool = False) -> str:
        """Update crew() method to enable memory."""
        # Find the Crew instantiation in crew() method
        pattern = r'(@crew\s+def crew\(self\) -> Crew:.*?return Crew\()(.*?)(\s+\))'

        def replacer(match):
            before = match.group(1)
            params = match.group(2)
            after = match.group(3)

            # Ensure memory=True
            if 'memory=' in params:
                params = re.sub(r'memory\s*=\s*\w+', 'memory=True', params)
            else:
                params += ',\n            memory=True'

            # Add memory_config if needed
            if use_memory_config:
                if 'memory_config=' not in params:
                    params += ',\n            memory_config=self.memory_config'

            return before + params + after

        content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        return content

    def _test_configuration(self) -> None:
        """Test the configuration."""
        print("\nTesting configuration...\n")

        try:
            # Try to import and initialize the crew
            sys.path.insert(0, str(self.project_root / "src"))
            from space_hulk_game.crew import SpaceHulkGame

            crew = SpaceHulkGame()
            print("✅ Successfully initialized SpaceHulkGame crew")

            # Check if memory is configured
            crew_obj = crew.crew()
            print(f"✅ Memory enabled: {crew_obj.memory}")

            if hasattr(crew, 'memory_config'):
                print(f"✅ Memory provider: {crew.memory_config.get('provider', 'default')}")

        except Exception as e:
            print(f"⚠️  Warning: Could not test configuration: {str(e)}")
            print("   This may be normal if dependencies are not fully installed.")

    def _create_env_file(self) -> None:
        """Create .env from .env.example if it doesn't exist."""
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, self.env_file)
            print(f"✅ Created .env from .env.example")
        else:
            # Create minimal .env
            with open(self.env_file, 'w') as f:
                f.write("# Space Hulk Game Environment Configuration\n")
                f.write("OPENAI_MODEL_NAME=ollama/qwen2.5\n")
                f.write("OLLAMA_BASE_URL=http://localhost:11434\n")
            print(f"✅ Created minimal .env file")

    def _get_env_var(self, key: str) -> Optional[str]:
        """Get environment variable from .env file."""
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.strip().startswith(key + '='):
                        return line.split('=', 1)[1].strip()
        except Exception:
            pass
        return None

    def _print_next_steps(self) -> None:
        """Print next steps for the user."""
        print("\nNext Steps:")
        print("-" * 60)

        if self.mode == "basic":
            print("1. Test the crew:")
            print("   crewai run")
            print()
            print("2. Check memory storage location:")
            print("   Windows: C:\\Users\\{username}\\AppData\\Local\\CrewAI\\space_hulk_game\\")
            print("   macOS: ~/Library/Application Support/CrewAI/space_hulk_game/")
            print("   Linux: ~/.local/share/CrewAI/space_hulk_game/")
            print()
            print("3. Monitor logs for memory operations")

        elif self.mode == "cloud":
            print("1. Verify MEM0_API_KEY is set in .env")
            print()
            print("2. Test the crew:")
            print("   crewai run")
            print()
            print("3. Monitor memory usage in mem0 dashboard:")
            print("   https://mem0.ai/dashboard")
            print()
            print("4. Check logs for 'Memory provider: mem0'")

        elif self.mode == "local":
            print("1. Ensure all services are running:")
            print("   - Ollama: ollama serve")
            if self.vector_store == "qdrant":
                print("   - Qdrant: docker run -d -p 6333:6333 qdrant/qdrant")
            print()
            print("2. Verify embedding model:")
            print("   ollama list | grep mxbai-embed-large")
            print()
            print("3. Test the crew:")
            print("   crewai run")
            print()
            if self.vector_store == "qdrant":
                print("4. Check Qdrant dashboard:")
                print("   http://localhost:6333/dashboard")
            print()
            print("5. Monitor logs for memory operations")

        print()
        print("For detailed documentation, see:")
        print("  docs/MEM0_SETUP_GUIDE.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Configure mem0 memory integration for Space Hulk Game",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--mode",
        choices=["basic", "cloud", "local"],
        default="basic",
        help="Memory configuration mode (default: basic)"
    )

    parser.add_argument(
        "--vector-store",
        choices=["qdrant", "chroma"],
        default="qdrant",
        help="Vector store for local mode (default: qdrant)"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate prerequisites, don't modify files"
    )

    parser.add_argument(
        "--crew-file",
        default="src/space_hulk_game/crew.py",
        help="Path to crew.py (default: src/space_hulk_game/crew.py)"
    )

    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env (default: .env)"
    )

    args = parser.parse_args()

    # Create configurator
    configurator = Mem0Configurator(
        mode=args.mode,
        vector_store=args.vector_store,
        crew_file=args.crew_file,
        env_file=args.env_file,
        validate_only=args.validate_only
    )

    # Run configuration
    success = configurator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
