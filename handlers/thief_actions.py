from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from models.game_state import active_game

router = Router()

async def thief_action(bot: Bot):
    thief_id = next((p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "ogr"), None)
    if not thief_id:
        return

    candidates = [p for p in active_game["players"] if p["id"] != thief_id]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"thief_steal:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        thief_id,
        "🥷🏻 Kimning rolini o‘g‘irlaysiz? Agar u aktiv rol bo‘lsa, sizga o‘tadi. U esa Tentak bo‘ladi.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("thief_steal:"))
async def handle_thief_steal(callback: CallbackQuery, bot: Bot):
    thief_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    thief_real_id = next((p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "ogr"), None)
    if thief_id != thief_real_id:
        await callback.answer("❗ Bu faqat O‘g‘ri uchun!", show_alert=True)
        return

    target_role = active_game["assignments"].get(target_id)
    active_roles = ["shifokor", "komissar", "serjant", "don", "mafiya", "daydi", "manyak", "kimyogar", "sotuvchi", "mashuqa", "wife", "teacher"]

    if target_role in active_roles:
        active_game["assignments"][thief_id] = target_role
        active_game["assignments"][target_id] = "tentak"
        await bot.send_message(
            thief_id,
            f"🥷 Siz muvaffaqiyatli <b>{target_role}</b> rolini o‘g‘irladingiz!",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            thief_id,
            "❌ Bu odamda aktiv rol yo‘q edi. Hech narsa o‘zgarmadi.",
            parse_mode="HTML"
        )

    await callback.message.edit_text("✅ Tanlov qabul qilindi.")
    await callback.answer("✅ Tanlov qabul qilindi.")
