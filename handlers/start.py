import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from aiogram import Router, Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.enums import ChatType
from aiogram import F
from models.game_state import active_game


from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.deep_linking import create_start_link
from utils.i18n import t


# .env ni yuklash
load_dotenv(find_dotenv())
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN o‘rnatilmagan! .env fayldagi BOT_TOKEN ni tekshiring.")

load_dotenv(find_dotenv())  # .env faylni yuklash
BOT_USERNAME = os.getenv("BOT_USERNAME")

if not BOT_USERNAME:
    raise RuntimeError("BOT_USERNAME .env fayldan topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# In-memory til saqlash
user_lang: dict[int, str] = {}

# Asosiy menyu yaratish
async def build_main_menu(lang: str) -> InlineKeyboardMarkup:
    # Guruhga qo‘shish uchun havola: .env'dan olinadi
    join_link = f"https://t.me/{BOT_USERNAME}?startgroup=true"

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text=t("menu_add", lang), url=join_link)
    ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text=t("menu_profile", lang), callback_data="show_profile")
    ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text=t("menu_news", lang), url="https://t.me/mafiaoyinlari")
    ])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text=t("menu_lang", lang), callback_data="change_lang"),
        InlineKeyboardButton(text=t("menu_rules", lang), callback_data="rules")
    ])
    return kb

# Profil menyuni yaratish
def build_profile_menu(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    kb.inline_keyboard.append([
        InlineKeyboardButton(text=t("menu_back", lang), callback_data="main_menu")
    ])
    return kb

@router.message(CommandStart(deep_link=True))
async def start_with_deeplink(msg: Message, bot: Bot):
    user_id = msg.from_user.id
    name = msg.from_user.first_name

    # Deep link argumentini olish
    args = msg.text.split(" ")
    deep_link_arg = args[1] if len(args) > 1 else ""

    if deep_link_arg == "join":
        # Ro‘yxatga qo‘shish
        if not any(p["id"] == user_id for p in active_game["players"]):
            active_game["players"].append({"id": user_id, "name": name})

        # Ishtirokchilar ro‘yxatini chiqarish
        player_names = "\n".join(
            [f"– <a href='tg://user?id={p['id']}'>{p['name']}</a>" for p in active_game["players"]]
        )

        text = (
            "✅ <b>Ro‘yxatdan o‘tish boshlandi.</b>\n"
            "<b>Ro‘yxatdan o‘tganlar:</b>\n"
            f"{player_names or '–'}\n\n"
            f"<b>Jami:</b> {len(active_game['players'])} ta\n\n"
            "⛔ O‘yin boshlash uchun kamida <b>5 o‘yinchi</b> kerak."
        )

        # Doimiy qo‘shilish tugmasi
        join_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Qo‘shilish",
                url=f"https://t.me/{BOT_USERNAME}?start=join"
            )]
        ])

        # Eski xabarni yangilash
        if active_game.get("chat_id") and active_game.get("message_id"):
            try:
                await bot.edit_message_text(
                    chat_id=active_game["chat_id"],
                    message_id=active_game["message_id"],
                    text=text,
                    parse_mode="HTML",
                    reply_markup=join_btn
                )
            except Exception as e:
                print("Xabarni yangilab bo‘lmadi:", e)

        await msg.answer(f"✅ Siz o‘yinga muvaffaqiyatli qo‘shildingiz, {name}!")

    else:
        await msg.answer("❗ Noma’lum havola.")

# 2) Oddiy /start — til tanlash
@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def start_plain(msg: Message):
    user_id = msg.from_user.id
    name = msg.from_user.first_name
    lang = user_lang.get(user_id, "uz")

    menu = await build_main_menu(lang)
    await msg.answer(
        t("welcome", lang, name=name),
        reply_markup=menu
    )

# 2) Til o‘rnatish va asosiy menyu
@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def set_language(cb: CallbackQuery):
    lang = cb.data.split(":", 1)[1]
    user_lang[cb.from_user.id] = lang
    menu = await build_main_menu(lang)
    text = t("welcome", lang, name=cb.from_user.first_name)
    await cb.message.edit_text(text, reply_markup=menu)
    await cb.answer()

# 3) Tilni o‘zgartirish
@router.callback_query(lambda c: c.data == "change_lang")
async def change_lang(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")

    # Til tanlash tugmalari — nomlari bilan
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")]
    ])

    await cb.message.edit_text(t("lang_prompt", lang), reply_markup=kb)
    await cb.answer()

# 4) Profil ekrani
@router.callback_query(lambda c: c.data == "show_profile")
async def show_profile(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    name = cb.from_user.username or cb.from_user.first_name or "User"
    stats = dict(dollar=0, diamond=0, protector=0, killer_protect=0,
                 vote_protect=0, gun=0, mask=0, fake_docs=0,
                 next_role="-", total_games=0, wins=0)
    text = t("profile_text", lang, name=name, **stats)
    kb = build_profile_menu(lang)
    await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()

# 5) Qoidalar
@router.callback_query(lambda c: c.data == "rules")
async def show_rules(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    rules = t("rules_text", lang)

    # Orqaga tugmasi
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("menu_back", lang), callback_data="main_menu")]
    ])

    await cb.message.edit_text(rules, reply_markup=kb)
    await cb.answer()

# 6) Orqaga qaytish — asosiy menyu
@router.callback_query(lambda c: c.data == "main_menu")
async def main_menu(cb: CallbackQuery):
    lang = user_lang.get(cb.from_user.id, "uz")
    menu = await build_main_menu(lang)
    text = t("welcome", lang, name=cb.from_user.first_name)
    await cb.message.edit_text(text, reply_markup=menu)
    await cb.answer()