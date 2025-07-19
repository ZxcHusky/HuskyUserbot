import random
import time
import sys
import os
import asyncio
import base64
import subprocess
import glob
import signal
import requests
import importlib.util
from pyrogram import Client, filters
from pyrogram.types import Message, User
from pyrogram.enums import ChatType

WEBSITE_URL = "https://huskyuserbot.vercel.app"

@Client.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_command(client: Client, message: Message):
    try:
        start = time.time()
        await message.edit("🏓 Понг!")
        end = time.time()
        await message.edit(f"🏓 Понг!\n⚡ Скорость отклика: {round((end - start) * 1000)}мс")
    except Exception as e:
        await message.edit("⚠️ Произошла ошибка при выполнении команды")

@Client.on_message(filters.command("test", prefixes=".") & filters.me)
async def test_command(client: Client, message: Message):
    await message.edit("✅ Бот работает!")

@Client.on_message(filters.command("restart", prefixes=".") & filters.me)
async def restart_command(client: Client, message: Message):
    try:
        with open('restart_msg.txt', 'w') as f:
            f.write(f"{message.chat.id},{message.id}")
        
        await message.edit("🔄 Перезапуск бота...\n\n⏳ Пожалуйста, подождите...")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        restart_path = os.path.join(os.path.dirname(script_dir), "restart.py")
        
        subprocess.Popen(
            ['start', 'cmd', '/k', 'python', restart_path],
            shell=True,
            cwd=os.path.dirname(script_dir)
        )
        
        await asyncio.sleep(2)
        
        sys.exit(0)
        
    except Exception as e:
        await message.edit(f"❌ Ошибка при перезапуске: {str(e)}")

@Client.on_message(filters.command("installmodule", prefixes=".") & filters.me)
async def install_module_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("❌ Использование: .installmodule [название_модуля]\n\nПример: .installmodule gpt_module")
            return
        
        module_name = message.command[1]
        await message.edit(f"🔄 Поиск модуля '{module_name}'...")
        
        module_path = f"modules/{module_name}.py"
        if os.path.exists(module_path):
            await message.edit(f"⚠️ Модуль '{module_name}' уже установлен!\n\nИспользуйте .updatemodule {module_name} для обновления")
            return
        
        try:
            response = requests.get(f"{WEBSITE_URL}/api/modules/{module_name}", timeout=10)
            
            if response.status_code == 404:
                await message.edit(f"❌ Модуль '{module_name}' не найден на сервере\n\nПроверьте название или посетите сайт для просмотра доступных модулей")
                return
            elif response.status_code != 200:
                await message.edit(f"❌ Ошибка сервера: {response.status_code}")
                return
            
            module_data = response.json()
            
        except requests.exceptions.RequestException as e:
            await message.edit(f"❌ Ошибка подключения к серверу:\n{str(e)}")
            return
        except Exception as e:
            await message.edit(f"❌ Ошибка при получении данных: {str(e)}")
            return
        
        await message.edit(f"📥 Скачивание модуля '{module_name}'...")
        
        os.makedirs("modules", exist_ok=True)
        
        try:
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_data['source_code'])
            
            await message.edit(f"🔄 Загрузка модуля '{module_name}'...")
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'setup'):
                    await module.setup(client)
                
                success_text = f"""✅ **Модуль успешно установлен!**

📦 **Название:** {module_data['name']}
📝 **Описание:** {module_data['description']}
👤 **Автор:** {module_data.get('author', 'Неизвестно')}
🔢 **Версия:** {module_data['version']}

🔄 Модуль загружен и готов к использованию!
Используйте `.help` для просмотра новых команд"""
                
                await message.edit(success_text)
                
            except Exception as e:
                if os.path.exists(module_path):
                    os.remove(module_path)
                await message.edit(f"❌ Ошибка при загрузке модуля:\n{str(e)}\n\nМодуль удален. Попробуйте перезапустить бота.")
                
        except Exception as e:
            await message.edit(f"❌ Ошибка при сохранении модуля: {str(e)}")
            
    except Exception as e:
        await message.edit(f"❌ Неожиданная ошибка: {str(e)}")

