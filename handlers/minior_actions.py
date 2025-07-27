from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game

router = Router()

async def minior_action(bot: Bot):
    minior_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "minior"),
        None
    )
    if not minior_id:
        return

    candidates = [p for p in active_game["players"] if p["id"] != minior_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"minior_mine:{p['id']}")]
            for p in candidates
        ] + [[InlineKeyboardButton(text="❌ Hech kimga mina qo‘ymaslik", callback_data="minior_mine:skip")]]
    )

    await bot.send_message(
        minior_id,
        "☠️ Kimning uyiga mina qo‘ymoqchisiz?",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("minior_mine:"))
async def handle_minior_mine(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_data = callback.data.split(":")[1]

    minior_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "minior"),
        None
    )

    if user_id != minior_id:
        await callback.answer("❗ Bu faqat Minior uchun!", show_alert=True)
        return

    if target_data == "skip":
        active_game["minior_target"] = None
        await callback.message.edit_text("❌ Bu tun Minior mina qo‘ymadi.")
    else:
        target_id = int(target_data)
        active_game["minior_target"] = target_id
        target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")
        await callback.message.edit_text(f"☠️ Mina {target_name} uyiga qo‘yildi.")

    await callback.answer("✅ Tanlov saqlandi.")
