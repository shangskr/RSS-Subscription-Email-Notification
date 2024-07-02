# RSS Feed Checker

该项目用来订阅自己喜欢的博主的文章，避免不知道其啥时候更新新的文章，
这是一个用于检查 RSS 源并发送电子邮件通知的项目。该项目使用 GitHub Actions 定期运行，检查指定的 RSS 源，并在发现新内容时发送电子邮件通知。
- 需要注意，fork本项目之后，请删除check这个文件夹，并且在rss_list.txt文件内填写需要检查的 RSS URL，运行之后就会自动生成check文件
- 另外，第一次运行之后发给你的邮箱通知内容会是全部的rss源的所有文章，不要在意，这只是在‘标记’~第二次运行之后，他就不会显示所有的文章了
## 举个例子
- 比如我在2024年6月29日第一次运行了该项目，那么发送给你的邮箱通知内容会是全部的rss源的所有文章，（但是你想要的并不是所有的文章————别急）假设我要在2024年7月1日再次（第二次）运行该项目，但是在这期间你自己订阅的rss源更新了3篇文章，那么这次邮箱发给你的内容就仅仅有这3篇新文章，也就是和上一次作对比（永远和前几次作对比——应该是这样的）如果在这期间你订阅的rss源没有更新文章，那么就不会给你发邮件通知（一开始是通知来着，但是频繁发邮箱·咳咳，就给去掉了）

## 记录
- 2024年7月2日16:56:11删除feed.txt文件该文件用来存放类似这样的rss'https://tianli-blog.club/feed/' 这样类似的rss源链接的使用方法请见《使用方法的3.5》
- check文件中生成的数字是 Unix 时间戳，这种时间戳表示自 1970 年 1 月 1 日（也称为 Unix 纪元）以来的秒数，如果你想查看这些时间戳对应的具体日期可以转换（方法不记）

## 功能
- 定期检查指定的 RSS 源
- 发送电子邮件通知
- 自动更新最近检查时间
- 新增 User-Agent 字段的值表示请求是由一个Windows 10操作系统上的Chrome浏览器发起的请求。

## 使用方法
#### 1. 克隆项目 
#### 2. 删除check文件夹
#### 3. 在rss_list.txt文件内填写需要检查的 RSS URL
#### 3.5 如果有些链接不能正常获取解析，那么你可将其现添加到rss_list.txt文件，然后进入check_rss.py文件的18到24行将不能正常获取解析的链接再填写进去。
#### 4. 设置环境变量
- EMAIL_USER: 发电子邮件的地址
- EMAIL_PASS: 电子邮件‘密码’（我用的outlook的SMTP服务）也就是应用码
- EMAIL_RECIPIENT: 收件人电子邮件地址
- SMTP_SERVER: SMTP 服务器地址（我用的outlook的，自行百度）SMTP服务器 ：smtp.office365.com
- SMTP_PORT: SMTP 服务器端口（我用的outlook的，自行百度）端口 ：587
#### 5.运行工程流文件
- 需要的设置也就不说了，都是老规矩了！
#### 如果在使用过程中遇到任何问题或有任何建议，欢迎提交Issues。
