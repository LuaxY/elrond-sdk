import logging
import sys
import time
from argparse import ArgumentParser

from erdpy.accounts import Account
from erdpy.proxy import ElrondProxy
from erdpy.transactions import (PlainTransaction, PreparedTransaction,
                                TransactionPayloadToSign)
from erdpy.wallet import signing
from erdpy import errors

logger = logging.getLogger("bon_mission4")

counter = 0


def main():
    parser = ArgumentParser()
    parser.add_argument("--proxy", default="https://api.elrond.com")
    parser.add_argument("--pem", required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)

    print("Press CTRL+C to stop the script execution")

    proxy = ElrondProxy(args.proxy)
    sender = Account(pem_file=args.pem)

    while True:
        sleep_time = 15
        print(f"Sleeping {sleep_time} seconds...")
        time.sleep(sleep_time)

        try:
            sender.sync_nonce(proxy)
            print(f"Sender nonce recalled: nonce={sender.nonce}.")
            send_txs(proxy, sender, 100)
        except errors.ProxyRequestError as err:
            logger.error(err)


def send_txs(proxy, sender, num):
    for i in range(0, num):
        send_one_tx(proxy, sender, "erd1hqplnafrhnd4zv846wumat2462jy9jkmwxtp3nwmw8ye9eclr6fq40f044")
        sender.nonce += 1
        send_one_tx(proxy, sender, "erd1utftdvycwgl3xt0r44ekncentlxgmhucxfq3jt6cjz0w7h6qjchsjarml6")
        sender.nonce += 1


def send_one_tx(proxy, sender, receiver_address):
    plain = PlainTransaction()
    plain.nonce = sender.nonce
    plain.value = "20000000000000000"  # 0.02 ERD
    plain.sender = sender.address.bech32()
    plain.receiver = receiver_address
    plain.gasPrice = 200000000000
    plain.gasLimit = 50000
    plain.data = ""

    payload = TransactionPayloadToSign(plain)
    signature = signing.sign_transaction(payload, sender.pem_file)
    prepared = PreparedTransaction(plain, signature)
    prepared.send(proxy)

    global counter
    counter += 1
    print(f"Sent transaction #{counter}, with nonce = {plain.nonce}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logger.fatal(err)
        sys.exit(1)
