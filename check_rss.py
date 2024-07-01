import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
from bs4 import BeautifulSoup  # 新增的库
import lxml  # 新增的库

# 创建保存检查时间文件的目录
os.makedirs('check', exist_ok=True)

# 读取RSS列表
with open('rss_list.txt', 'r') as file:
    rss_list = file.readlines()

def parse_rss_content(feed):
    """
    使用BeautifulSoup和lxml解析RSS内容，提取所需信息
    """
    parsed_entries = []
    for entry in feed.entries:
        # 使用BeautifulSoup解析entry内容
        soup = BeautifulSoup(entry.description, 'lxml')
        entry_title = entry.get('title', 'No Title')
        entry_link = entry.get('link', 'No Link')
        entry_content = soup.get_text()

        parsed_entries.append({
            'title': entry_title,
            'link': entry_link,
            'content': entry_content,
            'published_parsed': entry.get('published_parsed')
        })
    return parsed_entries

def check_and_notify():
    updated = False
    message_content = ""
    
    for rss_url in rss_list:
        rss_url = rss_url.strip()
        try:
            feed = feedparser.parse(rss_url)
        except (URLError, HTTPError, RemoteDisconnected) as e:
            print(f"访问 {rss_url} 出错: {e}")
            continue
        
        feed_title = feed.feed.get('title', 'Unknown Feed').replace(" ", "_")
        last_check_file = os.path.join('check', f"{feed_title}_last_check.txt")
        
        print(f"检查RSS源: {feed_title}")
        
        # 读取上次检查时间
        if os.path.exists(last_check_file):
            with open(last_check_file, 'r') as f:
                last_check_time = float(f.read().strip())
        else:
            last_check_time = 0
        
        # 使用parse_rss_content函数解析RSS内容
        parsed_entries = parse_rss_content(feed)
        new_entries = [entry for entry in parsed_entries if entry['published_parsed'] and time.mktime(entry['published_parsed']) > last_check_time]
        
        if new_entries:
            updated = True
            for entry in new_entries:
                message_content += f"RSS源: {feed_title}\n"
                message_content += f"文章标题: {entry['title']}\n"
                message_content += f"文章链接: {entry['link']}\n"
                message_content += f"文章内容: {entry['content']}\n\n"
            
            # 更新最后检查时间
            latest_time = max(time.mktime(entry['published_parsed']) for entry in new_entries)
            with open(last_check_file, 'w') as f:
                f.write(str(latest_time))
        else:
            print(f"{feed_title} 没有新文章")
    
    if updated:
        send_email("RSS更新提醒", message_content)
    else:
        print("没有RSS源更新")

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
