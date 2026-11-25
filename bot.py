
import asyncio
import html
import logging
import os
import random
import sys
import traceback

import httpx
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


# =========================
# تنظیمات
# =========================

TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

HTTP = None
bot = None
dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("telegram_game_bot")


# =========================
# کارت‌های بازی
# =========================

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

PENALTY = "😈 اگه کارت رو انجام ندی، باید از همه اسپنک بخوری!"


# =========================
# ارتباط با Supabase
# =========================

def db_headers(prefer=None):
    headers = {
        "apikey": SUPABASE_SECRET_KEY,
        "Content-Type": "application/json",
    }

    if prefer:
        headers["Prefer"] = prefer

    return headers


async def db_request(
    method,
    table,
    params=None,
    payload=None,
    prefer=None,
):
    if HTTP is None:
        raise RuntimeError("اتصال HTTP دیتابیس آماده نیست.")

    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL تنظیم نشده است.")

    response = await HTTP.request(
        method,
        f"{SUPABASE_URL}/rest/v1/{table}",
        params=params,
        json=payload,
        headers=db_headers(prefer),
    )

    if not response.is_success:
        logger.error(
            "Supabase error | status=%s | method=%s | table=%s | response=%s",
            response.status_code,
            method,
            table,
            response.text,
        )
        response.raise_for_status()

    if response.content:
        return response.json()

    return None


async def players(chat_id):
    rows = await db_request(
        "GET",
        "players",
        params={
            "select": "user_id,name,team",
            "chat_id": f"eq.{chat_id}",
        },
    )

    return [
        {
            "id": int(row["user_id"]),
            "name": row["name"],
            "team": row["team"],
        }
        for row in (rows or [])
    ]


async def active(chat_id):
    rows = await db_request(
        "GET",
        "games",
        params={
            "select": "active",
            "chat_id": f"eq.{chat_id}",
            "limit": "1",
        },
    )

    return bool(rows and rows[0]["active"])


async def set_active(chat_id, value):
    rows = await db_request(
        "PATCH",
        "games",
        params={
            "chat_id": f"eq.{chat_id}",
        },
        payload={
            "active": value,
        },
        prefer="return=representation",
    )

    if not rows:
        await db_request(
            "POST",
            "games",
            params={
                "on_conflict": "chat_id",
            },
            payload={
                "chat_id": chat_id,
                "active": value,
            },
            prefer="resolution=merge-duplicates,return=representation",
        )

    if await active(chat_id) != value:
        raise RuntimeError("ذخیره وضعیت بازی ناموفق بود.")


async def valid_game(chat_id):
    members = await players(chat_id)

    if len(members) != 4:
        return False

    teams = [p["team"] for p in members]

    return (
        teams.count(1) == 2
        and teams.count(2) == 2
    )


async def stop_if_incomplete(chat_id):
    if await active(chat_id) and not await valid_game(chat_id):
        await set_active(chat_id, False)
        return True

    return False


async def delete_player(chat_id, user_id):
    await db_request(
        "DELETE",
        "players",
        params={
            "chat_id": f"eq.{chat_id}",
            "user_id": f"eq.{user_id}",
        },
        prefer="return=minimal",
    )


# =========================
# ابزارهای عمومی
# =========================

def group_only(message):
    return message.chat.type in ("group", "supergroup")


def safe_name(name):
    return html.escape(name or "بدون نام")


async def is_admin(message):
    if not message.from_user:
        return False

    member = await bot.get_chat_member(
        message.chat.id,
        message.from_user.id,
    )

    return member.status in ("administrator", "creator")


def next_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎲 کارت بعدی",
                    callback_data="next_card",
                )
            ]
        ]
    )


# =========================
# ارسال کارت
# =========================

