from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game

async def mashuqa_action(bot: Bot):
    mashuqa_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "mashuqa"),
        None
    )

    if not mashuqa_id:
        return

    # Komissar tirikmi, tekshiruvni bloklash kerak bo'ladi
    commissioner_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "komissar"),
        None
    )

    players = [
        p for p in active_game["players"]
        if p["id"] != mashuqa_id
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"mashuqa_visit:{p['id']}")] for p in players
        ]
    )

    await bot.send_message(
        mashuqa_id,
        "💃 <b>Bugun kim bilan tun o‘tkazasiz?</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
