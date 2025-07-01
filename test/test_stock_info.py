import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import yfinance as yf
from src.stock_info import StockInfo



class TestStockInfo:
    """Test suite for StockInfo class"""
    
    @pytest.fixture
    def stock_info(self):
        """Create a StockInfo instance for testing"""
        return StockInfo("AAPL")
    
    @pytest.fixture
    def mock_stock_data(self):
        """Mock stock data for testing"""
        return {
            'longName': 'Apple Inc.',
            'shortRatio': 2.5,
            'shortPercentOfFloat': 15.3,
            'sharesShort': 100000000,
            'sharesShortPriorMonth': 95000000,
            'floatShares': 650000000,
            'marketCap': 3000000000000,
            'currentPrice': 185.50
        }
    
    @pytest.fixture
    def mock_price_history(self):
        """Mock price history data"""
        mock_df = pd.DataFrame({
            'Close': [180.0, 182.5, 185.0, 185.50]
        })
        return mock_df

    def test_init_ticker_uppercase(self):
        """Test that ticker is converted to uppercase"""
        stock = StockInfo("aapl")
        assert stock.ticker == "AAPL"
    
    def test_init_creates_yfinance_ticker(self):
        """Test that yfinance Ticker object is created"""
        stock = StockInfo("AAPL")
        assert isinstance(stock.stock, yf.Ticker)
        assert stock.stock.ticker == "AAPL"

    @patch('yfinance.Ticker')
    def test_get_current_price_success(self, mock_ticker, stock_info, mock_price_history):
        """Test successful price retrieval"""
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_price_history
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.get_current_price()
        
        assert "The current price of AAPL is $185.50" in result
        mock_ticker_instance.history.assert_called_once_with(period="1d")

    @patch('yfinance.Ticker')
    def test_get_current_price_error(self, mock_ticker, stock_info):
        """Test price retrieval error handling"""
        # Setup mock to raise exception
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = Exception("API Error")
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.get_current_price()
        
        assert "Error fetching price for AAPL" in result
        assert "API Error" in result

    @patch('yfinance.Ticker')
    def test_get_short_interest_data_success(self, mock_ticker, stock_info, mock_stock_data):
        """Test successful short interest data retrieval"""
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_stock_data
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.get_short_interest_data()
        
        assert result['Symbol'] == 'AAPL'
        assert result['Company'] == 'Apple Inc.'
        assert result['Short Ratio'] == 2.5
        assert result['Short % of Float'] == 15.3
        assert result['Shares Short'] == 100000000

    @patch('yfinance.Ticker')
    def test_get_short_interest_data_error(self, mock_ticker, stock_info):
        """Test short interest data error handling"""
        # Setup mock to raise exception
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = Mock(side_effect=Exception("API Error"))
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.get_short_interest_data()
        
        assert 'Error' in result
        assert "API Error" in result['Error']

    @patch('yfinance.Ticker')
    def test_get_short_interest_summary_success(self, mock_ticker, stock_info, mock_stock_data):
        """Test successful short interest summary generation"""
        # Setup mock
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_stock_data
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.get_short_interest_summary()
        
        assert "Short Interest Summary for AAPL" in result
        assert "Apple Inc." in result
        assert "15.30%" in result
        assert "2.50" in result

    @patch('yfinance.Ticker')
    def test_get_short_interest_summary_with_none_values(self, mock_ticker, stock_info):
        """Test short interest summary with missing data"""
        # Setup mock with None values
        mock_data = {
            'longName': 'Apple Inc.',
            'shortRatio': None,
            'shortPercentOfFloat': None,
            'sharesShort': None,
            'floatShares': None
        }
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_data
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.get_short_interest_summary()
        
        assert "N/A" in result
        assert "Apple Inc." in result

    @patch('yfinance.Ticker')
    def test_is_heavily_shorted_true(self, mock_ticker, stock_info, mock_stock_data):
        """Test heavily shorted detection - true case"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_stock_data
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.is_heavily_shorted(10.0)
        
        assert result is True  # 15.3% > 10.0%

    @patch('yfinance.Ticker')
    def test_is_heavily_shorted_false(self, mock_ticker, stock_info, mock_stock_data):
        """Test heavily shorted detection - false case"""
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_stock_data
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.is_heavily_shorted(20.0)
        
        assert result is False  # 15.3% < 20.0%

    @patch('yfinance.Ticker')
    def test_is_heavily_shorted_no_data(self, mock_ticker, stock_info):
        """Test heavily shorted detection with no data"""
        mock_data = {'longName': 'Apple Inc.', 'shortPercentOfFloat': None}
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = mock_data
        mock_ticker.return_value = mock_ticker_instance
        stock_info.stock = mock_ticker_instance
        
        result = stock_info.is_heavily_shorted(10.0)
        
        assert result is False

    @patch('stock_info.StockInfo')
    def test_compare_short_interest_success(self, mock_stock_info_class):
        """Test successful comparison of multiple stocks"""
        # Mock multiple StockInfo instances
        mock_data_list = [
            {
                'Symbol': 'AAPL',
                'Company': 'Apple Inc.',
                'Short % of Float': 15.3,
                'Short Ratio': 2.5
            },
            {
                'Symbol': 'TSLA',
                'Company': 'Tesla Inc.',
                'Short % of Float': 25.8,
                'Short Ratio': 3.2
            }
        ]
        
        def mock_stock_info_side_effect(symbol):
            mock_instance = Mock()
            if symbol == 'AAPL':
                mock_instance.get_short_interest_data.return_value = mock_data_list[0]
            else:
                mock_instance.get_short_interest_data.return_value = mock_data_list[1]
            return mock_instance
        
        mock_stock_info_class.side_effect = mock_stock_info_side_effect
        
        result = StockInfo.compare_short_interest(['AAPL', 'TSLA'])
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.iloc[0]['Symbol'] == 'TSLA'  # Should be sorted by short % (highest first)
        assert result.iloc[1]['Symbol'] == 'AAPL'

    @patch('stock_info.StockInfo.compare_short_interest')
    def test_find_high_short_interest_stocks(self, mock_compare):
        """Test finding high short interest stocks"""
        # Mock data with varying short interest
        mock_df = pd.DataFrame([
            {'Symbol': 'LOW', 'Short % of Float': 5.0},
            {'Symbol': 'HIGH1', 'Short % of Float': 15.0},
            {'Symbol': 'HIGH2', 'Short % of Float': 20.0},
            {'Symbol': 'NONE', 'Short % of Float': None}
        ])
        mock_compare.return_value = mock_df
        
        result = StockInfo.find_high_short_interest_stocks(['TEST'], min_short_percent=10.0)
        
        assert len(result) == 2
        assert 'HIGH1' in result['Symbol'].values
        assert 'HIGH2' in result['Symbol'].values
        assert 'LOW' not in result['Symbol'].values

    def test_compare_short_interest_empty_results(self):
        """Test comparison with no valid results"""
        with patch('stock_info.StockInfo') as mock_class:
            mock_instance = Mock()
            mock_instance.get_short_interest_data.return_value = {'Error': 'No data'}
            mock_class.return_value = mock_instance
            
            result = StockInfo.compare_short_interest(['INVALID'])
            
            assert result.empty

    @pytest.mark.parametrize("symbols,expected_calls", [
        (['AAPL'], 1),
        (['AAPL', 'TSLA'], 2),
        (['AAPL', 'TSLA', 'MSFT'], 3),
    ])
    def test_compare_short_interest_concurrent_calls(self, symbols, expected_calls):
        """Test that concurrent calls are made for multiple symbols"""
        with patch('stock_info.StockInfo') as mock_class:
            mock_instance = Mock()
            mock_instance.get_short_interest_data.return_value = {
                'Symbol': 'TEST',
                'Short % of Float': 10.0
            }
            mock_class.return_value = mock_instance
            
            StockInfo.compare_short_interest(symbols, max_workers=2)
            
            assert mock_class.call_count == expected_calls


class TestStockInfoIntegration:
    """Integration tests that use real API calls (slower, run separately)"""
    
    @pytest.mark.slow
    def test_real_api_call_aapl(self):
        """Test with real API call to AAPL"""
        stock = StockInfo("AAPL")
        
        # Test price retrieval
        price_result = stock.get_current_price()
        assert "The current price of AAPL is $" in price_result
        
        # Test short interest data
        short_data = stock.get_short_interest_data()
        assert short_data['Symbol'] == 'AAPL'
        assert 'Company' in short_data
    
    @pytest.mark.slow
    def test_real_api_comparison(self):
        """Test real API comparison with multiple stocks"""
        symbols = ['AAPL', 'MSFT']
        result = StockInfo.compare_short_interest(symbols)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(symbols)  # Some might fail
        if not result.empty:
            assert 'Symbol' in result.columns


# Pytest configuration and fixtures
@pytest.fixture(scope="session")
def setup_test_environment():
    """Setup test environment"""
    print("Setting up test environment...")
    yield
    print("Tearing down test environment...")


# Custom markers for different test types
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (real API calls)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, mocked)"
    )


if __name__ == "__main__":
    # Run tests programmatically
    pytest.main([__file__, "-v"])