from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game, ROLE_NAMES_UZ

router = Router()


@router.callback_query(F.data.startswith("commissioner_check:"))
async def handle_commissioner_check(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = int(callback.data.split(":")[1])

    commissioner_id = next((k for k, v in active_game["assignments"].items() if v == "komissar"), None)

    if user_id != commissioner_id:
        await callback.answer("❗ Bu faqat Komissar uchun!", show_alert=True)
        return

    active_game["commissioner_check"] = data
    role_checked = active_game["assignments"].get(data, "nomaʼlum")
    role_name = ROLE_NAMES_UZ.get(role_checked, "Nomaʼlum")

    target_name = next((p["name"] for p in active_game["players"] if p["id"] == data), "Nomaʼlum")

    text = f"🔍 {target_name} roli: <b>{role_name}</b>"
    await bot.send_message(user_id, text, parse_mode="HTML")

    await callback.message.edit_text(f"🔎 Tekshirildi: {target_name}")
    await callback.answer("✅ Tekshirildi.")


# SEN night_cycle.py da chaqiradigan COMMISSAR FUNKSIYASI
async def commissioner_action(bot: Bot):
    commissioner_id = next((k for k, v in active_game["assignments"].items() if v == "komissar"), None)
    players = active_game["players"]

    if not commissioner_id:
        return  # Komissar yo'q bo'lsa hech nima qilmaydi.

    commissioner_buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"commissioner_check:{p['id']}")]
        for p in players if p["id"] != commissioner_id  # Komissarning o'zi chiqarilmaydi
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=commissioner_buttons)

    await bot.send_message(
        commissioner_id,
        "🔍 Kimni tekshirasiz? Faqat bir odamni tanlang.",
        reply_markup=markup
    )
