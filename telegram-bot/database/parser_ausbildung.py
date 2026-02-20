import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import urllib.parse


def parse_ausbildung(city: str = 'Freiburg', max_result: int = 20) -> List[Dict]:
    """
      Parses job listings from Ausbildung.de

      Args:
        city: city for searching(default:Freiburg)
        max_result: max amount of job listings(default:20)

      Returns:
        list of dicts with job listenings
    """
    # URL for searching
    base_url = "https://www.ausbildung.de"
    search_url = f"{base_url}/suche?q={urllib.parse.quote(city)}"
    # Headers ,to like like a browser
    headers = {
        #User-Agent - "identifies as" by the Chrome browser on Windows
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        #Accept - says: "I accept HTML pages"
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #Accept-Language -I understand German and English
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        #Referer-"I came from the main page of ausbildung.de" (doesn't raise suspicion)
        'Referer': 'https://www.ausbildung.de/',
    }
    
