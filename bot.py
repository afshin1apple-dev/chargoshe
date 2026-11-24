
import asyncio
import os
import random
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = os.getenv("BOT_TOKEN")
DB = sqlite3.connect("game.db", check_same_thread=False)

CARDS = {
    "حقیقت": [
        "دوست داری برات بخوره یا براش بخوری",
        "کجای بدنتو بیشتر دوستداری",
        "دوست داری شرت مذکر گروه روبه‌رو را رو در بیاری؟",
        "دوستداری سوتین گروه مقابل را دربیاری؟",
        "مست هستی ؟ اگه نه یک پیک بخور",
        "از اخرین دیدار گروهی یه خاطره خفن بگو",
        "از چی پارتنرت خیلی خوشت میاد ؟",
        "خودتو سکسی توصیف کن",
        "یه خواسته پارتنر زوج مقابل بخواه",
        "چه چیزی تو پارتنرت برات خیلی جذابه",
        "دوست داری الان بری تو اتاق با پارتنرت 😉",
        "یک کونی در جمع معرفی کن",
    ],
    "جرئت": [
        "از پارتنرت لب بگیر",
        "یک تکه بکن",
        "هر جاشو دوس داره بخور براش",
        "یک پیک بخور",
        "یکاری کن حشری بشه",
        "با رقص یه تیکه بکن",
        "باید بقیه رو به صورت تک نفره بخندونی وگر نه یه پیک بخور",
        "چشم بند بزن بین بقیه به یه نفر دست بزن باید یه تیکه به انتخابش بکنی",
        "هیدن گوشی تو همه ببینن",
        "چشم بزار بقیه قایم شن اولین نفرو که پیدا کردی باید یه تیکه ازش بکنی",
        "چشم بند بزن هر کی یه جاتو نیشگون میگیره اگه درست تشخیص دادی کی بود جاتو باهاش عوض کن",
        "یه چی بزن روش بخور 😁",
        "با اهنگ غمگین شاد برقص",
        "یه جریمه برای نفر سمت راستی بگو",
        "یه جریمه برا نفر سمت چپ بگو",
        "یه جریمه برای دختر رو به رو بگو",
        "یه جریمه واسه پسر رو به رو بگو",
        "یه پول به حساب پارتنرت واریز کن زیر ۵۰۰/۰۰۰ قبول نی",
    ],
    "چالش شخصی": [
        "۳۰ ثانیه با نگاه اغواگرانه به انتخاب گروه نگاه کن.",
        "یه فانتزی سکسی‌ت رو بگو.",
        "با صدای آروم و اغواگرانه یک جمله برای پارتنرت بگو.",
        "سه ویژگی سکسی خودت رو نام ببر.",
        "یکی از افراد گروه رو انتخاب کن و ازش یک سؤال جسورانه بپرس.",
        "یک رقص خصوصی ۳۰ ثانیه‌ای اجرا کن.",
        "صدای سکست رو بلند تو جمع دربیار.",
        "اجازه بده گروه برایت یک لقب سکسی انتخاب کنه.",
        "یک صحنه سکسی بدون حرف زدن فقط با خودت با آه و ناله بازی کن.",
        "از بین سه نفر، جذاب‌ترین استایل رو انتخاب کن و دلیلش رو بگو.",
        "یک راز خجالت‌آور درباره روابطت تعریف کن.",
        "پارتنرت رو با پنج کلمه توصیف کن؛ حق مکث نداری!",
        "به انتخاب گروه برای پارتنرت یکاری کن",
    ],
    "چالش زوجی": [
        "یک فانتزی مشترک‌تون رو به‌صورت نمایشی و با رضایت هر دو اجرا کنید.",
        "یکی از زوج‌ها چشم‌هاش رو ببنده و دیگری با لمس دستش رو راهنمایی کنه.",
        "هر کدوم یک خواسته از طرف مقابل مطرح کنید و در صورت رضایت، همون لحظه انجامش بدید.",
        "هر کدوم یک نقطه از بدن طرف مقابل رو که دوست دارید انتخاب کنید و دلیلش رو بگید.",
        "یکی از زوج‌ها باید دیگری رو با یک جمله حسابی تحریک کنه.",
        "یک دقیقه ادای یک رابطه خودتون رو دربیارید.",
        "زوج‌ها یک سناریوی سکسی طراحی و اجرا کنن.",
        "به انتخاب زوج مقابل یک کار سکسی دونفره انجام بدید.",
        "هر نفر یک درخواست از پارتنرش مطرح کنه؛ اگر هر دو موافق بودند اجراش کنند.",
        "زوج مقابل برای هر زوج یک سناریوی سکسی انتخاب کنه تا به شکل نمایشی اجراش کن",
    ],
}

