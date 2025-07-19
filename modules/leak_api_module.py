import asyncio
import aiohttp
import json
import math
from typing import Dict, List, Union
from pyrogram import Client, filters
from pyrogram.types import Message

API_URL = 'https://leakosintapi.com/'
API_TOKEN = None

class LeakAPI:
    def __init__(self):
        self.token = None
        self.last_request_time = 0
    
    def calculate_price(self, limit: int, query: str) -> float:
        words = [w for w in query.split() if len(w) >= 4 and not w.isdigit()]
        complexity = 1
        if len(words) == 2:
            complexity = 5
        elif len(words) == 3:
            complexity = 16
        elif len(words) > 3:
            complexity = 40
        
        return (5 + math.sqrt(limit * complexity)) / 5000

    async def search(self, query: str, limit: int = 100, lang: str = "ru") -> Dict:
        if not self.token:
            raise ValueError("API токен не установлен. Используйте .settoken для установки.")
        
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_request_time < 1:
            await asyncio.sleep(1 - (current_time - self.last_request_time))
        
        data = {
            "token": self.token,
            "request": query,
            "limit": limit,
            "lang": lang
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=data) as response:
                self.last_request_time = asyncio.get_event_loop().time()
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"API ошибка: {error_text}")

leak_api = LeakAPI()

@Client.on_message(filters.command("settoken", prefixes=".") & filters.me)
async def set_token_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("❌ Использование: .settoken [API_TOKEN]")
            return
        
        leak_api.token = message.command[1]
        await message.edit("✅ API токен успешно установлен!")
        await asyncio.sleep(3)
        await message.delete()
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("leaksearch", prefixes=".") & filters.me)
async def leak_search_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit(
                "❌ Использование: .leaksearch [запрос] --limit=100 --lang=ru\n\n"
                "Примеры:\n"
                "`.leaksearch email@example.com`\n"
                "`.leaksearch \"Иван Петров\" --limit=200`\n"
                "`.leaksearch username --lang=en`"
            )
            return
        
        args = message.text.split()
        limit = 100
        lang = "ru"
        
        query_parts = []
        i = 1
        while i < len(args):
            if args[i].startswith("--"):
                if args[i].startswith("--limit="):
                    limit = int(args[i].split("=")[1])
                elif args[i].startswith("--lang="):
                    lang = args[i].split("=")[1]
            else:
                query_parts.append(args[i])
            i += 1
        
        query = " ".join(query_parts)
        
        price = leak_api.calculate_price(limit, query)
        await message.edit(f"🔍 Поиск...\n�� Стоимость запроса: ${price:.4f}")
        
        results = await leak_api.search(query, limit, lang)
        
        response = f"🔍 Результаты поиска для '{query}':\n\n"
        
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, (list, dict)):
                    response += f"**{key}:**\n"
                    if isinstance(value, list):
                        for item in value[:10]:
                            response += f"• {item}\n"
                        if len(value) > 10:
                            response += f"... и еще {len(value) - 10} результатов\n"
                    else:
                        response += f"```{json.dumps(value, indent=2, ensure_ascii=False)}```\n"
                else:
                    response += f"**{key}:** {value}\n"
        else:
            response += f"```{json.dumps(results, indent=2, ensure_ascii=False)}```"
        
        response += f"\n📊 Найдено результатов: {len(results) if isinstance(results, list) else 'N/A'}"
        response += f"\n💰 Стоимость запроса: ${price:.4f}"
        
        if len(response) > 4096:
            parts = [response[i:i+4096] for i in range(0, len(response), 4096)]
            await message.edit(parts[0])
            for part in parts[1:]:
                await client.send_message(message.chat.id, part)
        else:
            await message.edit(response)
            
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

help_text = """
**Команды поиска утечек:**
`.settoken` - Установить API токен
`.leaksearch` - Поиск утечек через API

**Параметры .leaksearch:**
--limit=N - Лимит результатов (по умолчанию 100)
--lang=XX - Язык результатов (по умолчанию ru)

**Примеры:**
`.leaksearch email@example.com`
`.leaksearch "Иван Петров" --limit=200`
`.leaksearch username --lang=en`
"""
