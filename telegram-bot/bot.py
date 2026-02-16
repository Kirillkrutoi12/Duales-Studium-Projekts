import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

load_dotenv()  # загружает переменные из .env(downloads variables from .env)
TOKEN = os.getenv('TOKEN')  # Getting a Token

# parametrs update and context contain info about event (Handlers always get these params)

# All Handlers have to be async


async def start(update: Update, context):
    """Command /start - greet"""
    # Answer on the message
    await update.message.reply_text('Hallo, ich helfe dir gern dein Ausbildung/Duales Studium zu finden')
    """Create buttons"""
    keyboard = [
        [InlineKeyboardButton(
            'Ausbildung', callback_data="program_ausbildung")],
        [InlineKeyboardButton(
            'Duales Studium', callback_data="program_duales")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # Sending a message with buttons
    await update.message.reply_text("Wähl bitte den Programtyp:", reply_markup=reply_markup)


async def handle_program_choice(update: Update, context):
    """"Processing program type selection(Обрабатываем выбор типа программы)"""
    query = update.callback_query
    # Removing wait-indicator(we can add pop-up notification)
    await query.answer()
    """Getting what a user pressed on"""
    choice = query.data
    """Saving user selection"""
    context.user_data['program_type'] = choice  # 'program_type' is key , choice is value
    """Showing city buttons"""
    keyboard = [
        [InlineKeyboardButton('Stuttgart', callback_data='city_stuttgart')],
        [InlineKeyboardButton('München', callback_data='city_muenchen')],
        [InlineKeyboardButton('Berlin', callback_data='city_berlin')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Wähl deine Stadt:', reply_markup=reply_markup)


def main():
    """Main function starts and sets bot"""
    app = Application.builder().token(TOKEN).build()
    """Register a command /start"""
    app.add_handler(CommandHandler('start', start))
    """Handler button program"""
    app.add_handler(CallbackQueryHandler(
        handle_program_choice,
        pattern="^program_"
    ))
    print('Bot gestartet!')
    """Start listening a Bot"""
    app.run_polling()


if __name__ == '__main__':
    main()
