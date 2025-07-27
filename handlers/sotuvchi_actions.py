from aiogram import Bot, Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from models.game_state import active_game, ROLE_NAMES_UZ

router = Router()

async def sotuvchi_action(bot: Bot):
    sotuvchi_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "sotuvchi"),
        None
    )

    if not sotuvchi_id:
        return

    candidates = [
        p for p in active_game["players"]
        if p["id"] != sotuvchi_id and active_game["assignments"].get(p["id"]) not in ["don", "mafiya"]
    ]

    if not candidates:
        return

    product_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"sotuvchi_sell:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        sotuvchi_id,
        "🎁 Kimga yordam bermoqchisiz? Rol/himoya/hujjat sotiladi:",
        reply_markup=product_keyboard
    )


@router.callback_query(F.data.startswith("sotuvchi_sell:"))
async def handle_sotuvchi_sell(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    sotuvchi_id = next(
        (p["id"] for p in active_game["players"]
         if active_game["assignments"].get(p["id"]) == "sotuvchi"),
        None
    )

    if user_id != sotuvchi_id:
        await callback.answer("❗ Bu faqat Sotuvchi uchun!", show_alert=True)
        return

    target_player = next((p for p in active_game["players"] if p["id"] == target_id), None)
    if not target_player:
        await callback.answer("❗ O'yinchi topilmadi!", show_alert=True)
        return

    active_game.setdefault("sotuvchi_protected", []).append(target_id)

    await bot.send_message(
        target_id,
        "🎁 Sizga sirli bir kishi (Sotuvchi) yordam ko‘rsatdi.\n"
        "Endi siz hujjatga egasiz va bir kechada osilmay qolishingiz mumkin!",
        parse_mode="HTML"
    )

    await callback.message.edit_text(f"✅ Tanlandi: {target_player['name']}")
    await callback.answer("✅ Yordam yuborildi.")
