[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/entanglr-laravel-artisan-mcp-badge.png)](https://mseep.ai/app/entanglr-laravel-artisan-mcp)

# Laravel Artisan MCP Server

A Model Context Protocol (MCP) server that enables secure execution of Laravel Artisan commands through Claude and other MCP clients. This server acts as a bridge between AI assistants and your **local** Laravel applications, allowing controlled management of Laravel projects through natural language conversations.

## Features

- Access a single directory containing a Laravel project
- Automatically locate PHP on your system
- Execute only whitelisted Artisan commands
- View all available Artisan commands
- Secure by design with robust input validation

## Examples

![Example](https://github.com/diggy/laravel-artisan-mcp/raw/main/images/example.jpg)

## Requirements

- Python 3.10 or higher
- Laravel project with Artisan CLI
- PHP installed and accessible in your PATH
- MCP-compatible client (such as Claude Desktop)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/diggy/laravel-artisan-mcp.git
   cd laravel-artisan-mcp
   ```

2. Create a virtual environment:
   ```bash
   uv init
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv add "mcp[cli]"
   ```

## Configuration

The server requires the following environment variables:

- `ARTISAN_DIRECTORY`: Absolute path to the Laravel project containing the Artisan executable
- `WHITELISTED_COMMANDS`: Comma-separated list of allowed Artisan commands (e.g., `route:list,cache:clear,make:controller` or any default or custom Commands registered in your Laravel application)

You can provide these variables in several ways:

1. Directly in the command line:
   ```bash
   ARTISAN_DIRECTORY="/absolute/path/to/your/laravel/project" WHITELISTED_COMMANDS="route:list,cache:clear,make:controller" uv run artisan_mcp_server.py
   ```

2. Using a `.env` file:
   ```
   ARTISAN_DIRECTORY=/absolute/path/to/your/laravel/project
   WHITELISTED_COMMANDS=route:list,cache:clear,make:controller
   ```

3. In the Claude Desktop configuration (cf. section on Claude Integration below)

## Testing with MCP Inspector

The MCP Inspector provides a graphical interface for testing your server before integrating it with Claude:

```bash
# Run with direct environment variables
ARTISAN_DIRECTORY="/absolute/path/to/your/laravel/project" WHITELISTED_COMMANDS="route:list,cache:clear,make:controller" uv run mcp dev artisan_mcp_server.py

# Or using an env file
uv run mcp dev artisan_mcp_server.py --env-file .env
```

Once the Inspector is running:

1. Open the web interface at http://localhost:5173
2. Explore the "Resources" tab to see available resources
3. Test the tools under the "Tools" tab:
   - `list_available_artisan_commands`: Shows all whitelisted commands in your Laravel project
   - `run_artisan`: Executes a specific command (must be whitelisted)

## Claude Integration

To use this server with Claude Desktop:

1. Ensure Claude Desktop is installed

2. Edit the Claude Desktop configuration file:

   **macOS**:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   **Windows**:
   ```powershell
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

3. Add the following configuration (adjust paths as needed):

   ```json
   {
     "mcpServers": {
       "laravel-artisan": {
         "command": "uv",
         "args": [
           "--directory", 
           "/absolute/path/to/laravel-artisan-mcp",
           "run", 
           "artisan_mcp_server.py"
         ],
         "env": {
           "ARTISAN_DIRECTORY": "/absolute/path/to/your/laravel/project",
           "WHITELISTED_COMMANDS": "route:list,cache:clear,make:controller"
         }
       }
     }
   }
   ```

4. Restart Claude Desktop

## Available Tools

### `run_artisan`

Executes a whitelisted Artisan command.

**Parameters:**
- `command`: The Artisan command to run (e.g., 'cache:clear')

**Example usage in Claude:**
"Run the route:list command to show all available routes in my Laravel app."

### `list_available_artisan_commands`

Displays all available whitelisted Artisan commands in the Laravel application.

**Example usage in Claude:**
"Show me all available Artisan commands."

## Security Considerations

This server implements several security measures (according to Claude):

- **Directory Isolation**: Only accesses the explicitly configured Laravel directory
- **Command Whitelisting**: Only executes commands that are specifically allowed
- **Input Validation**: Verifies all inputs before execution
- **Error Handling**: Prevents sensitive information leakage

## Troubleshooting

### "ARTISAN_DIRECTORY must be provided in configuration"

The server cannot find the path to your Laravel project. Check that:
- The environment variable is properly set
- The directory exists and is accessible

### "Artisan not found at: /path/to/artisan"

The specified directory does not contain the Artisan executable. Verify that:
- The path points to a valid Laravel project directory
- The Artisan file exists and has executable permissions

### "PHP executable not found"

The server cannot find PHP in your PATH. Ensure that:
- PHP is installed on your system
- The PHP executable is in your system PATH

## Disclaimer

This Laravel Artisan MCP Server is provided as-is, without any warranties or guarantees of any kind. By using this software, you assume all risks associated with its operation. The server has access to execute commands within your Laravel environment, which could potentially impact your application data and functionality. We strongly recommend using this tool only in development or testing environments. Use this server with production Laravel applications only if you fully understand the security implications and have implemented appropriate safeguards. Always maintain proper backups of your Laravel project before allowing AI assistants to execute Artisan commands through this interface. The authors and contributors of this software cannot be held responsible for any damages, data loss, or security breaches that may result from the use or misuse of this tool. You are solely responsible for configuring appropriate command whitelisting and access controls. This software has not undergone formal security auditing and should be considered experimental. Use at your own risk.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

This MCP server was crafted with assistance from Claude, Anthropic's AI assistant (who insisted on adding this humble credit while promising it wouldn't include smiley emoticons or excessive enthusiasm).