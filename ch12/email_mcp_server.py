from mcp.server.fastmcp import FastMCP
from email_tool import retrieve_last_emails as _retrieve_last_emails

mcp = FastMCP('Email Server')


@mcp.tool()
def retrieve_last_emails():
    '''Retrieve today's email from the mailbox.
    Returns a list of dicts with subject, address, and payload.
    '''
    return _retrieve_last_emails()


if __name__ == '__main__':
    mcp.run(transport='stdio')
