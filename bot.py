import asyncio
import sqlite3
import os
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# --- ВСТАВКА ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
# --------------------------

TOKEN = "8210189223:AAEw2i5wWPlzMTIAv4xkYp7Z4op_2DtbkuU"
ADMIN_ID = 5972327273 # Убрал кавычки и пробелы (ID должен быть int)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных
db = sqlite3.connect("movies.db", check_same_thread=False) # Важно для многопоточности
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS movies (id TEXT PRIMARY KEY, file_id TEXT)")
db.commit()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🎬 Xush kelibsiz!\nKino raqamini yozing.")

@dp.message(lambda m: m.text and m.text.startswith("/add"))
async def add_movie(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split(maxsplit=2)
        movie_id, file_id = parts[1], parts[2]
        cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (movie_id, file_id))
        db.commit()
        await message.answer(f"✅ Добавлено: {movie_id}")
    except Exception:
        await message.answer("❌ Формат: /add RAQAM FILE_ID")

@dp.message()
async def get_movie(message: types.Message):
    cursor.execute("SELECT file_id FROM movies WHERE id=?", (message.text.strip(),))
    result = cursor.fetchone()
    if result:
        await message.answer_video(video=result[0], caption=f"🎥 ID: {message.text}")
    else:
        await message.answer("❌ Не найдено")

async def main():
    # Запускаем Flask в отдельном потоке
    Thread(target=run_web).start()
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
