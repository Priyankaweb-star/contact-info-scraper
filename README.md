# 🔍 Contact Info Scraper & Web Crawler

This Python tool performs intelligent web crawling and contact extraction. Starting from DuckDuckGo search results, it scrapes websites and uses NLP (spaCy) to extract:

- Person names
- Organizations
- Email addresses
- Phone numbers

All results are deduplicated and exported to an Excel file.

---

## 🚀 Features

- 🌐 DuckDuckGo-based keyword and location search
- 🔗 Crawls internal links of each domain
- 🧠 Uses spaCy for named entity recognition (names, orgs)
- 📬 Extracts emails and Indian phone numbers
- 🧹 Deduplicates results
- 📊 Exports to Excel

---

## 🧰 Tech Stack

- Python 3
- `requests` and `BeautifulSoup` (web scraping)
- `duckduckgo_search` (for initial URL discovery)
- `spaCy` (`en_core_web_sm` model)
- `pandas` (for data storage/export)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/contact-info-scraper.git
cd contact-info-scraper
pip install -r requirements.txt
python -m spacy download en_core_web_sm
