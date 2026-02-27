import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from data import get_jobs_for_city

load_dotenv()  # downloads variables from .env
TOKEN = os.getenv('TOKEN')  # Getting a Token

# parametrs update and context contain info about event (Handlers always get these params)

# All Handlers have to be async


async def safe_answer(query):
    """Safely answer callback query (ignore if expired)"""
    try:
        await query.answer()
    except Exception as e:
        print(f'⚠️ Could not answer query: {e}')


async def start(update: Update, context):
    """Command /start - greet"""
    # Answer on the message
    # await update.message.reply_text('Hallo, ich helfe dir gern dein Ausbildung/Duales Studium zu finden')
    """Create buttons"""
    keyboard = [
        [InlineKeyboardButton(
            'Ausbildung', callback_data="program_ausbildung")],
        [InlineKeyboardButton(
            'Duales Studium', callback_data="program_duales")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # Sending a message with buttons
    await update.message.reply_text("Hallo, ich helfe dir gern dein Ausbildung/Duales Studium zu finden.\n"
                                    "Wähl bitte den Programtyp:", reply_markup=reply_markup)


async def handle_program_choice(update: Update, context):
    """"Processing program type selection(Обрабатываем выбор типа программы)"""
    query = update.callback_query
    # Removing wait-indicator(we can add pop-up notification)
    # await query.answer()Change below
    await safe_answer(query)
    """Getting what a user pressed on"""
    choice = query.data
    """Saving user selection"""
    context.user_data['program_type'] = choice  # 'program_type' is key , choice is value
    """Showing city buttons"""
    keyboard = [
        [InlineKeyboardButton('Stuttgart', callback_data='city_stuttgart')],
        [InlineKeyboardButton('München', callback_data='city_muenchen')],
        [InlineKeyboardButton('Berlin', callback_data='city_berlin')],
        [InlineKeyboardButton("🔙 Zurück", callback_data="back_to_programs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Wähl deine Stadt:', reply_markup=reply_markup)


async def handle_city_choice(update: Update, context):
    """Showing jobopenings in the selected city"""
    query = update.callback_query  # an object with information about the pressed button
    # await query.answer()
    await safe_answer(query)
    # Getting the city
    city = query.data.replace('city_', '')  # "city_stuttgart" → "stuttgart"
    city = city.capitalize()  # "stuttgart" → "Stuttgart"
    """Getting a type of programm from data"""
    program_type = context.user_data.get('program_type', 'program_ausbildung')

    # Show loading indicator
    await query.edit_message_text(f"🔍 Suche nach Stellen in {city}... Bitte warten.")

    # Using a parser!
    data = get_jobs_for_city(city, use_cache=True)

    keyboard = [[
        InlineKeyboardButton('🔙 Zurück', callback_data='back_to_cities')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not data:
        await query.edit_message_text(f"Leider in der {city} gibt es nun keine Stellen", reply_markup=reply_markup)
        return
    # Forming message with list of jobopenings
    message = f"Verfügbare Programme in {city}:\n\n"

    for i, job in enumerate(data, 1):
        message += f"{i}. {job['title']}\n"
        message += f"   🏢 {job['company']}\n"
        message += f"   🔗 {job['url']}\n\n"

    await query.edit_message_text(message, reply_markup=reply_markup)


async def handle_back(update: Update, context):
    query = update.callback_query
    # await query.answer()
    await safe_answer(query)
    # Determing where to return
    if query.data == 'back_to_programs':
        keyboard = [
            [InlineKeyboardButton(
                'Ausbildung', callback_data="program_ausbildung")],
            [InlineKeyboardButton(
                'Duales Studium', callback_data="program_duales")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('Wähl bitte den Programtyp:', reply_markup=reply_markup)
    elif query.data == 'back_to_cities':
        keyboard = [
            [InlineKeyboardButton(
                'Stuttgart', callback_data='city_stuttgart')],
            [InlineKeyboardButton('München', callback_data='city_muenchen')],
            [InlineKeyboardButton('Berlin', callback_data='city_berlin')],
            [InlineKeyboardButton(
                "🔙 Zurück", callback_data="back_to_programs")]
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
        # срабатывает на callback_data начинающиеся с "program_"(# triggers on callback_data starting with "program_")
        pattern="^program_"
    ))
    app.add_handler(CallbackQueryHandler(handle_city_choice, pattern="^city_"))
    app.add_handler(CallbackQueryHandler(handle_back, pattern='^back_'))
    print('Bot gestartet!')
    """Start listening a Bot"""
    app.run_polling()


if __name__ == '__main__':
    main()
