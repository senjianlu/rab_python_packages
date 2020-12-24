# rab_python_packages
我的爬虫自用包  
需要环境：Win64 位，Python3，Postgresql 数据库且版本大于10，Chrome 和 chromedirver 版本匹配

**rab_chrome**  
本地端口起 Chrome 并使用 selenium 进行控制。

**rab_logging**  
按照日期分隔文件并记录日志，默认 DEBUG 等级的日志不打印也不记录。

**rab_pgsql_driver**  
批量插入 Postgresql 数据库。

**rab_proxy**  
从数据库中查询稳定的自建爬虫信息并在每次使用时记录，以保证优先调用使用次数最少的那个。  
讯代理动态转发爬虫的封装。

**rab_telegram_bot**  
Telegram Bot 信息通知。