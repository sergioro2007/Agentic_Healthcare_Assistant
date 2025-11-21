"""
Tests for the Medical Search Tools.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tools.medical_search_tools import BingSearchTool, MedlineSearchTool, WHOSearchTool, MedicalSearchAggregator

class TestBingSearchTool:
    """Test suite for BingSearchTool."""
    
    def test_initialization(self):
        """Test initialization."""
        tool = BingSearchTool(api_key="test-key")
        assert tool.api_key == "test-key"
        
    def test_mock_search(self):
        """Test fallback to mock search when no API key."""
        tool = BingSearchTool(api_key=None)
        results = tool.search("diabetes")
        assert len(results) > 0
        assert "Mock Bing Search" in results[0]["source"]
        
    @patch('requests.get')
    def test_real_search(self, mock_get):
        """Test real search with API key."""
        tool = BingSearchTool(api_key="test-key")
        
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "webPages": {
                "value": [
                    {"name": "Result 1", "url": "http://example.com", "snippet": "Snippet 1"}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        results = tool.search("diabetes")
        
        assert len(results) == 1
        assert results[0]["title"] == "Result 1"
        assert results[0]["source"] == "Bing Search"

class TestMedlineSearchTool:
    """Test suite for MedlineSearchTool."""
    
    def test_initialization(self):
        """Test initialization."""
        tool = MedlineSearchTool(api_key="test-key", email="test@example.com")
        assert tool.api_key == "test-key"
        assert tool.email == "test@example.com"
        
    def test_mock_search(self):
        """Test fallback to mock search when no API key."""
        tool = MedlineSearchTool(api_key=None)
        results = tool.search("diabetes")
        assert len(results) > 0
        assert "Mock PubMed/Medline" in results[0]["source"]

class TestWHOSearchTool:
    """Test suite for WHOSearchTool."""
    
    def test_search_known_topic(self):
        """Test searching for a known topic."""
        tool = WHOSearchTool()
        results = tool.search("diabetes")
        assert len(results) > 0
        assert "Diabetes" in results[0]["title"]
        assert results[0]["source"] == "WHO"
        
    def test_search_unknown_topic(self):
        """Test searching for an unknown topic."""
        tool = WHOSearchTool()
        results = tool.search("unknown topic")
        assert len(results) > 0
        assert "WHO Health Topics" in results[0]["title"]

class TestMedicalSearchAggregator:
    """Test suite for MedicalSearchAggregator."""
    
    def test_initialization(self):
        """Test initialization."""
        aggregator = MedicalSearchAggregator(bing_api_key="test-key")
        assert aggregator.bing is not None
        assert aggregator.medline is not None
        assert aggregator.who is not None
        
    def test_search_all(self):
        """Test searching all sources."""
        aggregator = MedicalSearchAggregator() # No keys -> mocks
        results = aggregator.search_all("diabetes")
        
        assert "bing" in results
        assert "medline" in results
        assert "who" in results
        assert len(results["bing"]) > 0
        
    def test_get_combined_results(self):
        """Test getting combined results."""
        aggregator = MedicalSearchAggregator() # No keys -> mocks
        results = aggregator.get_combined_results("diabetes")
        
        assert len(results) > 0
        # Check if sorted (WHO first)
        assert results[0]["source"] == "WHO"
        
    def test_clear_all_caches(self):
        """Test clearing caches."""
        aggregator = MedicalSearchAggregator()
        # Manually populate cache since mock search doesn't cache
        aggregator.bing.results_cache["test"] = ["result"]
        aggregator.medline.results_cache["test"] = ["result"]
        aggregator.who.results_cache["test"] = ["result"]
        
        # Check caches are populated
        assert len(aggregator.bing.results_cache) > 0
        assert len(aggregator.medline.results_cache) > 0
        assert len(aggregator.who.results_cache) > 0
        
        aggregator.clear_all_caches()
        
        # Check caches are empty
        assert len(aggregator.bing.results_cache) == 0
        assert len(aggregator.medline.results_cache) == 0
        assert len(aggregator.who.results_cache) == 0
