#!/usr/bin/env python3
"""
SQLite MCP Server

This server demonstrates:
  - Connecting to a SQLite database.
  - Exposing table schemas as resources.
  - Providing a read-only SQL query tool.
  - Defining prompt templates for common data analysis tasks.
  
Logging is extensively used to help trace flow and for debugging purposes.
"""

import sqlite3
import json
import logging

# Import components from the MCP Python SDK (FastMCP and related prompt/message helpers).
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage, Message

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------
# Configure basic logging to log debug and higher level messages. Adjust logging
# configuration as required (for example, to log to a file or change log format).
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sqlite_mcp_server")

# ------------------------------------------------------------------------------
# Database Setup
# ------------------------------------------------------------------------------
# Path to your company’s SQLite database; adjust as needed.
#DB_PATH = "/Users/prayank/code/mcp-gpt-implementation/sample_company.db"
DB_PATH = "/Users/prayank/code/mcp-gpt-implementation/startups.db"

try:
    # Connect to the SQLite database using sqlite3 and set row_factory to
    # sqlite3.Row so that rows are returned as dictionaries.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    logger.info(f"Connected to SQLite database at '{DB_PATH}'.")
except Exception as e:
    logger.exception(f"Failed to connect to SQLite database: {e}")
    raise

# ------------------------------------------------------------------------------
# MCP Server Setup
# ------------------------------------------------------------------------------
# Create a FastMCP server instance with a given name (and optionally a version).
mcp = FastMCP("SQLite MCP Server")
logger.info("Initialized MCP server instance with name 'SQLite MCP Server'.")

# ------------------------------------------------------------------------------
# MCP Resources
# ------------------------------------------------------------------------------
# Resources expose information (such as table schemas) from the database.

@mcp.resource("schema://sqlite/{table}")
def get_table_schema(table: str) -> str:
    """
    MCP Resource to return the CREATE TABLE statement for a specified table in the database.
    
    Args:
        table: The name of the database table.
        
    Returns:
        SQL statement (as a string) describing the table schema, or an error message
        if the table is not found.
    """
    logger.debug(f"Received resource request for schema of table: '{table}'")
    try:
        # Execute a query to get the SQL for the table schema.
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        row = cursor.fetchone()
        if row is not None:
            schema_sql = row["sql"]
            logger.debug(f"Found schema for table '{table}': {schema_sql}")
            return schema_sql
        else:
            msg = f"Table '{table}' not found in database."
            logger.warning(msg)
            return msg
    except Exception as e:
        err_msg = f"Error retrieving schema for table '{table}': {e}"
        logger.exception(err_msg)
        return err_msg

@mcp.resource("schema://sqlite/all")
def list_table_schemas() -> str:
    """
    MCP Resource that returns a JSON-formatted object containing the schema for all tables.
    
    Returns:
        A JSON string mapping table names to their corresponding CREATE TABLE statements.
    """
    logger.debug("Received resource request for listing all table schemas.")
    try:
        cursor = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        rows = cursor.fetchall()
        # Build a dictionary of table schemas.
        schemas = {row["name"]: row["sql"] for row in rows if row["sql"] is not None}
        schema_json = json.dumps(schemas, indent=2)
        logger.debug("Successfully retrieved all table schemas.")
        return schema_json
    except Exception as e:
        err_msg = f"Error retrieving table schemas: {e}"
        logger.exception(err_msg)
        return err_msg

# ------------------------------------------------------------------------------
# MCP Tools
# ------------------------------------------------------------------------------
# Tools provide functionality that clients can invoke—here, a SQL query tool is defined.

@mcp.tool()
def sql_query(query: str) -> str:
    """
    MCP Tool to execute a read-only SQL query. For security, only queries starting with
    SELECT (case insensitive) are allowed.
    
    Args:
        query: A SQL query string provided by the client.
        
    Returns:
        JSON-formatted query results as a string or an error message.
    """
    logger.debug(f"Tool 'sql_query' invoked with query: {query}")
    
    # Enforce read-only queries: only allow queries starting with SELECT.
    query_stripped = query.strip().lower()
    if not query_stripped.startswith("select"):
        msg = "Error: Only SELECT queries are allowed."
        logger.warning(f"Rejected query. {msg} Received query: {query}")
        return msg

    try:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        # Convert query results to a list of dictionaries for JSON serialization.
        result_list = [dict(row) for row in rows]
        result_json = json.dumps(result_list, indent=2)
        logger.info("SQL query executed successfully.")
        return result_json
    except Exception as e:
        err_msg = f"Error executing query: {e}"
        logger.exception(err_msg)
        return err_msg

# ------------------------------------------------------------------------------
# MCP Prompts
# ------------------------------------------------------------------------------
# Prompts are reusable message templates that help language models understand what to do.

@mcp.prompt()
def analyze_table_prompt(table: str) -> list[Message]:
    """
    MCP Prompt that instructs the LLM to analyze a specific table's schema and data.
    
    Args:
        table: Name of the database table to analyze.
        
    Returns:
        A list of prompt messages for the language model.
    """
    logger.debug(f"Generating prompt to analyze table: {table}")
    prompt_text = (
        f"Analyze the table '{table}' from the SQLite database. Provide insights about the data structure, "
        "list key columns, and suggest potential data cleaning or further analysis steps."
    )
    logger.info("Prompt 'analyze_table_prompt' generated successfully.")
    return [UserMessage(prompt_text)]

@mcp.prompt()
def describe_query_prompt(query: str) -> list[Message]:
    """
    MCP Prompt that generates a description of what a given SQL query does and suggests improvements.
    
    Args:
        query: The SQL query to be described.
    
    Returns:
        A list of messages forming a prompt for the language model.
    """
    logger.debug(f"Generating prompt to describe the SQL query: {query}")
    prompt_text = (
        f"I executed the following SQL query:\n\n{query}\n\n"
        "Please explain what this query does, interpret the results, and suggest improvements if applicable."
    )
    logger.info("Prompt 'describe_query_prompt' generated successfully.")
    return [UserMessage(prompt_text)]


# ------------------------------------------------------------------------------
# Running the MCP Server
# ------------------------------------------------------------------------------
# The server is run using the default stdio transport. This mode is suitable for local
# development and testing, and can be used with MCP Inspector or integrated into a host like
# Claude Desktop.
if __name__ == "__main__":
    logger.info("Starting MCP server...")
    try:
        mcp.run()
    except Exception as e:
        logger.exception(f"MCP server terminated unexpectedly: {e}")
    finally:
        # Optional: close the database connection on server shutdown.
        conn.close()
        logger.info("Database connection closed. MCP server shutdown complete.")