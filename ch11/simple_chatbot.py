from keys import OPEN_AI_KEY
from openai import OpenAI

client = OpenAI(api_key=OPEN_AI_KEY)

MODEL = 'gpt-5.2'


def main():
    messages = [
        {'role': 'system', 'content': 'you are a useful assistant'},
    ]
    print('Welcome to the chatbot! Write bye to end!')
    while True:
        user_input = input('You: ')
        if not user_input:
            continue
        elif user_input.lower() == 'bye':
            print('Bot: Bye, bye!')
            break
        messages.append({'role': 'user', 'content': user_input})
        response = client.responses.create(
            model=MODEL,
            input=messages,
        )

        reply = response.output_text
        print('Bot: ', reply)
        messages.append({'role': 'assistant', 'content': reply})


if __name__ == '__main__':
    main()
