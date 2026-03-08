from ollama import chat
from colorama import init, Fore, Style

MODEL = 'qwen3:8b'

# Init colorama in all platform
# This may be required for colorama to work in some platforms like Windows
init()


def main():
    messages = [
        {'role': 'system', 'content': 'you are a helpful assistant. Be concise in your answers'},
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
        stream = chat(model=MODEL, messages=messages, stream=True)

        print('Bot: ')
        thinking_style = False
        for chunk in stream:
            if chunk.message.thinking:
                if not thinking_style:
                    # Thinking style, set clearer type for text
                    thinking_style = True
                    print(Fore.LIGHTBLACK_EX)
                # Print the thinking process
                text = chunk.message.thinking
                print(text, end='', flush=True)
            else:
                if thinking_style:
                    # Back to regular response, reset style
                    thinking_style = False
                    print(Style.RESET_ALL)

                text = chunk.message.content
                print(text, end='', flush=True)

        print()
        messages.append({'role': 'assistant', 'content': reply})


if __name__ == '__main__':
    main()
