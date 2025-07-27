from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game
from handlers.kamikade_action import kamikadze_shot

router = Router()


@router.callback_query(F.data.startswith("mafia_kill:"))
async def handle_mafia_kill(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = callback.data.split(":")[1]

    don_id = next(k for k, v in active_game["assignments"].items() if v == "don")

    if user_id != don_id:
        await callback.answer("❗ Bu faqat Don uchun!", show_alert=True)
        return

    if data == "skip":
        active_game["mafia_target"] = None
        await callback.message.edit_text("❌ Hech kim o‘ldirilmaydi.")
    else:
        target_id = int(data)
        active_game["mafia_target"] = target_id
        target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

        # KAMIKADZE TEKSHIRUV
        if active_game["assignments"].get(target_id) == "kamikadze":
            await kamikadze_shot(bot, active_game["chat_id"], shooter_id=don_id, kamikadze_id=target_id)
            # Kamikadze va Don o'lganidan keyin mafia_target ni o'chirib tashlaymiz
            active_game["mafia_target"] = None
            await callback.message.edit_text(f"💣 Kamikadze: {target_name} ni urishga urinildi. Ikkalasi ham halok.")
        else:
            await callback.message.edit_text(f"☠️ Tanlangan nishon: {target_name}")

    await callback.answer("✅ Tanlandi.")


# night_cycle ichida chaqiriladigan funksiya
async def mafia_action(bot: Bot):
    don_id = next((k for k, v in active_game["assignments"].items() if v == "don"), None)
    players = active_game["players"]

    if not don_id:
        return  # Don bo'lmasa, hech nima qilmaydi.

    mafia_target_buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"mafia_kill:{p['id']}")]
        for p in players if p["id"] != don_id
    ]
    mafia_target_buttons.append(
        [InlineKeyboardButton(text="❌ Hech kim", callback_data="mafia_kill:skip")]
    )

    markup = InlineKeyboardMarkup(inline_keyboard=mafia_target_buttons)

    await bot.send_message(
        don_id,
        "☠️ Kimni o‘ldirasiz? Tanlang:",
        reply_markup=markup
    )
