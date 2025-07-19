from pyrogram import Client, filters
from pyrogram.types import Message
import random
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("random", prefixes=".") & filters.me)
async def random_number(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) == 3:
            start = int(args[1])
            end = int(args[2])
            number = random.randint(start, end)
            await message.edit(f"🎲 Случайное число: **{number}**")
        else:
            await message.edit("❌ Использование: .random [start] [end]")
    except ValueError:
        await message.edit("❌ Пожалуйста, укажите числовые значения")

@Client.on_message(filters.command("dice", prefixes=".") & filters.me)
async def dice(client: Client, message: Message):
    try:
        await message.delete()
        await client.send_dice(message.chat.id)
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("dart", prefixes=".") & filters.me)
async def dart(client: Client, message: Message):
    try:
        await message.delete()
        await client.send_dice(message.chat.id, "🎯")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("basket", prefixes=".") & filters.me)
async def basket(client: Client, message: Message):
    try:
        await message.delete()
        await client.send_dice(message.chat.id, "🏀")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

async def setup(app: Client):
    logger.info("Модуль игр загружен") 