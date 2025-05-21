import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import uuid

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

if not os.path.exists("files"):
    os.makedirs("files")

ADD_GROUP, ADD_GROUP_NAME = range(2)
(
    ADD_STUDENT,
    ADD_STUDENT_NAME,
    ADD_STUDENT_TG_ID,
    ADD_STUDENT_GROUP,
    ADD_STUDENT_CURATOR,
) = range(5)
(
    ADD_CURATOR,
    ADD_CURATOR_NAME,
    ADD_CURATOR_TG_ID,
    ADD_CURATOR_DEPARTMENT,
    ADD_CURATOR_GROUPS,
) = range(5)
VIEW_STUDENTS, VIEW_CURATORS, VIEW_GROUPS = range(3)

SEND_MESSAGE, MESSAGE_TEXT, MESSAGE_CONFIRM, MESSAGE_SEND = range(4)
(
    SEND_PERSONAL_MESSAGE,
    SELECT_STUDENT,
    PERSONAL_MESSAGE_TEXT,
    PERSONAL_MESSAGE_CONFIRM,
    PERSONAL_MESSAGE_SEND,
) = range(5)
CREATE_NEWS, NEWS_TEXT, NEWS_CONFIRM = range(3)
CREATE_ANNOUNCEMENT, ANNOUNCEMENT_TEXT, ANNOUNCEMENT_CONFIRM = range(3)
CREATE_SURVEY, SURVEY_QUESTION, SURVEY_OPTIONS, SURVEY_CONFIRM = range(4)
(
    ADD_INFO,
    INFO_TYPE,
    INFO_TITLE,
    INFO_DESCRIPTION,
    INFO_CONTENT,
    INFO_CONFIRM,
) = range(6)

SEND_TO_CURATOR, STUDENT_MESSAGE_TEXT, STUDENT_MESSAGE_CONFIRM = range(3)

groups_db = {}
students_db = {}
curators_db = {}
messages_db = {}
news_db = {}
announcements_db = {}
surveys_db = {}
info_db = {}


def save_data() -> None:


    for db_name, db in [
        ("groups", groups_db),
        ("students", students_db),
        ("curators", curators_db),
        ("messages", messages_db),
        ("news", news_db),
        ("surveys", surveys_db),
        ("info", info_db),
    ]:
        for key, value in db.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, datetime):
                        value[k] = v.isoformat()

    with open("groups.json", "w", encoding="utf-8") as f:
        json.dump(groups_db, f, ensure_ascii=False, indent=2)

    with open("students.json", "w", encoding="utf-8") as f:
        json.dump(students_db, f, ensure_ascii=False, indent=2)

    with open("curators.json", "w", encoding="utf-8") as f:
        json.dump(curators_db, f, ensure_ascii=False, indent=2)

    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(messages_db, f, ensure_ascii=False, indent=2)

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_db, f, ensure_ascii=False, indent=2)

    with open("surveys.json", "w", encoding="utf-8") as f:
        json.dump(surveys_db, f, ensure_ascii=False, indent=2)

    with open("info.json", "w", encoding="utf-8") as f:
        json.dump(info_db, f, ensure_ascii=False, indent=2)


def load_data() -> None:

    try:

        with open("groups.json", "r", encoding="utf-8") as f:
            groups_data = json.load(f)
            globals()["groups_db"] = groups_data

        with open("students.json", "r", encoding="utf-8") as f:
            students_data = json.load(f)
            globals()["students_db"] = students_data

        with open("curators.json", "r", encoding="utf-8") as f:
            curators_data = json.load(f)
            globals()["curators_db"] = curators_data

        with open("messages.json", "r", encoding="utf-8") as f:
            messages_data = json.load(f)
            globals()["messages_db"] = messages_data

        with open("news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
            globals()["news_db"] = news_data

        with open("surveys.json", "r", encoding="utf-8") as f:
            surveys_data = json.load(f)
            globals()["surveys_db"] = surveys_data

        with open("info.json", "r", encoding="utf-8") as f:
            info_data = json.load(f)
            globals()["info_db"] = info_data

        for db_name, db in [
            ("groups", groups_db),
            ("students", students_db),
            ("curators", curators_db),
            ("messages", messages_db),
            ("news", news_db),
            ("surveys", surveys_db),
            ("info", info_db),
        ]:
            for key, value in db.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, str):
                            try:
                                value[k] = datetime.fromisoformat(v)
                            except ValueError:
                                pass

    except FileNotFoundError:

        globals()["groups_db"] = {}
        globals()["students_db"] = {}
        globals()["curators_db"] = {}
        globals()["messages_db"] = {}
        globals()["news_db"] = {}
        globals()["surveys_db"] = {}
        globals()["info_db"] = {}


ADMIN_IDS = []  

SURVEY_RESPONSE = 100


def is_admin(user_id: int) -> bool:

    return user_id in ADMIN_IDS


def is_curator(user_id: int) -> bool:

    for curator in curators_db.values():
        if curator.get("tg_id") == user_id:
            return True
    return False


def is_student(user_id: int) -> bool:


    for student in students_db.values():
        if student.get("tg_id") == user_id:
            return True
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_id = update.effective_user.id

    if is_admin(user_id):
        keyboard = [
            [KeyboardButton("🏫 Управление группами")],
            [KeyboardButton("👨‍🎓 Управление студентами")],
            [KeyboardButton("👨‍🏫 Управление кураторами")],
            [KeyboardButton("📋 Просмотр списков")],
            [KeyboardButton("ℹ️ Помощь")],
        ]
        welcome_text = "👋 Добро пожаловать в админ-панель!\n\nВыберите раздел:"
    elif is_curator(user_id):
        keyboard = [
            [KeyboardButton("📨 Отправить сообщение")],
            [KeyboardButton("📢 Новости и объявления")],
            [KeyboardButton("📋 Опросы")],
            [KeyboardButton("➕ Добавить информацию")],
            [KeyboardButton("ℹ️ Помощь")],
        ]
        welcome_text = "👋 Добро пожаловать в панель куратора!\n\nВыберите действие:"
    elif is_student(user_id):
        keyboard = [
            [KeyboardButton("📊 Опросы")],
            [KeyboardButton("📨 Написать куратору")],
            [KeyboardButton("📚 Информация")],
            [KeyboardButton("ℹ️ Помощь")],
        ]
        welcome_text = "👋 Добро пожаловать в панель студента!\n\nВыберите действие:"
    else:
        await update.message.reply_text("У вас нет доступа к боту.")
        return

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_id = update.effective_user.id

    if is_admin(user_id):
        help_text = """
📚 Основные команды:

/start - Начать работу с админ-панелью
/help - Показать это сообщение

📱 Основные разделы:

🏫 Управление группами:
- Добавить группу
- Удалить группу
- Просмотр групп

👨‍🎓 Управление студентами:
- Добавить студента
- Удалить студента
- Просмотр студентов

👨‍🏫 Управление кураторами:
- Добавить куратора
- Удалить куратора
- Просмотр кураторов

📋 Просмотр списков:
- Список групп
- Список студентов
- Список кураторов
"""
    elif is_curator(user_id):
        help_text = """
📚 Основные команды:

/start - Начать работу с ботом
/help - Показать это сообщение

📱 Основные разделы:

📨 Отправить сообщение:
- Отправка сообщений студентам группы
- Просмотр истории сообщений

📢 Новости и объявления:
- Создание новостей
- Создание объявлений
- Просмотр истории

📋 Опросы:
- Создание опросов
- Просмотр результатов
- Управление опросами

📚 Информация:
- Добавление информации для студентов
"""
    elif is_student(user_id):
        help_text = """
📚 Основные команды:

/start - Начать работу с ботом
/help - Показать это сообщение

📱 Основные разделы:

📚 Информация:
- Просмотр информации от куратора
"""
    else:
        await update.message.reply_text("У вас нет доступа к боту.")
        return

    await update.message.reply_text(help_text)


