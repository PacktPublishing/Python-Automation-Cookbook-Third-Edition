#!/usr/bin/env python3
"""
Installation Script for MCP Server in Claude Desktop

This script adds (or updates) a Claude Desktop configuration file entry that
instructs Claude to launch our MCP server script.
It does the following:
  1. Determines the correct path to the Claude configuration file.
  2. Reads the existing configuration or creates a new configuration if none exists.
  3. Inserts an entry under "mcpServers" for our SQLite MCP Server.
  4. Writes the updated configuration back to disk.

After running this script, Claude Desktop will automatically detect and launch
your MCP server when it starts.
"""

import os
import sys
import json
from pathlib import Path
import logging

# Set up a basic logger for this installation script.
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("install_claude_server")

def get_claude_config_path() -> Path:
    """
    Determine the location of the Claude Desktop configuration file based on the OS.
    
    Returns:
        A Path object pointing to the configuration file.
    """
    if sys.platform.startswith("win"):
        # On Windows, the config file is typically stored in %APPDATA%\Claude
        appdata = os.getenv("APPDATA")
        if not appdata:
            logger.error("APPDATA environment variable not set. Cannot locate configuration.")
            sys.exit(1)
        config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif sys.platform.startswith("darwin"):
        # On macOS, the config file is typically in the user's Library/Application Support
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        # On Linux or other OS - adjust if necessary (Claude Desktop is primarily for macOS and Windows)
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    
    logger.debug(f"Determined Claude configuration path: {config_path}")
    return config_path

def install_server_entry(server_name: str, command: str, args: list[str], env: dict[str, str] | None = None) -> None:
    """
    Install or update an MCP server entry in the Claude Desktop configuration file.
    
    Args:
        server_name: Identifier for your MCP server.
        command: The command to run (e.g. "python" to invoke your MCP server).
        args: List of command-line arguments (e.g. ["-u", "/path/to/sqlite_mcp_server.py"]).
        env: Optional dictionary of environment variables.
    """
    config_path = get_claude_config_path()
    logger.info(f"Using Claude config file at: {config_path}")

    # Ensure the directory exists.
    if not config_path.parent.exists():
        logger.debug(f"Creating configuration directory: {config_path.parent}")
        config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing configuration if present; otherwise, start fresh.
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.debug("Loaded existing Claude configuration.")
        except json.JSONDecodeError:
            logger.error("Existing configuration file is not valid JSON. Exiting.")
            sys.exit(1)
    else:
        config = {}
        logger.info("No existing configuration found; creating a new one.")

    # Ensure there is a key for MCP servers.
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        logger.debug("Created new 'mcpServers' key in configuration.")

    # Insert or update the entry for our MCP server.
    config["mcpServers"][server_name] = {
        "command": command,
        "args": args,
    }
    if env:
        config["mcpServers"][server_name]["env"] = env
        logger.debug("Set environment variables for the MCP server entry.")

    # Write the updated configuration back to the file.
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        logger.info(f"Successfully installed MCP server '{server_name}' in Claude configuration.")
    except Exception as e:
        logger.exception(f"Failed to write configuration file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Identifier for our MCP server; you can adjust this as desired.
    server_name = "sqlite_mcp_server"
    
    # Determine the absolute path of your MCP server script.
    # This example assumes the MCP server script (sqlite_mcp_server.py) is in the same directory as this installer.
    this_dir = Path(__file__).parent.resolve()
    server_script_path = str((this_dir / "sqlite_sdio_mcp_server.py").resolve())
    logger.debug(f"MCP server script absolute path: {server_script_path}")
    
    # Define the command to run your MCP server.
    # The "-u" flag is used for unbuffered output, which ensures that logging appears promptly.
    command = "python"
    args = ["-u", server_script_path]
    
    # Optionally, define environment variables needed by your server.
    # For example, you might include database credentials or API keys here.
    env = {}  # Leave empty if not needed.
    
    # Install the server entry into the Claude Desktop configuration.
    install_server_entry(server_name, command, args, env)