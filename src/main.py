import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers import router
from app.database.models import async_main
from consts import TG_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("Starting main function")
    load_dotenv()
    logging.info(f"TG_TOKEN: {TG_TOKEN[:5]}...") # Выводим первые 5 символов токена для проверки
    try:
        await async_main()
        logging.info("Database initialization complete")
    except Exception as e:
        logging.error(f"Error during database initialization: {e}")
        return

    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.info("Starting bot polling")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error during bot polling: {e}")

if __name__ == "__main__":
    logging.info("Script started")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
    logging.info("Script finished")