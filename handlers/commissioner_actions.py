from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game, ROLE_NAMES_UZ
from handlers.advokat_actions import get_commissioner_check_result  # ✅ ADVOKAT mantiqini chaqirish

router = Router()

@router.callback_query(F.data.startswith("commissioner_check:"))
async def handle_commissioner_check(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = int(callback.data.split(":")[1])

    commissioner_id = next(
        (k for k, v in active_game["assignments"].items() if v == "komissar"), None
    )

    if user_id != commissioner_id:
        await callback.answer("❗ Bu faqat Komissar uchun!", show_alert=True)
        return

    # ✅ MAJNUN redirect logikasi shu yerga
    if active_game.get("layli_for_redirect") == data:
        data = active_game.get("majnun_redirect_to")

    active_game["commissioner_check"] = data

    # ✅ ADVOKAT mantiqini ishlatamiz
    role_checked = get_commissioner_check_result(data)
    role_name = ROLE_NAMES_UZ.get(role_checked, "Nomaʼlum")

    target_name = next(
        (p["name"] for p in active_game["players"] if p["id"] == data),
        "Nomaʼlum"
    )

    text = f"🔍 {target_name} roli: <b>{role_name}</b>"

    await bot.send_message(user_id, text, parse_mode="HTML")
    await callback.message.edit_text(f"🔎 Tekshirildi: {target_name}")
    await callback.answer("✅ Tekshirildi.")


async def commissioner_action(bot: Bot):
    commissioner_id = next(
        (k for k, v in active_game["assignments"].items() if v == "komissar"),
        None
    )

    if not commissioner_id:
        return  # Komissar yo‘q

    if active_game.get("commissioner_blocked"):
        # 💬 Komissar uxlab qoldi - xabar foydalanuvchiga
        await bot.send_message(
            commissioner_id,
            "😴 Siz Mashuqa bilan tun o‘tkazdingiz va chuqur uyquga ketdingiz.\n"
            "Bu tun hech kimni tekshira olmaysiz.",
            parse_mode="HTML"
        )

        # 💬 Guruhga xabar
        chat_id = active_game["chat_id"]
        await bot.send_message(
            chat_id,
            "💤 <b>Komissar bu tun charchagan ko‘rinadi...</b>\n"
            "Aytishlaricha u mashuqa bilan tun bo‘yi birga bo‘lgan ekan.\n",
            parse_mode="HTML"
        )
        return

    players = active_game["players"]
    commissioner_buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"commissioner_check:{p['id']}")]
        for p in players if p["id"] != commissioner_id
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=commissioner_buttons)

    await bot.send_message(
        commissioner_id,
        "🔍 Kimni tekshirasiz? Faqat bir odamni tanlang.",
        reply_markup=markup
    )