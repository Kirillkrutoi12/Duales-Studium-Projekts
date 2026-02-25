import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import urllib.parse


def parse_ausbildung_de(city: str = 'Freiburg', max_results: int = 20) -> List[Dict]:
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
                location_elem = link.find('span', {'data-testid': 'jp-brances'})
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
                    'span', {'data-testid': 'jp-vacancies'})
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
                print(
                    f'✅ {len(jobs)}. {title[:60]}{'...' if len(title) > 60 else ''}-{company}')
                # Limiting the number of results
                if len(jobs) >= max_results:
                    print(f'⚠️ Reached the limit of {max_results} job openings')
                    break
                """ What for?: Don't parse more job listings than necessary -> saves time."""
            # Handling parcer errors(In the context of the parser: If one job listing is broken -> skip it, continue with the others)
                """AttributeError occurs when elemnt is not found | Attempt to access an attribute"""
            except AttributeError as e:
                print(f"⚠️ Error parsing job listing (element missing):{e}")
                continue
                """Exception catch all others errors(types of errors) """
            except Exception as e:
                print(f"⚠️ Unexpected error while parsing job opennings: {e}")
                continue

        # Final pop up
        print(f"\n✅ Total found: {len(jobs)} job opennings")
        return jobs
        # HTTP Exception Handling(From specific to general)
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: the server did not respond within 15 seconds")
        return []
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: failed to connect to {base_url}")
        print("Please check your internet conection")
        return []
        """RequestException -> Any other requests error"""
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during HTTP request: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error {e}")
        import traceback
        print(f"\n 📋 Complete traceback:")
        traceback.print_exc()  # Displays the full error stack
        return []


def parse_multiple_cities(cities: List[str], max_results: int = 10) -> Dict[str, List[Dict]]:
    """
        Parses job listings for multiple cities
        Args:
        cities (List[str]): List of cities
        max_results (int): Maximum number of job listings for each city
        Returns:
        Dict[str, List[Dict]]: Dictionary {city: list_of_jobs}
    """
    all_jobs = {}

    for i, city in enumerate(cities, 1):
        print(f"\n{'='*70}")
        print(f"📍 Parcing city {i}/{len(cities)}: {city}")
        print('='*70)  # A beautiful separator line.

        jobs = parse_ausbildung_de(city, max_results)
        all_jobs[city] = jobs
        # Pause between requests (important for following site rules)
        if i < len(cities):  # Don't make a pause after the last city (<)
            pause_seconds = 3
            print(
                f"⏳ Pause {pause_seconds} seconds before the next request...")
            # pauses the program's execution for a specific time
            time.sleep(pause_seconds)
    return all_jobs

def save_to_file(jobs: List[Dict], filename: str = 'jobs.txt'):
    """
        Saves job listings to a text file

        Args:
        jobs (List[Dict]): List of job listings(type hint)
        filename (str): Name of the file to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("FOUND VACANCIES AUSBILDUNG\n")
            f.write("=" * 80 + "\n\n")

        for i, job in enumerate(jobs, 1):
            f.write(f"{i}. {job['title']}\n")
            f.write(f" 🏢 Company: {job['company']}\n")
            f.write(f" 📍 Location: {job['location']}\n")
            f.write(f" 📅 Start: {job['start_date']}\n")
            f.write(f" 👥 Vacancies: {job['vacancies']}\n")
            f.write(f" 🔗 URL: {job['url']}\n")
            f.write("\n")
        print(f'💾 Results saved in file: {filename}')
    except Exception as e:
        print(f"❌ Error while saving a file: {e}")


def test_parser():
    """Test the parser with different scenarios"""
    print('=' * 70)
    print('🚀 TEST PARSER AUSBILDUNG.DE')
    print('=' * 70)

    # Test with city Freiburg
    jobs = parse_ausbildung_de('Freiburg', max_results=5)

    if jobs:
        print('\n' + "=" * 70)
        print("📋 RESULTS:")
        print("=" * 70)

    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   🏢 Company: {job['company']}")
        print(f"   📍 Location: {job['location']}")
        print(f"   📅 Start: {job['start_date']}")
        print(f"   👥 Vacancies: {job['vacancies']}")
        print(f"   🔗 URL: {job['url']}")

        save_to_file(jobs, "test_results_freiburg.txt")
    else:
        print("\n  No vacancies found!")
        print("\n  RECOMMENDATIONS:")
        print("1. Check debug_Freiburg.html file in browser")
        print("2. Open https://www.ausbildung.de and search manually")
        print("3. Copy the URL from address bar")
        print("4. Update search_url variable in parse_ausbildung_de()")


# Entry point
if __name__ == '__main__':
    test_parser()
