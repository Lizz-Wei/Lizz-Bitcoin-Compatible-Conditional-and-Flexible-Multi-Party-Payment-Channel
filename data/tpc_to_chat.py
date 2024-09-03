import random

import pandas as pd
import re

# 解析TPC日志文件
def parse_tpc_log_file(log_file):
    with open(log_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data = {
        'funding_fee_satoshi': [],
        'funding_fee_usd': [],
        'funding_tx_size': [],
        'create_tx_time': [],
        'signing_time': [],
        'closing_fee_satoshi': [],
        'closing_fee_usd': [],
        'closing_tx_size': [],
        'update_communication_size': [],
        'total_create_sign_time': []
    }

    for line in lines:
        if line.startswith("注资交易费用为:"):
            fees = re.findall(r"(\d+\.\d+|\d+)satoshi, (\d+\.\d+)\$", line)
            if fees:
                data['funding_fee_satoshi'].append(int(fees[0][0]))
                data['funding_fee_usd'].append(float(fees[0][1]))
        elif line.startswith("** 双方支付通道注资交易 **:"):
            size = re.findall(r"(\d+) Bytes", line)
            if size:
                data['funding_tx_size'].append(int(size[0]))
        elif line.startswith("创建交易时间为"):
            create_time = re.findall(r"创建交易时间为(\d+\.\d+)s", line)
            if create_time:
                data['create_tx_time'].append(float(create_time[0]))
        elif line.startswith("两人签名的时间分别为："):
            sign_times = re.findall(r"：(\d+\.\d+)s", line)
            if sign_times:
                total_sign_time = sum(float(t) for t in sign_times)
                data['signing_time'].append(total_sign_time)
        elif line.startswith("关闭通道交易费用为:"):
            fees = re.findall(r"(\d+)satoshi,([\d\.]+)\$", line)
            if fees:
                data['closing_fee_satoshi'].append(int(fees[0][0]))
                data['closing_fee_usd'].append(float(fees[0][1]))
        elif line.startswith("通道更新通信量大小为："):
            size_time = re.findall(r"通道更新通信量大小为：(\d+)Bytes，创建和签名总时间为(\d+\.\d+)s", line)
            if size_time:
                data['update_communication_size'].append(int(size_time[0][0]))
                data['total_create_sign_time'].append(float(size_time[0][1]))
        elif line.startswith("** 双方支付通道关闭通道交易 **"):
            size = re.findall(r"(\d+) Bytes", line)
            if size:
                data['closing_tx_size'].append(int(size[0]))
    return data

# 计算平均值
def calculate_averages(data):
    averages = {key: sum(values) / len(values) if values else 0 for key, values in data.items()}
    return averages

# 保存平均值到Excel
def save_averages_to_excel(averages, output_file):
    df = pd.DataFrame([averages])
    df.to_excel(output_file, index=False)

# 指定TPC日志文件路径
log_file = 'TPC-LOG.txt'

# output_file = '../../tpc_averages_output.xlsx'

# 解析日志文件并计算平均值
# data = parse_tpc_log_file(log_file)
# # print(data['total_create_sign_time'])
# for res in data['total_create_sign_time']:
#     print(1/res)
# averages = calculate_averages(data)
#
# # 保存平均值到Excel
# save_averages_to_excel(averages, output_file)
#
# print(f"平均数据已成功保存到 {output_file}")

res = [
133.54700854700855,
128.7995878413189,
133.5826876836762,
125.23481527864745,
134.62574044157245,
134.03029084573114,
132.87270794578794,
126.71059300557528,
121.93634922570418,
129.315918789603]

# 定义从数组中随机选择n个元素并计算平均值的函数
def random_mean(array, n):
    sample = random.sample(array, n)
    return sum(sample) / n

# 定义n
n = 2  # 你可以根据需要修改n的值

# 获取4个平均值
averages = [random_mean(res, n) for _ in range(5)]

print(averages)