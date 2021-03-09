# rab_python_packages
我的爬虫自用包。  
需要环境：Win64 位，Python3，PostgreSQL 数据库且版本大于10，Chrome 和 chromedirver 版本匹配  
使用方法（在项目主目录下）：  
只使用当前版本：git clone https://github.com/m18018230731/rab_python_packages.git  
依赖此仓库：git submodule add https://github.com/m18018230731/rab_python_packages.git  
*注：既存方法的方法名和参数不进行修改，实在需要添加参数会赋予初始值，任何改动以不影响现在的代码作为第一前提。*  

**rab_chrome**  
>本地端口起 Chrome 并使用 Selenium 进行控制。

**rab_logging**  
>按照日期分隔文件并记录日志，默认 DEBUG 等级的日志不打印也不记录。

**rab_pgsql_driver**  
>批量插入 PostgreSQL 数据库。

**rab_proxy**  
>从数据库中查询稳定的自建代理信息并在每次使用时记录，以保证优先调用使用次数最少的那个。  
讯代理动态转发代理的封装。

**rab_telegram_bot**  
>Telegram Bot 信息通知。

**rab_config**  
>读取 .ini 格式的配置文件。

**rab_storage**
>多线程爬虫下存储数据和锁保证安全。

**rab_steam**
>Steam 登录模块和手机令牌获取功能的封装。