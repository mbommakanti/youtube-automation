import os
import json
import yaml
from typing import Any, Optional
from pathlib import Path

class Config:
    """Configuration management class with singleton pattern"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.environment = os.environ.get('APP_ENV', 'local')
        self._config_data = self._load_config()
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_config(self) -> dict:
        """Load configuration from YAML files based on environment"""
        # Look for config directory relative to project root
        current_dir = Path(__file__).parent
        config_dir = current_dir / '../../config'  # Go up to project root, then to config
        
        # Resolve the path to handle relative paths properly
        config_dir = config_dir.resolve()
        
        # Load default config first
        default_config = {}
        default_config_file = config_dir / 'config_default.yaml'
        
        if default_config_file.exists():
            try:
                with open(default_config_file, 'r') as f:
                    default_config = yaml.safe_load(f) or {}
                print(f"Loaded default config from: {default_config_file}")
            except Exception as e:
                print(f"Warning: Could not load default config: {e}")
        
        # Load environment-specific config
        env_config = {}
        env_config_file = config_dir / f'config_{self.environment}.yaml'
        
        if env_config_file.exists():
            try:
                with open(env_config_file, 'r') as f:
                    env_config = yaml.safe_load(f) or {}
                print(f"Loaded environment config from: {env_config_file}")
            except Exception as e:
                print(f"Warning: Could not load environment config: {e}")
        else:
            print(f"Warning: No environment config found for '{self.environment}' at {env_config_file}")
        
        # Merge configs: environment config overrides default config
        config_data = self._merge_configs(default_config, env_config)
        
        # If no config loaded, use fallback defaults
        if not config_data:
            print(f"Warning: No config files found, using fallback defaults")
            config_data = self._get_default_config()
        
        return config_data
    
    def _merge_configs(self, default: dict, override: dict) -> dict:
        """Recursively merge two configuration dictionaries"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _get_default_config(self) -> dict:
        """Fallback default configuration"""
        defaults = {
            'local': {
                'log_level': 'DEBUG',
                'log_handler': 'console',
                'log_file_path': 'logs/app.log',
                'should_create_log_folder': True,
            },
            'development': {
                'log_level': 'DEBUG',
                'log_handler': 'console',
                'log_file_path': None,
                'should_create_log_folder': False,
            },
            'production': {
                'log_level': 'INFO',
                'log_handler': 'console',
                'log_file_path': None,
                'should_create_log_folder': False,
            }
        }
        
        return defaults.get(self.environment, defaults['local'])
    
    @property
    def log_level(self) -> str:
        """Get log level"""
        return self._config_data.get('log_level', 'INFO')
    
    @property
    def log_handler(self) -> str:
        """Get log handler type"""
        return self._config_data.get('log_handler', 'console')
    
    @property
    def log_file_path(self) -> Optional[str]:
        """Get log file path"""
        return self._config_data.get('log_file_path')
    
    @property
    def should_create_log_folder(self) -> bool:
        """Check if log folder should be created"""
        return self._config_data.get('should_create_log_folder', False)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation"""
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
