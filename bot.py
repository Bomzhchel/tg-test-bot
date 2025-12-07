import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

# Получаем токен из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')

# Хранилище баллов пользователей
user_scores = {}

# Команда /start
def start(update, context):
    user_id = update.message.chat_id
    user_scores[user_id] = {'score': 0, 'question': 1}
    
    # Отправляем первый вопрос
    keyboard = [['A', 'B'], ['C', 'D']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🧭 ТЕСТ: Твій шлях — власна справа чи стабільна робота?\n\n"
        "1. Що ти відчуваєш на роботі?\n"
        "A. Втома, нудьга\n"
        "B. Мені ок\n"
        "C. Подобається\n"
        "D. Люблю роботу",
        reply_markup=reply_markup
    )

# Обработка ответов
def handle_message(update, context):
    user_id = update.message.chat_id
    
    # Если пользователь не начал тест
    if user_id not in user_scores:
        update.message.reply_text("Напиши /start щоб почати")
        return
    
    answer = update.message.text.upper()
    
    # Вопросы теста
    questions = [
        "2. Ризики?\nA. Лякають\nB. Не люблю\nC. Нормально\nD. Не боюсь",
        "3. Бізнесмени?\nA. Пощастило\nB. Заздрю\nC. Надихає\nD. Хочу так!",
        "4. Рішення?\nA. Чекаю інструкцій\nB. Потрібна підтримка\nC. Інтуїтивно\nD. Швидко сам",
        "5. Гроші та час?\nA. Відпочивати\nB. Шукати заняття\nC. Досліджувати\nD. Відкривати справу",
        "6. Рутина?\nA. Люблю\nB. Терплю\nC. Важко\nD. Ненавиджу",
        "7. Що важливіше?\nA. Стабільність\nB. Баланс\nC. Реалізація\nD. Свобода"
    ]
    
    # Проверяем ответ
    if answer in ['A', 'B', 'C', 'D']:
        # Добавляем баллы
        scores = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        user_scores[user_id]['score'] += scores[answer]
        
        # Переходим к следующему вопросу
        current_q = user_scores[user_id]['question']
        
        if current_q <= 6:
            # Отправляем следующий вопрос
            keyboard = [['A', 'B'], ['C', 'D']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            update.message.reply_text(questions[current_q - 1], reply_markup=reply_markup)
            user_scores[user_id]['question'] += 1
        else:
            # Все вопросы отвечены - показываем результат
            score = user_scores[user_id]['score']
            
            # Определяем результат
            if score <= 11:
                result = "🔸 Тобі не потрібен бізнес"
            elif score <= 17:
                result = "🟠 Ти ще у пошуку"
            elif score <= 23:
                result = "🟡 У тебе є потенціал!"
            else:
                result = "🟢 Бізнес — твоє природнє середовище!"
            
            update.message.reply_text(
                f"📊 Твій результат: {score} балів\n\n{result}\n\n"
                f"Напиши /start щоб пройти знову"
            )
            
            # Удаляем данные пользователя
            del user_scores[user_id]
    else:
        update.message.reply_text("Будь ласка, обирай A, B, C або D")

# Основная функция
def main():
    # Создаем бота
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    # Запускаем бота
    print("🤖 Бот запускається...")
    updater.start_polling()
    updater.idle()

# Запуск
if __name__ == '__main__':
    main()
