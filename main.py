# monitor.py
import logging
import subprocess
import time
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MAX_RESTART_ATTEMPTS = 3

def run_script(script_name):
    restart_count = 0
    while restart_count < MAX_RESTART_ATTEMPTS:
        try:
            logging.info(f'Запуск {script_name}')
            result = subprocess.run(["python", script_name], check=True)
            if result.returncode == 0:
                logging.info(f'{script_name} успешно завершился')
                break
        except subprocess.CalledProcessError as e:
            restart_count += 1
            logging.warning(f'{script_name} упал. Попытка перезапуска ({restart_count}/{MAX_RESTART_ATTEMPTS})')
            time.sleep(5)
    else:
        logging.error(f'Не удалось запустить {script_name} после {MAX_RESTART_ATTEMPTS} попыток')

def main():
    try:
        while True:
            run_script("news_from_google.py")
            run_script("news_from_yandex.py")
            time.sleep(60)  # Интервал между циклами
    except KeyboardInterrupt:
        logging.info("Остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        logging.error(f'Ошибка в основном цикле: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
