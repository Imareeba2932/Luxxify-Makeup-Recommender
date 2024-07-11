import requests
from bs4 import BeautifulSoup
import html_to_json
import json
from jsonpath_ng import jsonpath, parse


from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup
import html_to_json
import json
from jsonpath_ng import jsonpath, parse




    
def get_category(link):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find_all(class_='CategoryCard')
    categories = {}
    #print(content)
    for c in content:
        category_tag = c.find('a', class_='pal-c-Link pal-c-Link--primary pal-c-Link--default')
        category_name = category_tag.get_text()
        category_link = category_tag.get('href')
        product_info[category_name] = {}
        product_info[category_name]['url'] = category_link
        #product_info[category_name]['products'] = []

        #print(category_link)
        get_product_links(category_link, category_name)


   

def get_product_links(category_link, category_name):
    r = requests.get(category_link)
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find_all(class_='ProductCard')
    all_products = {}
    all_products['category'] = category_name
    all_products['url'] = category_link
    all_products['product_list'] = []
    
    
    for c in content:
        product_link_tag = c.find('a', class_='pal-c-Link pal-c-Link--primary pal-c-Link--default')
        product_link = product_link_tag.get('href')
        all_products['product_list'].append(get_product_details(product_link))
    print(all_products)

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

    #Next Set of Info to get: 
    #get_spec_prod_details(product_link, product)
    #get_reviews(product_link, product)
    return product

    #Next set of info to get



def get_spec_prod_details(product_link, product): 
    r = requests.get(product_link)
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find_all(class_='ProductHero__content')

    

    for c in content:
        name = c.find(class_= 'Text-ds Text-ds--body-1 Text-ds--left')
        price = c.find(class_='ProductPricing')
        id_num = c.find(class_='Text-ds Text-ds--body-3 Text-ds--left Text-ds--neutral-600')

        product_price = price.get_text()
        product_name = name.get_text()
        product_id = id_num.get_text()

        product['price'] = product_price
        product['id'] = id_num
        product['name'] = name

   
def get_product_reviews(product_link, product):
    options = webdriver.ChromeOptions()
    # Uncomment the following line to run in headless mode
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
      
    # Initialize the WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.get(product_link)
    xhr_links = [] #stores the specific xhr links needed
    product['reviews'] = []
      
    # Function to extract the XHR URL
    def extract_xhr_url():
        for request in driver.requests: 
            xhr_links.append(request.url)    
     
    # Define a function to gradually scroll through the entire page
    def slow_scroll(start_position):
        scroll_height = driver.execute_script('return document.body.scrollHeight')
        current_position = start_position
        while current_position < scroll_height:
            driver.execute_script('window.scrollTo(0, {});'.format(current_position))
            current_position += 100  # Adjust scrolling speed by changing increment
            time.sleep(0.2)  # Adjust sleep time to control scrolling speed
    
    try:
        # Wait for the section to be visible (adjust timeout as needed)
        section_id = "reviews"
        section_element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, section_id))
        )
        height =  0
        time.sleep(2)
        slow_scroll(height)
        extract_xhr_url()
    finally:
        # Close the browser
        driver.quit()
    
    #Adding Reviews to Product JSON
    for x in xhr_links: 
        if 'display.powerreviews.com' in x: 
            product['reviews'].append(x)   

url = 'https://www.ulta.com/shop/makeup/face'
product_info = {}
get_category(url) 

 