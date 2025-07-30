from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from asyncio import create_task, sleep
from datetime import datetime
import random

from models.game_state import active_game, ROLE_POOL, get_roles_for_player_count, ROLE_NAMES_UZ
from utils.role_summary import generate_role_summary
from handlers.night_cycle import start_night
from handlers.voting import start_voting

router = Router()


def reset_game_state():
    keys_to_keep = ["chat_id", "group_title"]
    for key in list(active_game.keys()):
        if key not in keys_to_keep:
            active_game[key] = None

    active_game["players"] = []
    active_game["assignments"] = {}
    active_game["is_active"] = False
    active_game["day"] = 1
    active_game["message_id"] = None


@router.message(Command("start_game"))
async def start_game(msg: Message, bot: Bot):
    try:
        await msg.delete()
    except:
        pass

    reset_game_state()  # <--- BU QATORNI ENG BOSHIYA QO‘SHING

    chat_id = msg.chat.id
    active_game["chat_id"] = chat_id
    active_game["group_title"] = msg.chat.title
    active_game["players"] = []
    active_game["assignments"] = {}
    active_game["is_active"] = False
    active_game["day"] = 1

    me = await bot.get_me()
    bot_username = me.username

    join_btn = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👤 Qo‘shilish", url=f"https://t.me/{bot_username}?start=join")
    ]])

    player_list = "\n".join([
        f"– <a href='tg://user?id={p['id']}'>{p['name']}</a>"
        for p in active_game["players"]
    ]) or "–"

    msg_sent = await bot.send_message(
        chat_id,
        f"✅ <b>Ro‘yxatdan o‘tish boshlandi.</b>\n\n"
        f"Ro‘yxatdan o‘tganlar:\n\n{player_list}\n\n"
        f"Jami: {len(active_game['players'])} ta\n\n"
        "⏳ 3 daqiqa ichida o‘yin avtomatik boshlanadi.\n"
        "Yoki 5+ o‘yinchi yig‘ilgach /start_game_now buyrug‘i bilan boshlang.",
        reply_markup=join_btn,
        parse_mode="HTML"
    )

    active_game["message_id"] = msg_sent.message_id
    create_task(wait_and_start(bot))


@router.message(Command("stop"))
async def stop_game(msg: Message, bot: Bot):
    if not active_game.get("is_active") and not active_game.get("players"):
        await msg.answer("❌ Hech qanday o‘yin faol emas.")
        return

    chat_id = active_game.get("chat_id", msg.chat.id)
    await bot.send_message(chat_id, "⛔ O‘yin to‘xtatildi. Barcha ma'lumotlar bekor qilindi.", parse_mode="HTML")
    reset_game_state()


@router.message(Command("start_game_now"))
async def start_game_now(msg: Message, bot: Bot):
    if active_game.get("is_active"):
        await msg.answer("⛔ O‘yin allaqachon boshlandi.")
        return
    if len(active_game["players"]) < 5:
        await msg.answer("❗ Kamida 5 o‘yinchi kerak.")
        return
    await start_game_now_logic(bot)


async def wait_and_start(bot: Bot):
    await sleep(180)
    if active_game.get("is_active"):
        return

    if len(active_game["players"]) >= 5:
        await start_game_now_logic(bot)
    else:
        chat_id = active_game.get("chat_id")
        await bot.send_message(chat_id, "⚠️ O‘yin boshlanmadi. Kamida 5 o‘yinchi kerak edi.", parse_mode="HTML")
        reset_game_state()


async def send_current_players(msg: Message, bot: Bot):
    player_list = "\n".join([
        f"– <a href='tg://user?id={p['id']}'>{p['name']}</a>"
        for p in active_game["players"]
    ]) or "–"
    await msg.answer(
        f"⛔ O‘yin hali boshlanmadi, ammo ro‘yxat ochiq:\n\n"
        f"<b>Ro‘yxat:</b>\n\n{player_list}\n\n"
        f"Jami: {len(active_game['players'])} ta",
        parse_mode="HTML"
    )


