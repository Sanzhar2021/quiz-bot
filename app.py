import os
import json
import re
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import io, sys
import telebot
from dotenv import load_dotenv

# Force stdout to UTF-8 (Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Настройка Flask и базы данных
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///results.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # токен вашего Telegram бота
WEBHOOK_PATH = "/webhook"

bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Модель базы данных для хранения результатов
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(80), nullable=False)
    student_group = db.Column(db.String(80), nullable=True)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Result {self.student_name} - {self.score}>'

with app.app_context():
    db.create_all()

# Настройка API-ключа Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # используем .env
except Exception as e:
    print(f"Ошибка при настройке API-ключа: {e}")

model = genai.GenerativeModel('gemini-2.5-flash')

# Основной маршрут для студента
@app.route('/')
def index():
    return render_template('index.html')

# Маршрут для преподавателя
@app.route('/teacher')
def teacher_dashboard():
    results = Result.query.order_by(Result.timestamp.desc()).all()
    grouped_results = {}
    for res in results:
        grouped_results.setdefault(res.student_group, []).append(res)
    return render_template('teacher.html', grouped_results=grouped_results)

# Генерация тестов
@app.route('/generate_test', methods=['POST'])
def generate_test():
    try:
        data = request.json
        document_text = data.get('text')
        if not document_text:
            return jsonify({"error": "No text provided"}), 400

        prompt = f"""
        На основе следующего текста сгенерируй 20 тестовых вопросов с 4 вариантами ответа, где только один правильный.
        Ответ должен быть строго в формате JSON. Каждый вопрос должен быть объектом с полями:
        - "question"
        - "options"
        - "correct_option"
        Начни свой ответ сразу с JSON-массива.
        Текст:
        {document_text}
        """
        response = model.generate_content(prompt)
        generated_text = response.text

        match = re.search(r'\[.*\]', generated_text, re.DOTALL)
        if not match:
            return jsonify({"error": "Failed to parse JSON from AI response.", "ai_response": generated_text}), 500

        questions = json.loads(match.group(0))
        return jsonify({"success": True, "questions": questions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Сохранение результатов
@app.route('/save_result', methods=['POST'])
def save_result():
    try:
        data = request.json
        student_name = data.get('name')
        student_group = data.get('group', 'Без группы')
        score = data.get('score')
        if not student_name or score is None:
            return jsonify({"error": "Name or score is missing"}), 400

        new_result = Result(student_name=student_name, student_group=student_group, score=score)
        db.session.add(new_result)
        db.session.commit()
        return jsonify({"success": True, "message": "Result saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Telegram Webhook ----------
@app.route(WEBHOOK_PATH, methods=['POST'])
def telegram_webhook():
    try:
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# Пример команды бота
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Привет! Я бот для тестов.")

# ---------- Запуск Flask ----------
if __name__ == "__main__":
    if os.getenv("RENDER"):  # признак, что мы на Render
        app.run(host="0.0.0.0", port=5000)
    else:
        # Локальный запуск с HTTPS (mkcert)
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            ssl_context=("localhost+2.pem", "localhost+2-key.pem")
        )
