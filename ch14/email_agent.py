import asyncio
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
from agents import ModelSettings
from agents import function_tool, retry_policies
from agents.model_settings import ModelRetrySettings, ModelRetryBackoffSettings
from rich.console import Console
from rich.markdown import Markdown

from email_tool import retrieve_last_emails as _retrieve_last_emails
from email_tool import create_a_draft_reply as _create_a_draft_reply
from email_tool import send_a_summary_email as _send_a_summary_email
from email_tool import read_stored_sent_emails as _read_stored_sent_emails

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


@function_tool
def create_a_draft_reply(email_uid: str, content: str):
    '''
    Create a draft reply to an email, given its email_uid
    and the content will be the response.
    If there’s already a draft responding to the email, it
    won’t create a new one.
    '''
    return _create_a_draft_reply(email_uid, content)


@function_tool
def send_a_summary_email(summary: str, content: str):
    '''
    Send a summary email
    '''
    return _send_a_summary_email(summary, content)


@function_tool
def read_stored_sent_emails():
    '''
    Read stored sent emails content
    '''
    return _read_stored_sent_emails()


async def main():

    # Create retry settings that will help us if there's
    # a problem, like a rate-limit or error
    retry_settings = ModelRetrySettings(
        max_retries=6,
        policy=retry_policies.provider_suggested(),
        backoff=ModelRetryBackoffSettings(initial_delay=1.0,
                                          multiplier=2.0,
                                          max_delay=60.0,
                                          jitter=True)
    )

    agent = Agent(
        name='Assistant',
        instructions='You are a helpful assistant with access '
                     'to tools',
        tools=[retrieve_last_emails, create_a_draft_reply,
               send_a_summary_email, read_stored_sent_emails],
        model=MODEL,
        model_settings=ModelSettings(retry=retry_settings),
    )

    prompt = '''
        Review all emails received in the last 24 hours. Provide a clear,
        concise summary in one or two paragraphs, giving a high-level
        overview of the correspondence.

        For any emails that require a response:
          * Draft a reply in the style of previous sent emails.
          * Ensure the draft includes only relevant elements from the
          original email and maintains the established tone.
          * Save each draft using the proper tool.

        If no existing summary covers the same content, create and send
        a new summary email with the subject starting with "Summary :".
        The summary should have:
          * An opening paragraph with a high-level overview of all emails.
          * Each draft reply listed as a bullet point.
          * A separator line, followed by bullet points with detailed
          notes about each email.

        Conclude by reporting the completion of the task with a brief
        message.
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

# Run the main function
# asyncio.run(main())
print('This is the execution of the task')
