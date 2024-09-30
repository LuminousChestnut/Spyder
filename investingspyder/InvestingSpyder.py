import re
import csv
import json
import time
import pytz
import random
import datetime
from selenium import webdriver
from datetime import datetime, timezone, timedelta
import InvestingSymbolLookup as isl


def __init__():
    print("** InvestingSpyder.py **")


def Datetime2Timestamp(dt, tz_offset: str) -> int:
    """
    将 datetime 对象和时区偏移转换为时间戳。

    :param dt: datetime 对象
    :param tz_offset: 时区偏移，例如 'UTC-4' 或 'UTC+8'
    :return: 时间戳（秒）
    """
    sign = 1 if tz_offset[3] == '+' else -1
    hours_offset = int(tz_offset[4:])
    tz_info = timezone(timedelta(hours=sign * hours_offset))
    dt = dt.replace(tzinfo=tz_info)
    utc_datetime = dt.astimezone(timezone.utc)
    return int(utc_datetime.timestamp())


def Timestamp2Datetime(timestamp: int, tz_offset: str) -> datetime:
    """
    将时间戳和时区偏移转换为 datetime 对象。

    :param timestamp: 时间戳（秒）
    :param tz_offset: 时区偏移，例如 'UTC-4' 或 'UTC+8'
    :return: datetime 对象
    """
    sign = 1 if tz_offset[3] == '+' else -1
    hours_offset = int(tz_offset[4:])
    tz_info = timezone(timedelta(hours=sign * hours_offset))
    utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    local_datetime = utc_dt.astimezone(tz_info)
    return local_datetime


def UTC4Minus(utc_time):
    utc_zone = pytz.timezone('UTC')
    utc_minus_4_zone = pytz.timezone('Etc/GMT+4')

    if isinstance(utc_time, str):
        utc_time_0 = utc_zone.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S'))
    else:
        raise ValueError("\r* 格式有误")

    utc_minus_4_time = utc_time_0.astimezone(utc_minus_4_zone)
    return utc_minus_4_time.strftime('%Y-%m-%d %H:%M:%S')


def DataInit(symbol: int, resolution: str, start_time_string: str, utc_locale: str):
    """
    resolution:
        - 1(1分钟),
        - 5(5分钟),
        - 15(15分钟),
        - 30(30分钟),
        - 45(15)(45分钟),
        - 60(1小时),
        - 120(2小时),
        - 240(4小时),
        - 300(5小时),
        - D(一天),
        - W(一周),
        - M(一月)
    """
    # 初始化
    init_list = list()

    start_datetime = datetime.strptime(start_time_string, "%Y-%m-%d %H:%M:%S")
    start_timestamp = Datetime2Timestamp(start_datetime, utc_locale)
    now_timestamp = int(datetime.now().timestamp())

    secret_link = '9186edf029e99123d64071f9f8f20ba8/' + str(now_timestamp) + '/6/6/28'

    interval = 60

    print("\r* 数值初始化完成。")

    if isinstance(resolution, int):
        interval = 60 * resolution
    elif isinstance(resolution, str):
        if resolution == "D":
            interval = 86400
        if resolution == "W":
            interval = 604800
        if resolution == "M":
            interval = 2678400  # 按照 31 天
    else:
        raise ValueError("\r* resolution 值错误。")
    print("\r* 时间戳计算完成。")

    url = 'https://tvc4.investing.com/' + secret_link + '' + '/history?symbol=' + str(symbol) + '&resolution=' + str(
        resolution) + '&from=' + str(
        start_timestamp) + '&to=' + str(start_timestamp + 4999 * 60 * interval)
    print("* 正在爬取的 URL 为：" + url)
    return init_list, url, start_timestamp, now_timestamp, interval


def CloudFlareExceptionBeta(driver):
    print("\r* 触发模拟点击绕过 CloudFlare 验证。")
    try:
        def brownian_motion(x0, y0, x1, y1, num_steps=100, noise_factor=10):
            motion_path = []
            dx = (x1 - x0) / num_steps
            dy = (y1 - y0) / num_steps
            m_x, m_y = x0, y0
            for _ in range(num_steps):
                m_x += dx + random.uniform(-noise_factor, noise_factor)
                m_y += dy + random.uniform(-noise_factor, noise_factor)
                motion_path.append((m_x, m_y))
            return motion_path

        print("\ro 模拟鼠标轨迹完成。", end='')
        script = """
                    function moveTo(x, y) {
                        var evt = document.createEvent('MouseEvents');
                        evt.initMouseEvent('mousemove', true, true, window, 1, 0, 0, x, y, false, false, false, false, 0, null);
                        document.dispatchEvent(evt);
                    }
                    function clickAt(x, y) {
                        var evt = document.createEvent('MouseEvents');
                        evt.initMouseEvent('mousedown', true, true, window, 1, 0, 0, x, y, false, false, false, false, 0, null);
                        document.dispatchEvent(evt);
                        evt.initMouseEvent('mouseup', true, true, window, 1, 0, 0, x, y, false, false, false, false, 0, null);
                        document.dispatchEvent(evt);
                        evt.initMouseEvent('click', true, true, window, 1, 0, 0, x, y, false, false, false, false, 0, null);
                        document.dispatchEvent(evt);
                    }
                    """
        driver.execute_script(script)
        start_x, start_y = 331, 478  # 起始坐标
        target_x, target_y = 202, 255  # CloudFlare 验证坐标
        path = brownian_motion(start_x, start_y, target_x, target_y, num_steps=100, noise_factor=5)

        for (x, y) in path:
            driver.execute_script("moveTo(arguments[0], arguments[1]);", x, y)
            time.sleep(random.random() * 1)

        driver.execute_script("clickAt(arguments[0], arguments[1]);", target_x, target_y)
        print("\r* 向坐标 (202, 255) 点击以试图绕过 CloudFlare 人机验证。", end='')

        time.sleep(random.random() * 3)
        html_content = driver.page_source
        print("\r* 正在获取网站内容。", end='')
    except SyntaxError or Exception:
        html_content = ''
        print("\r* 绕过 CloudFlare 过程中出现错误。")
        pass
    return html_content


