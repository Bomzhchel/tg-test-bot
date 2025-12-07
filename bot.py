import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

# Токен
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Нет BOT_TOKEN!")
    print("Добавьте переменную BOT_TOKEN в Render")
    exit(1)

# Хранилище
users = {}

# Вопросы
questions = [
    "🧭 ТЕСТ: Твій шлях — власна справа чи стабільна робота?\n\n"
    "1. Що ти відчуваєш на роботі?\n"
    "A. Втома, нудьга\nB. Мені ок\nC. Подобається\nD. Люблю роботу",
    
    "2. Ризики?\nA. Лякають\nB. Не люблю\nC. Нормально\nD. Не боюсь",
    
    "3. Бізнесмени?\nA. Пощастило\nB. Заздрю\nC. Надихає\nD. Хочу так!",
    
    "4. Рішення?\nA. Чекаю інструкцій\nB. Потрібна підтримка\nC. Інтуїтивно\nD. Швидко сам",
    
    "5. Гроші та час?\nA. Відпочивати\nB. Шукати заняття\nC. Досліджувати\nD. Відкривати справу",
    
    "6. Рутина?\nA. Люблю\nB. Терплю\nC. Важко\nD. Ненавиджу",
    
    "7. Що важливіше?\nA. Стабільність\nB. Баланс\nC. Реалізація\nD. Свобода"
]

def start(update, context):
    chat_id = update.message.chat_id
    users[chat_id] = {'score': 0, 'q': 0}
    
    update.message.reply_text("🔹 Обери відповідь A, B, C або D")
    send_question(update, chat_id)

def send_question(update, chat_id):
    data = users[chat_id]
    q_num = data['q']
    
    if q_num < len(questions):
        keyboard = [['A', 'B'], ['C', 'D']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(questions[q_num], reply_markup=reply_markup)
    else:
        show_result(update, chat_id)

def handle_message(update, context):
    chat_id = update.message.chat_id
    
    if chat_id not in users:
        update.message.reply_text("Напиши /start")
        return
    
    answer = update.message.text.upper()
    
    if answer in ['A', 'B', 'C', 'D']:
        scores = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        users[chat_id]['score'] += scores[answer]
        users[chat_id]['q'] += 1
        
        send_question(update, chat_id)
    else:
        update.message.reply_text("Обери A, B, C або D")

def show_result(update, chat_id):
    score = users[chat_id]['score']
    
    if score <= 11:
        result = "🔸 Тобі не потрібен бізнес"
    elif score <= 17:
        result = "🟠 Ти ще у пошуку"
    elif score <= 23:
        result = "🟡 У тебе є потенціал!"
    else:
        result = "🟢 Бізнес — твоє природнє середовище!"
    
    update.message.reply_text(
        f"📊 Результат: {score} балів\n\n{result}\n\n/start - знову"
    )
    
    del users[chat_id]

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    print("🤖 Бот запущено!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
