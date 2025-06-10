import os
import json
import logging
import aiohttp
import asyncio
import random
from bs4 import BeautifulSoup

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'
KEYWORDS = [
    "открытие фонтанов 2025",
    "реставрация фонтана 2026",
    "строительство фонтана 2025",
    "голографические фонтаны 2026",
    "светомузыкальный фонтан 2025",
    "Пешеходный фонтан 2026",
    "Реконструкция фонтанов 2025",
    "Поющие фонтаны 2026",
    "Мультимедийный фонтан 2025",
    "Мультимедийный фонтан 2026",
    "Поющие фонтаны 2025",
    "Реконструкция фонтанов 2026",
    "Пешеходный фонтан 2025",
    "светомузыкальный фонтан 2026",
    "голографические фонтаны 2025",
    "строительство фонтана 2026",
    "реставрация фонтана 2025",
    "открытие фонтанов 2026",
]
MUST_HAVE_WORDS = {"Фонтан", "фонтан", "светомузыкальный"}
IGNORE_WORDS = {"Объявления", "Акци", "акци", "Экскурс", "экскурс", "Купит", "купит", "Услуги", "рукам", "Герона", "герона", "лыжн", "трасс", "Коммуна", "коммуна", "Водоканал", "Жило", "жило", "жильц", "Ледяно", "ледяно", "труб", "аварий", "забил", "бьёт", "из-под", "ситуац", "питьев", "кипят", "канализ", "пахучий", "нечистот", "фекал", "Петергоф", "петергоф", "Нефт", "нефт", "Газов", "газов", "недр", "месторож", "добыва", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"}
IGNORE_WORDS_LINK = {"instagram", "tiktok", "livejournal", "fontanka", "avito", "2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"}
USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/113.0", 
        "Mozilla/5.0 (Android 12; Mobile; rv:109.0) Gecko/113.0 Firefox/113.0", 
        "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16", 
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0", 
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0", 
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36", 
        "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15", 
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35", 
        "Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35", 
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35", 
]
logging.basicConfig(level=logging.DEBUG)

# Загрузка уже отправленных новостей
def load_sent_news():
    if os.path.exists(SENT_LIST_FILE):
        with open(SENT_LIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохранение отправленных новостей
def save_sent_news(sent_news):
    with open(SENT_LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(sent_news, f, ensure_ascii=False, indent=4)

# Проверка на наличие обязательных слов
def contains_must_have_words(text):
    return any(word in text for word in MUST_HAVE_WORDS)

# Проверка на наличие игнорируемых слов
def contains_ignore_words(text, ignore_words):
    return any(word in text for word in ignore_words)

# Проверка работоспособности ссылки
async def is_link_working(session, link):
    try:
        async with session.get(link, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logging.warning(f'__YANDEX__Проблема с ссылкой: {link} - {e}')
        return False

# Получение новостей из Yandex
async def get_news(session, keyword):
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Referer': 'https://yandex.ru/',  # Имитация перехода с главной страницы
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',  # Предпочитаемые языки
        'Accept-Encoding': 'gzip, deflate, br',  # Поддержка сжатия
        'Cache-Control': 'no-cache',  # Отключение кэша
        'Connection': 'keep-alive',  # Поддержка постоянного соединения
    }
    async with session.get(query, headers=headers) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            results = []
            for item in soup.find_all('li', class_='serp-item'):
                title = item.find('h2').get_text() if item.find('h2') else None
                link = item.find('a', class_='link')['href'] if item.find('a', class_='link') else None
                if title and link:
                    results.append({'title': title, 'link': link})
            return results
        else:
            logging.error(f'__YANDEX__Ошибка: {response.status} для запроса: {keyword}')
            return []

# Отправка сообщения в Telegram
async def send_to_telegram(session, title, link):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#Фонтан"
    payload = {
        'chat_id': CHANNEL_ID,
        'text': message_text
    }
    try:
        async with session.post(url, data=payload) as response:
            if response.status == 200:
                logging.info('__YANDEX__Отправлено.')
            else:
                logging.error(f'__YANDEX__Ошибка: {response.status} - {await response.text()}')
    except Exception as e:
        logging.error(f'__YANDEX__Ошибка: {e}')

# Основная функция
async def main():
    sent_news = load_sent_news()
    async with aiohttp.ClientSession() as session:
        while True:  # Бесконечный цикл
            for keyword in KEYWORDS:
                results = await get_news(session, keyword)
                logging.info(f'__YANDEX__Найдено {len(results)} : {keyword}')
                for result in results:
                    title = result['title']
                    link = result['link']

                    if contains_ignore_words(title, IGNORE_WORDS) or contains_ignore_words(link, IGNORE_WORDS_LINK):
                        logging.info(f'__YANDEX__Игнор: {link}')
                        continue

                    if not contains_must_have_words(title):
                        logging.info(f'__YANDEX__Нет слов: {title}')
                        continue

                    if any(news['link'] == link or news['title'] == title for news in sent_news):
                        logging.info(f'__YANDEX__Новость есть: {title} - {link}')
                        continue

                    if not await is_link_working(session, link):
                        logging.warning(f'__YANDEX__Ссылка не рабочая: {link}')
                        continue

                    await send_to_telegram(session, title, link)
                    sent_news.append({'title': title, 'link': link})
                    save_sent_news(sent_news)
                await asyncio.sleep(random.randint(222, 505))  # От минут до часа

# Запуск асинхронного цикла
if __name__ == "__main__":
    asyncio.run(main())
