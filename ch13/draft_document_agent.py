import os
import asyncio
from keys import OPEN_AI_KEY
from agents import Agent, Runner, set_default_openai_key
from agents import function_tool
from agents.mcp import MCPServerStdio

from notes_tools import available_notes as _available_notes
from notes_tools import retrieve_note as _retrieve_note


MODEL = 'gpt-5.4'

set_default_openai_key(OPEN_AI_KEY)

writer_subagent = Agent(
    name='Writer subagent',
    model=MODEL,
    instructions=(
        '''
        You are a writer agent that produces professional documents.
        You use a formal tone, but keeping a warm tone, without being
        too close. You keep things short and to the point, but without
        becoming to direct.
        '''
    ),
)

reviewer_subagent = Agent(
    name='Reviewer subagent',
    model=MODEL,
    instructions=(
        '''
        You are a reviewer and editor subagent focused on professional
        documents.  You proofread the documents and propose changes,
        improving the readability of the result. You try to maintain
        the voice of the author, but clarify points and remove cliches.
        Once a version is deemed good to go, say that it is approved.
        '''
    )
)


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


async def main():

    ORCHESTRATOR_PROMPT = '''
        You are the orchestrator of a multi-agent system. Your task is to
        take the user's request and generate a proper document draft based
        on their request by passing it to the appropriate agent tools. Be
        sure to see if we have any notes relevant for the document. Go
        to the tool to write something, and then pass it to the reviewer
        tools to get comments, iterating on the result.
        You may need to do the process multiple times, as well as calling
        call multiple agents to get all of the information you need. Once
        the draft is approved, write it as an MS Word file using the MCP
        server tools.  Do not mention or draw attention to the fact that
        this is a multi-agent system. Do not propose follow up.
    '''

    UV_COMMAND = os.environ.get('UV_COMMAND')
    MCP_DIR_PATH = os.environ.get('MCP_DIR_PATH')
    MCP_SERVER_PATH = os.path.join(MCP_DIR_PATH, 'word_mcp_server.py')

    async with MCPServerStdio(
        name='ms_word_writer',
        params={
            'command': UV_COMMAND,
            'args': ['run', '-w', MCP_DIR_PATH, MCP_SERVER_PATH],
        }
    ) as mcp_server:
        orchestrator = Agent(
            name='Orchestrator',
            model=MODEL,
            instructions=ORCHESTRATOR_PROMPT,
            mcp_servers=[mcp_server],
            tools=[
                writer_subagent.as_tool(
                    tool_name='writer_subagent',
                    tool_description='Writes documents'
                ),
                reviewer_subagent.as_tool(
                    tool_name='reviewer_subagent',
                    tool_description='Reviews documents'
                ),
                available_notes,
                retrieve_note,
            ]
        )

        result = Runner.run_streamed(
            starting_agent=orchestrator,
            input=('Make a document about the notes for user Jaime Buelta, '
                   'to propose a collaboration for a new project that will '
                   'use JavaScript'),
            max_turns=50,
        )

        async for event in result.stream_events():
            event_type = event.type

            # lifecycle
            if event_type == "agent_updated_stream_event":
                print(f"\nAgent: {event.new_agent.name}")

            # Show progress
            elif event_type == 'raw_response_event':
                print('.', end='', flush=True)

            # Tool calls
            elif event_type == "run_item_stream_event":
                item = event.item

                if item.type == "tool_call_item":
                    print(f"\nCalling tool: {item.raw_item.name}")

                elif item.type == "message_output_item":
                    # Final message chunks
                    for content in item.raw_item.content:
                        if content.type == "output_text":
                            print()
                            print(content.text)


if __name__ == '__main__':
    asyncio.run(main())
