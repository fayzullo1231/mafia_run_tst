from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from asyncio import create_task, sleep
import random

from models.game_state import active_game, ROLE_NAMES_UZ
from utils.role_summary import generate_role_summary
from handlers.night_cycle import start_night
from handlers.voting import start_voting
from models.game_state import get_roles_for_player_count  # <-- yuqoriga import


router = Router()

@router.message(Command("start_game"))
async def start_game(msg: Message, bot: Bot):
    if active_game.get("is_active"):
        await msg.answer("⛔ O‘yin allaqachon boshlandi. Avval uni yakunlang.")
        return

    chat_id = msg.chat.id
    active_game["chat_id"] = chat_id
    active_game["group_title"] = msg.chat.title
    active_game["players"] = []
    active_game["is_active"] = False
    active_game["assignments"] = {}
    active_game["day"] = 1

    me = await bot.get_me()
    bot_username = me.username

    join_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖓 Qo‘shilish", url=f"https://t.me/{bot_username}?start=join")]
    ])

    msg_sent = await msg.answer(
        f"✅ <b>Ro‘yxatdan o‘tish boshlandi.</b>\n\n"
        f"Ro‘yxatdan o‘tganlar:\n\n–\n\n"
        f"Jami: 0 ta\n\n"
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
        [InlineKeyboardButton(text="🖓 Qo‘shilish", url=f"https://t.me/{bot_username}?start=join")]
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
    roles = get_roles_for_player_count(count)  # <-- Avtomatik rollar tanlanadi
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

    while active_game["is_active"]:
        mafia = ["mafiya", "don"]
        alive_mafia = [p for p in active_game["players"] if active_game["assignments"].get(p["id"]) in mafia]
        alive_civilians = [p for p in active_game["players"] if active_game["assignments"].get(p["id"]) not in mafia]

        if not alive_mafia:
            await bot.send_message(chat_id, "🎉 Tinch aholi g‘alaba qozondi!", parse_mode="HTML")
            active_game["is_active"] = False
            break
        if len(alive_mafia) >= len(alive_civilians):
            await bot.send_message(chat_id, "💀 Mafiya g‘alaba qozondi!", parse_mode="HTML")
            active_game["is_active"] = False
            break

        await start_night(bot)
        await sleep(2)
        await start_voting(bot)
        await sleep(2)
        active_game["day"] += 1
