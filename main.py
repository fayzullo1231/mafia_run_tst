import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from database import init_db, init_groups_db
from handlers.game_flow import router as game_flow_router
from handlers.mafia_actions import router as mafia_router
from handlers.doctor_actions import router as doctor_router
from handlers.commissioner_actions import router as commissioner_router
from handlers.voting import router as vote_router
from handlers.group_welcome import router as group_router
from handlers.join import router as join_router  # MUHIM! Qo'shilish uchun
from handlers.daydi_actions import router as daydi_router
from handlers.manyak_actions import router as manyak_router


async def main():
    # Database tayyorlash
    init_db()
    init_groups_db()

    # Bot object (3.7 uchun to'g'ri usul)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # Barcha routerlar ulangan bo'lishi kerak
    dp.include_router(game_flow_router)
    dp.include_router(mafia_router)
    dp.include_router(doctor_router)
    dp.include_router(commissioner_router)
    dp.include_router(vote_router)
    dp.include_router(group_router)
    dp.include_router(join_router)  # MUHIM!!! Shu bo'lmasa ishlamaydi
    dp.include_router(daydi_router)
    dp.include_router(manyak_router)

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
