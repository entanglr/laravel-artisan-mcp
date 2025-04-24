from mcp.server.fastmcp import FastMCP, Context
import os
import subprocess
import shlex
import shutil
import logging
from typing import List, Dict
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("artisan-mcp")

# Default configuration
DEFAULT_CONFIG = {
    "artisan_directory": None,  # Must be provided
    "whitelisted_commands": [],  # Empty by default (no commands allowed)
}

# Global config storage
config = DEFAULT_CONFIG.copy()

def load_config(env_vars: Dict) -> Dict:
    """Load configuration from environment variables"""
    global config
    
    # Required configuration
    artisan_directory = env_vars.get("ARTISAN_DIRECTORY")
    if not artisan_directory:
        raise ValueError("ARTISAN_DIRECTORY must be provided in configuration")
    
    # Validate the directory exists
    if not os.path.isdir(artisan_directory):
        raise ValueError(f"Directory not found: {artisan_directory}")
    
    # Validate artisan file exists in the directory
    artisan_path = os.path.join(artisan_directory, "artisan")
    if not os.path.isfile(artisan_path):
        raise ValueError(f"Artisan not found at: {artisan_path}")
    
    # Parse whitelisted commands
    whitelisted_commands = []
    whitelist_str = env_vars.get("WHITELISTED_COMMANDS", "")
    if whitelist_str:
        whitelisted_commands = [cmd.strip() for cmd in whitelist_str.split(",")]
    
    config = {
        "artisan_directory": artisan_directory,
        "whitelisted_commands": whitelisted_commands,
    }
    
    logger.info(f"Loaded configuration: {config}")
    return config

def find_php_executable() -> str:
    """Find the PHP executable on the system"""
    php_path = shutil.which("php")
    if not php_path:
        raise ValueError("PHP executable not found. Please ensure PHP is installed and in your PATH.")
    return php_path

@dataclass
class AppContext:
    artisan_directory: str
    whitelisted_commands: List[str]
    php_path: str

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with typed context"""
    # Get environment variables
    env_vars = dict(os.environ)
    
    try:
        config = load_config(env_vars)
        php_path = find_php_executable()
        
        logger.info(f"Server initialized with artisan directory: {config['artisan_directory']}")
        logger.info(f"Whitelisted commands: {config['whitelisted_commands']}")
        logger.info(f"PHP executable: {php_path}")
        
        yield AppContext(
            artisan_directory=config['artisan_directory'],
            whitelisted_commands=config['whitelisted_commands'],
            php_path=php_path
        )
    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}")
        raise

# Create the MCP server with lifespan
mcp = FastMCP("Laravel Artisan", lifespan=app_lifespan)

@mcp.tool()
def run_artisan(command: str) -> str:
    """
    Run a Laravel Artisan command in the configured directory.
    
    Args:
        command: The Artisan command to run (e.g., 'route:list', 'cache:clear')
    
    Returns:
        The output from the Artisan command
    """
    global config
    
    # Validate the command is whitelisted
    if not any(command.startswith(cmd) for cmd in config["whitelisted_commands"]):
        allowed_commands = ", ".join(config["whitelisted_commands"])
        return f"Error: Command '{command}' is not whitelisted. Allowed commands: {allowed_commands}"
    
    # Build the full command
    php_path = find_php_executable() 
    artisan_path = os.path.join(config["artisan_directory"], "artisan")
    
    # shlex.split properly handles quoted strings and escaping
    args = shlex.split(command)
    full_command = [php_path, artisan_path] + args
    
    # Log the command being executed
    logger.info(f"Executing: {' '.join(full_command)}")
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            full_command,
            cwd=config["artisan_directory"],
            capture_output=True,
            text=True,
            check=False  # Don't raise an exception on non-zero exit
        )
        
        # Check for execution errors
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or f"Command exited with status {result.returncode}"
            return f"Error executing command: {error_msg}"
        
        return result.stdout
    except Exception as e:
        logger.error(f"Failed to execute command: {str(e)}")
        return f"Error executing command: {str(e)}"

@mcp.tool()
def list_available_artisan_commands() -> str:
    """List all whitelisted Artisan commands"""
    # Use global config instead of context
    global config
    
    if not config["whitelisted_commands"]:
        return "No commands are whitelisted in the current configuration."
    
    return "Whitelisted Artisan commands:\n" + "\n".join(
        f"- {cmd}" for cmd in config["whitelisted_commands"]
    )

# Run the server if this script is executed directly
if __name__ == "__main__":
    mcp.run()
