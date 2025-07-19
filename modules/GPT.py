from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import time
import asyncio

@Client.on_message(filters.command("gpt", prefixes=".") & filters.me)
async def gpt_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Использование: .gpt [ваш запрос]")
        return

    query = " ".join(message.command[1:])
    
    loading_frames = ["🤖 Думаю", "🤖 Думаю.", "🤖 Думаю..", "🤖 Думаю..."]
    for _ in range(2):
        for frame in loading_frames:
            await message.edit(frame)
            await asyncio.sleep(0.3)

    try:
        send = {
            "model": "gpt-4o-mini",
            "request": {
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            }
        }

        response = requests.post('http://api.onlysq.ru/ai/v2', json=send)
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            formatted_response = f"""╔══「 **GPT Response** 」══╗

**Запрос:**
```
{query}
```

**Ответ:**
```
{answer}
```

╚═══════════════════╝

⚡️ Время ответа: {response.elapsed.total_seconds():.2f}с"""
            
            await message.edit(formatted_response)
        else:
            await message.edit(f"""╔══「 ❌ **Error** 」══╗

**Ошибка API:**
```
Код ошибки: {response.status_code}
```

╚════════════════╝""")
    except Exception as e:
        await message.edit(f"""╔══「 ❌ **Error** 」══╗

**Системная ошибка:**
```
{str(e)}
```

╚════════════════╝""") 