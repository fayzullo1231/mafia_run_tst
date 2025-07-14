from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game


router = Router()


@router.callback_query(F.data.startswith("doctor_save:"))
async def handle_doctor_save(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = int(callback.data.split(":")[1])

    doctor_id = next((k for k, v in active_game["assignments"].items() if v == "shifokor"), None)

    if user_id != doctor_id:
        await callback.answer("❗ Bu faqat Shifokor uchun!", show_alert=True)
        return

    active_game["doctor_target"] = data
    target_name = next((p["name"] for p in active_game["players"] if p["id"] == data), "Nomaʼlum")

    await callback.message.edit_text(f"💊 Davolash tanlandi: {target_name}")
    await callback.answer("✅ Davolash tanlandi.")


# BU FUNKSIYANI SEN start_night() da chaqirasan
async def doctor_action(bot: Bot):
    doctor_id = next((k for k, v in active_game["assignments"].items() if v == "shifokor"), None)
    players = active_game["players"]

    if not doctor_id:
        return  # Shifokor yo'q bo'lsa hech nima qilmaydi.

    doctor_buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"doctor_save:{p['id']}")]
        for p in players
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=doctor_buttons)

    await bot.send_message(
        doctor_id,
        "💉 Kimni davolaysiz? O‘zini faqat bir marta davolay oladi.",
        reply_markup=markup
    )
