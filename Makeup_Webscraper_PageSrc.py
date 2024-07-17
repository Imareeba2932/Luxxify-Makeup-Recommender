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


# Determine number of CPUs
num_cpus = multiprocessing.cpu_count()

chrome_path = '/usr/bin/google-chrome'# Replace with your actual path
chromedriver_path = '/usr/local/bin/chromedriver'  # Adjust as necessary


options = Options() #webdriver.ChromeOptions()
options.binary_location = chrome_path


options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')



    
def get_category(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find_all(class_='CategoryCard')
    categories = {}
    product_links = []

    for c in content:
        category_tag = c.find('a', class_='pal-c-Link pal-c-Link--primary pal-c-Link--default')
        category_name = category_tag.get_text()
        print('Starting Category {}'.format(category_name), flush=True)
        category_link = category_tag.get('href')
        categories[category_name] = {}
        categories[category_name]['url'] = category_link

        product_links.extend(get_product_links(category_link, category_name))

    #Fierce parallelization
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
        futures = [executor.submit(get_product, link) for link in product_links]
        results = list(tqdm(as_completed(futures), total=len(product_links)))

def get_driver():
    # Install ChromeDriver if not found and create WebDriver instance
    driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options)
    #driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options= options)
    driver.maximize_window()
    return driver

def get_product(c):
    product_link_tag = c.find('a', class_='pal-c-Link pal-c-Link--primary pal-c-Link--default')
    product_link = product_link_tag.get('href')
    new_product = {}

    new_product = get_product_details(product_link)
    #Next Set of Info to get: 
    product_details = get_spec_prod_details(product_link)
    new_product.update(product_details)

    reviews = get_product_reviews(product_link)
    new_product['reviews'] = reviews
    return new_product

def get_product_links(category_link, category_name):
    driver = get_driver()
    driver.get(category_link)

    ##Gets and returns the link to the next page of products
    def click_next_page():
        try:
            next_page_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located ((By.CLASS_NAME, 'ProductListingWrapper__LoadContent' ))
            )
            next_page_link = next_page_link.find_element(By.TAG_NAME, 'a')
            next_page_href = next_page_link.get_attribute('href')
            return next_page_href
        except NoSuchElementException:
            return False

    def extract_links(): 
        soup = BeautifulSoup(driver.page_source, "html.parser")
        content = soup.find_all(class_='ProductCard')
        return content

    all_content = extract_links() #gets the first page

    #Handles pagination for the next pages of the category link
    next_page = click_next_page()
    while next_page: 
        driver.get(next_page)
        all_content.extend(extract_links())
        next_page = click_next_page()
    driver.quit()
    return all_content



# Returns info such as ingredrients and product description
def get_product_details(product_link):
    r = requests.get(product_link)
    soup = BeautifulSoup(r.content, "html.parser")
    html_content = soup.find_all(class_='ProductHero__content')
    description = ''
    product = {}
    product['url'] = product_link
    
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
    product['description'] = description
    #print(product)
    return product

#Adds specific product fields to json (name, id, price)
def get_spec_prod_details(product_link): 
    r = requests.get(product_link)
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find(class_='ProductHero__content')
    product_details = {}

    #c = content[0]
    name = content.find(class_= 'Text-ds Text-ds--body-1 Text-ds--left Text-ds--black')
    price = content.find(class_='ProductPricing')
    id_num = content.find(class_='Text-ds Text-ds--body-3 Text-ds--left Text-ds--neutral-600')

    product_price = price.get_text()
    product_name = name.get_text()
    product_id = id_num.get_text()

    product_details['price'] = product_price
    product_details['id'] = product_id
    product_details['name'] = product_name

    return product_details

def get_product_reviews(product_link):
    driver = get_driver()
    # Initialize the WebDriver
 
    driver.get(product_link)
    reviews = {}
    xhr_links = [] #stores the specific xhr links needed
    reviews = []
    
    # Function to extract the XHR URL
    def extract_xhr_url():
        for request in driver.requests: 
            xhr_links.append(request.url)
        return xhr_links
        
    # Define a function to gradually scroll through the entire page
    def slow_scroll(start_position):
        scroll_height = driver.execute_script('return document.body.scrollHeight')
        current_position = start_position
        while current_position < scroll_height:
            driver.execute_script('window.scrollTo(0, {});'.format(current_position))
            current_position += 100  # Adjust scrolling speed by changing increment
            time.sleep(0.2)  # Adjust sleep time to control scrolling speed

    # Function to click the "Next" link
    def click_next_review_page():
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

    try:
        # Wait for the section to be visible (adjust timeout as needed)
        section_id = "reviews"
        section_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, section_id))
        )
        height = section_element.location['y']
        time.sleep(2)
        slow_scroll(height)
        extract_xhr_url()

        pg_count = 1
        while click_next_review_page() and pg_count < 2:
            pg_count += 1
            time.sleep(2)  # Wait for new content to load
            slow_scroll(height)
            extract_xhr_url()       
    finally:
        # Close the browser
        driver.quit()
    
    #Adding Reviews to Product JSON
    for x in xhr_links: 
        if 'display.powerreviews.com' in x: 
            r = requests.get(x)
            soup = BeautifulSoup(r.content, "html.parser")   
            reviews.append(soup.prettify())  
    return reviews


url = 'https://www.ulta.com/shop/makeup/face'
print(os.cpu_count())
get_category(url)
#links  = get_product_links('https://www.ulta.com/shop/makeup/face/foundation', 'foundation')
#print(links)
#reviews = get_product_reviews("https://www.ulta.com/p/double-wear-stay-in-place-foundation-xlsImpprod14641507?sku=2309420")
#print(reviews)
 