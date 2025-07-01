import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional


class StockInfo:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)

    def get_current_price(self):
        try:
            current_price = self.stock.history(period="1d")["Close"].iloc[-1]
            return f"The current price of {self.ticker} is ${current_price:.2f}"
        except Exception as e:
            return f"Error fetching price for {self.ticker}: {str(e)}"

    def get_short_interest_data(self) -> Dict:
        """Get comprehensive short interest data for the stock"""
        try:
            info = self.stock.info

            short_data = {
                "Symbol": self.ticker,
                "Company": info.get("longName", "N/A"),
                "Short Ratio": info.get("shortRatio"),
                "Short % of Float": info.get("shortPercentOfFloat"),
                "Shares Short": info.get("sharesShort"),
                "Shares Short Prior Month": info.get("sharesShortPriorMonth"),
                "Float": info.get("floatShares"),
                "Market Cap": info.get("marketCap"),
                "Current Price": info.get("currentPrice"),
            }

            return short_data
        except Exception as e:
            return {
                "Error": f"Error getting short interest data for {self.ticker}: {str(e)}"
            }

    def get_short_interest_summary(self) -> str:
        """Get a formatted summary of short interest data"""
        data = self.get_short_interest_data()

        if "Error" in data:
            return data["Error"]

        summary = f"\n--- Short Interest Summary for {self.ticker} ---\n"
        summary += f"Company: {data['Company']}\n"

        if data["Short % of Float"]:
            summary += f"Short % of Float: {data['Short % of Float']:.2f}%\n"
        else:
            summary += "Short % of Float: N/A\n"

        if data["Short Ratio"]:
            summary += f"Short Ratio (Days to Cover): {data['Short Ratio']:.2f}\n"
        else:
            summary += "Short Ratio: N/A\n"

        if data["Shares Short"]:
            summary += f"Shares Short: {data['Shares Short']:,}\n"
        else:
            summary += "Shares Short: N/A\n"

        if data["Float"]:
            summary += f"Float: {data['Float']:,}\n"
        else:
            summary += "Float: N/A\n"

        return summary

    @staticmethod
    def compare_short_interest(
        symbols: List[str], max_workers: int = 10
    ) -> pd.DataFrame:
        """
        Compare short interest data across multiple stocks

        Args:
            symbols: List of stock symbols to compare
            max_workers: Number of concurrent workers for API calls

        Returns:
            DataFrame with short interest comparison
        """

        def get_stock_short_data(symbol):
            try:
                stock_info = StockInfo(symbol)
                return stock_info.get_short_interest_data()
            except Exception as e:
                print(f"Error getting data for {symbol}: {e}")
                return None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(get_stock_short_data, symbols))

        # Filter out None results and errors
        valid_results = [r for r in results if r is not None and "Error" not in r]

        if not valid_results:
            print("No valid data retrieved for any symbols")
            return pd.DataFrame()

        df = pd.DataFrame(valid_results)

        # Sort by short percentage of float (highest first)
        if "Short % of Float" in df.columns:
            df = df.sort_values("Short % of Float", ascending=False, na_last=True)

        return df

    @staticmethod
    def find_high_short_interest_stocks(
        symbols: List[str], min_short_percent: float = 10.0
    ) -> pd.DataFrame:
        """
        Find stocks with short interest above a certain threshold

        Args:
            symbols: List of stock symbols to check
            min_short_percent: Minimum short percentage of float to include

        Returns:
            DataFrame with high short interest stocks
        """
        df = StockInfo.compare_short_interest(symbols)

        if df.empty:
            return df

        # Filter for high short interest
        high_short_df = df[
            (df["Short % of Float"].notna())
            & (df["Short % of Float"] >= min_short_percent)
        ]

        return high_short_df

    def is_heavily_shorted(self, threshold: float = 10.0) -> bool:
        """
        Check if the stock is heavily shorted based on short % of float

        Args:
            threshold: Short percentage threshold to consider "heavily shorted"

        Returns:
            True if heavily shorted, False otherwise
        """
        data = self.get_short_interest_data()

        if "Error" in data or not data.get("Short % of Float"):
            return False

        return data["Short % of Float"] >= threshold


# Example usage:
if __name__ == "__main__":
    # Single stock analysis
    stock = StockInfo("GME")
    print(stock.get_current_price())
    print(stock.get_short_interest_summary())
    print(f"Is heavily shorted (>20%): {stock.is_heavily_shorted(20.0)}")

    # Compare multiple stocks
    symbols = ["GME", "AMC", "TSLA", "AAPL", "MSFT", "NVDA"]
    comparison_df = StockInfo.compare_short_interest(symbols)
    print("\n--- Short Interest Comparison ---")
    print(
        comparison_df[["Symbol", "Company", "Short % of Float", "Short Ratio"]].head()
    )

    # Find high short interest stocks
    high_short_df = StockInfo.find_high_short_interest_stocks(
        symbols, min_short_percent=5.0
    )
    print(f"\n--- Stocks with >5% Short Interest ---")
    print(high_short_df[["Symbol", "Company", "Short % of Float", "Short Ratio"]])

    # Save results
    if not comparison_df.empty:
        comparison_df.to_csv("short_interest_comparison.csv", index=False)
        print("\nResults saved to 'short_interest_comparison.csv'")
