from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game, ROLE_NAMES_UZ

router = Router()


async def serjant_action(bot: Bot):
    chat_id = active_game["chat_id"]

    # Komissar bor-yo'qligini aniqlaymiz (id bo'yicha)
    commissioner_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "komissar"),
        None
    )

    commissioner_alive = commissioner_id in [p["id"] for p in active_game["players"]]

    if commissioner_alive:
        return  # Komissar tirik bo'lsa, Serjant hech narsa qilmaydi

    # Serjantni topamiz
    serjant_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "serjant"),
        None
    )

    if not serjant_id:
        return

    # Serjantga inline tugma yuboramiz
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Komissar vazifasini qabul qilaman", callback_data="serjant_accept")]
        ]
    )

    await bot.send_message(
        serjant_id,
        "👮‍♂ Komissar vafot etdi. Siz uning o'rniga vazifani qabul qilasizmi?",
        reply_markup=markup
    )


@router.callback_query(F.data == "serjant_accept")
async def handle_serjant_accept(callback: CallbackQuery, bot: Bot):
    serjant_id = callback.from_user.id
    chat_id = active_game["chat_id"]

    active_game["assignments"][serjant_id] = "komissar"

    await callback.message.edit_text("✅ Siz endi Komissar bo‘ldingiz!")
    await bot.send_message(
        chat_id,
        f"👮‍♂ <b>{callback.from_user.first_name}</b> endi Komissar vazifasini davom ettiradi.",
        parse_mode="HTML"
    )
