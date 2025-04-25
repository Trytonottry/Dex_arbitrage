import pytest
from dex_arbitrage import get_price, POOLS

def test_get_price():
    price = get_price(POOLS['Uniswap'])
    assert isinstance(price, float)
    assert price > 0

def test_compare_prices():
    prices = {dex: get_price(addr) for dex, addr in POOLS.items()}
    assert len(prices) == 2
    assert all(isinstance(p, float) for p in prices.values())