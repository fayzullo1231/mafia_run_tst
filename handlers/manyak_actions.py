from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game, ROLE_NAMES_UZ

router = Router()


@router.callback_query(F.data.startswith("manyak_kill:"))
async def handle_manyak_kill(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = callback.data.split(":")[1]

    manyak_id = next((k for k, v in active_game["assignments"].items() if v == "manyak"), None)

    if user_id != manyak_id:
        await callback.answer("❗ Bu faqat Manyak uchun!", show_alert=True)
        return

    if data == "skip":
        active_game["manyak_target"] = None
        await callback.message.edit_text("❌ Manyak bu tun hech kimni o‘ldirmaydi.")
    else:
        target_id = int(data)
        active_game["manyak_target"] = target_id
        target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")
        await callback.message.edit_text(f"🔪 Manyak o‘z nishonini tanladi: {target_name}")

    await callback.answer("✅ Tanlandi.")


async def manyak_action(bot: Bot):
    manyak_id = next((k for k, v in active_game["assignments"].items() if v == "manyak"), None)
    players = active_game["players"]

    if not manyak_id:
        return

    buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"manyak_kill:{p['id']}")]
        for p in players if p["id"] != manyak_id
    ]
    buttons.append(
        [InlineKeyboardButton(text="❌ Hech kim", callback_data="manyak_kill:skip")]
    )

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(
        manyak_id,
        "🔪 Siz kimni o‘ldirmoqchisiz? Faqat bir kishini tanlang yoki 'Hech kim' tugmasini bosing.",
        reply_markup=markup
    )


async def notify_manyak_result(bot: Bot):
    chat_id = active_game["chat_id"]
    manyak_target = active_game.get("manyak_target")

    if manyak_target:
        killed_player = next((p for p in active_game["players"] if p["id"] == manyak_target), None)
        if killed_player:
            role = active_game["assignments"].get(manyak_target, 'nomaʼlum')
            role_name = ROLE_NAMES_UZ.get(role, "Nomaʼlum")

            active_game["players"] = [p for p in active_game["players"] if p["id"] != manyak_target]
            active_game["assignments"].pop(manyak_target, None)

            await bot.send_message(
                chat_id,
                f"Tunda {role_name} <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> Manyak tomonidan o‘ldirilgan.",
                parse_mode="HTML"
            )
