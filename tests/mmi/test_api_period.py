"""
Unit tests for tickersnap MMI module.

Tests cover:
- MMIPeriod class functionality
- API response validation
- Error handling
- Edge cases
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from tickersnap.mmi.api import MMIPeriod
from tickersnap.mmi.models import HistoricalData, MMIPeriodData, MMIPeriodResponse


class TestUnitMMIPeriod:
    """
    Unit test suite for MMIPeriod class with mocked API calls.
    """

    def test_mmi_period_initialization(self):
        """Test MMIPeriod initialization with default and custom timeout."""
        # with default timeout
        mmi = MMIPeriod()
        assert mmi.timeout == 10
        assert mmi.BASE_URL == "https://analyze.api.tickertape.in/homepage/mmi"
        assert mmi.DEFAULT_PERIOD == 4
        assert mmi.MIN_PERIOD == 1
        assert mmi.MAX_PERIOD == 10
        mmi.close()

        # with custom timeout
        mmi = MMIPeriod(timeout=30)
        assert mmi.timeout == 30
        mmi.close()

    def test_period_validation(self):
        """Test period parameter validation."""
        with MMIPeriod() as mmi:
            # valid periods should not raise
            for period in [1, 5, 10]:
                # mock the response to avoid actual API calls
                with patch.object(mmi.client, "get") as mock_get:
                    mock_response = Mock()
                    mock_response.json.return_value = self._get_mock_api_response()
                    mock_response.raise_for_status.return_value = None
                    mock_get.return_value = mock_response

                    result = mmi.get_data(period=period)
                    assert isinstance(result, MMIPeriodResponse)

            # invalid periods should raise ValueError
            for invalid_period in [0, 11, -1, 999]:
                with pytest.raises(ValueError, match="Period must be between"):
                    mmi.get_data(period=invalid_period)

    def test_default_period(self):
        """Test that default period is used when period is None."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = mmi.get_data()

                # verify the request was made with default period
                mock_get.assert_called_once_with(
                    mmi.BASE_URL, params={"period": mmi.DEFAULT_PERIOD}
                )

    @patch("httpx.Client")
    def test_context_manager(self, mock_client_class):
        """Test context manager functionality."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with MMIPeriod() as mmi:
            assert mmi is not None

        # verify close was called when exiting context
        mock_client.close.assert_called_once()

    def test_manual_close(self):
        """Test manual client closing."""
        mmi = MMIPeriod()
        mmi.close()
        # should not raise any exception

    @patch("httpx.Client")
    def test_http_error_handling(self, mock_client_class):
        """Test HTTP error handling."""
        from httpx import HTTPStatusError, RequestError

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mmi = MMIPeriod()

        # test HTTP status error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        http_error = HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_client.get.side_effect = http_error

        with pytest.raises(Exception, match="HTTP 404 error"):
            mmi.get_data(period=1)

        # test request error
        request_error = RequestError("Connection failed")
        mock_client.get.side_effect = request_error

        with pytest.raises(Exception, match="Request failed"):
            mmi.get_data(period=1)

        mmi.close()

    def test_api_response_structure_validation(self):
        """Test that API response is properly validated against Pydantic models."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                # valid response
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = mmi.get_data(period=1)

                # validate response structure
                assert isinstance(result, MMIPeriodResponse)
                assert result.success is True
                assert isinstance(result.data, MMIPeriodData)

                # validate ALL main data fields exist and have correct types
                data = result.data
                assert hasattr(data, "date") and isinstance(data.date, datetime)
                assert hasattr(data, "fii") and isinstance(data.fii, int)
                assert hasattr(data, "skew") and isinstance(data.skew, float)
                assert hasattr(data, "momentum") and isinstance(data.momentum, float)
                assert hasattr(data, "gold_on_nifty") and isinstance(
                    data.gold_on_nifty, float
                )
                assert hasattr(data, "gold") and isinstance(data.gold, int)
                assert hasattr(data, "nifty") and isinstance(data.nifty, float)
                assert hasattr(data, "extrema") and isinstance(data.extrema, float)
                assert hasattr(data, "fma") and isinstance(data.fma, float)
                assert hasattr(data, "sma") and isinstance(data.sma, float)
                assert hasattr(data, "trin") and isinstance(data.trin, float)
                assert hasattr(data, "indicator") and isinstance(data.indicator, float)
                assert hasattr(data, "raw") and isinstance(data.raw, float)
                assert hasattr(data, "vix") and isinstance(data.vix, float)
                assert hasattr(data, "days_historical") and isinstance(
                    data.days_historical, list
                )
                assert hasattr(data, "months_historical") and isinstance(
                    data.months_historical, list
                )

                # validate historical data structure
                if data.days_historical:
                    hist = data.days_historical[0]
                    assert isinstance(hist, HistoricalData)
                    # validate key historical fields exist
                    assert hasattr(hist, "date") and isinstance(hist.date, datetime)
                    assert hasattr(hist, "indicator") and isinstance(
                        hist.indicator, float
                    )
                    assert hasattr(hist, "fii") and isinstance(hist.fii, int)
                    assert hasattr(hist, "nifty") and isinstance(hist.nifty, float)
                if data.months_historical:
                    hist = data.months_historical[0]
                    assert isinstance(hist, HistoricalData)
                    # validate key historical fields exist
                    assert hasattr(hist, "date") and isinstance(hist.date, datetime)
                    assert hasattr(hist, "indicator") and isinstance(
                        hist.indicator, float
                    )
                    assert hasattr(hist, "fii") and isinstance(hist.fii, int)
                    assert hasattr(hist, "nifty") and isinstance(hist.nifty, float)

    def test_validation_error_handling(self):
        """Test handling of Pydantic validation errors."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                # invalid response structure
                mock_response = Mock()
                mock_response.json.return_value = {
                    "invalid": "response"
                }  # Missing required fields
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                with pytest.raises(Exception, match="Data validation error"):
                    mmi.get_data(period=1)

    def test_multiple_calls_same_client(self):
        """Test multiple API calls with same client instance."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                # make multiple calls
                results = []
                for period in [1, 2, 3]:
                    result = mmi.get_data(period=period)
                    results.append(result)

                # verify all calls succeeded
                assert len(results) == 3
                for result in results:
                    assert isinstance(result, MMIPeriodResponse)

                # verify client.get was called 3 times
                assert mock_get.call_count == 3

    def test_api_response_data_integrity(self):
        """Test that all expected fields are present and have correct types."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                mock_response = Mock()
                api_response = self._get_mock_api_response()
                mock_response.json.return_value = api_response
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = mmi.get_data(period=1)

                # check main response fields
                assert result.success == api_response["success"]

                # check data fields
                data = result.data
                expected_data = api_response["data"]

                assert data.fii == expected_data["fii"]
                assert data.skew == expected_data["skew"]
                assert data.momentum == expected_data["momentum"]
                assert data.gold_on_nifty == expected_data["goldOnNifty"]
                assert data.gold == expected_data["gold"]
                assert data.nifty == expected_data["nifty"]
                assert data.extrema == expected_data["extrema"]
                assert data.fma == expected_data["fma"]
                assert data.sma == expected_data["sma"]
                assert data.trin == expected_data["trin"]
                assert data.indicator == expected_data["indicator"]
                assert data.raw == expected_data["raw"]
                assert data.vix == expected_data["vix"]

                # check historical data
                assert len(data.days_historical) == len(expected_data["daysHistorical"])
                assert len(data.months_historical) == len(
                    expected_data["monthsHistorical"]
                )

    def _get_mock_api_response(self):
        """Helper method to create a mock API response matching the real API structure."""
        return {
            "success": True,
            "data": {
                "date": "2025-06-17T05:39:00.065Z",
                "fii": -101743,
                "skew": -3.41,
                "momentum": 2.1345873303243756,
                "goldOnNifty": 0.0022944493145140576,
                "gold": 97321,
                "nifty": 24874.55,
                "extrema": 0.054,
                "fma": 24797.233612788717,
                "sma": 24278.97763231699,
                "trin": -1.483348946247038,
                "indicator": 52.0216622730683,
                "raw": 42.98885533925628,
                "vix": -14.45,
                "daysHistorical": [
                    {
                        "date": "2025-06-16T00:00:00.000Z",
                        "fii": -92730,
                        "skew": -2.63,
                        "momentum": 2.181383301132762,
                        "goldOnNifty": -0.005578003115649599,
                        "gold": 97321,
                        "nifty": 24946.5,
                        "extrema": 0.066,
                        "fma": 24789.870147340025,
                        "sma": 24260.652328695975,
                        "trin": 0.7988172527676249,
                        "indicator": 53.76878319113767,
                        "raw": 61.05446920688031,
                        "vix": -14.84,
                    }
                ],
                "monthsHistorical": [
                    {
                        "date": "2025-05-30T00:00:00.000Z",
                        "fii": -78987,
                        "skew": -2.43,
                        "momentum": 2.4152913877334035,
                        "goldOnNifty": -0.02814232189800947,
                        "gold": 95175,
                        "nifty": 24750.7,
                        "extrema": 0.06,
                        "fma": 24592.635143682084,
                        "sma": 24012.659448067167,
                        "trin": 0.7810614494802155,
                        "indicator": 60.62300339992293,
                        "raw": 61.33870741262289,
                        "vix": -16.08,
                    }
                ],
            },
        }


@pytest.mark.integration
class TestIntegrationMMIPeriod:
    """
    Integration test suite for MMIPeriod class with real API calls.
    """

    def test_tickertape_api_call_validation(self):
        """Test real API call to validate response structure and catch API changes."""
        with MMIPeriod(timeout=30) as mmi:
            try:
                # make real API call with period=1 (fastest)
                result = mmi.get_data(period=1)

                # validate response structure - this will catch API changes
                assert isinstance(
                    result, MMIPeriodResponse
                ), "Response should be MMIPeriodResponse"
                assert result.success is True, "API call should be successful"
                assert isinstance(
                    result.data, MMIPeriodData
                ), "Data should be MMIPeriodData"

                # validate ALL fields in main data object
                data = result.data

                # validate datetime field
                assert hasattr(data, "date"), "Missing 'date' field"
                assert isinstance(
                    data.date, datetime
                ), f"Date should be datetime, got {type(data.date)}"

                # validate integer fields
                assert hasattr(data, "fii"), "Missing 'fii' field"
                assert isinstance(
                    data.fii, int
                ), f"FII should be int, got {type(data.fii)}"

                assert hasattr(data, "gold"), "Missing 'gold' field"
                assert isinstance(
                    data.gold, int
                ), f"Gold should be int, got {type(data.gold)}"
                assert data.gold > 0, f"Gold should be positive, got {data.gold}"

                # validate float fields with reasonable constraints
                assert hasattr(data, "skew"), "Missing 'skew' field"
                assert isinstance(
                    data.skew, float
                ), f"Skew should be float, got {type(data.skew)}"

                assert hasattr(data, "momentum"), "Missing 'momentum' field"
                assert isinstance(
                    data.momentum, float
                ), f"Momentum should be float, got {type(data.momentum)}"

                assert hasattr(data, "gold_on_nifty"), "Missing 'gold_on_nifty' field"
                assert isinstance(
                    data.gold_on_nifty, float
                ), f"Gold on Nifty should be float, got {type(data.gold_on_nifty)}"

                assert hasattr(data, "nifty"), "Missing 'nifty' field"
                assert isinstance(
                    data.nifty, float
                ), f"Nifty should be float, got {type(data.nifty)}"
                assert data.nifty > 0, f"Nifty should be positive, got {data.nifty}"
                assert (
                    20000 <= data.nifty <= 30000
                ), f"Nifty seems out of reasonable range: {data.nifty}"

                assert hasattr(data, "extrema"), "Missing 'extrema' field"
                assert isinstance(
                    data.extrema, float
                ), f"Extrema should be float, got {type(data.extrema)}"

                assert hasattr(data, "fma"), "Missing 'fma' field"
                assert isinstance(
                    data.fma, float
                ), f"FMA should be float, got {type(data.fma)}"
                assert data.fma > 0, f"FMA should be positive, got {data.fma}"

                assert hasattr(data, "sma"), "Missing 'sma' field"
                assert isinstance(
                    data.sma, float
                ), f"SMA should be float, got {type(data.sma)}"
                assert data.sma > 0, f"SMA should be positive, got {data.sma}"

                assert hasattr(data, "trin"), "Missing 'trin' field"
                assert isinstance(
                    data.trin, float
                ), f"TRIN should be float, got {type(data.trin)}"

                assert hasattr(data, "indicator"), "Missing 'indicator' field"
                assert isinstance(
                    data.indicator, float
                ), f"Indicator should be float, got {type(data.indicator)}"
                assert (
                    0 <= data.indicator <= 100
                ), f"MMI indicator should be between 0-100, got {data.indicator}"

                assert hasattr(data, "raw"), "Missing 'raw' field"
                assert isinstance(
                    data.raw, float
                ), f"Raw should be float, got {type(data.raw)}"

                assert hasattr(data, "vix"), "Missing 'vix' field"
                assert isinstance(
                    data.vix, float
                ), f"VIX should be float, got {type(data.vix)}"

                # validate historical data arrays
                assert hasattr(
                    data, "days_historical"
                ), "Missing 'days_historical' field"
                assert isinstance(
                    data.days_historical, list
                ), f"Days historical should be list, got {type(data.days_historical)}"

                assert hasattr(
                    data, "months_historical"
                ), "Missing 'months_historical' field"
                assert isinstance(
                    data.months_historical, list
                ), f"Months historical should be list, got {type(data.months_historical)}"

                # validate historical data structure if present
                if data.days_historical:
                    self._validate_historical_data(
                        data.days_historical[0], "days_historical[0]"
                    )
                if data.months_historical:
                    self._validate_historical_data(
                        data.months_historical[0], "months_historical[0]"
                    )

                # validate data freshness (within last 10 days to account for weekends)
                now = datetime.now()
                data_date = data.date.replace(tzinfo=None)
                time_diff = now - data_date
                assert (
                    time_diff.days <= 10
                ), f"Data seems too old: {data_date} (age: {time_diff.days} days)"

                print(
                    f"✅ Integration test passed! MMI: {data.indicator:.2f}, Nifty: {data.nifty:.2f}, Gold: {data.gold}"
                )
                print(
                    f"   Historical data points - Days: {len(data.days_historical)}, Months: {len(data.months_historical)}"
                )

            except Exception as e:
                pytest.fail(f"Integration test failed - API may have changed: {e}")

    def _validate_historical_data(self, hist_data, field_name):
        """Helper method to validate all fields in historical data objects."""
        assert isinstance(
            hist_data, HistoricalData
        ), f"{field_name} should be HistoricalData, got {type(hist_data)}"

        # validate all fields exist and have correct types
        assert hasattr(hist_data, "date"), f"{field_name} missing 'date' field"
        assert isinstance(
            hist_data.date, datetime
        ), f"{field_name}.date should be datetime, got {type(hist_data.date)}"

        assert hasattr(hist_data, "fii"), f"{field_name} missing 'fii' field"
        assert isinstance(
            hist_data.fii, int
        ), f"{field_name}.fii should be int, got {type(hist_data.fii)}"

        assert hasattr(hist_data, "skew"), f"{field_name} missing 'skew' field"
        assert isinstance(
            hist_data.skew, float
        ), f"{field_name}.skew should be float, got {type(hist_data.skew)}"

        assert hasattr(hist_data, "momentum"), f"{field_name} missing 'momentum' field"
        assert isinstance(
            hist_data.momentum, float
        ), f"{field_name}.momentum should be float, got {type(hist_data.momentum)}"

        assert hasattr(
            hist_data, "gold_on_nifty"
        ), f"{field_name} missing 'gold_on_nifty' field"
        assert isinstance(
            hist_data.gold_on_nifty, float
        ), f"{field_name}.gold_on_nifty should be float, got {type(hist_data.gold_on_nifty)}"

        assert hasattr(hist_data, "gold"), f"{field_name} missing 'gold' field"
        assert isinstance(
            hist_data.gold, int
        ), f"{field_name}.gold should be int, got {type(hist_data.gold)}"
        assert (
            hist_data.gold > 0
        ), f"{field_name}.gold should be positive, got {hist_data.gold}"

        assert hasattr(hist_data, "nifty"), f"{field_name} missing 'nifty' field"
        assert isinstance(
            hist_data.nifty, float
        ), f"{field_name}.nifty should be float, got {type(hist_data.nifty)}"
        assert (
            hist_data.nifty > 0
        ), f"{field_name}.nifty should be positive, got {hist_data.nifty}"

        assert hasattr(hist_data, "extrema"), f"{field_name} missing 'extrema' field"
        assert isinstance(
            hist_data.extrema, float
        ), f"{field_name}.extrema should be float, got {type(hist_data.extrema)}"

        assert hasattr(hist_data, "fma"), f"{field_name} missing 'fma' field"
        assert isinstance(
            hist_data.fma, float
        ), f"{field_name}.fma should be float, got {type(hist_data.fma)}"
        assert (
            hist_data.fma > 0
        ), f"{field_name}.fma should be positive, got {hist_data.fma}"

        assert hasattr(hist_data, "sma"), f"{field_name} missing 'sma' field"
        assert isinstance(
            hist_data.sma, float
        ), f"{field_name}.sma should be float, got {type(hist_data.sma)}"
        assert (
            hist_data.sma > 0
        ), f"{field_name}.sma should be positive, got {hist_data.sma}"

        assert hasattr(hist_data, "trin"), f"{field_name} missing 'trin' field"
        assert isinstance(
            hist_data.trin, float
        ), f"{field_name}.trin should be float, got {type(hist_data.trin)}"

        assert hasattr(
            hist_data, "indicator"
        ), f"{field_name} missing 'indicator' field"
        assert isinstance(
            hist_data.indicator, float
        ), f"{field_name}.indicator should be float, got {type(hist_data.indicator)}"
        assert (
            0 <= hist_data.indicator <= 100
        ), f"{field_name}.indicator should be between 0-100, got {hist_data.indicator}"

        assert hasattr(hist_data, "raw"), f"{field_name} missing 'raw' field"
        assert isinstance(
            hist_data.raw, float
        ), f"{field_name}.raw should be float, got {type(hist_data.raw)}"

        assert hasattr(hist_data, "vix"), f"{field_name} missing 'vix' field"
        assert isinstance(
            hist_data.vix, float
        ), f"{field_name}.vix should be float, got {type(hist_data.vix)}"
