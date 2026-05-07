"""
Purpose: Unit tests for version-freshness cache module

Scope: Cache paths, freshness checking, load/save, fetch (mocked), offline fallback

Overview: Tests the cache layer for endoflife.date API data including cache directory
    resolution, freshness checking, loading/saving JSON files, API fetch with mocked
    requests, and offline fallback to stale cache.
"""

import json
import time
from unittest.mock import MagicMock, patch

from src.linters.version_freshness.cache import (
    _fetch_from_api,
    _load_cache,
    _save_cache,
    get_cache_dir,
    get_product_data,
    is_cache_fresh,
)


class TestGetCacheDir:
    """Tests for cache directory resolution."""

    def test_returns_path_under_home(self):
        """Should return path under ~/.cache/thailint/endoflife/."""
        cache_dir = get_cache_dir()
        assert cache_dir.parts[-2:] == ("thailint", "endoflife")
        assert ".cache" in str(cache_dir)


class TestIsCacheFresh:
    """Tests for cache freshness checking."""

    def test_nonexistent_file_is_not_fresh(self, tmp_path):
        """Should return False for nonexistent file."""
        assert is_cache_fresh(tmp_path / "missing.json", 24) is False

    def test_recent_file_is_fresh(self, tmp_path):
        """Should return True for recently created file."""
        cache_file = tmp_path / "python.json"
        cache_file.write_text("[]")
        assert is_cache_fresh(cache_file, 24) is True

    def test_old_file_is_not_fresh(self, tmp_path):
        """Should return False for file older than TTL."""
        cache_file = tmp_path / "python.json"
        cache_file.write_text("[]")
        # Set mtime to 25 hours ago
        old_time = time.time() - (25 * 3600)
        import os

        os.utime(cache_file, (old_time, old_time))
        assert is_cache_fresh(cache_file, 24) is False

    def test_zero_ttl_is_never_fresh(self, tmp_path):
        """Should return False for zero TTL (always refresh)."""
        cache_file = tmp_path / "python.json"
        cache_file.write_text("[]")
        assert is_cache_fresh(cache_file, 0) is False


class TestLoadCache:
    """Tests for loading cache files."""

    def test_loads_valid_json(self, tmp_path):
        """Should load valid JSON list."""
        cache_file = tmp_path / "python.json"
        data = [{"cycle": "3.12", "eol": "2028-10-31"}]
        cache_file.write_text(json.dumps(data))
        assert _load_cache(cache_file) == data

    def test_returns_none_for_invalid_json(self, tmp_path):
        """Should return None for invalid JSON."""
        cache_file = tmp_path / "bad.json"
        cache_file.write_text("not json")
        assert _load_cache(cache_file) is None

    def test_returns_none_for_non_list(self, tmp_path):
        """Should return None if JSON is not a list."""
        cache_file = tmp_path / "dict.json"
        cache_file.write_text('{"key": "value"}')
        assert _load_cache(cache_file) is None


class TestSaveCache:
    """Tests for saving cache files."""

    def test_saves_json(self, tmp_path):
        """Should save data as JSON file."""
        cache_file = tmp_path / "python.json"
        data = [{"cycle": "3.12", "eol": "2028-10-31"}]
        _save_cache(cache_file, data)
        assert json.loads(cache_file.read_text()) == data

    def test_creates_parent_directories(self, tmp_path):
        """Should create parent directories if they don't exist."""
        cache_file = tmp_path / "deep" / "nested" / "python.json"
        _save_cache(cache_file, [])
        assert cache_file.exists()


class TestFetchFromApi:
    """Tests for API fetching (mocked)."""

    @patch("requests.get")
    def test_fetches_product_data(self, mock_get):
        """Should fetch data from endoflife.date API."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"cycle": "3.12", "eol": "2028-10-31"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = _fetch_from_api("python")
        assert result == [{"cycle": "3.12", "eol": "2028-10-31"}]
        mock_get.assert_called_once_with("https://endoflife.date/api/python.json", timeout=10)

    @patch("requests.get")
    def test_returns_none_on_network_error(self, mock_get):
        """Should return None on network failure."""
        import requests

        mock_get.side_effect = requests.RequestException("timeout")
        result = _fetch_from_api("python")
        assert result is None


class TestGetProductData:
    """Tests for the main get_product_data function."""

    @patch("src.linters.version_freshness.cache.get_cache_dir")
    @patch("src.linters.version_freshness.cache._fetch_from_api")
    def test_uses_fresh_cache(self, mock_fetch, mock_cache_dir, tmp_path):
        """Should use fresh cache without fetching."""
        mock_cache_dir.return_value = tmp_path
        cache_file = tmp_path / "python.json"
        data = [{"cycle": "3.12"}]
        cache_file.write_text(json.dumps(data))

        result = get_product_data("python", ttl_hours=24)
        assert result == data
        mock_fetch.assert_not_called()

    @patch("src.linters.version_freshness.cache.get_cache_dir")
    @patch("src.linters.version_freshness.cache._fetch_from_api")
    def test_fetches_when_cache_stale(self, mock_fetch, mock_cache_dir, tmp_path):
        """Should fetch from API when cache is stale."""
        mock_cache_dir.return_value = tmp_path
        fresh_data = [{"cycle": "3.13"}]
        mock_fetch.return_value = fresh_data

        result = get_product_data("python", ttl_hours=0)
        assert result == fresh_data

    @patch("src.linters.version_freshness.cache.get_cache_dir")
    @patch("src.linters.version_freshness.cache._fetch_from_api")
    def test_falls_back_to_stale_cache(self, mock_fetch, mock_cache_dir, tmp_path):
        """Should use stale cache when API fails."""
        mock_cache_dir.return_value = tmp_path
        cache_file = tmp_path / "python.json"
        stale_data = [{"cycle": "3.11"}]
        cache_file.write_text(json.dumps(stale_data))
        mock_fetch.return_value = None

        result = get_product_data("python", ttl_hours=0)
        assert result == stale_data

    @patch("src.linters.version_freshness.cache.get_cache_dir")
    @patch("src.linters.version_freshness.cache._fetch_from_api")
    def test_returns_none_no_cache_no_api(self, mock_fetch, mock_cache_dir, tmp_path):
        """Should return None when no cache and API fails."""
        mock_cache_dir.return_value = tmp_path
        mock_fetch.return_value = None

        result = get_product_data("unknown-product", ttl_hours=24)
        assert result is None
