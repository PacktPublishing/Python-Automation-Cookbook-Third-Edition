from keys import OPEN_AI_KEY
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

client = OpenAI(api_key=OPEN_AI_KEY)

MODEL = 'gpt-5.4'

console = Console()


def main():
    prompt = ('Create a calendar of the most important '
              'sport events in Europe for the new week. '
              'One event per day. Verify each event'
              'independently twice to be sure the date is '
              'correct. Do not suggest next steps')

    response = client.responses.create(
        model=MODEL,
        tools=[{'type': 'web_search'}],
        input=prompt
    )
    markdown = Markdown(response.output_text)
    console.print(markdown)


if __name__ == '__main__':
    main()
