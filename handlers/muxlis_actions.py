from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from models.game_state import active_game

router = Router()

async def muxlis_action(bot: Bot):
    muxlis_id = next((p["id"] for p in active_game["players"]
                      if active_game["assignments"].get(p["id"]) == "muxlis"), None)
    if not muxlis_id or "muxlis_killer" in active_game:
        return  # Agar allaqachon qotilga aylangan bo‘lsa — harakat yo‘q

    candidates = [p for p in active_game["players"] if p["id"] != muxlis_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"muxlis_select:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        muxlis_id,
        "🔮 Siz kimni himoya qilishni yoki kuzatishni tanlaysiz?\nU o‘lsa — siz qotilga aylanasiz!",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("muxlis_select:"))
async def handle_muxlis_select(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    muxlis_id = next((p["id"] for p in active_game["players"]
                      if active_game["assignments"].get(p["id"]) == "muxlis"), None)

    if user_id != muxlis_id:
        await callback.answer("❗ Bu faqat Muxlis uchun!", show_alert=True)
        return

    active_game["muxlis_target"] = target_id
    target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

    await callback.message.edit_text(f"🔮 Siz {target_name} ni himoya qilishga qaror qildingiz. U o‘lsa — siz qasos olasiz!")
    await callback.answer("✅ Tanlov saqlandi.")
