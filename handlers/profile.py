# handlers/profile.py
from aiogram import Router
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(lambda c: c.data == "profile")
async def show_profile(cb):
    # foydalanuvchi profilini ko'rsatish
    await cb.answer("Profil: ...")
