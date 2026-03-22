import asyncio
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
from agents import function_tool
from rich.console import Console
from rich.markdown import Markdown

from email_tool import retrieve_last_emails as _retrieve_last_emails

MODEL = 'gpt-5.4'

console = Console()

set_default_openai_key(OPEN_AI_KEY)


@function_tool
def retrieve_last_emails():
    '''
    Retrieve today's email from the mailbox.
    Returns a list of dicts with subject, address, and payload.
    '''
    return _retrieve_last_emails()


async def main():

    agent = Agent(
        name='MCP Assistant',
        instructions='You are a helpful assistant with access '
                     'to tools',
        tools=[retrieve_last_emails],
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

asyncio.run(main())
