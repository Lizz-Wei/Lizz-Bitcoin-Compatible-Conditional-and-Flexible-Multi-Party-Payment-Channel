import json
import math
import time

from bitcoinutils.script import Script
from bitcoinutils.transactions import TxInput, Transaction, TxOutput

import txs
import scripts
from main_join import hash256

# 定义常量
SATOSHIS_PER_BTC = 100_000_000
feerate = 15.922


def create_funding_transaction(user1, user2, amount):
    """
    创建两个用户的注资交易

    参数:
    - user1: 第一个用户对象
    - user2: 第二个用户对象
    - amount: 注资金额（以聪为单位）

    返回:
    - tx: 创建的注资交易对象
    """
    start_time = time.perf_counter()

    tx_in0 = user1.utxo
    tx_in1 = user2.utxo
    amount *= SATOSHIS_PER_BTC

    tx = txs.get_TPCTX_funding(tx_in0, tx_in1, user1, user2, amount, feerate)
    txf_id = hash256(tx.serialize())

    tpc_create_time = time.perf_counter() - start_time

    return TxInput(txf_id, 0), txf_id, tpc_create_time


def update_channel(txf_id, sender, receiver, amount, distribution=None):
    """
    更新通道，处理用户之间的支付并签名

    参数:
    - txf_id: 注资交易的输入
    - amount: 发送方向接收方的支付金额
    - sender: 发送方用户对象
    - receiver: 接收方用户对象
    - feerate: 交易费率

    返回:
    - tx: 更新后的交易对象
    - distribution: 更新后的支付分配情况字典
    - send_receive_time: 消息发送和接收的时延
    """
    start_time = time.perf_counter()

    if not distribution:
        # 初始化默认的支付分配情况
        distribution = {
            sender.name: 1 * SATOSHIS_PER_BTC,
            receiver.name: 1 * SATOSHIS_PER_BTC
        }

    amount *= SATOSHIS_PER_BTC

    # 更新支付分配情况，根据amount来定义新的支付
    if distribution[sender.name] < amount:
        raise ValueError("发送方的余额不足")

    distribution[sender.name] -= amount
    distribution[receiver.name] += amount

    # 创建新交易
    tx = Transaction()

    # 创建一个输入，从多签地址取出资金
    tx_in = txf_id
    tx.inputs.append(tx_in)

    # 创建输出，根据更新后的distribution字典分配资金
    for address, amount in distribution.items():
        tx_out = TxOutput(int(amount), scripts.get_script_TPCTXs(sender, receiver))
        tx.outputs.append(tx_out)

    creation_time = time.perf_counter() - start_time
    # print(f"创建交易时间为{creation_time:.6f}s")

    script_in = scripts.get_script_TPCTXs(sender, receiver)

    # 发送方签名
    start_time = time.perf_counter()
    sig_sender = sender.sk.sign_input(tx, 0, script_in)
    sign_time_sender = time.perf_counter() - start_time

    # 生成待接收方签名的内容
    content_tor = {"tx": tx.serialize()}
    content_tor_json = json.dumps(content_tor)
    # print(content_tor_json)
    content_tor_size = len(content_tor_json.encode('utf-8'))

    # 发送消息给接收方并记录时延
    start_time = sender.send_message(content_tor_json, receiver.port)
    message, end_time = receiver.receive_message()
    send_receive_time = end_time - start_time
    print(f"消息发送和接收时间为{send_receive_time:.6f}s")

    # 接收方签名
    start_time = time.perf_counter()
    sig_receiver = receiver.sk.sign_input(tx, 0, script_in)
    sign_time_receiver = time.perf_counter() - start_time

    sign_total_time = sign_time_sender + sign_time_receiver
    # print(f"两人签名的时间分别为：{sign_time_sender:.6f}s，{sign_time_receiver:.6f}s，总签名时间为{sign_total_time:.6f}s。")

    tx_in.script_sig = Script([sig_sender, sig_receiver])

    # 计算交易大小
    estimated_size = int(len(tx.serialize()) / 2)

    # 计算交易费用
    fee = math.ceil(feerate * estimated_size)

    total_time = creation_time + sign_total_time + send_receive_time
    # print(f"通道更新交易费用为: {fee}satoshi, {fee * 61731.91 / 100000000}$")
    print(f"双方支付通道更新通信量大小为：{content_tor_size}Bytes，创建，签名和广播交易的总时间为{total_time:.6f}s。")

    return tx, distribution, total_time, send_receive_time

