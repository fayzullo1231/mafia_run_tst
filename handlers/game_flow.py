from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random
from models.game_state import active_game, ROLE_NAMES_UZ, roles_for_5
from utils.role_summary import generate_role_summary
from handlers.night_cycle import start_night
from handlers.voting import start_voting
from asyncio import sleep

router = Router()


@router.message(Command("start_game"))
async def start_game(msg: Message, bot: Bot):
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
        "✅ <b>Ro‘yxatdan o‘tish boshlandi.</b>\n"
        "Kamida 5 kishi bo‘lishi kerak.",
        reply_markup=join_btn,
        parse_mode="HTML"
    )
    active_game["message_id"] = msg_sent.message_id


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
        "✅ Ro‘yxatdan o‘tish boshlandi.\n"
        "Ro‘yxatdan o‘tganlar:\n\n"
        f"{player_list or '–'}\n\n"
        f"Jami: {len(active_game['players'])} ta\n\n"
        "⛔ O‘yin boshlash uchun kamida 5 o‘yinchi kerak."
    )

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=join_btn,
        parse_mode="HTML"
    )


async def start_game_if_ready(bot: Bot):
    chat_id = active_game["chat_id"]
    players = active_game["players"]

    if len(players) < 5:
        await bot.send_message(chat_id, "⛔ O‘yin boshlash uchun kamida 5 o‘yinchi kerak.", parse_mode="HTML")
        return

    active_game["is_active"] = True
    active_game["day"] = 1
    random.shuffle(players)
    roles = random.sample(roles_for_5, len(players))
    active_game["assignments"] = {}

    for player, role in zip(players, roles):
        active_game["assignments"][player["id"]] = role
        await bot.send_message(
            player["id"], f"🎭 Sizning rolingiz: {ROLE_NAMES_UZ[role]}",
            parse_mode="HTML"
        )

    await bot.send_message(chat_id, "✅ O'yin boshlandi!", parse_mode="HTML")

    await run_game_cycle(bot)


async def run_game_cycle(bot: Bot):
    chat_id = active_game["chat_id"]

    while active_game["is_active"]:
        alive_mafia = [p for p in active_game["players"] if active_game["assignments"].get(p["id"]) in ["mafiya", "don"]]
        alive_civilians = [p for p in active_game["players"] if active_game["assignments"].get(p["id"]) not in ["mafiya", "don"]]

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
