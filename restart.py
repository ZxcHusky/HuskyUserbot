import os
import sys
import time
import psutil
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('restart.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def find_main_process():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'main.py' in ' '.join(cmdline) and proc.pid != current_pid:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def terminate_main_process():
    main_process = find_main_process()
    if main_process:
        try:
            logger.info(f"Завершаем процесс main.py (PID: {main_process.pid})")
            main_process.terminate()
            try:
                main_process.wait(timeout=5)
                logger.info("Процесс main.py успешно завершен")
                return True
            except psutil.TimeoutExpired:
                logger.warning("Таймаут ожидания, применяем принудительное завершение")
                main_process.kill()
                return True
        except psutil.NoSuchProcess:
            pass
    return False

def start_main_process():
    try:
        main_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        if not os.path.exists(main_path):
            logger.error(f"Файл main.py не найден по пути: {main_path}")
            return False
            
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        
        process = subprocess.Popen(
            [sys.executable, main_path],
            startupinfo=startupinfo,
            cwd=os.path.dirname(main_path)
        )
        
        if process.pid:
            logger.info(f"main.py успешно запущен (PID: {process.pid})")
            return True
        else:
            logger.error("Не удалось получить PID процесса main.py")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при запуске main.py: {str(e)}")
        return False

def verify_main_process():
    time.sleep(2)
    main_process = find_main_process()
    if main_process and main_process.is_running():
        return True
    return False

def main():
    try:
        logger.info("1. Запуск процесса перезапуска")
        
        logger.info("2. Закрытие main.py")
        if not terminate_main_process():
            logger.warning("main.py не был найден или уже закрыт")
        
        time.sleep(2)
        
        logger.info("3. Запуск main.py")
        if not start_main_process():
            logger.error("Не удалось запустить main.py")
            sys.exit(1)
            
        if not verify_main_process():
            logger.error("main.py не запустился или был преждевременно завершен")
            sys.exit(1)
        
        logger.info("4. Завершение restart.py")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Ошибка при перезапуске: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 