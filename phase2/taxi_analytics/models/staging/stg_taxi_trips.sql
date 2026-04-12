WITH source AS 
(SELECT * FROM {{source('raw_taxi', 'trips')}}),
cleaned AS (
    SELECT
        -- timestamps
        pickup_datetime,
        dropoff_datetime,
        duration_minutes,

        -- trip details
        trip_distance,
        passenger_count,
        pickup_location_id,
        dropoff_location_id,

        -- financials
        fare_amount,
        tip_amount,
        tolls_amount,
        total_amount,
        tip_pct,

        -- categoricals
        CASE payment_type
            WHEN 0 THEN 'flex_fare'
            WHEN 1 THEN 'credit_card'
            WHEN 2 THEN 'cash'
            WHEN 3 THEN 'no_charge'
            WHEN 4 THEN 'dispute'
            WHEN 5 THEN 'unknown'
            WHEN 6 THEN 'voided'
        END                             AS payment_method,

        -- time dimensions
        pickup_hour,
        pickup_day,
        pickup_month

    FROM source
)

SELECT * FROM cleaned