async def send_card(chat_id):
    members = await players(chat_id)

    if not await valid_game(chat_id):
        await bot.send_message(
            chat_id,
            "برای بازی دقیقاً ۴ نفر و ۲ نفر در هر تیم لازم است.",
        )
        return

    category = random.choice(list(CARDS.keys()))
    card = random.choice(CARDS[category])

    if category == "چالش زوجی":
        team_no = random.choice([1, 2])

        selected = [
            p for p in members
            if p["team"] == team_no
        ]

        target = (
            "زوج "
            + str(team_no)
            + ": "
            + " و ".join(
                safe_name(p["name"])
                for p in selected
            )
        )

    else:
        selected = random.choice(members)
        target = safe_name(selected["name"])

    await bot.send_message(
        chat_id,
        f"🎯 <b>{category}</b>\n"
        f"👤 نوبت: <b>{target}</b>\n\n"
        f"🃏 {html.escape(card)}\n\n"
        f"{PENALTY}",
        reply_markup=next_keyboard(),
    )


# =========================
# دستورات ربات
# =========================

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
        "انتخاب تیم: /team 1 یا /team 2\n"
        "وضعیت: /status\n"
        "راهنما: /help"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    if not group_only(message):
        return

    await message.answer(
        "<b>دستورهای بازی</b>\n\n"
        "/join — عضویت\n"
        "/leave — خروج از بازی\n"
        "/remove — حذف فرد با ریپلای (فقط مدیر)\n"
        "/team 1 — تیم اول\n"
        "/team 2 — تیم دوم\n"
        "/status — وضعیت بازیکنان\n"
        "/begin — شروع بازی\n"
        "/next — کارت بعدی\n"
        "/stop — توقف بازی\n"
        "/reset — پاک‌سازی کامل اعضا (فقط مدیر)"
    )


# =========================
# عضویت
# =========================

@dp.message(Command("join"))
async def join(message: Message):
    if not group_only(message) or not message.from_user:
        return

    chat_id = message.chat.id
    user = message.from_user

    existing = await db_request(
        "GET",
        "players",
        params={
            "select": "user_id",
            "chat_id": f"eq.{chat_id}",
            "user_id": f"eq.{user.id}",
            "limit": "1",
        },
    )

    if existing:
        await message.answer(
            "قبلاً عضو بازی هستی. برای تغییر تیم از /team استفاده کن."
        )
        return

    current = await players(chat_id)

    if len(current) >= 4:
        await message.answer("ظرفیت بازی تکمیل است.")
        return

    await db_request(
        "POST",
        "players",
        payload={
            "chat_id": chat_id,
            "user_id": user.id,
            "name": user.full_name,
            "team": None,
        },
        prefer="return=minimal",
    )

    await stop_if_incomplete(chat_id)

    await message.answer(
        f"✅ {safe_name(user.full_name)} عضو شد.\n"
        "حالا تیمت را با /team 1 یا /team 2 انتخاب کن."
    )


# =========================
# خروج از بازی
# =========================

@dp.message(Command("leave"))
async def leave(message: Message):
    if not group_only(message) or not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    current = await db_request(
        "GET",
        "players",
        params={
            "select": "user_id",
            "chat_id": f"eq.{chat_id}",
            "user_id": f"eq.{user_id}",
            "limit": "1",
        },
    )

    if not current:
        await message.answer("عضو بازی نیستی.")
        return

    await delete_player(chat_id, user_id)

    stopped = await stop_if_incomplete(chat_id)

    text = "از بازی خارج شدی. ✅"

    if stopped:
        text += "\n⏹ بازی به دلیل تغییر اعضا متوقف شد."

    await message.answer(text)


# =========================
# حذف بازیکن توسط مدیر
# =========================

