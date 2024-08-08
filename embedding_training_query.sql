DROP MATERIALIZED VIEW  preprocessed_makeup_plain_text ;
CREATE MATERIALIZED VIEW preprocessed_makeup_plain_text AS
WITH all_text AS (
SELECT
description
FROM clean_products
UNION
SELECT
pros
FROM clean_products
UNION
SELECT
cons
FROM clean_products
UNION
SELECT
best_uses
FROM clean_products
UNION
SELECT
describe_yourself
FROM clean_products
UNION
SELECT
faceoff_negative
FROM clean_products
UNION
SELECT
faceoff_positive
FROM clean_products
UNION
SELECT headline
FROM clean_reviews
UNION 
SELECT comments
FROM clean_reviews
), 

randomized_text As (
    SELECT
ROW_NUMBER() OVER (ORDER BY RANDOM()) AS random_row_number,
regexp_split_to_table(description, '\.\s*') as description
from all_text
)
SELECT * from randomized_text ORDER BY random_row_number;


\COPY (SELECT description FROM preprocessed_makeup_plain_text) TO 'preprocessed_makeup_plain_text.txt' WITH (FORMAT text);