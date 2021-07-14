# rab_python_packages

## 项目介绍  
简单可用的 Python3 模块包。  
方便的在此基础上进行爬虫开发、爬虫代理切换和爬虫数据存储，极端情况下也可使用 Selenium 接管 Chrome 爬取网页。  

## 环境
| 系统 | 版本 |  
| -----| ---- |  
| Linux | CentOS7 |

| 数据库 | 版本 |  
| -----| ---- |  
| PostgreSQL | 12 |

| 模块 | 版本 |
| -----| ---- |  
|**Python**|**3.8.2**|  
|fastapi|0.62.0|  
|requests|2.24.0|  
|uvicorn|0.13.1|

## 使用方法 
仅使用当前版本（维持爬虫的稳定可用）:
```bash
git clone https://github.com/senjianlu/rab_python_packages.git
```
依赖此仓库（获取更多的封装方法）:
```bash
git submodule add https://github.com/senjianlu/rab_python_packages.git
```
*注：既存方法的方法名和参数不进行修改，实在需要添加参数会赋予初始值，任何改动以不影响现在的代码作为第一前提。*  

## 模块描述
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

**rab_ssr**
>Linux 下解析 SSR 订阅信息并更新本机的 SS 设置以实现代理。

## 特别鸣谢
- 感谢 [JetBrains](https://www.jetbrains.com/) 为本项目提供的开源许可证