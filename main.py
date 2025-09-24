import telegram
from telegram.ext import Updater, CommandHandler
import datetime
import csv
import os

# توکن به صورت امن از متغیر محیطی (Environment Variable) خوانده می‌شود
TOKEN = os.environ.get("BOT_TOKEN") 

# مسیر فایل ذخیره داده‌ها
DATA_FILE = "clients.csv"

def generate_client_code():
    # ساخت کد مشتری بر اساس تاریخ و زمان دقیق
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d%H%M%S")

def start(update, context):
    """پاسخ به دستور /start"""
    update.message.reply_text('سلام مشاور عزیز! من ربات ثبت سریع مشتریان شما هستم. برای ثبت مشتری جدید از فرمت زیر استفاده کنید:\n\n/new نام_کامل | شماره_تماس | نوع_نیاز')

def new_client_entry(update, context):
    """پردازش دستور /new و ثبت اطلاعات"""
    
    # جدا کردن متن پیام از دستور /new
    text_data = update.message.text.replace("/new", "", 1).strip()
    
    # بررسی فرمت پیام
    if '|' not in text_data:
        update.message.reply_text("⛔️ فرمت پیام اشتباه است. لطفاً از فرمت زیر استفاده کنید:\n/new نام_کامل | شماره_تماس | نوع_نیاز")
        return

    try:
        # تقسیم اطلاعات بر اساس |
        parts = [part.strip() for part in text_data.split('|', 2)]
        if len(parts) < 3:
            raise ValueError("Not enough parts")
            
        full_name = parts[0]
        phone_number = parts[1]
        need_type = parts[2]
        client_code = generate_client_code()
        
        # ردیف جدید برای ذخیره
        new_row = [client_code, full_name, phone_number, need_type, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        
        # ذخیره در فایل CSV
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # اگر فایل وجود نداره، هدر رو بنویس (فقط برای اولین بار)
            if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
                writer.writerow(['کد مشتری', 'نام کامل', 'شماره تماس', 'نوع نیاز', 'تاریخ ثبت'])
            
            writer.writerow(new_row)
            
        # ارسال پیام تأیید به شما
        reply_message = f"✅ **مشتری ثبت شد!**\n\n"
        reply_message += f"کد مشتری: `{client_code}`\n"
        reply_message += f"نام: **{full_name}**\n"
        reply_message += f"نیاز: **{need_type}**"

        update.message.reply_text(reply_message, parse_mode=telegram.ParseMode.MARKDOWN)

    except Exception as e:
        update.message.reply_text(f"خطایی رخ داد. لطفاً فرمت را دوباره چک کنید.")


def main():
    """تابع اصلی برای راه‌اندازی ربات."""
    # اگر توکن به درستی از Render خوانده نشود، ربات اجرا نخواهد شد
    if not TOKEN:
        print("خطا: BOT_TOKEN پیدا نشد. لطفاً متغیر محیطی را در Render تنظیم کنید.")
        return

    updater = Updater(TOKEN) # <<<< اصلاح خطای use_context
    dp = updater.dispatcher

    # تنظیم Handlerها برای دستورات /start و /new
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("new", new_client_entry))

    # شروع کار ربات و گوش دادن به پیام‌ها
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
