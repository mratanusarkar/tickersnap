"""
Unit tests for tickersnap MMI Now module.

Tests cover:
- MMINowAPI class functionality
- API response validation
- Error handling
- Edge cases
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from tickersnap.mmi import MMINowAPI
from tickersnap.mmi.models import DailyData, HistoricalData, MMINowData, MMINowResponse


class TestUnitMMINow:
    """
    Unit test suite for MMINowAPI class with mocked API calls.
    """

    def test_mmi_now_initialization(self):
        """Test MMINowAPI initialization with default and custom timeout."""
        # with default timeout
        mmi = MMINowAPI()
        assert mmi.timeout == 10
        assert mmi.BASE_URL == "https://api.tickertape.in/mmi/now"
        mmi.close()

        # with custom timeout
        mmi = MMINowAPI(timeout=30)
        assert mmi.timeout == 30
        mmi.close()

    @patch("httpx.Client")
    def test_context_manager(self, mock_client_class):
        """Test context manager functionality."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with MMINowAPI() as mmi:
            assert mmi is not None

        # verify close was called when exiting context
        mock_client.close.assert_called_once()

    def test_manual_close(self):
        """Test manual client closing."""
        mmi = MMINowAPI()
        mmi.close()
        # should not raise any exception

    @patch("httpx.Client")
    def test_http_error_handling(self, mock_client_class):
        """Test HTTP error handling."""
        from httpx import HTTPStatusError, RequestError

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mmi = MMINowAPI()

        # test HTTP status error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        http_error = HTTPStatusError("404", request=Mock(), response=mock_response)
        mock_client.get.side_effect = http_error

        with pytest.raises(Exception, match="HTTP 404 error"):
            mmi.get_data()

        # test request error
        request_error = RequestError("Connection failed")
        mock_client.get.side_effect = request_error

        with pytest.raises(Exception, match="Request failed"):
            mmi.get_data()

        mmi.close()

    def test_api_response_structure_validation(self):
        """Test that API response is properly validated against Pydantic models."""
        with MMINowAPI() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                # valid response
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = mmi.get_data()

                # validate response structure
                assert isinstance(result, MMINowResponse)
                assert result.success is True
                assert isinstance(result.data, MMINowData)

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
                assert hasattr(data, "current_value") and isinstance(
                    data.current_value, float
                )
                assert hasattr(data, "daily") and isinstance(data.daily, list)

                # validate historical comparison fields
                assert hasattr(data, "last_day") and isinstance(
                    data.last_day, HistoricalData
                )
                assert hasattr(data, "last_week") and isinstance(
                    data.last_week, HistoricalData
                )
                assert hasattr(data, "last_month") and isinstance(
                    data.last_month, HistoricalData
                )
                assert hasattr(data, "last_year") and isinstance(
                    data.last_year, HistoricalData
                )

                # validate daily data structure
                if data.daily:
                    daily_item = data.daily[0]
                    assert isinstance(daily_item, DailyData)
                    assert hasattr(daily_item, "value") and isinstance(
                        daily_item.value, float
                    )
                    assert hasattr(daily_item, "date") and isinstance(
                        daily_item.date, datetime
                    )

    def test_validation_error_handling(self):
        """Test handling of Pydantic validation errors."""
        with MMINowAPI() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                # invalid response structure
                mock_response = Mock()
                mock_response.json.return_value = {
                    "invalid": "response"
                }  # Missing required fields
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                with pytest.raises(Exception, match="Data validation error"):
                    mmi.get_data()

    def test_multiple_calls_same_client(self):
        """Test multiple API calls with same client instance."""
        with MMINowAPI() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                # make multiple calls
                results = []
                for i in range(3):
                    result = mmi.get_data()
                    results.append(result)

                # verify all calls succeeded
                assert len(results) == 3
                for result in results:
                    assert isinstance(result, MMINowResponse)

                # verify client.get was called 3 times
                assert mock_get.call_count == 3

    def test_api_response_data_integrity(self):
        """Test that all expected fields are present and have correct types."""
        with MMINowAPI() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                mock_response = Mock()
                api_response = self._get_mock_api_response()
                mock_response.json.return_value = api_response
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = mmi.get_data()

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
                assert data.current_value == expected_data["currentValue"]

                # check historical comparison data
                assert data.last_day.indicator == expected_data["lastDay"]["indicator"]
                assert (
                    data.last_week.indicator == expected_data["lastWeek"]["indicator"]
                )
                assert (
                    data.last_month.indicator == expected_data["lastMonth"]["indicator"]
                )
                assert (
                    data.last_year.indicator == expected_data["lastYear"]["indicator"]
                )

                # check daily data
                assert len(data.daily) == len(expected_data["daily"])

    def test_no_parameters_api_call(self):
        """Test that get_data() is called without parameters."""
        with MMINowAPI() as mmi:
            with patch.object(mmi.client, "get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                result = mmi.get_data()

                # verify the request was made without parameters
                mock_get.assert_called_once_with(mmi.BASE_URL)

    def _get_mock_api_response(self):
        """Helper method to create a mock API response matching the real MMI Now API structure."""
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
                "lastDay": {
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
                },
                "lastWeek": {
                    "date": "2025-06-10T00:00:00.000Z",
                    "fii": -92730,
                    "skew": -2.63,
                    "momentum": 2.279836889383372,
                    "goldOnNifty": 0.0007692808302486309,
                    "gold": 97321,
                    "nifty": 25104.25,
                    "extrema": 0.096,
                    "fma": 24723.031084793784,
                    "sma": 24171.950050655614,
                    "trin": 0.33766255838171044,
                    "indicator": 64.82784845122984,
                    "raw": 62.79162999238044,
                    "vix": -14.02,
                },
                "lastMonth": {
                    "date": "2025-05-16T00:00:00.000Z",
                    "fii": -13521,
                    "skew": -1.76,
                    "momentum": 2.2953262029328867,
                    "goldOnNifty": 0.08331572988546121,
                    "gold": 89480,
                    "nifty": 25019.8,
                    "extrema": 0.062,
                    "fma": 24276.317681851888,
                    "sma": 23731.60004758445,
                    "trin": 0.6872066972852703,
                    "indicator": 76.46505342410525,
                    "raw": 82.01857514950483,
                    "vix": -16.55,
                },
                "lastYear": {
                    "fii": -318367,
                    "skew": -3.47,
                    "nifty": 23264.85,
                    "gold": 71819,
                    "goldOnNifty": 0.05956924175842382,
                    "date": "2024-06-11T00:00:00.000Z",
                    "extrema": 0.142,
                    "trin": 0.3168759447664276,
                    "fma": 22800.481297879927,
                    "sma": 22511.404741856433,
                    "momentum": 1.2841337950181377,
                    "vix": -14.77,
                    "raw": 58.32355068705067,
                    "indicator": 53.792827342085886,
                },
                "currentValue": 52.0216622730683,
                "daily": [
                    {"value": 52.0216622730683, "date": "2025-06-17T05:39:00.065Z"}
                ],
            },
            "error": None,
        }


