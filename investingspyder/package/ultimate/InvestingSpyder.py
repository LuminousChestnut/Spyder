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
from selenium.webdriver.chrome.service import Service


def Datetime2Timestamp(dt, tz_offset: str) -> int:
    """
    将 datetime 对象和时区偏移转换为时间戳。

    :param dt: datetime 对象
    :param tz_offset: 时区偏移，例如 'UTC-4' 或 'UTC+8'
    :return: 时间戳（秒）
    """

    # 在时区偏移字符串中读取对时区的操作，根据字符串中出现负号还是正好决定是向后还是向前
    sign = 1 if tz_offset[3] == '+' else -1
    # 提取出需要偏移的小时数量
    hours_offset = int(tz_offset[4:])
    # 对原有的时间根据时区进行偏移
    tz_info = timezone(timedelta(hours=sign * hours_offset))
    dt = dt.replace(tzinfo=tz_info)
    utc_datetime = dt.astimezone(timezone.utc)
    # 根据计算出的时间返回时间戳
    return int(utc_datetime.timestamp())


def Timestamp2Datetime(timestamp: int, tz_offset: str) -> datetime:
    """
    将时间戳和时区偏移转换为 datetime 对象。

    :param timestamp: 时间戳（秒）
    :param tz_offset: 时区偏移，例如 'UTC-4' 或 'UTC+8'
    :return: datetime 对象
    """
    # 在时区偏移字符串中读取对时区的操作，根据字符串中出现负号还是正好决定是向后还是向前
    sign = 1 if tz_offset[3] == '+' else -1
    # 提取出需要偏移的小时数量
    hours_offset = int(tz_offset[4:])
    # 对原有的时间根据时区进行偏移
    tz_info = timezone(timedelta(hours=sign * hours_offset))
    utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    local_dt = utc_dt.astimezone(tz_info)
    # 根据计算出的时间戳返回时间
    return local_dt


