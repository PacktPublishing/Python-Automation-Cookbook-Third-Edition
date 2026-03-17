import asyncio
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
from agents.mcp import MCPServerSse
from rich.console import Console
from rich.markdown import Markdown

MODEL = 'gpt-5.4'

console = Console()


set_default_openai_key(OPEN_AI_KEY)


async def main():
    async with MCPServerSse(
        params={'url': 'http://localhost:8000/sse'},
        name='database',
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

        markdown = Markdown(result.final_output)
        console.print(markdown)


asyncio.run(main())
