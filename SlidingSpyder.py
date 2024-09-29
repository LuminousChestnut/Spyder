import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By


def MainSpyder(target_url, start_x, start_y, end_x, end_y, step, xpath_of_label, xpath_of_number):
    driver = webdriver.Chrome()
    driver.get(target_url)

    label_changes = []
    number_changes = []

    for x in range(start_x, end_x, step):
        for y in range(start_y, end_y, step):
            if x == start_x:
                time.sleep(10)
            pyautogui.moveTo(x, y)
            time.sleep(0.5)
            label_element = driver.find_element(By.XPATH, xpath_of_label)
            number_element = driver.find_element(By.XPATH, xpath_of_number)  # 替换为实际的元素ID

            current_label_value = label_element.text
            current_number_value = number_element.text

            if not label_changes:
                label_changes.append(current_label_value)
                number_changes.append(current_number_value)
                print(f"此时的标签为：{current_label_value}")
                print(f"此时的数值为：{current_number_value}")

            if label_changes:
                if current_label_value != label_changes[-1]:
                    label_changes.append(current_label_value)
                    number_changes.append(current_number_value)
                print(f"此时的标签为：{current_label_value}")
                print(f"此时的数值为：{current_number_value}")

    print("记录到的变化:", label_changes)
    driver.quit()

    return label_changes, number_changes


if __name__ == "__main__":
    url = 'https://zh.tradingeconomics.com/ukraine/inflation-cpi'
    label_xpath = '/html/body/form/div[5]/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[4]/div/span/div/span[1]'
    number_xpath = '/html/body/form/div[5]/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div/div/div[2]/div/div[4]/div/span/div/span[2]'
    MainSpyder(url, 100, 640, 800, 640, 1, label_xpath, number_xpath)
