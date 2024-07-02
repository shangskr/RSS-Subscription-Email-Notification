import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
import requests
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
import threading

# 创建保存检查时间文件的目录
os.makedirs('check', exist_ok=True)

# 读取RSS列表
with open('rss_list.txt', 'r') as file:
    rss_list = file.readlines()

# 特殊解析的RSS链接列表
special_rss_urls = [
    'https://tianli-blog.club/feed/',
    # 在这里添加其他需要特殊处理的RSS链接
]

def fetch_feed(rss_url):
    try:
        feed = feedparser.parse(rss_url)
        return feed
    except (URLError, HTTPError, RemoteDisconnected) as e:
        print(f"访问 {rss_url} 出错: {e}")
        return None

def fetch_feed_with_requests(rss_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed
    except (requests.exceptions.RequestException, URLError, HTTPError, RemoteDisconnected) as e:
        print(f"访问 {rss_url} 出错: {e}")
        return None

def process_rss(rss_url):
    updated = False
    message_content = ""

    if rss_url in special_rss_urls:
        feed = fetch_feed_with_requests(rss_url)
    else:
        feed = fetch_feed(rss_url)
    
    if not feed or not feed.entries:
        print(f"使用 feedparser 获取 {rss_url} 失败，尝试使用 requests 再获取一次")
        feed = fetch_feed_with_requests(rss_url)

    if not feed or not feed.entries:
        print(f"访问 {rss_url} 失败两次，跳过")
        return

    feed_title = feed.feed.get('title', 'Unknown Feed').replace(" ", "_")
    last_check_file = os.path.join('check', f"{feed_title}_last_check.txt")

    print(f"检查RSS源: {feed_title}")

    # 读取上次检查时间
    if os.path.exists(last_check_file):
        with open(last_check_file, 'r') as f:
            last_check_time = float(f.read().strip())
    else:
        last_check_time = 0

    new_entries = [entry for entry in feed.entries if entry.get('published_parsed') and time.mktime(entry.published_parsed) > last_check_time]

    if new_entries:
        updated = True
        for entry in new_entries:
            entry_title = entry.get('title', 'No Title')
            entry_link = entry.get('link', 'No Link')
            message_content += f"RSS源: {feed_title}\n"
            message_content += f"文章标题: {entry_title}\n"
            message_content += f"文章链接: {entry_link}\n\n"

        # 更新最后检查时间
        latest_time = max(time.mktime(entry.published_parsed) for entry in new_entries)
        with open(last_check_file, 'w') as f:
            f.write(str(latest_time))
    else:
        print(f"{feed_title} 没有新文章")

    if updated:
        send_email("RSS更新提醒", message_content)

def check_and_notify():
    threads = []
    for rss_url in rss_list:
        rss_url = rss_url.strip()
        thread = threading.Thread(target=process_rss, args=(rss_url,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = os.environ['EMAIL_RECIPIENT']
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP(os.environ['SMTP_SERVER'], os.environ['SMTP_PORT'])
    server.starttls()
    server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
    server.send_message(msg)
    server.quit()
    print("邮件发送成功")

if __name__ == "__main__":
    check_and_notify()
