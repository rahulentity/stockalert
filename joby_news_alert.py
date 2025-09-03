import feedparser
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time
from datetime import datetime, timedelta

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

def get_recent_joby_news(minutes=30):
    feed = feedparser.parse(NEWS_FEED_URL)
    if not feed.entries:
        return []

    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    fresh_articles = []

    for entry in feed.entries:
        if hasattr(entry, "published_parsed"):
            published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            if published_time > cutoff:
                article = f"{entry.title}\n{entry.link}\nPublished: {entry.published}\n"
                fresh_articles.append(article)

    return fresh_articles


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
        "priority": 2,
        "retry": 60,
        "expire": 3600,
        "sound": "Alarm",
        "title": "🚨 Joby Aviation Breaking News",
        "message": news_content[:1000]
    })
    print("📱 Pushover alert sent:", response.status_code)


def send_telegram_alert(news_content):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": news_content})
    print("📲 Telegram alert sent:", response.status_code)


# ==== MAIN ====
if __name__ == "__main__":
    news_list = get_recent_joby_news(30)
    if news_list:
        for news in news_list:
            print(news)

            # Send Email (optional)
            # send_email(news)

            # Send Pushover
            send_pushover_alert(news)

            # Send Telegram (optional)
            # send_telegram_alert(news)

    else:
        print("No new news in the last 30 minutes.")
