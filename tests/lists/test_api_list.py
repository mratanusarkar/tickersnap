"""
Unit tests for tickersnap Assets List module.

Tests cover:
- AssetsListAPI class functionality
- API response validation
- Filter validation and normalization
- Error handling
- Edge cases
- Class constants access
"""

from unittest.mock import Mock, patch

import pytest

from tickersnap.lists import AssetsListAPI
from tickersnap.lists.models import AssetData, AssetsListResponse, AssetType


class TestUnitAssetsList:
    """
    Unit test suite for AssetsListAPI class with mocked API calls.
    """

    def test_assets_list_initialization(self):
        """Test AssetsListAPI initialization with default and custom timeout."""
        # with default timeout
        assets = AssetsListAPI()
        assert assets.timeout == 10
        assert assets.BASE_URL == "https://api.tickertape.in/stocks/list"
        assets.close()

        # with custom timeout
        assets = AssetsListAPI(timeout=30)
        assert assets.timeout == 30
        assets.close()

    def test_class_constants(self):
        """Test that all class constants are properly defined."""
        # validate constants exist and have correct values
        assert hasattr(AssetsListAPI, "VALID_LETTERS")
        assert hasattr(AssetsListAPI, "VALID_OTHERS")
        assert hasattr(AssetsListAPI, "VALID_FILTERS")
        assert hasattr(AssetsListAPI, "VALID_FILTERS_SORTED_LIST")

        # validate VALID_LETTERS contains all lowercase letters
        expected_letters = set("abcdefghijklmnopqrstuvwxyz")
        assert AssetsListAPI.VALID_LETTERS == expected_letters

        # validate VALID_OTHERS contains 'others'
        assert AssetsListAPI.VALID_OTHERS == {"others"}

        # validate VALID_FILTERS is union of letters and others
        assert (
            AssetsListAPI.VALID_FILTERS
            == AssetsListAPI.VALID_LETTERS | AssetsListAPI.VALID_OTHERS
        )

        # validate VALID_FILTERS_SORTED_LIST is properly ordered
        expected_sorted = list("abcdefghijklmnopqrstuvwxyz") + ["others"]
        assert AssetsListAPI.VALID_FILTERS_SORTED_LIST == expected_sorted

        # validate total count
        assert len(AssetsListAPI.VALID_FILTERS) == 27  # 26 letters + others

    def test_filter_validation_valid_cases(self):
        """Test filter validation with valid inputs."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                # test valid letters (lowercase)
                for letter in "abcdefghijklmnopqrstuvwxyz":
                    result = assets.get_data(filter=letter)
                    assert isinstance(result, AssetsListResponse)
                    mock_get.assert_called_with(
                        assets.BASE_URL, params={"filter": letter}
                    )

                # test 'others'
                result = assets.get_data(filter="others")
                assert isinstance(result, AssetsListResponse)
                mock_get.assert_called_with(
                    assets.BASE_URL, params={"filter": "others"}
                )

    def test_filter_validation_case_insensitive(self):
        """Test that filter validation is case insensitive for letters and 'others'."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                # test uppercase letters are converted to lowercase
                for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    result = assets.get_data(filter=letter)
                    assert isinstance(result, AssetsListResponse)
                    # verify the actual API call used lowercase
                    mock_get.assert_called_with(
                        assets.BASE_URL, params={"filter": letter.lower()}
                    )

                # test 'others' variations are case insensitive
                others_variations = ["others", "OTHERS", "Others", "OtHeRs"]
                for others_filter in others_variations:
                    result = assets.get_data(filter=others_filter)
                    assert isinstance(result, AssetsListResponse)
                    # verify the actual API call used lowercase 'others'
                    mock_get.assert_called_with(
                        assets.BASE_URL, params={"filter": "others"}
                    )

    def test_filter_validation_invalid_cases(self):
        """Test filter validation with invalid inputs (non-empty and non-whitespace cases only)."""
        with AssetsListAPI() as assets:
            # test specific invalid filters that remain invalid even after .lower(), (non-empty and non-whitespace cases only)
            invalid_filters = [
                "invalid",  # word that's not a single letter or 'others'
                "1",  # single numeric string
                "123",  # multiple numeric string
                "ab",  # multiple lowercase letters
                "XYZ",  # multiple uppercase letters
                "@",  # special character
                "!@#",  # multiple special character
            ]

            for invalid_filter in invalid_filters:
                with pytest.raises(ValueError) as exc_info:
                    assets.get_data(filter=invalid_filter)

                error_msg = str(exc_info.value)
                assert f"Invalid filter '{invalid_filter}'" in error_msg
                assert "Valid options are:" in error_msg
                assert "All filters are case insensitive" in error_msg

    def test_filter_validation_empty_and_whitespace_cases(self):
        """Test filter validation with empty strings and whitespace."""
        with AssetsListAPI() as assets:
            # test empty filters (caught by empty filter validation)
            empty_filters = [
                "",  # empty string
                " ",  # single space
                "  ",  # multiple spaces
                "\t",  # tab
                "\n",  # newline
                "   \t  ",  # mixed whitespace
            ]

            for empty_filter in empty_filters:
                with pytest.raises(ValueError) as exc_info:
                    assets.get_data(filter=empty_filter)

                error_msg = str(exc_info.value)
                assert f"Empty filter '{empty_filter}' not allowed" in error_msg
                assert (
                    "Use filter=None or omit the parameter to get all assets"
                    in error_msg
                )
                assert "Valid filters:" in error_msg

    def test_filter_validation_whitespace_padding_cases(self):
        """Test filter validation with leading/trailing whitespace."""
        with AssetsListAPI() as assets:
            # test filters with leading/trailing whitespace
            whitespace_filters = [
                " a",  # leading space
                "a ",  # trailing space
                " a ",  # both leading and trailing
                "  b",  # multiple leading spaces
                "c  ",  # multiple trailing spaces
                "\ta",  # leading tab
                "z\n",  # trailing newline
                " others ",  # whitespace around 'others'
            ]

            for ws_filter in whitespace_filters:
                with pytest.raises(ValueError) as exc_info:
                    assets.get_data(filter=ws_filter)

                error_msg = str(exc_info.value)
                assert (
                    f"Filter '{ws_filter}' contains leading or trailing whitespaces"
                    in error_msg
                )
                assert "Please remove the whitespaces and try again" in error_msg
                assert "Valid filters:" in error_msg

    def test_no_filter_parameter(self):
        """Test API call without filter parameter."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = assets.get_data()  # No filter
                assert isinstance(result, AssetsListResponse)
                # verify API call without filter parameter
                mock_get.assert_called_with(assets.BASE_URL, params={})

    def test_none_filter_parameter(self):
        """Test API call with explicit None filter."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = assets.get_data(filter=None)
                assert isinstance(result, AssetsListResponse)
                # verify API call without filter parameter
                mock_get.assert_called_with(assets.BASE_URL, params={})

    @patch("httpx.Client")
    def test_context_manager(self, mock_client_class):
        """Test context manager functionality."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with AssetsListAPI() as assets:
            assert assets is not None

        # verify close was called when exiting context
        mock_client.close.assert_called_once()

    def test_manual_close(self):
        """Test manual client closing."""
        assets = AssetsListAPI()
        assets.close()
        # should not raise any exception

    @patch("httpx.Client")
    def test_http_error_handling(self, mock_client_class):
        """Test HTTP error handling."""
        from httpx import HTTPStatusError, RequestError

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        assets = AssetsListAPI()

        # test HTTP status error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        http_error = HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_client.get.side_effect = http_error

        with pytest.raises(Exception, match="HTTP 404 error"):
            assets.get_data()

        # test request error
        request_error = RequestError("Connection failed")
        mock_client.get.side_effect = request_error

        with pytest.raises(Exception, match="Request failed"):
            assets.get_data()

        assets.close()

    def test_api_response_structure_validation(self):
        """Test that API response is properly validated against Pydantic models."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                # valid response
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = assets.get_data()

                # validate response structure
                assert isinstance(result, AssetsListResponse)
                assert result.success is True
                assert isinstance(result.data, list)
                assert len(result.data) > 0

                # validate asset data structure
                asset = result.data[0]
                assert isinstance(asset, AssetData)

                # validate ALL main data fields exist and have correct types
                assert hasattr(asset, "sid") and isinstance(asset.sid, str)
                assert hasattr(asset, "name") and isinstance(asset.name, str)
                assert hasattr(asset, "ticker") and isinstance(asset.ticker, str)
                assert hasattr(asset, "type") and isinstance(asset.type, AssetType)
                assert hasattr(asset, "slug") and isinstance(asset.slug, str)
                assert hasattr(asset, "isin") and isinstance(asset.isin, str)

                # validate asset type enum
                assert asset.type in [AssetType.STOCK, AssetType.ETF]

    def test_validation_error_handling(self):
        """Test handling of Pydantic validation errors."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                # invalid response structure
                mock_response = Mock()
                mock_response.json.return_value = {
                    "invalid": "response"
                }  # Missing required fields
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                with pytest.raises(Exception, match="Data validation error"):
                    assets.get_data()

    def test_multiple_calls_same_client(self):
        """Test making multiple API calls with the same client instance."""
        assets = AssetsListAPI()

        with patch.object(assets.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = self._get_mock_api_response()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # make multiple calls
            result1 = assets.get_data(filter="a")
            result2 = assets.get_data(filter="b")
            result3 = assets.get_data()

            # verify all calls succeeded
            assert isinstance(result1, AssetsListResponse)
            assert isinstance(result2, AssetsListResponse)
            assert isinstance(result3, AssetsListResponse)

            # verify correct number of calls
            assert mock_get.call_count == 3

        assets.close()

    def test_api_response_data_integrity(self):
        """Test that asset data maintains integrity through model validation."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response_with_etf()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = assets.get_data()

                # validate response structure
                assert result.success is True
                assert len(result.data) == 2  # stock + etf

                # validate stock data
                stock = result.data[0]
                assert stock.sid == "TEST"
                assert stock.name == "Test Company Ltd"
                assert stock.ticker == "TESTCO"
                assert stock.type == AssetType.STOCK
                assert stock.slug == "/stocks/test-company-TEST"
                assert stock.isin == "INE123456789"

                # validate ETF data
                etf = result.data[1]
                assert etf.sid == "TETF"
                assert etf.name == "Test ETF"
                assert etf.ticker == "TESTETF"
                assert etf.type == AssetType.ETF
                assert etf.slug == "/etfs/test-etf-TETF"
                assert etf.isin == "INF987654321"

    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""
        with AssetsListAPI() as assets:
            with patch.object(assets.client, "get") as mock_get:
                # simulate unexpected error
                mock_get.side_effect = RuntimeError("Unexpected error occurred")

                with pytest.raises(Exception, match="Unexpected error"):
                    assets.get_data()

    def _get_mock_api_response(self):
        """Generate mock API response for testing."""
        return {
            "success": True,
            "data": [
                {
                    "sid": "TEST",
                    "name": "Test Company Ltd",
                    "ticker": "TESTCO",
                    "type": "stock",
                    "slug": "/stocks/test-company-TEST",
                    "isin": "INE123456789",
                }
            ],
        }

    def _get_mock_api_response_with_etf(self):
        """Generate mock API response with both stock and ETF for testing."""
        return {
            "success": True,
            "data": [
                {
                    "sid": "TEST",
                    "name": "Test Company Ltd",
                    "ticker": "TESTCO",
                    "type": "stock",
                    "slug": "/stocks/test-company-TEST",
                    "isin": "INE123456789",
                },
                {
                    "sid": "TETF",
                    "name": "Test ETF",
                    "ticker": "TESTETF",
                    "type": "etf",
                    "slug": "/etfs/test-etf-TETF",
                    "isin": "INF987654321",
                },
            ],
        }


