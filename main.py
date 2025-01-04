import telebot
from feedparser import parse
import time
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

# Получаем значения из переменных окружения
#TOKEN = "7822287020:AAFaKbpCpvXZKOvfQpdu5ndHXVrz42ghhAc"
#CHAT_ID = "-1002486445419"
#RSS_URL = "https://pikabu.ru/xmlfeeds.php?cmd=popular"
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = (os.getenv("CHAT_ID"))
RSS_URL = os.getenv("RSS_URL")

# Имя файла для хранения списка отправленных ссылок
SENT_LINKS_FILE = "sent_links.json"

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Загрузить список уже отправленных ссылок из файла
try:
    with open(SENT_LINKS_FILE, "r") as file:
        sent_links = json.load(file)
except FileNotFoundError:
    sent_links = []

def save_sent_links():
    with open(SENT_LINKS_FILE, "w") as file:
        json.dump(sent_links, file)

def send_random_news():
    global sent_links

    # Парсим RSS-канал
    feed = parse(RSS_URL)

    # Отбираем только те записи, которые еще не были отправлены
    unseen_entries = [entry for entry in feed.entries if entry.link not in sent_links]

    # Если остались неотправленные записи
    if unseen_entries:
        # Выбираем случайную запись
        random_entry = random.choice(unseen_entries)
        title = random_entry.title
        link = random_entry.link

        # Форматируем сообщение
        message = f"📰 Новость:\n\n{title}\n\nПодробнее: {link}"

        # Отправляем сообщение в чат
        bot.send_message(CHAT_ID, message)

        # Добавляем ссылку в список отправленных
        sent_links.append(link)

        # Сохраняем обновленный список в файл
        save_sent_links()

if __name__ == "__main__":
    while True:
        send_random_news()
        # Ожидание между проверками (5 минут)
        time.sleep(100)
