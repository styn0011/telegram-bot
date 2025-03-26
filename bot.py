import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 🔹 Твой токен бота (полученный в @BotFather)
TOKEN = "7933425883:AAGSyezEltnjvrHEgiG5io3DnJU7rq1ph1g"

# 🔹 ID Google Таблицы (берётся из URL)
SPREADSHEET_ID = "1-TrWnh4isXef-Rmqa3bq5GiFcukXDJf8C1REjowd4Lg"

# 🔹 Авторизация в Google API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# 🔹 Открываем Google Таблицу
sheet = client.open_by_key("1-TrWnh4isXef-Rmqa3bq5GiFcukXDJf8C1REjowd4Lg").sheet1

bot = telebot.TeleBot("7933425883:AAGSyezEltnjvrHEgiG5io3DnJU7rq1ph1g")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введи свой логин, и я покажу все твои показатели.")

@bot.message_handler(func=lambda message: True)
def send_data(message):
    user_login = message.text.strip().upper()

    # Загружаем актуальные данные из Google Таблицы
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])  # Берём заголовки из первой строки

    # Убеждаемся, что логины сравниваются корректно
    df['Логин'] = df['Логин'].astype(str).str.strip().str.upper()

    row = df[df['Логин'] == user_login]

    if row.empty:
        bot.reply_to(message, "❌ Логин не найден. Проверьте правильность ввода.")
    else:
        response = f"📊 Данные по логину {user_login}:\n"
        for column in df.columns:
            value = row[column].values[0]
            
            # Принудительно преобразуем числа для точности
            try:
                if "." in value or "," in value:
                    value = float(value.replace(",", "."))
                else:
                    value = int(value)
            except ValueError:
                pass  # Оставляем как есть, если это текст

            response += f"🔹 {column}: {value}\n"

        bot.reply_to(message, response)

print("✅ Бот запущен...")
bot.polling(none_stop=True)