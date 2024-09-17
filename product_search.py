import streamlit as st
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from ortools.linear_solver import pywraplp
import gdown
import os
import requests
from googlesearch import search
#from duckduckgo_search import DDGS
import webbrowser
import traceback
import streamlit.components.v1 as components
import traceback
import requests
from bs4 import BeautifulSoup
import time
import random

# List of User-Agent strings to simulate different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
]


def import_data(): 
    product_info = pd.read_csv('cleaned_makeup_products.csv')
    return product_info

def google_search(product_name, product_details):
    query = product_name + ' '+ product_details  
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    search_url = f"https://duckduckgo.com/html/?q={query}"
    response = requests.get(search_url, headers=headers)

    # If the request is successful, parse the response
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all search results links
        results = soup.find_all('a', {'class': 'result__a'})
        
        # Return the first result link (or None if no results)
        if results:
            return results[0]['href']


def main(): 
    product_info = import_data()
    product_google_search  = pd.DataFrame(columns=['product_link_id', 'search_result'])
    #print(product_info.columns)
    for product in product_info:

        product_id = product['product_link_id']
        product_name = product['product_name']
        product_details = product['description']

        link = google_search(product_name, product_details)
        if link: 
            product_google_search['product_link_id'] = product_id
            product_google_search['search_result'] = link
            print('added to csv', product_id, product_name)
        time.sleep(random.uniform(120, 180)) 

main()