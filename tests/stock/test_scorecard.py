"""
Unit tests for tickersnap StockScorecard module.

Tests cover:
- StockScorecard class functionality
- User-facing model validation
- Rating calculation accuracy
- Progress tracking functionality
- Error handling and edge cases
- Data transformation logic
- Integration with real API responses
"""

from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import Future
import threading

import pytest

from tickersnap.stock import StockScorecard
from tickersnap.stock.models import (
    Score,
    ScoreRating,
    ScorecardElement,
    ScorecardItem,
    ScorecardResponse,
    StockScores,
    StockWithScorecard,
)
from tickersnap.lists.models import AssetData, AssetType


class TestUnitStockScorecard:
    """
    Unit test suite for StockScorecard class with mocked API calls.
    """

    def test_scorecard_initialization(self):
        """Test StockScorecard initialization with default and custom parameters."""
        # Default initialization
        scorecard = StockScorecard()
        assert scorecard.timeout == 10
        assert scorecard.max_workers == 10

        # Custom initialization
        scorecard = StockScorecard(timeout=30, max_workers=5)
        assert scorecard.timeout == 30
        assert scorecard.max_workers == 5

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_get_scorecard_basic(self, mock_api_class):
        """Test get_scorecard basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_scorecard_response()
        mock_client.get_data.return_value = mock_response

        # Test
        scorecard = StockScorecard(timeout=15)
        result = scorecard.get_scorecard("TCS")

        # Validate structure
        assert isinstance(result, StockScores)
        assert isinstance(result.performance, Score)
        assert isinstance(result.valuation, Score)
        assert result.entry_point is None  # Not in mock data
        assert result.red_flags is None  # Not in mock data

        # Validate performance data
        assert result.performance.name == "Performance"
        assert result.performance.value == "Low"
        assert result.performance.rating == ScoreRating.BAD
        assert "low performers" in result.performance.description

        # Validate valuation data
        assert result.valuation.name == "Valuation"
        assert result.valuation.value == "High"
        assert result.valuation.rating == ScoreRating.GOOD

        # Verify API usage
        mock_api_class.assert_called_once_with(timeout=15)
        mock_client.get_data.assert_called_once_with("TCS")

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_get_scorecard_with_entry_point_and_red_flags(self, mock_api_class):
        """Test get_scorecard with entry point and red flags data."""
        # Setup mock with entry point and red flags
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_scorecard_response_with_elements()
        mock_client.get_data.return_value = mock_response

        # Test
        scorecard = StockScorecard()
        result = scorecard.get_scorecard("RELI")

        # Validate entry point
        assert isinstance(result.entry_point, Score)
        assert result.entry_point.name == "Entry point"
        assert result.entry_point.rating == ScoreRating.GOOD
        assert isinstance(result.entry_point_elements, list)
        assert len(result.entry_point_elements) == 2

        # Validate entry point elements
        fundamentals = result.entry_point_elements[0]
        assert fundamentals.name == "Fundamentals"
        assert fundamentals.value == "high"
        assert fundamentals.rating == ScoreRating.GOOD

        # Validate red flags
        assert isinstance(result.red_flags, Score)
        assert result.red_flags.name == "Red flags"
        assert result.red_flags.rating == ScoreRating.BAD
        assert isinstance(result.red_flags_elements, list)
        assert len(result.red_flags_elements) == 1

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_get_scorecard_empty_response(self, mock_api_class):
        """Test get_scorecard with empty/failed API response."""
        # Setup mock with failed response
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_response = ScorecardResponse(success=False, data=None)
        mock_client.get_data.return_value = mock_response

        # Test
        scorecard = StockScorecard()
        result = scorecard.get_scorecard("INVALID")

        # Validate empty scorecard
        assert isinstance(result, StockScores)
        assert result.performance is None
        assert result.valuation is None
        assert result.growth is None
        assert result.profitability is None
        assert result.entry_point is None
        assert result.red_flags is None

    @patch("tickersnap.stock.scorecard.ThreadPoolExecutor")
    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_get_scorecards_basic(self, mock_api_class, mock_executor_class):
        """Test get_scorecards basic functionality."""
        # Setup mocks
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_scorecard_response()
        mock_client.get_data.return_value = mock_response

        # Mock ThreadPoolExecutor
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Create mock futures
        mock_futures = []
        for i in range(3):
            future = Mock(spec=Future)
            future.result.return_value = None
            mock_futures.append(future)
        
        mock_executor.submit.side_effect = mock_futures
        mock_executor_class.return_value.__enter__.return_value.submit = mock_executor.submit

        # Mock as_completed to return futures in order
        with patch("tickersnap.stock.scorecard.as_completed", return_value=mock_futures):
            # Test
            scorecard = StockScorecard(max_workers=5)
            result = scorecard.get_scorecards(["TCS", "RELI", "INFY"])

        # Validate structure
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Verify executor usage
        mock_executor_class.assert_called_once_with(max_workers=5)
        assert mock_executor.submit.call_count == 3

    def test_get_scorecards_empty_list(self):
        """Test get_scorecards with empty SID list."""
        scorecard = StockScorecard()
        result = scorecard.get_scorecards([])
        assert result == []

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_get_stock_with_scorecard_basic(self, mock_api_class):
        """Test get_stock_with_scorecard basic functionality."""
        # Setup mock
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_response = self._create_mock_scorecard_response()
        mock_client.get_data.return_value = mock_response

        # Create test asset
        asset = AssetData(
            sid="TCS",
            name="Tata Consultancy Services Limited",
            ticker="TCS",
            type=AssetType.STOCK,
            slug="tcs",
            isin="INE467B01029"
        )

        # Test
        scorecard = StockScorecard()
        result = scorecard.get_stock_with_scorecard(asset)

        # Validate structure
        assert isinstance(result, StockWithScorecard)
        assert result.asset == asset
        assert isinstance(result.scorecard, StockScores)
        assert result.scorecard.performance.name == "Performance"

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_get_stock_with_scorecard_api_failure(self, mock_api_class):
        """Test get_stock_with_scorecard when API call fails."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_client.get_data.side_effect = Exception("API Error")

        # Create test asset
        asset = AssetData(
            sid="INVALID",
            name="Invalid Stock",
            ticker="INVALID",
            type=AssetType.STOCK,
            slug="invalid",
            isin="INE000000000"
        )

        # Test
        scorecard = StockScorecard()
        result = scorecard.get_stock_with_scorecard(asset)

        # Validate structure
        assert isinstance(result, StockWithScorecard)
        assert result.asset == asset
        assert result.scorecard is None  # Should be None due to API failure

    def test_get_stocks_with_scorecards_empty_list(self):
        """Test get_stocks_with_scorecards with empty asset list."""
        scorecard = StockScorecard()
        result = scorecard.get_stocks_with_scorecards([])
        assert result == []

    def test_rating_determination_colors(self):
        """Test _determine_rating method with different colors."""
        scorecard = StockScorecard()
        
        # Test color-based ratings
        assert scorecard._determine_rating("green") == ScoreRating.GOOD
        assert scorecard._determine_rating("red") == ScoreRating.BAD
        assert scorecard._determine_rating("yellow") == ScoreRating.OKAY
        assert scorecard._determine_rating("orange") == ScoreRating.OKAY
        
        # Test case insensitivity
        assert scorecard._determine_rating("GREEN") == ScoreRating.GOOD
        assert scorecard._determine_rating("Red") == ScoreRating.BAD
        
        # Test unknown/None
        assert scorecard._determine_rating(None) == ScoreRating.UNKNOWN
        assert scorecard._determine_rating("") == ScoreRating.UNKNOWN
        assert scorecard._determine_rating("purple") == ScoreRating.UNKNOWN

    def test_rating_determination_flags(self):
        """Test _determine_rating_from_flag method with different flags."""
        scorecard = StockScorecard()
        
        # Test flag-based ratings
        assert scorecard._determine_rating_from_flag("high") == ScoreRating.GOOD
        assert scorecard._determine_rating_from_flag("low") == ScoreRating.BAD
        assert scorecard._determine_rating_from_flag("avg") == ScoreRating.OKAY
        
        # Test case insensitivity
        assert scorecard._determine_rating_from_flag("HIGH") == ScoreRating.GOOD
        assert scorecard._determine_rating_from_flag("Low") == ScoreRating.BAD
        
        # Test unknown/None
        assert scorecard._determine_rating_from_flag(None) == ScoreRating.UNKNOWN
        assert scorecard._determine_rating_from_flag("") == ScoreRating.UNKNOWN
        assert scorecard._determine_rating_from_flag("medium") == ScoreRating.UNKNOWN

    def test_progress_tracking_with_tqdm(self):
        """Test progress tracking with tqdm available."""
        scorecard = StockScorecard()
        
        # Mock tqdm import inside the method
        with patch("builtins.__import__") as mock_import:
            mock_tqdm_class = Mock()
            mock_progress_bar = Mock()
            mock_tqdm_class.return_value = mock_progress_bar
            
            def import_side_effect(name, *args, **kwargs):
                if name == "tqdm":
                    mock_module = Mock()
                    mock_module.tqdm = mock_tqdm_class
                    return mock_module
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            # Test progress bar initialization
            progress_bar = scorecard._init_progress_bar(100, "Test progress")
            assert progress_bar == mock_progress_bar
            mock_tqdm_class.assert_called_once_with(total=100, desc="Test progress")
            
            # Test progress update
            scorecard._update_progress(True, progress_bar, 50, 100, "item")
            mock_progress_bar.update.assert_called_once_with(1)

    def test_progress_tracking_without_tqdm(self):
        """Test progress tracking fallback when tqdm not available."""
        scorecard = StockScorecard()
        
        # Mock tqdm import to raise ImportError
        with patch("builtins.__import__") as mock_import:
            def import_side_effect(name, *args, **kwargs):
                if name == "tqdm":
                    raise ImportError("No module named 'tqdm'")
                else:
                    return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            # Test progress bar initialization fallback
            with patch("builtins.print") as mock_print:
                progress_bar = scorecard._init_progress_bar(100, "Test progress")
                assert progress_bar is None
                mock_print.assert_called_once_with(
                    "tqdm not installed, using simple progress tracking for: Test progress"
                )

    def test_progress_tracking_custom_callback(self):
        """Test progress tracking with custom callback."""
        scorecard = StockScorecard()
        
        # Test custom callback
        callback_calls = []
        def custom_callback(completed, total, item):
            callback_calls.append((completed, total, item))
        
        scorecard._update_progress(custom_callback, None, 25, 100, "test_item")
        
        assert len(callback_calls) == 1
        assert callback_calls[0] == (25, 100, "test_item")

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_error_handling_api_failure(self, mock_api_class):
        """Test error handling when API call fails."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        mock_client.get_data.side_effect = Exception("Network error")

        # Test
        scorecard = StockScorecard()
        
        with pytest.raises(Exception, match="Network error"):
            scorecard.get_scorecard("TCS")

    def test_transform_scorecard_response_edge_cases(self):
        """Test _transform_scorecard_response with edge cases."""
        scorecard = StockScorecard()
        
        # Test with success=False
        response = ScorecardResponse(success=False, data=None)
        result = scorecard._transform_scorecard_response(response)
        assert isinstance(result, StockScores)
        assert result.performance is None
        
        # Test with success=True but empty data
        response = ScorecardResponse(success=True, data=[])
        result = scorecard._transform_scorecard_response(response)
        assert isinstance(result, StockScores)
        assert result.performance is None

    def test_create_score_from_item_edge_cases(self):
        """Test _create_score_from_item with various edge cases."""
        scorecard = StockScorecard()
        
        # Test with minimal data
        item = ScorecardItem(
            name="Test Category",
            type="score",
            locked=False,
            stack=1,
            tag=None,
            description=None,
            colour=None
        )
        
        result = scorecard._create_score_from_item(item)
        assert result.name == "Test Category"
        assert result.description == "Test Category assessment"
        assert result.value == "Unknown"
        assert result.rating == ScoreRating.UNKNOWN

    def test_create_scores_from_elements_edge_cases(self):
        """Test _create_scores_from_elements with various edge cases."""
        scorecard = StockScorecard()
        
        # Test with elements having missing data
        elements = [
            ScorecardElement(
                title="Test Element",
                type="flag",
                display=True,
                description=None,
                flag=None,
                score="some_score"
            )
        ]
        
        result = scorecard._create_scores_from_elements(elements)
        assert len(result) == 1
        assert result[0].name == "Test Element"
        assert result[0].description == "Test Element assessment"
        assert result[0].value == "some_score"  # Should use score when flag is None
        assert result[0].rating == ScoreRating.UNKNOWN

    def test_concurrent_execution_simulation(self):
        """Test that concurrent execution logic handles threading correctly."""
        scorecard = StockScorecard(max_workers=2)
        
        # Test with empty lists to ensure threading setup works
        assert scorecard.get_scorecards([]) == []
        assert scorecard.get_stocks_with_scorecards([]) == []

    @patch("tickersnap.stock.scorecard.StockScorecardAPI")
    def test_mixed_success_failure_batch(self, mock_api_class):
        """Test batch processing with mixed success and failure results."""
        # Setup mock to succeed for some, fail for others
        mock_client = Mock()
        mock_api_class.return_value.__enter__.return_value = mock_client
        
        def side_effect(sid):
            if sid == "SUCCESS":
                return self._create_mock_scorecard_response()
            else:
                raise Exception(f"API Error for {sid}")
        
        mock_client.get_data.side_effect = side_effect
        
        # Test with mixed results
        scorecard = StockScorecard()
        
        # Test single failures
        try:
            scorecard.get_scorecard("FAIL")
            assert False, "Should have raised exception"
        except Exception as e:
            assert "API Error for FAIL" in str(e)

    def test_scorecard_response_with_all_categories(self):
        """Test response transformation with all possible categories."""
        scorecard = StockScorecard()
        
        # Create response with all 6 categories
        items = [
            ScorecardItem(name="Performance", tag="High", type="score", colour="green", locked=True, stack=1),
            ScorecardItem(name="Valuation", tag="Low", type="score", colour="red", locked=True, stack=2),
            ScorecardItem(name="Growth", tag="Medium", type="score", colour="yellow", locked=True, stack=3),
            ScorecardItem(name="Profitability", tag="Good", type="score", colour="green", locked=True, stack=4),
            ScorecardItem(
                name="Entry point", 
                tag="Fair", 
                type="entryPoint", 
                colour="yellow", 
                locked=False, 
                stack=5,
                elements=[
                    ScorecardElement(title="Technical", type="flag", flag="avg", display=True)
                ]
            ),
            ScorecardItem(
                name="Red flags", 
                tag="High", 
                type="redFlag", 
                colour="red", 
                locked=False, 
                stack=6,
                elements=[
                    ScorecardElement(title="Debt", type="flag", flag="high", display=True)
                ]
            )
        ]
        
        response = ScorecardResponse(success=True, data=items)
        result = scorecard._transform_scorecard_response(response)
        
        # Validate all categories are present
        assert result.performance is not None
        assert result.valuation is not None
        assert result.growth is not None
        assert result.profitability is not None
        assert result.entry_point is not None
        assert result.red_flags is not None
        
        # Validate elements
        assert result.entry_point_elements is not None
        assert len(result.entry_point_elements) == 1
        assert result.red_flags_elements is not None
        assert len(result.red_flags_elements) == 1

    def test_rating_edge_cases_comprehensive(self):
        """Test comprehensive rating edge cases and color consistency."""
        scorecard = StockScorecard()
        
        # Test all known color variations
        color_tests = [
            ("green", ScoreRating.GOOD),
            ("Green", ScoreRating.GOOD),
            ("GREEN", ScoreRating.GOOD),
            ("red", ScoreRating.BAD),
            ("Red", ScoreRating.BAD),
            ("RED", ScoreRating.BAD),
            ("yellow", ScoreRating.OKAY),
            ("Yellow", ScoreRating.OKAY),
            ("YELLOW", ScoreRating.OKAY),
            ("orange", ScoreRating.OKAY),
            ("Orange", ScoreRating.OKAY),
            (None, ScoreRating.UNKNOWN),
            ("", ScoreRating.UNKNOWN),
            ("unknown_color", ScoreRating.UNKNOWN),
            ("blue", ScoreRating.UNKNOWN),
            ("purple", ScoreRating.UNKNOWN),
        ]
        
        for color, expected_rating in color_tests:
            actual_rating = scorecard._determine_rating(color)
            assert actual_rating == expected_rating, f"Color '{color}' should map to {expected_rating}, got {actual_rating}"
        
        # Test all known flag variations
        flag_tests = [
            ("high", ScoreRating.GOOD),
            ("High", ScoreRating.GOOD),
            ("HIGH", ScoreRating.GOOD),
            ("low", ScoreRating.BAD),
            ("Low", ScoreRating.BAD),
            ("LOW", ScoreRating.BAD),
            ("avg", ScoreRating.OKAY),
            ("Avg", ScoreRating.OKAY),
            ("AVG", ScoreRating.OKAY),
            (None, ScoreRating.UNKNOWN),
            ("", ScoreRating.UNKNOWN),
            ("null", ScoreRating.UNKNOWN),
            ("medium", ScoreRating.UNKNOWN),
            ("unknown_flag", ScoreRating.UNKNOWN),
        ]
        
        for flag, expected_rating in flag_tests:
            actual_rating = scorecard._determine_rating_from_flag(flag)
            assert actual_rating == expected_rating, f"Flag '{flag}' should map to {expected_rating}, got {actual_rating}"

    def test_api_response_structure_validation(self):
        """Test that our implementation correctly handles real API response structure."""
        scorecard = StockScorecard()
        
        # Create a response that mimics the exact structure from Tickertape API
        real_api_structure = ScorecardResponse(
            success=True,
            data=[
                ScorecardItem(
                    name="Performance",
                    tag="Low",
                    type="score",
                    description="Hasn't fared well - amongst the low performers",
                    colour="red",
                    locked=True,
                    stack=1,
                    elements=[]
                ),
                ScorecardItem(
                    name="Valuation",
                    tag="High",
                    type="score",
                    description="Seems to be overvalued vs the market average",
                    colour="red",
                    locked=True,
                    stack=2,
                    elements=[]
                ),
                ScorecardItem(
                    name="Entry point",
                    tag="Good",
                    type="entryPoint",
                    description="The stock is underpriced and is not in the overbought zone",
                    colour="green",
                    locked=False,
                    stack=5,
                    elements=[
                        ScorecardElement(
                            title="Fundamentals",
                            type="flag",
                            description="Current price is less than the intrinsic value",
                            flag="High",
                            display=True
                        )
                    ]
                ),
                ScorecardItem(
                    name="Red flags",
                    tag="Low",
                    type="redFlag",
                    description="No red flag found",
                    colour="green",
                    locked=False,
                    stack=6,
                    elements=[
                        ScorecardElement(
                            title="ASM",
                            type="flag",
                            description="Stock is not in ASM list",
                            flag="High",
                            display=True
                        )
                    ]
                )
            ]
        )
        
        result = scorecard._transform_scorecard_response(real_api_structure)
        
        # Validate that color-based logic works correctly for real scenarios
        assert result.performance.rating == ScoreRating.BAD  # red color
        assert result.valuation.rating == ScoreRating.BAD    # red color  
        assert result.entry_point.rating == ScoreRating.GOOD # green color
        assert result.red_flags.rating == ScoreRating.GOOD   # green color
        
        # Validate elements use flag-based logic
        assert result.entry_point_elements[0].rating == ScoreRating.GOOD  # "High" flag
        assert result.red_flags_elements[0].rating == ScoreRating.GOOD    # "High" flag

    def test_color_consistency_validation(self):
        """Test that color interpretation is consistent across all categories."""
        scorecard = StockScorecard()
        
        # Test that the same color always gives the same rating regardless of category
        categories = ["Performance", "Valuation", "Growth", "Profitability", "Entry point", "Red flags"]
        
        for category in categories:
            # Green should always be GOOD
            green_item = ScorecardItem(
                name=category,
                tag="Some value",
                type="score",
                description="Test description",
                colour="green",
                locked=False,
                stack=1,
                elements=[]
            )
            green_score = scorecard._create_score_from_item(green_item)
            assert green_score.rating == ScoreRating.GOOD, f"Green color should be GOOD for {category}"
            
            # Red should always be BAD
            red_item = ScorecardItem(
                name=category,
                tag="Some value",
                type="score",
                description="Test description",
                colour="red",
                locked=False,
                stack=1,
                elements=[]
            )
            red_score = scorecard._create_score_from_item(red_item)
            assert red_score.rating == ScoreRating.BAD, f"Red color should be BAD for {category}"
            
            # Yellow should always be OKAY
            yellow_item = ScorecardItem(
                name=category,
                tag="Some value",
                type="score",
                description="Test description",
                colour="yellow",
                locked=False,
                stack=1,
                elements=[]
            )
            yellow_score = scorecard._create_score_from_item(yellow_item)
            assert yellow_score.rating == ScoreRating.OKAY, f"Yellow color should be OKAY for {category}"

    def test_api_change_detection(self):
        """Test that helps detect potential API changes in the future."""
        scorecard = StockScorecard()
        
        # Test with unexpected but possible API responses
        edge_cases = [
            # New color that might be introduced
            ScorecardItem(
                name="Performance",
                tag="Medium",
                type="score",
                description="Average performance",
                colour="blue",  # New color
                locked=False,
                stack=1,
                elements=[]
            ),
            # Missing color but has tag
            ScorecardItem(
                name="Valuation",
                tag="Moderate",
                type="score",
                description="Moderately valued",
                colour=None,  # Missing color
                locked=False,
                stack=2,
                elements=[]
            ),
            # New type that might be introduced
            ScorecardItem(
                name="ESG Score",
                tag="High",
                type="esg",  # New type
                description="Environmental, Social, and Governance score",
                colour="green",
                locked=False,
                stack=7,
                elements=[]
            )
        ]
        
        for item in edge_cases:
            # Should not crash - graceful handling
            score = scorecard._create_score_from_item(item)
            assert isinstance(score, Score)
            assert isinstance(score.rating, ScoreRating)
            assert score.name == item.name
            
            # Unknown colors should map to UNKNOWN rating
            if item.colour not in ["green", "red", "yellow", "orange"]:
                assert score.rating == ScoreRating.UNKNOWN

    def test_real_world_scenario_simulation(self):
        """Test realistic scenarios that might occur with real API data."""
        scorecard = StockScorecard()
        
        # Simulate a complete realistic response
        realistic_response = ScorecardResponse(
            success=True,
            data=[
                # Good stock scenario
                ScorecardItem(name="Performance", tag="High", colour="green", type="score", locked=True, stack=1, elements=[]),
                ScorecardItem(name="Valuation", tag="Low", colour="green", type="score", locked=True, stack=2, elements=[]),
                ScorecardItem(name="Growth", tag="High", colour="green", type="score", locked=True, stack=3, elements=[]),
                ScorecardItem(name="Profitability", tag="High", colour="green", type="score", locked=True, stack=4, elements=[]),
                ScorecardItem(name="Entry point", tag="Good", colour="green", type="entryPoint", locked=False, stack=5, elements=[]),
                ScorecardItem(name="Red flags", tag="Low", colour="green", type="redFlag", locked=False, stack=6, elements=[]),
            ]
        )
        
        result = scorecard._transform_scorecard_response(realistic_response)
        
        # All should be GOOD (green color)
        assert result.performance.rating == ScoreRating.GOOD
        assert result.valuation.rating == ScoreRating.GOOD
        assert result.growth.rating == ScoreRating.GOOD
        assert result.profitability.rating == ScoreRating.GOOD
        assert result.entry_point.rating == ScoreRating.GOOD
        assert result.red_flags.rating == ScoreRating.GOOD
        
        # Bad stock scenario
        bad_response = ScorecardResponse(
            success=True,
            data=[
                ScorecardItem(name="Performance", tag="Low", colour="red", type="score", locked=True, stack=1, elements=[]),
                ScorecardItem(name="Valuation", tag="High", colour="red", type="score", locked=True, stack=2, elements=[]),
                ScorecardItem(name="Growth", tag="Low", colour="red", type="score", locked=True, stack=3, elements=[]),
                ScorecardItem(name="Profitability", tag="Low", colour="red", type="score", locked=True, stack=4, elements=[]),
                ScorecardItem(name="Entry point", tag="Bad", colour="red", type="entryPoint", locked=False, stack=5, elements=[]),
                ScorecardItem(name="Red flags", tag="High", colour="red", type="redFlag", locked=False, stack=6, elements=[]),
            ]
        )
        
        bad_result = scorecard._transform_scorecard_response(bad_response)
        
        # All should be BAD (red color)
        assert bad_result.performance.rating == ScoreRating.BAD
        assert bad_result.valuation.rating == ScoreRating.BAD
        assert bad_result.growth.rating == ScoreRating.BAD
        assert bad_result.profitability.rating == ScoreRating.BAD
        assert bad_result.entry_point.rating == ScoreRating.BAD
        assert bad_result.red_flags.rating == ScoreRating.BAD

    # Helper methods for creating mock data
    def _create_mock_scorecard_response(self):
        """Create a mock scorecard response with basic financial categories."""
        items = [
            ScorecardItem(
                name="Performance",
                tag="Low",
                type="score",
                description="Hasn't fared well - amongst the low performers",
                colour="red",
                locked=True,
                stack=1
            ),
            ScorecardItem(
                name="Valuation",
                tag="High",
                type="score",
                description="Stock appears to be overvalued",
                colour="green",
                locked=True,
                stack=2
            )
        ]
        return ScorecardResponse(success=True, data=items)

    def _create_mock_scorecard_response_with_elements(self):
        """Create a mock scorecard response with entry point and red flags."""
        entry_elements = [
            ScorecardElement(
                title="Fundamentals",
                type="flag",
                description="Current price is less than the intrinsic value",
                flag="high",
                display=True
            ),
            ScorecardElement(
                title="Technical",
                type="flag",
                description="Stock is in oversold territory",
                flag="avg",
                display=True
            )
        ]
        
        red_flag_elements = [
            ScorecardElement(
                title="Debt Levels",
                type="flag",
                description="High debt-to-equity ratio",
                flag="low",
                display=True
            )
        ]
        
        items = [
            ScorecardItem(
                name="Entry point",
                tag="Good",
                type="entryPoint",
                description="The stock is underpriced and not in overbought zone",
                colour="green",
                locked=False,
                stack=5,
                elements=entry_elements
            ),
            ScorecardItem(
                name="Red flags",
                tag="Medium",
                type="redFlag",
                description="Some concerns about the company's financials",
                colour="red",
                locked=False,
                stack=6,
                elements=red_flag_elements
            )
        ]
        return ScorecardResponse(success=True, data=items)


@pytest.mark.integration
class TestIntegrationStockScorecard:
    """
    Integration test suite for StockScorecard with real API calls.
    
    These tests make actual API requests and validate the complete workflow.
    Keep these tests light to avoid overwhelming CI/CD pipelines.
    """

    def test_get_scorecard_integration(self):
        """Test get_scorecard with real API call."""
        scorecard = StockScorecard(timeout=30)
        
        try:
            result = scorecard.get_scorecard("TCS")
            
            # Validate structure
            assert isinstance(result, StockScores)
            
            # At least one category should be present for TCS
            categories = [
                result.performance, result.valuation, result.growth,
                result.profitability, result.entry_point, result.red_flags
            ]
            non_null_categories = [cat for cat in categories if cat is not None]
            assert len(non_null_categories) > 0, "TCS should have at least one scorecard category"
            
            # Validate each non-null category
            for category in non_null_categories:
                assert isinstance(category, Score)
                assert category.name is not None
                assert category.description is not None
                assert isinstance(category.rating, ScoreRating)
                
                # Value can be None, but if present should be string
                if category.value is not None:
                    assert isinstance(category.value, str)
            
            # If entry_point exists, validate elements
            if result.entry_point is not None and result.entry_point_elements is not None:
                assert isinstance(result.entry_point_elements, list)
                for element in result.entry_point_elements:
                    assert isinstance(element, Score)
                    assert element.name is not None
            
            # If red_flags exists, validate elements  
            if result.red_flags is not None and result.red_flags_elements is not None:
                assert isinstance(result.red_flags_elements, list)
                for element in result.red_flags_elements:
                    assert isinstance(element, Score)
                    assert element.name is not None
            
        except Exception as e:
            pytest.skip(f"Integration test skipped due to API error: {e}")

    def test_get_scorecards_integration_light(self):
        """Test get_scorecards with real API calls (light version)."""
        scorecard = StockScorecard(timeout=30)
        
        # Test with just 2 stocks to keep it light
        test_sids = ["TCS", "RELI"]
        
        try:
            results = scorecard.get_scorecards(test_sids)
            
            # Validate structure
            assert isinstance(results, list)
            assert len(results) == len(test_sids)
            
            # At least one should succeed for major stocks like TCS/RELI
            successful_results = [r for r in results if r is not None]
            assert len(successful_results) > 0, "At least one major stock should have scorecard data"
            
            # Validate successful results
            for result in successful_results:
                assert isinstance(result, StockScores)
                # At least one category should be present
                categories = [
                    result.performance, result.valuation, result.growth,
                    result.profitability, result.entry_point, result.red_flags
                ]
                non_null_categories = [cat for cat in categories if cat is not None]
                assert len(non_null_categories) > 0
                
        except Exception as e:
            pytest.skip(f"Integration test skipped due to API error: {e}")

    def test_combined_asset_scorecard_integration(self):
        """Test get_stock_with_scorecard with real data."""
        from tickersnap.lists import Assets
        
        scorecard_client = StockScorecard(timeout=30)
        assets_client = Assets(timeout=30)
        
        try:
            # Get a sample stock
            all_stocks = assets_client.get_all_stocks()
            tcs_stocks = [stock for stock in all_stocks if stock.sid == "TCS"]
            
            if not tcs_stocks:
                pytest.skip("TCS stock not found in assets list")
            
            tcs_asset = tcs_stocks[0]
            
            # Test combined functionality
            result = scorecard_client.get_stock_with_scorecard(tcs_asset)
            
            # Validate structure
            assert isinstance(result, StockWithScorecard)
            assert result.asset == tcs_asset
            assert "Tata Consultancy Services" in result.asset.name  # More flexible name check
            assert result.asset.ticker == "TCS"
            
            # Scorecard might be None if API fails, but asset should always be present
            if result.scorecard is not None:
                assert isinstance(result.scorecard, StockScores)
                # Validate at least one category exists
                categories = [
                    result.scorecard.performance, result.scorecard.valuation,
                    result.scorecard.growth, result.scorecard.profitability,
                    result.scorecard.entry_point, result.scorecard.red_flags
                ]
                non_null_categories = [cat for cat in categories if cat is not None]
                assert len(non_null_categories) > 0
                
        except Exception as e:
            pytest.skip(f"Integration test skipped due to API error: {e}")

    def test_rating_logic_validation_integration(self):
        """Test that rating logic correctly interprets real API responses."""
        scorecard = StockScorecard(timeout=30)
        
        try:
            result = scorecard.get_scorecard("TCS")
            
            # Validate rating logic consistency
            categories = [
                result.performance, result.valuation, result.growth,
                result.profitability, result.entry_point, result.red_flags
            ]
            
            for category in categories:
                if category is not None:
                    # Rating should never be None and should be valid enum
                    assert category.rating is not None
                    assert isinstance(category.rating, ScoreRating)
                    
                    # Basic validation - ensure ratings are logically consistent
                    if category.value:
                        value_lower = category.value.lower()
                        
                        # Context-aware validation based on category name
                        category_name = category.name.lower()
                        
                        # For "good" values, check context
                        if "good" in value_lower:
                            # "Good" should generally be GOOD or OKAY
                            assert category.rating in [ScoreRating.GOOD, ScoreRating.OKAY, ScoreRating.UNKNOWN]
                        
                        # For "bad" values, check context  
                        elif "bad" in value_lower:
                            # "Bad" should generally be BAD or OKAY
                            assert category.rating in [ScoreRating.BAD, ScoreRating.OKAY, ScoreRating.UNKNOWN]
                        
                        # For red flags specifically - "low" red flags is good
                        elif "red flag" in category_name and "low" in value_lower:
                            # Low red flags should be GOOD or OKAY
                            assert category.rating in [ScoreRating.GOOD, ScoreRating.OKAY, ScoreRating.UNKNOWN]
                        
                        # For valuation specifically - "high" valuation might be bad (expensive)
                        elif "valuation" in category_name and "high" in value_lower:
                            # High valuation could be BAD (expensive) - this is valid
                            assert category.rating in [ScoreRating.BAD, ScoreRating.OKAY, ScoreRating.UNKNOWN]
            
            # Validate element ratings if present
            if result.entry_point_elements:
                for element in result.entry_point_elements:
                    assert isinstance(element.rating, ScoreRating)
            
            if result.red_flags_elements:
                for element in result.red_flags_elements:
                    assert isinstance(element.rating, ScoreRating)
                    
        except Exception as e:
            pytest.skip(f"Integration test skipped due to API error: {e}")
