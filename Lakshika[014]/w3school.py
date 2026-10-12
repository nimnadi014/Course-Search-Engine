import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# -------------------- NLTK SETUP --------------------
nltk.download('punkt')
nltk.download('stopwords')

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

# -------------------- GLOBAL VARIABLES --------------------
visited_links = set()
url_to_doc_id = {}
SAVE_DIRECTORY = "C:\\Users\\hamdh\\Desktop\\web_CRAWLER\\skillshare_pages"

# -------------------- HELPER FUNCTIONS --------------------
def store_page(text, doc_id):
    """Save page content as a TXT file (not HTML)."""
    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)
    file_path = os.path.join(SAVE_DIRECTORY, f"doc_{doc_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

def is_valid_url(url, start_url):
    """Check if URL belongs to the same domain."""
    # Only stay within W3Schools domain
    return urlparse(url).netloc == urlparse(start_url).netloc

def normalize(text):
    """Tokenization + lowercase + stemming + stopword removal."""
    tokens = word_tokenize(text)
    normalized_tokens = [
        stemmer.stem(token.lower())
        for token in tokens
        if token.isalpha() and token.lower() not in stop_words
    ]
    return normalized_tokens

def create_inverted_index(folder_path):
    """Build an inverted index from stored TXT documents."""
    inverted_index = defaultdict(list)
    for file_name in os.listdir(folder_path):
        if file_name.startswith("doc_") and file_name.endswith(".txt"):
            doc_id = int(file_name.replace("doc_", "").replace(".txt", ""))
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                tokens = normalize(text)
                for token in set(tokens):
                    inverted_index[token].append(doc_id)
    return inverted_index

def save_index(index, output_file):
    """Save inverted index as JSON."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

# -------------------- WEB CRAWLER --------------------
def web_crawl(seed_url, max_links=1000, crawl_delay=1, retry_delay=3):
    """Crawl W3Schools starting from the Python seed page."""
    url_queue = [seed_url]
    doc_id = 1

    while url_queue and doc_id <= max_links:
        current_url = url_queue.pop(0)

        if current_url in visited_links:
            continue

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract visible text
            text_content = soup.get_text(separator=" ", strip=True)
            store_page(text_content, doc_id)

            visited_links.add(current_url)
            url_to_doc_id[current_url] = doc_id
            print(f"[{doc_id}] Crawled: {current_url}")
            doc_id += 1

            # Extract all valid links
            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link['href'])
                if is_valid_url(full_url, seed_url) and full_url not in visited_links and full_url not in url_queue:
                    # Only follow Python and related pages
                    if "/python" in full_url or "/python3" in full_url:
                        url_queue.append(full_url)

            time.sleep(crawl_delay)

        except requests.RequestException as e:
            print(f"Error crawling {current_url}: {e}")
            time.sleep(retry_delay)

    # Save URL → document ID mapping
    mapping_file = os.path.join(SAVE_DIRECTORY, "url_mapping.json")
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(url_to_doc_id, f, indent=2)

# -------------------- MAIN EXECUTION --------------------
if __name__ == "__main__":
    SEED_PAGE = "https://www.w3schools.com/python/"
    web_crawl(SEED_PAGE, max_links=1000, crawl_delay=1, retry_delay=3)

    inverted_index = create_inverted_index(SAVE_DIRECTORY)
    save_index(inverted_index, "w3school_python_inverted_index.json")

    print("Crawling and indexing completed successfully.")
