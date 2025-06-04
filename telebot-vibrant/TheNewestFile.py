import telebot
from telebot import types
import logging
from time import sleep
import users_list
import dynamic_groups
import importlib
import os

API_TOKEN = '7791548688:AAG6jXPTh5jfBKi34wE4RknRAvaHCWf85_Y'
channel_id = '-1002317377933'

bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')
logging.basicConfig(level=logging.INFO)

logged_in_users = {}
last_bot_messages = {}
edit_mode_users = set()

def get_keyboard(user_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("My Profile🔒", "About")
    user = logged_in_users.get(user_id)
    if user:
        if user.realname in ["Qozoqova Sevara", "Sharpbayev Diyor"]:
            kb.row("📂 My Groups", "➕ Add New Student")
            kb.add("✏️ Edit Student")
        kb.add("Log out")
    return kb

def clean_and_respond(message, text, keyboard=None):
    user_id = message.from_user.id
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass
    if user_id in last_bot_messages:
        try:
            bot.delete_message(message.chat.id, last_bot_messages[user_id])
        except Exception:
            pass
    sent = bot.send_message(message.chat.id, text, reply_markup=keyboard)
    last_bot_messages[user_id] = sent.message_id

def create_group_keyboard(teacher_name):
    groups = dynamic_groups.load_groups_from_file()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔙 Back to Main Menu")
    for group in groups:
        if teacher_name == "Qozoqova Sevara" and "English" in group:
            kb.add(group)
        elif teacher_name == "Sharpbayev Diyor" and "Math" in group:
            kb.add(group)
    return kb

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        with open('welcome.jpg', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="❗REMEMBER, here is our login system!")
    except Exception as e:
        logging.warning(f"Failed to send photo: {e}")

    clean_and_respond(
        message,
        f"Good day {message.from_user.first_name}!\n"
        f"I am a Vibrant educational Center's official Telegram Bot\n"
        f"For more questions, contact @zufar_BRO",
        get_keyboard(message.from_user.id)
    )
    sleep(0.5)
    bot.send_message(
        chat_id=channel_id,
        text=f"-----------New User-------------\n"
             f"nick name: {message.from_user.first_name}\n"
             f"user name: @{message.from_user.username}\n"
             f"user id: {message.from_user.id}\n"
             f"---------------------------------------\n"
    )

@bot.message_handler(func=lambda m: m.text == "📂 My Groups")
def handle_groups_message(message):
    user = logged_in_users.get(message.from_user.id)
    if not user:
        clean_and_respond(message, "You must be logged in to view your groups.", get_keyboard(message.from_user.id))
        return
    if user.realname in ["Qozoqova Sevara", "Sharpbayev Diyor"]:
        kb = create_group_keyboard(user.realname)
        clean_and_respond(message, "📚 Select a group to view its students:", kb)
    else:
        clean_and_respond(message, "You do not have access to any groups.", get_keyboard(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "🔙 Back to Main Menu")
def back_to_main(message):
    clean_and_respond(message, "You're back to the main menu.", get_keyboard(message.from_user.id))

@bot.message_handler(func=lambda m: m.text in dynamic_groups.load_groups_from_file())
def handle_dynamic_group(message):
    group_name = message.text
    groups = dynamic_groups.load_groups_from_file()
    students = groups.get(group_name, [])
    if students:
        clean_and_respond(message, f"<b>{group_name} Students:</b>\n\n" + "\n\n".join(students),
                          create_group_keyboard(logged_in_users.get(message.from_user.id).realname))
    else:
        clean_and_respond(message, f"No students found in {group_name}.", create_group_keyboard(logged_in_users.get(message.from_user.id).realname))

@bot.message_handler(func=lambda m: m.text == "My Profile🔒")
def handle_profile(message):
    user_id = message.from_user.id
    user = logged_in_users.get(user_id)
    if user:
        text = (
            f"Good Day <b>{user.realname}</b>!\n"
            f"Your Status: {user.status}\n"
            f"You are a student in: <i>{user.grs}</i>\n"
            f"{f'Your Payment Status: <b><i>{user.pstat}</i></b>' if hasattr(user, 'pstat') else ''}\n\n"
            f"<code>❗If you want to switch accounts, press 'Log out'.</code>"
        )
        clean_and_respond(message, text, get_keyboard(user_id))
    else:
        clean_and_respond(message, "Please enter your login:", get_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "About")
def handle_about(message):
    clean_and_respond(
        message,
        "🤖 This is the official bot of Vibrant Educational Center.\n"
        "Use it to log in, view your groups, and manage student access.\n"
        "For support, contact @zufar_BRO.",
        get_keyboard(message.from_user.id)
    )

@bot.message_handler(func=lambda m: m.text == "➕ Add New Student")
def prompt_add_student(message):
    clean_and_respond(message, "Please send the student’s data in this format:\n\n"
                               "<code>class_name\npassword\nfull name\nstatus\ngroup\npayment status</code>\n\n"
                               "Each on a new line.\nAnd Please Do not forget\nto write 'English' in groups section\nbefore the actual\nname of the group",
                      get_keyboard(message.from_user.id))

def save_user_to_file(class_name, password, realname, status, grs, pstat):
    with open("users_list.py", "a", encoding="utf-8") as f:
        f.write(f"\n\nclass {class_name}:\n")
        f.write(f"    Password = \"{password}\"\n")
        f.write(f"    realname = \"{realname}\"\n")
        f.write(f"    status = \"{status}\"\n")
        f.write(f"    grs = \"{grs}\"\n")
        f.write(f"    pstat = \"{pstat}\"\n")

def remove_old_user(class_name):
    with open("users_list.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    skip = False
    for line in lines:
        if line.startswith(f"class {class_name}"):
            skip = True
            continue
        if skip and line.strip().startswith("class "):
            skip = False
        if not skip:
            new_lines.append(line)
    with open("users_list.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

@bot.message_handler(func=lambda m: len(m.text.split("\n")) == 6)
def add_or_edit_user(message):
    user = logged_in_users.get(message.from_user.id)
    if not user or user.realname not in ["Qozoqova Sevara", "Sharpbayev Diyor"]:
        return
    class_name, password, realname, status, grs, pstat = message.text.split("\n")
    if user.realname == "Qozoqova Sevara" and "English" not in grs:
        clean_and_respond(message, "You can only add students to the IELTS group!", get_keyboard(message.from_user.id))
        return
    if user.realname == "Sharpbayev Diyor" and "Math" not in grs:
        clean_and_respond(message, "You can only add students to the Math group!", get_keyboard(message.from_user.id))
        return
    remove_old_user(class_name)
    save_user_to_file(class_name, password, realname, status, grs, pstat)
    importlib.reload(users_list)
    dynamic_groups.generate_group_file()
    clean_and_respond(message, f"✅ Student <b>{realname}</b> has been updated/added successfully!",
                      get_keyboard(message.from_user.id))

@bot.message_handler(func=lambda m: m.text == "✏️ Edit Student")
def prompt_edit_student(message):
    user_id = message.from_user.id
    edit_mode_users.add(user_id)
    clean_and_respond(message, "✏️ Please send the student's <b>password</b> to edit:",
                      get_keyboard(user_id))

@bot.message_handler(func=lambda m: m.text == "Log out")
def handle_logout(message):
    user_id = message.from_user.id
    logged_in_users.pop(user_id, None)
    edit_mode_users.discard(user_id)
    clean_and_respond(message, "🔓 You have been logged out. Please log in again.",
                      get_keyboard(user_id))

@bot.message_handler(func=lambda message: True)
def handle_login_or_edit(message):
    importlib.reload(users_list)
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id in edit_mode_users:
        for attr_name in dir(users_list):
            attr = getattr(users_list, attr_name)
            if isinstance(attr, type) and hasattr(attr, "Password") and attr.Password == text:
                student = attr
                class_name = attr_name
                edit_mode_users.remove(user_id)
                clean_and_respond(
                    message,
                    f"<b>{class_name}</b>\n{student.Password}\n{student.realname}\n"
                    f"{student.status}\n{student.grs}\n{student.pstat}\n\nSend new version to update.",
                    get_keyboard(user_id)
                )
                return
        clean_and_respond(message, "❌ No student found with that password.", get_keyboard(user_id))
        return

    for attr_name in dir(users_list):
        attr = getattr(users_list, attr_name)
        if isinstance(attr, type) and hasattr(attr, "Password") and attr.Password == text:
            logged_in_users[user_id] = attr
            handle_profile(message)
            return

    clean_and_respond(message, "This login or code does not exist.\nPlease contact @zufar_BRO",
                      get_keyboard(user_id))

if __name__ == "__main__":
    bot.infinity_polling()
