import os
import requests
import feedparser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected

def check_and_notify(rss_url, last_check_file, headers):
    try:
        response = requests.get(rss_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        content = response.content
        content = content.lstrip()  # 去除文档开头的空白字符
        feed = feedparser.parse(content)

        # 读取上次检查时间
        if os.path.exists(last_check_file):
            with open(last_check_file, 'r') as f:
                last_check_time = datetime.fromisoformat(f.read().strip())
        else:
            last_check_time = datetime.min

        # 检查是否有新文章
        new_entries = [entry for entry in feed.entries if datetime(*entry.published_parsed[:6]) > last_check_time]

        if new_entries:
            # 更新上次检查时间
            with open(last_check_file, 'w') as f:
                f.write(datetime.now().isoformat())

            # 收集新文章的信息并发送邮件
            email_content = "\n".join([f"{entry.title}: {entry.link}" for entry in new_entries])
            send_email(email_content)
            print(f"{rss_url} 有新文章")
        else:
            print(f"{rss_url} 没有新文章")
    except requests.exceptions.RequestException as e:
        print(f"访问 {rss_url} 出错: {e}")
    except Exception as e:
        print(f"解析RSS源 {rss_url} 时出错: {e}")

def send_email(content):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = os.getenv('EMAIL_RECIPIENT')
    msg['Subject'] = "RSS更新提醒"

    msg.attach(MIMEText(content, 'plain'))

    try:
        server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"发送邮件时出错: {e}")

if __name__ == "__main__":
    rss_list_file = "rss_list.txt"
    check_directory = "check"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    os.makedirs(check_directory, exist_ok=True)

    with open(rss_list_file, 'r') as f:
        rss_urls = f.readlines()

    for rss_url in rss_urls:
        rss_url = rss_url.strip()
        last_check_file = os.path.join(check_directory, f"{rss_url.replace('/', '_')}.txt")
        print(f"检查RSS源: {rss_url}")
        check_and_notify(rss_url, last_check_file, headers)
