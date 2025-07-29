from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game
from handlers.kamikade_action import kamikadze_shot

router = Router()


@router.callback_query(F.data.startswith("mafia_kill:"))
async def handle_mafia_kill(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = callback.data.split(":")[1]

    mafia_roles = ["don", "mafiya"]
    mafia_ids = [
        pid for pid, role in active_game["assignments"].items()
        if role in mafia_roles
    ]

    if user_id not in mafia_ids:
        await callback.answer("❗ Bu faqat mafiyalar uchun!", show_alert=True)
        return

    # Allaqachon tanlangan bo‘lsa, boshqa mafiyalar tanlay olmasin
    if "mafia_target" in active_game and active_game["mafia_target"] is not None:
        await callback.answer("⚠️ Tanlov allaqachon bajarilgan.", show_alert=True)
        return

    if data == "skip":
        active_game["mafia_target"] = None
        await callback.message.edit_text("❌ Hech kim o‘ldirilmaydi.")
    else:
        target_id = int(data)
        active_game["mafia_target"] = target_id
        target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

        # Kamikadze tekshiruv
        if active_game["assignments"].get(target_id) == "kamikadze":
            from handlers.kamikade_action import kamikadze_shot
            await kamikadze_shot(bot, active_game["chat_id"], shooter_id=user_id, kamikadze_id=target_id)
            active_game["mafia_target"] = None
            await callback.message.edit_text(f"💣 Kamikadze: {target_name} ni urishga urinildi. Ikkalasi ham halok.")
        else:
            await callback.message.edit_text(f"☠️ Tanlangan nishon: {target_name}")

    await callback.answer("✅ Tanlov bajarildi.")

async def mafia_action(bot: Bot):
    mafia_roles = ["don", "mafiya"]
    players = active_game["players"]

    mafia_ids = [
        pid for pid, role in active_game["assignments"].items()
        if role in mafia_roles
    ]

    # Nishonlar (mafiya bo'lmaganlar)
    target_buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"mafia_kill:{p['id']}")]
        for p in players if active_game["assignments"].get(p["id"]) not in mafia_roles
    ]
    target_buttons.append(
        [InlineKeyboardButton(text="❌ Hech kim", callback_data="mafia_kill:skip")]
    )
    markup = InlineKeyboardMarkup(inline_keyboard=target_buttons)

    for mafia_id in mafia_ids:
        await bot.send_message(
            mafia_id,
            "☠️ Kimni o‘ldirasiz? Tanlang:",
            reply_markup=markup
        )