async def handle_groups_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    keyboard = [
        [KeyboardButton("➕ Добавить группу")],
        [KeyboardButton("➖ Удалить группу")],
        [KeyboardButton("📋 Список групп")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие с группами:", reply_markup=reply_markup
    )


async def handle_add_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return ConversationHandler.END

    await update.message.reply_text("Введите название группы:")
    return ADD_GROUP_NAME


async def handle_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    group_name = update.message.text

    group_id = len(groups_db) + 1
    groups_db[group_id] = {
        "name": group_name,
        "students": [],
        "curator_id": None,
        "added_at": datetime.now(),
    }


    save_data()

    await update.message.reply_text(
        f"✅ Группа успешно добавлена!\n\n" f"Название: {group_name}"
    )

    await handle_groups_menu(update, context)
    return ConversationHandler.END


async def handle_students_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    keyboard = [
        [KeyboardButton("➕ Добавить студента")],
        [KeyboardButton("➖ Удалить студента")],
        [KeyboardButton("📋 Список студентов")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие со студентами:", reply_markup=reply_markup
    )


async def handle_add_student(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return ConversationHandler.END

    if not groups_db:
        await update.message.reply_text("Нет доступных групп. Сначала добавьте группу.")
        return ConversationHandler.END

    await update.message.reply_text("Введите ФИО студента:")
    return ADD_STUDENT_NAME


async def handle_student_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    context.user_data["student_name"] = update.message.text

    await update.message.reply_text(
        "Введите ID студента в Telegram (можно получить у @userinfobot):"
    )
    return ADD_STUDENT_TG_ID


async def handle_student_tg_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    try:
        tg_id = int(update.message.text)
        context.user_data["student_tg_id"] = tg_id
    except ValueError:
        await update.message.reply_text("ID должен быть числом. Попробуйте еще раз:")
        return ADD_STUDENT_TG_ID

    keyboard = []
    for group_id, group in groups_db.items():
        keyboard.append([KeyboardButton(group["name"])])

    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите группу для студента:", reply_markup=reply_markup
    )
    return ADD_STUDENT_GROUP


async def handle_student_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_students_menu(update, context)
        return ConversationHandler.END

    group_name = update.message.text
    group_id = None

    for g_id, group in groups_db.items():
        if group["name"] == group_name:
            group_id = g_id
            break

    if not group_id:
        await update.message.reply_text("Группа не найдена.")
        return ADD_STUDENT_GROUP

    curator_id = groups_db[group_id].get("curator_id")
    if not curator_id:
        await update.message.reply_text(
            "В этой группе нет куратора. Сначала назначьте куратора группе."
        )
        return ConversationHandler.END

    student_id = len(students_db) + 1
    students_db[student_id] = {
        "name": context.user_data["student_name"],
        "tg_id": context.user_data["student_tg_id"],
        "group_id": group_id,
        "curator_id": curator_id,
        "added_at": datetime.now(),
    }

    groups_db[group_id]["students"].append(student_id)

    save_data()

    curator_name = curators_db[curator_id]["name"]
    await update.message.reply_text(
        f"✅ Студент успешно добавлен!\n\n"
        f"ФИО: {context.user_data['student_name']}\n"
        f"ID в Telegram: {context.user_data['student_tg_id']}\n"
        f"Группа: {group_name}\n"
        f"Куратор: {curator_name}"
    )

    await handle_students_menu(update, context)
    return ConversationHandler.END


async def handle_messages_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    context.user_data["conversation_state"] = None

    keyboard = [
        [KeyboardButton("✉️ Отправить сообщение группе")],
        [KeyboardButton("👤 Отправить личное сообщение")],
        [KeyboardButton("📜 История сообщений")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие с сообщениями:", reply_markup=reply_markup
    )


async def handle_send_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    curator_id = None
    for c_id, curator in curators_db.items():
        if str(curator.get("tg_id")) == str(update.effective_user.id):
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return ConversationHandler.END

    curator_groups = []
    for group_id, group in groups_db.items():
        if str(group.get("curator_id")) == str(curator_id):
            curator_groups.append(group)

    if not curator_groups:
        await update.message.reply_text("У вас нет групп для отправки сообщений.")
        return ConversationHandler.END

    keyboard = []
    for group in curator_groups:
        keyboard.append([KeyboardButton(group["name"])])

    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите группу для отправки сообщения:", reply_markup=reply_markup
    )
    return MESSAGE_TEXT


async def handle_message_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    context.user_data["message_group"] = update.message.text

    await update.message.reply_text("Введите текст сообщения:")
    return MESSAGE_CONFIRM


async def handle_message_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "❌ Отменить":
        await update.message.reply_text("Отправка сообщения отменена.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    context.user_data["message_text"] = update.message.text

    group_name = context.user_data["message_group"]
    group_id = None
    for g_id, group in groups_db.items():
        if group["name"] == group_name:
            group_id = g_id
            break

    if not group_id:
        await update.message.reply_text("Группа не найдена.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    keyboard = [
        [KeyboardButton("✅ Отправить")],
        [KeyboardButton("❌ Отменить")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Подтвердите отправку сообщения в группу {group_name}:\n\n"
        f"{context.user_data['message_text']}",
        reply_markup=reply_markup,
    )
    return MESSAGE_SEND


async def handle_message_send(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "❌ Отменить":
        await update.message.reply_text("Отправка сообщения отменена.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    if update.message.text != "✅ Отправить":
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для подтверждения."
        )
        return MESSAGE_SEND

    group_name = context.user_data["message_group"]
    group_id = None
    for g_id, group in groups_db.items():
        if group["name"] == group_name:
            group_id = g_id
            break

    if not group_id:
        await update.message.reply_text("Группа не найдена.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    message_id = len(messages_db) + 1
    messages_db[message_id] = {
        "text": context.user_data["message_text"],
        "group_id": group_id,
        "curator_id": curator_id,
        "timestamp": datetime.now(),
        "is_personal": False,
    }

    save_data()

    students = []
    for student_id in groups_db[group_id]["students"]:
        if student_id in students_db:
            students.append(students_db[student_id])

    for student in students:
        try:
            await context.bot.send_message(
                chat_id=student["tg_id"],
                text=f"📨 Сообщение от куратора:\n\n{context.user_data['message_text']}",
            )
        except Exception as e:
            logger.error(f"Failed to send message to student {student['name']}: {e}")

    await update.message.reply_text("✅ Сообщение успешно отправлено!")
    await handle_messages_menu(update, context)
    return ConversationHandler.END


async def handle_news_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [KeyboardButton("📢 Создать новость")],
        [KeyboardButton("📝 Создать объявление")],
        [KeyboardButton("📜 История")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие с новостями и объявлениями:", reply_markup=reply_markup
    )


async def handle_create_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    await update.message.reply_text("Введите текст новости:")
    return NEWS_TEXT


async def handle_news_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    context.user_data["news_text"] = update.message.text

    keyboard = [
        [KeyboardButton("✅ Опубликовать")],
        [KeyboardButton("❌ Отменить")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Подтвердите публикацию новости:\n\n{context.user_data['news_text']}",
        reply_markup=reply_markup,
    )
    return NEWS_CONFIRM


async def handle_news_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "❌ Отменить":
        await update.message.reply_text("Публикация новости отменена.")
        await handle_news_menu(update, context)
        return ConversationHandler.END

    news_id = len(news_db) + 1
    news_db[news_id] = {
        "text": context.user_data["news_text"],
        "curator_id": update.effective_user.id,
        "timestamp": datetime.now(),
    }

    await update.message.reply_text("✅ Новость успешно опубликована!")
    await handle_news_menu(update, context)
    return ConversationHandler.END


async def handle_surveys_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    keyboard = [
        [KeyboardButton("📝 Создать опрос")],
        [KeyboardButton("📊 Результаты")],
        [KeyboardButton("📜 История")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие с опросами:", reply_markup=reply_markup
    )


async def handle_create_survey(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    await update.message.reply_text("Введите вопрос опроса:")
    return SURVEY_QUESTION


async def handle_survey_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["survey_question"] = update.message.text
    await update.message.reply_text(
        "Введите варианты ответов через запятую (например: Да, Нет, Не знаю):"
    )
    return SURVEY_OPTIONS


async def handle_survey_options(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    options = [opt.strip() for opt in update.message.text.split(",")]
    context.user_data["survey_options"] = options

    keyboard = [
        [KeyboardButton("✅ Создать")],
        [KeyboardButton("❌ Отменить")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    text = f"Вопрос: {context.user_data['survey_question']}\n\nВарианты ответов:\n"
    for i, option in enumerate(options, 1):
        text += f"{i}. {option}\n"

    await update.message.reply_text(
        f"Подтвердите создание опроса:\n\n{text}", reply_markup=reply_markup
    )
    return SURVEY_CONFIRM


async def handle_survey_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "❌ Отменить":
        await update.message.reply_text("Создание опроса отменено.")
        await handle_surveys_menu(update, context)
        return ConversationHandler.END

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        await handle_surveys_menu(update, context)
        return ConversationHandler.END

    survey_id = len(surveys_db) + 1
    surveys_db[survey_id] = {
        "question": context.user_data["survey_question"],
        "options": context.user_data["survey_options"],
        "curator_id": curator_id,
        "timestamp": datetime.now(),
        "responses": {},
    }

    save_data()

    await update.message.reply_text("✅ Опрос успешно создан!")
    await handle_surveys_menu(update, context)
    return ConversationHandler.END


async def handle_info_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    keyboard = [
        [KeyboardButton("➕ Добавить информацию")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие с информацией:", reply_markup=reply_markup
    )


async def handle_add_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    keyboard = [
        [KeyboardButton("📊 Оценки")],
        [KeyboardButton("🔗 Ссылки")],
        [KeyboardButton("📎 Другое")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите тип информации для добавления:", reply_markup=reply_markup
    )
    return INFO_TYPE


async def handle_info_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if update.message.text == "🔙 Назад":
        context.user_data["conversation_state"] = None
        await handle_info_menu(update, context)
        return ConversationHandler.END

    if update.message.text not in ["📊 Оценки", "🔗 Ссылки", "📎 Другое"]:
        await update.message.reply_text("Пожалуйста, выберите тип информации из предложенных.")
        return INFO_TYPE

    context.user_data["info_type"] = update.message.text
    context.user_data["conversation_state"] = INFO_TITLE
    await update.message.reply_text("Введите заголовок:")
    return INFO_TITLE


async def handle_info_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    if update.message.text == "🔙 Назад":
        context.user_data["conversation_state"] = INFO_TYPE
        await handle_add_info(update, context)
        return INFO_TYPE

    context.user_data["info_title"] = update.message.text
    context.user_data["conversation_state"] = INFO_DESCRIPTION
    await update.message.reply_text("Введите описание:")
    return INFO_DESCRIPTION


async def handle_info_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        context.user_data["conversation_state"] = INFO_TITLE
        await update.message.reply_text("Введите заголовок:")
        return INFO_TITLE

    context.user_data["info_description"] = update.message.text
    context.user_data["conversation_state"] = INFO_CONTENT


    info_type = context.user_data.get("info_type", "")
    
    if info_type == "📊 Оценки":
        await update.message.reply_text("Отправьте файл с оценками (Excel, CSV или текстовый файл):")
    elif info_type == "🔗 Ссылки":
        await update.message.reply_text("Введите ссылку:")
    else:
        await update.message.reply_text("Отправьте файл или введите текст (максимальный размер файла 50 МБ):")

    return INFO_CONTENT


async def handle_info_content(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        context.user_data["conversation_state"] = INFO_DESCRIPTION
        await update.message.reply_text("Введите описание:")
        return INFO_DESCRIPTION


    info_type = context.user_data.get("info_type", "")

    if update.message.document:
        if update.message.document.file_size > 50 * 1024 * 1024:  
            await update.message.reply_text("Размер файла превышает 50 МБ. Пожалуйста, отправьте файл меньшего размера.")
            return INFO_CONTENT

        try:
            file = await context.bot.get_file(update.message.document.file_id)
            file_path = os.path.join("files", update.message.document.file_name)
            await file.download_to_drive(file_path)
            context.user_data["info_content"] = {
                "type": "file",
                "path": file_path,
                "name": update.message.document.file_name,
                "file_id": update.message.document.file_id
            }
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await update.message.reply_text("Произошла ошибка при загрузке файла. Пожалуйста, попробуйте еще раз.")
            return INFO_CONTENT
    else:
        context.user_data["info_content"] = {
            "type": "text",
            "content": update.message.text
        }

    context.user_data["conversation_state"] = INFO_CONFIRM
    keyboard = [
        [KeyboardButton("✅ Добавить")],
        [KeyboardButton("❌ Отменить")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    info_type = context.user_data.get("info_type", "")
    title = context.user_data.get("info_title", "")
    description = context.user_data.get("info_description", "")
    content = context.user_data.get("info_content", {})

    text = (
        f"Подтвердите добавление информации:\n\n"
        f"Тип: {info_type}\n"
        f"Заголовок: {title}\n"
        f"Описание: {description}\n"
    )

    if content.get("type") == "file":
        text += f"Файл: {content.get('name', '')}"
    else:
        text += f"Содержимое: {content.get('content', '')}"

    await update.message.reply_text(text, reply_markup=reply_markup)
    return INFO_CONFIRM


async def handle_info_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "❌ Отменить":
        context.user_data["conversation_state"] = None
        await update.message.reply_text("Добавление информации отменено.")
        await handle_info_menu(update, context)
        return ConversationHandler.END

    if update.message.text != "✅ Добавить":
        await update.message.reply_text("Пожалуйста, используйте кнопки для подтверждения.")
        return INFO_CONFIRM

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        context.user_data["conversation_state"] = None
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        await handle_info_menu(update, context)
        return ConversationHandler.END

    info_id = len(info_db) + 1
    info_db[info_id] = {
        "type": context.user_data["info_type"],
        "title": context.user_data["info_title"],
        "description": context.user_data["info_description"],
        "content": context.user_data["info_content"],
        "curator_id": curator_id,
        "timestamp": datetime.now()
    }


    save_data()

    context.user_data["conversation_state"] = None
    await update.message.reply_text("✅ Информация успешно добавлена!")
    await handle_info_menu(update, context)
    return ConversationHandler.END


async def handle_info_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return

    curator_info = []
    for info_id, info in info_db.items():
        if info.get("curator_id") == curator_id:
            curator_info.append(info)

    if not curator_info:
        await update.message.reply_text("У вас пока нет добавленной информации.")
        return

    text = "📋 Список вашей информации:\n\n"
    for info in curator_info:
        text += (
            f"📌 {info['type']}\n"
            f"Заголовок: {info['title']}\n"
            f"Описание: {info['description']}\n"
            f"Добавлено: {info['timestamp'].strftime('%d.%m.%Y %H:%M')}\n\n"
        )

    await update.message.reply_text(text)
    await handle_info_menu(update, context)


async def handle_student_info(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    keyboard = [
        [KeyboardButton("📊 Оценки")],
        [KeyboardButton("🔗 Ссылки")],
        [KeyboardButton("📎 Другое")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите тип информации:", reply_markup=reply_markup
    )


async def handle_student_info_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    if update.message.text == "🔙 Назад":
        await handle_student_menu(update, context)
        return

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        return

    info_type = update.message.text
    student_info = []

    curator_id = students_db[student_id].get("curator_id")
    if curator_id:
        for info_id, info in info_db.items():
            if info.get("curator_id") == curator_id and info.get("type") == info_type:
                student_info.append(info)
    
    if not student_info:
        for info_id, info in info_db.items():
            if info.get("type") == info_type:
                student_info.append(info)

    if not student_info:
        await update.message.reply_text(f"Пока нет доступной информации типа {info_type}.")
        return

    text = f"📋 Доступная информация ({info_type}):\n\n"
    for info in student_info:
        text += (
            f"📌 {info['title']}\n"
            f"Описание: {info['description']}\n"
            f"Добавлено: {info['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
        )

        if info["content"]["type"] == "file":
            text += f"Файл: {info['content']['name']}\n"

            try:
                await update.message.reply_document(
                    document=info["content"]["file_id"], caption=text
                )
                text = ""  
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                text += "❌ Ошибка при отправке файла\n"
        else:
            text += f"Содержимое: {info['content']['content']}\n"

        text += "\n"

    if text.strip():  
        await update.message.reply_text(text)

    await handle_student_info(update, context)


async def handle_student_surveys(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        return

    curator_id = students_db[student_id].get("curator_id")
    if not curator_id:
        await update.message.reply_text("У вас нет назначенного куратора.")
        return

    curator_surveys = []
    for survey_id, survey in surveys_db.items():
        if survey.get("curator_id") == curator_id:
            curator_surveys.append((survey_id, survey))

    if not curator_surveys:
        await update.message.reply_text("Пока нет доступных опросов.")
        return

    keyboard = []
    for survey_id, survey in curator_surveys:

        student_tg_id = update.effective_user.id
        has_responded = student_tg_id in survey.get("responses", {})
        status = "✅" if has_responded else "📝"
        keyboard.append(
            [
                KeyboardButton(
                    f"{status} Опрос от {survey['timestamp'].strftime('%d.%m.%Y %H:%M')}"
                )
            ]
        )

    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите опрос для ответа:", reply_markup=reply_markup
    )


async def handle_survey_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_student_menu(update, context)
        return ConversationHandler.END

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        return ConversationHandler.END

    curator_id = students_db[student_id].get("curator_id")
    if not curator_id:
        await update.message.reply_text("У вас нет назначенного куратора.")
        return ConversationHandler.END

    try:
        survey_timestamp = datetime.strptime(
            update.message.text.split("Опрос от ")[1], "%d.%m.%Y %H:%M"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Ошибка выбора опроса. Попробуйте еще раз.")
        return ConversationHandler.END

    selected_survey = None
    for survey_id, survey in surveys_db.items():
        if (
            survey["timestamp"].strftime("%d.%m.%Y %H:%M")
            == survey_timestamp.strftime("%d.%m.%Y %H:%M")
            and survey.get("curator_id") == curator_id
        ):
            selected_survey = (survey_id, survey)
            break

    if not selected_survey:
        await update.message.reply_text("Опрос не найден.")
        return ConversationHandler.END

    survey_id, survey = selected_survey
    context.user_data["selected_survey_id"] = survey_id

    student_tg_id = update.effective_user.id
    if student_tg_id in survey.get("responses", {}):
        await update.message.reply_text("Вы уже ответили на этот опрос.")
        await handle_student_surveys(update, context)
        return ConversationHandler.END

    keyboard = []
    for i, option in enumerate(survey["options"], 1):
        keyboard.append([KeyboardButton(f"{i}. {option}")])
    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Вопрос: {survey['question']}\n\nВыберите вариант ответа:",
        reply_markup=reply_markup,
    )
    return SURVEY_RESPONSE


async def handle_survey_response(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not context.user_data.get("current_survey"):
        await update.message.reply_text("В данный момент нет активного опроса.")
        return

    survey_id = context.user_data["current_survey"]
    selected_option = update.message.text

    if survey_id not in surveys_db:
        await update.message.reply_text("Опрос не найден.")
        del context.user_data["current_survey"]
        return

    survey = surveys_db[survey_id]
    if selected_option not in survey["options"]:
        await update.message.reply_text(
            "Пожалуйста, выберите один из предложенных вариантов ответа."
        )
        return


    if "responses" not in survey:
        survey["responses"] = {}

    survey["responses"][update.effective_user.id] = {
        "selected_option": selected_option,
        "timestamp": datetime.now()
    }
    surveys_db[survey_id] = survey


    del context.user_data["current_survey"]

    await update.message.reply_text("Спасибо за ваш ответ! 🎉")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user_id = update.effective_user.id
    text = update.message.text

    if not (is_admin(user_id) or is_curator(user_id) or is_student(user_id)):
        await update.message.reply_text("У вас нет доступа к боту.")
        return


    if text == "🔙 Назад":
        if is_curator(user_id):
            await start(update, context)
        elif is_student(user_id):
            await start(update, context)
        elif is_admin(user_id):
            await start(update, context)
        return

    if context.user_data.get("conversation_state") == SELECT_STUDENT:
        await handle_select_student(update, context)
        return
    elif context.user_data.get("conversation_state") == PERSONAL_MESSAGE_TEXT:
        await handle_personal_message_text(update, context)
        return
    elif context.user_data.get("conversation_state") == PERSONAL_MESSAGE_CONFIRM:
        await handle_personal_message_confirm(update, context)
        return

    if context.user_data.get("conversation_state") == INFO_TYPE:
        await handle_info_type(update, context)
        return
    elif context.user_data.get("conversation_state") == INFO_TITLE:
        await handle_info_title(update, context)
        return
    elif context.user_data.get("conversation_state") == INFO_DESCRIPTION:
        await handle_info_description(update, context)
        return
    elif context.user_data.get("conversation_state") == INFO_CONTENT:
        await handle_info_content(update, context)
        return
    elif context.user_data.get("conversation_state") == INFO_CONFIRM:
        await handle_info_confirm(update, context)
        return

    if text.startswith("📊 Опрос от "):
        await show_survey_results(update, context)
        return

    if is_admin(user_id):
        if text == "🏫 Управление группами":
            await handle_groups_menu(update, context)
        elif text == "👨‍🎓 Управление студентами":
            await handle_students_menu(update, context)
        elif text == "👨‍🏫 Управление кураторами":
            await handle_curators_menu(update, context)
        elif text == "📋 Просмотр списков":
            await handle_view_lists(update, context)
        elif text == "➕ Добавить группу":
            await handle_add_group(update, context)
        elif text == "➕ Добавить студента":
            await handle_add_student(update, context)
        elif text == "➕ Добавить куратора":
            await handle_add_curator(update, context)
        elif text == "📋 Список групп":
            await handle_view_groups(update, context)
        elif text == "📋 Список студентов":
            await handle_view_students(update, context)
        elif text == "📋 Список кураторов":
            await handle_view_curators(update, context)
        elif text == "🔙 Назад":
            await start(update, context)
        elif text == "ℹ️ Помощь":
            await help_command(update, context)
        else:
            await update.message.reply_text(
                "Я не понимаю эту команду. Используйте меню или /help для справки."
            )

    elif is_curator(user_id):
        if text == "📨 Отправить сообщение":
            await handle_messages_menu(update, context)
        elif text == "👤 Отправить личное сообщение":
            context.user_data["conversation_state"] = SELECT_STUDENT
            await handle_send_personal_message(update, context)
        elif text == "📢 Новости и объявления":
            await handle_news_menu(update, context)
        elif text == "📋 Опросы":
            await handle_surveys_menu(update, context)
        elif text == "📊 Результаты":
            await handle_survey_results(update, context)
        elif text == "📚 Информация":
            await handle_info_menu(update, context)
        elif text == "➕ Добавить информацию":
            context.user_data["conversation_state"] = INFO_TYPE
            await handle_add_info(update, context)
        elif text == "ℹ️ Помощь":
            await help_command(update, context)
        else:

            if "ID:" in text:
                await handle_select_student(update, context)
            else:
                await update.message.reply_text(
                    "Я не понимаю эту команду. Используйте меню или /help для справки."
                )

    elif is_student(user_id):
        if text == "📊 Опросы":
            await handle_student_surveys(update, context)
        elif text == "📨 Написать куратору":
            await handle_send_to_curator(update, context)
        elif text == "📚 Информация":
            await handle_student_info(update, context)
        elif text == "📢 Новости и объявления":
            await handle_student_news_menu(update, context)
        elif text == "📢 Новости":
            await handle_student_news(update, context)
        elif text == "📝 Объявления":
            await handle_student_announcements(update, context)
        elif text in ["📊 Оценки", "🔗 Ссылки", "📎 Другое"]:
            await handle_student_info_type(update, context)
        elif text == "🔙 Назад":
            await start(update, context)
        elif text == "ℹ️ Помощь":
            await help_command(update, context)
        else:
            await update.message.reply_text(
                "Я не понимаю эту команду. Используйте меню или /help для справки."
            )


async def show_survey_results(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не зарегистрированы как куратор.")
        return

    try:
        survey_timestamp = datetime.strptime(
            update.message.text.split("Опрос от ")[1], "%d.%m.%Y %H:%M"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Ошибка выбора опроса. Попробуйте еще раз.")
        return

    selected_survey = None
    for survey_id, survey in surveys_db.items():
        if survey["timestamp"].strftime("%d.%m.%Y %H:%M") == survey_timestamp.strftime(
            "%d.%m.%Y %H:%M"
        ):
            selected_survey = (survey_id, survey)
            break

    if not selected_survey:
        await update.message.reply_text("Опрос не найден.")
        return

    survey_id, survey = selected_survey

    text = f"📊 Результаты опроса от {survey['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
    text += f"❓ Вопрос: {survey['question']}\n\n"

    responses = {}
    total_responses = 0
    
    for response in survey.get('responses', {}).values():
        option = response.get('selected_option')
        if option:
            responses[option] = responses.get(option, 0) + 1
            total_responses += 1


    if total_responses > 0:
        for option in survey['options']:
            count = responses.get(option, 0)
            percentage = (count / total_responses) * 100
            bar_length = int(percentage / 5) 
            progress_bar = "█" * bar_length + "░" * (20 - bar_length)
            text += f"{option}: {count} ({percentage:.1f}%)\n"
            text += f"{progress_bar}\n\n"
        
        text += f"Всего ответов: {total_responses}"
    else:
        text += "Пока нет ответов на этот опрос."

    await update.message.reply_text(text)
    await handle_messages_menu(update, context)


async def handle_student_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    keyboard = [
        [KeyboardButton("📨 Написать куратору")],
        [KeyboardButton("📚 Информация")],
        [KeyboardButton("📊 Опросы")],
        [KeyboardButton("📢 Новости и объявления")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def handle_send_to_curator(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return ConversationHandler.END

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        return ConversationHandler.END

    curator_id = students_db[student_id].get("curator_id")
    if not curator_id or curator_id not in curators_db:
        await update.message.reply_text("У вас нет назначенного куратора.")
        return ConversationHandler.END

    await update.message.reply_text("Введите текст сообщения для куратора:")
    return STUDENT_MESSAGE_TEXT

async def handle_student_message_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    context.user_data["student_message_text"] = update.message.text

    keyboard = [
        [KeyboardButton("✅ Отправить")],
        [KeyboardButton("❌ Отменить")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Подтвердите отправку сообщения куратору:\n\n{context.user_data['student_message_text']}",
        reply_markup=reply_markup,
    )
    return STUDENT_MESSAGE_CONFIRM

async def handle_student_message_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "❌ Отменить":
        await update.message.reply_text("Отправка сообщения отменена.")
        await handle_student_menu(update, context)
        return ConversationHandler.END

    if update.message.text != "✅ Отправить":
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для подтверждения."
        )
        return STUDENT_MESSAGE_CONFIRM

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        await handle_student_menu(update, context)
        return ConversationHandler.END

    curator_id = students_db[student_id].get("curator_id")
    if not curator_id or curator_id not in curators_db:
        await update.message.reply_text("У вас нет назначенного куратора.")
        await handle_student_menu(update, context)
        return ConversationHandler.END

    curator = curators_db[curator_id]
    student = students_db[student_id]

    message_id = len(messages_db) + 1
    messages_db[message_id] = {
        "text": context.user_data["student_message_text"],
        "student_tg_id": update.effective_user.id,
        "curator_id": curator_id,
        "timestamp": datetime.now(),
        "is_from_student": True,
    }

    save_data()

    try:
        await context.bot.send_message(
            chat_id=curator["tg_id"],
            text=f"📨 Сообщение от студента {student['name']}:\n\n{context.user_data['student_message_text']}",
        )
        await update.message.reply_text("✅ Сообщение успешно отправлено!")
    except Exception as e:
        logger.error(f"Failed to send message to curator: {e}")
        await update.message.reply_text(
            "❌ Не удалось отправить сообщение. Возможно, куратор заблокировал бота."
        )

    await handle_student_menu(update, context)
    return ConversationHandler.END

async def handle_survey_results(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return

    curator_surveys = []
    for survey_id, survey in surveys_db.items():
        if survey.get("curator_id") == curator_id:
            curator_surveys.append((survey_id, survey))

    if not curator_surveys:
        await update.message.reply_text("У вас пока нет созданных опросов.")
        return

    keyboard = []
    for survey_id, survey in curator_surveys:
        keyboard.append(
            [
                KeyboardButton(
                    f"📊 Опрос от {survey['timestamp'].strftime('%d.%m.%Y %H:%M')}"
                )
            ]
        )

    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите опрос для просмотра результатов:", reply_markup=reply_markup
    )

async def handle_student_news_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    keyboard = [
        [KeyboardButton("📢 Новости")],
        [KeyboardButton("📝 Объявления")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите тип информации:", reply_markup=reply_markup
    )

async def handle_student_news(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    if update.message.text == "🔙 Назад":
        await handle_student_news_menu(update, context)
        return

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        return

    curator_id = students_db[student_id].get("curator_id")
    student_news = []
    
    if curator_id:

        for news_id, news in news_db.items():
            if news.get("curator_id") == curator_id:
                student_news.append(news)
    else:

        student_news = list(news_db.values())

    if not student_news:
        await update.message.reply_text("Пока нет доступных новостей.")
        return

    text = "📢 Новости:\n\n"
    for news in sorted(student_news, key=lambda x: x["timestamp"], reverse=True):
        text += (
            f"📌 {news['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
            f"Текст: {news['text']}\n\n"
        )

    await update.message.reply_text(text)
    await handle_student_news_menu(update, context)

async def handle_student_announcements(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_student(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели студента.")
        return

    if update.message.text == "🔙 Назад":
        await handle_student_news_menu(update, context)
        return

    student_id = None
    for s_id, student in students_db.items():
        if student.get("tg_id") == update.effective_user.id:
            student_id = s_id
            break

    if not student_id:
        await update.message.reply_text("Вы не зарегистрированы как студент.")
        return

    curator_id = students_db[student_id].get("curator_id")
    student_announcements = []
    
    if curator_id:

        for announcement_id, announcement in announcements_db.items():
            if announcement.get("curator_id") == curator_id:
                student_announcements.append(announcement)
    else:

        student_announcements = list(announcements_db.values())

    if not student_announcements:
        await update.message.reply_text("Пока нет доступных объявлений.")
        return

    text = "📝 Объявления:\n\n"
    for announcement in sorted(student_announcements, key=lambda x: x["timestamp"], reverse=True):
        text += (
            f"📌 {announcement['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
            f"Текст: {announcement['text']}\n\n"
        )

    await update.message.reply_text(text)
    await handle_student_news_menu(update, context)


async def handle_add_curator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return ConversationHandler.END

    await update.message.reply_text("Введите ФИО куратора:")
    return ADD_CURATOR_NAME


async def handle_curator_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    context.user_data["curator_name"] = update.message.text

    await update.message.reply_text(
        "Введите ID куратора в Telegram (можно получить у @userinfobot):"
    )
    return ADD_CURATOR_TG_ID


async def handle_curator_tg_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    try:
        tg_id = int(update.message.text)
        context.user_data["curator_tg_id"] = tg_id
    except ValueError:
        await update.message.reply_text("ID должен быть числом. Попробуйте еще раз:")
        return ADD_CURATOR_TG_ID

    await update.message.reply_text("Введите кафедру куратора:")
    return ADD_CURATOR_DEPARTMENT


async def handle_curator_department(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    context.user_data["curator_department"] = update.message.text

    keyboard = []
    for group_id, group in groups_db.items():
        keyboard.append([KeyboardButton(group["name"])])

    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите группы для куратора:", reply_markup=reply_markup
    )
    return ADD_CURATOR_GROUPS


async def handle_curator_groups(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_curators_menu(update, context)
        return ConversationHandler.END

    group_name = update.message.text
    group_id = None

    for g_id, group in groups_db.items():
        if group["name"] == group_name:
            group_id = g_id
            break

    if not group_id:
        await update.message.reply_text("Группа не найдена.")
        return ADD_CURATOR_GROUPS

    curator_id = len(curators_db) + 1
    curators_db[curator_id] = {
        "name": context.user_data["curator_name"],
        "tg_id": context.user_data["curator_tg_id"],
        "department": context.user_data["curator_department"],
        "groups": [group_id],
        "added_at": datetime.now(),
    }

    groups_db[group_id]["curator_id"] = curator_id

    save_data()

    await update.message.reply_text(
        f"✅ Куратор успешно добавлен!\n\n"
        f"ФИО: {context.user_data['curator_name']}\n"
        f"ID в Telegram: {context.user_data['curator_tg_id']}\n"
        f"Кафедра: {context.user_data['curator_department']}\n"
        f"Группа: {group_name}"
    )

    await handle_curators_menu(update, context)
    return ConversationHandler.END


async def handle_curators_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    keyboard = [
        [KeyboardButton("➕ Добавить куратора")],
        [KeyboardButton("➖ Удалить куратора")],
        [KeyboardButton("📋 Список кураторов")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите действие с кураторами:", reply_markup=reply_markup
    )


async def handle_personal_message_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    if update.message.text == "🔙 Назад":
        await handle_messages_menu(update, context)
        return ConversationHandler.END
    elif update.message.text in ["✅ Отправить", "❌ Отменить"]:
        return await handle_personal_message_confirm(update, context)

    context.user_data["personal_message_text"] = update.message.text

    keyboard = [
        [KeyboardButton("✅ Отправить")],
        [KeyboardButton("❌ Отменить")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Подтвердите отправку личного сообщения:\n\n{context.user_data['personal_message_text']}",
        reply_markup=reply_markup,
    )
    return PERSONAL_MESSAGE_CONFIRM


async def handle_personal_message_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_messages_menu(update, context)
        return ConversationHandler.END
    elif update.message.text == "❌ Отменить":
        await update.message.reply_text("Отправка сообщения отменена.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END
    elif update.message.text != "✅ Отправить":
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для подтверждения."
        )
        return PERSONAL_MESSAGE_CONFIRM

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    student_tg_id = context.user_data.get("selected_student_tg_id")
    student_name = context.user_data.get("selected_student_name")

    if not student_tg_id or not student_name:
        await update.message.reply_text("Ошибка: информация о студенте не найдена.")
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    message_id = len(messages_db) + 1
    messages_db[message_id] = {
        "text": context.user_data["personal_message_text"],
        "student_tg_id": student_tg_id,
        "curator_id": curator_id,
        "timestamp": datetime.now(),
        "is_personal": True,
    }

    save_data()

    try:
        await context.bot.send_message(
            chat_id=student_tg_id,
            text=f"📨 Сообщение от куратора:\n\n{context.user_data['personal_message_text']}",
        )
        await update.message.reply_text("✅ Сообщение успешно отправлено!")
    except Exception as e:
        logger.error(f"Failed to send message to student: {e}")
        await update.message.reply_text(
            "❌ Не удалось отправить сообщение. Возможно, студент заблокировал бота."
        )

    await handle_messages_menu(update, context)
    return ConversationHandler.END


async def handle_view_lists(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    keyboard = [
        [KeyboardButton("📋 Список групп")],
        [KeyboardButton("📋 Список студентов")],
        [KeyboardButton("📋 Список кураторов")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите список для просмотра:", reply_markup=reply_markup
    )


async def handle_view_groups(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    if not groups_db:
        await update.message.reply_text("Нет доступных групп.")
        return

    text = "📋 Список групп:\n\n"
    for group_id, group in groups_db.items():
        curator_name = "Нет куратора"
        if group.get("curator_id") in curators_db:
            curator_name = curators_db[group["curator_id"]]["name"]

        text += (
            f"Группа: {group['name']}\n"
            f"Куратор: {curator_name}\n"
            f"Количество студентов: {len(group.get('students', []))}\n\n"
        )

    await update.message.reply_text(text)
    await handle_view_lists(update, context)


async def handle_view_students(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    if not students_db:
        await update.message.reply_text("Нет зарегистрированных студентов.")
        return

    text = "📋 Список студентов:\n\n"
    for student_id, student in students_db.items():
        group_name = "Нет группы"
        if student.get("group_id") in groups_db:
            group_name = groups_db[student["group_id"]]["name"]

        curator_name = "Нет куратора"
        if student.get("curator_id") in curators_db:
            curator_name = curators_db[student["curator_id"]]["name"]

        text += (
            f"Студент: {student['name']}\n"
            f"ID в Telegram: {student['tg_id']}\n"
            f"Группа: {group_name}\n"
            f"Куратор: {curator_name}\n\n"
        )

    await update.message.reply_text(text)
    await handle_view_lists(update, context)


async def handle_view_curators(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return

    if not curators_db:
        await update.message.reply_text("Нет зарегистрированных кураторов.")
        return

    text = "📋 Список кураторов:\n\n"
    for curator_id, curator in curators_db.items():
        groups = []
        for group_id, group in groups_db.items():
            if group.get("curator_id") == curator_id:
                groups.append(group["name"])

        text += (
            f"Куратор: {curator['name']}\n"
            f"ID в Telegram: {curator['tg_id']}\n"
            f"Кафедра: {curator['department']}\n"
            f"Группы: {', '.join(groups) if groups else 'Нет групп'}\n\n"
        )

    await update.message.reply_text(text)
    await handle_view_lists(update, context)


async def handle_send_personal_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    curator_id = None
    for c_id, curator in curators_db.items():
        if str(curator.get("tg_id")) == str(update.effective_user.id):
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return ConversationHandler.END

    curator_students = []
    for student_id, student in students_db.items():
        if str(student.get("curator_id")) == str(curator_id):
            curator_students.append(student)

    if not curator_students:
        await update.message.reply_text("У вас нет студентов для отправки сообщений.")
        return ConversationHandler.END

    keyboard = []
    for student in curator_students:
        keyboard.append([KeyboardButton(f"{student['name']} (ID: {student['tg_id']})")])

    keyboard.append([KeyboardButton("🔙 Назад")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите студента для отправки сообщения:", reply_markup=reply_markup
    )
    return SELECT_STUDENT


async def handle_message_history(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return

    curator_messages = []
    for message_id, message in messages_db.items():
        if message.get("curator_id") == curator_id:
            curator_messages.append(message)

    if not curator_messages:
        await update.message.reply_text("У вас пока нет отправленных сообщений.")
        return

    text = "📜 История ваших сообщений:\n\n"
    for message in curator_messages:
        if message.get("is_personal"):

            student_name = "Неизвестный студент"
            for student in students_db.values():
                if student.get("tg_id") == message.get("student_tg_id"):
                    student_name = student["name"]
                    break
            text += (
                f"📨 Личное сообщение от {message['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
                f"Студент: {student_name}\n"
                f"Текст: {message['text']}\n\n"
            )
        else:

            group_name = "Неизвестная группа"
            if message.get("group_id") in groups_db:
                group_name = groups_db[message["group_id"]]["name"]
            text += (
                f"📨 Сообщение от {message['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
                f"Группа: {group_name}\n"
                f"Текст: {message['text']}\n\n"
            )

    await update.message.reply_text(text)
    await handle_messages_menu(update, context)


async def handle_select_student(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_messages_menu(update, context)
        return ConversationHandler.END

    try:
        if "ID:" in update.message.text:

            student_tg_id = int(update.message.text.split("ID:")[1].strip().rstrip(")"))
        else:

            student_tg_id = int(update.message.text.strip())
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Неверный формат ID студента. Используйте формат: 'имя (ID: номер)' или просто номер ID."
        )
        return SELECT_STUDENT

    student = None
    for s in students_db.values():
        if s.get("tg_id") == student_tg_id:
            student = s
            break

    if not student:
        await update.message.reply_text("Студент не найден.")
        return SELECT_STUDENT

    curator_id = None
    for c_id, curator in curators_db.items():
        if str(curator.get("tg_id")) == str(update.effective_user.id):
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return SELECT_STUDENT

    if str(student.get("curator_id")) != str(curator_id):
        await update.message.reply_text("У вас нет доступа к этому студенту.")
        return SELECT_STUDENT

    context.user_data["selected_student_tg_id"] = student_tg_id
    context.user_data["selected_student_name"] = student["name"]
    context.user_data["conversation_state"] = PERSONAL_MESSAGE_TEXT

    await update.message.reply_text("Введите текст сообщения:")
    return PERSONAL_MESSAGE_TEXT


async def handle_create_announcement(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return ConversationHandler.END

    await update.message.reply_text("Введите текст объявления:")
    return ANNOUNCEMENT_TEXT


async def handle_announcement_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

 
    if update.message.text == "🔙 Назад":
        await handle_news_menu(update, context)
        return ConversationHandler.END
    elif update.message.text in ["✅ Опубликовать", "❌ Отменить"]:
        return await handle_announcement_confirm(update, context)

    context.user_data["announcement_text"] = update.message.text

    keyboard = [
        [KeyboardButton("✅ Опубликовать")],
        [KeyboardButton("❌ Отменить")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Подтвердите публикацию объявления:\n\n{context.user_data['announcement_text']}",
        reply_markup=reply_markup,
    )
    return ANNOUNCEMENT_CONFIRM


async def handle_announcement_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    if update.message.text == "🔙 Назад":
        await handle_news_menu(update, context)
        return ConversationHandler.END
    elif update.message.text == "❌ Отменить":
        await update.message.reply_text("Публикация объявления отменена.")
        await handle_news_menu(update, context)
        return ConversationHandler.END
    elif update.message.text != "✅ Опубликовать":
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для подтверждения."
        )
        return ANNOUNCEMENT_CONFIRM

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        await handle_news_menu(update, context)
        return ConversationHandler.END

    announcement_id = len(announcements_db) + 1
    announcements_db[announcement_id] = {
        "text": context.user_data["announcement_text"],
        "curator_id": curator_id,
        "timestamp": datetime.now(),
    }


    save_data()

    await update.message.reply_text("✅ Объявление успешно опубликовано!")
    await handle_news_menu(update, context)
    return ConversationHandler.END


async def handle_news_history(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return

    curator_news = []
    curator_announcements = []

    for news_id, news in news_db.items():
        if news.get("curator_id") == curator_id:
            curator_news.append(news)

    for announcement_id, announcement in announcements_db.items():
        if announcement.get("curator_id") == curator_id:
            curator_announcements.append(announcement)

    if not curator_news and not curator_announcements:
        await update.message.reply_text(
            "У вас пока нет созданных новостей и объявлений."
        )
        return

    text = "📜 История новостей и объявлений:\n\n"

    if curator_news:
        text += "📢 Новости:\n"
        for news in sorted(curator_news, key=lambda x: x["timestamp"], reverse=True):
            text += (
                f"📌 {news['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
                f"Текст: {news['text']}\n\n"
            )

    if curator_announcements:
        text += "📝 Объявления:\n"
        for announcement in sorted(
            curator_announcements, key=lambda x: x["timestamp"], reverse=True
        ):
            text += (
                f"📌 {announcement['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
                f"Текст: {announcement['text']}\n\n"
            )

    await update.message.reply_text(text)
    await handle_news_menu(update, context)


async def handle_view_info_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    keyboard = [
        [KeyboardButton("📊 Оценки")],
        [KeyboardButton("🔗 Ссылки")],
        [KeyboardButton("📎 Другое")],
        [KeyboardButton("🔙 Назад")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите тип информации для просмотра:", reply_markup=reply_markup
    )

async def handle_curator_info_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not is_curator(update.effective_user.id):
        await update.message.reply_text("У вас нет доступа к панели куратора.")
        return

    if update.message.text == "🔙 Назад":
        await handle_info_menu(update, context)
        return

    curator_id = None
    for c_id, curator in curators_db.items():
        if curator.get("tg_id") == update.effective_user.id:
            curator_id = c_id
            break

    if not curator_id:
        await update.message.reply_text("Вы не назначены куратором ни одной группы.")
        return

    info_type = update.message.text
    curator_info = []
    for info_id, info in info_db.items():
        if info.get("curator_id") == curator_id and info.get("type") == info_type:
            curator_info.append(info)

    if not curator_info:
        await update.message.reply_text(f"Пока нет доступной информации типа {info_type}.")
        return

    text = f"📋 Доступная информация ({info_type}):\n\n"
    for info in curator_info:
        text += (
            f"📌 {info['title']}\n"
            f"Описание: {info['description']}\n"
            f"Добавлено: {info['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
        )

        if info["content"]["type"] == "file":
            text += f"Файл: {info['content']['name']}\n"

            try:
                await update.message.reply_document(
                    document=info["content"]["file_id"], caption=text
                )
                text = ""  
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                text += "❌ Ошибка при отправке файла\n"
        else:
            text += f"Содержимое: {info['content']['content']}\n"

        text += "\n"

    if text.strip():  
        await update.message.reply_text(text)

    await handle_info_menu(update, context)


def main() -> None:


    load_data()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Токен бота не найден! Убедитесь, что файл .env существует и содержит TELEGRAM_BOT_TOKEN")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📝 Опрос от .*$"), handle_survey_selection
                )
            ],
            states={
                SURVEY_RESPONSE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_survey_response
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📨 Написать куратору$"), handle_send_to_curator
                )
            ],
            states={
                STUDENT_MESSAGE_TEXT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_student_message_text
                    ),
                ],
                STUDENT_MESSAGE_CONFIRM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_student_message_confirm
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📊 Опросы$") & ~filters.COMMAND, handle_student_surveys
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📚 Информация$") & ~filters.COMMAND, handle_student_info
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^(📊 Оценки|🔗 Ссылки|📎 Другое)$") & ~filters.COMMAND,
            handle_student_info_type,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📢 Новости и объявления$") & ~filters.COMMAND,
            handle_student_news_menu,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Regex("^📢 Новости$") & ~filters.COMMAND,
            handle_student_news,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Regex("^📝 Объявления$") & ~filters.COMMAND,
            handle_student_announcements,
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^✉️ Отправить сообщение группе$"), handle_send_message
                )
            ],
            states={
                MESSAGE_TEXT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_message_text
                    ),
                ],
                MESSAGE_CONFIRM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_message_confirm
                    ),
                ],
                MESSAGE_SEND: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_message_send
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^➕ Добавить студента$"), handle_add_student
                )
            ],
            states={
                ADD_STUDENT_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_student_name
                    ),
                ],
                ADD_STUDENT_TG_ID: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_student_tg_id
                    ),
                ],
                ADD_STUDENT_GROUP: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_student_group
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex("^➕ Добавить группу$"), handle_add_group)
            ],
            states={
                ADD_GROUP_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group_name),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^➕ Добавить куратора$"), handle_add_curator
                )
            ],
            states={
                ADD_CURATOR_NAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_curator_name
                    ),
                ],
                ADD_CURATOR_TG_ID: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_curator_tg_id
                    ),
                ],
                ADD_CURATOR_DEPARTMENT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_curator_department
                    ),
                ],
                ADD_CURATOR_GROUPS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_curator_groups
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📝 Создать объявление$") & ~filters.COMMAND,
                    handle_create_announcement,
                )
            ],
            states={
                ANNOUNCEMENT_TEXT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        handle_announcement_text,
                    ),
                ],
                ANNOUNCEMENT_CONFIRM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_announcement_confirm
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📢 Создать новость$"), handle_create_news
                )
            ],
            states={
                NEWS_TEXT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_news_text),
                ],
                NEWS_CONFIRM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_news_confirm
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^📝 Создать опрос$"), handle_create_survey
                )
            ],
            states={
                SURVEY_QUESTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_survey_question
                    ),
                ],
                SURVEY_OPTIONS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_survey_options
                    ),
                ],
                SURVEY_CONFIRM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_survey_confirm
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    application.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    filters.Regex("^➕ Добавить информацию$"), handle_add_info
                )
            ],
            states={
                INFO_TYPE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_info_type),
                ],
                INFO_TITLE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_info_title),
                ],
                INFO_DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_info_description
                    ),
                ],
                INFO_CONTENT: [
                    MessageHandler(
                        filters.TEXT | filters.Document.ALL, handle_info_content
                    ),
                ],
                INFO_CONFIRM: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, handle_info_confirm
                    ),
                ],
            },
            fallbacks=[CommandHandler("start", start)],
        )
    )

    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
