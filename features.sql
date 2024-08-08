CREATE OR REPLACE PROCEDURE refresh_all_products_reviews(batch_size INT)
LANGUAGE plpgsql
AS $$
DECLARE
    start_id INTEGER := 1;
    end_id INTEGER;
    max_id INTEGER;
BEGIN
    -- Handle table truncation properly
    BEGIN
        EXECUTE 'TRUNCATE TABLE all_products_reviews';
    EXCEPTION
        WHEN undefined_table THEN
            -- If table does not exist, do nothing
            RAISE NOTICE 'Table all_products_reviews does not exist, skipping TRUNCATE.';
    END;

    -- Create the new table if it does not exist
    EXECUTE '
    CREATE TABLE IF NOT EXISTS all_products_reviews (
        unique_review_id INTEGER,
        review_link_id INTEGER,
        user_rating FLOAT,
        locale TEXT,
        location TEXT,
        helpful_score INTEGER,
        young_review FLOAT,
        mother_review FLOAT,
        professional_review FLOAT,
        vibe_review FLOAT,
        acne_review FLOAT,
        dry_review FLOAT,
        wrinkles_review FLOAT,
        poc_review FLOAT,
        white_review FLOAT,
        tan_review FLOAT,
        redness_review FLOAT,
        coverage_review FLOAT,
        light_coverage_review FLOAT,
        medium_coverage_review FLOAT,
        full_coverage_review FLOAT,
        expensive_review FLOAT,
        inexpensive_review FLOAT,
        skin_concerns_review FLOAT,
        comfortable_wear_review FLOAT,
        easy_use_review FLOAT,
        pilling_review FLOAT,
        shade_range_review FLOAT,
        product_link_id INTEGER,
        category TEXT,
        recommended_ratio FLOAT,
        num_shades INTEGER,
        overall_product_rating FLOAT,
        num_reviews INTEGER,
        young FLOAT,
        mother FLOAT,
        professional FLOAT,
        vibe FLOAT,
        acne FLOAT,
        dry FLOAT,
        wrinkles FLOAT,
        poc FLOAT,
        white FLOAT,
        tan FLOAT,
        redness FLOAT,
        coverage FLOAT,
        light_coverage FLOAT,
        medium_coverage FLOAT,
        full_coverage FLOAT,
        expensive FLOAT,
        inexpensive FLOAT,
        skin_concerns FLOAT,
        comfortable_wear FLOAT,
        easy_use FLOAT,
        pilling FLOAT,
        shade_range FLOAT
    )';
    COMMIT;

    -- Get the maximum product_link_id
    SELECT MAX(product_link_id) INTO max_id
    FROM clean_products;

    -- Batch processing
    WHILE start_id <= max_id LOOP
        end_id := start_id + batch_size - 1;

        -- Ensure end_id does not exceed max_id
        IF end_id > max_id THEN
            end_id := max_id;
        END IF;

        -- Insert data in the current batch with predicate pushed down into the query
        EXECUTE FORMAT('
            INSERT INTO all_products_reviews
            WITH product_profile AS (
                SELECT 
                    product_link_id,
                    category,
                    recommended_ratio,  
                    num_shades, 
                    rating AS overall_product_rating, 
                    num_reviews,
                    similarity(describe_yourself, ''young mid twenties'') AS young,
                    similarity(describe_yourself, ''working mom working mother working parent'') AS mother,
                    similarity(describe_yourself, ''mature professional active'') AS professional, 
                    similarity(describe_yourself, ''energetic trendy youthful'') AS vibe, 
                    similarity(describe_yourself, ''acne oily sensitive skin  zits blemishes pores'')  + similarity(pros, ''acne oily sensitive skin  zits blemishes pores'') + similarity(cons, ''acne oily sensitive skin  zits blemishes pores'') +  similarity(pros, ''acne oily sensitive skin  zits blemishes pores'') + similarity(best_uses, ''acne oily sensitive skin  zits blemishes pores'') AS acne,
                    similarity(describe_yourself, ''dry sensitive skin'') AS dry,
                    similarity(describe_yourself, ''wrinkles'') AS wrinkles, 
                    similarity(describe_yourself, ''dark skin'')  AS poc, 
                    similarity(describe_yourself, ''fair pale light skin'')  AS white, 
                    similarity(describe_yourself, ''tan olive skin'') AS tan, 
                    similarity(describe_yourself, ''redness rosacea'') + similarity(pros, ''redness rosacea'') + similarity(cons, ''redness rosacea'') + similarity(best_uses, ''redness rosacea'') AS redness,
                    similarity(pros, ''coverage'') + similarity(cons, ''coverage'') AS coverage, 
                    similarity(pros, ''light coverage natural skin like'') + similarity(cons, ''light coverage natural skin like'') +  similarity(best_uses, ''light coverage natural skin like'') AS light_coverage,
                    similarity(pros, ''medium coverage buildable coverage'') + similarity(cons, ''medium coverage buildable coverage'') + similarity(best_uses, ''medium coverage buildable coverage'') AS medium_coverage,
                    similarity(pros, ''full coverage full face'') + similarity(cons, ''full coverage full face'') + similarity(best_uses, ''full coverage full face'') AS full_coverage,
                    similarity(pros, ''expensive pricey'') + similarity(cons, ''expensive pricey'') AS expensive, 
                    similarity(pros, ''inexpensive budget friendly drugstore'') + similarity(cons, ''inexpensive budget friendly drugstore'') as inexpensive, 
                    similarity(pros, ''wrinkles hyperpigmentation acne'') + similarity(cons, ''wrinkles hyperpigmentation acne'') AS skin_concerns,  
                    similarity(pros, ''comfortable lightweight breathable'') + similarity(cons, ''comfortable breathable lightweight'') - similarity(cons, ''uncomfortable heavy'')  AS comfortable_wear, 
                    similarity(pros, ''easy easy to use blendable'') + similarity(cons, ''easy easy to use blendable'') - similarity(cons, ''not easy hard to blend'') AS easy_use,
                    similarity(pros, ''pilling separates'') + similarity(cons, ''pilling separates'') AS pilling,
                    (similarity(pros, ''many shades shade range'') + similarity(faceoff_positive, ''many shades shade range'') ) - (similarity(cons, ''limited shade range few shades'') + similarity(faceoff_negative, ''limited shade range few shades'') ) AS shade_range
                FROM clean_products
                WHERE product_link_id BETWEEN %L AND %L
            ), 
            reviewer_profile AS (
                SELECT 
                    unique_review_id, 
                    product_link_id AS review_link_id, 
                    rating AS user_rating,
                    locale, 
                    location, 
                    helpful_score, 
                    similarity(headline, ''young mid twenties'') + similarity(comments, ''young mid twenties'') AS young_review,
                    similarity(headline, ''working mom working mother working parent'')  + similarity(comments, ''working mom working mother working parent'') AS mother_review,
                    similarity(headline, ''mature professional active'') + similarity(comments, ''mature professional active'') AS professional_review, 
                    similarity(headline, ''energetic trendy youthful'') + similarity(comments, ''energetic trendy youthful'') AS vibe_review, 
                    similarity(headline, ''acne oily sensitive skin  zits blemishes pores'')  + similarity(comments, ''acne oily sensitive skin  zits blemishes pores'') AS acne_review,
                    similarity(headline, ''dry sensitive skin'') + similarity(comments, ''dry sensitive skin'') AS dry_review,
                    similarity(headline, ''wrinkles'') + similarity(comments, ''wrinkles'') AS wrinkles_review, 
                    similarity(headline, ''dark skin'') + similarity(comments, ''dry sensitive skin'') AS poc_review, 
                    similarity(headline, ''fair pale light skin'') + similarity(comments, ''dark skin'')  AS white_review, 
                    similarity(headline, ''tan olive skin'') + similarity(comments, ''dry sensitive skin'') AS tan_review, 
                    similarity(headline, ''redness rosacea'') + similarity(comments, ''redness rosacea'') AS redness_review, 
                    similarity(headline, ''coverage'') + similarity(comments, ''coverage'') AS coverage_review, 
                    similarity(headline, ''light coverage natural skin like'') + similarity(comments, ''light coverage natural skin like'') AS light_coverage_review,
                    similarity(headline, ''medium coverage buildable coverage'') + similarity(comments, ''medium coverage buildable coverage'') AS medium_coverage_review,
                    similarity(headline, ''full coverage full face'') + similarity(comments, ''full coverage full face'') AS full_coverage_review,
                    similarity(headline, ''expensive pricey'') + similarity(comments, ''expensive pricey'') AS expensive_review, 
                    similarity(headline, ''inexpensive budget friendly drugstore'') + similarity(comments, ''inexpensive budget friendly drugstore'') as inexpensive_review, 
                    similarity(headline, ''wrinkles hyperpigmentation acne'') + similarity(comments, ''wrinkles hyperpigmentation acne'') AS skin_concerns_review,  
                    similarity(headline, ''comfortable lightweight breathable'') + similarity(comments, ''comfortable breathable lightweight'') - similarity(comments, ''uncomfortable heavy'') AS comfortable_wear_review, 
                    similarity(headline, ''easy easy to use blendable'') + similarity(comments, ''easy easy to use blendable'') - similarity(comments, ''not easy hard to blend'') AS easy_use_review,
                    similarity(headline, ''pilling separates'') + similarity(comments, ''pilling separates'') AS pilling_review,
                    (similarity(headline, ''many shades shade range'') + similarity(comments, ''many shades shade range'') ) - (similarity(headline, ''limited shade range few shades'') + similarity(comments, ''limited shade range few shades'') ) AS shade_range_review
                FROM clean_reviews
                WHERE product_link_id BETWEEN %L AND %L
            )
            SELECT * 
            FROM reviewer_profile
            LEFT JOIN product_profile 
            ON reviewer_profile.review_link_id = product_profile.product_link_id
        ', start_id, end_id, start_id, end_id);

        -- Update the start_id for the next batch
        start_id := end_id + 1;
           RAISE NOTICE 'batch complete';
        COMMIT;
    END LOOP;
END;
$$;
