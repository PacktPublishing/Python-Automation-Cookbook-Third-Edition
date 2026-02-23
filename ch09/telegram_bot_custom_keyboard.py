from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

TOKEN = 'your token here'

async def start(update, context):
    await update.message.reply_text("Hello! I'm your Telegram bot!. How can I help you?")
    await show_options(update, context)


async def help_command(update, context):
    await update.message.reply_text(get_help())
    await show_options(update, context)


def get_help():
    # Define the information to return per command
    msg = '''
    Use one of the following commands:
        help: To show this help
        offers: To see this week offers
        events: To see this week events
        /options: To show the options in a custom keyboard
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


async def show_options(update, context):
    keyboard = [
        [
            InlineKeyboardButton('Offers', callback_data='offers'),
            InlineKeyboardButton('Events', callback_data='events'),
            InlineKeyboardButton('Help', callback_data='help'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Available Options:', reply_markup=reply_markup)


async def press_button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    option = query.data

    await query.edit_message_text(text=f'Selected option: {option}')

    message_back = COMMANDS[option]()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_back)


def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", get_help))
    application.add_handler(CommandHandler("options", show_options))
    application.add_handler(CallbackQueryHandler(press_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                           chat_message))
    application.run_polling()


if __name__ == "__main__":
    main()
