# Luxxify Makeup Recommender

## Overview 
The Luxxify Makeup Recommender generates curated product suggestions tailored to individual profiles based on skin tone, type, age, makeup coverage preference, and specific skin concerns. The recommendation engine leverages machine learning with rule-based logic, trained on a custom dataset collected through web scraping. The project is deployed on a scalable Streamlit application, showcasing strong data science and deployment capabilities.

To use the Luxxify Makeup Recommender click on this link: https://luxxify.streamlit.app/



## Technologies Used
- **Programming Languages:** Python and PostgreSQL
- **Python Libraries:**
  - `[pandas](https://pandas.pydata.org/)`: Data manipulation and analysis 
  - `[numpy](https://numpy.org/)`: Numerical computing
  - `[gensim](https://pypi.org/project/gensim/)`: Natural language processing
  - `[scikit-learn](https://scikit-learn.org/stable/)`: Machine learning
  - `[matplotlib] (https://matplotlib.org/)` and `[seaborn] (https://seaborn.pydata.org/)`: Data visualization
  - `[ortools](https://pypi.org/project/ortools/)`: Operations research and optimization for rule based logic
  - `[psycopg2](https://pypi.org/project/psycopg2/)`: PostgreSQL database adapter for Python
  - `[streamlit](https://streamlit.io/)`: Application hosting
  - `[requests](https://pypi.org/project/requests/)`: Requesting URLs
  - `[selenium](https://selenium-python.readthedocs.io/)`: Scrolling and button interactions
  - `[beautifulsoup4](https://pypi.org/project/beautifulsoup4/)`: Accessing site text
  


## Features
- **Personalized Recommendations:** Utilizes a [Random Forest] (https://scikit-learn.org/1.5/modules/generated/sklearn.ensemble.RandomForestClassifier.html) model to predict scores for makeup products based on user profiles.
- **Budget Optimization:** Implements a [linear programming solver](https://developers.google.com/optimization/mip/mip_example) to recommend products that fit within the user-defined budget while maximizing predicted satisfaction scores.
- **Similarity Assessment:** Computes text similarity using [Word2Vec](https://radimrehurek.com/gensim/models/word2vec.html) embeddings for better understanding of product descriptions and user queries.
- **Interactive User Input:** Processes user preferences including skin type, coverage needs, and specific concerns to generate tailored product suggestions.
- **Custom Dataset Collection:** Web scraping of product and review data from various online sources, creating a dataset uniquely tailored to the beauty and skincare domain.
- **Handcrafted Feature Engineering:** Features were selected based on insights from Natural Language Processing (NLP) and word embeddings derived from Reddit discussions on makeup.
- **Model Training with Class Diversity:** The Random Forest model was trained with both over-sampling and under-sampling to ensure balanced recommendations across different product classes.
- **Constraint-based Logic:** Linear programming enforces rule-based constraints, refining recommendations based on compatibility with user preferences.
- **Optimized Deployment:** Streamlit caching is leveraged to optimize app speed and scalability.

## Technical Details

### Data Collection and Processing

- **Web Scraping:** Product and review data are scraped from [Ulta](https://www.ulta.com/), which is a popular e-commerce site for cosmetics. This raw data serves as the foundation for a robust recommendation engine, with a custom scraper built using requests, Selenium, and BeautifulSoup4. Selenium was used to perform button click and scroll interactions on the Ulta site to dynamically load data. We then used requests to access specific URLs from XHR GET requests. Finally, we used BeautifulSoup4 for scraping static text data.
 
- **PostgreSQL Ingestion**: For data management, [PostgreSQL](https://www.postgresql.org/) was chosen for its scalability and efficient storage capabilities. This decision supports complex queries and enhances data integrity while providing a structured environment for storing diverse datasets, including user profiles and product data. 

- **Leveraging PostgreSQL UDFs For Feature Extraction**: Python PostgreSQL UDFs were used to make feature engineering more scalable. To optimize performance, a caching mechanism was introduced, storing computed vectors for previously encountered phrases, which significantly speeds up similarity calculations for repeated queries. 

- **NLP and Feature Engineering:** Key features are extracted using word embeddings from Reddit makeup discussions (https://www.reddit.com/r/beauty/). Incorporating Word2Vec embeddings for text processing was a key engineering decision. This approach allows the system to capture semantic relationships between words, enabling more meaningful comparisons of makeup product descriptions and user inputs. This allows us to tap into consumer insights and user preferences across various demographics, focusing on features highly relevant to makeup selection.  

### Modeling and Optimization

- **Random Forest Model Selection:** To power the recommendation engine, a Random Forest model was selected for its robustness against overfitting and its ability to handle a mix of numerical and categorical variables. This choice is particularly well-suited for processing diverse user input data related to makeup products, such as skin type and conditions, ensuring accurate and reliable recommendations.

- **Cross Validation and Sampling:** A Random Forest model is employed to handle the complexity and non-linearity of makeup recommendation. Due to the class imbalance with many reviews being five-stars, we utilized mixed over-sampling and under-sampling to balance class diversity. This approach improves accuracy across different product categories, especially those with lower initial representation. We also randomly sampled mutually exlcusive product sets for train/test splits. This helped us avoid data leakage. 

- **Linear Programming for Constraints:** Understanding user needs in practical shopping scenarios, the system includes features for budget optimization. The optimization algorithm ensures that users receive product recommendations that not only align with their preferences but also adhere to their financial constraints, making the tool practical and user-friendly. To enhance the relevance of recommendations, a linear programming-based rule engine is used to apply budget constraints, ensuring recommendations align with user skin tone, age, and experience level. We also included domain knowledge based rules to help with product category selection. 



### Deployment

- **User Experience:** The system is designed with user experience in mind, offering an interactive interface that allows for easy input of user profiles and preferences. This design choice enhances accessibility, ensuring that individuals with varying levels of technical expertise can utilize the system effectively.

- **User Input Handling:** A comprehensive preprocessing phase for user inputs was integrated to transform raw data into a format that can be effectively processed by the model. Although the preprocessing function is currently commented out, this initial design anticipates potential enhancements to streamline user interactions and improve recommendation accuracy. Additionally, a robust error-handling mechanism ensures that the system can gracefully manage unexpected inputs or computational failures, returning a default value rather than crashing.

- **Scalability with Streamlit Caching:** Streamlit’s caching functionality is used to speed up response times and make the application scalable for multiple users. Cached elements minimize redundant processing, ensuring faster delivery of results for users with similar inputs. This avoids Streamlit throttling errors. 



### Future Improvements

- **Enhance NLP Based Features:** Integrate additional sources for a broader and more diverse dataset.
Enhanced NLP Features: Experiment with more advanced NLP models like BERT or other transformers to capture deeper insights from beauty reviews.
- **User Feedback Integration:** Allow users to rate recommendations, creating a feedback loop for continuous model improvement.
- **Add Causal Discrete Choice Model:** Add causal discrete choice model to capture choices across the competitive landscape and causally determine why customers select certain products. Nested logit models look like a good choice to ensemble with our existing model. 
- **Implement Computer Vision Based Features:** Extract CV based features from image and video review data. This is will allow us to extract more fine grained demographic information.  
 

# Contact
For any inquiries, reach out via:

GitHub: @zara-sarkar

LinkedIn: https://www.linkedin.com/in/zsarkar/

Email: sarkar.z@northeastern.edu

