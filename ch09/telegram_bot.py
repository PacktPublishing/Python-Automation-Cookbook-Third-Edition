from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

TOKEN = 'your token here'

async def start(update, context):
    await update.message.reply_text("Hello! I'm your Telegram bot!. How can I help you?")


async def help_command(update, context):
    await update.message.reply_text(get_help())


def get_help():
    # Define the information to return per command
    msg = '''
    Use one of the following commands:
        help: To show this help
        offers: To see this week offers
        events: To see this week events
    '''
    return msg


def get_offers():
    msg = '''
    This week enjoy these amazing offers!
        20% discount in beach products
        15% discount if you spend more than €50
    '''
    return msg


def get_events():
    msg = '''
    Join us for an incredible party the Thursday in our Sun City shop!
    '''
    return msg


COMMANDS = {
    'help': get_help,
    'offers': get_offers,
    'events': get_events,
}


async def chat_message(update, context):
    # Detect the message and return the proper response
    message = update.message.text.lower()
    if message not in COMMANDS:
        await update.message.reply_text('Sorry, I did not catch that. Type "help" to see all options.')
        return

    message_back = COMMANDS[message]()
    await update.message.reply_text(message_back)


def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", get_help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                           chat_message))
    application.run_polling()


if __name__ == "__main__":
    main()
