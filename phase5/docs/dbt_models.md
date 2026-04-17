# dbt Models — Taxi Analytics

## Project Structure
taxi_analytics/
├── models/
│   ├── staging/
│   │   └── stg_taxi_trips.sql      — bronze layer, standardized raw data
│   └── marts/
│       ├── daily_revenue.sql       — gold layer, daily aggregations
│       └── payment_summary.sql     — gold layer, payment method analysis

## Staging Models

### stg_taxi_trips
**Materialization:** View
**Source:** NYC TLC Yellow Taxi clean Parquet files (Jan-Feb 2024)
**Description:** Standardized and cleaned taxi trip data. Applies payment type labels,
retains all derived columns from Phase 1 cleaning.

**Columns:**
| Column | Type | Description |
|---|---|---|
| pickup_datetime | timestamp | Trip start time |
| dropoff_datetime | timestamp | Trip end time |
| duration_minutes | float | Trip duration in minutes |
| trip_distance | float | Distance in miles |
| passenger_count | int | Number of passengers |
| pickup_location_id | int | TLC zone ID for pickup location |
| dropoff_location_id | int | TLC zone ID for dropoff location |
| fare_amount | float | Metered fare in USD |
| tip_amount | float | Tip amount in USD (credit card only) |
| tolls_amount | float | Tolls in USD |
| total_amount | float | Total charge in USD |
| tip_pct | float | Tip as percentage of fare |
| payment_method | string | Human readable payment type |
| pickup_hour | int | Hour of pickup (0-23) |
| pickup_day | string | Day of week name |
| pickup_month | int | Month number (1=January, 2=February) |

**Payment Method Values:**
- flex_fare — Dynamic pricing trips (payment_type=0)
- credit_card — Credit card payment (payment_type=1)
- cash — Cash payment (payment_type=2)
- no_charge — No charge trips (payment_type=3)
- dispute — Disputed trips (payment_type=4)
- unknown — Unknown payment (payment_type=5)
- voided — Voided trips (payment_type=6)

**Tests:**
- not_null on pickup_datetime, dropoff_datetime, fare_amount, trip_distance, payment_method
- accepted_values on payment_method
- accepted_values on pickup_month (1, 2 only)

## Mart Models

### daily_revenue
**Materialization:** Table
**Source:** stg_taxi_trips
**Description:** Daily aggregated revenue and trip metrics. One row per calendar day.
Primary table for revenue trend analysis and dashboard queries.

**Columns:**
| Column | Type | Description |
|---|---|---|
| trip_date | date | Calendar date |
| pickup_month | int | Month number |
| pickup_day | string | Day of week |
| total_trips | int | Number of trips that day |
| total_fare | float | Sum of fare amounts |
| total_tips | float | Sum of tip amounts |
| total_revenue | float | Sum of total charges |
| avg_fare | float | Average fare per trip |
| avg_distance | float | Average trip distance in miles |
| avg_duration_mins | float | Average trip duration in minutes |
| overall_tip_pct | float | Tips as % of total fare |

**Key Statistics (Jan-Feb 2024):**
- Daily trip range: 25,896 to 153,260
- Daily revenue range: $742,901 to $4,946,709
- Average daily trips: 119,561
- Average fare: $21.66

**Data Quality Tests:**
- total_trips between 20,000 and 184,000
- total_revenue between $600,000 and $5,900,000
- avg_fare between $15 and $32
- No future trip dates

### payment_summary
**Materialization:** Table
**Source:** stg_taxi_trips
**Description:** Payment method breakdown by month. Shows trip volume,
revenue, and tip behavior per payment type per month.

**Columns:**
| Column | Type | Description |
|---|---|---|
| pickup_month | int | Month number |
| payment_method | string | Payment type label |
| total_trips | int | Trips using this payment method |
| total_fare | float | Total fare for this payment method |
| avg_tip | float | Average tip amount |
| avg_tip_pct | float | Average tip as % of fare |
| pct_of_monthly_trips | float | Share of monthly trip volume |

**Key Findings:**
- Credit card: ~67% of trips, 21% average tip rate
- Flex fare: ~31% of trips, 1.5% average tip rate
- Cash: ~9% of trips, 0% tip rate (tips not recorded for cash)
- Tips analysis only meaningful for credit card transactions