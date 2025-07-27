from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game

async def teacher_action(bot: Bot):
    teacher_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "oqituvchi"),
        None
    )

    if not teacher_id:
        return

    if "teacher_training" not in active_game:
        active_game["teacher_training"] = {}  # {player_id: {"day": N}}

    already_training = active_game["teacher_training"].keys()

    candidates = [
        p for p in active_game["players"]
        if p["id"] != teacher_id and p["id"] not in already_training
    ]

    if not candidates:
        await bot.send_message(teacher_id, "📚 Hech kim qolmadi. Barcha o‘yinchilar allaqachon o‘qitilgan.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"teacher_teach:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        teacher_id,
        "👩🏻‍🏫 Bugun kimni o‘qitasiz? (2 kecha davomida o‘qitiladi, 3-kecha kuchli rolga aylanadi)",
        reply_markup=keyboard
    )
