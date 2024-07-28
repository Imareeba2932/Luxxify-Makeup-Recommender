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



from Connection_Pool import ResourceManager

MAX_CONCURRENT_REQUESTS = 8
#semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# Determine number of CPUs
num_cpus = multiprocessing.cpu_count()

chrome_path = '/usr/bin/google-chrome'# Replace with your actual path
chromedriver_path = '/usr/local/bin/chromedriver'  # Adjust as necessary
#logging.basicConfig(level=logging.INFO)


options = Options() #webdriver.ChromeOptions()
options.binary_location = chrome_path


options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

rm = ResourceManager(max_threads=MAX_CONCURRENT_REQUESTS)
n= 0
pagination = []

def get_product_links():
    # Write your query
    query = "SELECT * FROM product_links;"
    with rm.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows

async def get_product_reviews(product_link, product_link_id):
    async with rm.async_scoped_driver() as driver:
        reviews = []
        next_url = None
        try:
            driver.get(product_link)
        except Exception as e:
            print(e)
            return (None, product_link_id, next_url)
        print("Starting")
        # Wait for the section to be visible (adjust timeout as needed)
        found_reviews = await slow_scroll(driver)
        if not found_reviews:
             return (None, product_link_id, next_url)
        time.sleep(2)
        xhr_links = await extract_xhr_url(driver) #get first page
        print("XHR", len(xhr_links))
        #Adding Reviews to Product JSON
        for x in xhr_links:
            if 'display.powerreviews.com' in x:
                async with aiohttp.ClientSession() as session:
                    async with session.get(x) as response:
                        soup = BeautifulSoup(await response.text(), "html.parser")
                        reviews.append(soup.prettify())
        #next_url = await get_next_review_page(driver)
        print("Finished")
        return (reviews, product_link_id, next_url)

def insert_table(product_reviews, product_id, page):
    query = """
    INSERT INTO product_reviews (product_link_id, reviews, page) 
    VALUES (%s, %s, %s);
    """

    # Convert product_reviews to JSONB format
    values = (product_id, json.dumps(product_reviews), page)
    rm.execute_query(query, values)

    print(f'Inserted reviews for product_id: {product_id}, page: {page}')

async def get_all_product_reviews(products):
    async with aiohttp.ClientSession() as session:
        # Create a list of tasks for get_product_links
        tasks = [get_product_reviews(product[1],product[0]) for product in products]
        # Gather results from all tasks
        return await asyncio.gather(*tasks)

'''
async def get_product_reviews(product_link):
    async with rm.scoped_driver() as driver:
        # Initialize the WebDriver
        driver.get(product_link)
        reviews = {}
        xhr_links = [] #stores the specific xhr links needed
        reviews = []
        
        # Wait for the section to be visible (adjust timeout as needed)
        section_id = "reviews"
        await slow_scroll(height)
        section_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, section_id))
        )
        height = section_element.location['y']
        time.sleep(2)
        await extract_xhr_url() #get first page

        pg_count = 1
        while await click_next_review_page() and pg_count < 2:
            pg_count += 1
            time.sleep(2)  # Wait for new content to load
            await slow_scroll(height)
            await extract_xhr_url(driver, xhr_links)       
        
        #Adding Reviews to Product JSON
        for x in xhr_links:
            if 'display.powerreviews.com' in x:
                async with aiohttp.ClientSession() as session:
                    async with session.get(x) as response:
                        soup = BeautifulSoup(await response.text(), "html.parser")
                        reviews.append(soup.prettify()) 
        return reviews
'''
# Define a function to gradually scroll through the entire page
async def slow_scroll(driver):
    #scroll_height = driver.execute_script('return document.body.scrollHeight')
    current_position = 0
    found_reviews = False
    i = 0
    height = -1
    while not found_reviews and i < 100:
        driver.execute_script('window.scrollTo(0, {});'.format(current_position))
        current_position += 100  # Adjust scrolling speed by changing increment
        i += 1
        try:
            section_id = "reviews"
            loop = asyncio.get_event_loop()
            section_element = await loop.run_in_executor(None, lambda: WebDriverWait(driver, 0.2).until(
                EC.visibility_of_element_located((By.ID, section_id))
            ))
            height = section_element.location['y']
        except Exception as e:
            continue
        found_reviews = True
    if found_reviews:
        scroll_height = driver.execute_script('return document.body.scrollHeight')
        current_position = height
        while current_position < scroll_height:
            driver.execute_script('window.scrollTo(0, {});'.format(current_position))
            current_position += 100  # Adjust scrolling speed by changing increment
            time.sleep(0.2)  # Adjust sleep time to control scrolling speed
    return found_reviews
    

# Function to click the "Next" link
async def get_next_review_page(driver):
    try:
        loop = asyncio.get_event_loop()
        next_page_link = await loop.run_in_executor(None, lambda: WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'pr-rd-pagination-btn--next'))
        ))
        next_href = next_page_link.get_attribute('href')
        return next_href
    except NoSuchElementException:
        return None

# Function to extract the XHR URL
async def extract_xhr_url(driver):
    xhr_links = []
    for request in driver.requests: 
        xhr_links.append(request.url)
    return xhr_links

results = get_product_links()
results_as_list = [list(row) for row in results]
next_page = []

# Convert to a list of lists if needed
for row in results_as_list: 
    url = row[1]
    id = row[0]
    print(url, id)
    break

full_product_list = results_as_list
product_map = {row[0]:row[1] for row in full_product_list}

def make_product_list(old_product_list, page):
    new_product_list = []
    for row in old_product_list:
        new_url = product_map[row[0]] + f'&pr_rd_page={page+1}'
        new_product_list.append([row[0],  new_url])
    return new_product_list

def chonk_list(lst, chonk_size=8):
    chonks = []
    for i in range(0, len(lst), chonk_size):
        chonks.append(lst[i:i + chonk_size])
    return chonks

# Example usage
#my_list = list(range(20))  # Sample list with 20 elements
for product_list in tqdm(chonk_list(full_product_list)[2:]):
    for page in range(1,6):
        reviews = asyncio.run(get_all_product_reviews(product_list))
        new_product_list = []
        for product_review, product_id, next_url in reviews:
            if product_review is None: continue
            insert_table(product_review, product_id, page)
        product_list = make_product_list(product_list, page)
#for _ in range(5): 
#    for row in results_as_list: 
#        url = row[1]
#        id = row[0]
#        reviews = asyncio.run(get_all_product_reviews())
#        #some sort of array to equal the 
#        #get the first reviews json and insert

