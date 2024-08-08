
'''
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from gensim.models import CoherenceModel
from gensim.corpora import Dictionary
from gensim.utils import simple_preprocess
import numpy as np
import matplotlib.pyplot as plt
#tokenized_texts = 'preprocessed_makeup_plain_text.txt'


with open('user_data.txt', 'r') as file:
    tokenized_texts = file.readlines()
    tokenized_texts = [line.strip() for line in tokenized_texts]  # Remove any leading/trailing whitespace



#print(type(tokenized_texts))
#print(tokenized_texts[:5])  # Print the first 5 items to check


# Vectorize the tokenized data
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(tokenized_texts)



# Train LDA model
lda_model = LatentDirichletAllocation(n_components=10, random_state=0)
lda_model.fit(X)

# Save the model and vectorizer
joblib.dump(lda_model, 'lda_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print('Successfully saved model and vectorizer')

# Get topic distributions for each document
topic_distributions = lda_model.transform(X)

def clean_paragraph(paragraph):
    """Clean unwanted characters from the paragraph."""
    return ' '.join(part.strip() for part in paragraph.split() if part.strip() and part.strip() != '\\N')

def print_top_paragraphs(topic_distributions, documents, n_top_paragraphs):
    num_topics = topic_distributions.shape[1]
    for topic_idx in range(num_topics):
        print(f"Topic #{topic_idx}:")
        # Get indices of documents most relevant to the topic
        top_docs_idx = np.argsort(topic_distributions[:, topic_idx])[-n_top_paragraphs:][::-1]
        top_docs = [documents[i] for i in top_docs_idx]  # Map indices to documents
        for doc in top_docs:
            cleaned_doc = clean_paragraph(doc)  # Clean the document
            if cleaned_doc:  # Check if the cleaned document is not empty
                print(cleaned_doc)
                print()
        print()

# Assume `documents` is a list of your paragraphs
# `topic_distributions` is the output from `lda_model.transform(documents)`

# Print top paragraphs for each topic
print_top_paragraphs(topic_distributions, tokenized_texts, n_top_paragraphs=5)
'''
'''
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Load the tokenized texts
with open('reviews_data.txt', 'r') as file:
    tokenized_texts = file.readlines()
    tokenized_texts = [line.strip() for line in tokenized_texts]  # Remove any leading/trailing whitespace

# Vectorize the tokenized data
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(tokenized_texts)

# Define range for number of topics
topic_range = range(2, 21)  # e.g., from 2 to 20 topics

perplexities = []

for n_topics in topic_range:
    # Train LDA model
    lda_model = LatentDirichletAllocation(n_components=n_topics,     learning_method='batch',       # Use 'batch' for smaller datasets
    learning_decay=0.001,            # Default value
    learning_offset=10.0,          # Default value
    max_iter=30,                   # Increase iterations
    batch_size=128,                # Default value for 'online' learning
    evaluate_every=-1,             # Not used in 'batch' learning
    total_samples=1000000)          # Total samples for 'online' learning (adjust if needed)
    lda_model.fit(X)
    
    # Compute perplexity
    perplexity = lda_model.perplexity(X)
    perplexities.append(perplexity)
    
    # Save the model and vectorizer
    joblib.dump(lda_model, f'lda_model_{n_topics}_topics.pkl')
    joblib.dump(vectorizer, f'vectorizer_{n_topics}_topics.pkl')
    print(f"Number of Topics: {n_topics}, Perplexity: {perplexity}")

# Plot the elbow chart for Perplexity
plt.figure(figsize=(10, 6))
plt.plot(topic_range, perplexities, marker='o')
plt.xlabel('Number of Topics')
plt.ylabel('Perplexity')
plt.title('Elbow Plot for Perplexity')
plt.grid(True)
plt.show()

# Get topic distributions for the final model (e.g., 10 topics)
lda_model = joblib.load('lda_model_10_topics.pkl')
topic_distributions = lda_model.transform(X)

def clean_paragraph(paragraph):
    """Clean unwanted characters from the paragraph."""
    return ' '.join(part.strip() for part in paragraph.split() if part.strip() and part.strip() != '\\N')

def print_top_paragraphs(topic_distributions, documents, n_top_paragraphs):
    num_topics = topic_distributions.shape[1]
    for topic_idx in range(num_topics):
        print(f"Topic #{topic_idx}:")
        # Get indices of documents most relevant to the topic
        top_docs_idx = np.argsort(topic_distributions[:, topic_idx])[-n_top_paragraphs:][::-1]
        top_docs = [documents[i] for i in top_docs_idx]  # Map indices to documents
        for doc in top_docs:
            cleaned_doc = clean_paragraph(doc)  # Clean the document
            if cleaned_doc:  # Check if the cleaned document is not empty
                print(cleaned_doc)
                print()
        print()

# Print top paragraphs for each topic
print_top_paragraphs(topic_distributions, tokenized_texts, n_top_paragraphs=5)
'''

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from gensim.utils import simple_preprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


