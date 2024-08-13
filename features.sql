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
        black_review FLOAT,
        white_review FLOAT,
        tan_review FLOAT,
        redness_review FLOAT,
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
        black FLOAT,
        white FLOAT,
        tan FLOAT,
        redness FLOAT,
        light_coverage FLOAT,
        medium_coverage FLOAT,
        full_coverage FLOAT,
        sheer_finish FLOAT, 
        glowy_finish FLOAT, 
        matte_finish FLOAT, 
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
                        similarity(concat(describe_yourself, '' '', description), ''acne oily sensitive skin zits blemishes pores'') + similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''acne oily sensitive skin zits blemishes pores'') AS acne,
                        similarity(concat(describe_yourself, '' '', description), ''dry sensitive skin'') AS dry,
                        similarity(concat(describe_yourself, '' '', description), ''wrinkles'') AS wrinkles, 
                        similarity(concat(describe_yourself, '' '', description), ''black deep african american'') AS black, 
                        similarity(concat(describe_yourself, '' '', description), ''fair pale light skin freckles white caucasian'') AS white, 
                        similarity(concat(describe_yourself, '' '', description), ''tan olive skin latina south asian brown asian'') AS tan, 
                        similarity(concat(describe_yourself, '' '', description), ''redness rosacea'') + similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''redness rosacea'') AS redness,
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''light coverage natural skin like long lasting'') AS light_coverage,
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''medium coverage buildable coverage long lasting'') AS medium_coverage,
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''full coverage full face glam even coverage long lasting'') AS full_coverage,
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description) , ''natural sheer lightweight light'')  AS sheer_finish,
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description) , ''hydrating glowy radiant illuminating luminous dewy'')  AS glowy_finish, 
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description) , ''matte no-shine velvety air brushed no oil'')  AS matte_finish,  
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''expensive pricey'') AS expensive, 
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''inexpensive budget friendly drugstore'') AS inexpensive, 
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''wrinkles hyperpigmentation acne'') AS skin_concerns,  
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''comfortable lightweight breathable'') AS comfortable_wear, 
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''easy easy to use blendable'') AS easy_use, 
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''pilling separates'') AS pilling,
                        similarity(concat(pros, '' '', faceoff_positive, '' '', best_uses, '' '', description), ''many shades shade range'') AS shade_range
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
                        similarity(headline, ''working mom working mother working parent'') + similarity(comments, ''working mom working mother working parent'') AS mother_review,
                        similarity(headline, ''mature professional active'') + similarity(comments, ''mature professional active'') AS professional_review, 
                        similarity(headline, ''energetic trendy youthful'') + similarity(comments, ''energetic trendy youthful'') AS vibe_review, 
                        similarity(headline, ''acne oily sensitive skin zits blemishes pores'') + similarity(comments, ''acne oily sensitive skin zits blemishes pores'') AS acne_review,
                        similarity(headline, ''dry sensitive skin'') + similarity(comments, ''dry sensitive skin'') AS dry_review,
                        similarity(headline, ''wrinkles'') + similarity(comments, ''wrinkles'') AS wrinkles_review, 
                        similarity(headline, ''black deep african american'') + similarity(comments, ''black deep african american'') AS black_review, 
                        similarity(headline, ''fair pale light skin freckles white caucasian'') + similarity(comments, ''fair pale light skin freckles white caucasian'') AS white_review, 
                        similarity(headline, ''tan olive skin latina south asian brown asian'') + similarity(comments, ''tan olive skin latina south asian brown asian'') AS tan_review, 
                        similarity(headline, ''redness rosacea'') + similarity(comments, ''redness rosacea'') AS redness_review,
                        similarity(headline, ''light coverage natural skin like long lasting'') + similarity(comments, ''light coverage natural skin like long lasting'') AS light_coverage_review,
                        similarity(headline, ''medium coverage buildable coverage long lasting'') + similarity(comments, ''medium coverage buildable coverage long lasting'') AS medium_coverage_review,
                        similarity(headline, ''full coverage full face glam even coverage long lasting'') + similarity(comments, ''full coverage full face glam even coverage long lasting'') AS full_coverage_review,
                        similarity(headline, ''expensive pricey'') + similarity(comments, ''expensive pricey'') AS expensive_review, 
                        similarity(headline, ''inexpensive budget friendly drugstore'') + similarity(comments, ''inexpensive budget friendly drugstore'') AS inexpensive_review, 
                        similarity(headline, ''wrinkles hyperpigmentation acne'') + similarity(comments, ''wrinkles hyperpigmentation acne'') AS skin_concerns_review,  
                        similarity(headline, ''comfortable lightweight breathable'') + similarity(comments, ''comfortable lightweight breathable'') AS comfortable_wear_review, 
                        similarity(headline, ''easy easy to use blendable'') + similarity(comments, ''easy easy to use blendable'') AS easy_use_review,
                        similarity(headline, ''pilling separates'') + similarity(comments, ''pilling separates'') AS pilling_review,
                        similarity(headline, ''many shades shade range'') + similarity(comments, ''many shades shade range'') AS shade_range_review
                    FROM clean_reviews WHERE product_link_id BETWEEN %L AND %L
                )
                SELECT 
                    reviewer_profile.*,
                    product_profile.*
                FROM reviewer_profile
                JOIN product_profile ON reviewer_profile.review_link_id = product_profile.product_link_id
            ', start_id, end_id, start_id, end_id);
        COMMIT;

        start_id := end_id + 1;
    END LOOP;
END;
$$;