async def start_game_now_logic(bot: Bot):
    chat_id = active_game["chat_id"]
    players = active_game["players"]

    active_game["is_active"] = True
    active_game["day"] = 1
    random.shuffle(players)

    count = len(players)
    roles = get_roles_for_player_count(count)
    active_game["assignments"] = {}

    for player, role in zip(players, roles):
        active_game["assignments"][player["id"]] = role
        await bot.send_message(
            player["id"],
            f"🎭 Sizning rolingiz: {ROLE_NAMES_UZ[role]}",
            parse_mode="HTML"
        )

    await bot.send_message(chat_id, "✅ O'yin boshlandi!", parse_mode="HTML")
    await run_game_cycle(bot)


async def run_game_cycle(bot: Bot):
    chat_id = active_game["chat_id"]
    start_time = datetime.now()
    winner_type = None

    mafia_roles = ["mafiya", "don", "donning_xotini", "muxlis", "kimyogar"]

    while active_game["is_active"]:
        alive_mafia = [
            p for p in active_game["players"]
            if active_game["assignments"].get(p["id"]) in mafia_roles
        ]
        alive_civilians = [
            p for p in active_game["players"]
            if active_game["assignments"].get(p["id"]) not in mafia_roles
        ]

        if not alive_mafia:
            winner_type = "civilian"
            await bot.send_message(chat_id, "🎉 Tinch aholi g‘alaba qozondi!", parse_mode="HTML")
            active_game["is_active"] = False
            break

        if len(alive_mafia) >= len(alive_civilians):
            winner_type = "mafia"
            await bot.send_message(chat_id, "💀 Mafiya g‘alaba qozondi!", parse_mode="HTML")
            active_game["is_active"] = False
            break

        await start_night(bot)
        await sleep(2)
        await start_voting(bot)
        await sleep(2)
        active_game["day"] += 1

    end_time = datetime.now()
    duration = end_time - start_time
    minutes = duration.seconds // 60
    seconds = duration.seconds % 60

    players = active_game["players"]
    assignments = active_game["assignments"]
    winners, losers = [], []
    seen_user_ids = set()

    for p in players:
        user_id = p["id"]
        name = p["name"]
        mention = f"<a href='tg://user?id={user_id}'>{name}</a>"
        role_key = assignments.get(user_id)
        role_text = ROLE_NAMES_UZ.get(role_key, "Nomaʼlum")
        line = f"{mention} - {role_text}"

        seen_user_ids.add(user_id)

        if winner_type == "civilian" and role_key not in mafia_roles:
            winners.append(line)
        elif winner_type == "mafia" and role_key in mafia_roles:
            winners.append(line)
        else:
            losers.append(line)

    # Qo‘shilgan, ammo roli belgilanmagan (yoki aniqlanmagan) o‘yinchilarni ham loser sifatida qo‘shamiz
    for p in players:
        if p["id"] not in seen_user_ids:
            mention = f"<a href='tg://user?id={p['id']}'>{p['name']}</a>"
            line = f"{mention} - Nomaʼlum"
            losers.append(line)

    winners_text = "\n".join(winners) or "–"
    losers_text = "\n".join(losers) or "–"

    result_text = (
        f"<b>🎉 G‘olib bo‘lgan o‘yinchilar:</b>\n\n"
        f"{winners_text}\n\n"
        f"<b>❌ Qolgan o‘yinchilar ro‘yxati:</b>\n\n"
        f"{losers_text}\n\n"
        f"🕒 <i>O‘yin vaqti:</i> {minutes} minut {seconds} sekund"
    )

    await bot.send_message(chat_id, result_text, parse_mode="HTML")


async def update_registration_message(bot: Bot):
    chat_id = active_game["chat_id"]
    message_id = active_game["message_id"]

    me = await bot.get_me()
    bot_username = me.username

    join_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Qo‘shilish", url=f"https://t.me/{bot_username}?start=join")]
    ])

    player_list = "\n".join([
        f"– <a href='tg://user?id={p['id']}'>{p['name']}</a>"
        for p in active_game["players"]
    ]) or "–"

    text = (
        "✅ <b>Ro‘yxatdan o‘tish boshlandi.</b>\n\n"
        "Ro‘yxatdan o‘tganlar:\n\n"
        f"{player_list}\n\n"
        f"Jami: {len(active_game['players'])} ta\n\n"
        "⏳ 3 daqiqa ichida o‘yin avtomatik boshlanadi.\n"
        "Yoki 5+ o‘yinchi yig‘ilgach /start_game_now buyrug‘i bilan boshlang."
    )

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=join_btn,
        parse_mode="HTML"
    )


reset_game_state()
