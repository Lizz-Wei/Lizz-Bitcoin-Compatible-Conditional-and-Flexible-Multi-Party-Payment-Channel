import binascii
import json
import math
import time
import hashlib
from typing import Dict

from bitcoinutils.script import Script
from bitcoinutils.transactions import TxInput

import txs
import scripts
Lizz import join_channel
from User import User

# 定义常量
SATOSHIS_PER_BTC = 100_000_000
feerate = 15.922

# 代理映射
proxy_mapping = {}
# 存储加入用户、代理、支付通道txid和通道内分配情况的映射
join_channel_info = {}


def join_test(user_list):
    # 初始化用户和其他参数
    users, utxos, selected_users = initialize_users(6, user_list)
    layer1, layer2, layer3, committee = split_users(users, selected_users, 6, 3)

    distribution = {key: 1.0 * SATOSHIS_PER_BTC for key in users}
    committee_num = 3
    committee_threshold = 2
    c = 1 * SATOSHIS_PER_BTC

    tx_in_channel, TXf_MPC = create_MPCTX_funding(users, utxos, committee_num, committee_threshold, c, feerate)

    log_filename = f"output_log_0.txt"
    with open(log_filename, "w") as log_file:
        log_file.write(f"注资交易ID为：{tx_in_channel.txid}\n")

        # # 第一轮支付（初始状态）
        # log_file.write(f"\n第一轮支付（初始状态）:\n")
        # print(f"\n第一轮支付（初始状态）:\n")
        #
        # start_time = time.perf_counter()
        # distribution, total_transactions, total_communication_time, total_network_time = log_payment(log_file, layer1, layer2, layer3,
        #                                                                          tx_in_channel, distribution,
        #                                                                          users, committee, committee_num,
        #                                                                          committee_threshold)
        # end_time = time.perf_counter()
        # duration = end_time - start_time
        # throughput = total_transactions / duration
        #
        # log_file.write(f"第一轮总交易数量：{total_transactions}\n")
        # log_file.write(f"第一轮时延：{duration:.6f} s\n")
        # log_file.write(f"第一轮吞吐量：{throughput:.6f} transactions/s\n")
        # log_file.write(f"\n第一轮支付的总通信时延为：{total_network_time:.6f} s\n")
        # print(f"\n第一轮支付的总通信时延为：{total_network_time:.6f} s\n")
        # print(f"第一轮总交易数量：{total_transactions}\n")
        # print(f"第一轮时延：{duration:.6f} s\n")
        # print(f"第一轮吞吐量：{throughput:.6f} transactions/s\n")

        # 累积加入的用户列表
        accumulated_selected_users = []
        accumulated_proxy_users = []
        tpc_distributions = []

        # 第二轮支付（加入一个用户）
        log_file.write(f"\n第二轮支付（加入一个用户）:\n")
        print(f"\n第二轮支付（加入一个用户）:\n")

        start_time = time.perf_counter()
        accumulated_selected_users, accumulated_proxy_users, tpc_distributions, distribution, total_transactions, total_communication_time, total_network_time, total_tpc_create_update_time = join_user_and_log_payment(
            log_file, user_list, users, utxos, layer1, layer2, layer3, committee, distribution, tx_in_channel, 1,
            accumulated_selected_users, accumulated_proxy_users, tpc_distributions)
        end_time = time.perf_counter()
        duration = end_time - start_time
        throughput = total_transactions / duration

        log_file.write(f"第二轮总交易数量：{total_transactions}\n")
        log_file.write(f"第二轮时延：{duration:.6f} s\n")
        log_file.write(f"第二轮吞吐量：{throughput:.6f} transactions/s\n")
        log_file.write(f"\n第二轮支付的总通信时延为：{total_network_time:.6f} s\n")
        log_file.write(f"第二轮TPC耗时：{total_tpc_create_update_time:.6f} s\n")
        print(f"\n第二轮支付的总通信时延为：{total_network_time:.6f} s\n")
        print(f"第二轮总交易数量：{total_transactions}\n")
        print(f"第二轮时延：{duration:.6f} s\n")
        print(f"第二轮吞吐量：{throughput:.6f} transactions/s\n")
        print(f"第二轮TPC耗时：{total_tpc_create_update_time:.6f} s\n")

        # 第三轮支付（加入两个用户）
        log_file.write(f"\n第三轮支付（加入两个用户）:\n")
        print(f"\n第三轮支付（加入两个用户）:\n")

        start_time = time.perf_counter()
        accumulated_selected_users, accumulated_proxy_users, tpc_distributions, distribution, total_transactions, total_communication_time, total_network_time, total_tpc_create_update_time = join_user_and_log_payment(
            log_file, user_list, users, utxos, layer1, layer2, layer3, committee, distribution, tx_in_channel, 2,
            accumulated_selected_users, accumulated_proxy_users, tpc_distributions)
        end_time = time.perf_counter()
        duration = end_time - start_time
        throughput = total_transactions / duration

        log_file.write(f"第三轮总交易数量：{total_transactions}\n")
        log_file.write(f"第三轮时延：{duration:.6f} s\n")
        log_file.write(f"第三轮吞吐量：{throughput:.6f} transactions/s\n")
        log_file.write(f"\n第三轮支付的总通信时延为：{total_network_time:.6f} s\n")
        log_file.write(f"第三轮TPC耗时：{total_tpc_create_update_time:.6f} s\n")
        print(f"\n第三轮支付的总通信时延为：{total_network_time:.6f} s\n")
        print(f"第三轮总交易数量：{total_transactions}\n")
        print(f"第三轮时延：{duration:.6f} s\n")
        print(f"第三轮吞吐量：{throughput:.6f} transactions/s\n")
        print(f"第三轮TPC耗时：{total_tpc_create_update_time:.6f} s\n")

        # 第四轮支付（加入三个用户）
        log_file.write(f"\n第四轮支付（加入三个用户）:\n")
        print(f"\n第四轮支付（加入三个用户）:\n")

        start_time = time.perf_counter()
        accumulated_selected_users, accumulated_proxy_users, tpc_distributions, distribution, total_transactions, total_communication_time, total_network_time, total_tpc_create_update_time = join_user_and_log_payment(
            log_file, user_list, users, utxos, layer1, layer2, layer3, committee, distribution, tx_in_channel, 3,
            accumulated_selected_users, accumulated_proxy_users, tpc_distributions)
        end_time = time.perf_counter()
        duration = end_time - start_time
        throughput = total_transactions / duration

        log_file.write(f"第四轮总交易数量：{total_transactions}\n")
        log_file.write(f"第四轮时延：{duration:.6f} s\n")
        log_file.write(f"第四轮吞吐量：{throughput:.6f} transactions/s\n")
        log_file.write(f"\n第四轮支付的总通信时延为：{total_network_time:.6f} s\n")
        log_file.write(f"第四轮TPC耗时：{total_tpc_create_update_time:.6f} s\n")
        print(f"\n第四轮支付的总通信时延为：{total_network_time:.6f} s\n")
        print(f"第四轮总交易数量：{total_transactions}\n")
        print(f"第四轮时延：{duration:.6f} s\n")
        print(f"第四轮吞吐量：{throughput:.6f} transactions/s\n")
        print(f"第四轮TPC耗时：{total_tpc_create_update_time:.6f} s\n")


