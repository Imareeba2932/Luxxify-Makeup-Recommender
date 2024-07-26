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

async def get_category(link):
    product_links = []
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            content = soup.find_all(class_='CategoryCard')
            

            for category_soup in content:
                product_link = get_product_links(category_soup)
                #product_links.extend(product_link)


  
            #tasks = [get_product(link) for link in product_links]
            #results = await asyncio.gather(*tasks)
            #return results

async def insert_table(product_link):

    query = "INSERT INTO product_links (data) VALUES ($1)"
    values = (product_link, ) 
    await rm.execute_query(query, *values)


def click_next_page(driver):
    try:
        next_page_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located ((By.CLASS_NAME, 'ProductListingWrapper__LoadContent' ))
        )
        next_page_link = next_page_link.find_element(By.TAG_NAME, 'a')
        next_page_href = next_page_link.get_attribute('href')
        return next_page_href
    except Exception:
        return False

def extract_links(driver): 
    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.find_all(class_='ProductCard')
    page_product_links = []
    for c in content:
        product = c.find('a', class_='pal-c-Link pal-c-Link--primary pal-c-Link--default')
        link = product.get('href')
        insert_table(link)
        print('inserted into table: ', link)
        page_product_links.append(link)
    return page_product_links

def get_product_links(category_soup):
    print('get_product_links')
    time.sleep(2)
    category_tag = category_soup.find('a', class_="pal-c-Link pal-c-Link--primary pal-c-Link--default")
    
    category_name = category_tag.get_text()
    category_link = category_tag.get('href')

    all_content = []
    pages = 0
    next_page = category_link
    with rm.scoped_driver() as driver: 
        while next_page:
            try: 
                pages += 1
                driver.get(next_page)
                all_content.extend(extract_links(driver))
                next_page = click_next_page(driver)
                print('next_page',next_page,flush=True)
                if pages % 10 == 0: 
                    time.sleep(5)
            except StaleElementReferenceException as e:
                time.sleep(5)
                print('stale element',flush=True)
                continue
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
 
    return all_content

async def main():
    url = 'https://www.ulta.com/shop/makeup/face'
    await get_category(url)
    #url = 'https://www.ulta.com/shop/makeup/face/bb-cc-creams'
    #await get_product_links(url)

if __name__ == "__main__":
    asyncio.run(main())