@pytest.mark.integration
class TestIntegrationAssetsList:
    """
    Integration test suite for AssetsListAPI class with real API calls.
    These tests make actual HTTP requests to the Tickertape API.
    """

    def test_real_api_call_no_filter(self):
        """Test real API call without filter to get all assets."""
        with AssetsListAPI() as assets:
            result = assets.get_data()

            # validate response structure
            assert isinstance(result, AssetsListResponse)
            assert result.success is True
            assert isinstance(result.data, list)
            assert len(result.data) > 1000  # should have thousands of assets

            # validate asset data structure
            asset = result.data[0]
            assert isinstance(asset, AssetData)
            assert len(asset.sid) > 0
            assert len(asset.name) > 0
            assert len(asset.ticker) > 0
            assert asset.type in [AssetType.STOCK, AssetType.ETF]
            assert asset.slug.startswith("/")
            assert len(asset.isin) > 0

    def test_real_api_call_with_letter_filter(self):
        """Test real API call with letter filter."""
        with AssetsListAPI() as assets:
            # test with 'a' filter
            result = assets.get_data(filter="a")

            # validate response structure
            assert isinstance(result, AssetsListResponse)
            assert result.success is True
            assert isinstance(result.data, list)
            assert len(result.data) > 0

            # validate all assets start with 'a' (case insensitive)
            for asset in result.data:
                assert asset.name.lower().startswith("a")

    def test_real_api_call_with_others_filter(self):
        """Test real API call with 'others' filter."""
        with AssetsListAPI() as assets:
            result = assets.get_data(filter="others")

            # validate response structure
            assert isinstance(result, AssetsListResponse)
            assert result.success is True
            assert isinstance(result.data, list)
            assert len(result.data) > 0

            # validate assets in 'others' don't start with letters
            for asset in result.data:
                first_char = asset.name[0].lower()
                assert first_char not in "abcdefghijklmnopqrstuvwxyz"

    def test_real_api_call_case_insensitive(self):
        """Test real API call with uppercase filter for letters and 'others'."""
        with AssetsListAPI() as assets:
            # test case insensitive letters
            # get results with lowercase 'a'
            result_lower = assets.get_data(filter="a")
            # get results with uppercase 'A'
            result_upper = assets.get_data(filter="A")

            # should return identical results
            assert len(result_lower.data) == len(result_upper.data)
            assert result_lower.success == result_upper.success

            # validate asset counts match
            lower_sids = {asset.sid for asset in result_lower.data}
            upper_sids = {asset.sid for asset in result_upper.data}
            assert lower_sids == upper_sids

            # test case insensitive 'others'
            # get results with lowercase 'others'
            result_others_lower = assets.get_data(filter="others")
            # get results with uppercase 'OTHERS'
            result_others_upper = assets.get_data(filter="OTHERS")

            # should return identical results
            assert len(result_others_lower.data) == len(result_others_upper.data)
            assert result_others_lower.success == result_others_upper.success

            # validate asset counts match
            others_lower_sids = {asset.sid for asset in result_others_lower.data}
            others_upper_sids = {asset.sid for asset in result_others_upper.data}
            assert others_lower_sids == others_upper_sids

    def test_real_api_completeness_validation(self):
        """Test that sum of all filters equals total assets."""
        with AssetsListAPI() as assets:
            # get total count
            all_assets = assets.get_data()
            total_count = len(all_assets.data)

            # get count for each filter
            filter_counts = {}
            for filter_name in AssetsListAPI.VALID_FILTERS_SORTED_LIST:
                filtered_assets = assets.get_data(filter=filter_name)
                filter_counts[filter_name] = len(filtered_assets.data)

            # sum should equal total
            sum_of_filters = sum(filter_counts.values())
            assert sum_of_filters == total_count, (
                f"Sum of filters ({sum_of_filters}) != total ({total_count}). "
                f"Filter breakdown: {filter_counts}"
            )

    def test_real_api_data_consistency(self):
        """Test that API data is consistent across calls."""
        with AssetsListAPI() as assets:
            # make two identical calls
            result1 = assets.get_data(filter="x")
            result2 = assets.get_data(filter="x")

            # should return identical results
            assert len(result1.data) == len(result2.data)
            assert result1.success == result2.success

            # validate asset data is identical
            sids1 = {asset.sid for asset in result1.data}
            sids2 = {asset.sid for asset in result2.data}
            assert sids1 == sids2

    def test_real_api_asset_types_distribution(self):
        """Test that API returns both stocks and ETFs."""
        with AssetsListAPI() as assets:
            result = assets.get_data()

            # check for both asset types
            asset_types = {asset.type for asset in result.data}
            assert AssetType.STOCK in asset_types
            assert AssetType.ETF in asset_types

            # count distribution
            stock_count = sum(
                1 for asset in result.data if asset.type == AssetType.STOCK
            )
            etf_count = sum(1 for asset in result.data if asset.type == AssetType.ETF)

            assert stock_count > 0
            assert etf_count > 0
            assert stock_count + etf_count == len(result.data)

    def test_real_api_performance(self):
        """Test API response performance."""
        import time

        with AssetsListAPI(
            timeout=30
        ) as assets:  # increased timeout for performance test
            start_time = time.time()
            result = assets.get_data()
            end_time = time.time()

            # validate response
            assert isinstance(result, AssetsListResponse)
            assert result.success is True

            # check performance (should complete within reasonable time)
            response_time = end_time - start_time
            assert response_time < 10.0, f"API call took too long: {response_time:.2f}s"
