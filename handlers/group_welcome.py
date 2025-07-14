from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.enums import ChatType
from aiogram.types import (
    ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, Message
)
from database import set_group_language

router = Router()

# Guruhdagi /start komandasi (faqat adminlar uchun)
@router.message(CommandStart(), F.chat.type.in_({"group", "supergroup"}))
async def group_start_handler(message: Message):
    admins = await message.bot.get_chat_administrators(message.chat.id)
    if message.from_user.id not in [admin.user.id for admin in admins]:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="group_lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="group_lang:ru")
        ]
    ])
    text = (
        "Assalomu alaykum.\n\n"
        "🤖 Botni guruhda ishlatish uchun unga quyidagi admin funksiyalarini yoqing:\n\n"
        "🗑 Xabarlarni o'chirish\n"
        "🚫 Foydalanuvchilarni bloklash\n"
        "📌 Xabarlarni qadash\n\n"
        "🌐 Bot tilini tanlang:"
    )
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# Til tanlang tugmasi bosilganda
@router.callback_query(F.data.startswith("group_lang:"))
async def set_group_lang(cb: CallbackQuery):
    lang = cb.data.split(":")[1]
    chat_id = cb.message.chat.id

    set_group_language(chat_id, lang)

    msg = (
        "✅ Guruh tili muvaffaqiyatli o‘rnatildi!" if lang == "uz"
        else "✅ Язык группы успешно установлен!"
    )
    await cb.message.edit_text(msg)
    await cb.answer()
