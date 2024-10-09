import re
import pandas as pd
from selenium import webdriver


# 将列表转为 .csv 文件
def List2CSV(raw_data: list, country):
    # 表头内容
    first_row = [['项目', '近期数据', '前次数据', '最高', '最低', '单位', '日期']]
    # 将表头和初始数据进行拼接
    pro_data: list = first_row + raw_data
    # 将拼接好的数据转换为 DataFrame 数据
    df1 = pd.DataFrame(pro_data)
    # df1 = pd.DataFrame(pro_data[0:], columns=pro_data[0])
    # df1.set_index(df1.columns[0], inplace=True)
    # 将 DataFrame 数据转换为 Excel 文件
    df1.to_excel(country + '总数据.xlsx', index=False)

    # pro_data2 = first_row + df1.loc['进口'].T + df1.loc['出口'].T
    # df2 = pd.DataFrame(pro_data[0:], columns=pro_data[0])
    # df2.set_index(df2.columns[0], inplace=True)
    # df2.to_excel(country + '进口和出口.xlsx', index=False)
    return df1


# 爬虫主程序（国家名称：字符串）
def MainSpyder(country: str):
    # 将国家名称字符串拼接为新字符串
    spyder_url = f"https://zh.tradingeconomics.com/{country}/indicators"

    # 配置浏览器设置
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=110,414")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

    chrome_options.add_argument(f'user-agent={user_agent}')
    # chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # service = Service('/path/to/chromedriver')  # 替换为实际的 ChromeDriver 路径

    # 驱动浏览器
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
    driver.get(spyder_url)
    print("\r* 正在运行 Selenium。")

    # 获取网页内容
    raw_html_content = driver.page_source
    driver.quit()

    # 将网页内容当中的换行符和多余的空格替换掉
    html_content = raw_html_content.replace("\n", "").replace("  ", "")

    # 运用正则表达式匹配出 </thead> 和 </tbody> 当中的内容，放入临时列表
    temp_list = re.findall("</thead>(.*?)</tbody>", html_content)

    # rt 作为结果生成的列表，进行初始化
    rt = list()

    # 对于临时列表当中的内容，根据正则表达式匹配出所需内容，最后删除临时列表
    # for index, item in enumerate(temp_list):
    #     block = re.findall("<tr>(.*?)</tr>", item)
    #     for index_2 , item_2 in enumerate(block):
    #         temp_list2 = list()
    #         name = re.findall("<a.*?>(.*?)</a>", item_2)[0]
    #         single = re.findall("<td.*?>(.*?)</td>", item_2)[1:]
    #         for index_3, item_3 in enumerate(single):
    #             item_3 = item_3.replace('<span class="te-value-negative">', "").replace("</span>", "")
    #         temp_list2.append(name)
    #         for line in single:
    #             temp_list2.append(line)
    #         rt.append(temp_list2)
    #         del temp_list2

    # 对于临时列表当中的内容，根据正则表达式匹配出所需内容，最后删除临时列表
    for i in range(len(temp_list)):
        block = re.findall("<tr>(.*?)</tr>", temp_list[i])
        for j in range(len(block)):
            temp_list2 = list()
            name = re.findall("<a.*?>(.*?)</a>", block[j])[0]
            single = re.findall("<td.*?>(.*?)</td>", block[j])[1:]
            for index in range(len(single)):
                single[index] = single[index].replace('<span class="te-value-negative">', "").replace("</span>", "")
            temp_list2.append(name)
            for line in single:
                temp_list2.append(line)
            rt.append(temp_list2)
            del temp_list2

    # TradingEconomics.com 对国家指标不同方面的分类
    item_list = ['overview', 'gdp', 'labour', 'prices', 'money',
                 'trade', 'government', 'business', 'consumer', 'housing',
                 'energy', 'health']

    # 对于此前根据正则表达式匹配到的每个块，提取出块名和块内容
    for item in item_list:
        exec(f"{item}_tbody_list = list()")
        exec(f"{item}_single_list = list()")
        for line in eval(f"{item}_tbody_list"):
            single_name = re.findall("<a href=.*?>(.*?)</a></td>", line)[0]
            single_block = re.findall("<td.*?>(.*?)</td>", line)
            for index in range(len(single_block)):
                single_block[index] = single_block[index].replace('<span class="te-value-negative">', "").replace("</span>", "")
            [single_name, single_block]

    # 将 rt 列表进行导出
    List2CSV(rt, country)
    # 输出网页内容以及 rt 列表
    return html_content, rt


# URL 生成器，根据国家名称和项目进行生成
def URLGenerator(country: str, item: str) -> str:
    url = f"https://zh.tradingeconomics.com/{country}/indicators#{item}"
    return url


# 作为主程序运行
if __name__ == "__main__":
    # 以对中国的国家指标进行爬取为例，输出网页内容和结果列表
    raw_content, return_list = MainSpyder('china')
