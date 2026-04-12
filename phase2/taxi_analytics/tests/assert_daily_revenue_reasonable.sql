-- Fails if any day has suspiciously high or low trip counts
-- Historical range from Jan-Feb 2024: 25,896 to 153,260
-- Thresholds set at 20% buffer outside observed range

SELECT
    trip_date,
    total_trips,
    total_revenue,
    avg_fare
FROM {{ ref('daily_revenue') }}
WHERE total_trips > 184000          -- 20% above observed max of 153,260
   OR total_trips < 20000           -- 20% below observed min of 25,896
   OR total_revenue > 5900000       -- 20% above observed max of 4,946,709
   OR total_revenue < 600000        -- 20% below observed min of 742,901
   OR avg_fare > 32                 -- 20% above observed max of 26.23
   OR avg_fare < 15                 -- 20% below observed min of 19.08