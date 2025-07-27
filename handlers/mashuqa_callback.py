from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from models.game_state import active_game

router = Router()

@router.callback_query(F.data.startswith("mashuqa_visit:"))
async def handle_mashuqa_visit(callback: CallbackQuery, bot: Bot):
    mashuqa_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    # Faqat mashuqa bosishi kerak
    if active_game["assignments"].get(mashuqa_id) != "mashuqa":
        await callback.answer("⛔ Bu faqat Mashuqa uchun!", show_alert=True)
        return

    active_game["mashuqa_target"] = target_id
    await callback.message.edit_text("✅ Tun sherigingiz tanlandi.")

    # Agar bu komissar bo‘lsa, bloklash uchun flag o‘rnatamiz
    commissioner_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "komissar"),
        None
    )

    if target_id == commissioner_id:
        active_game["commissioner_blocked"] = True
    else:
        active_game["commissioner_blocked"] = False