@dp.message(Command("remove"))
async def remove(message: Message):
    if not group_only(message):
        return

    if not await is_admin(message):
        await message.answer(
            "⛔ فقط مدیر گروه می‌تواند بازیکن حذف کند."
        )
        return

    target_id = None

    if (
        message.reply_to_message
        and message.reply_to_message.from_user
    ):
        target_id = message.reply_to_message.from_user.id

    else:
        parts = (message.text or "").split()

        if len(parts) == 2 and parts[1].isdigit():
            target_id = int(parts[1])

    if target_id is None:
        await message.answer(
            "برای حذف، روی پیام فرد ریپلای کن و بنویس /remove\n"
            "یا شناسه عددی او را وارد کن:\n"
            "/remove USER_ID"
        )
        return

    current = await db_request(
        "GET",
        "players",
        params={
            "select": "user_id,name",
            "chat_id": f"eq.{message.chat.id}",
            "user_id": f"eq.{target_id}",
            "limit": "1",
        },
    )

    if not current:
        await message.answer("این فرد عضو بازی نیست.")
        return

    await delete_player(message.chat.id, target_id)

    stopped = await stop_if_incomplete(message.chat.id)

    text = (
        f"🗑 {safe_name(current[0]['name'])} "
        "از بازی حذف شد."
    )

    if stopped:
        text += "\n⏹ بازی به دلیل تغییر اعضا متوقف شد."

    await message.answer(text)


# =========================
# انتخاب تیم
# =========================

@dp.message(Command("team"))
async def choose_team(message: Message):
    if not group_only(message) or not message.from_user:
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or parts[1] not in ("1", "2"):
        await message.answer(
            "فرمت صحیح: /team 1 یا /team 2"
        )
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    team_no = int(parts[1])

    exists = await db_request(
        "GET",
        "players",
        params={
            "select": "user_id,team",
            "chat_id": f"eq.{chat_id}",
            "user_id": f"eq.{user_id}",
            "limit": "1",
        },
    )

    if not exists:
        await message.answer("اول /join را بزن.")
        return

    if exists[0]["team"] == team_no:
        await message.answer(
            f"همین الان عضو تیم {team_no} هستی."
        )
        return

    team_members = await db_request(
        "GET",
        "players",
        params={
            "select": "user_id",
            "chat_id": f"eq.{chat_id}",
            "team": f"eq.{team_no}",
            "user_id": f"neq.{user_id}",
        },
    )

    if len(team_members or []) >= 2:
        await message.answer(
            "این تیم تکمیل است. تیم دیگر را انتخاب کن."
        )
        return

    await db_request(
        "PATCH",
        "players",
        params={
            "chat_id": f"eq.{chat_id}",
            "user_id": f"eq.{user_id}",
        },
        payload={
            "team": team_no,
        },
        prefer="return=minimal",
    )

    await message.answer(
        f"تیم {team_no} برایت ثبت شد. ✅"
    )


# =========================
# وضعیت بازی
# =========================

@dp.message(Command("status"))
async def status(message: Message):
    if not group_only(message):
        return

    chat_id = message.chat.id
    members = await players(chat_id)

    lines = ["<b>وضعیت بازی</b>"]

    for team_no in (1, 2):
        names = [
            safe_name(p["name"])
            for p in members
            if p["team"] == team_no
        ]

        lines.append(
            f"تیم {team_no}: "
            + (", ".join(names) or "—")
        )

    unassigned = [
        safe_name(p["name"])
        for p in members
        if p["team"] is None
    ]

    if unassigned:
        lines.append(
            "بدون تیم: " + ", ".join(unassigned)
        )

    lines.append(
        f"تعداد اعضا: {len(members)}/4"
    )

    lines.append(
        "وضعیت اجرا: "
        + (
            "🔥 فعال"
            if await active(chat_id)
            else "⏹ متوقف"
        )
    )

    await message.answer("\n".join(lines))


# =========================
# شروع بازی
# =========================

