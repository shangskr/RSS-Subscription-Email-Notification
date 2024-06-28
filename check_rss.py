import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json

# 配置邮件发送
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')

# 读取RSS链接
RSS_FEEDS = [
    'https://hexo.shangskr.top/atom.xml'
]

# 读取上一次检查的时间戳
def load_last_check():
    if os.path.exists('last_check.json'):
        with open('last_check.json', 'r') as f:
            return json.load(f)
    return {}

# 保存最新的时间戳
def save_last_check(last_check):
    with open('last_check.json', 'w') as f:
        json.dump(last_check, f)

# 发送邮件
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USER, TO_EMAIL, text)

# 检查RSS变动
def check_rss():
    last_check = load_last_check()
    new_last_check = {}
    new_posts = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            latest_entry = feed.entries[0]
            new_last_check[feed_url] = latest_entry.published

            if feed_url in last_check:
                if latest_entry.published > last_check[feed_url]:
                    new_posts.append((feed_url, latest_entry))
            else:
                new_posts.append((feed_url, latest_entry))

    save_last_check(new_last_check)

    if new_posts:
        for feed_url, entry in new_posts:
            subject = f"New post in {feed_url}"
            body = f"New post titled '{entry.title}' at {feed_url}\n\nLink: {entry.link}"
            send_email(subject, body)

if __name__ == "__main__":
    check_rss()
