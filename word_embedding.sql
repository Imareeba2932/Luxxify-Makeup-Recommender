CREATE OR REPLACE FUNCTION similarity_impl(text_column TEXT, phrase TEXT)
RETURNS FLOAT8 AS $$
import gensim
import numpy as np

# Cache for the model
if 'model' not in globals():
    # Load the pre-trained Word2Vec model only once
    globals()['model'] = gensim.models.Word2Vec.load('/mnt/c/Users/ZaraS/Makeup_Recommender/fine_tuned_word2vec.model')
if 'cache' not in globals():    
    globals()['cache'] = {}

def get_phrase_vector(phrase):
    """Compute the vector for a given phrase."""
    with open('/mnt/c/Users/ZaraS/Makeup_Recommender/output.txt', 'w') as f:
        # Redirect stdout to the file
        sys.stdout = f
        if phrase in cache:
            print('cache hit: ', phrase)
            return cache[phrase]
        words = phrase.split()
        word_vectors = [model.wv[word] for word in words if word in model.wv]
        
        if not word_vectors:
            return None
        
        cache[phrase] = np.mean(word_vectors, axis=0)
        print('cache miss: ', phrase)
        return cache[phrase]
    sys.stdout = sys.__stdout__

def compute_similarity(text_vector, phrase_vector):
    """Compute cosine similarity between text_vector and phrase_vector."""
    if text_vector is None or phrase_vector is None:
        return None
    
    similarity = np.dot(phrase_vector, text_vector) / (np.linalg.norm(phrase_vector) * np.linalg.norm(text_vector))
    return similarity

# Compute the vector for the given phrase
phrase_vector = get_phrase_vector(phrase)

# Compute the vector for the text column value
text_vector = get_phrase_vector(text_column)

# Compute and return the similarity score
return compute_similarity(text_vector, phrase_vector)
$$ LANGUAGE plpython3u;


CREATE OR REPLACE FUNCTION similarity(text_column TEXT, phrase TEXT)
RETURNS FLOAT8 AS $$
DECLARE
    preprocessed_text_column TEXT;
    preprocessed_phrase TEXT;
    similarity_score FLOAT8;
BEGIN
    
    -- Compute the similarity score
    BEGIN
        -- Preprocess the text and phrase
        --preprocessed_text_column := nlp_preprocess(text_column);
        --preprocessed_phrase := nlp_preprocess(phrase);
        similarity_score := similarity_impl(text_column, phrase);
    EXCEPTION
        WHEN others THEN
            -- Return 0 in case of an exception
            similarity_score := 0;
    END;

    RETURN similarity_score;
END;
$$ LANGUAGE plpgsql;

