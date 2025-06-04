import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


import users_list  # Adjust path if needed

API_TOKEN = '7791548688:AAG6jXPTh5jfBKi34wE4RknRAvaHCWf85_Y'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

logged_in_users = {}  # {user_id: user_object}
last_bot_messages = {}  # {user_id: bot_message_id}


def get_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("My Profile🔒"))
    kb.add(KeyboardButton("About"))
    if user_id in logged_in_users:
        kb.add(KeyboardButton("Log out"))
    return kb


# Helper to delete previous user and bot messages and send a new one
async def clean_and_respond(message: types.Message, text: str, keyboard: ReplyKeyboardMarkup = None):
    user_id = message.from_user.id

    # Delete user message
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception:
        pass

    # Delete last bot message if exists
    if user_id in last_bot_messages:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=last_bot_messages[user_id])
        except Exception:
            pass

    # Send new message
    sent = await message.answer(text, reply_markup=keyboard)
    last_bot_messages[user_id] = sent.message_id


@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    # Do NOT delete /start or its reply
    sent = await message.answer(
        f"Good day {message.from_user.first_name}!\n"
        f"I am a Vibrant educational Center's\n"
        f"official Telegram Bot\n"
        f"For more questions, contact @zufar_BRO",
        reply_markup=get_keyboard(message.from_user.id)
    )
    # Save this message ID so later replies can still be cleaned
    last_bot_messages[message.from_user.id] = sent.message_id



# About
@dp.message_handler(lambda message: message.text == "About")
async def handle_about(message: types.Message):
    await clean_and_respond(
        message,
        "For more information, please contact @zufar_BRO",
        get_keyboard(message.from_user.id)
    )


# Log out
@dp.message_handler(lambda message: message.text == "Log out" or message.text == "/logout")
async def handle_logout(message: types.Message):
    user_id = message.from_user.id
    if user_id in logged_in_users:
        del logged_in_users[user_id]
        text = "You have been logged out. You can now log in again."
    else:
        text = "You're not logged in."
    await clean_and_respond(message, text, get_keyboard(user_id))


# My Profile🔒
@dp.message_handler(lambda message: message.text == "My Profile🔒")
async def handle_profile(message: types.Message):
    user_id = message.from_user.id
    if user_id in logged_in_users:
        user = logged_in_users[user_id]
        text = (f"Good Day <b>{user.realname}</b>!\n"
                f"Your Status: {user.status}\n"
                f"You are a student in: <i>{user.grs}</i>\n"
                f"{f'Your Payment Status: <b><i>{user.pstat}' if hasattr(user, 'pstat') else ''}</i></b>\n\n"
                f"<code>❗If you want to switch accounts, press 'Log out'.</code>")
    else:
        text = "Please enter your login:"
    await clean_and_respond(message, text, get_keyboard(user_id))


# Login input
@dp.message_handler()
async def handle_login(message: types.Message):
    user_id = message.from_user.id

    if user_id in logged_in_users:
        await clean_and_respond(
            message,
            "You're already logged in. Press 'Log out' to switch accounts.",
            get_keyboard(user_id)
        )
        return

    login_code = message.text.strip()
    user = None

    if login_code == "ziyayevbosd123":
        user = users_list.bosdziyayev
    elif login_code == "zufarxojiakbarov123":
        user = users_list.adminzufar
    elif login_code == "sevaraqozoqova123":
        user = users_list.sevarateacher

    if user:
        logged_in_users[user_id] = user
        text = (f"Good Day <b>{user.realname}</b>!\n"
                f"Your Status: {user.status}\n"
                f"You are a student in: <i>{user.grs}</i>\n"
                f"{f'Your Payment Status: <b><i>{user.pstat}' if hasattr(user, 'pstat') else ''}</i></b>\n\n"
                f"For more questions, contact @zufar_BRO")
    else:
        text = "This login or code does not exist.\nPlease ask the admin @zufar_BRO"

    await clean_and_respond(message, text, get_keyboard(user_id))


# Start polling
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
