"""
StockScorecard - Simplified Stock Scorecard Data for Analysis

Provides simplified access to stock scorecard data for common daily usage:

- `get_scorecard()`: Get scorecard for a single stock
- `get_scorecards()`: Get scorecards for multiple stocks with progress tracking
- `get_stock_with_scorecard()`: Get combined asset + scorecard data for single stock
- `get_stocks_with_scorecards()`: Get combined asset +
    scorecard data for multiple stocks

Removes API complexity and provides clean, user-friendly scorecard analysis.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional, Union

from ..lists.models import AssetData
from .api import StockScorecardAPI
from .models import (
    Score,
    ScorecardElement,
    ScorecardItem,
    ScorecardResponse,
    ScoreRating,
    StockScores,
    StockWithScorecard,
)

# Type definitions for progress tracking
ProgressCallback = Callable[[int, int, str], None]
ProgressType = Union[bool, ProgressCallback]


class StockScorecard:
    """
    Simplified stock scorecard data for market analysis.

    Removes the Tickertape API complexity and provides simple functions to get
    scorecard data that users need for daily stock analysis and screening.

    Features:
        - Single and batch scorecard retrieval
        - Combined asset + scorecard data
        - Progress tracking for large batches
        - Concurrent processing for performance
        - Error resilience (partial failures don't stop the process)
    """

    def __init__(self, timeout: int = 10, max_workers: int = 10):
        """
        Initialize StockScorecard.

        Args:
            timeout (int): Request timeout in seconds. Defaults to 10.
            max_workers (int): Maximum concurrent workers for batch operations.
                Defaults to 10.
        """

        self.timeout = timeout
        self.max_workers = max_workers
        self._progress_lock = threading.Lock()

    def get_scorecard(self, sid: str) -> StockScores:
        """
        Get scorecard for a single stock by SID.

        Args:
            sid (str): Stock SID (Security ID) as used by Tickertape.

        Returns:
            StockScores: Simplified scorecard data with user-friendly ratings.

        Raises:
            Exception: If the API request fails or SID is invalid.
        """

        with StockScorecardAPI(timeout=self.timeout) as client:
            response = client.get_data(sid)

        return self._transform_scorecard_response(response)

    def get_scorecards(
        self,
        sids: List[str],
        progress: Optional[ProgressType] = None,
    ) -> List[Optional[StockScores]]:
        """
        Get scorecards for multiple stocks by SID list.

        Args:
            sids (List[str]): List of stock SIDs to fetch.
            progress: Progress tracking options:
                - None (default): No progress tracking
                - True: Show tqdm progress bar (requires: pip install tqdm)
                - False: (same as None) No progress tracking
                - Callable: Custom progress function(completed, total, current_sid)

        Returns:
            List[Optional[StockScores]]: List of scorecard data.
                None entries indicate failed requests for that SID.

        Note:
            - Uses concurrent processing for better performance
            - Partial failures don't stop the entire process
            - Order matches input SID order
        """

        if not sids:
            return []

        results = [None] * len(sids)
        completed_count = 0
        progress_bar = None

        # Initialize progress tracking
        if progress is True:
            progress_bar = self._init_progress_bar(len(sids), "Fetching scorecards")
        elif progress is False:
            progress = None

        def fetch_single(index: int, sid: str) -> None:
            nonlocal completed_count
            try:
                with StockScorecardAPI(timeout=self.timeout) as client:
                    response = client.get_data(sid)
                    results[index] = self._transform_scorecard_response(response)
            except Exception:
                # Silently handle individual failures
                results[index] = None

            # Update progress
            with self._progress_lock:
                completed_count += 1
                self._update_progress(
                    progress, progress_bar, completed_count, len(sids), sid
                )

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(fetch_single, i, sid) for i, sid in enumerate(sids)
            ]
            # Wait for all to complete
            for future in as_completed(futures):
                # raise any unexpected exceptions
                future.result()

        # Close progress bar if using tqdm
        if progress_bar:
            progress_bar.close()

        return results

    def get_stock_with_scorecard(self, asset: AssetData) -> StockWithScorecard:
        """
        Get combined asset + scorecard data for single stock.

        Args:
            asset (AssetData): Stock asset information.

        Returns:
            StockWithScorecard: Combined asset and scorecard data.
                scorecard will be None if the API request fails.
        """

        try:
            scorecard = self.get_scorecard(asset.sid)
        except Exception:
            scorecard = None

        return StockWithScorecard(asset=asset, scorecard=scorecard)

    def get_stocks_with_scorecards(
        self,
        assets: List[AssetData],
        progress: Optional[ProgressType] = None,
    ) -> List[StockWithScorecard]:
        """
        Get combined asset + scorecard data for multiple stocks.

        Args:
            assets (List[AssetData]): List of stock asset information.
            progress: Progress tracking options:
                - None (default): No progress tracking
                - True: Show tqdm progress bar (requires: pip install tqdm)
                - False: (same as None) No progress tracking
                - Callable: Custom progress function(completed, total, current_name)

        Returns:
            List[StockWithScorecard]: List of combined asset and scorecard data.
                scorecard will be None for assets where API requests failed.

        Note:
            - Uses concurrent processing for better performance
            - Partial failures don't stop the entire process
            - Order matches input assets order
        """

        if not assets:
            return []

        results = [None] * len(assets)
        completed_count = 0
        progress_bar = None

        # Initialize progress tracking
        if progress is True:
            progress_bar = self._init_progress_bar(
                len(assets), "Fetching stock scorecards"
            )
        elif progress is False:
            progress = None

        def fetch_single(index: int, asset: AssetData) -> None:
            nonlocal completed_count
            try:
                scorecard = self.get_scorecard(asset.sid)
            except Exception:
                scorecard = None

            results[index] = StockWithScorecard(asset=asset, scorecard=scorecard)

            # Update progress
            with self._progress_lock:
                completed_count += 1
                self._update_progress(
                    progress, progress_bar, completed_count, len(assets), asset.name
                )

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(fetch_single, i, asset)
                for i, asset in enumerate(assets)
            ]
            # Wait for all to complete
            for future in as_completed(futures):
                # raise any unexpected exceptions
                future.result()

        # Close progress bar if using tqdm
        if progress_bar:
            progress_bar.close()

        return results

    def _transform_scorecard_response(self, response: ScorecardResponse) -> StockScores:
        """
        Transform raw API response to user-friendly StockScores.

        Args:
            response (ScorecardResponse): Raw stock scorecard API response
                from Tickertape.

        Returns:
            StockScores: Simplified stock scorecard data.
        """

        if not response.success or not response.data:
            return StockScores()

        scores = StockScores()

        for item in response.data:
            item_name = item.name.lower()

            if item_name == "performance":
                scores.performance = self._create_score_from_item(item)
            elif item_name == "valuation":
                scores.valuation = self._create_score_from_item(item)
            elif item_name == "growth":
                scores.growth = self._create_score_from_item(item)
            elif item_name == "profitability":
                scores.profitability = self._create_score_from_item(item)
            elif item_name == "entry point":
                scores.entry_point = self._create_score_from_item(item)
                scores.entry_point_elements = self._create_scores_from_elements(
                    item.elements
                )
            elif item_name == "red flags":
                scores.red_flags = self._create_score_from_item(item)
                scores.red_flags_elements = self._create_scores_from_elements(
                    item.elements
                )

        return scores

    def _create_score_from_item(self, item: ScorecardItem) -> Score:
        """
        Create a Score object from a ScorecardItem.

        Args:
            item (ScorecardItem): Raw scorecard item.

        Returns:
            Score: Simplified score with rating.
        """

        # Format the description
        description = item.description or f"{item.name} assessment"

        # Extract value from tag or description
        value = item.tag or item.colour or "Unknown"

        # Determine rating based on color and value
        rating = self._determine_rating(item.colour)

        return Score(
            name=item.name,
            description=description,
            value=value,
            rating=rating,
        )

    def _create_scores_from_elements(
        self, elements: List[ScorecardElement]
    ) -> List[Score]:
        """
        Create Score objects from scorecard elements.

        Args:
            elements: List of scorecard elements.

        Returns:
            List[Score]: List of simplified scores.
        """

        scores = []
        for element in elements:

            # Format the description
            description = element.description or f"{element.title} assessment"

            # Extract value from flag or description
            value = element.flag or element.score or "Unknown"

            # Determine rating based on flag or description
            rating = self._determine_rating_from_flag(element.flag)

            scores.append(
                Score(
                    name=element.title,
                    description=description,
                    value=value,
                    rating=rating,
                )
            )
        return scores

    def _determine_rating(self, colour: Optional[str]) -> ScoreRating:
        """
        Determine rating based on color from API.

        Args:
            colour (Optional[str]): Color indicator from API ("green", "red", "yellow").

        Returns:
            ScoreRating: Simplified rating.
        """

        if not colour:
            return ScoreRating.UNKNOWN

        colour_lower = colour.lower()

        # color-based rating
        # first one is the current api response, rest are just fancy future proofing
        if colour_lower in ["green"]:
            return ScoreRating.GOOD
        elif colour_lower in ["red"]:
            return ScoreRating.BAD
        elif colour_lower in ["yellow", "orange"]:
            return ScoreRating.OKAY

        # TODO: add context-aware interpretation of rating based on name and value
        # if in future the color fails from tickertape

        return ScoreRating.UNKNOWN

    def _determine_rating_from_flag(self, flag: Optional[str]) -> ScoreRating:
        """
        Determine rating based on flag value for elements.

        Args:
            flag (Optional[str]): Flag value from element ("high", "avg", "low", "null")

        Returns:
            ScoreRating: Simplified rating.
        """

        if not flag:
            return ScoreRating.UNKNOWN

        flag_lower = flag.lower()

        if flag_lower in ["high"]:
            return ScoreRating.GOOD
        elif flag_lower in ["low"]:
            return ScoreRating.BAD
        elif flag_lower in ["avg"]:
            return ScoreRating.OKAY

        return ScoreRating.UNKNOWN

    def _init_progress_bar(self, total: int, desc: str):
        """
        Initialize tqdm progress bar if available.

        Args:
            total (int): Total number of items.
            desc (str): Description for progress bar.

        Returns:
            Progress bar object or None.
        """

        try:
            from tqdm import tqdm

            return tqdm(total=total, desc=desc)
        except ImportError:
            print(f"tqdm not installed, using simple progress tracking for: {desc}")
            return None

    def _update_progress(
        self,
        progress: Optional[ProgressType],
        progress_bar,
        completed: int,
        total: int,
        current_item: str,
    ):
        """
        Update progress tracking.

        Args:
            progress: Progress tracking option.
            progress_bar: tqdm progress bar (if available).
            completed (int): Number of completed items.
            total (int): Total number of items.
            current_item (str): Current item being processed.
        """

        if progress_bar:
            progress_bar.update(1)
        elif progress is True:
            # Fallback to simple print if tqdm not available
            print(f"Progress: {completed}/{total} - {current_item}")
        elif callable(progress):
            progress(completed, total, current_item)
