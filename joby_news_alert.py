import feedparser
import requests
from datetime import datetime
import gspread
from rapidfuzz import fuzz
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

# ==== SETTINGS ====
NEWS_FEED_URL = "https://news.google.com/rss/search?q=Joby+Aviation&hl=en-US&gl=US&ceid=US:en"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ENEUAFY4Que87U4ZTiLoguc4VhAVVc4l4cGyDU5k34Y/edit#gid=0"
SERVICE_ACCOUNT_FILE = "credentials.json"  # JSON key for stocksheet@stockalert-471023.iam.gserviceaccount.com

# Email (optional)
SENDER_EMAIL = "rahulentity5@gmail.com"
SENDER_PASSWORD = "vcxg mhpi qefr jntr"
RECEIVER_EMAIL = "a34k92k346@pomail.net"

# Pushover
PUSHOVER_TOKEN = "atipnrf5hi5uov8ziaqw8fg38ckqgw"
PUSHOVER_USER = "us7hz9nakfggsqh3s8ayn5wh92r6gg"

# Telegram (optional)
BOT_TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_chat_id"

# ==== FUNCTIONS ====

def get_all_joby_news():
    feed = feedparser.parse(NEWS_FEED_URL)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return articles


def init_google_sheet():
    creds = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sheet = creds.open_by_url(SHEET_URL).sheet1
    return sheet


def is_article_new(sheet, article_title, article_link, threshold=85):
    """
    Check if the article is new using both:
    1. Fuzzy title matching
    2. Exact link match
    """
    existing_titles = sheet.col_values(2)  # Title column
    existing_links = sheet.col_values(3)   # Source column

    if article_link in existing_links:
        return False

    for existing in existing_titles:
        similarity = fuzz.token_set_ratio(article_title, existing)
        if similarity >= threshold:
            return False

    return True


def append_to_google_sheet(sheet, article):
    sheet.append_row([article["published"], article["title"], article["link"]])
    print("Added to Google Sheet:", article["title"])


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


def send_telegram_alert(news_content):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": news_content})
    print("📲 Telegram alert sent:", response.status_code)


# ==== MAIN ====
if __name__ == "__main__":
    sheet = init_google_sheet()
    news_list = get_all_joby_news()

    for article in news_list:
        if is_article_new(sheet, article["title"], article["link"]):
            append_to_google_sheet(sheet, article)
            alert_text = f"{article['title']}\n{article['link']}\nPublished: {article['published']}"

            # Send alerts
            send_pushover_alert(alert_text)
            # send_email(alert_text)       # optional
            # send_telegram_alert(alert_text)  # optional
        else:
            print("Already recorded:", article["title"])
