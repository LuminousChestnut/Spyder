import pandas as pd


def Launcher(input_mode: str, output_mode: str, string: str):
    """
    英为财情编号对照器

    :param input_mode: 输入字段，可以是 'symbol'（英为财情编制的编号）、'code'（交易所当中股票的缩写）、'name'（股票公司的名称）
    :param output_mode: 输出字段，可以是 'symbol'（英为财情编制的编号）、'code'（交易所当中股票的缩写）、'name'（股票公司的名称）
    :param string: 查询字符串
    :return: 字符串
    """
    # 需要在程序文件夹下新建一个 data 文件夹，并且 data 文件夹当中需要 symbol.xlsx 数据
    file_path = './data/symbol.xlsx'
    # 将 symbol.xlsx 数据读取为 DataFrame 数据
    df = pd.read_excel(file_path)

    # 将字符串进行修改
    def switcher(i):
        if i == 'symbol':
            o = 'pairID'
        elif i == 'code':
            o = 'ticker'
        elif i == 'name':
            o = 'name'
        else:
            raise ValueError("输入错误。")
        return o

    input_mode = switcher(input_mode)
    output_mode = switcher(output_mode)

    # 输出对应的输出
    return df[df[input_mode] == string][output_mode]


# 作为主函数运行
if __name__ == "__main__":
    # 输入苹果公司的名称，输出苹果公司的代码
    result = Launcher('name', 'symbol', 'Apple')
