import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

# 读取RSS列表
with open('rss_list.txt', 'r') as file:
    rss_list = file.readlines()

# 检查并发送邮件
def check_and_notify():
    updated = False
    message_content = ""

    for rss_url in rss_list:
        rss_url = rss_url.strip()
        feed = feedparser.parse(rss_url)

        last_check_time_file = f"{feed.feed.title}_last_check.txt"

        # 读取上次检查的时间戳
        if os.path.exists(last_check_time_file):
            with open(last_check_time_file, 'r') as f:
                last_check_time = float(f.read().strip())
        else:
            last_check_time = 0

        new_entries = [entry for entry in feed.entries if time.mktime(entry.published_parsed) > last_check_time]
        
        if new_entries:
            updated = True
            for entry in new_entries:
                message_content += f"博客: {feed.feed.title}\n"
                message_content += f"最新文章: {entry.title}\n"
                message_content += f"链接: {entry.link}\n\n"
                
            # 更新最后检查时间为最新文章的时间戳
            latest_time = max(time.mktime(entry.published_parsed) for entry in new_entries)
            with open(last_check_time_file, 'w') as f:
                f.write(str(latest_time))

    if updated:
        send_email(message_content)

def send_email(message_content):
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    email_recipient = os.getenv('EMAIL_RECIPIENT')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_recipient
    msg['Subject'] = "RSS Feed 更新通知"

    msg.attach(MIMEText(message_content, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, email_recipient, text)
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    check_and_notify()