@pytest.mark.integration
class TestIntegrationMMINow:
    """
    Integration test suite for MMINowAPI class with real API calls.
    """

    def test_tickertape_now_api_call_validation(self):
        """Test real API call to validate response structure and catch API changes."""
        with MMINowAPI(timeout=30) as mmi:
            try:
                # make real API call
                result = mmi.get_data()

                # validate response structure - this will catch API changes
                assert isinstance(
                    result, MMINowResponse
                ), "Response should be MMINowResponse"
                assert result.success is True, "API call should be successful"
                assert isinstance(result.data, MMINowData), "Data should be MMINowData"

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

                # validate MMINowAPI specific fields
                assert hasattr(data, "current_value"), "Missing 'current_value' field"
                assert isinstance(
                    data.current_value, float
                ), f"Current value should be float, got {type(data.current_value)}"
                assert (
                    0 <= data.current_value <= 100
                ), f"Current value should be between 0-100, got {data.current_value}"

                # validate historical comparison fields
                assert hasattr(data, "last_day"), "Missing 'last_day' field"
                assert isinstance(
                    data.last_day, HistoricalData
                ), f"Last day should be HistoricalData, got {type(data.last_day)}"

                assert hasattr(data, "last_week"), "Missing 'last_week' field"
                assert isinstance(
                    data.last_week, HistoricalData
                ), f"Last week should be HistoricalData, got {type(data.last_week)}"

                assert hasattr(data, "last_month"), "Missing 'last_month' field"
                assert isinstance(
                    data.last_month, HistoricalData
                ), f"Last month should be HistoricalData, got {type(data.last_month)}"

                assert hasattr(data, "last_year"), "Missing 'last_year' field"
                assert isinstance(
                    data.last_year, HistoricalData
                ), f"Last year should be HistoricalData, got {type(data.last_year)}"

                # validate daily data array
                assert hasattr(data, "daily"), "Missing 'daily' field"
                assert isinstance(
                    data.daily, list
                ), f"Daily should be list, got {type(data.daily)}"
                assert len(data.daily) > 0, "Daily array should not be empty"

                # validate daily data structure
                daily_item = data.daily[0]
                assert isinstance(
                    daily_item, DailyData
                ), f"Daily item should be DailyData, got {type(daily_item)}"
                assert hasattr(daily_item, "value"), "Daily item missing 'value' field"
                assert isinstance(
                    daily_item.value, float
                ), f"Daily value should be float, got {type(daily_item.value)}"
                assert hasattr(daily_item, "date"), "Daily item missing 'date' field"
                assert isinstance(
                    daily_item.date, datetime
                ), f"Daily date should be datetime, got {type(daily_item.date)}"

                # validate historical data structure
                self._validate_historical_data(data.last_day, "last_day")
                self._validate_historical_data(data.last_week, "last_week")
                self._validate_historical_data(data.last_month, "last_month")
                self._validate_historical_data(data.last_year, "last_year")

                # validate data freshness (within last 10 days to account for weekends)
                now = datetime.now()
                data_date = data.date.replace(tzinfo=None)
                time_diff = now - data_date
                assert (
                    time_diff.days <= 10
                ), f"Data seems too old: {data_date} (age: {time_diff.days} days)"

                # validate current value matches indicator (they should be the same)
                assert (
                    abs(data.current_value - data.indicator) < 0.01
                ), f"Current value ({data.current_value}) should match indicator ({data.indicator})"

                print(
                    f"✅ Integration test passed! Current MMI: {data.current_value:.2f}, Nifty: {data.nifty:.2f}, Gold: {data.gold}"
                )
                print(
                    f"   Historical MMI - Day: {data.last_day.indicator:.2f}, Week: {data.last_week.indicator:.2f}, Month: {data.last_month.indicator:.2f}, Year: {data.last_year.indicator:.2f}"
                )
                print(f"   Daily data points: {len(data.daily)}")

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