def UTC4Minus(utc_time):
    """
    将 UTC 时间转换为 UTC-4 时间

    :param utc_time: UTC 时间的 datetime 类型
    :return: UTC-4 时间
    """

    # 定义当前的时间
    utc_zone = pytz.timezone('UTC')
    utc_minus_4_zone = pytz.timezone('Etc/GMT+4')

    # 检查 utc_time 的格式是否为字符串
    if isinstance(utc_time, str):
        utc_time_0 = utc_zone.localize(datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S'))
    else:
        raise ValueError("\r* 格式有误")

    # 转为 datetime 数据
    utc_minus_4_time = utc_time_0.astimezone(utc_minus_4_zone)
    # 返回时间
    return utc_minus_4_time.strftime('%Y-%m-%d %H:%M:%S')


def DataInit(symbol: int, resolution, start_time_string: str, utc_locale: str):
    """
    数据初始化

    :param symbol: 英为财情当中的股票编号
    :param resolution: 时间间隔
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
    :param start_time_string: 开始的时间字符串
    :param utc_locale: UTC 时区（例如:"UTC-4"）
    :return:
    """

    # 将开始的字符串转换为开始的 datetime
    start_datetime = datetime.strptime(start_time_string, "%Y-%m-%d %H:%M:%S")
    # 将开始的 datetime 根据 UTC 时区转换为开始的时间戳
    start_timestamp = Datetime2Timestamp(start_datetime, utc_locale)
    # 定义当前的时间戳
    now_timestamp = int(datetime.now().timestamp())

    # 将字符串拼接为 URL 子字符串
    secret_link = '9186edf029e99123d64071f9f8f20ba8/' + str(now_timestamp) + '/6/6/28'

    # 定义最小的时间戳间隔为 60（一分钟）
    interval = 60

    print("\r* 数值初始化完成。")

    # 如果分辨率变量为 int 类型，则时间戳间隔为 60 * 分辨率
    if isinstance(resolution, int):
        interval = 60 * resolution
    # 如果分辨率变量为 str 类型，则根据具体的字符串判断时间戳间隔，一天的时间戳间隔为 86400，一周的时间戳间隔为 604800，一个月的时间戳间隔为 2678400（31天）
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

    # 根据子字符串拼接为完整的 URL 字符串
    url = 'https://tvc4.investing.com/' + secret_link + '' + '/history?symbol=' + str(symbol) + '&resolution=' + str(
        resolution) + '&from=' + str(
        start_timestamp) + '&to=' + str(start_timestamp + 4999 * 60 * interval)
    print("* 正在爬取的 URL 为：" + url)
    return url, start_timestamp, now_timestamp, interval


def CloudFlareExceptionBeta(driver):
    """
    测试的，用于跳过 CloudFlare 检测

    :param driver: 用于 Selenium 爬虫的 driver
    :return: 网页内容数据
    """
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
    """
    将获取到的数据列表写为 .csv 文件

    :param resolution: 数据分辨率
    :param data_list: 数据列表
    :return:
    """
    with open('output_' + str(resolution) + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for item in data_list:
            writer.writerow(item)


def MainSpyder(utc_locale, spyder_url, cloudflare_exception_beta_flag_0=0):
    """
    英为财情爬虫主程序

    :param utc_locale: UTC 时区
    :param spyder_url: URL
    :param cloudflare_exception_beta_flag_0: 是否运用测试的 CloudFlare 跳过验证程序，0 为不使用，1 为使用
    :return: data_list, raw_data, last_timestamp, local_dt, next_timestamp, local_next_dt: 数据列表，网站初始数据，最后的时间戳，最后的时间，下一次时间戳，下一次时间
    """

    # 配置浏览器设置
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=110,414")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

    chrome_options.add_argument(f'user-agent={user_agent}')
    # chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    Service(r'D:\Arch\Python\driver\131.0.6738.0\chromedriver.exe')  # 替换为实际的 ChromeDriver 路径

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
    })

    # 设置浏览器窗口大小
    driver.set_window_size(1920, 1080)
    # 调出浏览器
    driver.get(spyder_url)
    print("\r* 正在运行 Selenium。")

    # 获取网页内容
    html_content = driver.page_source
    print(html_content)
    # 第一种特殊情况，出现 no_data，说明时间戳过大，可以及时终止。
    if "no_data" in html_content:
        print("* 时间戳超出数据集范围，无数据，终止程序。")
        return -1

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
        print("* 到达可获取数据的边界，程序终止。")
        return -1

    # 初始化列表
    norm_data = list()

    # 将 raw_data 中的信息进行分类
    date_ = raw_data['t']
    close_ = raw_data['c']
    open_ = raw_data['o']
    high_ = raw_data['h']
    low_ = raw_data['l']
    volume_ = raw_data['v']
    vo_ = raw_data['vo']
    vac_ = raw_data['vac']

    # 时间戳和时间计算
    # 最后一个时间戳，是 date_ 列表中的最后一个
    last_timestamp = date_[-1]
    # 将最后一个时间戳根据时区进行偏移，转换为时间
    local_dt = Timestamp2Datetime(last_timestamp, utc_locale)
    # 下一个时间戳，是 date_ 列表中的最后一个加 60 （向未来偏移一分钟）得到的
    next_timestamp = date_[-1] + 60
    # 将下一个时间戳根据时区进行偏移，转换为时间
    local_next_dt = Timestamp2Datetime(next_timestamp, utc_locale)

    # 对每一个 date_ 列表中的记录进行遍历
    for trade_item in range(len(date_)):
        # 将时间转换为更可读的形式
        utc_time = datetime.utcfromtimestamp(date_[trade_item]).strftime('%Y-%m-%d %H:%M:%S')
        converted_time = UTC4Minus(utc_time)
        # norm_data.append(converted_time)
        # 对 OHLC 数据进行四舍五入，保留两位小数
        try:
            norm_data.append([
                converted_time,
                round(open_[trade_item], 2),
                round(high_[trade_item], 2),
                round(low_[trade_item], 2),
                round(close_[trade_item], 2),
                volume_[trade_item],
                vo_[trade_item],
                round(vac_[trade_item], 2) if isinstance(vac_[trade_item], int) else vac_[trade_item]
            ])
        except Exception as err:
            print(f"填充列表时出错。\n{err}")
            break
    # 输出内容：整理完毕的数据，最初获取到的数据，最后一个时间戳，最后的时间，下一个时间戳，下一个时间
    return norm_data, raw_data, last_timestamp, local_dt, next_timestamp, local_next_dt


