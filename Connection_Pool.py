import requests
from bs4 import BeautifulSoup
import html_to_json
import json
import os
import atexit
from contextlib import contextmanager
from jsonpath_ng import jsonpath, parse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from psycopg2 import pool
import time
import threading
import queue
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import psycopg2
import gc

'''
# Create a cursor object
cursor = conn.cursor()

# Print PostgreSQL version
cursor.execute("SELECT version();")
db_version = cursor.fetchone()
print(f"PostgreSQL version: {db_version}")

conn = ResourcePool.get_connection()
try:
    cursor = conn.cursor()
    query = 'INSERT INTO json_data (text) VALUES (%s)'
    cursor.execute(query, [json.dumps(new_product)])
    conn.commit()
    cursor.close()
finally:
    ResourcePool.put_connection(conn)
'''

chrome_path = '/usr/bin/google-chrome'# Replace with your actual path
chromedriver_path = '/usr/local/bin/chromedriver'  # Adjust as necessary

class ResourceManager:
    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__initialized = False
        return cls._instance

    def __init__(self, max_threads=16, max_connections=1):
        if self.__initialized:
            return
        self.__initialized = True
        self.max_threads = max_threads
        self.driver_queue = queue.Queue()
        self.lock = threading.Lock()
        gc.collect()
        gc.disable()
        #atexit.register(self.cleanup)
  
   

        self.db_connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn= max_connections,
            database="makeup",
            user="zsarkar01",
            password="project",
            host="localhost",
            port="5432",
            sslmode="disable"
        )



        self.create_resources()

    def create_resources(self):

        # Create WebDriver pool
        options = Options() #webdriver.ChromeOptions()
        options.binary_location = chrome_path


        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(executable_path=chromedriver_path)
        for _ in range(self.max_threads):
            driver = webdriver.Chrome(service=service, options=options)
            driver.maximize_window()
            self.driver_queue.put(driver)

    def get_driver(self):
        with self.lock:
            return self.driver_queue.get()

    def release_driver(self, driver):
        with self.lock:
            self.driver_queue.put(driver)
        


    def execute_query(self, query, values=None):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
    
    @contextmanager
    def get_connection(self):
        conn = self.db_connection_pool.getconn()
        try:
            yield conn
        finally:
            self.db_connection_pool.putconn(conn)

    def __del__(self):
        """Destructor to clean up resources."""
        self.cleanup()
        gc.collect()

    def cleanup(self):
        with self.lock:
            while not self.driver_queue.empty():
                driver = self.driver_queue.get()
                driver.quit()
                del driver
            
        if self.db_connection_pool:
            self.db_connection_pool.closeall()
            self.db_connection_pool = None
            del self.db_connection_pool

    @contextmanager
    def scoped_driver(self):
        driver = self.get_driver()
        try:
            yield driver
        finally:
            self.release_driver(driver)