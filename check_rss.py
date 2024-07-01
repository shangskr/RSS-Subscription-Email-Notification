import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected

# 创建保存检查时间文件的目录
os.makedirs('check', exist_ok=True)

# 读取 RSS 列表
with open('rss_list.txt', 'r') as file:
    rss_list = file.readlines()

def check_and_notify():
    updated = False
    message_content = ""
    
    for rss_url in rss_list:
        rss_url = rss_url.strip()
        try:
            feed = feedparser.parse(rss_url, sanitize_html=False)  # 尝试添加 sanitize_html=False
        except (URLError, HTTPError, RemoteDisconnected) as e:
            print(f"访问 {rss_url} 出错: {e}")
            continue
        
        feed_title = feed.feed.get('title', 'Unknown Feed').replace(" ", "_")
        last_check_file = os.path.join('check', f"{feed_title}_last_check.txt")
        
        print(f"检查 RSS 源: {feed_title}")
        
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
                message_content += f"RSS 源: {feed_title}\n"
                message_content += f"文章标题: {entry_title}\n"
                message_content += f"文章链接: {entry_link}\n\n"
            
            # 更新最后检查时间
            latest_time = max(time.mktime(entry.published_parsed) for entry in new_entries)
            with open(last_check_file, 'w') as f:
                f.write(str(latest_time))
        else:
            print(f"{feed_title} 没有新文章")
    
    if updated:
        send_email("RSS 更新提醒", message_content)
    else:
        print("没有 RSS 源更新")

def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = os.environ['EMAIL_RECIPIENT'] 
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    server = smtplib.SMTP(os.environ['SMTP_SERVER'], os.environ['SMTP_PORT'])
    server.starttls()
    try:
        server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print(f"邮件发送出错: {e}")

if __name__ == "__main__":
    check_and_notify()
