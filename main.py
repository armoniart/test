from threading import Thread

def run_script(script_name, restart_count=0):
    def target():
        nonlocal restart_count
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

    thread = Thread(target=target)
    thread.start()
    return thread

def main():
    try:
        while True:
            run_script("news_from_google.py")
            run_script("news_from_yandex.py")

            time.sleep(60)  # Пауза между новыми запусками
    except KeyboardInterrupt:
        logging.info("Остановлено пользователем")
