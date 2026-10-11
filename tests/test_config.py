import pytest
from src.config import ConfigManager

def test_config_defaults(tmp_path):
    config_file = tmp_path / "config.json"
    cfg = ConfigManager(str(config_file))
    data = cfg.load()
    assert data["x"] == 100
    assert data["y"] == 100
    assert data["hotkey"] == "F9"
    assert data["update_interval_ms"] == 1000
    assert data["locked"] is True

def test_config_save_and_update(tmp_path):
    config_file = tmp_path / "config.json"
    cfg = ConfigManager(str(config_file))
    cfg.set("x", 450)
    cfg.set("y", 220)
    cfg.save()
    
    cfg2 = ConfigManager(str(config_file))
    assert cfg2.get("x") == 450
    assert cfg2.get("y") == 220
