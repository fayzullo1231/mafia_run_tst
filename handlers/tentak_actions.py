from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from models.game_state import active_game

router = Router()


# Tentakka xabar yuborib, tanlash imkonini berish
async def tentak_action(bot: Bot):
    tentak_id = next((p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "tentak"), None)
    if not tentak_id:
        return

    players = [p for p in active_game["players"] if p["id"] != tentak_id]

    buttons = [
        [InlineKeyboardButton(text=p["name"], callback_data=f"tentak_target:{p['id']}")]
        for p in players
    ]
    buttons.append([InlineKeyboardButton(text="❌ Hech kim", callback_data="tentak_target:skip")])

    await bot.send_message(
        chat_id=tentak_id,
        text="👨🏻‍🦲 Qaysi odamga kechasi bosh urasiz? Agar u odamga mafiya hujum qilsa, Donni urib o'ldirasiz.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


# Tentak tugma bosganda callback qabul qiladigan funksiya
@router.callback_query(F.data.startswith("tentak_target:"))
async def handle_tentak_target(callback: CallbackQuery):
    data = callback.data.split(":")[1]
    if data == "skip":
        active_game["tentak_target"] = None
        await callback.message.answer("❌ Siz hech kimni tanlamadingiz.")
    else:
        active_game["tentak_target"] = int(data)
        player = next((p for p in active_game["players"] if str(p["id"]) == data), None)
        name = player["name"] if player else "nomaʼlum"
        await callback.message.answer(f"✅ Siz {name} ga bosh urishga tayyormiz!")

    await callback.answer()
