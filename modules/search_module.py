from pyrogram import Client, filters
from pyrogram.types import Message
import re
import requests

async def search_ip(ip: str) -> str:
    try:
        ip_info = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        shodan_url = f"https://www.shodan.io/host/{ip}"
        
        info = f"""╔══「 🌐 **IP Information** 」══╗

**IP Address:** `{ip}`

📍 **Геолокация:**
• Страна: {ip_info.get('country', 'Н/Д')}
• Регион: {ip_info.get('regionName', 'Н/Д')}
• Город: {ip_info.get('city', 'Н/Д')}
• Координаты: {ip_info.get('lat', 'Н/Д')}, {ip_info.get('lon', 'Н/Д')}

🏢 **Техническая информация:**
• ISP: {ip_info.get('isp', 'Н/Д')}
• Организация: {ip_info.get('org', 'Н/Д')}
• ASN: {ip_info.get('as', 'Н/Д')}
• Временная зона: {ip_info.get('timezone', 'Н/Д')}

🔍 **Ссылки для анализа:**
• [Shodan]({shodan_url})
• [AbuseIPDB](https://www.abuseipdb.com/check/{ip})
• [VirusTotal](https://www.virustotal.com/gui/ip-address/{ip})
• [Censys](https://censys.io/ipv4/{ip})

╚════════════════════╝"""
        return info
    except Exception as e:
        return f"❌ Ошибка при поиске информации: {str(e)}"

@Client.on_message(filters.command("search", prefixes=".") & filters.me)
async def ip_search(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit(
            "❌ Использование: `.search [IP-адрес]`\n"
            "Пример: `.search 8.8.8.8`"
        )
        return

    ip = message.command[1]
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        await message.edit("❌ Некорректный формат IP-адреса")
        return

    await message.edit("🔍 Поиск информации...")
    result = await search_ip(ip)
    await message.edit(result, disable_web_page_preview=True) 