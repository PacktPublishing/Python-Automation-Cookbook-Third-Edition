from ollama import chat

MODEL = 'qwen3:8b'


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
        response = chat(model=MODEL, messages=messages)

        reply = response.message.content
        print('Bot: ', reply)
        messages.append({'role': 'assistant', 'content': reply})


if __name__ == '__main__':
    main()
