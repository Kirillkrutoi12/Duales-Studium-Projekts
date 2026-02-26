"""
Data management for the bot 
Loads job listenings from parser or cache
"""

from database.parser_ausbildung import parse_ausbildung_de
from typing import Dict,List

#Cache for saving results
_jobs_cache = {}

def get_jobs_for_city(city:str , use_cache: bool = True)->List[Dict]:
    """
    Get job listings for a city (with caching)
    
    Args:
        city: City name
        use_cache: Use cached data if available
    
    Returns:
        List of job listings
    """
    #Cache controll
    if use_cache and city in _jobs_cache:
        print(f"📦 Using cache for {city}")
        return _jobs_cache[city]
    #Parse fresh data
    print(f'🔄 Parsing fresh data for {city}...')
    jobs=parse_ausbildung_de(city, max_results=10)
    _jobs_cache[city]=jobs

    return jobs