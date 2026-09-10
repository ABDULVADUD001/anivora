import os
import sqlite3
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)
from aiogram.filters import CommandStart, Command


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables ichida topilmadi!")

OWNER_ID = 8113271428

WEBAPP_URL = "https://abdulvadud001.github.io/anivora/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_NAME = "anivora.db"


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'uz',
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content_type TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content_type TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(user):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO users
        (user_id, username, first_name, language, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user.id,
        user.username,
        user.first_name,
        "uz",
        datetime.now().isoformat()
    ))

    cur.execute("""
        UPDATE users
        SET username = ?, first_name = ?
        WHERE user_id = ?
    """, (
        user.username,
        user.first_name,
        user.id
    ))

    conn.commit()
    conn.close()


def set_language(user_id, language):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET language = ?
        WHERE user_id = ?
    """, (language, user_id))

    conn.commit()
    conn.close()


def get_language(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,)
    )

    row = cur.fetchone()
    conn.close()

    if row:
        return row["language"]

    return "uz"


def add_history(user_id, title, content_type):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO history
        (user_id, title, content_type, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        title,
        content_type,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def add_favorite(user_id, title, content_type):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM favorites
        WHERE user_id = ? AND title = ? AND content_type = ?
    """, (
        user_id,
        title,
        content_type
    ))

    if cur.fetchone():
        conn.close()
        return False

    cur.execute("""
        INSERT INTO favorites
        (user_id, title, content_type, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        title,
        content_type,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return True


def remove_favorite(user_id, title, content_type):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM favorites
        WHERE user_id = ? AND title = ? AND content_type = ?
    """, (
        user_id,
        title,
        content_type
    ))

    conn.commit()
    conn.close()


def get_favorites(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT title, content_type
        FROM favorites
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return rows


def get_history(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT title, content_type
        FROM history
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 20
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return rows


def get_user_stats(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM history WHERE user_id = ?",
        (user_id,)
    )
    history_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM favorites WHERE user_id = ?",
        (user_id,)
    )
    favorites_count = cur.fetchone()[0]

    conn.close()

    return history_count, favorites_count


def get_total_users():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    result = cur.fetchone()[0]

    conn.close()

    return result


# =========================
# LANGUAGES
# =========================

LANGUAGES = {
    "uz": "🇺🇿 O‘zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "ja": "🇯🇵 日本語",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "tr": "🇹🇷 Türkçe",
    "ko": "🇰🇷 한국어",
    "zh": "🇨🇳 中文"
}


def language_keyboard():
    buttons = []

    for code, name in LANGUAGES.items():
        buttons.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"lang:{code}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# MAIN MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎌 Anime",
                    callback_data="anime"
                ),
                InlineKeyboardButton(
                    text="🎬 Kino",
                    callback_data="movie"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Global qidiruv",
                    callback_data="global_search"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Sevimlilar",
                    callback_data="favorites"
                ),
                InlineKeyboardButton(
                    text="🕘 Xronologiya",
                    callback_data="history"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Profil",
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    text="✦ AniVora Pass",
                    callback_data="pass"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Yordam",
                    callback_data="help"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚀 AniVora Mini App",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )


# =========================
# ANIME MENU
# =========================

def anime_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Yangi animelar",
                    callback_data="anime_new"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Mashhur",
                    callback_data="anime_popular"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🟢 Ongoing",
                    callback_data="anime_ongoing"
                ),
                InlineKeyboardButton(
                    text="✅ Completed",
                    callback_data="anime_completed"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎲 Random",
                    callback_data="anime_random"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Sevimlilar",
                    callback_data="anime_favorites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Bosh menyu",
                    callback_data="home"
                )
            ]
        ]
    )


# =========================
# MOVIE MENU
# =========================

def movie_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Yangi kinolar",
                    callback_data="movie_new"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Mashhur",
                    callback_data="movie_popular"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎭 Janrlar",
                    callback_data="movie_genres"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Yillar",
                    callback_data="movie_years"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Sevimlilar",
                    callback_data="movie_favorites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Bosh menyu",
                    callback_data="home"
                )
            ]
        ]
    )


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):
    add_user(message.from_user)

    await message.answer(
        "👋 <b>AniVora</b>ga xush kelibsiz!\n\n"
        "Avval tilni tanlang:",
        reply_markup=language_keyboard(),
        parse_mode="HTML"
    )


# =========================
# LANGUAGE
# =========================

