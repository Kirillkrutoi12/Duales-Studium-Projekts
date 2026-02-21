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
        # User-Agent - "identifies as" by the Chrome browser on Windows
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Accept - says: "I accept HTML pages"
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # Accept-Language -I understand German and English
        'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        # Referer-"I came from the main page of ausbildung.de" (doesn't raise suspicion)
        'Referer': 'https://www.ausbildung.de/',
    }
    try:
        print(f"We're parsing job openings in {city}...")
        print(f"URL: {search_url}")
        # Sending an HTTP request
        response = requests.get(search_url, headers=headers, timeout=15)
        # What happens:
        # 1.Python sends an HTTP GET request to 'search_url'
        # 2.Sends 'headers' (pretending to be a browser
        # 3.Waits for a response for up to 15 seconds ('timeout=15')
        # 4.The server returns an HTML page → it is saved in 'response'(in variable)
        print(f"Status Code: {response.status_code}")
        # Check if the request was succesfull(status_code -> f.e: 200 means a page has been downloaded without trubles)
        if response.status_code != 200:
            print(f"❌ Error: status received {response.status_code}")
            if response.status_code == 403:
                print("⚠️ The site may have blocked the request. Please try again later")
            elif response.status_code == 404:
                print("⚠️ Page not found. Check the URL")
            return []
        # Parcing HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        """ 
        Params:
          response.content - HTML website's code
          'html.parser' - Parcer for HTML
        """
        #Saving HTML for debugging
        debug_filename = f"debug_{city}.html"
        try:
            with open (debug_filename,'w',encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"💾 HTML saved in {debug_filename}")
        except Exception as e:
            print(f'⚠️ Failed to save debug file:{e}')
        
