WITH extracted_elements AS (
    SELECT
        jsonb_array_elements(reviews)::text AS elem,
        product_link_id
    FROM
        product_reviews
    WHERE page = 1
    LIMIT 1
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
    product_link_id
    FROM results
), 
roll AS (
    SELECT (roll_up -> 'rating_histogram') AS rating_histogram, 
    (roll_up -> 'review_histogram') AS review_histogram, 
    (roll_up -> 'rating_count') AS rating_count, 
    (roll_up -> 'review_count') AS review_count, 
    (roll_up -> 'average_rating') AS average_rating, 
    (roll_up -> 'recommended_ratio') AS recommended_ratio, 
    (roll_up -> 'native_review_count') AS native_review_count,
    (roll_up -> ' native_sampling_review_count') AS  native_sampling_review_count,
    (roll_up -> 'native_community_content_review_count') AS native_community_content_review_count,
    (roll_up -> 'syndicated_review_count') AS syndicated_review_count,

    --json_array_elements(roll_up -> 'properties') AS properties,
    --json_array_elements(roll_up -> 'media') AS media,
    product_link_id , 
    roll_up -> 'properties' as properties,
    roll_up -> 'media' as media

    FROM sub_result
), reviews_hist as (
    SELECT
        *,
        row_number() OVER (PARTITION BY product_link_id) AS elem_index
    FROM
        (SELECT product_link_id, json_array_elements(review_histogram)::text::integer AS elem FROM roll) as t
), rating_hist as (
    SELECT
        *,
        row_number() OVER (PARTITION BY product_link_id) AS elem_index
    FROM
        (SELECT product_link_id, json_array_elements(rating_histogram)::text::integer AS elem FROM roll) as t
), prop as (
    SELECT
        product_link_id,
        property_name::text as property_name,
         REPLACE(REPLACE(STRING_AGG(elem, ' '), '''', ''), '"', '') as property_text,
        row_number() OVER (PARTITION BY product_link_id) AS elem_index
    FROM
        (SELECT product_link_id, json_array_elements(properties)->'name' as property_name, json_array_elements(json_array_elements(properties)-> 'display_values')::text AS elem FROM roll) as t
        GROUP BY 1,2
)

SELECT
(SELECT elem from reviews_hist where roll.product_link_id = reviews_hist.product_link_id AND elem_index = 1) as review_star_1,
(SELECT elem from reviews_hist where roll.product_link_id = reviews_hist.product_link_id AND elem_index = 2) as review_star_2,
(SELECT elem from reviews_hist where roll.product_link_id = reviews_hist.product_link_id AND elem_index = 3) as review_star_3,
(SELECT elem from reviews_hist where roll.product_link_id = reviews_hist.product_link_id AND elem_index = 4) as review_star_4,
(SELECT elem from reviews_hist where roll.product_link_id = reviews_hist.product_link_id AND elem_index = 5) as review_star_5,
(SELECT elem from rating_hist where roll.product_link_id = rating_hist.product_link_id AND elem_index = 1) as rating_star_1,
(SELECT elem from rating_hist where roll.product_link_id = rating_hist.product_link_id AND elem_index = 2) as rating_star_2,
(SELECT elem from rating_hist where roll.product_link_id = rating_hist.product_link_id AND elem_index = 3) as rating_star_3,
(SELECT elem from rating_hist where roll.product_link_id = rating_hist.product_link_id AND elem_index = 4) as rating_star_4,
(SELECT elem from rating_hist where roll.product_link_id = rating_hist.product_link_id AND elem_index = 5) as rating_star_5,
rating_count,
review_count,
average_rating,
recommended_ratio,
native_review_count,
native_sampling_review_count,
native_community_content_review_count,
syndicated_review_count
FROM  roll limit 5;



