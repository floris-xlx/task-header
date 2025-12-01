"""
Configuration management for the Linear Task Header application.
Handles storing and retrieving API keys, hotkeys, and window preferences.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to config file. Defaults to ~/.linear_task_header_config.json
        """
        if config_path is None:
            config_path = os.path.join(
                str(Path.home()), 
                ".linear_task_header_config.json"
            )
        
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "linear_api_key": "",
            "hotkey": "ctrl+w",
            "window": {
                "width_percent": 10,
                "height_percent": 10,
                "position": "top-middle"
            },
            "current_issue_id": None,
            "font_size": 40,
            "markdown": {
                "auto_generate": True,
                "sync_on_edit": True,
                "output_dir": "."
            }
        }
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'window.width_percent')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    @property
    def linear_api_key(self) -> str:
        """Get Linear API key."""
        return self.get("linear_api_key", "")
    
    @linear_api_key.setter
    def linear_api_key(self, value: str) -> None:
        """Set Linear API key."""
        self.set("linear_api_key", value)
    
    @property
    def hotkey(self) -> str:
        """Get hotkey combination."""
        return self.get("hotkey", "ctrl+w")
    
    @hotkey.setter
    def hotkey(self, value: str) -> None:
        """Set hotkey combination."""
        self.set("hotkey", value)
    
    @property
    def current_issue_id(self) -> Optional[str]:
        """Get current issue ID."""
        return self.get("current_issue_id")
    
    @current_issue_id.setter
    def current_issue_id(self, value: Optional[str]) -> None:
        """Set current issue ID."""
        self.set("current_issue_id", value)
    
    @property
    def font_size(self) -> int:
        """Get font size for issue display."""
        return self.get("font_size", 40)
    
    @font_size.setter
    def font_size(self, value: int) -> None:
        """Set font size for issue display."""
        self.set("font_size", value)

