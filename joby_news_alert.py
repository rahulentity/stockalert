import feedparser
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time

# ==== SETTINGS ====
NEWS_FEED_URL = "https://news.google.com/rss/search?q=Joby+Aviation&hl=en-US&gl=US&ceid=US:en"

# Email
SENDER_EMAIL = "rahulentity5@gmail.com"
SENDER_PASSWORD = "vcxg mhpi qefr jntr"   # Gmail App Password
RECEIVER_EMAIL = "a34k92k346@pomail.net"

# Pushover
PUSHOVER_TOKEN = "atipnrf5hi5uov8ziaqw8fg38ckqgw"
PUSHOVER_USER = "us7hz9nakfggsqh3s8ayn5wh92r6gg"

# Telegram
BOT_TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_chat_id"  # e.g. from @userinfobot


# ==== FUNCTIONS ====

def get_latest_joby_news():
    feed = feedparser.parse(NEWS_FEED_URL)
    if not feed.entries:
        return None

    # Sort by published date (most recent first)
    latest_entry = sorted(
        feed.entries,
        key=lambda x: x.get("published_parsed", time.gmtime(0)),
        reverse=True
    )[0]

    # Format single latest article
    article = f"{latest_entry.title}\n{latest_entry.link}\nPublished: {latest_entry.published}\n"
    return article


def send_email(news_content):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "[High Importance] Latest Joby Aviation News"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    part = MIMEText(news_content, "plain")
    msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


def send_pushover_alert(news_content):
    response = requests.post("https://api.pushover.net/1/messages.json", data={
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "priority": 2,              # 🚨 Emergency
        "retry": 60,                # retry every 60 seconds
        "expire": 3600,             # keep retrying for 1 hour
        "sound": "Alarm",      # 🔊 louder & repeating sound
        "title": "🚨 Joby Aviation Breaking News",
        "message": news_content[:1000]  # limit length
    })
    print("📱 Pushover alert sent:", response.status_code)


def send_telegram_alert(news_content):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": news_content})
    print("📲 Telegram alert sent:", response.status_code)


# ==== MAIN ====
if __name__ == "__main__":
    news = get_latest_joby_news()
    if news:
        print(news)

        # Send Email (optional)
        # send_email(news)

        # Send Pushover
        send_pushover_alert(news)

        # Send Telegram (optional)
        # send_telegram_alert(news)

    else:
        print("No news found.")