# Load and preprocess your tokenized texts
with open('reviews_data.txt', 'r') as file:
    tokenized_texts = file.readlines()
    # Convert each line into a list of tokens
    tokenized_texts = [line.strip().split() for line in tokenized_texts]

# Vectorize the tokenized data
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform([' '.join(doc) for doc in tokenized_texts])

# Train LDA model
lda_model = LatentDirichletAllocation(n_components=7, random_state=0)
lda_model.fit(X)

# Save the model and vectorizer
#joblib.dump(lda_model, 'lda_model.pkl')
#joblib.dump(vectorizer, 'vectorizer.pkl')
#print('Successfully saved model and vectorizer')

# Get topic distributions for each document
topic_distributions = lda_model.transform(X)

def clean_paragraph(paragraph):
    """Clean unwanted characters from the paragraph."""
    return ' '.join(part.strip() for part in paragraph.split() if part.strip() and part.strip() != '\\N')

def print_top_paragraphs(topic_distributions, documents, n_top_paragraphs):
    num_topics = topic_distributions.shape[1]
    for topic_idx in range(num_topics):
        print(f"Topic #{topic_idx}:")
        top_docs_idx = np.argsort(topic_distributions[:, topic_idx])[-n_top_paragraphs:][::-1]
        top_docs = [documents[i] for i in top_docs_idx]
        for doc in top_docs:
            cleaned_doc = clean_paragraph(doc)
            if cleaned_doc:
                print(cleaned_doc)
                print()
        print()

# Print top paragraphs for each topic
print_top_paragraphs(topic_distributions, [' '.join(doc) for doc in tokenized_texts], n_top_paragraphs=5)

'''
# Convert tokenized texts to Gensim format
dictionary = Dictionary(tokenized_texts)
corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

# Compute coherence score
def compute_coherence_score(lda_model, corpus, dictionary):
    # Prepare the topics in the format required by CoherenceModel
    topics = [lda_model.components_[i].argsort()[-10:][::-1] for i in range(lda_model.n_components)]
    # Convert topic words to list of words
    topic_words = [[dictionary[idx] for idx in topic] for topic in topics]
    
    # Compute coherence score
    coherence_model = CoherenceModel(topics=topic_words, texts=tokenized_texts, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    return coherence_score

# Parameters for LDA
num_topics_range = range(2, 21)  # Test from 2 to 20 topics
coherence_scores = []

for num_topics in num_topics_range:

    lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=0)

    lda_model.fit(X)
    
    # Convert tokenized texts to Gensim format
    dictionary = Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]
    
    # Compute coherence score
    coherence_score = compute_coherence_score(lda_model, corpus, dictionary)
    coherence_scores.append(coherence_score)
    print(f"Number of Topics: {num_topics}, Coherence Score: {coherence_score:.4f}")

# Plot coherence scores
plt.figure(figsize=(10, 6))
plt.plot(num_topics_range, coherence_scores, marker='o')
plt.xlabel('Number of Topics')
plt.ylabel('Coherence Score')
plt.title('Coherence Scores for Different Numbers of Topics')
plt.xticks(num_topics_range)
plt.grid(True)
plt.show()
'''



