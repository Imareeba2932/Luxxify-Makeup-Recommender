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

MAX_CONCURRENT_REQUESTS = 4
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

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
    

async def get_product_reviews(product_link):
    async with rm.scoped_driver() as driver:
        # Initialize the WebDriver
        driver.get(product_link)
        reviews = {}
        xhr_links = [] #stores the specific xhr links needed
        reviews = []
        
        # Wait for the section to be visible (adjust timeout as needed)
        section_id = "reviews"
        slow_scroll(height)
        section_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, section_id))
        )
        height = section_element.location['y']
        time.sleep(2)
        await extract_xhr_url()

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

# Define a function to gradually scroll through the entire page
async def slow_scroll(driver, start_position):
    scroll_height = driver.execute_script('return document.body.scrollHeight')
    current_position = start_position
    while current_position < scroll_height:
        driver.execute_script('window.scrollTo(0, {});'.format(current_position))
        current_position += 100  # Adjust scrolling speed by changing increment
        time.sleep(0.2)  # Adjust sleep time to control scrolling speed

# Function to click the "Next" link
async def click_next_review_page(driver):
    try:
        next_page_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'pr-rd-pagination-btn--next'))
        )
        try:
            next_page_link.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", next_page_link)
        return True
    except NoSuchElementException:
        return False

# Function to extract the XHR URL
async def extract_xhr_url(driver, xhr_links):
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

for _ in range(5): 
    for row in results_as_list: 
        url = row[1]
        id = row[0]
        reviews = asyncio.run(get_product_reviews())
        #some sort of array to equal the 
        #get the first reviews json and insert