DB.execute("""
CREATE TABLE IF NOT EXISTS players (
    chat_id INTEGER,
    user_id INTEGER,
    name TEXT,
    team INTEGER,
    PRIMARY KEY(chat_id, user_id)
)
""")
DB.execute("""
CREATE TABLE IF NOT EXISTS games (
    chat_id INTEGER PRIMARY KEY,
    active INTEGER DEFAULT 0
)
""")
DB.commit()

bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


def group_only(message):
    return message.chat.type in ("group", "supergroup")


def players(chat_id):
    rows = DB.execute(
        "SELECT user_id, name, team FROM players WHERE chat_id=?",
        (chat_id,)
    ).fetchall()
    return [
        {"id": r[0], "name": r[1], "team": r[2]}
        for r in rows
    ]


def active(chat_id):
    row = DB.execute(
        "SELECT active FROM games WHERE chat_id=?",
        (chat_id,)
    ).fetchone()
    return bool(row and row[0])


def set_active(chat_id, value):
    DB.execute(
        "INSERT INTO games(chat_id, active) VALUES(?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET active=excluded.active",
        (chat_id, int(value))
    )
    DB.commit()


def safe_name(name):
    return (
        name.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def next_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎲 کارت بعدی",
                    callback_data="next_card"
                )
            ]
        ]
    )


async def send_card(chat_id):
    members = players(chat_id)

    if (
        len(members) != 4
        or sorted(p["team"] for p in members) != [1, 1, 2, 2]
    ):
        await bot.send_message(
            chat_id,
            "برای شروع دقیقاً ۴ نفر و ۲ نفر در هر تیم لازم است."
        )
        return

    category = random.choice(list(CARDS.keys()))
    card = random.choice(CARDS[category])

    if category == "چالش زوجی":
        team_no = random.choice([1, 2])
        selected = [
            p for p in members if p["team"] == team_no
        ]
        target = "زوج " + str(team_no) + ": " + " و ".join(
            safe_name(p["name"]) for p in selected
        )
    else:
        selected = random.choice(members)
        target = safe_name(selected["name"])

    await bot.send_message(
        chat_id,
        f"🎯 <b>{category}</b>\n"
        f"👤 نوبت: <b>{target}</b>\n\n"
        f"🃏 {card}\n\n"
        "🩵 اجرای کارت فقط با رضایت افراد است؛ "
        "هرکس می‌تواند کارت را رد کند.",
        reply_markup=next_keyboard()
    )


