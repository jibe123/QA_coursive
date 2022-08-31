import telebot
from config import TOKEN
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
from models import CoursesList, CoursesDetails
from db import db


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def welcome(message):
    cursor = db.cursor()
    welcome_text = f"""
Добро пожаловать!
С помощью этого бота Вы можете узнать информацию о курсах c сайта coursive.id!
Нажмите кнопку ниже чтобы узнать информацию о каком-либо курсе!"""
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    cursor.execute("SELECT * FROM courseslist")
    records = cursor.fetchall()
    rowcount = len(records)
    if rowcount > 0:
        pass
    else:
        CoursesList.parser()
    cursor.execute("SELECT title, slug FROM courseslist")
    all_items = cursor.fetchall()
    global sluglist
    sluglist = []
    for item in all_items:
        button = InlineKeyboardButton(item[0], callback_data=item[1].replace("-", "_"))
        sluglist.append(item[1].replace("-", "_"))
        markup.add(button)
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in sluglist)
def course_details(call):
    message = call.message
    cursor = db.cursor()
    slug = call.data.replace("_", "-")
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    query = CoursesDetails.select().where(CoursesDetails.details_slug_id == slug)
    if query.exists():
        pass
    else:
        CoursesDetails.parser(slug)
    cursor.execute("SELECT details_slug_id, date_created, title, name_tutor, description,"
                   "learn_to, blocks FROM coursesdetails WHERE details_slug_id = '%s'" % slug)
    all_items = cursor.fetchone()
    global dict_buttons
    dict_buttons = {"description": all_items[4], "learn_to": all_items[5],
                    "blocks": all_items[6]}
    global dict_keys
    dict_keys = {"description": "Описание курса", "learn_to": "Что можно узнать из курса?",
                 "blocks": "Из каких блоков состоит курс?"}
    for key, value in dict_buttons.items():
        button = InlineKeyboardButton(dict_keys.get(key), callback_data=key)
        markup.add(button)
    back = InlineKeyboardButton("Назад к списку курсов", callback_data="back_to_courses")
    markup.add(back)
    course_text = f"""
Ниже вы можете узнать информацию о курсе: <b>"{all_items[2]}"</b>!
<b>Дата создания курса</b>: {all_items[1]}.
<b>Преподаватель</b>: {all_items[3]}.
Нажмите кнопку ниже, чтобы узнать детальную информацию:"""
    bot.send_message(message.chat.id, course_text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in dict_buttons)
def course_blocks(call):
    message = call.message
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    block_text = dict_buttons.get(call.data)
    for key, value in dict_buttons.items():
        button = InlineKeyboardButton(dict_keys.get(key), callback_data=key)
        markup.add(button)
    back = InlineKeyboardButton("Назад к списку курсов", callback_data="back_to_courses")
    markup.add(back)
    bot.send_message(message.chat.id, block_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_courses")
def back_to_courses(call):
    welcome(call.message)


bot.infinity_polling()