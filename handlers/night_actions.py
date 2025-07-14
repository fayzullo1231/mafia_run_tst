from aiogram import Bot, Router
from models.game_state import active_game

router = Router()

# Harakatlar vaqtinchalik saqlanadi
actions = {
    "mafiya": None,       # O'ldiriladigan odam IDsi
    "shifokor": None,     # Saqlanadigan odam IDsi
    "komissar": None,     # Tekshiriladigan odam IDsi
    "daydi": None,        # Kuzatiladigan odam IDsi
    "don": None           # Don tanlovi (agar Don bo'lsa, ustunlik beradi)
}


async def run_night_phase(bot: Bot):
    """
    Tun bosqichi harakatlari: har bir rolga mos xabar yuboriladi.
    """
    players = active_game["players"]
    assignments = active_game["assignments"]

    for player in players:
        uid = player["id"]
        role = assignments.get(uid)

        if role == "don":
            await bot.send_message(uid, "🔪 Don! Qaysi o‘yinchini o‘ldirmoqchisiz?\n/kill [id]")

        elif role == "mafiya":
            await bot.send_message(uid, "🤵 Mafiya! Don topshirig‘iga binoan o‘ldirishingiz mumkin. /kill [id]")

        elif role == "shifokor":
            await bot.send_message(uid, "🩺 Shifokor! Kimni davolaysiz? /heal [id]\nEslatma: O‘zingizni faqat 1 marta davolashingiz mumkin.")

        elif role == "komissar":
            await bot.send_message(uid, "🕵🏻‍♂ Komissar! Kimni tekshirasiz? /check [id]")

        elif role == "daydi":
            await bot.send_message(uid, "🧙🏼‍♂️ Daydi! Kimning uyida tunaysiz? /sleep [id]")


# Quyidagi funksiyalar boshqa fayl (masalan, handlers/night_commands.py) dan ishlatiladi
def get_user_name(uid: int):
    return next((p["name"] for p in active_game["players"] if p["id"] == uid), "")


async def handle_kill(uid: int, target_id: int):
    role = active_game["assignments"].get(uid)
    if role == "don":
        actions["don"] = target_id
    elif role == "mafiya":
        actions["mafiya"] = target_id


async def handle_heal(uid: int, target_id: int):
    # TODO: shifokor o'zini necha marta davolaganini hisobga olish kerak
    actions["shifokor"] = target_id


async def handle_check(uid: int, target_id: int):
    actions["komissar"] = target_id


async def handle_sleep(uid: int, target_id: int):
    actions["daydi"] = target_id


async def process_night_results(bot: Bot, chat_id: int):
    killed = actions["don"] or actions["mafiya"]
    healed = actions["shifokor"]

    # Shifokor davolaganmi?
    if killed and killed == healed:
        await bot.send_message(chat_id, "✅ Hech kim o‘lmadi. Shifokor uni qutqardi!")
    elif killed:
        player_name = get_user_name(killed)
        await bot.send_message(chat_id, f"💀 <b>{player_name}</b> o‘ldirildi!", parse_mode="HTML")

        # O'yindan chiqarish
        active_game["players"] = [p for p in active_game["players"] if p["id"] != killed]
        del active_game["assignments"][killed]

    # Komissar uchun tekshiruv natijasi
    check_target = actions["komissar"]
    if check_target:
        role = active_game["assignments"].get(check_target, "")
        is_mafia = role in ["mafiya", "don", "advokat"]
        for player in active_game["players"]:
            if active_game["assignments"].get(player["id"]) == "komissar":
                result = "❗U mafiya!" if is_mafia else "✅ Tinch aholi."
                await bot.send_message(player["id"], f"Tekshiruv natijasi: {result}")

    # Daydi kuzatuvi (logikasi to‘liq emas)
    sleep_target = actions["daydi"]
    if sleep_target:
        visitors = [k for k, v in actions.items() if v == sleep_target and k != "daydi"]
        if visitors:
            visitor_text = " va ".join(visitors)
            for player in active_game["players"]:
                if active_game["assignments"].get(player["id"]) == "daydi":
                    await bot.send_message(player["id"], f"🔍 Siz tunagan joyga quyidagilar kelgan: {visitor_text}")

    # Harakatlarni tozalash
    for key in actions:
        actions[key] = None
