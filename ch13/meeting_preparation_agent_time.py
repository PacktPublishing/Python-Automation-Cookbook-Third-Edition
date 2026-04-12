import asyncio
from datetime import datetime
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
from agents import function_tool
from rich.console import Console
from rich.markdown import Markdown

from notes_tools import available_notes as _available_notes
from notes_tools import retrieve_note as _retrieve_note
from notes_tools import write_meeting_brief as _write_meeting_brief
from calendar_tools import retrieve_calendar_events as _retrieve_calendar_events


@function_tool
def available_notes():
    '''
    Retrieve all available notes from people from previous meetings
    '''
    return _available_notes()


@function_tool
def retrieve_note(user: str):
    '''
    Retrieve the note for a person to check information on previous meetings
    It returns Markdown text with the general notes and specifics about
    previous meetings
    '''
    return _retrieve_note(user)


@function_tool
def retrieve_calendar_events():
    '''
    Obtain the next calendar events
    '''
    return _retrieve_calendar_events()


@function_tool
def write_meeting_brief(user: str, date: str, text: str):
    '''
    Write a meeting brief for a person.

    Returns:
        SUCCESS
        ERROR: Error Description
    '''
    return _write_meeting_brief(user, date, text)


@function_tool
def current_time():
    '''
    Return current date time
    '''
    return datetime.now()


MODEL = 'gpt-5.4'

console = Console()

set_default_openai_key(OPEN_AI_KEY)


async def main():

    agent = Agent(
        name='Calendar assistant',
        instructions='You are a helpful assistant preparing meetings',
        tools=[available_notes, retrieve_note, write_meeting_brief,
               retrieve_calendar_events, current_time],
        model=MODEL,
    )

    prompt = '''
    Check the calendar events for meetings. Only for the next one,
    verifying with the current time, check if there are meeting
    notes for any of the participants (name will be related to the
    email in the calendar, but it will likely not match completely),
    and provide a summary of the relevant information for the meeting.
    Format it as a short meeting brief. Do not suggest follow up.
    Write the meeting brief.
    '''

    result = Runner.run_streamed(agent, input=prompt)

    async for event in result.stream_events():
        event_type = event.type

        # lifecycle
        if event_type == "agent_updated_stream_event":
            console.print(f"\nAgent: {event.new_agent.name}")

        # Show progress
        elif event_type == 'raw_response_event':
            print('.', end='', flush=True)

        # Tool calls
        elif event_type == "run_item_stream_event":
            item = event.item

            if item.type == "tool_call_item":
                console.print(f"\nCalling tool: {item.raw_item.name}")

            elif item.type == "message_output_item":
                # Final message chunks
                for content in item.raw_item.content:
                    if content.type == "output_text":
                        print()
                        markdown = Markdown('---')
                        console.print(markdown)
                        markdown = Markdown(content.text)
                        console.print(markdown)


if __name__ == '__main__':
    asyncio.run(main())
