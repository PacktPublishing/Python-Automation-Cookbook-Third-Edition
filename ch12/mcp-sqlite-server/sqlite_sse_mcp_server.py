#!/usr/bin/env python3
"""
SQLite MCP Server (SSE Implementation with Extensive Comments)

This server connects to a SQLite database and exposes MCP resources, tools, and prompts 
over Server-Sent Events (SSE) via an ASGI application. Detailed logging and comments are 
provided to explain the entire flow for ease of understanding and debugging.

Usage:
    Run the server using an ASGI server such as Uvicorn:
      uvicorn sqlite_mcp_server:app --host 0.0.0.0 --port 8000

Dependencies:
    - mcp (MCP Python SDK)
    - uvicorn
    - sqlite3 (standard library)
    - logging (standard library)
"""

import sqlite3  # SQLite DB library
import json  # For converting data to JSON format
import logging  # For logging and debugging messages
import uvicorn  # ASGI server to run the SSE app
import sys

# Import MCP server components from the MCP Python SDK.
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage, Message

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------
# Configure logging to output debug information, format messages, and include timestamps.
logging.basicConfig(
    level=logging.DEBUG,  # Setting the logging level to DEBUG for detailed output.
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",  # Log format includes time, level, name and message.
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format for the logs.
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to stdout
        logging.FileHandler("sqlite_sse_mcp_server.log"),  # Also log to a file
    ]
)
logger = logging.getLogger("sqlite_mcp_server")
logger.debug("Logging is configured.")

# Add a special console message to verify logging is working
print("STARTING SERVER: Check logs in sqlite_sse_mcp_server.log and console output")

# ------------------------------------------------------------------------------
# Database Connection
# ------------------------------------------------------------------------------
# Set the path to the SQLite database file. Change as needed.
DB_PATH = "/Users/prayank/code/mcp-gpt-implementation/startups.db"

try:
    # Connect to the SQLite database; disable thread check since this server is asynchronous.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Set row_factory to sqlite3.Row so that rows can be accessed like dictionaries.
    conn.row_factory = sqlite3.Row
    logger.info(f"Connected to SQLite database at '{DB_PATH}'.")
except Exception as e:
    # Log any errors in connecting to the database and raise the exception.
    logger.exception(f"Failed to connect to database '{DB_PATH}': {e}")
    raise

# ------------------------------------------------------------------------------
# MCP Server Initialization
# ------------------------------------------------------------------------------
# Create an instance of FastMCP with a specified name for the server.
mcp = FastMCP("SQLite MCP Server (SSE)")
logger.debug("Initialized MCP server instance.")

# ------------------------------------------------------------------------------
# MCP Resources
# ------------------------------------------------------------------------------
# Resources are used to expose data (e.g., database schema) in a read-only manner.

@mcp.resource("schema://sqlite/{table}")
def get_table_schema(table: str) -> str:
    """
    Retrieve the SQL 'CREATE TABLE' statement for a specific table in the database.
    
    Args:
        table: The name of the table whose schema is to be retrieved.
    
    Returns:
        A string containing the SQL schema or an error message.
    """
    logger.debug(f"Entering get_table_schema() with table = '{table}'")
    try:
        # Query the SQLite internal table sqlite_master to get the table creation SQL statement.
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        row = cursor.fetchone()
        if row:
            schema_sql = row["sql"]  # Retrieve the SQL statement from the row.
            logger.debug(f"Found schema for table '{table}': {schema_sql}")
            result = schema_sql
        else:
            result = f"Table '{table}' not found."
            logger.warning(result)
    except Exception as e:
        # Log exception and prepare an error message.
        result = f"Error retrieving schema for table '{table}': {e}"
        logger.exception(result)
    logger.debug(f"Exiting get_table_schema() with result: {result}")
    return result