@Client.on_message(filters.command("updatemodule", prefixes=".") & filters.me)
async def update_module_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("❌ Использование: .updatemodule [название_модуля]")
            return
        
        module_name = message.command[1]
        module_path = f"modules/{module_name}.py"
        
        if not os.path.exists(module_path):
            await message.edit(f"❌ Модуль '{module_name}' не установлен\n\nИспользуйте .installmodule {module_name} для установки")
            return
        
        await message.edit(f"🔄 Обновление модуля '{module_name}'...")
        
        try:
            response = requests.get(f"{WEBSITE_URL}/api/modules/{module_name}", timeout=10)
            
            if response.status_code == 404:
                await message.edit(f"❌ Модуль '{module_name}' не найден на сервере")
                return
            elif response.status_code != 200:
                await message.edit(f"❌ Ошибка сервера: {response.status_code}")
                return
            
            module_data = response.json()
            
        except requests.exceptions.RequestException as e:
            await message.edit(f"❌ Ошибка подключения к серверу:\n{str(e)}")
            return
        
        backup_path = f"modules/{module_name}.py.backup"
        try:
            if os.path.exists(module_path):
                with open(module_path, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(old_content)
        except Exception:
            pass
        
        try:
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_data['source_code'])
            
            success_text = f"""✅ **Модуль обновлен!**

📦 **Название:** {module_data['name']}
🔢 **Версия:** {module_data['version']}

⚠️ **Перезапустите бота** для применения изменений:
`.restart`"""
            
            await message.edit(success_text)
            
        except Exception as e:
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                    with open(module_path, 'w', encoding='utf-8') as f:
                        f.write(old_content)
                    os.remove(backup_path)
                except Exception:
                    pass
            await message.edit(f"❌ Ошибка при обновлении модуля: {str(e)}")
            
    except Exception as e:
        await message.edit(f"❌ Неожиданная ошибка: {str(e)}")

@Client.on_message(filters.command("removemodule", prefixes=".") & filters.me)
async def remove_module_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("❌ Использование: .removemodule [название_модуля]")
            return
        
        module_name = message.command[1]
        
        if module_name in ['mainmodules', '__init__']:
            await message.edit("❌ Нельзя удалить системный модуль!")
            return
        
        module_path = f"modules/{module_name}.py"
        
        if not os.path.exists(module_path):
            await message.edit(f"❌ Модуль '{module_name}' не найден")
            return
        
        try:
            os.remove(module_path)
            await message.edit(f"✅ Модуль '{module_name}' удален\n\n⚠️ Перезапустите бота для применения изменений")
        except Exception as e:
            await message.edit(f"❌ Ошибка при удалении: {str(e)}")
            
    except Exception as e:
        await message.edit(f"❌ Неожиданная ошибка: {str(e)}")

@Client.on_message(filters.command("listmodules", prefixes=".") & filters.me)
async def list_available_modules_command(client: Client, message: Message):
    try:
        await message.edit("🔄 Получение списка доступных модулей...")
        
        try:
            response = requests.get(f"{WEBSITE_URL}/api/modules", timeout=10)
            
            if response.status_code != 200:
                await message.edit(f"❌ Ошибка сервера: {response.status_code}")
                return
            
            modules_data = response.json()
            
            if not modules_data:
                await message.edit("❌ На сервере нет доступных модулей")
                return
            
            modules_text = "📚 **Доступные модули на сервере:**\n\n"
            
            for module in modules_data[:10]:
                status = "✅ Установлен" if os.path.exists(f"modules/{module['name']}.py") else "📥 Не установлен"
                modules_text += f"📦 **{module['name']}** v{module['version']}\n"
                modules_text += f"└─ {module['description']}\n"
                modules_text += f"└─ {status}\n\n"
            
            if len(modules_data) > 10:
                modules_text += f"... и еще {len(modules_data) - 10} модулей\n\n"
            
            modules_text += "**Команды:**\n"
            modules_text += "`.installmodule [название]` - установить\n"
            modules_text += "`.updatemodule [название]` - обновить\n"
            modules_text += "`.removemodule [название]` - удалить"
            
            await message.edit(modules_text)
            
        except requests.exceptions.RequestException as e:
            await message.edit(f"❌ Ошибка подключения к серверу:\n{str(e)}")
        except Exception as e:
            await message.edit(f"❌ Ошибка при получении данных: {str(e)}")
            
    except Exception as e:
        await message.edit(f"❌ Неожиданная ошибка: {str(e)}")

@Client.on_message(filters.command("calc", prefixes=".") & filters.me)
async def calc_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Использование: .calc [выражение]")
        return
    
    try:
        expression = " ".join(message.command[1:])
        result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})
        await message.edit(f"🔢 {expression} = **{result}**")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("pin", prefixes=".") & filters.me)
