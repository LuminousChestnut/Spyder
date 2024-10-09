import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By


# 主函数（目标 URL，鼠标开始的 X 坐标，鼠标开始的 Y 坐标，鼠标结束的 X 坐标，鼠标结束的 Y 坐标，标签项的 XPATH，数值项的 XPATH）
def MainSpyder(target_url, start_x, start_y, end_x, end_y, step, xpath_of_label, xpath_of_number):
    # 使用 Selenium 驱动 Chrome
    driver = webdriver.Chrome()
    driver.get(target_url)

    # 初始化列表
    label_changes = list()
    number_changes = list()

    # 根据步长，循环刷新鼠标的位置，若退出可以按 Alt + F4
    for x in range(start_x, end_x, step):
        for y in range(start_y, end_y, step):
            if x == start_x:
                time.sleep(25)
            # 运用 pyautogui 库模拟鼠标移动
            pyautogui.moveTo(x, y)
            time.sleep(0.5)
            # 根据 XPATH 获取到当前的标签元素和数值元素
            label_element = driver.find_element(By.XPATH, xpath_of_label)
            number_element = driver.find_element(By.XPATH, xpath_of_number)
            # 生成最近的标签元素值和最近的数值元素值，便于比较发现是否发生了变化
            current_label_value = label_element.text
            current_number_value = number_element.text

            # 首次运行时，label_changes 列表为空，此时无须判断是否与前值发生变化，直接添加元素即可
            if not label_changes:
                label_changes.append(current_label_value)
                number_changes.append(current_number_value)
                print(f"此时的标签为：{current_label_value}")
                print(f"此时的数值为：{current_number_value}")

            # 非首次运行时，如果最近的标签值和 label_changes 中最后的一个元素不同，则将标签值和数值分别添加至对应的列表
            if label_changes:
                if current_label_value != label_changes[-1]:
                    label_changes.append(current_label_value)
                    number_changes.append(current_number_value)
                print(f"此时的标签为：{current_label_value}")
                print(f"此时的数值为：{current_number_value}")

    print("记录到的变化:", label_changes)

    # 函数输出值为两个列表，label_changes 为标签列表，number_changes 为数值列表
    return label_changes, number_changes


# 作为主程序执行的情形下
if __name__ == "__main__":
    # 以乌克兰 CPI 数据爬取为例
    # URL 为乌克兰 CPI 数据爬取的网页
    url = 'https://zh.tradingeconomics.com/ukraine/inflation-cpi'
    # label_xpath 为指标显示图中 tooltip 里时间标签的 XPATH
    label_xpath = '/html/body/form/div[5]/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[4]/div/span/div/span[1]'
    # label_xpath 为指标显示图中 tooltip 里 CPI 数字的 XPATH
    number_xpath = '/html/body/form/div[5]/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[4]/div/span/div/span[2]'
    # 调用主函数
    # MainSpyder(网页链接，鼠标初始 X 坐标，鼠标初始 Y 坐标，鼠标最终 X 坐标，鼠标最终 Y 坐标，标签 XPATH，数字 XPATH)
    # 在浏览器窗口调出后和鼠标模拟滑动前有大致 10 秒的时间可以将鼠标移动到相应的位置使对应的内容刷新
    # 运行时可以通过按下 Alt + F4 关闭浏览器窗口终止程序
    MainSpyder(url, 100, 640, 800, 641, 1, label_xpath, number_xpath)
