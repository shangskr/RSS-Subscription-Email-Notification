import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
import html
import logging

# 设置日志记录
logging.basicConfig(filename='rss_checker.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 创建保存检查时间文件的目录
os.makedirs('check', exist_ok=True)

# 读取RSS列表
with open('rss_list.txt', 'r') as file:
    rss_list = file.readlines()

def get_feed_title(feed):
    if 'title' in feed.feed:
        return feed.feed.title
    elif 'title' in feed:
        return feed.title
    elif len(feed.entries) > 0 and 'title' in feed.entries[0]:
        return feed.entries[0].title
    else:
        return 'Unknown Feed'

def decode_html_entities(text):
    return html.unescape(text)

def check_and_notify():
    updated = False
    message_content = ""
    
    for rss_url in rss_list:
        rss_url = rss_url.strip()
        try:
            feed = feedparser.parse(rss_url, request_headers={'Accept-Charset': 'utf-8'})
        except (URLError, HTTPError, RemoteDisconnected) as e:
            logging.error(f"访问 {rss_url} 出错: {e}")
            print(f"访问 {rss_url} 出错: {e}")
            continue
        
        feed_title = get_feed_title(feed).replace(" ", "_")
        last_check_file = os.path.join('check', f"{feed_title}_last_check.txt")
        
        logging.info(f"检查RSS源: {feed_title}")
        print(f"检查RSS源: {feed_title}")
        
        if os.path.exists(last_check_file):
            with open(last_check_file, 'r') as f:
                last_check_time = float(f.read().strip())
        else:
            last_check_time = 0
        
        new_entries = [entry for entry in feed.entries if (entry.get('published_parsed') or entry.get('updated_parsed')) and time.mktime(entry.get('published_parsed', entry.get('updated_parsed'))) > last_check_time]
        
        if new_entries:
            updated = True
            for entry in new_entries:
                entry_title = decode_html_entities(entry.get('title', 'No Title'))
                entry_link = entry.get('link', 'No Link')
                message_content += f"RSS源: {feed_title}\n"
                message_content += f"文章标题: {entry_title}\n"
                message_content += f"文章链接: {entry_link}\n\n"
            
            latest_time = max(time.mktime(entry.get('published_parsed', entry.get('updated_parsed'))) for entry in new_entries)
            with open(last_check_file, 'w') as f:
                f.write(str(latest_time))
        else:
            logging.info(f"{feed_title} 没有新文章")
            print(f"{feed_title} 没有新文章")
    
    if updated:
        send_email("RSS更新提醒", message_content)
    else:
        logging.info("没有RSS源更新")
        print("没有RSS源更新")

def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = os.environ['EMAIL_USER']
    msg['To'] = os.environ['EMAIL_RECIPIENT'] 
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP(os.environ['SMTP_SERVER'], os.environ['SMTP_PORT'])
        server.starttls()
        server.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASS'])
        server.send_message(msg)
        server.quit()
        logging.info("邮件发送成功")
        print("邮件发送成功")
    except Exception as e:
        logging.error(f"发送邮件失败: {e}")
        print(f"发送邮件失败: {e}")

if __name__ == "__main__":
    check_and_notify()
