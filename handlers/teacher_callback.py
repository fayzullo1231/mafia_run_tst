from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from models.game_state import active_game

router = Router()

@router.callback_query(F.data.startswith("teacher_teach:"))
async def handle_teacher_teach(callback: CallbackQuery, bot: Bot):
    teacher_id = callback.from_user.id
    target_id = int(callback.data.split(":")[1])

    if active_game["assignments"].get(teacher_id) != "oqituvchi":
        await callback.answer("⛔ Bu faqat O‘qituvchi uchun!", show_alert=True)
        return

    if "teacher_training" not in active_game:
        active_game["teacher_training"] = {}

    if target_id in active_game["teacher_training"]:
        await callback.answer("⛔ Bu o‘yinchi allaqachon o‘qitilmoqda.", show_alert=True)
        return

    active_game["teacher_training"][target_id] = {"day": active_game["day"]}

    target_name = next(
        (p["name"] for p in active_game["players"] if p["id"] == target_id),
        "Nomaʼlum"
    )

    await callback.message.edit_text(f"📘 Siz {target_name} ni o‘qitishni boshladingiz (2 tun).")
    await callback.answer("✅ O‘qitish boshlandi.")
