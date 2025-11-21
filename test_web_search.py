"""
Quick test to verify if web search tools are using real APIs or mock data.
"""
import os
from tools.medical_search_tools import BingSearchTool, MedlineSearchTool, WHOSearchTool, MedicalSearchAggregator

def test_bing_search():
    """Test Bing Search Tool."""
    print("\n" + "="*80)
    print("BING SEARCH TOOL TEST")
    print("="*80)
    
    bing_tool = BingSearchTool()
    
    if bing_tool.api_key:
        print(f"✓ Bing API key found: {bing_tool.api_key[:10]}...")
        print("  Status: Will use REAL Bing Search API")
    else:
        print("✗ No Bing API key found (BING_SEARCH_API_KEY)")
        print("  Status: Using MOCK data")
    
    print("\nTesting search for 'diabetes symptoms'...")
    results = bing_tool.search("diabetes symptoms", count=3)
    
    if results:
        print(f"\nReturned {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result.get('title')}")
            print(f"     Source: {result.get('source')}")
            print(f"     URL: {result.get('url')[:60]}...")
            
            # Check if it's mock data
            if "Mock" in result.get('source', ''):
                print("     ⚠️  This is MOCK data")
            else:
                print("     ✓ This is REAL API data")
    else:
        print("No results returned")

def test_medline_search():
    """Test Medline/PubMed Search Tool."""
    print("\n" + "="*80)
    print("MEDLINE/PUBMED SEARCH TOOL TEST")
    print("="*80)
    
    medline_tool = MedlineSearchTool()
    
    if medline_tool.api_key:
        print(f"✓ NCBI API key found: {medline_tool.api_key[:10]}...")
        print("  Status: Will use REAL PubMed API (with higher rate limits)")
    else:
        print("✗ No NCBI API key found (NCBI_API_KEY)")
        print("  Status: Will use REAL PubMed API (with lower rate limits)")
    
    print(f"  Email: {medline_tool.email}")
    
    print("\nTesting search for 'diabetes treatment'...")
    results = medline_tool.search("diabetes treatment", max_results=3)
    
    if results:
        print(f"\nReturned {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result.get('title')[:70]}...")
            print(f"     Source: {result.get('source')}")
            print(f"     PMID: {result.get('pmid')}")
            print(f"     Authors: {result.get('authors')}")
            
            # Check if it's mock data
            if "Mock" in result.get('source', ''):
                print("     ⚠️  This is MOCK data")
            else:
                print("     ✓ This is REAL API data")
    else:
        print("No results returned")

def test_who_search():
    """Test WHO Search Tool."""
    print("\n" + "="*80)
    print("WHO SEARCH TOOL TEST")
    print("="*80)
    
    who_tool = WHOSearchTool()
    
    print("  Status: Using predefined WHO resources (no API needed)")
    
    print("\nTesting search for 'covid-19'...")
    results = who_tool.search("covid-19", max_results=3)
    
    if results:
        print(f"\nReturned {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. {result.get('title')}")
            desc = result.get('description', 'N/A')
            if desc and desc != 'N/A':
                print(f"     Description: {desc[:70]}...")
            print(f"     URL: {result.get('url', 'N/A')[:60]}...")
    else:
        print("No results returned")

def test_aggregator():
    """Test Medical Search Aggregator."""
    print("\n" + "="*80)
    print("MEDICAL SEARCH AGGREGATOR TEST")
    print("="*80)
    
    aggregator = MedicalSearchAggregator()
    
    print("\nTesting aggregated search for 'hypertension'...")
    results = aggregator.get_combined_results("hypertension", max_total_results=5)
    
    if results:
        print(f"\nReturned {len(results)} combined results:")
        
        # Count by source
        sources = {}
        for result in results:
            source = result.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("\nResults by source:")
        for source, count in sources.items():
            status = "⚠️  MOCK" if "Mock" in source else "✓ REAL"
            print(f"  {source}: {count} results {status}")
    else:
        print("No results returned")

def check_environment_variables():
    """Check which API keys are configured."""
    print("\n" + "="*80)
    print("ENVIRONMENT VARIABLES CHECK")
    print("="*80)
    
    api_keys = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "BING_SEARCH_API_KEY": os.getenv("BING_SEARCH_API_KEY"),
        "NCBI_API_KEY": os.getenv("NCBI_API_KEY"),
        "NCBI_EMAIL": os.getenv("NCBI_EMAIL")
    }
    
    for key, value in api_keys.items():
        if value:
            print(f"✓ {key}: Set ({value[:10]}...)")
        else:
            print(f"✗ {key}: Not set")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("WEB SEARCH FUNCTIONALITY TEST")
    print("="*80)
    
    check_environment_variables()
    test_bing_search()
    test_medline_search()
    test_who_search()
    test_aggregator()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nSUMMARY:")
    print("- Bing Search: Will use MOCK data if BING_SEARCH_API_KEY not set")
    print("- PubMed/Medline: Will use REAL API (no key required, but recommended)")
    print("- WHO Search: Always uses predefined resources (no API needed)")
    print("\nTo enable REAL Bing Search, set BING_SEARCH_API_KEY environment variable.")
    print()
