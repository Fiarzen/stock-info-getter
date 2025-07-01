# test/conftest.py
"""
Pytest configuration file to handle imports and setup.
"""

import sys
import os
import pytest

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Fixtures for common test data
@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        'AAPL': {
            'Company': 'Apple Inc.',
            'Current Price': 175.43,
            'Shares Short': 95000000,
            'Shares Outstanding': 15500000000,
            'Short Interest Ratio': 0.613,
            'Market Cap': 2720000000000
        },
        'MSFT': {
            'Company': 'Microsoft Corporation',
            'Current Price': 378.85,
            'Shares Short': 45000000,
            'Shares Outstanding': 7430000000,
            'Short Interest Ratio': 0.606,
            'Market Cap': 2815000000000
        }
    }

@pytest.fixture
def mock_yfinance_response():
    """Mock yfinance API response."""
    return {
        'shortName': 'Apple Inc.',
        'currentPrice': 175.43,
        'sharesShort': 95000000,
        'sharesOutstanding': 15500000000,
        'marketCap': 2720000000000,
        'floatShares': 15400000000,
        'sharesShortPriorMonth': 90000000
    }

@pytest.fixture
def error_response():
    """Mock error response."""
    return "Error fetching data"

# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")