@mcp.resource("schema://sqlite/all")
def list_table_schemas() -> str:
    """
    Retrieve the schemas for all tables in the database in JSON format.
    
    Returns:
        A JSON-formatted string mapping table names to their SQL schema.
    """
    logger.debug("Entering list_table_schemas()")
    try:
        # Get all tables from sqlite_master where type is table.
        cursor = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        rows = cursor.fetchall()
        # Build a dictionary: table name -> schema SQL.
        schemas = {row["name"]: row["sql"] for row in rows if row["sql"]}
        result = json.dumps(schemas, indent=2)
        logger.debug(f"Retrieved table schemas: {schemas}")
    except Exception as e:
        result = f"Error retrieving table schemas: {e}"
        logger.exception(result)
    logger.debug("Exiting list_table_schemas()")
    return result

# ------------------------------------------------------------------------------
# MCP Tools
# ------------------------------------------------------------------------------
# Tools are functions that perform actions or computations – here, executing SQL queries.

@mcp.tool()
def sql_query(query: str) -> str:
    """
    Execute a read-only SQL query. Only SELECT statements are allowed.
    
    Args:
        query: The SQL query to execute.
    
    Returns:
        A JSON-formatted string containing query results or an error message.
    """
    logger.debug(f"Entering sql_query() with query: {query}")
    
    # Basic safety check: enforce that only SELECT queries are permitted.
    if not query.strip().lower().startswith("select"):
        msg = "Error: Only SELECT queries are allowed."
        logger.warning(f"Query rejected: {query}. {msg}")
        return msg

    try:
        # Execute the query.
        cursor = conn.execute(query)
        # Convert the resulting rows into a list of dictionaries for serialization.
        rows = [dict(row) for row in cursor.fetchall()]
        result = json.dumps(rows, indent=2)
        logger.debug(f"SQL query executed successfully. Result: {result}")
    except Exception as e:
        result = f"Error executing query: {e}"
        logger.exception(result)
    
    logger.debug("Exiting sql_query()")
    return result

# ------------------------------------------------------------------------------
# MCP Prompts
# ------------------------------------------------------------------------------
# Prompts are templates for communicating with an LLM. They provide instructions and context.

@mcp.prompt()
def analyze_table_prompt(table: str) -> list[Message]:
    """
    Generate a prompt to ask an LLM to analyze a specific table.
    
    Args:
        table: The name of the table.
    
    Returns:
        A list containing a single prompt message instructing an analysis.
    """
    logger.debug(f"Entering analyze_table_prompt() with table: {table}")
    prompt_text = (
        f"Please analyze the table '{table}' from the SQLite database. "
        "Describe its structure, highlight key columns, and suggest potential data insights."
    )
    logger.debug(f"Generated analyze_table_prompt text: {prompt_text}")
    result = [UserMessage(prompt_text)]
    logger.debug("Exiting analyze_table_prompt()")
    return result

@mcp.prompt()
def describe_query_prompt(query: str) -> list[Message]:
    """
    Generate a prompt to ask an LLM to explain what a given SQL query does.
    
    Args:
        query: The SQL query string.
    
    Returns:
        A list containing a prompt message to explain the query.
    """
    logger.debug(f"Entering describe_query_prompt() with query: {query}")
    prompt_text = (
        f"Explain the following SQL query:\n\n{query}\n\n"
        "Describe what data it retrieves and suggest any potential improvements."
    )
    logger.debug(f"Generated describe_query_prompt text: {prompt_text}")
    result = [UserMessage(prompt_text)]
    logger.debug("Exiting describe_query_prompt()")
    return result

# ------------------------------------------------------------------------------
# Expose the MCP Server as an SSE ASGI Application
# ------------------------------------------------------------------------------
# The sse_app() method converts the MCP server to an ASGI application that uses SSE to stream responses.
logger.debug("Converting MCP server to SSE ASGI application.")
app = mcp.sse_app()
logger.info("SSE ASGI application is created and assigned to 'app'.")

# ------------------------------------------------------------------------------
# Run the Server via Uvicorn when executed directly
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting SSE MCP server via Uvicorn on http://0.0.0.0:8000")
    try:
        # Start the ASGI server with Uvicorn, which serves the SSE app.
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        # Log any exceptions that occur during server runtime.
        logger.exception(f"Server terminated unexpectedly: {e}")
    finally:
        # Ensure the SQLite database connection is closed on shutdown.
        conn.close()
        logger.info("Closed SQLite database connection.")