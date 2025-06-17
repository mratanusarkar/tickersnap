"""
Unit tests for tickersnap MMI module.

Tests cover:
- MMIPeriod class functionality
- API response validation
- Error handling
- Edge cases
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from tickersnap.mmi.mmi import MMIPeriod
from tickersnap.mmi.models import MMIPeriodResponse, MMIPeriodData, HistoricalData


class UnitTestMMIPeriod:
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
                with patch.object(mmi.client, 'get') as mock_get:
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
            with patch.object(mmi.client, 'get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = self._get_mock_api_response()
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                result = mmi.get_data()
                
                # verify the request was made with default period
                mock_get.assert_called_once_with(
                    mmi.BASE_URL,
                    params={"period": mmi.DEFAULT_PERIOD}
                )

    @patch('httpx.Client')
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

    @patch('httpx.Client')
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
            with patch.object(mmi.client, 'get') as mock_get:
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
                assert isinstance(result.data.indicator, float)
                assert isinstance(result.data.fii, int)
                assert isinstance(result.data.days_historical, list)
                assert isinstance(result.data.months_historical, list)
                
                # validate historical data structure
                if result.data.days_historical:
                    assert isinstance(result.data.days_historical[0], HistoricalData)
                if result.data.months_historical:
                    assert isinstance(result.data.months_historical[0], HistoricalData)

    def test_validation_error_handling(self):
        """Test handling of Pydantic validation errors."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, 'get') as mock_get:
                # invalid response structure
                mock_response = Mock()
                mock_response.json.return_value = {"invalid": "response"}  # Missing required fields
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response
                
                with pytest.raises(Exception, match="Data validation error"):
                    mmi.get_data(period=1)

    def test_multiple_calls_same_client(self):
        """Test multiple API calls with same client instance."""
        with MMIPeriod() as mmi:
            with patch.object(mmi.client, 'get') as mock_get:
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
            with patch.object(mmi.client, 'get') as mock_get:
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
                assert len(data.months_historical) == len(expected_data["monthsHistorical"])

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
                        "vix": -14.84
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
                        "vix": -16.08
                    }
                ]
            }
        }

