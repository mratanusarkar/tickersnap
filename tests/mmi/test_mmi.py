"""
Unit tests for tickersnap MarketMoodIndex module.

Tests cover:
- MarketMoodIndex class functionality
- User-facing model validation
- Zone calculation accuracy
- Property calculations
- Error handling
- Edge cases
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from tickersnap.mmi import MarketMoodIndex
from tickersnap.mmi.models import (
    MMIChanges,
    MMICurrent,
    MMIDataPoint,
    MMINowData,
    MMINowResponse,
    MMIPeriodData,
    MMIPeriodResponse,
    MMITrends,
    MMIZone,
)


class TestUnitMarketMoodIndex:
    """
    Unit test suite for MarketMoodIndex class with mocked API calls.
    """

    def test_mmi_initialization(self):
        """Test MarketMoodIndex initialization with default and custom timeout."""
        # with default timeout
        mmi = MarketMoodIndex()
        assert mmi.timeout == 10

        # with custom timeout
        mmi = MarketMoodIndex(timeout=30)
        assert mmi.timeout == 30

    @patch("tickersnap.mmi.mmi.MMINow")
    def test_get_current_mmi_basic(self, mock_mmi_now_class):
        """Test get_current_mmi basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_mmi_now_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_now_response()
        mock_client.get_data.return_value = mock_response

        # Test
        mmi = MarketMoodIndex(timeout=15)
        result = mmi.get_current_mmi()

        # Validate
        assert isinstance(result, MMICurrent)
        assert result.value == 65.5
        assert result.zone == MMIZone.GREED  # 65.5 should be GREED (50-70)
        assert isinstance(result.date, datetime)

        # Verify API usage
        mock_mmi_now_class.assert_called_once_with(timeout=15)
        mock_client.get_data.assert_called_once()

    @patch("tickersnap.mmi.mmi.MMINow")
    def test_get_current_mmi_zone_calculations(self, mock_mmi_now_class):
        """Test zone calculation for different MMI values."""
        mock_client = Mock()
        mock_mmi_now_class.return_value.__enter__.return_value = mock_client

        mmi = MarketMoodIndex()

        # Test different MMI values and expected zones
        test_cases = [
            (15.0, MMIZone.EXTREME_FEAR),  # < 30
            (45.0, MMIZone.FEAR),  # 30-50
            (65.0, MMIZone.GREED),  # 50-70
            (85.0, MMIZone.EXTREME_GREED),  # >= 70
            (30.0, MMIZone.FEAR),  # boundary
            (50.0, MMIZone.GREED),  # boundary
            (70.0, MMIZone.EXTREME_GREED),  # boundary
        ]

        for mmi_value, expected_zone in test_cases:
            mock_response = self._create_mock_now_response(indicator=mmi_value)
            mock_client.get_data.return_value = mock_response

            result = mmi.get_current_mmi()
            assert (
                result.zone == expected_zone
            ), f"MMI {mmi_value} should be {expected_zone}, got {result.zone}"
            assert result.value == mmi_value

    @patch("tickersnap.mmi.mmi.MMIPeriod")
    def test_get_mmi_trends_basic(self, mock_mmi_period_class):
        """Test get_mmi_trends basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_mmi_period_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_period_response()
        mock_client.get_data.return_value = mock_response

        # Test
        mmi = MarketMoodIndex(timeout=20)
        result = mmi.get_mmi_trends()

        # Validate structure
        assert isinstance(result, MMITrends)
        assert isinstance(result.current, MMIDataPoint)
        assert isinstance(result.last_10_days, list)
        assert isinstance(result.last_10_months, list)

        # Validate data
        assert result.current.value == 58.3
        assert len(result.last_10_days) == 2  # From mock
        assert len(result.last_10_months) == 1  # From mock

        # Validate list contents
        for day_point in result.last_10_days:
            assert isinstance(day_point, MMIDataPoint)
            assert isinstance(day_point.date, datetime)
            assert isinstance(day_point.value, float)

        for month_point in result.last_10_months:
            assert isinstance(month_point, MMIDataPoint)
            assert isinstance(month_point.date, datetime)
            assert isinstance(month_point.value, float)

        # Verify API usage
        mock_mmi_period_class.assert_called_once_with(timeout=20)
        mock_client.get_data.assert_called_once_with(period=10)

    @patch("tickersnap.mmi.mmi.MMINow")
    def test_get_mmi_changes_basic(self, mock_mmi_now_class):
        """Test get_mmi_changes basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_mmi_now_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_now_response()
        mock_client.get_data.return_value = mock_response

        # Test
        mmi = MarketMoodIndex()
        result = mmi.get_mmi_changes()

        # Validate structure
        assert isinstance(result, MMIChanges)
        assert isinstance(result.current, MMIDataPoint)
        assert isinstance(result.last_day, MMIDataPoint)
        assert isinstance(result.last_week, MMIDataPoint)
        assert isinstance(result.last_month, MMIDataPoint)
        assert isinstance(result.last_year, MMIDataPoint)

        # Validate data values
        assert result.current.value == 65.5
        assert result.last_day.value == 60.0
        assert result.last_week.value == 70.0
        assert result.last_month.value == 55.0
        assert result.last_year.value == 50.0

        # Validate property calculations
        assert result.vs_last_day == 5.5  # 65.5 - 60.0
        assert result.vs_last_week == -4.5  # 65.5 - 70.0
        assert result.vs_last_month == 10.5  # 65.5 - 55.0
        assert result.vs_last_year == 15.5  # 65.5 - 50.0

        # Test vs_last method
        assert result.vs_last("day") == 5.5
        assert result.vs_last("week") == -4.5
        assert result.vs_last("month") == 10.5
        assert result.vs_last("year") == 15.5

        # Verify API usage
        mock_client.get_data.assert_called_once()

    def test_get_mmi_changes_vs_last_invalid_period(self):
        """Test vs_last method with invalid period."""
        # Create a minimal MMIChanges object for testing
        current = MMIDataPoint(date=datetime.now(), value=65.0)
        last_day = MMIDataPoint(date=datetime.now(), value=60.0)

        changes = MMIChanges(
            current=current,
            last_day=last_day,
            last_week=last_day,
            last_month=last_day,
            last_year=last_day,
        )

        with pytest.raises(ValueError, match="Invalid period"):
            changes.vs_last("invalid")

    @patch("tickersnap.mmi.mmi.MMINow")
    def test_get_raw_current_data(self, mock_mmi_now_class):
        """Test get_raw_current_data basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_mmi_now_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_now_response()
        mock_client.get_data.return_value = mock_response

        # Test
        mmi = MarketMoodIndex()
        result = mmi.get_raw_current_data()

        # Validate
        assert isinstance(result, MMINowData)
        assert result.indicator == 65.5
        assert result.current_value == 65.5
        assert hasattr(result, "last_day")
        assert hasattr(result, "last_week")

        # Verify API usage
        mock_client.get_data.assert_called_once()

    @patch("tickersnap.mmi.mmi.MMIPeriod")
    def test_get_raw_period_data(self, mock_mmi_period_class):
        """Test get_raw_period_data basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_mmi_period_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_period_response()
        mock_client.get_data.return_value = mock_response

        # Test with default period
        mmi = MarketMoodIndex()
        result = mmi.get_raw_period_data()

        # Validate
        assert isinstance(result, MMIPeriodData)
        assert result.indicator == 58.3
        assert hasattr(result, "days_historical")
        assert hasattr(result, "months_historical")

        # Verify API usage
        mock_client.get_data.assert_called_once_with(period=4)

        # Test with custom period
        result = mmi.get_raw_period_data(period=7)
        mock_client.get_data.assert_called_with(period=7)

    @patch("tickersnap.mmi.mmi.MMINow")
    def test_error_handling_api_failure(self, mock_mmi_now_class):
        """Test error handling when API calls fail."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_mmi_now_class.return_value.__enter__.return_value = mock_client
        mock_client.get_data.side_effect = Exception("API Error")

        # Test
        mmi = MarketMoodIndex()
        with pytest.raises(Exception, match="API Error"):
            mmi.get_current_mmi()

    @patch("tickersnap.mmi.mmi.MMIPeriod")
    def test_multiple_calls_different_methods(self, mock_mmi_period_class):
        """Test multiple calls to different methods."""
        # Setup mock
        mock_client = Mock()
        mock_mmi_period_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_period_response()
        mock_client.get_data.return_value = mock_response

        # Test multiple calls
        mmi = MarketMoodIndex()

        # Call get_mmi_trends multiple times
        result1 = mmi.get_mmi_trends()
        result2 = mmi.get_mmi_trends()

        assert isinstance(result1, MMITrends)
        assert isinstance(result2, MMITrends)
        assert result1.current.value == result2.current.value

        # Verify each call created new context manager
        assert mock_mmi_period_class.call_count == 2

    def test_timeout_parameter_propagation(self):
        """Test that timeout parameter is properly propagated to API clients."""
        mmi = MarketMoodIndex(timeout=45)

        with patch("tickersnap.mmi.mmi.MMINow") as mock_now:
            with patch("tickersnap.mmi.mmi.MMIPeriod") as mock_period:
                # Setup mocks
                mock_now.return_value.__enter__.return_value.get_data.return_value = (
                    self._create_mock_now_response()
                )
                mock_period.return_value.__enter__.return_value.get_data.return_value = (
                    self._create_mock_period_response()
                )

                # Test different methods
                mmi.get_current_mmi()
                mock_now.assert_called_with(timeout=45)

                mmi.get_mmi_trends()
                mock_period.assert_called_with(timeout=45)

                mmi.get_mmi_changes()
                # Called twice now (once above, once here)
                assert mock_now.call_count == 2
                mock_now.assert_called_with(timeout=45)

    # Helper methods
    def _create_mock_now_response(self, indicator=65.5):
        """Create a mock MMINowResponse for testing."""
        mock_data = Mock(spec=MMINowData)
        mock_data.date = datetime(2024, 1, 15, 10, 0, 0)
        mock_data.indicator = indicator
        mock_data.current_value = indicator
        mock_data.fii = -50000
        mock_data.nifty = 21500.0
        mock_data.vix = -12.5

        # Mock historical data
        mock_data.last_day = Mock()
        mock_data.last_day.date = datetime(2024, 1, 14, 10, 0, 0)
        mock_data.last_day.indicator = 60.0

        mock_data.last_week = Mock()
        mock_data.last_week.date = datetime(2024, 1, 8, 10, 0, 0)
        mock_data.last_week.indicator = 70.0

        mock_data.last_month = Mock()
        mock_data.last_month.date = datetime(2023, 12, 15, 10, 0, 0)
        mock_data.last_month.indicator = 55.0

        mock_data.last_year = Mock()
        mock_data.last_year.date = datetime(2023, 1, 15, 10, 0, 0)
        mock_data.last_year.indicator = 50.0

        # Mock response
        mock_response = Mock(spec=MMINowResponse)
        mock_response.success = True
        mock_response.data = mock_data

        return mock_response

    def _create_mock_period_response(self):
        """Create a mock MMIPeriodResponse for testing."""
        mock_data = Mock(spec=MMIPeriodData)
        mock_data.date = datetime(2024, 1, 15, 10, 0, 0)
        mock_data.indicator = 58.3
        mock_data.fii = -45000
        mock_data.nifty = 21800.0

        # Mock historical data arrays
        mock_day1 = Mock()
        mock_day1.date = datetime(2024, 1, 14, 10, 0, 0)
        mock_day1.indicator = 62.1

        mock_day2 = Mock()
        mock_day2.date = datetime(2024, 1, 13, 10, 0, 0)
        mock_day2.indicator = 59.8

        mock_data.days_historical = [mock_day1, mock_day2]

        mock_month1 = Mock()
        mock_month1.date = datetime(2023, 12, 15, 10, 0, 0)
        mock_month1.indicator = 67.4

        mock_data.months_historical = [mock_month1]

        # Mock response
        mock_response = Mock(spec=MMIPeriodResponse)
        mock_response.success = True
        mock_response.data = mock_data

        return mock_response


@pytest.mark.integration
class TestIntegrationMarketMoodIndex:
    """
    Integration test suite for MarketMoodIndex class with real API calls.
    """

    def test_get_current_mmi_integration(self):
        """Test get_current_mmi with real API call."""
        try:
            mmi = MarketMoodIndex(timeout=30)
            result = mmi.get_current_mmi()

            # Validate structure
            assert isinstance(result, MMICurrent)
            assert isinstance(result.date, datetime)
            assert isinstance(result.value, float)
            assert isinstance(result.zone, MMIZone)

            # Validate data ranges
            assert 0 <= result.value <= 100
            assert result.zone in [
                MMIZone.EXTREME_FEAR,
                MMIZone.FEAR,
                MMIZone.GREED,
                MMIZone.EXTREME_GREED,
            ]

            # Validate zone consistency
            if result.value < 30:
                assert result.zone == MMIZone.EXTREME_FEAR
            elif result.value < 50:
                assert result.zone == MMIZone.FEAR
            elif result.value < 70:
                assert result.zone == MMIZone.GREED
            else:
                assert result.zone == MMIZone.EXTREME_GREED

            print(f"✅ Current MMI: {result.value:.2f} ({result.zone})")

        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")

    def test_get_mmi_trends_integration(self):
        """Test get_mmi_trends with real API call."""
        try:
            mmi = MarketMoodIndex(timeout=30)
            result = mmi.get_mmi_trends()

            # Validate structure
            assert isinstance(result, MMITrends)
            assert isinstance(result.current, MMIDataPoint)
            assert isinstance(result.last_10_days, list)
            assert isinstance(result.last_10_months, list)

            # Validate current data
            assert 0 <= result.current.value <= 100
            assert isinstance(result.current.date, datetime)

            # Validate historical data
            for day_point in result.last_10_days:
                assert isinstance(day_point, MMIDataPoint)
                assert 0 <= day_point.value <= 100
                assert isinstance(day_point.date, datetime)

            for month_point in result.last_10_months:
                assert isinstance(month_point, MMIDataPoint)
                assert 0 <= month_point.value <= 100
                assert isinstance(month_point.date, datetime)

            # Validate data count (should be up to 10 each)
            assert len(result.last_10_days) <= 10
            assert len(result.last_10_months) <= 10

            print(
                f"✅ Trends - Current: {result.current.value:.2f}, Days: {len(result.last_10_days)}, Months: {len(result.last_10_months)}"
            )

        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")

    def test_get_mmi_changes_integration(self):
        """Test get_mmi_changes with real API call."""
        try:
            mmi = MarketMoodIndex(timeout=30)
            result = mmi.get_mmi_changes()

            # Validate structure
            assert isinstance(result, MMIChanges)
            assert isinstance(result.current, MMIDataPoint)
            assert isinstance(result.last_day, MMIDataPoint)
            assert isinstance(result.last_week, MMIDataPoint)
            assert isinstance(result.last_month, MMIDataPoint)
            assert isinstance(result.last_year, MMIDataPoint)

            # Validate all values are in valid range
            for point in [
                result.current,
                result.last_day,
                result.last_week,
                result.last_month,
                result.last_year,
            ]:
                assert 0 <= point.value <= 100
                assert isinstance(point.date, datetime)

            # Validate property calculations
            assert (
                abs(result.vs_last_day - (result.current.value - result.last_day.value))
                < 0.01
            )
            assert (
                abs(
                    result.vs_last_week
                    - (result.current.value - result.last_week.value)
                )
                < 0.01
            )
            assert (
                abs(
                    result.vs_last_month
                    - (result.current.value - result.last_month.value)
                )
                < 0.01
            )
            assert (
                abs(
                    result.vs_last_year
                    - (result.current.value - result.last_year.value)
                )
                < 0.01
            )

            # Test vs_last method
            assert result.vs_last("day") == result.vs_last_day
            assert result.vs_last("week") == result.vs_last_week
            assert result.vs_last("month") == result.vs_last_month
            assert result.vs_last("year") == result.vs_last_year

            print(f"✅ Changes - Current: {result.current.value:.2f}")
            print(
                f"   vs Day: {result.vs_last_day:+.1f}, vs Week: {result.vs_last_week:+.1f}"
            )
            print(
                f"   vs Month: {result.vs_last_month:+.1f}, vs Year: {result.vs_last_year:+.1f}"
            )

        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")

    def test_all_methods_consistency(self):
        """Test that all methods return consistent current MMI values."""
        try:
            mmi = MarketMoodIndex(timeout=30)

            # Get data from all methods
            current = mmi.get_current_mmi()
            trends = mmi.get_mmi_trends()
            changes = mmi.get_mmi_changes()

            # The current values should be very close (within small tolerance for timing differences)
            tolerance = 0.1  # Allow small differences due to timing

            assert abs(current.value - trends.current.value) <= tolerance
            assert abs(current.value - changes.current.value) <= tolerance
            assert abs(trends.current.value - changes.current.value) <= tolerance

            # Dates should be close (within 1 hour)
            time_tolerance = 3600  # 1 hour in seconds

            def time_diff(dt1, dt2):
                return abs((dt1 - dt2).total_seconds())

            assert time_diff(current.date, trends.current.date) <= time_tolerance
            assert time_diff(current.date, changes.current.date) <= time_tolerance

            print(
                "✅ Consistency check passed - all methods return similar current values"
            )
            print(
                f"   Current: {current.value:.2f}, Trends: {trends.current.value:.2f}, Changes: {changes.current.value:.2f}"
            )

        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")
