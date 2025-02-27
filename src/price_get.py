import yfinance as yf


class StockInfo:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)

    def get_current_price(self):
        try:
            current_price = self.stock.history(period="1d")['Close'].iloc[-1]
            return f"The current price of {self.ticker} is ${current_price:.2f}"
        except Exception as e:
            return f"Error fetching price for {self.ticker}: {str(e)}"

def main():
    ticker = input("Enter a stock ticker symbol (e.g., AAPL, TSLA, GOOG): ").strip()
    fetcher = StockInfo(ticker)
    print(fetcher.get_current_price())

if __name__ == "__main__":
    main()
