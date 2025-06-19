import subprocess
import time
import logging
import sys
import os
from telegram.ext import Updater

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Конфигурация
PORT = int(os.environ.get('PORT', 10000))
TOKEN = os.environ.get('API_TOKEN')
MAX_RESTART_ATTEMPTS = 3
SCRIPTS = ["news_from_google.py", "news_from_yandex.py"]

class BotManager:
    def __init__(self):
        self.updater = Updater(TOKEN, use_context=True)
        self.processes = {}

    def run_script(self, script_name, restart_count=0):
        try:
            logging.info(f'Запуск скрипта: {script_name}')
            process = subprocess.Popen(["python", script_name])
            self.processes[script_name] = process
            return process
        except Exception as e:
            logging.error(f'Ошибка при запуске {script_name}: {e}')
            return None

    def monitor_process(self, script_name, process, restart_count=0):
        try:
            process.wait()
            
            if process.returncode != 0:
                logging.warning(f'Скрипт {script_name} завершился с кодом ошибки: {process.returncode}')
                
                if restart_count < MAX_RESTART_ATTEMPTS:
                    logging.info(f'Попытка перезапуска {script_name} (Попытка {restart_count + 1})')
                    new_process = self.run_script(script_name, restart_count + 1)
                    
                    if new_process:
                        self.monitor_process(script_name, new_process, restart_count + 1)
                else:
                    logging.error(f'Превышено максимальное количество попыток перезапуска для {script_name}')
            else:
                logging.info(f'Скрипт {script_name} завершился успешно с кодом: {process.returncode}')
        
        except Exception as e:
            logging.error(f'Ошибка при мониторинге {script_name}: {e}')

    def start_scripts(self):
        for script in SCRIPTS:
            process = self.run_script(script)
            if process:
                self.monitor_process(script, process)

    def start_webhook(self):
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
        self.updater.bot.set_webhook(webhook_url)
        
        self.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url
        )
        logging.info(f"Webhook запущен на порту {PORT}")

    def start(self):
        try:
            # Запуск скриптов в фоне
            self.start_scripts()
            
            # Запуск webhook
            self.start_webhook()
            
            # Бесконечный цикл для поддержания работы
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logging.info('Программа остановлена пользователем')
            self.shutdown()
            sys.exit(0)
        except Exception as e:
            logging.error(f'Непредвиденная ошибка: {e}')
            self.shutdown()
            sys.exit(1)

    def shutdown(self):
        logging.info("Завершение работы...")
        # Остановка всех процессов
        for script, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                logging.info(f"Остановлен процесс {script}")
        
        # Остановка бота
        if hasattr(self, 'updater'):
            self.updater.stop()
            logging.info("Бот остановлен")

if __name__ == "__main__":
    if not TOKEN:
        logging.error("Токен бота не установлен! Укажите BOT_TOKEN в переменных окружения.")
        sys.exit(1)
        
    manager = BotManager()
    manager.start()