@dp.message(Command("begin"))
async def begin(message: Message):
    if not group_only(message):
        return

    chat_id = message.chat.id

    if not await valid_game(chat_id):
        await message.answer(
            "برای شروع، ۴ عضو و ۲ نفر در هر تیم لازم است. /status"
        )
        return

    try:
        await set_active(chat_id, True)

    except Exception:
        logger.exception("Could not activate game")

        await message.answer(
            "❌ ذخیره وضعیت بازی ناموفق بود."
        )
        return

    await message.answer("🔥 بازی شروع شد!")

    await send_card(chat_id)


# =========================
# کارت بعدی
# =========================

@dp.message(Command("next"))
async def next_command(message: Message):
    if not group_only(message):
        return

    if not await active(message.chat.id):
        await message.answer(
            "بازی فعال نیست. اول /begin را بزن."
        )
        return

    await send_card(message.chat.id)


# =========================
# توقف بازی
# =========================

@dp.message(Command("stop"))
async def stop(message: Message):
    if not group_only(message):
        return

    await set_active(message.chat.id, False)

    await message.answer("⏹ بازی متوقف شد.")


# =========================
# پاک‌سازی کامل توسط مدیر
# =========================

@dp.message(Command("reset"))
async def reset(message: Message):
    if not group_only(message):
        return

    if not await is_admin(message):
        await message.answer(
            "⛔ فقط مدیر گروه می‌تواند بازی را پاک‌سازی کند."
        )
        return

    chat_id = message.chat.id

    await set_active(chat_id, False)

    await db_request(
        "DELETE",
        "players",
        params={
            "chat_id": f"eq.{chat_id}",
        },
        prefer="return=minimal",
    )

    await message.answer(
        "♻️ بازی پاک‌سازی شد.\n"
        "تمام اعضا حذف شدند و بازی متوقف است.\n"
        "برای شروع مجدد، همه باید /join بزنند."
    )


# =========================
# دکمه کارت بعدی
# =========================

@dp.callback_query(F.data == "next_card")
async def next_button(callback: CallbackQuery):
    if not callback.message:
        await callback.answer()
        return

    chat_id = callback.message.chat.id

    if not await active(chat_id):
        await callback.answer(
            "بازی فعال نیست.",
            show_alert=True,
        )
        return

    await callback.answer()

    await send_card(chat_id)


# =========================
# راه‌اندازی اصلی
# =========================

async def main():
    global HTTP, bot

    logger.info("Starting Telegram Game Bot...")

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN تنظیم نشده است."
        )

    if not SUPABASE_URL:
        raise RuntimeError(
            "SUPABASE_URL تنظیم نشده است."
        )

    if not SUPABASE_SECRET_KEY:
        raise RuntimeError(
            "SUPABASE_SECRET_KEY تنظیم نشده است."
        )

    logger.info("Environment variables are present.")

    HTTP = httpx.AsyncClient(
        timeout=httpx.Timeout(20.0)
    )

    bot = Bot(
        TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        ),
    )

    try:
        # بررسی اتصال تلگرام
        logger.info("Checking Telegram connection...")

        me = await bot.get_me()

        logger.info(
            "Telegram connection OK. Bot username: @%s",
            me.username,
        )

        # بررسی اتصال Supabase
        logger.info("Checking Supabase players table...")

        await db_request(
            "GET",
            "players",
            params={
                "select": "user_id",
                "limit": "1",
            },
        )

        logger.info("Players table connection OK.")

        logger.info("Checking Supabase games table...")

        await db_request(
            "GET",
            "games",
            params={
                "select": "chat_id,active",
                "limit": "1",
            },
        )

        logger.info("Games table connection OK.")

        logger.info("All checks passed.")
        logger.info("Telegram bot is starting polling.")

        await dp.start_polling(bot)

    finally:
        logger.info("Closing connections...")

        if HTTP is not None:
            await HTTP.aclose()

        if bot is not None:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")

    except Exception:
        logger.critical(
            "BOT STARTUP OR RUNTIME FAILED:"
        )
        traceback.print_exc()
        sys.exit(1)
