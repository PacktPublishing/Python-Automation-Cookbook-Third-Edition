# SQLite MCP Server

This repository contains an MCP (Model Context Protocol) server written in Python that connects to a SQLite database containing startup funding data. The server exposes table schemas as resources, provides a read-only SQL query tool, and offers prompt templates for common data analysis tasks. It is designed to work with MCP clients and language models (LLMs) and communicates via the STDIO protocol.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Setup and Installation](#setup-and-installation)
  - [Creating the Sample SQLite Database](#creating-the-sample-sqlite-database)
  - [Creating a Virtual Environment](#creating-a-virtual-environment)
  - [Running the MCP Server](#running-the-mcp-server)
  - [Installing into Claude Desktop](#installing-into-claude-desktop)
- [Usage](#usage)
- [Testing](#testing)
- [Logging](#logging)
- [License](#license)

---

## Overview

The MCP server uses the [MCP Python SDK](https://pypi.org/project/mcp/) (with CLI extras) to implement a server that:

- **Connects to a SQLite database** (e.g., a database with startup funding information).
- **Exposes table schemas as MCP resources.**
- **Provides a tool for executing read-only SQL queries.**
- **Offers prompt templates** that help language models generate data analysis insights.
- **Communicates via the STDIO protocol**, reading JSON-RPC messages from standard input and writing responses to standard output.

---

## Features

- **Resources**
  - `schema://sqlite/{table}`: Returns the SQL schema for a specific table.
  - `schema://sqlite/all`: Returns a JSON mapping of all table schemas.

- **Tools**
  - `sql_query`: Executes read-only SQL queries. Only `SELECT` statements are permitted.

- **Prompts**
  - `analyze_table_prompt`: Generates an analysis prompt for a specific table.
  - `describe_query_prompt`: Generates a prompt explaining a SQL query.

- **STDIO Protocol**
  - Reads from `stdin` and writes responses to `stdout`, making integration easy.

- **Logging**
  - Uses Python’s `logging` module to trace activity and debug errors.

---

## Setup and Installation

### Creating the Sample SQLite Database

Save the following script as `create_db.py`:

```python
<same as earlier>
```

Run with:

```bash
python create_db.py
```

### Creating a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

- **Windows**:
  ```cmd
  venv\Scripts\activate
  ```

Install dependencies:

```bash
pip install "mcp[cli]"
```

### Running the MCP Server

1. Save your server code as `sqlite_mcp_server.py`.
2. Run the server:

```bash
python sqlite_mcp_server.py
```

Optional (using `uv`):

```bash
uv run sqlite_mcp_server.py
```

### Installing into Claude Desktop

Save the following as `install_to_claude.py` and run it:

```bash
python install_to_claude.py
```

Update Claude Desktop config with:

```json
{
  "mcpServers": {
    "sqlite_mcp_server": {
      "command": "python",
      "args": ["-u", "/absolute/path/to/sqlite_mcp_server.py"]
    }
  }
}
```

Restart Claude Desktop afterward.

---

## Usage

- **Access Resources**: `schema://sqlite/all`, `schema://sqlite/startups`
- **Invoke Tools**:
  ```sql
  SELECT * FROM startups WHERE funding_amount > 10000000;
  ```
- **Use Prompts**: Generate SQL or explain queries.

---

## Testing

Run the test script:

```bash
python sqlite_mcp_client_tests.py sqlite_mcp_server.py
```

This script tests:

- Listing resources
- Retrieving schemas
- Valid/invalid queries
- Prompt templates

---

## Logging

Modify logging config:

```python
logging.basicConfig(
    filename='mcp_server.log',
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
```

Logs print to stderr by default.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file.

---

## Additional Notes

- Adjust paths in installation/config scripts as needed.
- Ensure the SQLite database is created before running the server.
- Integrates with MCP Inspector or Claude Desktop.
