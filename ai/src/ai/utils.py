import os
import logging
import threading
import time
import re
import json
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MissingEnvironmentVariableError(Exception):
    """Custom exception for missing environment variables."""
    def __init__(self, env_var_name: str):
        self.env_var_name = env_var_name
        super().__init__(f"Missing required environment variable: {env_var_name}")

class InvalidEnvironmentVariableError(Exception):
    """Custom exception for invalid environment variables."""
    def __init__(self, env_var_name: str, reason: str):
        self.env_var_name = env_var_name
        self.reason = reason
        super().__init__(f"Invalid environment variable {env_var_name}: {reason}")

class MissingEnvFileError(Exception):
    """Custom exception for missing environment file."""
    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Missing required environment file: {file_path}")

class InvalidEnvValueError(Exception):
    """Custom exception for invalid environment values."""
    def __init__(self, env_var_name: str, reason: str):
        self.env_var_name = env_var_name
        self.reason = reason
        super().__init__(f"Invalid value for environment variable {env_var_name}: {reason}")

class Environment:
    _loaded = False
    _env_cache: Dict[str, Optional[str]] = {}
    _lock = threading.RLock()
    _last_load_time = 0
    _immutable = False
    _default_config = {}
    _env_source_priorities = ['.env.local', '.env', 'env']
    _cache_expiration_time = 300

    @staticmethod
    def _load_env_files(dotenv_paths: Optional[list] = None) -> None:
        """
        Loads environment variables from multiple .env files in a prioritized order.
        
        :param dotenv_paths: List of custom paths for .env files to load.
        """
        if dotenv_paths is None:
            dotenv_paths = Environment._env_source_priorities

        for dotenv_path in dotenv_paths:
            if os.path.exists(dotenv_path):
                logger.info(f"Loading .env file from: {dotenv_path}")
                with open(dotenv_path) as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
            else:
                logger.warning(f"Environment file not found: {dotenv_path}")

    @staticmethod
    def load_env(force_reload=False, dotenv_paths: Optional[list] = None) -> None:
        """
        Loads environment variables from .env files in the specified order.

        :param force_reload: Forces reloading of the .env files and cache.
        :param dotenv_paths: List of custom paths for .env files.
        """
        if Environment._immutable:
            logger.debug("Environment configuration is immutable, skipping load.")
            return

        with Environment._lock:
            current_time = time.time()
            if not Environment._loaded or force_reload or (current_time - Environment._last_load_time) > Environment._cache_expiration_time:
                Environment._load_env_files(dotenv_paths)
                Environment._loaded = True
                Environment._last_load_time = current_time
            else:
                logger.debug("Environment variables already loaded and up-to-date.")

    @staticmethod
    def set_default_config(default_config: Dict[str, Any]) -> None:
        """
        Sets default configuration to be used as a fallback when environment variables are missing.

        :param default_config: A dictionary of default configuration.
        """
        Environment._default_config = default_config

    @staticmethod
    def get_env_variable(env_var_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves an environment variable, checking multiple sources (system variables, .env files, and defaults).

        :param env_var_name: The environment variable name to fetch.
        :param default: The default value to return if the variable is not found.
        :return: The value of the environment variable, or default if not found.
        """
        if env_var_name in Environment._env_cache:
            logger.debug(f"Using cached value for {env_var_name}")
            return Environment._env_cache[env_var_name]

        Environment.load_env()

        api_key = os.getenv(env_var_name)
        
        if api_key:
            logger.debug(f"Found {env_var_name} in system environment variables.")
        else:
            api_key = os.getenv(env_var_name, default)

            if api_key:
                logger.debug(f"Found {env_var_name} in .env files.")
            else:
                api_key = Environment._default_config.get(env_var_name, default)
                logger.debug(f"Using default fallback for {env_var_name}.")
            
        Environment._env_cache[env_var_name] = api_key
        return api_key

    @staticmethod
    def validate_api_key(api_key: Optional[str], env_var_name: str) -> None:
        """
        Validates the retrieved API key to ensure it is not empty and matches expected format.

        :param api_key: The API key value.
        :param env_var_name: The name of the environment variable.
        :raises InvalidEnvironmentVariableError: If the key is invalid.
        """
        if not api_key:
            logger.error(f"{env_var_name} is missing or empty!")
            raise MissingEnvironmentVariableError(env_var_name)
        
        if not re.match(r'^[A-Za-z0-9_]+$', api_key):
            logger.error(f"{env_var_name} is invalid. Expected alphanumeric format.")
            raise InvalidEnvironmentVariableError(env_var_name, "Expected alphanumeric format.")
    
    @staticmethod
    def get_api_key(env_var_name: str, default: Optional[str] = None, validate: bool = True) -> Optional[str]:
        """
        Retrieves an API key from the environment variables, using caching for improved performance.
        
        :param env_var_name: The name of the environment variable to fetch.
        :param default: An optional default value to return if the environment variable is not found.
        :param validate: Whether to validate the key format.
        :return: The value of the environment variable, or the default value if not found.
        """
        api_key = Environment.get_env_variable(env_var_name, default)

        if validate:
            Environment.validate_api_key(api_key, env_var_name)
        
        return api_key

    @staticmethod
    def get_required_api_key(env_var_name: str) -> str:
        """
        Retrieves a required API key, raises an error if not found or if the value is empty.
        
        :param env_var_name: The name of the environment variable to fetch.
        :return: The value of the environment variable.
        :raises MissingEnvironmentVariableError: If the environment variable is not found or is empty.
        """
        api_key = Environment.get_api_key(env_var_name)
        if not api_key:
            raise MissingEnvironmentVariableError(env_var_name)
        return api_key

    @staticmethod
    def make_immutable() -> None:
        """
        Makes the environment configuration immutable, preventing further loading or changes.
        """
        Environment._immutable = True
        logger.debug("Environment configuration is now immutable.")

def pretty_print_result(result: str, line_length: int = 80, format_json: bool = False) -> str:
    """
    Formats a long string into lines of a specified maximum length, making it easier to read.
    Optionally formats JSON output for readability.

    :param result: The string to be formatted.
    :param line_length: The maximum length of each line. Defaults to 80 characters.
    :param format_json: Whether to format the output as pretty JSON (default False).
    :return: A string with formatted lines.
    """
    if format_json:
        try:
            parsed_json = json.loads(result)
            return json.dumps(parsed_json, indent=4)
        except json.JSONDecodeError:
            logger.warning("Failed to format result as JSON.")
    
    logger.debug(f"Pretty printing result with max line length: {line_length}")
    return "\n".join(_wrap_text(line, line_length) for line in result.split('\n'))

def _wrap_text(text: str, line_length: int) -> str:
    """Helper function to wrap long lines."""
    wrapped_lines = []
    current_line = ""
    for word in text.split(' '):
        if len(current_line) + len(word) + 1 > line_length:
            wrapped_lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += ' ' + word
            else:
                current_line = word
    wrapped_lines.append(current_line)
    return "\n".join(wrapped_lines)

