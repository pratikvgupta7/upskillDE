-- Fails if any trips have pickup dates in the future
-- Simple sanity check that catches timestamp corruption

SELECT
    trip_date,
    total_trips
FROM {{ ref('daily_revenue') }}
WHERE trip_date > CURRENT_DATE