def List2CSV(raw_data: list, path: str) -> int:
    """
    列表转换为 .csv 文件

    :param raw_data: 列表数据
    :param path: 路径
    """

    try:
        import pandas as pd
        # 表头数据
        first_row = [['time', 'open', 'high', 'low', 'close', 'volume', 'vo', 'vac']]
        pro_data: list = raw_data
        # 原始数据和表头数据进行组合
        df = pd.DataFrame(pro_data, columns=first_row)
        df.to_csv(path, index=False)
        flag_List2CSV = 0
    except Exception as err:
        flag_List2CSV = -1
        print(err)
    return flag_List2CSV


def Launcher(symbol, resolution, start_time_string, utc_locale, cloudflare_exception_beta_flag, save_as_csv_flag=1):
    """
    英为财情爬虫启动器

    :param symbol: 英为财情中的代码
    :param resolution: 分辨率（代表时间间隔的整型或者字符串）
    :param start_time_string: 开始的时间字符串
    :param utc_locale: UTC 时区（如 UTC-4）
    :param cloudflare_exception_beta_flag: 是否采用测试版的绕过 CloudFlare 人机验证程序，0 为不使用，1 为使用
    :param save_as_csv_flag: 是否将列表保存为 .csv，0 为不使用，1 为使用
    :return raw_list, url, start_timestamp, now_timestamp, interval: 初始数据，URL，开始时间戳，当前时间戳，时间间隔
    """

    # 导入英伟财情代码、分辨率、开始的时间字符串、时区字符串等进行数据初始化，返回拼接出的 URL、开始的时间戳、现在的时间戳以及时间间隔
    url, start_timestamp, now_timestamp, interval = DataInit(symbol, resolution, start_time_string, utc_locale)

    # 根据 MainSpyder 输出内容进行解包，若输出内容无法得到匹配则说明获取的数据很有可能已经到达了边界
    try:
        data_list, raw_data, end_timestamp, local_dt, next_timestamp, local_next_dt = \
            MainSpyder(utc_locale, url, cloudflare_exception_beta_flag)
    except ValueError or IndexError or NotImplementedError:
        print("获取数据到达边界。")
        return -1

    # 如果选择了进行保存，则将文件保存到指定的位置
    if save_as_csv_flag == 1:
        csv_save_path = f"./InvestingSpyder_{symbol}_{start_time_string[0:10].replace('-', '')}_{str(local_dt)[0:10].replace('-', '')}_{resolution}.csv"
        List2CSV(data_list, csv_save_path)
    # 输出整理出的数据、最后一个时间戳、最后一个时间、下一个时间戳、下一个时间
    return data_list, end_timestamp, local_dt, next_timestamp, local_next_dt


