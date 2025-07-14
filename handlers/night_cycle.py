from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from asyncio import sleep, gather
import os
from models.game_state import active_game
from utils.role_summary import generate_role_summary
from models.game_state import ROLE_NAMES_UZ


async def start_night(bot: Bot):
    chat_id = active_game["chat_id"]

    if os.path.exists("media/sunset.mp4"):
        await bot.send_video(
            chat_id, FSInputFile("media/sunset.mp4"),
            caption="🌃 <b>Tun boshlandi</b>\nKo'chaga faqat jasur va qo'rqmas odamlar chiqishdi. Ertalab tirik qolganlarni sanaymiz...",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            chat_id,
            "🌃 <b>Tun boshlandi</b>\nKo'chaga faqat jasur va qo'rqmas odamlar chiqishdi. Ertalab tirik qolganlarni sanaymiz...",
            parse_mode="HTML"
        )

    bot_username = (await bot.get_me()).username
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Botga o'tish", url=f"https://t.me/{bot_username}")]
        ]
    )

    summary = generate_role_summary(active_game["assignments"])
    await bot.send_message(chat_id, summary, parse_mode="HTML", reply_markup=keyboard)

    # HAR BIR ROL HARAKATI
    from handlers.mafia_actions import mafia_action
    from handlers.doctor_actions import doctor_action
    from handlers.commissioner_actions import commissioner_action
    from handlers.daydi_actions import daydi_action, notify_daydi
    from handlers.manyak_actions import manyak_action  # MANYAK HAM QO‘SHILDI

    await gather(
        mafia_action(bot),
        doctor_action(bot),
        commissioner_action(bot),
        daydi_action(bot),
        manyak_action(bot)
    )

    await sleep(20)

    mafia_target = active_game.get("mafia_target")
    doctor_target = active_game.get("doctor_target")
    manyak_target = active_game.get("manyak_target")

    # MAFIYA O‘LDIRADI
    if mafia_target and mafia_target != doctor_target:
        killed_player = next((p for p in active_game["players"] if p["id"] == mafia_target), None)
        if killed_player:
            role = active_game["assignments"].get(mafia_target, 'nomaʼlum')
            role_name = ROLE_NAMES_UZ.get(role, "Nomaʼlum")

            active_game["players"] = [p for p in active_game["players"] if p["id"] != mafia_target]
            active_game["assignments"].pop(mafia_target, None)

            await bot.send_message(
                chat_id,
                f"Tunda {role_name} <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> vahshiylarcha o'ldirildi...\n"
                "Aytishlaricha u 🤵🏻 Don tomonidan o‘ldirilgan.",
                parse_mode="HTML"
            )

    # MANYAK O‘LDIRADI
    if manyak_target and manyak_target != doctor_target:
        killed_player = next((p for p in active_game["players"] if p["id"] == manyak_target), None)
        if killed_player:
            role = active_game["assignments"].get(manyak_target, 'nomaʼlum')
            role_name = ROLE_NAMES_UZ.get(role, "Nomaʼlum")

            active_game["players"] = [p for p in active_game["players"] if p["id"] != manyak_target]
            active_game["assignments"].pop(manyak_target, None)

            await bot.send_message(
                chat_id,
                f"Tunda {role_name} <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> Manyak tomonidan o‘ldirilgan.",
                parse_mode="HTML"
            )

    if (not mafia_target or mafia_target == doctor_target) and (not manyak_target or manyak_target == doctor_target):
        await bot.send_message(chat_id, "🛡 Bu tun hech kim halok bo‘lmadi.", parse_mode="HTML")

    await notify_daydi(bot)

    if os.path.exists("media/sunrise.mp4"):
        await bot.send_video(
            chat_id, FSInputFile("media/sunrise.mp4"),
            caption=f"🏙 <b>{active_game['day']}-kun</b>\nQuyosh chiqdi, ammo tun orqasida nima bo‘lganini faqat bir necha kishi biladi...",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            chat_id,
            f"🏙 <b>{active_game['day']}-kun</b>\nQuyosh chiqdi, ammo tun orqasida nima bo‘lganini faqat bir necha kishi biladi...",
            parse_mode="HTML"
        )

    await sleep(2)

    await bot.send_message(chat_id, generate_role_summary(active_game["assignments"]), parse_mode="HTML", reply_markup=keyboard)

    await bot.send_message(
        chat_id,
        "👨‍⚖ <b>Aybdorlarni aniqlash va jazolash vaqti keldi.</b>\nOvoz berish vaqti: 45 soniya.",
        parse_mode="HTML",
        reply_markup=keyboard
    )
