from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from models.game_state import active_game, ROLE_NAMES_UZ

router = Router()

@router.callback_query(F.data.startswith("donxotini_check:"))
async def handle_donxotini_check(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = int(callback.data.split(":")[1])

    # Donning xotini ID
    don_xotini_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "don_xotini"),
        None
    )

    if user_id != don_xotini_id:
        await callback.answer("❗ Bu faqat Donning xotiniga tegishli!", show_alert=True)
        return

    # Raqamdan rolni olish
    checked_role = active_game["assignments"].get(data, "nomaʼlum")
    role_name = ROLE_NAMES_UZ.get(checked_role, "Nomaʼlum")

    checked_name = next((p["name"] for p in active_game["players"] if p["id"] == data), "Nomaʼlum")

    # Donning xotiniga xabar
    await bot.send_message(
        user_id,
        f"🔍 {checked_name} roli: <b>{role_name}</b>",
        parse_mode="HTML"
    )

    # Don va mafiya a’zolariga xabar
    for player in active_game["players"]:
        pid = player["id"]
        role = active_game["assignments"].get(pid)
        if role in ["don", "mafiya"] and pid != user_id:
            try:
                await bot.send_message(
                    pid,
                    f"🧠 Donning xotini {checked_name} roli haqida ma’lumot berdi:\n"
                    f"🔍 {checked_name} — <b>{role_name}</b>",
                    parse_mode="HTML"
                )
            except:
                continue

    await callback.message.edit_text(f"🔎 Tekshirildi: {checked_name}")
    await callback.answer("✅ Ma’lumot yuborildi.")
