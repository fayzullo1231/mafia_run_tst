from aiogram import Bot
from models.game_state import active_game
from utils.role_summary import generate_role_summary
from models.game_state import ROLE_NAMES_UZ

# Ushbu funksiya har safar ovoz berish yakunida osilgan odamni tekshirish uchun ishlatiladi
async def check_suicider_hanging(hanged_id: int, bot: Bot):
    # Agar osilgan odam suidsid bo‘lsa
    if active_game["assignments"].get(hanged_id) == "suicider":
        player = next((p for p in active_game["players"] if p["id"] == hanged_id), None)
        if player:
            chat_id = active_game["chat_id"]
            # O‘yinni yakunlash
            active_game["is_active"] = False
            active_game["players"] = []
            active_game["assignments"] = {}

            # Suidsid g‘alabasi haqida guruhga xabar
            text = (
                f"🧌 <b>{player['name']}</b> oddiy fuqaro ko‘rinishida yashiringan edi.\n"
                "Adashib uni osib qo‘yishdi... ammo bu aynan uning rejasi edi!\n\n"
                "🎉 <b>O‘yin yakunlandi!</b>\n"
                "🏆 G‘olib: <b>Suidsid</b> — boshqa hammangiz yutqazdingiz."
            )

            await bot.send_message(chat_id, text, parse_mode="HTML")
            return True  # O‘yin to‘xtadi

    return False  # O‘yin davom etadi
