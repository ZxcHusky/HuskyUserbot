import os
import sys
import logging
import asyncio
import importlib
import glob
import subprocess
import signal
from typing import Dict
from pyrogram import Client
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import Progress
from colorama import init
from dotenv import load_dotenv

init()
load_dotenv()
console = Console()

API_ID = ""
API_HASH = ""
NAME = "userbot"

loaded_modules = {}
restart_flag = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def handle_restart():
    global restart_flag
    restart_flag = True

signal.signal(signal.SIGTERM, lambda signum, frame: handle_restart())

def show_banner():
    console.print(Panel("""
[bold cyan]╔══╗─────╔╗──╔═╗
║╔╗║─────║║──║╔╝
║╚╝╚╦╗╔╦═╝║╔═╝╚╦══╦═╗╔══╗
║╔═╗║║║║╔╗║║╔═╗║║═╣╔╝║══╣
║╚═╝║╚╝║╚╝║║╚═╝║║═╣║─╠══║
╚═══╩══╩══╝╚═══╩══╩╝─╚══╝[/bold cyan]

[blink yellow]▄︻デT͎E͎L͎E͎G͎R͎A͎M͎ U͎S͎E͎R͎B͎O͎T══━一[/blink yellow]
[green]Версия: 2.1 Beta| Husky-inspired[/green]""", 
title="🚀 [bold white]ЗАПУСК СИСТЕМЫ[/bold white]", border_style="bright_cyan"))

async def authorize_user() -> Client:
    console.print(Panel("[bold bright_white]⚡ ИНИЦИАЛИЗАЦИЯ АВТОРИЗАЦИИ[/bold bright_white]", border_style="yellow"))
    
    if not API_ID or not API_HASH:
        console.print(Panel("[red]⛔ ОШИБКА: Отсутствуют API-ключи![/red]", border_style="red"))
        sys.exit(1)

    app = Client(NAME, api_id=API_ID, api_hash=API_HASH, plugins=dict(root="modules"))
    
    try:
        session_file = f"{NAME}.session"
        if os.path.exists(session_file):
            console.print("[green]✓ Найден существующий файл сессии[/green]")
            return app

        console.print("[yellow]Подключение к Telegram...[/yellow]")
        await app.connect()

        try:
            await app.get_me()
        except Exception:
            phone = Prompt.ask("[bold yellow]📱 ВВЕДИТЕ НОМЕР ТЕЛЕФОНА[/bold yellow]")
            sent_code = await app.send_code(phone)
            
            code = Prompt.ask("[bold yellow]🔑 ВВЕДИТЕ КОД ИЗ TELEGRAM[/bold yellow]")
            
            try:
                await app.sign_in(phone, sent_code.phone_code_hash, code)
            except SessionPasswordNeeded:
                password = Prompt.ask("[bold red]🔒 Введите пароль 2FA[/bold red]", password=True)
                await app.check_password(password)
        
        await app.disconnect()
        console.print(Panel("[green]✅ АВТОРИЗАЦИЯ УСПЕШНА![/green]", border_style="green"))
        return app
    except Exception as e:
        console.print(Panel(f"[red]⛔ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}[/red]", border_style="red"))
        try:
            await app.disconnect()
        except:
            pass
        sys.exit(1)

async def load_modules(app: Client):
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
        console.print("[yellow]📁 Создана директория modules[/yellow]")
        return

    module_files = glob.glob(os.path.join(modules_dir, "*.py"))
    
    for module_path in module_files:
        try:
            module_name = os.path.basename(module_path)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'setup'):
                await module.setup(app)
            
            loaded_modules[module_name] = module
            console.print(f"[green]✓ Загружен модуль:[/green] {module_name}")
        except Exception as e:
            console.print(f"[red]⚠️ Ошибка загрузки модуля {module_name}:[/red] {str(e)}")

async def main():
    show_banner()
    
    with Progress() as progress:
        task = progress.add_task("[cyan]🔄 ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            await asyncio.sleep(0.02)
    
    app = await authorize_user()
    
    try:
        await app.start()
        await load_modules(app)
        
        console.print(Panel("[bold green]✅ СИСТЕМА АКТИВИРОВАНА[/bold green]", 
                          subtitle="Используйте [yellow].help[/yellow] для списка команд", 
                          border_style="green"))
        
        print("\n[green]Бот успешно запущен! Нажмите CTRL+C для остановки.[/green]")
        
        while not restart_flag:
            await asyncio.sleep(1)
        
        if restart_flag:
            console.print("[yellow]⚡ Запуск процесса перезагрузки...[/yellow]")
            subprocess.Popen([sys.executable, "restart.py"],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           start_new_session=True)
            await app.stop()
            sys.exit(0)
            
    except KeyboardInterrupt:
        console.print(Panel("[yellow]⚡ Завершение работы...[/yellow]", border_style="yellow"))
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
    finally:
        try:
            if app.is_connected:
                await app.stop()
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {str(e)}")

def idle():
    loop = asyncio.get_event_loop()
    return loop.create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(Panel("[red]⛔ СИСТЕМА ОСТАНОВЛЕНА[/red]", border_style="red"))
