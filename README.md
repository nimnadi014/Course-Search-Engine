# Course Search Engine

## Project Overview

An Integrated Information Retrieval System that searches educational course pages collected from W3Schools, Udemy, and Coursera.

## Technologies Used

* Python
* Streamlit
* NLTK
* BeautifulSoup
* Selenium
* Requests

## Information Retrieval Models

* Vector Space Model (VSM)
* Query Likelihood Model (QLM)

## Main Features

* Web crawling and text extraction
* Text preprocessing using tokenization, stopword removal, and stemming
* Inverted index integration
* Ranked search results using VSM and QLM
* Links to original course pages

## How to Run

1. Install Python.

2. Install the required packages:

   `pip install -r requirements.txt`

3. Run the application:

   `streamlit run app.py`

## Project Note

The crawler data folders must be configured correctly before searching. Some crawler websites may restrict automated access.
