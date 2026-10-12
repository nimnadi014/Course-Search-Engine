import os
import time
import requests
from bs4 import BeautifulSoup  #parsing html content
from urllib.parse import urlparse, urljoin
from collections import defaultdict
import json
import nltk   #natural language processing, including tokenization, stopwords, and stemming.
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


nltk.download('punkt')
#Punkt is a pre-trained tokenizer for sentence segmentation and word tokenization.
nltk.download('stopwords')
#stopwords are common words like the, and, is, in, etc., 
#that are usually removed during text processing because they do not carry much meaningful information. 



# initialize stemmer and stopwords
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))  #common english words to exclude during text analysis.


visited_links = set()             # already-visited URLs to avoid duplicate processing
save_directory = "D:\\Downloads\\web_CRAWLER\\downloaded_pages"
url_to_doc_id = {}  # mapping from URL to document ID

def web_crawl(start_url, max_links=500, crawl_delay=1, retry_delay=4, save_directory=save_directory):
    """Crawls web pages starting from a specified start URL up to a maximum number of links."""
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    url_queue = [start_url]
    link_count = 0

    while url_queue and link_count < max_links:
        current_url = url_queue.pop(0)  #order they were added to the queue
        
        if current_url not in visited_links:   #checks if the url has already been processed to avoid duplicate crawling. #request page content
            try:
                response = requests.get(current_url, timeout=10)     
                response.raise_for_status()

                # Assign document ID
                doc_id = link_count + 1
                url_to_doc_id[current_url] = doc_id

                # store the page content as txt in the specified directory
                store_page(current_url, response.text, save_directory, doc_id)

                visited_links.add(current_url)
                link_count += 1

                print(f"Link {link_count}: {current_url} crawled successfully.")

# parse page content and extract valid links
                page_content = BeautifulSoup(response.text, 'html.parser')
                for link in page_content.find_all('a', href=True):
                    full_url = urljoin(current_url, link['href'])

                    if is_valid_url(full_url, start_url) and full_url not in visited_links:
                        url_queue.append(full_url)

                time.sleep(crawl_delay)

            except requests.RequestException as error:
                print(f"Failed to crawl {current_url}: {error}")
                print(f"Pausing for {retry_delay} seconds before retrying.")
                time.sleep(retry_delay)

    # Save URL to document ID mapping
    mapping_file = os.path.join(save_directory, "url_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(url_to_doc_id, f, indent=2)

def store_page(url, html_content, save_directory, doc_id):
    """Storing crawled pages as text files."""
    # Extract text content from HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True)
    
    # Use document ID for file naming
    file_name = f"doc_{doc_id}.txt"
    file_path = os.path.join(save_directory, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text_content)

def is_valid_url(url, start_url):
    """checks if a  is within the same domain as the start URL."""
    return urlparse(url).netloc == urlparse(start_url).netloc

def normalize(text):
    """Normalizes text by tokenizing, converting to lowercase, removing punctuation, and stemming."""
    tokens = word_tokenize(text)

    normalized_tokens = [
        stemmer.stem(token.lower())
        for token in tokens
        if token.isalpha() and token.lower() not in stop_words
    ]

    return normalized_tokens

def create_inverted_index(folder_path):
    """Creates an inverted index from text files stored in a specified directory."""
    inverted_index = defaultdict(list)

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt") and file_name.startswith("doc_"):
            file_path = os.path.join(folder_path, file_name)
            
            # Extract document ID from filename
            doc_id = int(file_name.replace("doc_", "").replace(".txt", ""))

            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                tokens = normalize(text)
                
                # Populate inverted index with tokens and document IDs
                for token in set(tokens):  # use set tokens to avoid duplicate entries
                    inverted_index[token].append(doc_id)

    return inverted_index

def save_index(inverted_index, output_file):
    """Saves the inverted index as a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=2)

# main execution
if __name__ == "__main__":
    start_page = "https://www.udemy.com/courses/development"
    web_crawl(start_page, max_links=500, crawl_delay=1, retry_delay=3)

    # create the inverted index from saved txt files
    folder_path = save_directory
    inverted_index = create_inverted_index(folder_path)

    # save the json 
    output_file = 'inverted_index.json'
    save_index(inverted_index, output_file)

    print(f"Inverted index saved to {output_file}")
