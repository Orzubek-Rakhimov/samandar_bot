import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# ==================================
# ⚡ Telegram bot token va admin ID
TOKEN = "8210189223:AAEw2i5wWPlzMTIAv4xkYp7Z4op_2DtbkuU"
ADMIN_ID = " 5972327273 "# O'zingning Telegram ID
# ==================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==================================
# 🗂 SQLite baza yaratish / ulanadi
db = sqlite3.connect("movies.db")
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id TEXT PRIMARY KEY,   -- foydalanuvchi yozadigan raqam
    file_id TEXT           -- Telegram file_id
)
""")
db.commit()
# ==================================

# =============================
# /start buyrug‘i
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "🎬 Mister Kino Botga xush kelibsiz!\n\n"
        "Kino raqamini yozing (masalan: 233)\n"
        "Admin kino qo‘shish: /add RAQAM FILE_ID"
    )

# =============================
# 👑 Admin kino qo‘shadi
@dp.message(lambda m: m.text.startswith("/add"))
async def add_movie(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Siz admin emassiz")
        return

    try:
        _, movie_id, file_id = message.text.split(maxsplit=2)
        cursor.execute(
            "INSERT OR REPLACE INTO movies VALUES (?, ?)",
            (movie_id, file_id)
        )
        db.commit()
        await message.answer(f"✅ Kino {movie_id} qo‘shildi")
    except:
        await message.answer("❌ Format: /add RAQAM FILE_ID")

# =============================
# 🎬 Foydalanuvchi raqam yozsa
@dp.message()
async def get_movie(message: types.Message):
    movie_id = message.text.strip()
    cursor.execute("SELECT file_id FROM movies WHERE id=?", (movie_id,))
    result = cursor.fetchone()

    if result:
        await message.answer_video(
            video=result[0],
            caption=f"🎥 Kino ID: {movie_id}"
        )
    else:
        await message.answer("❌ Kino topilmadi")

# =============================
# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
