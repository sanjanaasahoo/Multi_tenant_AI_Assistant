"""
scripts/scrape_site.py
──────────────────────────────────────────────────────────────────────
Scrapes all public pages of a target website and saves each page's
cleaned text to a file.

Run this script ONCE (or whenever the website content updates):
    python scripts/scrape_site.py

Output:
    data/crushaders_tech/raw/home.txt
    data/crushaders_tech/raw/about.txt
    data/crushaders_tech/raw/service_seo.txt
    ... etc
──────────────────────────────────────────────────────────────────────
"""

import os
import time
import requests
from bs4 import BeautifulSoup

# ── Every page we want to scrape ──────────────────────────────────────
# Format: (filename_without_extension, url, page_type)
# page_type becomes a metadata field in Qdrant — used for filtering later
PAGES = [
    # Home page
    ("home",                 "https://crushaderstech.com/",                              "home"),

    # About
    ("about",                "https://crushaderstech.com/about",                         "about"),

    # Service pages
    ("service_content",      "https://crushaderstech.com/content-creation",              "service"),
    ("service_branding",     "https://crushaderstech.com/digital-branding",              "service"),
    ("service_ecommerce",    "https://crushaderstech.com/e-commerce-solutions",          "service"),
    ("service_lead_gen",     "https://crushaderstech.com/lead-generation",               "service"),
    ("service_celebrity",    "https://crushaderstech.com/celebrity-profile-management",  "service"),
    ("service_orm",          "https://crushaderstech.com/online-reputation-management",  "service"),
    ("service_political",    "https://crushaderstech.com/political-campaign-management", "service"),

    # Industry pages
    ("industry_education",   "https://crushaderstech.com/education",                    "industry"),
    ("industry_realestate",  "https://crushaderstech.com/real-estate",                  "industry"),
    ("industry_healthcare",  "https://crushaderstech.com/healthcare",                   "industry"),
    ("industry_hospitality", "https://crushaderstech.com/hospitality-tourism",          "industry"),
    ("industry_jewellery",   "https://crushaderstech.com/jewellery-watches",            "industry"),
    ("industry_manufact",    "https://crushaderstech.com/manufacturing",                "industry"),

    # Contact
    ("contact",              "https://crushaderstech.com/contacts",                     "contact"),

    # Blogs (grab the listing page — individual blogs optional)
    ("blogs",                "https://crushaderstech.com/blogs",                        "blog"),
]

WEBSITE_ID = "crushaders_tech"
OUTPUT_DIR = os.path.join("data", WEBSITE_ID, "raw")

# Browser-like headers — some sites block requests without a User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def extract_text(html: str) -> str:
    """
    Extract readable text from raw HTML.
    Removes: <nav>, <footer>, <header>, <script>, <style>, cookie banners.
    Keeps: main content text, headings, paragraphs.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove elements that contain no useful content
    for tag in soup(["nav", "footer", "header", "script",
                     "style", "noscript", "iframe", "form"]):
        tag.decompose()

    # Some sites wrap nav in these classes — remove them
    for cls in ["cookie-banner", "popup", "modal", "breadcrumb"]:
        for el in soup.find_all(class_=cls):
            el.decompose()

    # Get text with spaces between elements (separator=" ")
    # strip=True removes leading/trailing whitespace per element
    text = soup.get_text(separator=" ", strip=True)

    return text


def clean_text(text: str) -> str:
    """
    Remove excessive whitespace from extracted text.
    The raw extraction often has many consecutive spaces and newlines.
    """
    import re
    # Collapse multiple spaces into one
    text = re.sub(r" {2,}", " ", text)
    # Collapse more than 2 consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def scrape_page(url: str) -> str | None:
    """
    Fetch one URL, extract and clean its text.
    Returns None if the request fails.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()  # raises exception for 4xx/5xx status codes
        text = extract_text(response.text)
        text = clean_text(text)
        print(f"  ✓  {url}  ({len(text)} chars)")
        return text
    except requests.RequestException as e:
        print(f"  ✗  FAILED: {url}  →  {e}")
        return None


def save_text(filename: str, text: str) -> None:
    """Save text to a file, creating directories if needed."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    print(f"\n{'='*60}")
    print(f"  Scraping: {WEBSITE_ID}")
    print(f"  Output:   {OUTPUT_DIR}")
    print(f"  Pages:    {len(PAGES)}")
    print(f"{'='*60}\n")

    success = 0
    failed  = 0

    for filename, url, page_type in PAGES:
        text = scrape_page(url)
        if text:
            save_text(filename, text)
            success += 1
        else:
            failed += 1

        # Be polite — don't hammer the server
        # 1 second between requests is courteous scraping
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"  Done.  ✓ {success} saved   ✗ {failed} failed")
    print(f"  Files in: {OUTPUT_DIR}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()