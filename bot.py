import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    logger.error("❌ Токен не найден! Установите переменную BOT_TOKEN в Render")
    exit(1)

# Этапы разговора
QUESTION = 1

# Вопросы теста (упрощенная версия)
QUESTIONS = [
    "🧭 ТЕСТ: Твій шлях — власна справа чи стабільна робота?\n\n"
    "1. Що ти відчуваєш на роботі?\n"
    "A. Втома, нудьга\n"
    "B. Нормально, але мрію про більше\n"
    "C. Подобається, але хочеться змін\n"
    "D. Люблю свою роботу",
    
    "2. Як ти ставишся до ризиків?\n"
    "A. Лякають\n"
    "B. Не люблю\n"
    "C. У міру\n"
    "D. Спокійно",
    
    "3. Що відчуваєш, коли бачиш бізнесмена?\n"
    "A. Йому пощастило\n"
    "B. Заздрю\n"
    "C. Надихає\n"
    "D. Хочу так само!",
    
    "4. Як приймаєш рішення?\n"
    "A. Чекаю інструкцій\n"
    "B. Потрібна підтримка\n"
    "C. Інтуїтивно\n"
    "D. Швидко сам(а)",
    
    "5. Що робитимеш з грошима та часом?\n"
    "A. Відпочивати\n"
    "B. Шукати заняття\n"
    "C. Досліджувати ідеї\n"
    "D. Відкривати справу",
    
    "6. Як до рутини?\n"
    "A. Люблю\n"
    "B. Терплю\n"
    "C. Важко\n"
    "D. Ненавиджу",
    
    "7. Що важливіше?\n"
    "A. Стабільність\n"
    "B. Баланс\n"
    "C. Реалізація\n"
    "D. Свобода"
]

# Результаты
RESULTS = {
    (7, 11): "🔸 Тобі не потрібен бізнес.\n✨ Спробуй змінити роботу, а не життя.",
    (12, 17): "🟠 Ти ще у пошуку.\n✨ Пробуй підробітки та навчання.",
    (18, 23): "🟡 У тебе є потенціал!\n✨ Починай будувати свою справу.",
    (24, 28): "🟢 Бізнес — твоє природнє середовище!\n✨ Дій прямо зараз!"
}

# Хранилище пользователей
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {'score': 0, 'question': 0}
    
    await update.message.reply_text(
        "🔹 Обери одну відповідь\n🔹 В кінці буде результат\n\nПочинаємо!"
    )
    
    # Отправляем первый вопрос
    await send_question(update, user_id)
    return QUESTION

async def send_question(update: Update, user_id: int):
    data = user_data[user_id]
    question_num = data['question']
    
    if question_num < len(QUESTIONS):
        keyboard = [['A', 'B'], ['C', 'D']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(QUESTIONS[question_num], reply_markup=reply_markup)
    else:
        # Все вопросы отвечены
        await show_result(update, user_id)
        return ConversationHandler.END

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("Напиши /start щоб почати")
        return ConversationHandler.END
    
    answer = update.message.text.upper()
    
    if answer in ['A', 'B', 'C', 'D']:
        # Подсчет баллов
        scores = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
        user_data[user_id]['score'] += scores[answer]
        user_data[user_id]['question'] += 1
        
        # Отправляем следующий вопрос
        await send_question(update, user_id)
        return QUESTION
    else:
        await update.message.reply_text("Будь ласка, обирай A, B, C або D")
        return QUESTION

async def show_result(update: Update, user_id: int):
    score = user_data[user_id]['score']
    
    # Определяем результат
    result_text = ""
    for (min_s, max_s), text in RESULTS.items():
        if min_s <= score <= max_s:
            result_text = text
            break
    
    await update.message.reply_text(
        f"📊 Твій результат: {score} балів\n\n{result_text}\n\n/start - пройти знову"
    )
    
    # Очищаем данные
    if user_id in user_data:
        del user_data[user_id]

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data:
        del user_data[user_id]
    
    await update.message.reply_text("Тест скасовано. /start - почати знову")
    return ConversationHandler.END

def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Создаем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    
    # Запускаем бота
    logger.info("🤖 Бот запускається...")
    print("Бот працює! Чекаю повідомлень...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
