import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! Railway Variables ga BOT_TOKEN qo‘shing.")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


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
    "zh": "🇨🇳 中文",
}


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message):
    keyboard = InlineKeyboardBuilder()

    for code, name in LANGUAGES.items():
        keyboard.button(
            text=name,
            callback_data=f"lang:{code}"
        )

    keyboard.adjust(2)

    await message.answer(
        "🌐 <b>AniVora</b>\n\n"
        "Tilni tanlang:",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


# =========================
# LANGUAGE SELECT
# =========================

@dp.callback_query(F.data.startswith("lang:"))
async def language_handler(callback: CallbackQuery):
    lang = callback.data.split(":")[1]

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🎌 Anime",
        callback_data=f"menu:anime:{lang}"
    )

    keyboard.button(
        text="🎬 Kino",
        callback_data=f"menu:movie:{lang}"
    )

    keyboard.button(
        text="🔍 Global qidiruv",
        callback_data=f"menu:search:{lang}"
    )

    keyboard.button(
        text="⭐ Sevimlilar",
        callback_data=f"menu:favorites:{lang}"
    )

    keyboard.button(
        text="🕐 Xronologiya",
        callback_data=f"menu:history:{lang}"
    )

    keyboard.button(
        text="👤 Profil",
        callback_data=f"menu:profile:{lang}"
    )

    keyboard.button(
        text="👑 AniVora Pass",
        callback_data=f"menu:pass:{lang}"
    )

    keyboard.button(
        text="🆘 Yordam",
        callback_data=f"menu:help:{lang}"
    )

    keyboard.adjust(2)

    await callback.message.edit_text(
        "✨ <b>AniVora</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# MENU
# =========================

@dp.callback_query(F.data.startswith("menu:"))
async def menu_handler(callback: CallbackQuery):
    parts = callback.data.split(":")
    section = parts[1]

    texts = {
        "anime": (
            "🎌 <b>Anime</b>\n\n"
            "Bu yerda anime katalogi bo‘ladi.\n"
            "🆕 Yangi animelar\n"
            "🔥 Mashhur animelar\n"
            "🟢 Ongoing\n"
            "✅ Completed"
        ),

        "movie": (
            "🎬 <b>Kino</b>\n\n"
            "Bu yerda filmlar katalogi bo‘ladi.\n"
            "🆕 Yangi kinolar\n"
            "🔥 Mashhur kinolar\n"
            "🎭 Janrlar\n"
            "📅 Yillar"
        ),

        "search": (
            "🔍 <b>Global qidiruv</b>\n\n"
            "Anime yoki kino nomini yozing.\n\n"
            "Masalan:\n"
            "<code>Naruto</code>\n"
            "<code>Avengers</code>"
        ),

        "favorites": (
            "⭐ <b>Sevimlilar</b>\n\n"
            "Hozircha sevimlilar ro‘yxati bo‘sh."
        ),

        "history": (
            "🕐 <b>Xronologiya</b>\n\n"
            "Ko‘rgan anime va kinolaringiz shu yerda chiqadi."
        ),

        "profile": (
            "👤 <b>Profil</b>\n\n"
            "Profil tizimi tez orada ulanadi."
        ),

        "pass": (
            "👑 <b>AniVora Pass</b>\n\n"
            "Premium imkoniyatlar tez orada qo‘shiladi."
        ),

        "help": (
            "🆘 <b>Yordam markazi</b>\n\n"
            "AniVora'dan foydalanish bo‘yicha yordam."
        ),
    }

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🏠 Bosh menyu",
        callback_data=f"back:{parts[2]}"
    )

    await callback.message.edit_text(
        texts.get(section, "❌ Bo‘lim topilmadi."),
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# BACK TO MENU
# =========================

@dp.callback_query(F.data.startswith("back:"))
async def back_handler(callback: CallbackQuery):
    lang = callback.data.split(":")[1]

    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="🎌 Anime", callback_data=f"menu:anime:{lang}")
    keyboard.button(text="🎬 Kino", callback_data=f"menu:movie:{lang}")
    keyboard.button(text="🔍 Global qidiruv", callback_data=f"menu:search:{lang}")
    keyboard.button(text="⭐ Sevimlilar", callback_data=f"menu:favorites:{lang}")
    keyboard.button(text="🕐 Xronologiya", callback_data=f"menu:history:{lang}")
    keyboard.button(text="👤 Profil", callback_data=f"menu:profile:{lang}")
    keyboard.button(text="👑 AniVora Pass", callback_data=f"menu:pass:{lang}")
    keyboard.button(text="🆘 Yordam", callback_data=f"menu:help:{lang}")

    keyboard.adjust(2)

    await callback.message.edit_text(
        "✨ <b>AniVora</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================
# TEXT SEARCH
# =========================

@dp.message(F.text)
async def text_handler(message: Message):
    query = message.text.strip()

    if not query:
        return

    await message.answer(
        f"🔍 <b>Global qidiruv</b>\n\n"
        f"Qidiruv: <code>{query}</code>\n\n"
        "⏳ Anime va kino bazasidan qidirish tizimi ulanmoqda...",
        parse_mode="HTML"
    )


# =========================
# RUN BOT
# =========================

async def main():
    print("AniVora bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
