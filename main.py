import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Налаштування для виведення інформації про роботу бота в консоль
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- НАЛАШТУВАННЯ ЗІ ЗМІННИХ СЕРЕДОВИЩА ---
# Беремо токен та ID каналу з налаштувань сервера, а не з коду
TOKEN = os.environ.get("TELEGRAM_TOKEN")
try:
    CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
except (ValueError, TypeError):
    CHANNEL_ID = 0

# Текст, який буде додано
SIGNATURE_TEXT = '\n\nЗберігається «<a href="https://t.me/ArtOfLOL">Музеєм Орного Мистецтва</a>»'

async def edit_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Ця функція спрацьовує на кожне нове повідомлення з медіа в каналі.
    """
    message = update.channel_post
    if not message:
        return

    original_caption = message.caption or ""
    new_caption = original_caption + SIGNATURE_TEXT

    if len(new_caption) > 1024:
        logger.warning(
            f"Не вдалося відредагувати повідомлення {message.message_id}, "
            f"оскільки новий підпис занадто довгий ({len(new_caption)}/1024)."
        )
        return

    try:
        await context.bot.edit_message_caption(
            chat_id=message.chat_id,
            message_id=message.message_id,
            caption=new_caption,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Успішно додано підпис до повідомлення {message.message_id} в каналі {message.chat.title}.")
    except Exception as e:
        logger.error(f"Не вдалося відредагувати повідомлення {message.message_id}: {e}")

def main() -> None:
    """Основна функція для запуску бота."""
    if not TOKEN or not CHANNEL_ID:
        logger.error("ПОМИЛКА: Не вказано TELEGRAM_TOKEN або CHANNEL_ID у змінних середовища.")
        return

    application = Application.builder().token(TOKEN).build()

    handler = MessageHandler(
        filters.Chat(chat_id=CHANNEL_ID) & (filters.PHOTO | filters.VIDEO | filters.Document.ALL),
        edit_new_post
    )
    
    application.add_handler(handler)

    logger.info("Бот успішно запущений і слухає канал...")
    application.run_polling()

if __name__ == '__main__':
    main()
