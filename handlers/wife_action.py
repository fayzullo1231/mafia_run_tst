from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game

async def wife_action(bot: Bot):
    wife_id = next((p["id"] for p in active_game["players"]
                    if active_game["assignments"].get(p["id"]) == "donxotini"), None)

    if wife_id is None:
        return

    players = [p for p in active_game["players"] if p["id"] != wife_id]

    if not players:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"wife_protect:{p['id']}")]
            for p in players
        ] + [[InlineKeyboardButton(text="❌ Hech kimni tanlamayman", callback_data="wife_protect:skip")]]
    )

    await bot.send_message(
        wife_id,
        "🧕 Siz Donning xotinisiz!\nTun bo‘yi kimnidir himoya qilishingiz mumkin. Kimni himoya qilmoqchisiz?",
        reply_markup=keyboard
    )