def main(user_num, committee_num, committee_threshold):
    with open("users_96.txt", "r") as f:
        user_list = json.load(f)
    two_layer_total_network_time = 0
    users, utxos, selected_users = initialize_users(user_num, user_list)
    layer1, layer2, layer3, committee = split_users(users, selected_users, user_num, committee_num)

    distribution = {key: 1.0 * SATOSHIS_PER_BTC for key in users}

    c = 1 * SATOSHIS_PER_BTC
    feerate = 15.922
    TXf_MPC = txs.get_MPCTX_funding(utxos, users, c, feerate, committee_num, committee_threshold)
    txf_id = hash256(TXf_MPC.serialize())
    log_filename = f"output_{user_num}_{committee_num}_log.txt"
    with open(log_filename, "w") as log_file:
        log_file.write(f"注资交易ID为：{txf_id}\n")
        tx_in_channel = TxInput(txf_id, 0)

        start_total_time = time.perf_counter()

        total_size_1 = 0
        total_time_1 = 0
        for sender_key, sender in layer1.items():
            size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(log_file,
                                                                                                            sender_key,
                                                                                                            sender,
                                                                                                            tx_in_channel,
                                                                                                            distribution,
                                                                                                            users,
                                                                                                            committee,
                                                                                                            committee_num,
                                                                                                            committee_threshold,
                                                                                                            recipients=layer2)
            total_size_1 += size
            total_time_1 += time_spent
            two_layer_total_network_time += total_network_time
        log_file.write(
            f"第一层向第二层的支付通信量大小为：{total_size_1} bytes, 创建交易和签名的总时间为：{total_time_1:.6f} s\n")

        total_size_2 = 0
        total_time_2 = 0
        for sender_key, sender in layer2.items():
            size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(log_file,
                                                                                                            sender_key,
                                                                                                            sender,
                                                                                                            tx_in_channel,
                                                                                                            distribution,
                                                                                                            users,
                                                                                                            committee,
                                                                                                            committee_num,
                                                                                                            committee_threshold,
                                                                                                            recipients=layer3)
            total_size_2 += size
            total_time_2 += time_spent
            two_layer_total_network_time += total_network_time
        log_file.write(
            f"第二层向第三层的支付通信量大小为：{total_size_2} bytes, 创建交易和签名的总时间为：{total_time_2:.6f} s\n")
        tx_size = int(len(tx.serialize()) / 2)
        print(f"关闭通道交易大小为{tx_size}bytes")
        # 计算交易费用
        fee = math.ceil(feerate * tx_size)
        print(f"关闭通道的费用为: {fee}satoshi,{fee * 61731.91 / 100000000}$")
        total_size = total_size_1 + total_size_2
        total_time = total_time_1 + total_time_2
        end_total_time = time.perf_counter()
        total_duration = end_total_time - start_total_time
        throughput = 2 * (user_num / 3) * (user_num / 3) / total_duration

        log_file.write(f"总通信量大小为：{total_size} bytes\n")
        log_file.write(f"创建交易和签名的总时间为：{total_time:.6f} s\n")
        log_file.write(f"通信总时间为：{two_layer_total_network_time:.6f} s\n")
        log_file.write(f"完成所有支付所需总时间为：{total_duration:.6f} s\n")
        log_file.write(f"吞吐量为：{throughput} Transactions/s\n")
        log_file.write('----------------------------------\n')
        print(f"更新总通信量大小为：{total_size} bytes\n")
        print(f"创建交易和签名的总时间为：{total_time:.6f} s\n")
        print(f"通信总时间为：{two_layer_total_network_time:.6f} s\n")
        print(f"完成所有支付所需总时间为：{total_duration:.6f} s\n")
        print(f"吞吐量为：{throughput} Transactions/s\n")

        print('----------------------------------\n')