async def pin_message(client: Client, message: Message):
    if message.reply_to_message:
        try:
            await client.pin_chat_message(
                message.chat.id,
                message.reply_to_message.id
            )
            await message.edit("📌 Сообщение закреплено!")
        except Exception as e:
            await message.edit(f"❌ Ошибка: {str(e)}")
    else:
        await message.edit("❌ Ответьте на сообщение, которое хотите закрепить")

@Client.on_message(filters.command(["id", "chatid"], prefixes=".") & filters.me)
async def get_id(client: Client, message: Message):
    if message.command[0] == "chatid":
        await message.edit(f"ID чата: `{message.chat.id}`")
    else:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            await message.edit(f"ID пользователя: `{user_id}`")
        else:
            await message.edit(f"ID чата: `{message.chat.id}`\nВаш ID: `{message.from_user.id}`")

@Client.on_message(filters.command("info", prefixes=".") & filters.me)
async def user_info(client: Client, message: Message):
    if not message.reply_to_message:
        await message.edit("❌ Ответьте на сообщение пользователя")
        return

    user: User = message.reply_to_message.from_user
    info_text = f"""
👤 **Информация о пользователе:**
**ID:** `{user.id}`
**Имя:** {user.first_name}
**Фамилия:** {user.last_name or "Нет"}
**Username:** @{user.username or "Нет"}
**Бот:** {"Да" if user.is_bot else "Нет"}
"""
    await message.edit(info_text)

@Client.on_message(filters.command("user", prefixes=".") & filters.me)
async def find_user(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Укажите username пользователя")
        return
    
    username = message.command[1].replace("@", "")
    try:
        user = await client.get_users(username)
        info_text = f"""
👤 **Найден пользователь:**
**ID:** `{user.id}`
**Имя:** {user.first_name}
**Фамилия:** {user.last_name or "Нет"}
**Username:** @{user.username or "Нет"}
"""
        await message.edit(info_text)
    except Exception:
        await message.edit("❌ Пользователь не найден")

@Client.on_message(filters.command("setname", prefixes=".") & filters.me)
async def set_name(client: Client, message: Message):
    args = message.text.split(maxsplit=2)[1:]
    if not args:
        await message.edit("❌ Укажите новое имя")
        return
    
    try:
        if len(args) == 2:
            await client.update_profile(first_name=args[0], last_name=args[1])
            await message.edit(f"✅ Имя изменено на: {args[0]} {args[1]}")
        else:
            await client.update_profile(first_name=args[0])
            await message.edit(f"✅ Имя изменено на: {args[0]}")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("setbio", prefixes=".") & filters.me)
async def set_bio(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit("❌ Укажите новое био")
        return
    
    new_bio = message.text.split(maxsplit=1)[1]
    try:
        await client.update_profile(bio=new_bio)
        await message.edit("✅ Био успешно обновлено")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command(["coin", "flip"], prefixes=".") & filters.me)
async def coin_command(client: Client, message: Message):
    try:
        result = random.choice(["👑 Орёл", "🪙 Решка"])
        await message.edit("🎲 Подбрасываю монетку...")
        await asyncio.sleep(1)
        await message.edit(result)
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("parse", prefixes=".") & filters.me)
async def parse_members(client: Client, message: Message):
    if not message.chat.id:
        await message.edit("❌ Эта команда работает только в группах/каналах")
        return

    await message.edit("🔄 Начинаю парсинг участников...")
    try:
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot:
                user = member.user
                members.append(f"• {user.first_name} {user.last_name or ''} (@{user.username or 'Нет'}) - `{user.id}`")
                
                if len(members) >= 50:
                    break
        
        result = "👥 **Участники чата:**\n\n" + "\n".join(members)
        await message.edit(result)
    except Exception as e:
        await message.edit(f"❌ Ошибка при парсинге: {str(e)}")

