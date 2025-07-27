from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from models.game_state import active_game

router = Router()

async def buqalamun_action(bot: Bot):
    buqalamun_id = next((p["id"] for p in active_game["players"]
                         if active_game["assignments"].get(p["id"]) == "buqalamun"), None)
    if not buqalamun_id:
        return

    candidates = [p for p in active_game["players"] if p["id"] != buqalamun_id]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["name"], callback_data=f"buqalamun_target:{p['id']}")]
            for p in candidates
        ]
    )

    await bot.send_message(
        buqalamun_id,
        "🦎 Kimning tarafini olasiz? Siz o‘sha odamga o‘xshab qolasiz.",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("buqalamun_target:"))
async def handle_buqalamun_target(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    buqalamun_id = next((p["id"] for p in active_game["players"]
                         if active_game["assignments"].get(p["id"]) == "buqalamun"), None)

    if user_id != buqalamun_id:
        await callback.answer("❗ Bu faqat Buqalamun uchun!", show_alert=True)
        return

    target_role = active_game["assignments"].get(target_id)

    if target_role in ["don", "mafiya", "jinoyatchi"]:
        new_role = "mafiya"
    elif target_role in ["shifokor", "serjant", "komissar", "daydi"]:
        new_role = "serjant"
    elif target_role in ["manyak", "tentak", "yakka", "afifist", "majnun"]:
        new_role = "manyak"
    else:
        new_role = "serjant"

    active_game["assignments"][buqalamun_id] = new_role

    target_name = next((p["name"] for p in active_game["players"] if p["id"] == target_id), "Nomaʼlum")

    await bot.send_message(
        user_id,
        f"🦎 Siz {target_name} ning roliga moslashdingiz. Endi siz <b>{new_role.upper()}</b> sifatida o‘ynaysiz.",
        parse_mode="HTML"
    )
    await callback.message.edit_text(f"✅ Tanlangan: {target_name}")
    await callback.answer("✅ Raqib roli qabul qilindi.")
