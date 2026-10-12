# -------------------- IMPORTS --------------------
import os
import time
import json
from collections import defaultdict
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# -------------------- NLTK SETUP --------------------
nltk.download('punkt')
nltk.download('stopwords')

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

# -------------------- GLOBALS --------------------
visited_links = set()
save_directory =  "C:\\Users\\hamdh\\Desktop\\web_CRAWLER\\coursera_pages"

url_to_doc_id = {}

# -------------------- SELENIUM DRIVER --------------------
def init_driver():
    """Initialize Selenium Chrome driver using Selenium Manager."""
    options = Options()
    options.add_argument("--headless")  # run Chrome in the background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)  # Selenium Manager auto-downloads driver
    return driver

# -------------------- WEB CRAWLER --------------------
def web_crawl(start_url, driver, max_links=500, crawl_delay=3, retry_delay=5):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    url_queue = [start_url]
    link_count = 0

    while url_queue and link_count < max_links:
        current_url = url_queue.pop(0)

        if current_url not in visited_links:
            try:
                driver.get(current_url)
                time.sleep(2)  # wait for page to load fully

                page_source = driver.page_source

                # Assign document ID
                doc_id = link_count + 1
                url_to_doc_id[current_url] = doc_id

                # Store page text
                store_page(current_url, page_source, save_directory, doc_id)

                visited_links.add(current_url)
                link_count += 1
                print(f"Link {link_count}: {current_url} crawled successfully.")

                # Extract all valid links
                soup = BeautifulSoup(page_source, 'html.parser')
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(current_url, link['href'])
                    if is_valid_url(full_url, start_url) and full_url not in visited_links:
                        url_queue.append(full_url)

                time.sleep(crawl_delay)

            except WebDriverException as e:
                print(f"Failed to crawl {current_url}: {e}")
                print(f"Retrying after {retry_delay} seconds...")
                time.sleep(retry_delay)

    # Save URL → document ID mapping
    mapping_file = os.path.join(save_directory, "url_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(url_to_doc_id, f, indent=2)

# -------------------- STORE PAGE --------------------
def store_page(url, html_content, save_directory, doc_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True)

    file_name = f"doc_{doc_id}.txt"
    file_path = os.path.join(save_directory, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_content)

# -------------------- URL VALIDATION --------------------
def is_valid_url(url, start_url):
    return urlparse(url).netloc == urlparse(start_url).netloc

# -------------------- TEXT NORMALIZATION --------------------
def normalize(text):
    tokens = word_tokenize(text)
    normalized_tokens = [
        stemmer.stem(token.lower())
        for token in tokens
        if token.isalpha() and token.lower() not in stop_words
    ]
    return normalized_tokens

# -------------------- INVERTED INDEX --------------------
def create_inverted_index(folder_path):
    inverted_index = defaultdict(list)
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt") and file_name.startswith("doc_"):
            file_path = os.path.join(folder_path, file_name)
            doc_id = int(file_name.replace("doc_", "").replace(".txt", ""))
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                tokens = normalize(text)
                for token in set(tokens):
                    inverted_index[token].append(doc_id)
    return inverted_index

def save_index(inverted_index, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=2)

# -------------------- MAIN --------------------
if __name__ == "__main__":
    driver = init_driver()
    try:
        start_page = "https://www.coursera.org/browse/development"
       # web_crawl(start_page, driver, max_links=500, crawl_delay=3, retry_delay=5)
    finally:
        driver.quit()  # ensure driver closes

    inverted_index = create_inverted_index(save_directory)
    output_file = "coursera_inverted_index.json"
    save_index(inverted_index, output_file)
    print(f"Inverted index saved to {output_file}")
