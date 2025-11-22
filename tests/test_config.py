"""
Tests for configuration management.
"""

import os
import pytest
import tempfile
import json
import yaml
from pathlib import Path
from aimemo.config import Config

@pytest.fixture
def temp_config_files():
    """Create temporary config files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "enable_extraction": False,
            "working_memory_limit": 10,
            "extraction_confidence_threshold": 0.5
        }, f)
        json_path = f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "enable_categorization": False,
            "db_path": "custom.db"
        }, f)
        yaml_path = f.name
        
    yield json_path, yaml_path
    
    Path(json_path).unlink(missing_ok=True)
    Path(yaml_path).unlink(missing_ok=True)


def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert config.db_path == "aimemo.db"
    assert config.enable_extraction is True
    assert config.enable_categorization is True
    assert config.working_memory_limit == 5
    assert config.extraction_confidence_threshold == 0.8


def test_env_config():
    """Test loading from environment variables."""
    os.environ["AIMEMO_DB_PATH"] = "env.db"
    os.environ["AIMEMO_ENABLE_EXTRACTION"] = "false"
    os.environ["AIMEMO_WORKING_MEMORY_LIMIT"] = "20"
    
    try:
        config = Config.from_env()
        assert config.db_path == "env.db"
        assert config.enable_extraction is False
        assert config.working_memory_limit == 20
        # Defaults should remain
        assert config.enable_categorization is True
    finally:
        # Cleanup
        del os.environ["AIMEMO_DB_PATH"]
        del os.environ["AIMEMO_ENABLE_EXTRACTION"]
        del os.environ["AIMEMO_WORKING_MEMORY_LIMIT"]


def test_load_from_json(temp_config_files):
    """Test loading from JSON file."""
    json_path, _ = temp_config_files
    
    config = Config.load_from_file(json_path)
    
    assert config.enable_extraction is False
    assert config.working_memory_limit == 10
    assert config.extraction_confidence_threshold == 0.5
    # Default should remain
    assert config.enable_categorization is True


def test_load_from_yaml(temp_config_files):
    """Test loading from YAML file."""
    _, yaml_path = temp_config_files
    
    config = Config.load_from_file(yaml_path)
    
    assert config.enable_categorization is False
    assert config.db_path == "custom.db"
    # Default should remain
    assert config.enable_extraction is True


def test_load_missing_file():
    """Test loading from non-existent file."""
    with pytest.raises(FileNotFoundError):
        Config.load_from_file("non_existent.json")


def test_load_invalid_extension():
    """Test loading from unsupported extension."""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"dummy content")
        txt_path = f.name
        
    try:
        with pytest.raises(ValueError):
            Config.load_from_file(txt_path)
    finally:
        Path(txt_path).unlink(missing_ok=True)
