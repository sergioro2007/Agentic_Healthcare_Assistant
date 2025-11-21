"""
Web Search Tools for Medical Information Retrieval.
Integrates with external APIs for disease information from trusted sources.
"""
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class WebSearchTool:
    """Base class for web search tools."""
    
    def __init__(self, api_key: str = None):
        """Initialize the search tool."""
        self.api_key = api_key
        self.results_cache = {}
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute search query."""
        raise NotImplementedError("Subclasses must implement search method")
    
    def _cache_key(self, query: str, **kwargs) -> str:
        """Generate cache key for query."""
        return f"{query}_{json.dumps(kwargs, sort_keys=True)}"
    
    def clear_cache(self) -> None:
        """Clear the results cache."""
        self.results_cache = {}


class BingSearchTool(WebSearchTool):
    """
    Bing Web Search API integration for medical information.
    Focuses on authoritative health sources.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize Bing Search tool."""
        super().__init__(api_key or os.getenv("BING_SEARCH_API_KEY"))
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.api_key} if self.api_key else {}
    
    def search(
        self,
        query: str,
        count: int = 5,
        market: str = "en-US",
        safe_search: str = "Moderate"
    ) -> List[Dict[str, Any]]:
        """
        Search for medical information using Bing.
        
        Args:
            query: Search query
            count: Number of results
            market: Market/language
            safe_search: Safe search level
            
        Returns:
            List of search results
        """
        if not self.api_key:
            print(f"⚠️  Bing API key not configured - using mock Bing data")
            return self._mock_search(query, count)
        
        # Check cache
        cache_key = self._cache_key(query, count=count, market=market)
        if cache_key in self.results_cache:
            print(f"✅ Using cached Bing results for: {query}")
            return self.results_cache[cache_key]
        
        # Build medical-focused query
        medical_query = f"{query} site:nih.gov OR site:who.int OR site:cdc.gov OR site:mayoclinic.org"
        
        params = {
            "q": medical_query,
            "count": count,
            "mkt": market,
            "safeSearch": safe_search
        }
        
        try:
            print(f"🔍 Searching REAL Bing API for: {query}")
            response = requests.get(self.endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                    "source": "Bing Search",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Cache results
            self.results_cache[cache_key] = results
            print(f"✅ Successfully retrieved {len(results)} REAL Bing results")
            
            return results
            
        except Exception as e:
            print(f"❌ Bing Search API error: {str(e)} - falling back to mock data")
            return self._mock_search(query, count)
    
    def _mock_search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Return mock search results when API is not available."""
        return [
            {
                "title": f"Medical Information about {query}",
                "url": f"https://www.nih.gov/search?query={query.replace(' ', '+')}",
                "snippet": f"Authoritative medical information about {query} from trusted sources.",
                "source": "Mock Bing Search",
                "timestamp": datetime.now().isoformat()
            }
        ]


class MedlineSearchTool(WebSearchTool):
    """
    PubMed/Medline API integration for medical literature search.
    Uses NCBI E-utilities API.
    """
    
    def __init__(self, api_key: str = None, email: str = None):
        """Initialize Medline search tool."""
        super().__init__(api_key or os.getenv("NCBI_API_KEY"))
        self.email = email or os.getenv("NCBI_EMAIL", "healthcare.assistant@example.com")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        sort: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search PubMed/Medline for medical articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            sort: Sort order (relevance, pub_date)
            
        Returns:
            List of article results
        """
        # Check if we should use real API or mocks
        if not self.api_key or not self.email:
            print(f"⚠️  NCBI API key or email not configured - using mock PubMed data")
            return self._mock_medline_search(query, max_results)
        
        # Check cache
        cache_key = self._cache_key(query, max_results=max_results, sort=sort)
        if cache_key in self.results_cache:
            print(f"✅ Using cached PubMed results for: {query}")
            return self.results_cache[cache_key]
        
        try:
            print(f"🔍 Searching REAL PubMed API for: {query}")
            
            # Step 1: Search for article IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": sort,
                "tool": "HealthcareAssistant",
                "email": self.email
            }
            
            if self.api_key:
                search_params["api_key"] = self.api_key
            
            search_url = f"{self.base_url}/esearch.fcgi"
            search_response = requests.get(search_url, params=search_params, timeout=10)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                print(f"ℹ️  No PubMed results found for: {query}")
                return []
            
            print(f"✅ Found {len(id_list)} PubMed articles")
            
            # Step 2: Fetch article summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
                "tool": "HealthcareAssistant",
                "email": self.email
            }
            
            if self.api_key:
                summary_params["api_key"] = self.api_key
            
            summary_url = f"{self.base_url}/esummary.fcgi"
            summary_response = requests.get(summary_url, params=summary_params, timeout=10)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # Parse results
            results = []
            for pmid in id_list:
                article = summary_data.get("result", {}).get(pmid, {})
                if article:
                    results.append({
                        "pmid": pmid,
                        "title": article.get("title", ""),
                        "authors": self._format_authors(article.get("authors", [])),
                        "journal": article.get("fulljournalname", ""),
                        "pub_date": article.get("pubdate", ""),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "snippet": article.get("title", "")[:200],  # Add snippet for consistency
                        "source": "PubMed/Medline",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Cache results
            self.results_cache[cache_key] = results
            print(f"✅ Successfully retrieved {len(results)} REAL PubMed articles")
            
            return results
            
        except Exception as e:
            print(f"❌ Medline Search API error: {str(e)} - falling back to mock data")
            return self._mock_medline_search(query, max_results)
    
    def _format_authors(self, authors: List[Dict]) -> str:
        """Format author list."""
        if not authors:
            return "Unknown"
        
        author_names = [a.get("name", "") for a in authors[:3]]
        formatted = ", ".join(author_names)
        
        if len(authors) > 3:
            formatted += " et al."
        
        return formatted
    
    def _mock_medline_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Return mock Medline results when API is not available."""
        return [
            {
                "pmid": "12345678",
                "title": f"Clinical Study on {query}",
                "authors": "Smith J, Johnson M, Williams K",
                "journal": "Journal of Medical Research",
                "pub_date": "2024",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(' ', '+')}",
                "source": "Mock PubMed/Medline",
                "timestamp": datetime.now().isoformat()
            }
        ]