@dp.callback_query(F.data.startswith("lang:"))
async def select_language(callback: CallbackQuery):
    language = callback.data.split(":")[1]

    set_language(
        callback.from_user.id,
        language
    )

    await callback.message.edit_text(
        "✨ <b>AniVora</b>\n\n"
        "Nimani izlaymiz?",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

    await callback.answer("Til saqlandi ✅")


# =========================
# HOME
# =========================

@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    await callback.message.edit_text(
        "✨ <b>AniVora</b>\n\n"
        "Anime, kino yoki boshqa bo‘limni tanlang:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# ANIME
# =========================

@dp.callback_query(F.data == "anime")
async def anime(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎌 <b>Anime</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=anime_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(
    F.data.in_({
        "anime_new",
        "anime_popular",
        "anime_ongoing",
        "anime_completed",
        "anime_random"
    })
)
async def anime_category(callback: CallbackQuery):

    names = {
        "anime_new": "🆕 Yangi animelar",
        "anime_popular": "🔥 Mashhur animelar",
        "anime_ongoing": "🟢 Ongoing animelar",
        "anime_completed": "✅ Completed animelar",
        "anime_random": "🎲 Random anime"
    }

    title = names.get(
        callback.data,
        "🎌 Anime"
    )

    await callback.message.edit_text(
        f"<b>{title}</b>\n\n"
        "⏳ Anime API hali ulanmagan.\n\n"
        "Keyingi bosqichda bu yerda haqiqiy "
        "anime posterlari va ma’lumotlari chiqadi.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Anime",
                        callback_data="anime"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# MOVIE
# =========================

@dp.callback_query(F.data == "movie")
async def movie(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎬 <b>Kino</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=movie_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(
    F.data.in_({
        "movie_new",
        "movie_popular",
        "movie_genres",
        "movie_years"
    })
)
async def movie_category(callback: CallbackQuery):

    names = {
        "movie_new": "🆕 Yangi kinolar",
        "movie_popular": "🔥 Mashhur kinolar",
        "movie_genres": "🎭 Kino janrlari",
        "movie_years": "📅 Kino yillari"
    }

    title = names.get(
        callback.data,
        "🎬 Kino"
    )

    await callback.message.edit_text(
        f"<b>{title}</b>\n\n"
        "⏳ Kino API hali ulanmagan.\n\n"
        "Keyingi bosqichda bu yerda haqiqiy "
        "kino posterlari va ma’lumotlari chiqadi.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Kino",
                        callback_data="movie"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# GLOBAL SEARCH
# =========================

@dp.callback_query(F.data == "global_search")
async def global_search(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔍 <b>Global qidiruv</b>\n\n"
        "Anime yoki kino nomini yozing.\n\n"
        "Masalan:\n"
        "• Naruto\n"
        "• One Piece\n"
        "• Avatar\n"
        "• Spider-Man",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# FAVORITES
# =========================

@dp.callback_query(F.data == "favorites")
async def favorites(callback: CallbackQuery):

    rows = get_favorites(callback.from_user.id)

    if not rows:
        text = (
            "⭐ <b>Sevimlilar</b>\n\n"
            "Hozircha sevimlilaringiz yo‘q."
        )
    else:
        text = "⭐ <b>Sevimlilar</b>\n\n"

        for i, row in enumerate(rows, 1):
            icon = (
                "🎌"
                if row["content_type"] == "anime"
                else "🎬"
            )

            text += (
                f"{i}. {icon} "
                f"{row['title']}\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "anime_favorites")
async def anime_favorites(callback: CallbackQuery):

    rows = get_favorites(callback.from_user.id)

    anime_rows = [
        row for row in rows
        if row["content_type"] == "anime"
    ]

    if not anime_rows:
        text = (
            "⭐ <b>Anime sevimlilar</b>\n\n"
            "Hozircha sevimli anime yo‘q."
        )
    else:
        text = "⭐ <b>Anime sevimlilar</b>\n\n"

        for i, row in enumerate(anime_rows, 1):
            text += f"{i}. 🎌 {row['title']}\n"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Anime",
                        callback_data="anime"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "movie_favorites")
async def movie_favorites(callback: CallbackQuery):

    rows = get_favorites(callback.from_user.id)

    movie_rows = [
        row for row in rows
        if row["content_type"] == "movie"
    ]

    if not movie_rows:
        text = (
            "⭐ <b>Kino sevimlilar</b>\n\n"
            "Hozircha sevimli kino yo‘q."
        )
    else:
        text = "⭐ <b>Kino sevimlilar</b>\n\n"

        for i, row in enumerate(movie_rows, 1):
            text += f"{i}. 🎬 {row['title']}\n"

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Kino",
                        callback_data="movie"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# HISTORY
# =========================

@dp.callback_query(F.data == "history")
async def history(callback: CallbackQuery):

    rows = get_history(callback.from_user.id)

    if not rows:
        text = (
            "🕘 <b>Xronologiya</b>\n\n"
            "Hozircha ko‘rilgan kontent yo‘q."
        )
    else:
        text = "🕘 <b>Xronologiya</b>\n\n"

        for i, row in enumerate(rows, 1):

            icon = (
                "🎌"
                if row["content_type"] == "anime"
                else "🎬"
            )

            text += (
                f"{i}. {icon} "
                f"{row['title']}\n"
            )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# PROFILE
# =========================

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    user = callback.from_user

    history_count, favorites_count = get_user_stats(
        user.id
    )

    username = (
        f"@{user.username}"
        if user.username
        else "Username yo‘q"
    )

    text = (
        "👤 <b>Profil</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Ism: {user.first_name}\n"
        f"🔗 Username: {username}\n\n"
        f"🕘 Ko‘rilgan: {history_count}\n"
        f"⭐ Sevimlilar: {favorites_count}\n"
        f"✦ Status: Free"
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🚀 Mini App",
                        web_app=WebAppInfo(
                            url=WEBAPP_URL
                        )
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# PASS
# =========================

@dp.callback_query(F.data == "pass")
async def pass_menu(callback: CallbackQuery):

    await callback.message.edit_text(
        "✦ <b>AniVora Pass</b>\n\n"
        "Premium foydalanuvchilar uchun "
        "qo‘shimcha imkoniyatlar.\n\n"
        "⭐ Premium bildirishnomalar\n"
        "🚫 Reklamasiz foydalanish\n"
        "⚡ Premium funksiyalar\n"
        "🎁 Maxsus imkoniyatlar\n\n"
        "💳 To‘lov tizimlari keyingi bosqichda ulanadi.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💎 Tariflarni ko‘rish",
                        callback_data="pass_plans"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


@dp.callback_query(F.data == "pass_plans")
async def pass_plans(callback: CallbackQuery):

    await callback.message.edit_text(
        "💎 <b>AniVora Pass tariflari</b>\n\n"
        "🗓 1 oy — 9 990 so‘m\n"
        "🗓 3 oy — 28 490 so‘m\n"
        "🗓 6 oy — 53 990 so‘m\n"
        "🗓 1 yil — 95 990 so‘m\n\n"
        "💳 To‘lov tizimlari keyingi bosqichda ulanadi.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Pass",
                        callback_data="pass"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# HELP
# =========================

@dp.callback_query(F.data == "help")
async def help_menu(callback: CallbackQuery):

    await callback.message.edit_text(
        "❓ <b>AniVora yordam</b>\n\n"
        "🎌 <b>Anime</b> — anime bo‘limlari.\n\n"
        "🎬 <b>Kino</b> — filmlar bo‘limi.\n\n"
        "🔍 <b>Global qidiruv</b> — anime va kinoni birgalikda qidirish.\n\n"
        "⭐ <b>Sevimlilar</b> — saqlangan kontent.\n\n"
        "🕘 <b>Xronologiya</b> — ko‘rilgan kontent.\n\n"
        "👤 <b>Profil</b> — shaxsiy statistika.\n\n"
        "✦ <b>AniVora Pass</b> — premium imkoniyatlar.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Bosh menyu",
                        callback_data="home"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# TEXT SEARCH
# =========================

@dp.message(F.text)
async def text_handler(message: Message):

    text = message.text.strip()

    if text.startswith("/"):
        return

    add_user(message.from_user)

    await message.answer(
        f"🔍 <b>Global qidiruv</b>\n\n"
        f"Qidiruv: <code>{text}</code>\n\n"
        "⏳ Hozircha Anime + Kino API ulanmagan.\n"
        "Keyingi bosqichda bu qidiruv orqali "
        "anime va kino natijalari birga chiqadi.",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )


# =========================
# ADMIN
# =========================

def admin_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Bosh menyu",
                    callback_data="home"
                )
            ]
        ]
    )


@dp.message(Command("admin"))
async def admin(message: Message):

    if message.from_user.id != OWNER_ID:
        await message.answer(
            "⛔ Sizda admin huquqi yo‘q."
        )
        return

    await message.answer(
        "🛠 <b>AniVora Admin Panel</b>",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )


@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    if callback.from_user.id != OWNER_ID:
        await callback.answer(
            "⛔ Ruxsat yo‘q.",
            show_alert=True
        )
        return

    total_users = get_total_users()

    await callback.message.edit_text(
        "📊 <b>AniVora statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: {total_users}",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# STARTUP
# =========================

async def main():

    init_db()

    print("================================")
    print("AniVora bot ishga tushmoqda...")
    print("================================")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
