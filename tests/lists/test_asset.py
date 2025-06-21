"""
Unit tests for tickersnap Assets module.

Tests cover:
- Assets class functionality
- Asset filtering (stocks vs ETFs)
- Return value validation
- Error handling
- Edge cases
"""

from unittest.mock import Mock, patch

import pytest

from tickersnap.lists.asset import Assets
from tickersnap.lists.models import AssetData, AssetsListResponse, AssetType


class TestUnitAssets:
    """
    Unit test suite for Assets class with mocked API calls.
    """

    def test_assets_initialization(self):
        """Test Assets initialization with default and custom timeout."""
        # with default timeout
        assets = Assets()
        assert assets.timeout == 10

        # with custom timeout
        assets = Assets(timeout=30)
        assert assets.timeout == 30

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_get_all_stocks_basic(self, mock_assets_list_class):
        """Test get_all_stocks basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_assets_response()
        mock_client.get_data.return_value = mock_response

        # Test
        assets = Assets(timeout=15)
        result = assets.get_all_stocks()

        # Validate structure
        assert isinstance(result, list)
        assert len(result) == 2  # From mock - 2 stocks

        # Validate all returned items are stocks
        for asset in result:
            assert isinstance(asset, AssetData)
            assert asset.type == AssetType.STOCK

        # Validate specific data
        stock_tickers = [asset.ticker for asset in result]
        assert "RELIANCE" in stock_tickers
        assert "TCS" in stock_tickers

        # Verify API usage
        mock_assets_list_class.assert_called_once_with(timeout=15)
        mock_client.get_data.assert_called_once_with()

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_get_all_etfs_basic(self, mock_assets_list_class):
        """Test get_all_etfs basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_assets_response()
        mock_client.get_data.return_value = mock_response

        # Test
        assets = Assets(timeout=20)
        result = assets.get_all_etfs()

        # Validate structure
        assert isinstance(result, list)
        assert len(result) == 1  # From mock - 1 ETF

        # Validate all returned items are ETFs
        for asset in result:
            assert isinstance(asset, AssetData)
            assert asset.type == AssetType.ETF

        # Validate specific data
        etf_tickers = [asset.ticker for asset in result]
        assert "NIFTYBEES" in etf_tickers

        # Verify API usage
        mock_assets_list_class.assert_called_once_with(timeout=20)
        mock_client.get_data.assert_called_once_with()

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_get_all_assets_basic(self, mock_assets_list_class):
        """Test get_all_assets basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_assets_response()
        mock_client.get_data.return_value = mock_response

        # Test
        assets = Assets()
        result = assets.get_all_assets()

        # Validate structure
        assert isinstance(result, list)
        assert len(result) == 3  # From mock - all assets

        # Validate asset type distribution
        stock_count = sum(1 for asset in result if asset.type == AssetType.STOCK)
        etf_count = sum(1 for asset in result if asset.type == AssetType.ETF)
        assert stock_count == 2
        assert etf_count == 1

        # Validate all returned items are AssetData
        for asset in result:
            assert isinstance(asset, AssetData)
            assert asset.type in [AssetType.STOCK, AssetType.ETF]

        # Verify API usage
        mock_client.get_data.assert_called_once_with()

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_filtering_accuracy(self, mock_assets_list_class):
        """Test that filtering works correctly for different asset combinations."""
        # Setup mock with mixed assets
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client

        # Create response with more diverse mix
        mixed_response = self._create_mock_mixed_assets_response()
        mock_client.get_data.return_value = mixed_response

        assets = Assets()

        # Test stocks filtering
        stocks = assets.get_all_stocks()
        assert len(stocks) == 3
        assert all(asset.type == AssetType.STOCK for asset in stocks)
        stock_tickers = {asset.ticker for asset in stocks}
        assert stock_tickers == {"RELIANCE", "TCS", "HDFC"}

        # Test ETFs filtering
        etfs = assets.get_all_etfs()
        assert len(etfs) == 2
        assert all(asset.type == AssetType.ETF for asset in etfs)
        etf_tickers = {asset.ticker for asset in etfs}
        assert etf_tickers == {"NIFTYBEES", "BANKNIFTY"}

        # Test all assets (no filtering)
        all_assets = assets.get_all_assets()
        assert len(all_assets) == 5
        all_tickers = {asset.ticker for asset in all_assets}
        assert all_tickers == {"RELIANCE", "TCS", "HDFC", "NIFTYBEES", "BANKNIFTY"}

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_empty_results_handling(self, mock_assets_list_class):
        """Test handling when API returns empty results."""
        # Setup mock with empty response
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        empty_response = AssetsListResponse(success=True, data=[])
        mock_client.get_data.return_value = empty_response

        assets = Assets()

        # Test all methods return empty lists
        assert assets.get_all_stocks() == []
        assert assets.get_all_etfs() == []
        assert assets.get_all_assets() == []

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_only_stocks_scenario(self, mock_assets_list_class):
        """Test scenario where API returns only stocks."""
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client

        # Response with only stocks
        stocks_only_response = AssetsListResponse(
            success=True,
            data=[
                AssetData(
                    sid="RELIANCE",
                    name="Reliance Industries Ltd",
                    ticker="RELIANCE",
                    type=AssetType.STOCK,
                    slug="reliance-industries-ltd",
                    isin="INE002A01018",
                ),
                AssetData(
                    sid="TCS",
                    name="Tata Consultancy Services Ltd",
                    ticker="TCS",
                    type=AssetType.STOCK,
                    slug="tata-consultancy-services-ltd",
                    isin="INE467B01029",
                ),
            ],
        )
        mock_client.get_data.return_value = stocks_only_response

        assets = Assets()

        # Test results
        stocks = assets.get_all_stocks()
        etfs = assets.get_all_etfs()
        all_assets = assets.get_all_assets()

        assert len(stocks) == 2
        assert len(etfs) == 0
        assert len(all_assets) == 2

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_only_etfs_scenario(self, mock_assets_list_class):
        """Test scenario where API returns only ETFs."""
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client

        # Response with only ETFs
        etfs_only_response = AssetsListResponse(
            success=True,
            data=[
                AssetData(
                    sid="NIFTYBEES",
                    name="Nippon India ETF Nifty BeES",
                    ticker="NIFTYBEES",
                    type=AssetType.ETF,
                    slug="nippon-india-etf-nifty-bees",
                    isin="INF204KB17I5",
                )
            ],
        )
        mock_client.get_data.return_value = etfs_only_response

        assets = Assets()

        # Test results
        stocks = assets.get_all_stocks()
        etfs = assets.get_all_etfs()
        all_assets = assets.get_all_assets()

        assert len(stocks) == 0
        assert len(etfs) == 1
        assert len(all_assets) == 1

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_error_handling_api_failure(self, mock_assets_list_class):
        """Test error handling when API calls fail."""
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        mock_client.get_data.side_effect = Exception("API Error")

        assets = Assets()

        # Test that exceptions are properly propagated
        with pytest.raises(Exception, match="API Error"):
            assets.get_all_stocks()

        with pytest.raises(Exception, match="API Error"):
            assets.get_all_etfs()

        with pytest.raises(Exception, match="API Error"):
            assets.get_all_assets()

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_multiple_calls_different_methods(self, mock_assets_list_class):
        """Test multiple calls to different methods use fresh API calls."""
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_assets_response()
        mock_client.get_data.return_value = mock_response

        assets = Assets()

        # Call all methods
        stocks = assets.get_all_stocks()
        etfs = assets.get_all_etfs()
        all_assets = assets.get_all_assets()

        # Verify each method made its own API call
        assert mock_client.get_data.call_count == 3
        assert len(stocks) == 2
        assert len(etfs) == 1
        assert len(all_assets) == 3

    def test_timeout_parameter_propagation(self):
        """Test that timeout parameter is properly propagated to API client."""
        with patch("tickersnap.lists.asset.AssetsListAPI") as mock_assets_list_class:
            mock_client = Mock()
            mock_assets_list_class.return_value.__enter__.return_value = mock_client
            mock_client.get_data.return_value = self._create_mock_assets_response()

            # Test different timeout values
            timeout_values = [5, 15, 30, 60]
            for timeout in timeout_values:
                assets = Assets(timeout=timeout)
                assets.get_all_stocks()

                # Verify AssetsListAPI was called with correct timeout
                mock_assets_list_class.assert_called_with(timeout=timeout)

    @patch("tickersnap.lists.asset.AssetsListAPI")
    def test_asset_data_integrity(self, mock_assets_list_class):
        """Test that returned asset data maintains integrity."""
        mock_client = Mock()
        mock_assets_list_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_assets_response()
        mock_client.get_data.return_value = mock_response

        assets = Assets()

        # Test stocks data integrity
        stocks = assets.get_all_stocks()
        for stock in stocks:
            assert hasattr(stock, "sid")
            assert hasattr(stock, "name")
            assert hasattr(stock, "ticker")
            assert hasattr(stock, "type")
            assert hasattr(stock, "slug")
            assert hasattr(stock, "isin")
            assert stock.sid is not None
            assert stock.name is not None
            assert stock.ticker is not None
            assert stock.type == AssetType.STOCK

        # Test ETFs data integrity
        etfs = assets.get_all_etfs()
        for etf in etfs:
            assert hasattr(etf, "sid")
            assert hasattr(etf, "name")
            assert hasattr(etf, "ticker")
            assert hasattr(etf, "type")
            assert hasattr(etf, "slug")
            assert hasattr(etf, "isin")
            assert etf.type == AssetType.ETF

    def _create_mock_assets_response(self):
        """Create mock API response with mixed assets."""
        return AssetsListResponse(
            success=True,
            data=[
                AssetData(
                    sid="RELIANCE",
                    name="Reliance Industries Ltd",
                    ticker="RELIANCE",
                    type=AssetType.STOCK,
                    slug="reliance-industries-ltd",
                    isin="INE002A01018",
                ),
                AssetData(
                    sid="TCS",
                    name="Tata Consultancy Services Ltd",
                    ticker="TCS",
                    type=AssetType.STOCK,
                    slug="tata-consultancy-services-ltd",
                    isin="INE467B01029",
                ),
                AssetData(
                    sid="NIFTYBEES",
                    name="Nippon India ETF Nifty BeES",
                    ticker="NIFTYBEES",
                    type=AssetType.ETF,
                    slug="nippon-india-etf-nifty-bees",
                    isin="INF204KB17I5",
                ),
            ],
        )

    def _create_mock_mixed_assets_response(self):
        """Create mock API response with more diverse asset mix."""
        return AssetsListResponse(
            success=True,
            data=[
                AssetData(
                    sid="RELIANCE",
                    name="Reliance Industries Ltd",
                    ticker="RELIANCE",
                    type=AssetType.STOCK,
                    slug="reliance-industries-ltd",
                    isin="INE002A01018",
                ),
                AssetData(
                    sid="TCS",
                    name="Tata Consultancy Services Ltd",
                    ticker="TCS",
                    type=AssetType.STOCK,
                    slug="tata-consultancy-services-ltd",
                    isin="INE467B01029",
                ),
                AssetData(
                    sid="HDFC",
                    name="HDFC Bank Ltd",
                    ticker="HDFC",
                    type=AssetType.STOCK,
                    slug="hdfc-bank-ltd",
                    isin="INE040A01034",
                ),
                AssetData(
                    sid="NIFTYBEES",
                    name="Nippon India ETF Nifty BeES",
                    ticker="NIFTYBEES",
                    type=AssetType.ETF,
                    slug="nippon-india-etf-nifty-bees",
                    isin="INF204KB17I5",
                ),
                AssetData(
                    sid="BANKNIFTY",
                    name="Bank Nifty ETF",
                    ticker="BANKNIFTY",
                    type=AssetType.ETF,
                    slug="bank-nifty-etf",
                    isin="INF204KB18I6",
                ),
            ],
        )


@pytest.mark.integration
class TestIntegrationAssets:
    """
    Integration test suite for Assets class with real API calls.

    These tests make actual API calls and validate real data.
    """

    def test_get_all_stocks_integration(self):
        """Test get_all_stocks with real API call."""
        assets = Assets(timeout=15)
        result = assets.get_all_stocks()

        # Basic validation
        assert isinstance(result, list)
        assert len(result) > 0, "Should return at least some stocks"

        # Validate data structure
        for stock in result[:5]:  # Check first 5 for performance
            assert isinstance(stock, AssetData)
            assert stock.type == AssetType.STOCK
            assert stock.sid is not None
            assert stock.name is not None
            assert stock.ticker is not None
            assert stock.slug is not None
            assert stock.isin is not None

    def test_get_all_etfs_integration(self):
        """Test get_all_etfs with real API call."""
        assets = Assets(timeout=15)
        result = assets.get_all_etfs()

        # Basic validation
        assert isinstance(result, list)
        assert len(result) > 0, "Should return at least some ETFs"

        # Validate data structure
        for etf in result[:5]:  # Check first 5 for performance
            assert isinstance(etf, AssetData)
            assert etf.type == AssetType.ETF
            assert etf.sid is not None
            assert etf.name is not None
            assert etf.ticker is not None
            assert etf.slug is not None
            assert etf.isin is not None

    def test_get_all_assets_integration(self):
        """Test get_all_assets with real API call."""
        assets = Assets(timeout=15)
        result = assets.get_all_assets()

        # Basic validation
        assert isinstance(result, list)
        assert len(result) > 0, "Should return at least some assets"

        # Validate asset type distribution
        stock_count = sum(1 for asset in result if asset.type == AssetType.STOCK)
        etf_count = sum(1 for asset in result if asset.type == AssetType.ETF)

        assert stock_count > 0, "Should have some stocks"
        assert etf_count > 0, "Should have some ETFs"
        assert stock_count + etf_count == len(
            result
        ), "All assets should be stocks or ETFs"

    def test_consistency_across_methods(self):
        """Test that data is consistent across different method calls."""
        assets = Assets(timeout=15)

        # Get data from all methods
        all_assets = assets.get_all_assets()
        all_stocks = assets.get_all_stocks()
        all_etfs = assets.get_all_etfs()

        # Validate consistency
        assert len(all_assets) == len(all_stocks) + len(all_etfs)

        # Validate that filtered results are subsets of all_assets
        all_asset_sids = {asset.sid for asset in all_assets}
        stock_sids = {stock.sid for stock in all_stocks}
        etf_sids = {etf.sid for etf in all_etfs}

        assert stock_sids.issubset(all_asset_sids)
        assert etf_sids.issubset(all_asset_sids)
        assert stock_sids.isdisjoint(etf_sids)  # No overlap between stocks and ETFs

    def test_data_quality_validation(self):
        """Test that returned data meets quality expectations."""
        assets = Assets(timeout=15)

        # Sample some assets for quality checks
        all_assets = assets.get_all_assets()
        sample_size = min(20, len(all_assets))
        sample_assets = all_assets[:sample_size]

        for asset in sample_assets:
            # Validate ISIN format (basic check)
            assert len(asset.isin) >= 10, f"ISIN {asset.isin} seems too short"

            # Validate ticker is not empty
            assert asset.ticker.strip() != "", "Ticker should not be empty"

            # Validate name is meaningful
            assert len(asset.name.strip()) > 2, "Asset name should be meaningful"

            # Validate SID is not empty
            assert asset.sid.strip() != "", "SID should not be empty"

    def test_performance_expectations(self):
        """Test that API calls complete within reasonable time."""
        import time

        assets = Assets(timeout=30)  # Allow more time for real API

        # Test each method's performance
        methods_to_test = [
            ("get_all_stocks", assets.get_all_stocks),
            ("get_all_etfs", assets.get_all_etfs),
            ("get_all_assets", assets.get_all_assets),
        ]

        for method_name, method in methods_to_test:
            start_time = time.time()
            result = method()
            end_time = time.time()

            duration = end_time - start_time
            assert duration < 30, f"{method_name} took too long: {duration:.2f}s"
            assert len(result) > 0, f"{method_name} returned no results"