class WHOSearchTool(WebSearchTool):
    """
    WHO (World Health Organization) information search.
    Searches WHO fact sheets and guidelines.
    """
    
    def __init__(self):
        """Initialize WHO search tool."""
        super().__init__()
        self.base_url = "https://www.who.int"
    
    def search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search WHO resources for disease information.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of WHO resources
        """
        # Check cache
        cache_key = self._cache_key(query, max_results=max_results)
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
        
        # For now, return structured mock data pointing to real WHO resources
        # In production, implement actual WHO API or web scraping
        results = self._get_who_resources(query, max_results)
        
        # Cache results
        self.results_cache[cache_key] = results
        
        return results
    
    def _get_who_resources(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get WHO resources for common health topics."""
        # Common WHO fact sheets and resources
        who_resources = {
            "diabetes": {
                "title": "Diabetes - WHO Fact Sheet",
                "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
                "snippet": "Key facts about diabetes from the World Health Organization"
            },
            "hypertension": {
                "title": "Hypertension - WHO Fact Sheet",
                "url": "https://www.who.int/news-room/fact-sheets/detail/hypertension",
                "snippet": "Global overview of hypertension statistics and prevention"
            },
            "covid": {
                "title": "Coronavirus disease (COVID-19) - WHO",
                "url": "https://www.who.int/health-topics/coronavirus",
                "snippet": "WHO guidance and resources on COVID-19"
            }
        }
        
        results = []
        query_lower = query.lower()
        
        # Check for matching topics
        for topic, resource in who_resources.items():
            if topic in query_lower:
                results.append({
                    "title": resource["title"],
                    "url": resource["url"],
                    "snippet": resource["snippet"],
                    "source": "WHO",
                    "timestamp": datetime.now().isoformat()
                })
        
        # If no specific match, return generic result
        if not results:
            results.append({
                "title": f"WHO Health Topics - {query}",
                "url": f"https://www.who.int/health-topics/{query.lower().replace(' ', '-')}",
                "snippet": f"World Health Organization information on {query}",
                "source": "WHO",
                "timestamp": datetime.now().isoformat()
            })
        
        return results[:max_results]


class MedicalSearchAggregator:
    """
    Aggregates results from multiple medical search tools.
    Provides unified interface for medical information retrieval.
    """
    
    def __init__(
        self,
        bing_api_key: str = None,
        ncbi_api_key: str = None,
        ncbi_email: str = None
    ):
        """Initialize the aggregator with all search tools."""
        self.bing = BingSearchTool(bing_api_key)
        self.medline = MedlineSearchTool(ncbi_api_key, ncbi_email)
        self.who = WHOSearchTool()
    
    def search_all(
        self,
        query: str,
        max_results_per_source: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search all medical information sources.
        
        Args:
            query: Search query
            max_results_per_source: Max results from each source
            
        Returns:
            Dictionary with results from each source
        """
        results = {
            "bing": self.bing.search(query, count=max_results_per_source),
            "medline": self.medline.search(query, max_results=max_results_per_source),
            "who": self.who.search(query, max_results=max_results_per_source)
        }
        
        return results
    
    def get_combined_results(
        self,
        query: str,
        max_total_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get combined and ranked results from all sources.
        
        Args:
            query: Search query
            max_total_results: Maximum total results to return
            
        Returns:
            Combined list of search results
        """
        all_results = self.search_all(query, max_results_per_source=5)
        
        # Combine all results
        combined = []
        for source_results in all_results.values():
            combined.extend(source_results)
        
        # Simple ranking: prioritize WHO and Medline
        def rank_result(result):
            source = result.get("source", "")
            if "WHO" in source:
                return 0
            elif "Medline" in source or "PubMed" in source:
                return 1
            else:
                return 2
        
        combined.sort(key=rank_result)
        
        return combined[:max_total_results]
    
    def clear_all_caches(self) -> None:
        """Clear caches for all search tools."""
        self.bing.clear_cache()
        self.medline.clear_cache()
        self.who.clear_cache()
