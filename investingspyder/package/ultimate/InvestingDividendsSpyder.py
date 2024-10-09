import asyncio
import random
import time
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def Downloader(switch, start_date='', end_date='', **kwargs):
    """
    Investing Dividends Downloader

    :param switch: Dividends 的选择的模式:
    - -1: 昨天
    - 0: 今天
    - 1: 明天
    - -7: 本周
    - 7: 下周
    - o: 自选日期（需要设置 start_date 和 end_date）
    :param start_date: 以 '01/31/2024' 格式的日期，若不进行日期自选则不需要填写
    :param end_date: 以 '01/31/2024' 格式的日期，若不进行日期自选则不需要填写
    :param kwargs: 可接受可选 url 关键字测试
    :return:
    """

    print("* 开始初始化。")
    print("\r* 检查参数输入是否正确......", end='')
    if (switch == 'o') & ((start_date == '') | (end_date == '')):
        raise ValueError("选择自定义时间时应当填写具体的起始时间，格式为'01/31/1970'")
    print("\ro 参数输入正确。", end='')

    # 配置 ChromeDriver 和 ChromeOptions
    print("\r* 定义初始值......", end='')
    # URL
    download_directory = './'

    # XPATH Library
    table_XPATH = "/html/body/div[7]/section/div[4]/table/tbody"

    close_pop_sign_ad_XPATH = "/html/body/div[8]/div[2]/i"
    close_pop_tv_ad_XPATH = "/html/body/div[7]/aside/div[2]/div/div/div/div[2]/div/div[1]/div[1]/div[2]"

    yesterday_XPATH = "/html/body/div[7]/section/div[4]/form/div/div[1]/div[1]/a[1]"
    today_XPATH = "/html/body/div[7]/section/div[4]/form/div/div[1]/div[1]/a[2]"
    tomorrow_XPATH = "/html/body/div[7]/section/div[4]/form/div/div[1]/div[1]/a[3]"
    this_week_XPATH = "/html/body/div[7]/section/div[4]/form/div/div[1]/div[1]/a[4]"
    next_week_XPATH = "/html/body/div[7]/section/div[4]/form/div/div[1]/div[1]/a[5]"
    option_XPATH = "/html/body/div[7]/section/div[4]/form/div/div[1]/div[1]/a[6]"

    input_start_XPATH = "/html/body/div[10]/div[1]/input[1]"
    input_end_XPATH = "/html/body/div[10]/div[1]/input[2]"
    input_apply_XPATH = "/html/body/div[10]/div[5]/a"

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

    # chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=110,414")
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--auto-open-devtools-for-tabs")  # 自动打开 DevTools
    chrome_options.add_argument("--remote-debugging-port=9222")  # 启用 CDP
    # chrome_options.add_argument("--headless")  # 如果不需要显示浏览器窗口
    # chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速

    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_directory,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
        })
        """
    })
    driver.execute_cdp_cmd('Network.enable', {})
    print("\r* 定义初始值成功。", end='')

    # 执行测试逻辑
    if kwargs.get("url") is None:
        url = "https://www.investing.com/dividends-calendar/"
    else:
        url = kwargs.get("url")

    print("\r* 针对 " + url + " 进行爬虫中......")

    # # 启动 DevTools WebSocket 连接
    # def on_message(ws, message):
    #     msg = json.loads(message)
    #     if 'method' in msg and msg['method'] == 'Network.responseReceived':
    #         url = msg['params']['response']['url']
    #         if url.startswith('http') and 'Content-Disposition' in msg['params']['response']['headers']:
    #             filename = msg['params']['response']['headers']['Content-Disposition'].split('filename=')[1].strip('"')
    #             print(f"Found file URL: {url}")
    #             print(f"Downloading file: {filename}")
    #             download_file(url, os.path.join(download_directory, filename))
    #
    # def on_error(ws, error):
    #     print("Error:", error)
    #
    # def on_close(ws):
    #     print("### closed ###")
    #
    # def on_open(ws):
    #     ws.send(json.dumps({
    #         "id": 1,
    #         "method": "Network.enable"
    #     }))
    #
    # def download_file(url, filepath):
    #     response = requests.get(url, stream=True)
    #     with open(filepath, 'wb') as file:
    #         for chunk in response.iter_content(chunk_size=8192):
    #             file.write(chunk)
    #     print(f"Downloaded file to {filepath}")

    driver.set_window_size(1034, 887)
    driver.get(url)

    # try:
    #     element = WebDriverWait(driver, 6).until(
    #         ec.visibility_of_element_located((By.ID, 'element-id'))
    #     )
    # except Exception as exception_at_init:
    #     print("x 一项错误发生，详情请调用 exception_at_init 变量。")

    print("* 正在运行 Selenium......")

    # 异步函数用于关闭弹出的登录广告
    async def AR_close_pop():
        flag = 0
        while flag == 0:
            print("\r* 弹出窗口关闭异步函数正在运作中" + random.choice(["|", "/", "\\", "-"]), end='')
            try:
                print("\r* 正在尝试关闭弹出窗口。" + random.choice(["|", "/", "\\", "-"]), end='')
                driver.find_element(By.XPATH, close_pop_sign_ad_XPATH).click()
                raise EOFError
            except ElementNotInteractableException:
                print("\r* 未检测到弹出窗口。" + random.choice(["|", "/", "\\", "-"]), end='')
            except EOFError:
                print("\r* 关闭成功。" + random.choice(["|", "/", "\\", "-"]), end='')
                return
            await asyncio.sleep(1)

    # 异步函数用于持续唤醒关闭弹出的登录广告窗口
    async def BG_main():
        asyncio.create_task(AR_close_pop())
        for i in range(5):
            print("\r* 关闭弹出窗口异步函数持续唤醒中，持续 5.00 秒...{:.2f}/5.00 s".format(i * 1), end='')
            await asyncio.sleep(1)

    asyncio.run(BG_main())

    # devtools_url = driver.command_executor._url.replace("http", "ws") + "/devtools/browser/" + driver.session_id
    # ws = websocket.WebSocketApp(devtools_url, on_message=on_message, on_error=on_error, on_close=on_close)
    # ws.on_open = on_open
    # ws.run_forever()
    # input("请按下 Enter 以继续")

    print("\n* 正在尝试进行下一步：模拟点击操作。")

    # 选择日期
    if switch == "-1":
        print("* 正在尝试点击，获取昨日的信息。")
        try:
            try:
                driver.find_element(By.XPATH, yesterday_XPATH).click()
            except ElementClickInterceptedException or ElementNotInteractableException:
                driver.find_element(By.XPATH, close_pop_sign_ad_XPATH).click()
                driver.find_element(By.XPATH, yesterday_XPATH).click()
            raise EOFError
        except EOFError:
            print("* 刷新成功。")
        except not EOFError:
            print("x 模拟点击过程出错。")
    elif switch == "0":
        driver.find_element(By.XPATH, today_XPATH).click()
    elif switch == "1":
        driver.find_element(By.XPATH, tomorrow_XPATH).click()
    elif switch == "-7":
        driver.find_element(By.XPATH, this_week_XPATH).click()
    elif switch == "7":
        driver.find_element(By.XPATH, next_week_XPATH).click()
    elif switch == "o":
        driver.find_element(By.XPATH, option_XPATH).click()
        driver.find_element(By.XPATH, input_start_XPATH).clear()
        driver.find_element(By.XPATH, input_start_XPATH).send_keys(start_date)
        driver.find_element(By.XPATH, input_end_XPATH).clear()
        driver.find_element(By.XPATH, input_end_XPATH).send_keys(end_date)
        driver.find_element(By.XPATH, input_apply_XPATH).click()

    print("* 获取页面源代码中。")

    WebDriverWait(driver, 10, 1).until(
        ec.visibility_of_element_located((By.XPATH, table_XPATH))
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2.5)
    page_data = driver.page_source
    print("* 获取页面源代码完成。\n以下为获取到的页面源代码的前 300 个字符：\n" + page_data[:300])
    driver.quit()
    print("* 正在退出 Selenium。")
    print("* 已完成。")
    return page_data


def Reader(dividends_data):
    """
    英为财情股利股息阅读器

    :param dividends_data: 股利股息数据
    :return: 股利股息列表
    """

    import re

    content = dividends_data

    # 将网站数据当中用于混淆的换行符、制表符、双斜杠、双反斜杠等部分进行替换
    content = content.replace("\n", "").replace("\t", "").replace("  ", "").replace('\\"', '"').replace('"/', '"').replace('\\"', '"').replace("\\/", "").replace("/\\", "")
    # print(content)
    print("* 正在清洗数据中......")

    # a_list 匹配内容
    a_list = re.findall(r'<td class="flag">(.*?)<tr>', content)
    # b_list 初始化新列表
    b_list = list()
    for item in a_list:
        # 匹配公司名称
        company = re.findall('<span class="earnCalCompanyName middle">(.*?)</span>', item)[0]
        # 匹配派发股利股息的日期
        try:
            ex_dividend_date = re.findall(r'<td>([a-zA-z]+ \d+, \d+)</td>', item)[0]
            # ex_dividend_date = re.findall(r'<td>(\d+年\d+月\d+日)</td>', item)[0]
        # 若不显示日期则显示为横线
        except IndexError:
            ex_dividend_date = "--"
        # 匹配派发股利股息
        try:
            dividend = re.findall(r'<td>(-?\d+.\d+)?</td>', item)[0]
        # 若不显示则显示为横线
        except IndexError:
            dividend = "--"
        # 匹配频率类型
        try:
            type_ = re.findall('<span class="icon(.*?)" title=', item)[0]
        # 若不显示则显示为横线
        except IndexError:
            type_ = "--"
        # 匹配支付日期
        try:
            payment_date = re.findall(r'<td data-value="\d+">(.*?)</td>', item)[0]
        # 若不显示则显示为横线
        except IndexError:
            payment_date = "--"
        # 匹配支付率
        try:
            yield_ = re.findall(r'<td>(-?\d+.\d+?%)</td>', item)[0]
        # 若不显示则显示为横线
        except IndexError:
            yield_ = "--"
        # 将数据整理为新的列表
        b_list.append([company, ex_dividend_date, dividend, type_, payment_date, yield_])

    print("o 清洗数据完成。")
    print("InvestingDividendsReader.py oo")
    return b_list


def Launcher(switch, start_date='', end_date=''):
    """
    英为财情股利股息信息爬取启动器

    :param switch: Dividends 的选择的模式:
    - -1: 昨天
    - 0: 今天
    - 1: 明天
    - -7: 本周
    - 7: 下周
    - o: 自选日期（需要设置 start_date 和 end_date）
    :param start_date: 以 '01/31/2024' 格式的日期，若不进行日期自选则不需要填写
    :param end_date: 以 '01/31/2024' 格式的日期，若不进行日期自选则不需要填写
    :return: 处理后的数据
    """

    # 股利股息数据下载
    raw_data = Downloader(switch, start_date, end_date)
    # 股利股息数据读取
    pro_data = Reader(raw_data)
    return pro_data


if __name__ == "__main__":
    Launcher('7', '01/31/2024', '09/01/2024')