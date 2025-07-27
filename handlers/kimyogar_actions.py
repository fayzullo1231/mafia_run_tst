from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Router, F
from models.game_state import active_game, ROLE_NAMES_UZ

router = Router()

async def kimyogar_action(bot: Bot):
    kimyogar_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "kimyogar"),
        None
    )

    if not kimyogar_id:
        return

    candidates = [p for p in active_game["players"] if p["id"] != kimyogar_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"kimyogar_eliksir:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        kimyogar_id,
        "🧪 Kimyogar! Kimga eliksir berasiz? Faqat bitta odamni tanlang:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("kimyogar_eliksir:"))
async def handle_kimyogar_eliksir(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    kimyogar_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "kimyogar"),
        None
    )

    if user_id != kimyogar_id:
        await callback.answer("❗ Bu faqat Kimyogar uchun!", show_alert=True)
        return

    target_role = active_game["assignments"].get(target_id, "nomaʼlum")
    active_game["kimyogar_target"] = target_id
    active_game["kimyogar_target_mafiya"] = (target_role in ["don", "mafiya"])

    target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

    await bot.send_message(
        user_id,
        f"🧪 Siz {target_name} ga eliksir berdingiz.",
        parse_mode="HTML"
    )
    await callback.message.edit_text(f"✅ Tanlandi: {target_name}")
    await callback.answer("✅ Eliksir berildi.")
