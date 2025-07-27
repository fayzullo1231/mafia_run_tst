from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from models.game_state import active_game

router = Router()

async def mergan_action(bot: Bot):
    mergan_id = next((p["id"] for p in active_game["players"]
                      if active_game["assignments"].get(p["id"]) == "mergan"), None)
    if not mergan_id:
        return

    candidates = [p for p in active_game["players"] if p["id"] != mergan_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"mergan_kill:{p['id']}")]
            for p in candidates
        ] + [[InlineKeyboardButton(text="❌ O‘q uzilmaydi", callback_data="mergan_kill:skip")]]
    )

    await bot.send_message(
        mergan_id,
        "🎯 Kimga qarata o‘q uzasiz? Daydi ham bu harakatni seza olmaydi, himoya ham to‘xtata olmaydi.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("mergan_kill:"))
async def handle_mergan_kill(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_str = callback.data.split(":")[1]

    mergan_id = next((p["id"] for p in active_game["players"]
                      if active_game["assignments"].get(p["id"]) == "mergan"), None)

    if user_id != mergan_id:
        await callback.answer("❗ Bu faqat Mergan uchun!", show_alert=True)
        return

    if target_str == "skip":
        active_game["mergan_target"] = None
        await callback.message.edit_text("❌ Bu tun mergan o‘q uzmadi.")
    else:
        target_id = int(target_str)
        active_game["mergan_target"] = target_id
        target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")
        await callback.message.edit_text(f"🎯 Siz o‘q uzdingiz: {target_name}")

    await callback.answer("✅ Tanlov qabul qilindi.")
