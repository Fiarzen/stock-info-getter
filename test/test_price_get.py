import pytest
from src.price_get import StockInfo  

@pytest.mark.parametrize("ticker", ["AAPL", "TSLA", "GOOG"])
def test_get_current_price_valid_ticker(ticker):
    fetcher = StockInfo(ticker)
    price = fetcher.get_current_price()
    assert isinstance(price, str)
    assert f"The current price of {ticker}" in price  

def test_get_current_price_invalid_ticker():
    fetcher = StockInfo("INVALID_TICKER")
    price = fetcher.get_current_price()
    assert "Error fetching price" in price  

def test_get_current_price_empty_ticker():
    fetcher = StockInfo("")
    price = fetcher.get_current_price()
    assert "Error fetching price" in price  