"""
Zhipu AI Web Search API implementation for news retrieval.
Supports structured news search using Zhipu's web_search API.
"""
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


def _format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results into a readable string.
    
    Args:
        results: List of search result objects or dictionaries from Zhipu API
        
    Returns:
        str: Formatted search results
    """
    if not results:
        return "No search results found."
    
    formatted_output = []
    for idx, result in enumerate(results, 1):
        # Handle both object attributes and dictionary keys
        if hasattr(result, 'title'):
            # Object attributes
            title = result.title or "No title"
            url = result.link or ""
            summary = result.content or ""
            publish_date = result.publish_date or ""
            website = result.media or ""
        else:
            # Dictionary keys
            title = result.get("title", "No title")
            url = result.get("link", result.get("url", ""))
            summary = result.get("content", result.get("describe", ""))
            publish_date = result.get("publish_date", "")
            website = result.get("media", result.get("website_name", ""))
        
        # Format the result entry
        item = f"[{idx}] {title}"
        if website:
            item += f" ({website})"
        formatted_output.append(item)
        
        # Add summary (truncate to 200 chars)
        if summary:
            # Clean up the summary - remove excessive whitespace
            clean_summary = " ".join(summary.split()[:50])  # Limit to first 50 words
            formatted_output.append(f"    摘要: {clean_summary}...")
        
        # Add link
        if url:
            formatted_output.append(f"    链接: {url}")
        
        # Add publish date
        if publish_date:
            formatted_output.append(f"    发布时间: {publish_date}")
        
        formatted_output.append("")
    
    return "\n".join(formatted_output)


def get_global_news_zhipu(curr_date: str, look_back_days: int = 7, limit: int = 5) -> str:
    """
    Retrieve global macroeconomic news using Zhipu Web Search API.
    
    This function uses Zhipu's web_search API to search for global or macroeconomic news
    that would be informative for trading purposes. It searches for news published within
    the specified time range.
    
    Args:
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): Number of days to look back (default 7)
        limit (int): Maximum number of articles to return (default 5)
        
    Returns:
        str: Formatted string containing global news data with titles, summaries, links, and dates
        
    Example:
        >>> news = get_global_news_zhipu("2025-10-22", look_back_days=7, limit=5)
        >>> print(news)
    """
    try:
        from zai import ZhipuAiClient
    except ImportError:
        raise ImportError(
            "zai-sdk not installed. Please install it with: pip install zai-sdk"
        )
    
    # Get API key from environment variable only
    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError(
            "Zhipu API key not found. "
            "Please set the 'ZHIPU_API_KEY' environment variable."
        )
    
    # Initialize Zhipu client
    client = ZhipuAiClient(api_key=api_key)
    
    # Parse dates for search query
    try:
        curr_date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format. Expected yyyy-mm-dd, got {curr_date}")
    
    start_date_obj = curr_date_obj - timedelta(days=look_back_days)
    
    # Create search query for macroeconomic news
    search_query = (
        f"Can you search global or macroeconomics news from {look_back_days} days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period. Limit the results to {limit} articles.Can you search global or macroeconomics news from {look_back_days} days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period. Limit the results to {limit} articles."
        #f"from {start_date_obj.strftime('%Y-%m-%d')} to {curr_date}"
    )
    
    # Make Web Search API call
    response = client.web_search.web_search(
        search_engine="search_std",  # Use high-precision search engine
        search_query=search_query,
        count=min(limit, 50),  # API supports max 50 results
        search_recency_filter="noLimit",  # No specific recency filter needed, query contains dates
        content_size="high"  # Get detailed summaries
    )
    
    # Extract and format results
    # According to Zhipu API docs, response has 'search_result' field
    if hasattr(response, 'search_result') and response.search_result:
        results = response.search_result
    elif isinstance(response, dict) and 'search_result' in response:
        results = response['search_result']
    elif isinstance(response, list):
        # Fallback: if response is directly a list
        results = response
    else:
        # If response format doesn't match expected patterns, return empty list
        results = []
    
    # Format and return results
    formatted = _format_search_results(results)
    
    # Add metadata
    header = f"=== Global News (Last {look_back_days} days as of {curr_date}) ===\n"
    footer = f"\nTotal results: {len(results)}"
    
    return header + formatted + footer


def get_stock_news_zhipu(query: str, start_date: str, end_date: str) -> str:
    """
    Retrieve company-specific news using Zhipu Web Search API.
    
    This function searches for news related to a specific company or ticker symbol
    within a specified date range.
    
    Args:
        query (str): Search query (e.g., company name or ticker)
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
        
    Returns:
        str: Formatted string containing news data
        
    Example:
        >>> news = get_stock_news_zhipu("Tesla TSLA", "2025-10-15", "2025-10-22")
        >>> print(news)
    """
    try:
        from zai import ZhipuAiClient
    except ImportError:
        raise ImportError(
            "zai-sdk not installed. Please install it with: pip install zai-sdk"
        )
    
    # Get API key from environment variable only
    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError(
            "Zhipu API key not found. "
            "Please set the 'ZHIPU_API_KEY' environment variable."
        )
    
    # Initialize Zhipu client
    client = ZhipuAiClient(api_key=api_key)
    
    # Make Web Search API call
    response = client.web_search.web_search(
        search_engine="search_pro",
        search_query=f"{query} news from {start_date} to {end_date}",
        count=10,
        search_recency_filter="noLimit",
        content_size="high"
    )
    
    # Extract and format results
    # According to Zhipu API docs, response has 'search_result' field
    if hasattr(response, 'search_result') and response.search_result:
        results = response.search_result
    elif isinstance(response, dict) and 'search_result' in response:
        results = response['search_result']
    elif isinstance(response, list):
        # Fallback: if response is directly a list
        results = response
    else:
        # If response format doesn't match expected patterns, return empty list
        results = []
    
    # Format and return results
    formatted = _format_search_results(results)
    
    # Add metadata
    header = f"=== News for '{query}' ({start_date} to {end_date}) ===\n"
    footer = f"\nTotal results: {len(results)}"
    
    return header + formatted + footer


def get_fundamentals_zhipu(ticker: str, curr_date: str) -> str:
    """
    Retrieve fundamental analysis data using Zhipu Web Search API.
    
    This function searches for fundamental information about a company including
    PE ratio, PS ratio, cash flow, and other financial metrics.
    
    Args:
        ticker (str): Stock ticker symbol
        curr_date (str): Current date in yyyy-mm-dd format
        
    Returns:
        str: Formatted string containing fundamental analysis data
        
    Example:
        >>> fundamentals = get_fundamentals_zhipu("TSLA", "2025-10-22")
        >>> print(fundamentals)
    """
    try:
        from zai import ZhipuAiClient
    except ImportError:
        raise ImportError(
            "zai-sdk not installed. Please install it with: pip install zai-sdk"
        )
    
    # Get API key from environment variable only
    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        raise ValueError(
            "Zhipu API key not found. "
            "Please set the 'ZHIPU_API_KEY' environment variable."
        )
    
    # Initialize Zhipu client
    client = ZhipuAiClient(api_key=api_key)
    
    # Parse date to get month range
    try:
        curr_date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format. Expected yyyy-mm-dd, got {curr_date}")
    
    # Get previous month
    first_day_of_curr_month = curr_date_obj.replace(day=1)
    last_day_of_prev_month = first_day_of_curr_month - timedelta(days=1)
    first_day_of_prev_month = last_day_of_prev_month.replace(day=1)
    
    # Make Web Search API call
    response = client.web_search.web_search(
        search_engine="search_pro",
        search_query=(
            f"{ticker} fundamental analysis PE PS cash flow earnings "
            f"from {first_day_of_prev_month.strftime('%Y-%m-%d')} "
            f"to {curr_date}"
        ),
        count=15,
        search_recency_filter="noLimit",
        content_size="high"
    )
    
    # Extract and format results
    # According to Zhipu API docs, response has 'search_result' field
    if hasattr(response, 'search_result') and response.search_result:
        results = response.search_result
    elif isinstance(response, dict) and 'search_result' in response:
        results = response['search_result']
    elif isinstance(response, list):
        # Fallback: if response is directly a list
        results = response
    else:
        # If response format doesn't match expected patterns, return empty list
        results = []
    
    # Format and return results
    formatted = _format_search_results(results)
    
    # Add metadata
    header = f"=== Fundamental Analysis for {ticker} (as of {curr_date}) ===\n"
    footer = f"\nTotal results: {len(results)}"
    
    return header + formatted + footer