def initialize_users(user_num, user_list):
    users = {}
    utxos = {}
    selected_users = {k: v for k, v in list(user_list.items())[:user_num]}  # 选择前n个用户
    port = 10000
    for i, (key, user) in enumerate(selected_users.items()):
        while True:
            try:
                users[key] = User(key, user, port=port, is_committee_member=(i < 3))
                users[key].utxo = TxInput(user["utxos"][0]["txid"], user["utxos"][0]["vout"])
                break
            except OSError:
                port += 1  # 如果端口被占用，尝试下一个端口
        utxos[key] = TxInput(user["utxos"][0]["txid"], user["utxos"][0]["vout"])
        port += 1  # 确保每个用户使用不同的端口
    return users, utxos, selected_users


def split_users(users, selected_users, user_num, committee_num):
    layer1 = {}
    layer2 = {}
    layer3 = {}
    committee = {}
    # keys = list(users.keys())
    for i, key in enumerate(selected_users):
        if i < user_num // 3:
            layer1[key] = users[key]
        elif i < 2 * user_num // 3:
            layer2[key] = users[key]
        else:
            layer3[key] = users[key]
        if i < committee_num:
            committee[key] = users[key]
    return layer1, layer2, layer3, committee


def process_payment(log_file, sender_key, sender, tx_in_channel, distribution, users, committee, committee_num,
                    committee_threshold, recipients, sender_proxy_user=None, out_sender_key=None,
                    recipient_proxy_user=None, out_recipient_key=None):
    total_size = 0
    total_time = 0
    send_receive_times = []
    total_network_time = 0
    total_tpc_update_time = 0

    payments = {receiver_key: 0.01 for receiver_key in recipients.keys()}
    condition = {receiver_key: {"num": 1000} for receiver_key in recipients.keys()}

    if sender_key not in distribution:
        raise KeyError(f"Sender key {sender_key} not in distribution")

    distribution = update_distribution(distribution, sender_key, payments)
    log_file.write(f"更新的分布: {distribution}\n")

    start_time = time.perf_counter()
    redeem_script = scripts.get_script_MPCTXs(users, committee_num, committee_threshold)
    tx = sender.create_transaction(tx_in_channel, distribution, redeem_script)
    creation_time = time.perf_counter() - start_time
    log_file.write(f"创建交易时间: {creation_time:.6f} s\n")

    start_time = time.perf_counter()
    sig_s = sender.sign_transaction(tx, 0)
    signing_time_s = time.perf_counter() - start_time
    log_file.write(f"发送方{sender_key}签名时间: {signing_time_s:.6f} s\n")

    if sender_proxy_user is not None:
        tx_input = join_channel_info[out_sender_key]['txid']
        if tx_input is not None:
            tpctx, tpcdistribution, tpc_total_time, tpc_send_receive_time = join_channel.update_channel(tx_input, users[
                out_sender_key],
                                                                                                        users[
                                                                                                            sender_proxy_user],
                                                                                                        0.01,
                                                                                                        join_channel_info[
                                                                                                            out_sender_key][
                                                                                                            'distribution'])
            join_channel_info[out_sender_key] = {
                'proxy_user': sender_proxy_user,
                'txid': join_channel_info[out_sender_key]['txid'],
                'distribution': tpcdistribution
            }
            send_receive_times.append(tpc_send_receive_time)
            total_network_time += tpc_send_receive_time
            total_tpc_update_time += tpc_total_time
            print(f"本次TPC更新耗时：{tpc_total_time},TPC总更新耗时：{total_tpc_update_time:.6f}")
            log_file.write(f"TPC更新耗时: {total_tpc_update_time:.6f} s\n")

    if recipient_proxy_user is not None:

        tx_input = join_channel_info[out_recipient_key]['txid']
        if tx_input is not None:
            tpctx, tpcdistribution, tpc_total_time, tpc_send_receive_time = join_channel.update_channel(tx_input, users[
                recipient_proxy_user],
                                                                                                        users[
                                                                                                            out_recipient_key],
                                                                                                        0.01,
                                                                                                        join_channel_info[
                                                                                                            out_recipient_key][
                                                                                                            'distribution'])
            join_channel_info[out_recipient_key] = {
                'proxy_user': recipient_proxy_user,
                'txid': join_channel_info[out_recipient_key]['txid'],
                'distribution': tpcdistribution
            }
            send_receive_times.append(tpc_send_receive_time)
            total_network_time += tpc_send_receive_time
            total_tpc_update_time += tpc_total_time
            print(f"本次TPC更新耗时：{tpc_total_time},TPC总更新耗时：{total_tpc_update_time:.6f}")
            log_file.write(f"TPC更新耗时: {total_tpc_update_time:.6f} s\n")

    content_tocr = {"tx": tx.serialize(), "sig_s": sig_s, "condition": condition}
    content_tocr_json = json.dumps(content_tocr)
    content_tocr_size = len(content_tocr_json.encode('utf-8'))
    content_tocr_size_total = content_tocr_size * (committee_num + len(recipients))

    start_time = sender.send_message(content_tocr_json, committee[next(iter(committee))].port)
    message, end_time = committee[next(iter(committee))].receive_message()
    network_time_s = end_time - start_time
    total_network_time += network_time_s
    log_file.write(f"发送到委员会的时间: {network_time_s:.6f} s\n")
    log_file.write(f"发送方广播总字节数: {content_tocr_size_total} bytes\n")

    first_receiver_key = next(iter(recipients))
    first_receiver = recipients[first_receiver_key]
    start_time = time.perf_counter()
    sig_r = first_receiver.sign_transaction(tx, 0, sig_s)
    signing_time_r = time.perf_counter() - start_time
    log_file.write(f"{first_receiver_key}签名时间: {signing_time_r:.6f} s\n")

    content_r1toc = {"sig_r": sig_r, "num": 1000}
    content_r1toc_json = json.dumps(content_r1toc)
    content_r1toc_size = len(content_r1toc_json.encode('utf-8'))
    content_rtoc_size_total = content_r1toc_size * committee_num

    start_time = first_receiver.send_message(content_r1toc_json, committee[next(iter(committee))].port)
    message, end_time = committee[next(iter(committee))].receive_message()
    network_time_r = end_time - start_time
    total_network_time += network_time_r
    log_file.write(f"接收方广播时间: {network_time_r:.6f} s\n")
    log_file.write(f"接收方广播总字节数: {content_rtoc_size_total} bytes\n")

    sig_committee = []
    total_committee_broadcast_size = 0
    total_signing_time_c = 0
    previous_sig = sig_r
    for j, (committee_key, committee_member) in enumerate(committee.items()):
        if j >= committee_threshold:
            break
        start_time = time.perf_counter()
        sig_c = committee_member.sign_transaction(tx, 0, previous_sig)
        signing_time_c = time.perf_counter() - start_time
        total_signing_time_c += signing_time_c
        log_file.write(f"委员会成员{committee_key}签名时间: {signing_time_c:.6f} s\n")
        previous_sig = sig_c

        sig_committee.append(sig_c)
        if len(sig_committee) < committee_threshold:
            content_to_otherc = {"sig_c": sig_c}
            content_to_otherc_json = json.dumps(content_to_otherc)
            content_to_otherc_size = len(content_to_otherc_json.encode('utf-8'))
            remaining_committee_members = committee_num - len(sig_committee)
            content_to_otherc_total = content_to_otherc_size * remaining_committee_members
            total_committee_broadcast_size += content_to_otherc_total
            log_file.write(f"委员会成员{committee_key} 广播总字节数: {content_to_otherc_total} bytes\n")
            start_time = committee_member.send_message(content_to_otherc_json, committee[next(iter(committee))].port)
            message, end_time = committee[next(iter(committee))].receive_message()
            network_time_c = end_time - start_time
            total_network_time += network_time_c
            log_file.write(f"委员会成员{committee_key} 广播时间: {network_time_c:.6f} s\n")

    log_file.write(f"委员会门限签名总耗时: {total_signing_time_c:.6f} s\n")
    log_file.write(f"委员会门限签名广播总字节数: {total_committee_broadcast_size} bytes\n")
    tx_in_channel.script_sig = Script([0] + sig_c + [redeem_script.to_hex()])
    content_tor = {"sig_c": sig_c}
    content_tor_json = json.dumps(content_tor)
    content_tor_size = len(content_tor_json.encode('utf-8'))
    log_file.write(f"委员会发给接收方的总字节数: {content_tor_size} bytes\n")

    total_size += content_tocr_size_total + content_rtoc_size_total + total_committee_broadcast_size + content_tor_size
    total_time += creation_time + signing_time_s + signing_time_r + total_signing_time_c + network_time_s + network_time_r + network_time_c

    for send_receive_time in send_receive_times:
        total_time += send_receive_time
        total_network_time += send_receive_time

    return total_size, total_time, total_network_time, distribution, tx, total_tpc_update_time


