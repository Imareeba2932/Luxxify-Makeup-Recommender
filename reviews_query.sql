DROP MATERIALIZED VIEW clean_reviews;
CREATE MATERIALIZED VIEW clean_reviews AS
WITH extracted_elements AS (
    SELECT
        jsonb_array_elements(reviews)::text AS elem,
        product_link_id
    FROM
        product_reviews
    --WHERE page = 1
),
converted_elements AS (
    SELECT
        elem,
        CASE
            WHEN can_convert_to_json(elem) THEN clean_and_convert_json(elem)::json
            ELSE NULL
        END AS converted_json,
        product_link_id
    FROM
        extracted_elements
), 
results AS(
    SELECT json_array_elements(converted_json->'results') AS result_elem,
    product_link_id
    FROM converted_elements
), 
sub_result AS(
    SELECT (result_elem -> 'page_id') AS page_id, 
     (result_elem -> 'reviews') AS reviews,
    (result_elem->'rollup') AS roll_up,
    product_link_id ,
    result_elem::jsonb ? 'rollup' as has_rollup
    FROM results  
), 
roll AS (
    SELECT product_link_id, json_array_elements(roll_up -> 'media') AS media 
    FROM sub_result
    where has_rollup
), 
media_reviews AS(
    SELECT product_link_id, 
    (media->>'review_id')::bigint AS review_id,
        media->>'type' AS type,
    media->>'id' AS id,
    NULL as ugc_id,
    NULL as legacy_id,
    -1 as internal_review_id,
    media->>'headline' AS headline,
    media->>'nickname' AS nickname,
    to_timestamp((media->>'created_date')::bigint / 1000) AS created_date,
    '1970-01-01 00:00:00'::timestamp as updated_date,
        (media->>'rating')::int AS rating,
    (media->>'helpful_votes')::int AS helpful_votes,
    (media->>'not_helpful_votes')::int AS not_helpful_votes,

    media->>'uri' AS uri,

    NULL AS comments,
   
    
    NULL AS locale,
    NULL AS location,
    
   
    NULL AS bottom_line,
    NULL AS product_page_id,
    NULL AS upc,
    NULL AS gtin,
    
    -- Extracting badges
    FALSE AS is_staff_reviewer,
    FALSE AS is_verified_buyer,
    FALSE AS is_verified_reviewer,
    

    -1 AS helpful_score
    
    
    
    FROM roll
    
),
text_reviews AS(
    SELECT product_link_id,
    (review->>'review_id')::bigint AS review_id,
    'pure_text' as type,
    NULL as id,
    review->>'ugc_id' AS ugc_id,
    review->>'legacy_id' AS legacy_id,
    (review->>'internal_review_id')::bigint AS internal_review_id,
     (review->'details'->>'headline') AS headline,
     (review->'details'->>'nickname') AS nickname,
     to_timestamp((review->'details'->>'created_date')::bigint /1000) AS created_date,
      to_timestamp((review->'details'->>'updated_date')::bigint /1000)  AS updated_date,
(review->'metrics'->>'rating')::int AS rating,
    -- Extracting metrics
    (review->'metrics'->>'helpful_votes')::int AS helpful_votes,
    (review->'metrics'->>'not_helpful_votes')::int AS not_helpful_votes,
 NULL as uri,
    -- Extracting details
    (review->'details'->>'comments') AS comments,
   
    
    (review->'details'->>'locale') AS locale,
    (review->'details'->>'location') AS location,
    
   
    (review->'details'->>'bottom_line') AS bottom_line,
    (review->'details'->>'product_page_id') AS product_page_id,
    (review->'details'->>'upc') AS upc,
    (review->'details'->>'gtin') AS gtin,
    
    -- Extracting badges
    (review->'badges'->>'is_staff_reviewer')::boolean AS is_staff_reviewer,
    (review->'badges'->>'is_verified_buyer')::boolean AS is_verified_buyer,
    (review->'badges'->>'is_verified_reviewer')::boolean AS is_verified_reviewer,
    

    
    (review->'metrics'->>'helpful_score')::int AS helpful_score
    FROM (SELECT product_link_id, json_array_elements(reviews) AS review FROM sub_result) as t
), all_reviews AS (
    SELECT * from media_reviews
    UNION ALL
    SELECT * from text_reviews
)
SELECT row_number() over() as unique_review_id,
* FROM all_reviews; 



