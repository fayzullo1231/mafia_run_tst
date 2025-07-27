from aiogram import Bot
import random
from models.game_state import active_game, ROLE_NAMES_UZ


async def kamikadze_hanged(bot: Bot, bot_chat_id):
    kamikadze_id = next(
        (p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "kamikadze"),
        None
    )

    if not kamikadze_id:
        return  # Kamikadze yo'q bo'lsa

    kamikadze_player = next((p for p in active_game["players"] if p["id"] == kamikadze_id), None)
    if not kamikadze_player:
        return

    # Kamikadzeni osishdi, random bitta odamni o'zi bilan olib ketadi
    other_players = [p for p in active_game["players"] if p["id"] != kamikadze_id]
    if not other_players:
        return

    victim = random.choice(other_players)
    active_game["players"] = [p for p in active_game["players"] if p["id"] not in [kamikadze_id, victim["id"]]]
    active_game["assignments"].pop(kamikadze_id, None)
    active_game["assignments"].pop(victim["id"], None)

    await bot.send_message(
        bot_chat_id,
        f"💣 <b>{kamikadze_player['name']}</b> Kamikadze edi. Uni osishdi. "
        f"Lekin u o'zi bilan <b>{victim['name']}</b> ni ham olib ketdi.",
        parse_mode="HTML"
    )


async def kamikadze_shot(bot: Bot, bot_chat_id, shooter_id, kamikadze_id):
    # Ikkalasi ham o'ladi: Kamikadze ham, otgan ham
    kamikadze_player = next((p for p in active_game["players"] if p["id"] == kamikadze_id), None)
    shooter_player = next((p for p in active_game["players"] if p["id"] == shooter_id), None)

    if kamikadze_player and shooter_player:
        active_game["players"] = [p for p in active_game["players"] if p["id"] not in [kamikadze_id, shooter_id]]
        active_game["assignments"].pop(kamikadze_id, None)
        active_game["assignments"].pop(shooter_id, None)

        await bot.send_message(
            bot_chat_id,
            f"💣 {kamikadze_player['name']} Kamikadze edi. "
            f"Unga o'q uzgan {shooter_player['name']} ham Kamikadze bilan birga halok bo‘ldi.",
            parse_mode="HTML"
        )