def update_distribution(distribution: Dict[str, float], payer: str, payments: Dict[str, float]) -> Dict[str, float]:
    # print(distribution, payer, payments)
    new_distribution = distribution.copy()
    total_payment = sum(payments.values()) * SATOSHIS_PER_BTC
    if new_distribution[payer] < total_payment:
        raise ValueError("支付用户的余额不足")
    new_distribution[payer] -= total_payment
    for payee, amount in payments.items():
        new_distribution[payee] += amount * SATOSHIS_PER_BTC
    return new_distribution


def hash256(hexstring: str) -> str:
    data = binascii.unhexlify(hexstring)
    h1 = hashlib.sha256(data)
    h2 = hashlib.sha256(h1.digest())
    return h2.hexdigest()


def create_MPCTX_funding(users, utxos, committee_num, committee_threshold, c, feerate):
    TXf_MPC = txs.get_MPCTX_funding(utxos, users, c, feerate, committee_num, committee_threshold)
    txf_id = hash256(TXf_MPC.serialize())
    return TxInput(txf_id, 0), TXf_MPC


def log_payment(log_file, layer1, layer2, layer3, tx_in_channel, distribution, users, committee, committee_num,
                committee_threshold, joining_users=None, proxy_users=None):
    total_size = 0
    total_time = 0
    total_transactions = 0
    total_communication_time = 0
    two_layer_total_tpc_update_time = 0

    start_total_time = time.perf_counter()

    def get_actual_user(user_key):
        if joining_users and user_key in joining_users:
            return proxy_mapping.get(user_key, user_key)
        return user_key

    # 第一层向第二层支付
    for sender_key, sender in layer1.items():
        for recipient_key in layer2.keys():
            actual_sender_key = get_actual_user(sender_key)
            actual_recipient_key = get_actual_user(recipient_key)
            if joining_users and (sender_key in joining_users or recipient_key in joining_users):
                sender_proxy = proxy_mapping.get(sender_key) if sender_key in joining_users else None
                recipient_proxy = proxy_mapping.get(recipient_key) if recipient_key in joining_users else None
                if sender_proxy and recipient_proxy:
                    size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                        log_file,
                        actual_sender_key,
                        users[actual_sender_key],
                        tx_in_channel,
                        distribution, users,
                        committee, committee_num,
                        committee_threshold,
                        {actual_recipient_key:
                             layer2[
                                 recipient_key]},
                        sender_proxy_user=sender_proxy,
                        out_sender_key=sender_key,
                        recipient_proxy_user=recipient_proxy,
                        out_recipient_key=recipient_key)
                    two_layer_total_tpc_update_time += total_tpc_update_time
                    payment_info = f"第1层的{sender_key}（通过代理 {sender_proxy}）向第2层的{recipient_key}（通过代理 {recipient_proxy}）支付"
                elif sender_proxy:
                    size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                        log_file,
                        actual_sender_key,
                        users[actual_sender_key],
                        tx_in_channel,
                        distribution, users,
                        committee, committee_num,
                        committee_threshold,
                        {actual_recipient_key:
                             layer2[
                                 recipient_key]},
                        sender_proxy_user=sender_proxy,
                        out_sender_key=sender_key)
                    two_layer_total_tpc_update_time += total_tpc_update_time
                    payment_info = f"第1层的{sender_key}（通过代理 {sender_proxy}）向第2层的{recipient_key}支付"
                else:
                    size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                        log_file,
                        actual_sender_key,
                        users[actual_sender_key],
                        tx_in_channel,
                        distribution, users,
                        committee, committee_num,
                        committee_threshold,
                        {actual_recipient_key:
                             layer2[
                                 recipient_key]},
                        recipient_proxy_user=recipient_proxy,
                        out_recipient_key=recipient_key)
                    two_layer_total_tpc_update_time += total_tpc_update_time
                    payment_info = f"第1层的{sender_key}向第2层的{recipient_key}（通过代理 {recipient_proxy}）支付"
            else:
                size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                    log_file, sender_key, sender,
                    tx_in_channel,
                    distribution, users, committee,
                    committee_num,
                    committee_threshold,
                    {recipient_key: layer2[
                        recipient_key]})
                two_layer_total_tpc_update_time += total_tpc_update_time
                payment_info = f"第1层的{sender_key}向第2层的{recipient_key}支付"

            log_file.write(payment_info + "\n")
            print(payment_info)

            total_size += size
            total_time += time_spent
            total_communication_time += time_spent  # 累积通信时延
            total_transactions += 1

    # 第二层向第三层支付
    for sender_key, sender in layer2.items():
        for recipient_key in layer3.keys():
            actual_sender_key = get_actual_user(sender_key)
            actual_recipient_key = get_actual_user(recipient_key)
            if joining_users and (sender_key in joining_users or recipient_key in joining_users):
                sender_proxy = proxy_mapping.get(sender_key) if sender_key in joining_users else None
                recipient_proxy = proxy_mapping.get(recipient_key) if recipient_key in joining_users else None
                if sender_proxy and recipient_proxy:
                    size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                        log_file,
                        actual_sender_key,
                        users[actual_sender_key],
                        tx_in_channel,
                        distribution, users,
                        committee, committee_num,
                        committee_threshold,
                        {actual_recipient_key:
                             layer3[
                                 recipient_key]},
                        sender_proxy_user=sender_proxy,
                        out_sender_key=sender_key,
                        recipient_proxy_user=recipient_proxy,
                        out_recipient_key=recipient_key)
                    two_layer_total_tpc_update_time += total_tpc_update_time
                    payment_info = f"第2层的{sender_key}（通过代理 {sender_proxy}）向第3层的{recipient_key}（通过代理 {recipient_proxy}）支付"
                elif sender_proxy:
                    size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                        log_file,
                        actual_sender_key,
                        users[actual_sender_key],
                        tx_in_channel,
                        distribution, users,
                        committee, committee_num,
                        committee_threshold,
                        {actual_recipient_key:
                             layer3[
                                 recipient_key]},
                        sender_proxy_user=sender_proxy,
                        out_sender_key=sender_key)
                    two_layer_total_tpc_update_time += total_tpc_update_time
                    payment_info = f"第2层的{sender_key}（通过代理 {sender_proxy}）向第3层的{recipient_key}支付"
                else:
                    size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                        log_file,
                        actual_sender_key,
                        users[actual_sender_key],
                        tx_in_channel,
                        distribution, users,
                        committee, committee_num,
                        committee_threshold,
                        {actual_recipient_key:
                             layer3[
                                 recipient_key]},
                        recipient_proxy_user=recipient_proxy,
                        out_recipient_key=recipient_key)
                    two_layer_total_tpc_update_time += total_tpc_update_time
                    payment_info = f"第2层的{sender_key}向第3层的{recipient_key}（通过代理 {recipient_proxy}）支付"
            else:
                size, time_spent, total_network_time, distribution, tx, total_tpc_update_time = process_payment(
                    log_file, sender_key, sender,
                    tx_in_channel,
                    distribution, users, committee,
                    committee_num,
                    committee_threshold,
                    {recipient_key: layer3[
                        recipient_key]})
                two_layer_total_tpc_update_time += total_tpc_update_time
                payment_info = f"第2层的{sender_key}向第3层的{recipient_key}支付"

            log_file.write(payment_info + "\n")
            print(payment_info)
            total_size += size
            total_time += time_spent
            total_communication_time += time_spent  # 累积通信时延
            total_transactions += 1

    end_total_time = time.perf_counter()
    total_duration = end_total_time - start_total_time

    throughput = total_transactions / total_duration

    log_file.write(
        f"总通信量大小为：{total_size} bytes, 创建交易和签名的总时间为：{total_time:.6f} s, 总时延为：{total_duration:.6f} s\n")
    log_file.write(f"总交易数量为：{total_transactions}, 吞吐量为：{throughput:.6f} transactions/s\n")
    log_file.write(f"总通信时延为：{total_communication_time:.6f} s\n")

    return distribution, total_transactions, total_communication_time, total_network_time, two_layer_total_tpc_update_time


