{% call statement('disable_optimizer') %}
    PRAGMA disable_optimizer
{% endcall %}

WITH trips AS (
    SELECT * FROM {{ref('stg_taxi_trips')}}
)

SELECT
    pickup_month,
    payment_method,
    count(*)                                AS total_trips,
    round(sum(fare_amount), 2)              AS total_fare,
    round(avg(tip_amount), 2)               AS avg_tip,
    round(avg(tip_amount) / 
          NULLIF(avg(fare_amount), 0) * 100, 2)  AS avg_tip_pct,
    round(count(*) * 100.0 / 
          sum(count(*)) OVER 
          (PARTITION BY pickup_month), 2)   AS pct_of_monthly_trips

FROM trips
GROUP BY pickup_month, payment_method
ORDER BY pickup_month, total_trips DESC