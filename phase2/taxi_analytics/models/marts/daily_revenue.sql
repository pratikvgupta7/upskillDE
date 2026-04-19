WITH trips AS (
    SELECT * FROM {{ref('stg_taxi_trips')}}
)

SELECT
    DATE_TRUNC('day', pickup_datetime::TIMESTAMP)      AS trip_date,
    pickup_month,
    pickup_day,
    count(*)                                AS total_trips,
    round(sum(fare_amount), 2)              AS total_fare,
    round(sum(tip_amount), 2)               AS total_tips,
    round(sum(total_amount), 2)             AS total_revenue,
    round(avg(fare_amount), 2)              AS avg_fare,
    round(avg(trip_distance), 2)            AS avg_distance,
    round(avg(duration_minutes), 2)         AS avg_duration_mins,
    round(sum(tip_amount) / 
          NULLIF(sum(fare_amount), 0) * 100, 2)  AS overall_tip_pct

FROM trips
GROUP BY
    DATE_TRUNC('day', pickup_datetime::TIMESTAMP),
    pickup_month,
    pickup_day
ORDER BY trip_date