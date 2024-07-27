import psycopg2
import requests
from bs4 import BeautifulSoup
import html_to_json
import json
import os
from jsonpath_ng import jsonpath, parse
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import sys
import multiprocessing
import aiohttp
import asyncio



from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
from tqdm.asyncio import tqdm  # Import tqdm for async
import logging

from Connection_Pool import ResourceManager
MAX_CONCURRENT_REQUESTS = 4
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

rm = ResourceManager(max_threads=MAX_CONCURRENT_REQUESTS)





def insert_table(product_details, product_id):
    query = """
    INSERT INTO product_details (details, product_link_id) 
    VALUES (%s, %s);
    """

    values = (json.dumps(product_details), product_id)
    rm.execute_query(query, values)
 
    print(f'Inserted link: {product_details['name']}')

def get_product_links():
    # Write your query
    query = "SELECT * FROM product_links;"
    with rm.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows



# Returns info such as ingredrients and product description
async def get_product_details(product_link):
    product_details = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(product_link) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            html_content = soup.find_all(class_='ProductHero__content')
            description = ''
            product_details['url'] = product_link
    
            def extract_text_fields(json_data):
                jsonpath_expression = parse('$.._value')
                matches = jsonpath_expression.find(json_data)
                return [match.value for match in matches]

            
            def html_to_text_json(html_content):
                """Convert HTML content to a nested JSON containing only text fields."""
                json_data = html_to_json.convert(html_content)
                text_fields = extract_text_fields(json_data)
                #print(json.dumps(json_data, indent=4))
                return text_fields

    # Convert HTML to text-only JSON
    text_json = html_to_text_json(str(html_content))
    
    # Print the JSON output
    #print(json.dumps(text_json, indent=4) )
    description = ' '.join(text_json)
    product_details['description'] = description
    #print(product_details)
    await get_spec_prod_details(product_link, product_details)
    return product_details



#<a class="pal-c-Link pal-c-Link--primary pal-c-Link--compact" href="https://www.ulta.com/brand/it-cosmetics" target="_self" iconsize="default">IT Cosmetics</a>

#Adds specific product fields to json (name, id, price)
async def get_spec_prod_details(product_link, product_details):
    async with aiohttp.ClientSession() as session:
        async with session.get(product_link) as response:
            #response.raise_for_status()
            soup = BeautifulSoup(await response.text(), "html.parser")
            price = soup.find_all(class_='ProductPricing')
            brand = soup.find_all(class_='pal-c-Link pal-c-Link--primary pal-c-Link--compact')
            name = soup.find_all(class_='Text-ds Text-ds--title-5 Text-ds--left Text-ds--black')
            id_num  = soup.find_all(class_ = 'Text-ds Text-ds--body-3 Text-ds--left Text-ds--neutral-600')

            product_price = "NA"
            product_name = "NA"
            product_id = "NA"
            product_brand = 'NA'
            
            if len(price) > 0:
                product_price = price[0].get_text()
            if len(name) > 0:
                product_name = name[0].get_text()
            if len(brand) > 8: 
                product_brand = brand[8].get_text()

            for id_content in id_num:
                line = id_content.find(class_='Text-ds Text-ds--body-3 Text-ds--left Text-ds--black')
                if line is not None:
                    product_id = line.get_text()
                    break

            product_details['price'] = product_price
            product_details['id'] = product_id
            product_details['brand'] = product_brand
            product_details['name'] = product_name
            #print(product_details)
'''
url = 'https://www.ulta.com/p/double-wear-stay-in-place-foundation-xlsImpprod14641507?sku=2309420'
asyncio.run( get_spec_prod_details(url) )
#asyncio.run( get_product_details(url) )
'''

# Store results in a variable

results = get_product_links()
results_as_list = [list(row) for row in results]


# Convert to a list of lists if needed
for row in tqdm(results_as_list): 
    url = row[-1]
    id = row[0]
    product_details = asyncio.run(get_product_details(url) )
    insert_table(product_details, id)

 
