
import time



from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options
options = webdriver.ChromeOptions()
# Uncomment the following line to run in headless mode
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Initialize the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


# Navigate to the Ulta product page
driver.get("https://www.ulta.com/p/double-wear-stay-in-place-foundation-xlsImpprod14641507?sku=2309420")

# Define variables for pagination
current_page = 1
max_pages = 5  # Example: scrape up to 5 pages

#review_elements = driver.find_element('xpath', "//div[contains(@class, 'ProductReviews__Reviews--containerList')]")
#print(review_elements) 
articleDictionary = dict()
myKey = ""
myValue_total = ""

# Optionally wait for the page to load completely
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='ProductReviews__Reviews--containerList']")))
    
# Get the HTML content
html_content = driver.page_source
print(html_content) 