@dp.message(Command("start"))
async def start(message: Message):
    if not group_only(message):
        await message.answer(
            "این ربات برای گروه چهارنفره طراحی شده است."
        )
        return

    await message.answer(
        "سلام! 🎲\n"
        "برای عضویت /join را بزنید.\n"
        "برای انتخاب تیم /team 1 یا /team 2\n"
        "راهنما: /help"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    if not group_only(message):
        return

    await message.answer(
        "<b>دستورهای بازی</b>\n"
        "/join — عضویت\n"
        "/team 1 — تیم اول\n"
        "/team 2 — تیم دوم\n"
        "/status — وضعیت بازیکنان\n"
        "/begin — شروع بازی\n"
        "/next — کارت بعدی\n"
        "/stop — توقف بازی"
    )


@dp.message(Command("join"))
async def join(message: Message):
    if not group_only(message) or not message.from_user:
        return

    chat_id = message.chat.id
    user = message.from_user

    exists = DB.execute(
        "SELECT 1 FROM players WHERE chat_id=? AND user_id=?",
        (chat_id, user.id)
    ).fetchone()

    if exists:
        await message.answer("قبلاً عضو شدی.")
        return

    count = DB.execute(
        "SELECT COUNT(*) FROM players WHERE chat_id=?",
        (chat_id,)
    ).fetchone()[0]

    if count >= 4:
        await message.answer("ظرفیت بازی تکمیل است.")
        return

    DB.execute(
        "INSERT INTO players VALUES(?, ?, ?, NULL)",
        (chat_id, user.id, user.full_name)
    )
    DB.commit()

    await message.answer(
        f"✅ {safe_name(user.full_name)} عضو شد. "
        "حالا تیمت را با /team 1 یا /team 2 انتخاب کن."
    )


@dp.message(Command("team"))
async def choose_team(message: Message):
    if not group_only(message) or not message.from_user:
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or parts[1] not in ("1", "2"):
        await message.answer("فرمت: /team 1 یا /team 2")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    team_no = int(parts[1])

    exists = DB.execute(
        "SELECT 1 FROM players WHERE chat_id=? AND user_id=?",
        (chat_id, user_id)
    ).fetchone()

    if not exists:
        await message.answer("اول /join را بزن.")
        return

    count = DB.execute(
        "SELECT COUNT(*) FROM players "
        "WHERE chat_id=? AND team=? AND user_id<>?",
        (chat_id, team_no, user_id)
    ).fetchone()[0]

    if count >= 2:
        await message.answer("این تیم تکمیل است.")
        return

    DB.execute(
        "UPDATE players SET team=? WHERE chat_id=? AND user_id=?",
        (team_no, chat_id, user_id)
    )
    DB.commit()

    await message.answer(f"تیم {team_no} برایت ثبت شد. ✅")


@dp.message(Command("status"))
async def status(message: Message):
    if not group_only(message):
        return

    members = players(message.chat.id)
    lines = ["<b>وضعیت بازی</b>"]

    for team_no in (1, 2):
        names = [
            safe_name(p["name"])
            for p in members if p["team"] == team_no
        ]
        lines.append(
            f"تیم {team_no}: " + (", ".join(names) or "—")
        )

    unassigned = [
        safe_name(p["name"])
        for p in members if p["team"] is None
    ]

    if unassigned:
        lines.append("بدون تیم: " + ", ".join(unassigned))

    lines.append(f"تعداد اعضا: {len(members)}/4")
    await message.answer("\n".join(lines))


@dp.message(Command("begin"))
async def begin(message: Message):
    if not group_only(message):
        return

    members = players(message.chat.id)

    if (
        len(members) != 4
        or sorted(p["team"] for p in members) != [1, 1, 2, 2]
    ):
        await message.answer(
            "برای شروع، ۴ عضو و ۲ نفر در هر تیم لازم است. /status"
        )
        return

    set_active(message.chat.id, True)
    await message.answer("🔥 بازی شروع شد!")
    await send_card(message.chat.id)


@dp.message(Command("next"))
async def next_command(message: Message):
    if not group_only(message):
        return

    if not active(message.chat.id):
        await message.answer("بازی فعال نیست. اول /begin را بزن.")
        return

    await send_card(message.chat.id)


@dp.message(Command("stop"))
async def stop(message: Message):
    if not group_only(message):
        return

    set_active(message.chat.id, False)
    await message.answer("⏹ بازی متوقف شد.")


@dp.callback_query(F.data == "next_card")
async def next_button(callback: CallbackQuery):
    if not callback.message:
        await callback.answer()
        return

    chat_id = callback.message.chat.id

    if not active(chat_id):
        await callback.answer(
            "بازی فعال نیست.",
            show_alert=True
        )
        return

    await callback.answer()
    await send_card(chat_id)


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
