import asyncio
import sqlite3
import os
from threading import Thread
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# --- 1. RENDER PORT FIX (Flask Server) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    # Render requires binding to a port (usually 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURATION ---
TOKEN = "8210189223:AAEw2i5wWPlzMTIAv4xkYp7Z4op_2DtbkuU"
ADMIN_ID = 5972327273 # Numeric ID (No quotes)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- 3. DATABASE SETUP ---
# check_same_thread=False is required when using Flask threads
db = sqlite3.connect("movies.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id TEXT PRIMARY KEY,
    file_id TEXT
)
""")
db.commit()

# --- 4. BOT HANDLERS ---

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "🎬 Mister Kino Botga xush kelibsiz!\n\n"
        "Kino raqamini yozing (masalan: 233)\n"
        "Admin kino qo‘shish: `/add RAQAM FILE_ID`",
        parse_mode="Markdown"
    )

@dp.message(F.text.startswith("/add"))
async def add_movie(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Siz admin emassiz")
        return

    try:
        # Splits "/add 123 abc_file_id" into 3 parts
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            raise ValueError
        
        movie_id = parts[1]
        file_id = parts[2]

        cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (movie_id, file_id))
        db.commit()
        await message.answer(f"✅ Kino {movie_id} muvaffaqiyatli qo‘shildi!")
    except Exception:
        await message.answer("❌ Xato! Format: `/add RAQAM FILE_ID`")

@dp.message(F.text) # Only process messages that contain text
async def get_movie(message: types.Message):
    movie_id = message.text.strip()
    
    # Check database
    cursor.execute("SELECT file_id FROM movies WHERE id=?", (movie_id,))
    result = cursor.fetchone()

    if result:
        try:
            await message.answer_video(
                video=result[0],
                caption=f"🎥 Kino ID: {movie_id}"
            )
        except Exception as e:
            await message.answer(f"❌ Kinoni yuborishda xatolik: {e}")
    else:
        # Only reply if the user typed a short code/number
        if len(movie_id) < 10:
            await message.answer("❌ Bunday raqamdagi kino topilmadi")

# --- 5. EXECUTION ---
async def main():
    # Start Flask in background
    Thread(target=run_web, daemon=True).start()
    # Start Polling
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