@Client.on_message(filters.command("call", prefixes=".") & filters.me)
async def call_all_members(client: Client, message: Message):
    try:
        if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await message.edit("❌ Эта команда работает только в группах")
            return

        await message.edit("🔄 Сбор участников...")
        
        custom_text = " ".join(message.command[1:]) if len(message.command) > 1 else "👥 Всем привет!"
        
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)
        
        if not members:
            await message.edit("❌ Не найдено участников для тега")
            return
        
        chunk_size = 5
        for i in range(0, len(members), chunk_size):
            chunk = members[i:i + chunk_size]
            mentions = []
            
            for user in chunk:
                name = user.first_name
                if user.last_name:
                    name += f" {user.last_name}"
                mentions.append(f"[{name}](tg://user?id={user.id})")
            
            mention_text = f"{custom_text}\n{' '.join(mentions)}"
            try:
                await client.send_message(message.chat.id, mention_text)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Ошибка при отправке тегов: {e}")
                continue
        
        await message.edit("✅ Все участники были уведомлены!")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("encode", prefixes=".") & filters.me)
async def encode_base64(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("❌ Использование: .encode [текст]")
            return
        
        text = " ".join(message.command[1:])
        encoded = base64.b64encode(text.encode()).decode()
        await message.edit(f"🔒 **Encoded:**\n`{encoded}`")
    except Exception as e:
        await message.edit(f"❌ Ошибка: {str(e)}")

@Client.on_message(filters.command("decode", prefixes=".") & filters.me)
async def decode_base64(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit("❌ Использование: .decode [base64]")
            return
        
        text = " ".join(message.command[1:])
        decoded = base64.b64decode(text.encode()).decode()
        await message.edit(f"🔓 **Decoded:**\n`{decoded}`")
    except Exception as e:
        await message.edit(f"❌ Ошибка: неверный формат base64")

@Client.on_message(filters.command("help", prefixes=".") & filters.me)
async def help_command(client: Client, message: Message):
    try:
        help_text = """
📚 **Доступные команды:**

**Основные:**
`.ping` - Проверка работоспособности бота
`.test` - Тест бота
`.help` - Показать это сообщение
`.restart` - Перезапустить юзербота
`.modules` - Показать список загруженных модулей
`.id` - Показать ID пользователя/чата
`.info` - Информация о пользователе (реплаем)
`.chatid` - ID текущего чата
`.user` - Найти пользователя по нику
`.pin` - Закрепить сообщение (реплаем)
`.calc` - Калькулятор (например, .calc 2+2*3)
`.parse` - Парсинг участников группы
`.call` - Тегнуть всех участников чата

**Управление модулями:**
`.installmodule [название]` - Установить модуль с сайта
`.updatemodule [название]` - Обновить модуль
`.removemodule [название]` - Удалить модуль
`.listmodules` - Список доступных модулей

**Шифрование:**
`.encode [текст]` - Зашифровать текст в base64
`.decode [base64]` - Расшифровать текст из base64

**Профиль:**
`.setname` - Изменить имя/фамилию
`.setbio` - Изменить био

**Развлечения:**
`.coin` или `.flip` - Подбросить монетку

**Дополнительно:**
Другие команды зависят от установленных модулей
"""
        await message.edit(help_text)
    except Exception as e:
        await message.edit("⚠️ Произошла ошибка при выполнении команды")

@Client.on_message(filters.command("modules", prefixes=".") & filters.me)
async def list_modules(client: Client, message: Message):
    try:
        module_files = glob.glob("modules/*.py")
        
        if not module_files:
            await message.edit("❌ Модули не найдены")
            return
        
        modules_text = "📚 **Загруженные модули:**\n\n"
        
        for module_path in module_files:
            module_name = os.path.basename(module_path)[:-3]
            
            if module_name.startswith('_'):
                continue
                
            if module_name == "mainmodules":
                description = "Основные команды бота"
            elif module_name == "gpt_module":
                description = "Интеграция с ChatGPT"
            elif module_name == "search_module":
                description = "Поиск информации"
            elif module_name == "saver_module":
                description = "Сохранение медиафайлов"
            elif module_name == "games":
                description = "Игровые команды"
            elif module_name == "osint_module":
                description = "OSINT и поиск утечек"
            else:
                description = "Дополнительный модуль"
            
            modules_text += f"📌 **{module_name}**\n"
            modules_text += f"└─ {description}\n\n"
        
        total_modules = len([m for m in module_files if not os.path.basename(m)[:-3].startswith('_')])
        modules_text += f"**Всего модулей:** {total_modules}\n\n"
        modules_text += "**Управление модулями:**\n"
        modules_text += "`.listmodules` - доступные на сайте\n"
        modules_text += "`.installmodule [название]` - установить новый"
        
        await message.edit(modules_text)
        
    except Exception as e:
        await message.edit(f"❌ Ошибка при получении списка модулей: {str(e)}")
