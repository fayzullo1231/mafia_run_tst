from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from asyncio import sleep, gather
import os
import random

from handlers.wife_action import wife_action
from handlers.teacher_actions import teacher_action
from models.game_state import active_game
from utils.role_summary import generate_role_summary
from models.game_state import ROLE_NAMES_UZ
from utils.redirect import apply_majnun_redirect

from handlers.serjant_actions import serjant_action
from handlers.mafia_actions import mafia_action
from handlers.doctor_actions import doctor_action
from handlers.commissioner_actions import commissioner_action
from handlers.daydi_actions import daydi_action, notify_daydi
from handlers.manyak_actions import manyak_action
from handlers.tentak_actions import tentak_action
from handlers.kimyogar_actions import kimyogar_action
from handlers.sotuvchi_actions import sotuvchi_action  # yuqoriga import
from handlers.majnun_actions import majnun_action
from handlers.minior_actions import minior_action
from handlers.mergan_actions import mergan_action, router as mergan_router
from handlers.muxlis_actions import muxlis_action, router as muxlis_router
from handlers.buqalamun_actions import buqalamun_action  # tepadagi importlarga qo‘shing
from handlers.thief_actions import thief_action  # yuqoriga import qiling


async def start_night(bot: Bot):
    chat_id = active_game["chat_id"]

    # 🌅 TUN BOSHLANDI VIDEO YOKI TEXT
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

    # 🌙 HOZIRGI HOLAT (ROL TASNIFI)
    summary = generate_role_summary(active_game["assignments"])
    await bot.send_message(chat_id, summary, parse_mode="HTML", reply_markup=keyboard)

    # 🚶 HAR BIR ROL HARAKATI
    await gather(
        mafia_action(bot),
        doctor_action(bot),
        commissioner_action(bot),
        daydi_action(bot),
        manyak_action(bot),
        tentak_action(bot),
        serjant_action(bot),
        wife_action(bot),
        teacher_action(bot),  # YANGI QO'SHILGAN
        kimyogar_action(bot),
        sotuvchi_action(bot),  # ⬅️ BUNI HAM QO‘SHING
        majnun_action(bot),
        minior_action(bot),  # ⬅️ BU YERDA QO‘SHASIZ
        mergan_action(bot),
        muxlis_action(bot),
        buqalamun_action(bot),  # ⬅️ bu joyga qo‘shasiz
        thief_action(bot),  # ✅ Bu yerda chaqirasiz
    )

    await sleep(60)

    # 🔁 MAJNUN EFFECT (redirect targets)
    original_targets = {
        "mafiya_target": active_game.get("mafia_target"),
        "doctor_target": active_game.get("doctor_target"),
        "commissioner_check": active_game.get("commissioner_check"),
        "serjant_target": active_game.get("serjant_target"),
        "daydi_target": active_game.get("daydi_target"),
        "tentak_target": active_game.get("tentak_target"),
    }

    redirected_targets = apply_majnun_redirect(original_targets)

    # Qayta yozamiz
    active_game["doctor_target"] = redirected_targets["doctor_target"]
    active_game["commissioner_check"] = redirected_targets["commissioner_check"]
    active_game["serjant_target"] = redirected_targets["serjant_target"]
    active_game["daydi_target"] = redirected_targets["daydi_target"]
    active_game["tentak_target"] = redirected_targets["tentak_target"]

    # 🔽 endi boshqa kodlar davom etadi
    mafia_target = active_game.get("mafia_target")
    doctor_target = active_game.get("doctor_target")
    manyak_target = active_game.get("manyak_target")
    tentak_target = active_game.get("tentak_target")

    # ✅ TENTAK LOGIKA
    if tentak_target and tentak_target == mafia_target:
        don_id = next((p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "don"),
                      None)
        if don_id:
            killed_player = next((p for p in active_game["players"] if p["id"] == don_id), None)
            if killed_player:
                active_game["players"] = [p for p in active_game["players"] if p["id"] != don_id]
                active_game["assignments"].pop(don_id, None)
                await bot.send_message(
                    chat_id,
                    f"👨‍🧂 Tentak bosh urib 🧕 Don <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> ni kechasi o‘ldirdi!",
                    parse_mode="HTML"
                )

    # Kimyogar eliksiri
    kimyogar_target = active_game.get("kimyogar_target")
    is_mafiya = active_game.get("kimyogar_target_mafiya")

    if kimyogar_target is not None:
        if not is_mafiya:
            killed_player = next((p for p in active_game["players"] if p["id"] == kimyogar_target), None)
            if killed_player:
                role = active_game["assignments"].get(kimyogar_target, 'nomaʼlum')
                role_name = ROLE_NAMES_UZ.get(role, "Nomaʼlum")
                active_game["players"] = [p for p in active_game["players"] if p["id"] != kimyogar_target]
                active_game["assignments"].pop(kimyogar_target, None)
                await bot.send_message(
                    active_game["chat_id"],
                    f"🧪 Kimyogar eliksiri <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> ni zaharladi!\n"
                    f"U aslida {role_name} edi!",
                    parse_mode="HTML"
                )

    minior_target = active_game.get("minior_target")

    if minior_target:
        visitors = []

        for role_key in ["mafia_target", "doctor_target", "commissioner_check", "serjant_target", "daydi_target"]:
            visitor_id = active_game.get(role_key)
            if visitor_id == minior_target:
                actor_id = next((k for k, v in active_game["assignments"].items() if v == role_key.split("_")[0]), None)
                if actor_id:
                    visitors.append(actor_id)

        if visitors:
            for visitor_id in visitors:
                player = next((p for p in active_game["players"] if p["id"] == visitor_id), None)
                if player:
                    role = active_game["assignments"].get(visitor_id, 'nomaʼlum')
                    role_name = ROLE_NAMES_UZ.get(role, "Nomaʼlum")

                    active_game["players"] = [p for p in active_game["players"] if p["id"] != visitor_id]
                    active_game["assignments"].pop(visitor_id, None)

                    await bot.send_message(
                        active_game["chat_id"],
                        f"💥 <a href='tg://user?id={player['id']}'>{player['name']}</a> ({role_name}) mina portlashidan halok bo‘ldi!",
                        parse_mode="HTML"
                    )

        active_game.pop("minior_target", None)

    # Sotuvchi himoyasi haqida tongda ma’lumot
    if "sotuvchi_target" in active_game:
        target_id = active_game["sotuvchi_target"]
        player = next((p for p in active_game["players"] if p["id"] == target_id), None)
        if player:
            await bot.send_message(
                target_id,
                "🛡 Siz tunda noma’lum odam tomonidan himoyalandingiz yoki maxfiy hujjatlar oldingiz.",
                parse_mode="HTML"
            )
        active_game.pop("sotuvchi_target")

    sotuvchi_protected = active_game.get("sotuvchi_protected", [])
    # ☠️ Qasosni amalga oshirish (faqat 1 marta)
    # ☠️ Qasosni amalga oshirish (faqat 1 marta)
    if active_game.get("muxlis_killer") and "muxlis_revenge_done" not in active_game:
        killer_id = next((p["id"] for p in active_game["players"] if active_game["assignments"].get(p["id"]) == "don"),
                         None)
        if killer_id:
            killed_player = next((p for p in active_game["players"] if p["id"] == killer_id), None)
            if killed_player:
                active_game["players"] = [p for p in active_game["players"] if p["id"] != killer_id]
                active_game["assignments"].pop(killer_id, None)
                await bot.send_message(
                    chat_id,
                    f"☠️ Qasoskor o‘z qasosini oldi!\nDon <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> halok bo‘ldi!",
                    parse_mode="HTML"
                )
                active_game["muxlis_revenge_done"] = True

    # ❌ MAFIYA QATL QILADI (o‘zgartirilgan holda)
    if mafia_target and mafia_target != doctor_target and mafia_target not in sotuvchi_protected:
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

    mergan_target = active_game.get("mergan_target")

    if mergan_target:
        killed_player = next((p for p in active_game["players"] if p["id"] == mergan_target), None)
        if killed_player:
            role = active_game["assignments"].get(mergan_target, 'nomaʼlum')
            role_name = ROLE_NAMES_UZ.get(role, "Nomaʼlum")
            active_game["players"] = [p for p in active_game["players"] if p["id"] != mergan_target]
            active_game["assignments"].pop(mergan_target, None)
            await bot.send_message(
                chat_id,
                f"🎯 Mergan tomonidan {role_name} <a href='tg://user?id={killed_player['id']}'>{killed_player['name']}</a> otib o‘ldirildi!",
                parse_mode="HTML"
            )

    # 🔰 HECH KIM O'LMAGAN HOLAT (faqat ro‘yxatdan hech kim o‘chmagan bo‘lsa)
    players_before = set(p["id"] for p in active_game["players"])
    # bu yerga o‘ldirilganlar ustidagi barcha kodlar kirgan bo‘lishi kerak edi (yuqorida ular ishlagan)
    players_after = set(p["id"] for p in active_game["players"])

    if players_before == players_after:
        await bot.send_message(chat_id, "🛡 Bu tun hech kim halok bo‘lmadi.", parse_mode="HTML")

    await notify_daydi(bot)

    active_game["sotuvchi_protected"] = []
    active_game.pop("layli_for_redirect", None)
    active_game.pop("majnun_redirect_to", None)
    active_game.pop("mergan_target", None)

    # 🌅 TONGI VIDEO YOKI TEXT
    if os.path.exists("media/sunrise.mp4"):
        await bot.send_video(
            chat_id, FSInputFile("media/sunrise.mp4"),
            caption=f"🌇 <b>{active_game['day']}-kun</b>\nQuyosh chiqdi, ammo tun orqasida nima bo‘lganini faqat bir necha kishi biladi...",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            chat_id,
            f"🌇 <b>{active_game['day']}-kun</b>\nQuyosh chiqdi, ammo tun orqasida nima bo‘lganini faqat bir necha kishi biladi...",
            parse_mode="HTML"
        )

    # 🎓 O'qituvchining bitiruvchilari
    graduation_list = []
    if "teacher_training" in active_game:
        for student_id, info in list(active_game["teacher_training"].items()):
            if active_game["day"] - info["day"] >= 2:
                graduation_list.append(student_id)
                new_role = random.choice(["shifokor", "serjant", "daydi", "mashuqa"])
                active_game["assignments"][student_id] = new_role

                await bot.send_message(
                    student_id,
                    f"🎓 O‘qituvchining sabrli darslari samara berdi!\nEndi siz yangi kuchli rolga ega bo‘ldingiz: <b>{ROLE_NAMES_UZ.get(new_role, new_role)}</b>",
                    parse_mode="HTML"
                )

                player = next((p for p in active_game["players"] if p["id"] == student_id), None)
                if player:
                    await bot.send_message(
                        chat_id,
                        f"🎓 <b>{player['name']}</b> o‘qituvchining ta’siri ostida kuchli rolda qayta tug‘ildi!",
                        parse_mode="HTML"
                    )

        for sid in graduation_list:
            active_game["teacher_training"].pop(sid, None)

    await sleep(2)

    await bot.send_message(chat_id, generate_role_summary(active_game["assignments"]), parse_mode="HTML",
                           reply_markup=keyboard)

    await bot.send_message(
        chat_id,
        "👨‍⚖ <b>Aybdorlarni aniqlash va jazolash vaqti keldi.</b>\nOvoz berish vaqti: 45 soniya.",
        parse_mode="HTML",
        reply_markup=keyboard
    )
