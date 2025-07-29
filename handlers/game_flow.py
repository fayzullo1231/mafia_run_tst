from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from asyncio import create_task, sleep
from datetime import datetime
import random

from models.game_state import active_game, ROLE_NAMES_UZ
from utils.role_summary import generate_role_summary
from handlers.night_cycle import start_night
from handlers.voting import start_voting
from models.game_state import get_roles_for_player_count

router = Router()

@router.message(Command("start_game"))
async def start_game(msg: Message, bot: Bot):
    try:
        await msg.delete()  # Komandani yuborgan odamning xabarini o‘chirish
    except:
        pass

    if active_game.get("is_active"):
        # O'yin allaqachon boshlangan bo‘lsa – faqat ro‘yxatni yuboradi
        player_list = "\n".join([
            f"– <a href='tg://user?id={p['id']}'>{p['name']}</a>"
            for p in active_game["players"]
        ]) or "–"

        await msg.answer(
            f"⛔ O‘yin allaqachon boshlandi.\n\n"
            f"<b>Ro‘yxat:</b>\n\n{player_list}\n\n"
            f"Jami: {len(active_game['players'])} ta",
            parse_mode="HTML"
        )
        return

    if active_game.get("players"):
        # Agar ro‘yxat mavjud bo‘lsa (yangi boshlanmagan), uni davom ettiradi
        player_list = "\n".join([
            f"– <a href='tg://user?id={p['id']}'>{p['name']}</a>"
            for p in active_game["players"]
        ])
    else:
        player_list = "–"

    chat_id = msg.chat.id
    active_game["chat_id"] = chat_id
    active_game["group_title"] = msg.chat.title
    active_game.setdefault("players", [])
    active_game["is_active"] = False
    active_game["assignments"] = {}
    active_game["day"] = 1

    me = await bot.get_me()
    bot_username = me.username

    join_btn = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👤 Qo‘shilish", url=f"https://t.me/{bot_username}?start=join")
    ]])

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
    ])

    text = (
        "✅ <b>Ro‘yxatdan o‘tish boshlandi.</b>\n\n"
        "Ro‘yxatdan o‘tganlar:\n\n"
        f"{player_list or '–'}\n\n"
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


async def wait_and_start(bot: Bot):
    await sleep(180)  # 3 daqiqa kutadi
    if not active_game["is_active"] and len(active_game["players"]) >= 5:
        await start_game_now_logic(bot)


@router.message(Command("start_game_now"))
async def start_game_now(msg: Message, bot: Bot):
    if active_game.get("is_active"):
        await msg.answer("⛔ O‘yin allaqachon boshlandi.")
        return
    if len(active_game["players"]) < 5:
        await msg.answer("❗ Kamida 5 o‘yinchi kerak.")
        return
    await start_game_now_logic(bot)


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

    while active_game["is_active"]:
        mafia = ["mafiya", "don"]
        alive_mafia = [p for p in active_game["players"] if active_game["assignments"].get(p["id"]) in mafia]
        alive_civilians = [p for p in active_game["players"] if active_game["assignments"].get(p["id"]) not in mafia]

        if not alive_mafia:
            await bot.send_message(chat_id, "🎉 Tinch aholi g‘alaba qozondi!", parse_mode="HTML")
            active_game["is_active"] = False
            winner_type = "civilian"
            break
        if len(alive_mafia) >= len(alive_civilians):
            await bot.send_message(chat_id, "💀 Mafiya g‘alaba qozondi!", parse_mode="HTML")
            active_game["is_active"] = False
            winner_type = "mafia"
            break

        await start_night(bot)
        await sleep(2)
        await start_voting(bot)
        await sleep(2)
        active_game["day"] += 1

    # 🏁 O‘yin yakuni — natijalarni chiqaramiz
    end_time = datetime.now()
    duration = end_time - start_time
    minutes = duration.seconds // 60
    seconds = duration.seconds % 60

    players = active_game["players"]
    assignments = active_game["assignments"]

    winners = []
    losers = []
    mafia_roles = ["mafiya", "don"]

    for p in players:
        user_id = p["id"]
        name = p["name"]
        mention = f"<a href='tg://user?id={user_id}'>{name}</a>"
        role_key = assignments.get(user_id, "nomaʼlum")
        role_text = ROLE_NAMES_UZ.get(role_key, role_key)
        line = f"{mention} - {role_text}"

        if winner_type == "civilian" and role_key not in mafia_roles:
            winners.append(line)
        elif winner_type == "mafia" and role_key in mafia_roles:
            winners.append(line)
        else:
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
