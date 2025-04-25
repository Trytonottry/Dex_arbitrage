# Требования: pip install web3 python-dotenv
# Настройка: создайте .env с INFURA_URL, PRIVATE_KEY, YOUR_ADDRESS
# Запуск: python dex_arbitrage.py
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import time
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# Настройка логирования
logging.basicConfig(filename='arbitrage.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Подключение к ноде
INFURA_URL = os.getenv('INFURA_URL')
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Ключи
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
YOUR_ADDRESS = w3.eth.account.from_key(PRIVATE_KEY).address

# ABI пула
UNISWAP_PAIR_ABI = json.loads('''
[{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"name":"reserve0","type":"uint112"},{"name":"reserve1","type":"uint112"},{"name":"blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"}]
''')

# Адреса пулов
POOLS = {
    'Uniswap': '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc',  # USDC/WETH
    'Sushiswap': '0x397FF1542f962076d0BFE58eA045FfA2d347ACa0'  # USDC/WETH
}

def get_price(pool_address):
    contract = w3.eth.contract(address=pool_address, abi=UNISWAP_PAIR_ABI)
    reserves = contract.functions.getReserves().call()
    return reserves[1] / reserves[0]  # WETH/USDC

def send_swap_transaction(amount_in, pool_address):
    # Упрощенный пример вызова swap (нужен контракт Uniswap Router)
    tx = {
        'from': YOUR_ADDRESS,
        'value': 0,
        'gas': 200000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': w3.eth.get_transaction_count(YOUR_ADDRESS)
    }
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()

def monitor_arbitrage():
    while True:
        try:
            prices = {dex: get_price(addr) for dex, addr in POOLS.items()}
            logging.info(f"Prices: {prices}")
            print(f"Prices: {prices}")

            # Проверка арбитража
            if prices['Uniswap'] < prices['Sushiswap'] * 0.99:  # Учитываем комиссии
                profit = (prices['Sushiswap'] - prices['Uniswap']) * 1000  # Для 1000 USDC
                if profit > 0.1:  # Порог профита
                    logging.info(f"Arbitrage opportunity: Buy on Uniswap, Sell on Sushiswap, Profit: {profit}")
                    # tx_hash = send_swap_transaction(1000 * 10**6, POOLS['Uniswap'])
                    # logging.info(f"Transaction sent: {tx_hash}")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    if not w3.is_connected():
        logging.error("Failed to connect to Ethereum node")
        exit(1)
    monitor_arbitrage()