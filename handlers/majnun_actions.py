from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from models.game_state import active_game

router = Router()

async def majnun_action(bot: Bot):
    majnun_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "majnun"),
        None
    )
    if not majnun_id:
        return

    candidates = [p for p in active_game["players"] if p["id"] != majnun_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"majnun_layli:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        majnun_id,
        "🕺🏻 Kimni Layli sifatida tanlaysiz? Uning harakatlari sizga o‘tadi.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("majnun_layli:"))
async def handle_majnun_layli(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    majnun_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "majnun"),
        None
    )

    if user_id != majnun_id:
        await callback.answer("❗ Bu faqat Majnun uchun!", show_alert=True)
        return

    active_game["majnun_layli"] = target_id
    target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

    await bot.send_message(
        user_id,
        f"🕺🏻 Siz {target_name} ni Layli sifatida tanladingiz. Uning harakatlari sizga o‘tadi.",
        parse_mode="HTML"
    )
    await callback.message.edit_text(f"✅ Tanlandi: {target_name}")
    await callback.answer("✅ Tanlov qabul qilindi.")