def DataWriter(resolution, data_list):
    with open('output_' + str(resolution) + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for item in data_list:
            writer.writerow(item)


def MainSpyder(data_list, utc_locale, spyder_url, cloudflare_exception_beta_flag_0=0):
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
    driver.set_window_size(1920, 1080)
    driver.get(spyder_url)
    print("\r* 正在运行 Selenium。")

    html_content = driver.page_source

    # 第一种特殊情况，出现 no_data，说明时间戳过大，可以及时终止。
    if "no_data" in html_content:
        print("* 时间戳超出数据集范围，无数据，终止程序。")
        raise ValueError("* 时间戳超出数据集范围，无数据，终止程序。")

    # 第二种特殊情况，触发 CloudFlare 机器人验证。
    if cloudflare_exception_beta_flag_0 == 1:
        if "Just a moment..." or "请稍等" or "moment" in html_content:
            html_content = CloudFlareExceptionBeta(driver)
    else:
        print("\r* 未触发绕过 CloudFlare 机器人验证程序。")

    # with open('webpage.html', 'w', encoding='utf-8') as webpage_saver:
    #     webpage_saver.write(html_content)
    # print("\r* 正在将获取网站内容写入 webpage.html 文件。", end='')

    driver.quit()
    print("\r* 关闭浏览器完成。")
    try:
        raw_data_0 = re.findall("</head><body>(.*?)</body></html>", html_content)[0]
    except IndexError:
        raw_data_0 = html_content
        print("* 最后获取到的网页为：", html_content)

    try:
        raw_data = json.loads(raw_data_0)
    except json.decoder.JSONDecodeError:
        print("* 最后获取到的信息为：" + raw_data_0)
        print("* 最后一个爬取的 URL 为：" + spyder_url)
        raise ValueError("* 到达可获取数据的边界，程序终止。")

    norm_data = []

    date_ = raw_data['t']
    close_ = raw_data['c']
    open_ = raw_data['o']
    high_ = raw_data['h']
    low_ = raw_data['l']
    volume_ = raw_data['v']
    vo_ = raw_data['vo']
    vac_ = raw_data['vac']

    last_timestamp = date_[-1]
    local_dt = Timestamp2Datetime(last_timestamp, utc_locale)

    next_timestamp = date_[-1] + 60
    local_next_dt = Timestamp2Datetime(next_timestamp, utc_locale)

    for trade_item in range(len(date_)):
        utc_time = datetime.utcfromtimestamp(date_[trade_item]).strftime('%Y-%m-%d %H:%M:%S')
        converted_time = UTC4Minus(utc_time)
        norm_data.append(converted_time)
        data_list.append([
            norm_data[trade_item],
            round(open_[trade_item], 2),
            round(high_[trade_item], 2),
            round(low_[trade_item], 2),
            round(close_[trade_item], 2),
            volume_[trade_item],
            vo_[trade_item],
            round(vac_[trade_item], 2)
        ])
    return data_list, raw_data, last_timestamp, local_dt, next_timestamp, local_next_dt


def List2CSV(raw_data: list):
    import pandas as pd
    first_row = [['time', 'open', 'high', 'low', 'close', 'volume', 'vo', 'vac']]
    pro_data: list = first_row + raw_data
    df = pd.DataFrame(pro_data[0:], columns=pro_data[0])
    df.to_csv('InvestingSpyderOutput.csv', index=False)


def Launcher(symbol, resolution, start_time_string, utc_locale, cloudflare_exception_beta_flag):
    raw_list, url, start_timestamp, now_timestamp, interval = DataInit(symbol, resolution, start_time_string, utc_locale)
    try:
        data_list, raw_data, end_timestamp, local_dt, next_timestamp, local_next_dt = \
            MainSpyder(raw_list, utc_locale, url, cloudflare_exception_beta_flag)
        return data_list, end_timestamp, local_dt, next_timestamp, local_next_dt
    except ValueError:
        pass


def InvestingSpyderCycler(time_string: str, resolution: str, cycle_times: int, company_name: str, download_as_csv=1):
    total_data_list = list()
    end_timestamp, local_dt, next_timestamp, local_next_dt = (0, 0, 0, 0)
    for i in range(cycle_times):
        symbol = isl.__init__('name', 'symbol', company_name)
        try:
            temp_data_list, end_timestamp, local_dt, next_timestamp, local_next_dt = \
                Launcher(int(symbol.iloc[0]), resolution, time_string, 'UTC-4', 0)
            total_data_list.extend(temp_data_list)
            time_string = str(local_next_dt)[:-6]
        except TypeError:
            break
    if download_as_csv == 1:
        List2CSV(total_data_list)
    del temp_data_list
    print("\n* 已完成。")
    return total_data_list, end_timestamp, local_dt, next_timestamp, local_next_dt
