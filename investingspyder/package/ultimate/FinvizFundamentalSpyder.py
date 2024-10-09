import re
import json
import pytz
import pandas as pd
from selenium import webdriver
from datetime import datetime
import InvestingSymbolLookup


def UTC4Minus(utc_time):
    """
    将 UTC 时间转为 UTC-4 时间

    :param utc_time:
    :return:
    """

    # 定义时区
    utc_zone = pytz.timezone('UTC')
    utc_minus_4_zone = pytz.timezone('Etc/GMT+4')

    # 判断输入时间的数据类型
    # 若数据类型为字符串，则将字符串进行转换
    if isinstance(utc_time, str):
        utc_time_0 = utc_zone.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S'))
    # 若数据类型为其他，则报错格式有误
    else:
        raise ValueError("\r* 格式有误")

    # 将 UTC 时区的时间转换为 UTC-4 的时间
    utc_minus_4_time = utc_time_0.astimezone(utc_minus_4_zone)
    # 返回 datetime 格式的时间
    return utc_minus_4_time.strftime('%Y-%m-%d %H:%M:%S')


def UrlGenerator(company_name: str, **kwargs) -> str:
    """
    FinViz URL 生成器

    首先根据公司名查找相应的缩写，再运用字符串拼接将链接和公司缩写进行拼接
    输入公司名称字符串，或者可选的附加链接，输出 URL 字符串

    :param company_name:
    :param kwargs:
    :return:
    """

    company_symbol = InvestingSymbolLookup.Launcher("name", "code", company_name)
    if kwargs.get("r") is not None:
        finviz_url = 'https://finviz.com/quote.ashx?t=' + str(company_symbol.iloc[0]) + str(kwargs.get("r"))
    else:
        finviz_url = 'https://finviz.com/quote.ashx?t=' + str(company_symbol.iloc[0])
    return finviz_url


def DownloadInitiation(finviz_url: str) -> str:
    """
    FinViz 下载初始化器

    设置浏览器设置，设置浏览器驱动，获取网页内容
    输入 URL 字符串，返回网页内容字符串

    :param finviz_url: URL 字符串
    :return: 网页内容
    """

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=110,414")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

    chrome_options.add_argument(f'user-agent={user_agent}')
    # chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # service = Service('/path/to/chromedriver')  # 替换为实际的 ChromeDriver 路径

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                })
                """
    })
    driver.set_window_size(1642, 988)
    driver.get(finviz_url)
    print("\r* 正在运行 Selenium。")
    html_content = driver.page_source
    return html_content


def DataTranslator(html_content: str):
    """
    FinViz 数据处理器

    运用 pandas 当中的 read_html 方法读取网页内容形成表格，提取出表格内容

    :param html_content: 网页内容字符串
    :return: 基本面数据
    """

    try:
        raw_data = pd.read_html(html_content)
        fundamental_data = raw_data[5][3:16]
    # 如果 pandas 版本较高，运用 StringIO
    except FutureWarning:
        from io import StringIO
        raw_data = pd.read_html(StringIO(html_content))
        fundamental_data = raw_data[5][3:16]
    return fundamental_data


def KLineJSONReader(html_content: str):
    """
    FinViz K 线 JSON 数据读取器

    将 JSON 格式的 K 线数据转换为更可读的列表数据

    :param html_content: 网页内容数据
    :return: 公司缩写、时间戳、整理得到的嵌套列表和股息股票分割股票回购等操作的列表
    """

    # 初始化列表
    norm_data = list()
    # 根据正则表达式提取出 K 线数据
    k_line_data_json = re.findall("var data = (.*?),\"last", html_content)[0] + '}'
    # 根据正则表达式提取 chartEvents 数据
    chart_events_data_json = re.findall('"chartEvents":\\[(.*?)],"patterns', html_content)[0]
    # 提取出未经处理过的 K 线数据
    k_line_raw_data = json.loads(k_line_data_json)

    # 根据不同的字段整理出数据
    ticker = k_line_raw_data['ticker']
    timeframe = k_line_raw_data['timeframe']
    date_list = k_line_raw_data['date']
    open_list = k_line_raw_data['open']
    high_list = k_line_raw_data['high']
    low_list = k_line_raw_data['low']
    close_list = k_line_raw_data['close']
    volume_list = k_line_raw_data['volume']
    chart_events_list = chart_events_data_json

    # 遍历，根据整理出的数据列表填充新列表
    for trade_item in range(len(date_list)):
        utc_time = datetime.utcfromtimestamp(date_list[trade_item]).strftime('%Y-%m-%d %H:%M:%S')
        converted_time = UTC4Minus(utc_time)
        norm_data.append([
            converted_time,
            round(open_list[trade_item], 2),
            round(high_list[trade_item], 2),
            round(low_list[trade_item], 2),
            round(close_list[trade_item], 2),
            volume_list[trade_item]
        ])
    return ticker, timeframe, norm_data, chart_events_list


def DataDownloader(html_content: str) -> int:
    """
    FinViz 网页数据下载器

    将输入得到的网页数据保存为程序路径下的 webpage.html

    :param html_content: 网页内容数据
    :return: 完成状态
    """

    with open('webpage.html', 'w', encoding='utf-8') as webpage_saver:
        webpage_saver.write(html_content)
    print("\r* 正在将获取网站内容写入 webpage.html 文件。", end='')
    return 0


def Launcher(company_name, **kwargs):
    """
    FinViz 基本面爬虫启动器

    将其他函数进行组合的启动器

    :param company_name: 公司名称
    :param kwargs: 可选参数
    :return: 输出网页内容、基本面信息、行情信息、股票事件列表、下载状态
    """

    # 运用 FinViz URL 生成器将公司名称转换为 URL
    finviz_url = UrlGenerator(company_name, **kwargs)
    # 运用 FinViz 下载初始化器根据 URL 提取出网页数据内容
    html_content = DownloadInitiation(finviz_url)
    # 运用 FinViz JSON 格式 K 线数据阅读器读取网页内容，形成 K 线数据和股票事件列表
    _, _, k_line_data, chart_events_list = KLineJSONReader(html_content)
    # 运用 FinViz 网页数据处理器将网页内容数据转换为基本面数据
    fundamental_data = DataTranslator(html_content)
    # 运用 FinViz 网页数据下载器将网页内容数据下载，并且返回下载状态
    downloader_status = DataDownloader(html_content)
    print("\n* 已完成。")
    return html_content, fundamental_data, k_line_data, chart_events_list, downloader_status


if __name__ == "__main__":
    finviz_raw_data, finviz_fundamental_data, finviz_k_line_data, finviz_chart_events_list, finviz_downloader_status = Launcher('Apple')
