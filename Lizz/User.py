import socket
import time
from typing import Dict

from bitcoinutils.keys import PrivateKey, PublicKey, P2pkhAddress
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxOutput, TxInput
import init

init.initNetwork()
SATOSHIS_PER_BTC = 100_000_000

class User:
    def __init__(self, name: str, user_info: Dict[str, str], port: int, is_committee_member: bool = False):
        self.name = name
        self.address = user_info['address']
        self.private_key = user_info['private_key']
        self.public_key = user_info['public_key']
        self.sk = PrivateKey(self.private_key)
        self.pk = PublicKey(self.public_key)
        self.p2pkh = P2pkhAddress(self.address).to_script_pub_key()
        self.port = port
        self.is_committee_member = is_committee_member
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', self.port))
        self.socket.listen(5)

    def create_transaction(self, tx_in: str, distribution: Dict[str, int], redeem_script: str):
        # 创建新交易
        tx_outs = [TxOutput(int(amount), redeem_script) for address, amount in distribution.items()]
        tx = Transaction([tx_in], tx_outs)
        return tx

    def sign_transaction(self, tx: Transaction, input_index: int, existing_signatures=None):
        if existing_signatures is None:
            existing_signatures = []
        sig = self.sk.sign_input(tx, input_index, self.p2pkh)
        new_signatures = existing_signatures + [sig]
        return new_signatures

    def send_message(self, message: str, recipient_port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', recipient_port))
            start_time = time.perf_counter()
            s.sendall(message.encode('utf-8'))
            s.close()
            return start_time

    def receive_message(self):
        conn, _ = self.socket.accept()
        with conn:
            message = conn.recv(1024).decode('utf-8')
            end_time = time.perf_counter()
            return message, end_time

    def close_socket(self):
        self.socket.close()

    def create_tpc_transaction(self, tx_in: TxInput, distribution: Dict[str, float], script_pub_key: Script) -> Transaction:
        tx_outs = [TxOutput(int(amount * SATOSHIS_PER_BTC), script_pub_key) for address, amount in distribution.items()]
        tx = Transaction([tx_in], tx_outs)
        return tx

