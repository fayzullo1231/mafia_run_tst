from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from models.game_state import active_game
from .game_flow import update_registration_message, start_game_if_ready

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_deeplink(message: Message, bot: Bot):
    if active_game["chat_id"] is None:
        await message.answer("⛔ Guruhda /start_game bo‘lmasdan siz qo‘shila olmaysiz.")
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if any(p["id"] == user_id for p in active_game["players"]):
        await message.answer("✅ Siz allaqachon qo‘shilgansiz.")
        return

    active_game["players"].append({"id": user_id, "name": user_name})

    await update_registration_message(bot)

    await message.answer(
        f"✅ Tabriklaymiz, siz <b>{active_game['group_title']}</b> guruhda o'yinga qo'shildingiz!",
        parse_mode="HTML"
    )

    if len(active_game["players"]) >= 5:
        await start_game_if_ready(bot)
