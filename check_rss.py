import feedparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
import requests
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 创建保存检查时间文件的目录
os.makedirs('check', exist_ok=True)

# 读取RSS列表
with open('rss_list.txt', 'r') as file:
    rss_list = file.readlines()

def requests_with_retries(url, headers=None, retries=3, backoff_factor=0.3):
    """使用重试机制的requests请求"""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    response = session.get(url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    response.encoding = response.apparent_encoding  # 确保使用正确的编码
    return response.text

def check_and_notify():
    updated = False
    message_content = ""
    
    for rss_url in rss_list:
        rss_url = rss_url.strip()
        try:
            feed = feedparser.parse(rss_url)
            if feed.bozo:
                raise feed.bozo_exception
        except (URLError, HTTPError, RemoteDisconnected, Exception) as e:
            print(f"直接解析 {rss_url} 出错: {e}, 尝试使用requests获取内容")
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }
                feed_content = requests_with_retries(rss_url, headers=headers)
                
                # 移除BOM和空白字符
                feed_content = feed_content.lstrip('\ufeff \n\r\t')
                
                # 使用feedparser解析RSS feed内容
                feed = feedparser.parse(feed_content)
                if feed.bozo:
                    print(f"解析RSS源 {rss_url} 时出错: {feed.bozo_exception}")
                    continue
            except (requests.RequestException, URLError, HTTPError, RemoteDisconnected) as e:
                print(f"使用requests访问 {rss_url} 出错: {e}")
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
