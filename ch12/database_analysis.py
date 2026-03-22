import asyncio
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
import os
from agents.mcp import MCPServerStdio
from rich.console import Console
from rich.markdown import Markdown

MODEL = 'gpt-5.4'

console = Console()

set_default_openai_key(OPEN_AI_KEY)

UV_COMMAND = os.environ.get('UV_COMMAND')
MCP_PATH = os.environ.get('MCP_PATH')


async def main():
    async with MCPServerStdio(
        name='database',
        params={
            'command': UV_COMMAND,
            'args': ['run', MCP_PATH],
        },
    ) as mcp_server:
        agent = Agent(
            name='MCP Assistant',
            instructions='You are a helpful assistant with access '
                         'to MCP tools',
            mcp_servers=[mcp_server],
            model=MODEL,
        )

        prompt = '''
            Explain the contents of the database accessible through
            MCP server. Provide insights about the situation
            described. Be concise. Return your results in a
            couple of paragraphs.
        '''

        result = await Runner.run(agent, input=prompt)

        markdown = Markdown('---')
        console.print(markdown)

        markdown = Markdown(result.final_output)
        console.print(markdown)

        markdown = Markdown('---')
        console.print(markdown)


asyncio.run(main())
