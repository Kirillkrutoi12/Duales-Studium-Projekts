import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler

load_dotenv()  # загружает переменные из .env(downloads variables from .env)
TOKEN = os.getenv('TOKEN')  # Getting a Token

# parametrs update and context contain info about event (Handlers always get these params)


async def start(update: Update, context):
    """Create buttons"""
    keyboard = [
        [InlineKeyboardButton(
            'Ausbildung', callback_data="program_ausbildung")],
        [InlineKeyboardButton(
            'Duales Studium,', callback_data="program_duales")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    #Sending a message with buttons
    await update.message.reply_text("Выберите тип программы:",reply_markup=reply_markup)

    """Command /start - greet"""
    # Answer on the message
    await update.message.reply_text('Hallo, ich helfe dir gern dein Ausbildung/Duales Studium zu finden')


def main():
    """Main function starts and sets bot"""
    app = Application.builder().token(TOKEN).build()
    """Register a command /start"""
    app.add_handler(CommandHandler('start', start))
    print('Bot gestartet!')
    """Start listening a Bot"""
    app.run_polling()


if __name__ == '__main__':
    main()
