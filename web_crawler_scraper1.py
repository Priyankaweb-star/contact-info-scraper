import requests
from bs4 import BeautifulSoup
import re
import spacy
import pandas as pd
from urllib.parse import urljoin, urlparse
import time
from duckduckgo_search import DDGS

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Constants
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"(?:(?:\+|00)?91[\s\-]?)?[6-9]\d{9}"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

visited_links = set()

def search_urls(keyword, country, max_results=50):
    """Search DuckDuckGo for URLs"""
    query = f"{keyword} {country}"
    urls = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            urls.append(r['href'])
    return urls

def get_links(base_url, max_pages=10):
    """Extract internal links from a base URL"""
    links = set()
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        domain = urlparse(base_url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = urljoin(base_url, a_tag['href'])
            if domain in href and href not in visited_links:
                links.add(href)
                visited_links.add(href)
                if len(links) >= max_pages:
                    break
    except Exception as e:
        print(f"Error getting links from {base_url}: {e}")
    return list(links)

def extract_entities(text):
    """Use spaCy to extract names and organizations"""
    doc = nlp(text)
    names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
    return names, orgs

def scrape_page(url):
    """Extract relevant data from a page"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        emails = list(set(re.findall(EMAIL_REGEX, text)))
        phones = list(set(re.findall(PHONE_REGEX, text)))

        names, orgs = extract_entities(text)

        return {
            "url": url,
            "names": names,
            "orgs": orgs,
            "emails": emails,
            "phones": phones
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def crawl_and_scrape(start_urls, max_pages=10):
    """Crawl and extract data from all URLs"""
    results = []

    for base_url in start_urls:
        print(f"\nCrawling: {base_url}")
        pages = get_links(base_url, max_pages=max_pages)
        pages.insert(0, base_url)  # Include main URL
        for page in pages:
            print(f"  → Scraping: {page}")
            data = scrape_page(page)
            if data:
                for i in range(max(len(data["names"]), 1)):
                    name = data["names"][i] if i < len(data["names"]) else None
                    company = data["orgs"][0] if data["orgs"] else None
                    results.append({
                        "Person Name": name,
                        "Designation": None,  # Placeholder
                        "Company": company,
                        "Email(s)": ", ".join(data["emails"]) if data["emails"] else None,
                        "Phone(s)": ", ".join(data["phones"]) if data["phones"] else None,
                        "Source URL": data["url"]
                    })
            time.sleep(1)  # Be polite
    return results

def deduplicate(results):
    """Remove duplicate records"""
    seen = set()
    unique = []
    for item in results:
        key = (item['Email(s)'], item['Phone(s)'])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def save_to_excel(data, filename="output427.xlsx"):
    """Save final results to Excel"""
    if not data or not isinstance(data, list):
        print("\n⚠️ No data to save. Skipping Excel export.")
        return
    df = pd.DataFrame(data)
    df.fillna("None", inplace=True)
    try:
        df.to_excel(filename, index=False)
        print(f"\n✅ Saved {len(data)} records to {filename}")
    except PermissionError:
        print(f"\n❌ Permission denied: {filename} might be open. Please close it and try again.")


def main():
    # Step 1: Ask user for input
    keyword = input("Enter keyword (e.g., cardiologist): ").strip()
    country = input("Enter country (e.g., India): ").strip()

    # Step 2: Search URLs
    print(f"\n🔍 Searching DuckDuckGo for: '{keyword} {country}' ...")
    urls = search_urls(keyword, country, max_results=50)
    if not urls:
        print("No URLs found.")
        return

    # Step 3: Crawl and extract
    print(f"🔗 Found {len(urls)} URLs. Starting crawl...")
    scraped_data = crawl_and_scrape(urls, max_pages=10)

    # Step 4: Deduplicate and save
    deduped_data = deduplicate(scraped_data)
    print(f"Number of deduplicated records: {len(deduped_data)}")
    print(f"Type of deduped_data: {type(deduped_data)}")
    print(f"Sample data: {deduped_data[:1]}")
    save_to_excel(deduped_data)


if __name__ == "__main__":
    main()
