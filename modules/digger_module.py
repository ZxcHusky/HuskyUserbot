from pyrogram import Client, filters
import asyncio
import re
from collections import defaultdict

MINE_BOT_ID = 7084173311

active_tasks = {}

stats = {
    'digs': 0,
    'items': defaultdict(int),
    'plasma': 0,
    'ore_found': 0
}

ITEMS_MAP = {
    "✉️": "Конверт",
    "🧧": "Редкий Конверт",
    "📦": "Кейс",
    "🗳": "Редкий Кейс",
    "🕋": "Мифический Кейс",
    "🎆": "Плазма",
    "💼": "Портфель",
    "👜": "Сумка",
}

DEFAULT_DELAY = 1.3

async def dig_loop(client: Client, delay: float = DEFAULT_DELAY):
    try:
        while True:
            await client.send_message(MINE_BOT_ID, "Копать")
            stats['digs'] += 1
            await asyncio.sleep(delay)
    except asyncio.CancelledError:
        pass

@Client.on_message(filters.regex(r"^\.dig(\s+\d*\.?\d*)?$") & filters.me)
async def handle_dig(client: Client, message):
    user_id = message.from_user.id
    
    if user_id in active_tasks and not active_tasks[user_id].done():
        active_tasks[user_id].cancel()
        
        total_digs = stats['digs']
        
        stats_text = [
            "🛑 Копание остановлено",
            f"⛏ Вскопано: {total_digs} раз",
            "\n📊 Найденные предметы:"
        ]
        
        items_found = False
        for emoji, item_name in ITEMS_MAP.items():
            count = stats['items'][emoji]
            if count > 0:
                items_found = True
                stats_text.append(f"{emoji} | {item_name}: {count} шт.")
        
        if not items_found:
            stats_text.append("❌ Предметы не найдены")
        
        stats['digs'] = 0
        stats['items'].clear()
        stats['plasma'] = 0
        stats['ore_found'] = 0
        
        await message.edit_text("\n".join(stats_text))
        return

    delay = DEFAULT_DELAY
    match = re.match(r"^\.dig(?:\s+(\d*\.?\d*))?$", message.text)
    if match and match.group(1):
        try:
            delay = float(match.group(1))
            if delay < 1.0:
                delay = 1.0
        except ValueError:
            await message.edit_text("❌ Ошибка: Неверный формат задержки. Используйте число (например: .dig 2)")
            return

    await message.edit_text(f"⛏ Запускаю копание (задержка: {delay:.1f}с)...")
    
    task = asyncio.create_task(dig_loop(client, delay))
    active_tasks[user_id] = task
    
    await message.edit_text(
        f"✅ Копание запущено (задержка: {delay:.1f}с)\n"
        "Используйте .dig еще раз для остановки"
    )

@Client.on_message(
    filters.chat(MINE_BOT_ID) & 
    filters.user(MINE_BOT_ID)
)
async def handle_mine_messages(_, message):
    text = message.text or ""
    
    for emoji in ITEMS_MAP:
        if emoji in text:
            stats['items'][emoji] += 1
            break

async def setup(app: Client):
    pass 