# Makeup_Recommender
This project aims to recommend a user specific makeup products given their skin type and concerns. 
It was divided into three stages: webscraping, model development, and web development. 

## Webscraping
The makeup data was scraped from Ulta as it is a reputable site with makeup products at various pricepoints. To perform the webscraping, I first used BeautifulSoup to scrape the initial product data such as the name, brand, price, item ID, and the product link. Because this information is static, it was possible to make use of BeautifulSoup. This is a different story when scraping for the product reviews. 

The main difficulty with scraping the product reviews is that there were hundreds of pages of reviews for each product. That meant that scraping each page sequentially was not an option, especially given the fact that my only resource was my laptop. In order to do this I used Asyncio and Selenium to asynchronously scrape reviews for each makeup product. Even with the optimizations, it still took around a day to successfully load the data into Postgres. 

All the data was loaded into Postgres. 

## Model Development

To begin development, I started with EDA. I used LDA to perform a soft cluster on the reviews data to examine any patterns in the reviewer (and thereby user) data. I used materialized views to gather all the review information before performing LDA on it. 

I then created a word embedding model to quantify the text data. The motivation behind picking this model was twofold. One was that it is easy to run given my limited computing power. The second was because I have a lot of domain knowledge when it comes to makeup. Therefore, with a word embedding model, it is easy for me to tune parameters given my existing model. I trained the model on Reddit makeup data so that the model also understands makeup related terminology. 

Finally, I used the outputs from the word embedding model as parameters for the RandomForest model. THe RandomForest was designed to predict a rating (from 1 to 5) of a specific product given a user profile and budget per product constraint. The RandomForest was trained using all the reviews and product descriptions. With some tweaking, I was able to improve the F1 score to 0.91.

## Web Development

To develop the site, I used StreamLit. That way, I could develop everything in Python, which made it easy to incporate my model into an interactive site. 

I also made sure to add concurrency measures to prevent the site from crashing should there be multiple  users at the same time. 