def InvestingSpyderCycler(time_string: str, utc_locale, resolution, cycle_times: int, save_csv_path, company_name='', symbol='', download_as_csv=1):
    """
    英为财情爬虫自动化循环器

    :param time_string: 时间字符串
    :param utc_locale: 代表时区的字符串
    :param resolution: 分辨率（代表时间间隔的整型或者字符串）
    :param cycle_times: 循环次数，一般可以设置为 100
    :param save_csv_path: 保存的 .csv 文件路径
    :param company_name: 公司名称
    :param symbol: 英为财情代号
    :param download_as_csv: 是否下载为 .csv 文件，1 为下载

    :return sum_data_list, end_timestamp, local_dt, next_timestamp, local_next_dt: 总数据列表，最后时间戳，最后时间，下一次时间戳，下一次时间
    """

    # 对列表进行初始化
    sum_data_list = list()
    timestamp_list = list()
    end_timestamp, local_dt, next_timestamp, local_next_dt = (0, 0, 0, 0)

    # 如果公司名称不为空而英为财情代码为空，则运用公司名称进行操作
    if company_name != '' and symbol == '':
        for i in range(cycle_times):
            # 根据公司名称获取英为财情代码
            symbol = isl.Launcher('name', 'symbol', company_name)
            # 根据英为财情代码、分辨率、时间字符串、时区等调用爬虫启动函数
            # 若能够成功对爬虫启动函数输出内容进行解包，则将正常的数据导入到总数据列表中
            try:
                temp_data_list, end_timestamp, local_dt, next_timestamp, local_next_dt = \
                    Launcher(int(symbol.iloc[0]), resolution, time_string, 'UTC-4', 0, 1)
                timestamp_list.append(end_timestamp)
                # 如果爬虫启动函数返回了一个空列表，则说明此处无数据，应当终止循环
                if not temp_data_list:
                    break
                sum_data_list.extend(temp_data_list)
                time_string = str(local_next_dt)[:-6]
            # 如果捕捉到此类错误，则说明已经到达可以获取到的数据的边界，计算时间戳和时间并且终止循环
            except TypeError or ValueError or NotImplementedError:
                end_timestamp = timestamp_list[-1]
                local_dt = Timestamp2Datetime(end_timestamp, utc_locale)
                next_timestamp = timestamp_list[-1] + 60
                local_next_dt = Timestamp2Datetime(next_timestamp, utc_locale)
                break
    # 如果公司名称为空但是英为财情代码不为空，则按照英为财情代码进行操作
    elif company_name == '' and symbol != '':
        for i in range(cycle_times):
            # 根据英为财情代码、分辨率、时间字符串、时区等调用爬虫启动函数
            # 若能够成功对爬虫启动函数输出内容进行解包，则将正常的数据导入到总数据列表中
            try:
                temp_data_list, end_timestamp, local_dt, next_timestamp, local_next_dt = \
                    Launcher(int(symbol), resolution, time_string, utc_locale, 0, 1)
                # 如果爬虫启动函数返回了一个空列表，则说明此处无数据，应当终止循环
                if not temp_data_list:
                    break
                sum_data_list.extend(temp_data_list)
                time_string = str(local_next_dt)[:-6]
            # 如果捕捉到此类错误，则说明已经到达可以获取到的数据的边界，计算时间戳和时间并且终止循环
            except TypeError or ValueError or NotImplementedError:
                end_timestamp = timestamp_list[-1]
                local_dt = Timestamp2Datetime(end_timestamp, utc_locale)
                next_timestamp = timestamp_list[-1] + 60
                local_next_dt = Timestamp2Datetime(next_timestamp, utc_locale)
                break
    # 判断是否存在公司名称和英为财情代码都填写的情况
    elif company_name != '' and symbol != '':
        raise ValueError("公司名称 company_name 和 英为财情代码 symbol 只需填写其中一个。")
    # 如果选择了对数据进行保存的选项，则执行
    if download_as_csv == 1:
        List2CSV(sum_data_list, save_csv_path)

    print("\n* 已完成。")
    return sum_data_list, end_timestamp, local_dt, next_timestamp, local_next_dt


# 以主程序运行
if __name__ == "__main__":
    # 示例程序
    # 不使用循环，以英为财情代码获取数据的情形
    # total_data_list, the_end_timestamp, local_datetime, the_next_timestamp, local_next_datetime = \
    #     Launcher(2208, 'D', '2022-01-01 00:00:00', 'UTC-4', 0, 1)

    # 使用循环，以公司名称获取数据的情形
    data_list_, end_timestamp_, end_local_dt_, next_timestamp_, next_local_dt_ = InvestingSpyderCycler('2024-01-01 00:00:00', 'UTC-4', 1, 100, 'Apple.csv', company_name='Apple')

    # 使用循环，以英为财情代码获取数据的情形
    # data_list_, end_timestamp_, end_local_dt_, next_timestamp_, next_local_dt_ = InvestingSpyderCycler('2024-01-01 00:00:00', 'UTC-4', 1, 100, 'Apple.csv', symbol=2208)
