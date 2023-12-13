import openai
import logging
import random
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext

# Токен бота
TOKEN = '6828815775:AAEY46F9-IvnPd9fZueomDe-gWMe6MDmDEo'

# Настройка журналирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализируйте бота и обновление
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Функции команд

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот с различными функциями. Вот что я могу:\n'
                              '/weather - узнать прогноз погоды\n'
                              '/random - сгенерировать случайное число\n'
                              '/exchange - получить курсы валют и стоимость акций\n'
                              '/news - прочитать последние новости\n'
                              '/chat - ChatGPT')



WEATHERSTACK_API_KEY = "0ab2afb6fa6e69d6523ead08fcf966ec"


def weather(update: Update, context: CallbackContext) -> None:
    # Получаем название города из сообщения пользователя
    city = context.args[0] if context.args else "Saint Petersburg"

    # Формируем запрос к Weatherstack API
    url = f"http://api.weatherstack.com/current?access_key={WEATHERSTACK_API_KEY}&query={city}"
    response = requests.get(url)
    data = response.json()

    # Обрабатываем ответ от API
    if response.status_code == 200:
        current_temperature = data['current']['temperature']
        description = data['current']['weather_descriptions'][0]
        update.message.reply_text(f'Погода в городе {city}: {current_temperature}°C, {description}')
    else:
        update.message.reply_text('Не удалось получить прогноз погоды. Попробуйте позже.')


def random_number(update: Update, context: CallbackContext) -> None:
    if context.args and context.args[0].lower() == 'coin':
        # Режим подброса монетки
        result = random.choice(['Орел', 'Решка'])
        update.message.reply_text(f'Результат подброса монетки: {result}')
    else:
        # Режим случайного числа
        if context.args:
            try:
                start_range = int(context.args[0])
                end_range = int(context.args[1]) + 1
                random_num = random.randint(start_range, end_range)
                update.message.reply_text(f'Случайное число от {start_range} до {end_range - 1}: {random_num}')
            except ValueError:
                update.message.reply_text('Пожалуйста, введите корректные числовые значения для диапазона.')
        else:
            random_num = random.randint(1, 100)
            update.message.reply_text(f'Случайное число от 1 до 100: {random_num}')


# Ваш ключ для exchangeratesapi.io
EXCHANGE_API_KEY = "429b637415f8c3674e7112841f9cb6b5"

def exchange(update: Update, context: CallbackContext) -> None:
    # Формируем запрос к exchangeratesapi.io
    url = f"https://open.er-api.com/v6/latest"
    params = {'apikey': EXCHANGE_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()

    # Обрабатываем ответ от API
    if response.status_code == 200:
        rates = data['rates']
        message = "Курсы валют:\n"
        for currency, rate in rates.items():
            message += f"{currency}: {rate}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text('Не удалось получить курсы валют. Попробуйте позже.')



NEWS_API_KEY = "a354576782354fbb89cd0e47cd61c100"

def news(update: Update, context: CallbackContext) -> None:
    # Формируем запрос к News API
    url = "https://newsapi.org/v2/top-headlines"
    params = {'apiKey': NEWS_API_KEY, 'country': 'us'}  # Используем США для примера, можно изменить страну
    response = requests.get(url, params=params)
    data = response.json()

    # Обрабатываем ответ от API
    if response.status_code == 200:
        articles = data['articles']
        message = "Последние новости:\n"
        for article in articles:
            title = article['title']
            url = article['url']
            message += f"- {title}\n{url}\n\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text('Не удалось получить новости. Попробуйте позже.')




OPENAI_API_KEY = "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"

# Установка ключа API OpenAI
openai.api_key = OPENAI_API_KEY

def chat_with_gpt(update: Update, context: CallbackContext) -> None:
    # Получаем текст сообщения пользователя
    user_input = ' '.join(context.args)

    if not user_input:
        update.message.reply_text('Пожалуйста, введите текст для общения с GPT.')
        return

    # Вызываем чат с GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input},
        ]
    )

    # Получаем ответ от GPT
    gpt_reply = response['choices'][0]['message']['content'].strip()

    # Отправляем ответ пользователю
    update.message.reply_text(f'GPT: {gpt_reply}')

# Обработчики команд
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("weather", weather, pass_args=True))
dispatcher.add_handler(CommandHandler("random", random_number, pass_args=True))
dispatcher.add_handler(CommandHandler("exchange", exchange))
dispatcher.add_handler(CommandHandler("news", news))
dispatcher.add_handler(CommandHandler("chat", chat_with_gpt, pass_args=True))

# Запуск бота
updater.start_polling()
updater.idle()
