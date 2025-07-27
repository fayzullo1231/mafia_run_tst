from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from models.game_state import active_game

router = Router()

@router.callback_query(F.data.startswith("wife_protect:"))
async def handle_wife_protect(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    wife_id = next((p["id"] for p in active_game["players"]
                    if active_game["assignments"].get(p["id"]) == "donxotini"), None)

    if user_id != wife_id:
        await callback.answer("❗ Bu faqat Donning xotini uchun!", show_alert=True)
        return

    target_id = callback.data.split(":")[1]

    if target_id == "skip":
        active_game["wife_protect"] = None
        await callback.message.edit_text("❌ Siz hech kimni himoya qilmaysiz.")
    else:
        active_game["wife_protect"] = int(target_id)
        target_player = next((p for p in active_game["players"] if p["id"] == int(target_id)), None)
        await callback.message.edit_text(f"🛡 Siz <b>{target_player['name']}</b> ni himoya qilishga qaror qildingiz.", parse_mode="HTML")
