import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import urllib.parse


def parse_ausbildung(city: str = 'Freiburg', max_results: int = 20) -> List[Dict]:
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
        # Saving HTML for debugging
        debug_filename = f"debug_{city}.html"
        try:
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"💾 HTML saved in {debug_filename}")
        except Exception as e:
            print(f'⚠️ Failed to save debug file:{e}')
        # Search links for job opennings
        """The code finds all links (<a>) on the page that have the following in their address:/stellen/(second part is filter for href)"""
        job_links = soup.find_all(
            'a', href=lambda href: href and '/stellen/' in href)
        # Checking search result
        print(f"📦 Number of links on job openings found:{len(job_links)}")
        # If there are no job openings (empty list),pop up typs for debug
        if len(job_links) == 0:
            print('⚠️ No job openings found. Possible reasons:'
                  '1.False URL for search'
                  '2.Website changed his struktur'
                  '3.There are no job opening for {city}'
                  '4.Check please a file{debug_filename}')
        # Dublicates avoiding
        jobs = []
        processed_urls = set()
        # Link processing cycle
        for link in job_links:
            href = link.get('href', '')
            # If a link is already processed -> skip and move on to the next iteration of the loop(Dublicates avoiding)
            if href in processed_urls:
                continue
            processed_urls.add(href)

        try:
            # Search elems inside job openings card

            # Job title(required field)
            # Search for h3 elem with atributte:data-testid="jp-title"
            title_elem = link.find('h3', {'data-testid': 'jp-title'})
            if not title_elem:
                # Alternative search by class
                title_elem = link.find(
                    'h3', class_=lambda c: c and 'jpTitle' in c)

            # If there are no title - skip job opening
            if not title_elem:
                continue

            title = title_elem.text.strip()
            """
                title_elem -> object BeautifulSoup
                .text -> extracts text
                .strip -> removes spaces on the edges
            """
            # Company search(optional field)
            company_elem = link.find('h4', {'data-testid': 'jp-customer'})
            if company_elem:
                company = company_elem.text.strip()
                # Remove 'bei' at the begining
                if company.startswith('bei'):
                    # Prunning(cut off)
                    company = company[4:]
            else:
                company = 'Keine Angabe'
            # City/Location(optinal field)
            location_elem = link.find('span', {'data-testid': 'jp-customer'})
            if location_elem:
                # Extracting text
                location = location_elem.text.strip()
            else:
                location = city
            # Start date (optinal field)
            start_date_elem = link.find(
                'span', {'data-testid': 'jp-starting-at'})
            if start_date_elem:
                start_date = start_date_elem.text.strip()
            else:
                start_date = 'Nicht angegeben'
            # Number of available seats (optional field)
            vacancies_elem = link.find(
                'span', {'data-testid': 'jp-starting-at'})
            if vacancies_elem:
                vacancies = vacancies_elem.text.strip()
            else:
                vacancies = 'Nicht angegeben '
            # Forming a full link(3 different forms of link)
            # 1. Absolut link(full)
            if href.startswith('http'):
                full_url = href
            # 2. Relative link (starts with /)
            elif href.startswith('/'):
                full_url = f'{base_url}{href}'
            # 3. Relativ link (without /)
            else:
                full_url = f'{base_url}/{href}'
            """What for ?:Different websites use different link formats. The parser should handle all cases"""
            # Creating dict with job opennings data
            job = {
                'title': title,
                'company': company,
                'location': location,
                'start_date': start_date,
                'vacancies': vacancies,
                'url': full_url
            }
            jobs.append(job)
            # Pop up the progress
            print(f'✅ {len(jobs)}. {title[:60]}{'...' if len(title) > 60 else ''}-{company}')
            # Limiting the number of results
            if len(jobs) >= max_results:
                print(f'⚠️ Reached the limit of {max_results} job openings')
                break
            """ What for?: Don't parse more job listings than necessary -> saves time."""