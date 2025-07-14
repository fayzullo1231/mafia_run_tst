from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game

router = Router()


@router.callback_query(F.data.startswith("daydi_watch:"))
async def handle_daydi_watch(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = int(callback.data.split(":")[1])

    daydi_id = next((k for k, v in active_game["assignments"].items() if v == "daydi"), None)

    if user_id != daydi_id:
        await callback.answer("❗ Bu faqat Daydi uchun!", show_alert=True)
        return

    active_game["daydi_target"] = data
    target_name = next((p["name"] for p in active_game["players"] if p["id"] == data), "Nomaʼlum")

    await callback.message.edit_text(f"👀 Siz tunda {target_name} uyini kuzatishga qaror qildingiz.")
    await callback.answer("✅ Tanlandi.")


async def daydi_action(bot: Bot):
    daydi_id = next((k for k, v in active_game["assignments"].items() if v == "daydi"), None)
    players = active_game["players"]

    if not daydi_id:
        return  # Daydi o'yinchi bo'lmasa, chiqib ketamiz

    # O'zini tanlay olmasin
    buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"daydi_watch:{p['id']}")]
        for p in players if p["id"] != daydi_id
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(
        daydi_id,
        "🧙🏼‍♂️ Siz tunda kimni kuzatmoqchisiz? Faqat bitta odamni tanlang.",
        reply_markup=markup
    )


async def notify_daydi(bot: Bot):
    daydi_id = next((k for k, v in active_game["assignments"].items() if v == "daydi"), None)
    target_id = active_game.get("daydi_target")
    mafia_target = active_game.get("mafia_target")

    if not daydi_id:
        return

    if not target_id:
        await bot.send_message(daydi_id, "👀 Siz bu tun hech kimni kuzatmadingiz.")
        return

    target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

    if mafia_target == target_id:
        await bot.send_message(
            daydi_id,
            f"👀 Siz tunda <b>{target_name}</b> uyida edingiz va u yerga qotil keldi.",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            daydi_id,
            f"👀 Siz tunda <b>{target_name}</b> uyida edingiz. Hech qanday shubhali holat ko‘rmadingiz.",
            parse_mode="HTML"
        )
