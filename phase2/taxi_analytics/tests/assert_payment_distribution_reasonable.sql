-- Fails if payment method trip counts fall outside expected ranges
-- Based on Jan-Feb 2024 observed data with 20% buffer

SELECT
    pickup_month,
    payment_method,
    total_trips
FROM {{ ref('payment_summary') }}
WHERE
    -- credit card should always dominate
    (payment_method = 'credit_card' AND total_trips < 1640000)   -- 20% below min
    OR (payment_method = 'credit_card' AND total_trips > 2700000) -- 20% above max

    -- flex fare second largest
    OR (payment_method = 'flex_fare' AND total_trips < 818000)
    OR (payment_method = 'flex_fare' AND total_trips > 1305000)

    -- cash
    OR (payment_method = 'cash' AND total_trips < 213000)
    OR (payment_method = 'cash' AND total_trips > 365000)