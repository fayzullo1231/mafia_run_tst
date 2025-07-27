from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict
from models.game_state import active_game, ROLE_NAMES_UZ
from asyncio import sleep
from aiogram.exceptions import TelegramBadRequest
from handlers.kamikade_action import kamikadze_hanged
from handlers.suicider_role import check_suicider_hanging  # ✅ Suidsid import

router = Router()

vote_counts = defaultdict(list)
voted_users = set()
final_vote_results = {"yes": [], "no": []}
final_vote_users = {}


@router.callback_query(F.data.startswith("vote:"))
async def handle_vote(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    data = callback.data.split(":")[1]

    if user_id in voted_users:
        await callback.answer("❗ Siz allaqachon ovoz berdingiz!", show_alert=True)
        return

    if data == "skip":
        await callback.message.edit_text("⏭ Ovoz berish o'tkazildi.")
    else:
        voted_id = int(data)
        vote_counts[voted_id].append(user_id)
        await callback.message.edit_text("✅ Ovoz qabul qilindi.")

        voter_name = callback.from_user.first_name
        target_name = next(
            (p["name"] for p in active_game["players"] if p["id"] == voted_id), "Nomaʼlum"
        )

        await bot.send_message(
            active_game["chat_id"],
            f"📢 <a href='tg://user?id={user_id}'>{voter_name}</a> → <a href='tg://user?id={voted_id}'>{target_name}</a> ga ovoz berdi",
            parse_mode="HTML"
        )

    voted_users.add(user_id)


@router.callback_query(F.data.startswith("finalvote:"))
async def handle_final_vote(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    vote_type = callback.data.split(":")[1]

    if user_id not in [p["id"] for p in active_game["players"]]:
        await callback.answer("❗ Faqat o‘yindagi ishtirokchilar ovoz bera oladi!", show_alert=True)
        return

    old_vote = final_vote_users.get(user_id)
    if old_vote:
        final_vote_results[old_vote].remove(user_id)

    final_vote_results[vote_type].append(user_id)
    final_vote_users[user_id] = vote_type

    yes = len(final_vote_results["yes"])
    no = len(final_vote_results["no"])

    vote_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"👍 {yes}", callback_data="finalvote:yes"),
                InlineKeyboardButton(text=f"👎 {no}", callback_data="finalvote:no")
            ]
        ]
    )

    try:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=active_game["final_vote_message_id"],
            reply_markup=vote_markup
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer("✅ Ovoz qabul qilindi.")


async def start_voting(bot: Bot):
    players = active_game["players"]

    for player in players:
        vote_buttons = [
            [InlineKeyboardButton(text=p["name"], callback_data=f"vote:{p['id']}")]
            for p in players if p["id"] != player["id"]
        ]
        vote_buttons.append([InlineKeyboardButton(text="❌ O‘tkazib yuborish", callback_data="vote:skip")])

        await bot.send_message(
            player["id"],
            "🗳 Ovoz berish boshlandi. Kimni osamiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=vote_buttons)
        )

    await sleep(45)
    await finish_voting(bot)


async def finish_voting(bot: Bot):
    chat_id = active_game["chat_id"]

    if not vote_counts:
        await bot.send_message(chat_id, "⚠️ Hech kimga ovoz bermadi!")
        return

    max_votes = max(len(v) for v in vote_counts.values())
    candidates = [pid for pid, v in vote_counts.items() if len(v) == max_votes]

    if len(candidates) != 1:
        await bot.send_message(chat_id, "🤷‍♂️ Bahslar tugadi, hech kim osilmadi.")
        return

    selected_id = candidates[0]
    selected_name = next((p["name"] for p in active_game["players"] if p["id"] == selected_id), "Nomaʼlum")
    active_game["final_vote_candidate_id"] = selected_id

    vote_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍 0", callback_data="finalvote:yes"),
                InlineKeyboardButton(text="👎 0", callback_data="finalvote:no")
            ]
        ]
    )

    msg = await bot.send_message(
        chat_id,
        f"Rostdan xam <b>{selected_name}</b> ni osmoqchimisiz?",
        reply_markup=vote_markup,
        parse_mode="HTML"
    )

    active_game["final_vote_message_id"] = msg.message_id
    await sleep(20)

    yes = len(final_vote_results["yes"])
    no = len(final_vote_results["no"])
    final_role = active_game["assignments"].get(selected_id, 'Nomaʼlum')

    result_text = (
        f"Ovoz berish natijalari:\n{yes} 👍 | {no} 👎\n"
        f"<b>{selected_name}</b> {'osildi ☠️' if yes > no else 'qutuldi.'}"
    )

    await bot.edit_message_text(
        result_text,
        chat_id=chat_id,
        message_id=active_game["final_vote_message_id"],
        parse_mode="HTML"
    )

    if yes > no:
        await bot.send_message(
            chat_id,
            f"🦦 {selected_name} - {ROLE_NAMES_UZ.get(final_role, 'Nomaʼlum')} edi",
            parse_mode="HTML"
        )

        # ✅ Suicider tekshirish
        if await check_suicider_hanging(selected_id, bot):
            return  # Suicider yutdi — o‘yin tugadi

        # Kamikadze tekshirish
        if active_game["assignments"].get(selected_id) == "kamikadze":
            await kamikadze_hanged(bot, chat_id)

        active_game["players"] = [p for p in active_game["players"] if p["id"] != selected_id]
        active_game["assignments"].pop(selected_id, None)

    vote_counts.clear()
    voted_users.clear()
    final_vote_results["yes"].clear()
    final_vote_results["no"].clear()
    final_vote_users.clear()
