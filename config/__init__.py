import os
import yaml
import json
import types
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Professional configuration management with environment-specific overrides."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_config()
            Config._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get the singleton configuration instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_config(self):
        """Load and merge configuration files."""
        try:
            # Load base configuration
            base_config = self._load_yaml_file('config/config_default.yaml')
            
            # Detect environment and load overrides
            environment = self._detect_environment()
            env_config = self._load_environment_config(environment)
            
            # Deep merge configurations
            merged_config = self._deep_merge(base_config, env_config)
            
            # Convert to dot notation access
            self.config = self._dict_to_namespace(merged_config)
            self.environment = environment
            
            logger.info(f"Configuration loaded for environment: {environment}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            # Fallback to minimal config
            self.config = self._get_fallback_config()
            self.environment = 'fallback'
    
    def _detect_environment(self):
        """Detect current environment from APP_ENV variable."""
        return os.environ.get('APP_ENV', 'local').lower()
    
    def _load_yaml_file(self, filepath):
        """Load a YAML file safely."""
        try:
            config_path = Path(filepath)
            if not config_path.exists():
                logger.warning(f"Config file not found: {filepath}")
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
                
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {filepath}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return {}
    
    def _load_environment_config(self, environment):
        """Load environment-specific configuration."""
        env_file = f'config/config_{environment}.yaml'
        return self._load_yaml_file(env_file)
    
    def _deep_merge(self, base_dict, override_dict):
        """Recursively merge dictionaries with override precedence."""
        if not isinstance(override_dict, dict):
            return base_dict
        
        result = base_dict.copy()
        
        for key, value in override_dict.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_namespace(self, config_dict):
        """Convert nested dictionary to SimpleNamespace for dot notation."""
        try:
            return json.loads(
                json.dumps(config_dict), 
                object_hook=lambda d: types.SimpleNamespace(**d)
            )
        except Exception as e:
            logger.error(f"Failed to convert config to namespace: {e}")
            return types.SimpleNamespace()
    
    def _get_fallback_config(self):
        """Provide minimal fallback configuration."""
        fallback = {
            'logging': {
                'level': 'INFO',
                'handler': 'console',
                'create_folder': False,
                'file_path': None
            }
        }
        return self._dict_to_namespace(fallback)
    
    # Industry standard: Provide commonly used config as properties
    @property
    def log_level(self):
        """Get logging level with validation."""
        try:
            level = self.config.logging.level
            valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
            if level.upper() in valid_levels:
                return level.upper()
            else:
                logger.warning(f"Invalid log level '{level}', using INFO")
                return 'INFO'
        except AttributeError:
            return 'INFO'
    
    @property
    def log_handler(self):
        """Get logging handler type."""
        try:
            return self.config.logging.handler
        except AttributeError:
            return 'console'
    
    @property
    def log_file_path(self):
        """Get log file path."""
        try:
            return self.config.logging.file_path
        except AttributeError:
            return None
    
    @property
    def should_create_log_folder(self):
        """Check if log folder should be created."""
        try:
            return bool(self.config.logging.create_folder)
        except AttributeError:
            return False
    
    def get_config_value(self, path, default=None):
        """Generic method to get any config value by dot notation path."""
        try:
            parts = path.split('.')
            current = self.config
            
            for part in parts:
                current = getattr(current, part)
            
            return current
        except AttributeError:
            logger.debug(f"Config path '{path}' not found, using default: {default}")
            return default
    
    def __repr__(self):
        return f"Config(environment='{self.environment}')"