def join_user_and_log_payment(log_file, user_list, users, utxos, layer1, layer2, layer3, committee, distribution,
                              tx_in_channel, join_round, accumulated_selected_users, accumulated_proxy_users,
                              tpc_distributions):
    if join_round == 1:
        new_user_key = list(user_list.keys())[6]  # 选择第7个用户
        new_proxy_key = list(user_list.keys())[0]
        layer = layer1
        layer_num = 1
    elif join_round == 2:
        new_user_key = list(user_list.keys())[7]  # 选择第8个用户
        new_proxy_key = list(user_list.keys())[2]
        layer = layer2
        layer_num = 2
    elif join_round == 3:
        new_user_key = list(user_list.keys())[8]  # 选择第9个用户
        new_proxy_key = list(user_list.keys())[4]
        layer = layer3
        layer_num = 3
    else:
        return accumulated_selected_users, accumulated_proxy_users, tpc_distributions, distribution

    accumulated_selected_users.append(new_user_key)
    accumulated_proxy_users.append(new_proxy_key)

    for selected_user_key, proxy_user_key in zip([new_user_key], [new_proxy_key]):
        user = user_list[selected_user_key]
        utxos[selected_user_key] = TxInput(user_list[selected_user_key]["utxos"][0]["txid"],
                                           user_list[selected_user_key]["utxos"][0]["vout"])
        port = 10000 + len(users)
        while True:
            try:
                users[selected_user_key] = User(selected_user_key, user, port=port, is_committee_member=False)
                users[selected_user_key].utxo = utxos[selected_user_key]
                break
            except OSError:
                port += 1  # 如果端口被占用，尝试下一个端口

        utxos[selected_user_key] = TxInput(user["utxos"][0]["txid"], user["utxos"][0]["vout"])
        # 将新用户添加到层中
        layer[selected_user_key] = users[selected_user_key]

        log_file.write(f"第{join_round}轮加入: 第{layer_num}层的{selected_user_key}通过代理{proxy_user_key}\n")
        print(f"第{join_round}轮加入: 第{layer_num}层的{selected_user_key}通过代理{proxy_user_key}\n")

        # 更新代理映射
        proxy_mapping[selected_user_key] = proxy_user_key

        # 创建双方支付通道并得到分布
        tpc_input, tpc_id, tpc_create_time = join_channel.create_funding_transaction(users[selected_user_key],
                                                                                     users[proxy_user_key], 1)
        # print(tpc_input)
        tpc_distribution = {selected_user_key: 1 * SATOSHIS_PER_BTC, proxy_user_key: 1 * SATOSHIS_PER_BTC}
        tpc_distributions.append(tpc_distribution)
        # # 记录用户和代理的UTXO映射
        # user_proxy_utxo_mapping[(selected_user_key, proxy_user_key)] = tpc_input

        # 更新join_channel_info字典
        join_channel_info[selected_user_key] = {
            'proxy_user': proxy_user_key,
            'txid': tpc_input,
            'distribution': tpc_distribution
        }

    # 记录并支付，更新distribution不包含加入用户
    distribution, total_transactions, total_communication_time, total_network_time, two_layer_total_tpc_update_time = log_payment(
        log_file, layer1,
        layer2, layer3,
        tx_in_channel,
        distribution, users,
        committee, 3, 2,
        joining_users=accumulated_selected_users,
        proxy_users=accumulated_proxy_users)
    total_tpc_create_update_time = two_layer_total_tpc_update_time + tpc_create_time

    return accumulated_selected_users, accumulated_proxy_users, tpc_distributions, distribution, total_transactions, total_communication_time, total_network_time, total_tpc_create_update_time


if __name__ == "__main__":
    with open("users_96.txt", "r") as f:
        user_list = json.load(f)
    print(f"测试用户数量: 6，委员会数量： 3，委员会门限： 2。")
    join_test(user_list)

    # user_counts = [6, 12, 24, 48, 96]
    # committee_num = 3
    # committee_threshold = 2
    # for user_num in user_counts:
    #     print(f"测试用户数量: {user_num}，委员会数量： {committee_num}，委员会门限： {committee_threshold}。")
    #     main(user_num, committee_num, committee_threshold)
