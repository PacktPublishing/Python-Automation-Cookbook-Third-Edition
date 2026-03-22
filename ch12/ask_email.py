import asyncio
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
from agents.mcp import MCPServerStdio
from rich.console import Console
from rich.markdown import Markdown

MODEL = 'gpt-5.4'

console = Console()

set_default_openai_key(OPEN_AI_KEY)


async def main():

    async with MCPServerStdio(
        params={
            'command': 'uv',
            'args': ['run', 'email_mcp_server.py'],
        },
        name='email',
        # Longer session (default is 5 seconds) to allow
        # enough time to retrieve the emails
        client_session_timeout_seconds=30,
    ) as mcp_server:
        agent = Agent(
            name='MCP Assistant',
            instructions='You are a helpful assistant with access '
                         'to MCP tools',
            mcp_servers=[mcp_server],
            model=MODEL,
        )

        prompt = '''
            Summarise me in a paragraph or two the latest day of emails
            received
        '''

        messages = [
            {'role': 'user', 'content': prompt}
        ]

        result = await Runner.run(agent, input=messages)

        markdown = Markdown('---')
        console.print(markdown)

        markdown = Markdown(result.final_output)
        console.print(markdown)

        markdown = Markdown('---')
        console.print(markdown)

        while True:
            # Allow to ask questions
            question = input('Do you want to ask any question? [end to finish] ')
            if question == 'end':
                print('bye!')
                break

            # As in other chatbots, we add the context up to this moment
            # question to the context of the AI Model
            messages = result.to_input_list(mode='normalized')
            # Plus the new question from the user
            messages.append({'role': 'user', 'content': question})

            result = await Runner.run(agent, input=messages)

            markdown = Markdown('---')
            console.print(markdown)

            markdown = Markdown(result.final_output)
            console.print(markdown)

            markdown = Markdown('---')
            console.print(markdown)


asyncio.run(main())
