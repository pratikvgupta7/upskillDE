# Modern Data Engineering Stack

End-to-end data engineering project built to demonstrate modern stack proficiency.
Built from scratch over 6 weeks as a deliberate upskilling project.

## Architecture

[Architecture diagram goes here]

## Stack

| Layer | Technology | Purpose |
|---|---|---|
| Ingestion | DuckDB + Polars | Local analytical pipeline |
| Orchestration | Dagster + dbt | Scheduling, testing, lineage |
| Streaming | Redpanda + Flink | Real-time event processing |
| Storage | Apache Iceberg + MinIO | Open lakehouse format |
| AI/RAG | Qdrant + GPT-4o-mini | Semantic search over docs |
| Infrastructure | Docker Compose | Local development stack |

## Phases

### Phase 1 — Local Foundation
- 7M row NYC Taxi dataset cleaned with DuckDB
- Data quality investigation — recovered 2.1M rows from incorrect filter assumption
- Partitioned Parquet output by month

### Phase 2 — Orchestration
- dbt staging and mart models with 10 automated tests
- Dagster asset-based orchestration with full lineage
- Singular tests with real thresholds based on actual data distribution

### Phase 3 — Streaming
- Dual-event streaming pipeline (trip_started / trip_ended)
- Partition affinity via message keys — eliminated orphaned events
- Flink SQL interval join with bounded state
- Python consumer with orphan tracking and health monitoring

### Phase 4 — Lakehouse
- Apache Iceberg table on MinIO (local S3)
- Time travel across snapshots
- Multi-engine queries — PyIceberg, DuckDB, Spark all reading same table
- Persistent REST catalog with SQLite backend

### Phase 5 — GenAI Infrastructure
- RAG pipeline over project documentation
- Local embeddings with sentence-transformers
- Qdrant vector store with cosine similarity
- Evaluation harness — Recall@5 and answer accuracy

## Running Locally

### Prerequisites
- Docker Desktop
- Python 3.11+
- DuckDB CLI

### Start the stack
```bash
cd phase3
docker compose up -d
```

### Run individual phases
```bash
# Phase 1
cd phase1 && python clean.py

# Phase 2
cd phase2/taxi_analytics && dbt build

# Phase 3
cd phase3 && python producer.py

# Phase 4
cd phase4 && python write_iceberg.py

# Phase 5
cd phase5 && python embed.py && python query.py
```

## Key Technical Decisions

**DuckDB over Spark for local analytics** — for sub-100M row datasets on a single machine DuckDB is faster, simpler, and requires no cluster setup. Spark is reserved for distributed processing.

**Dagster over Airflow** — asset-based orchestration makes data lineage a first-class concern. Tasks know what they produce, not just what they do. This matters for debugging and impact analysis.

**Redpanda over Kafka** — Kafka-compatible, single binary, no Zookeeper. Identical API means production migration requires only a bootstrap server change.

**Iceberg over Delta Lake** — vendor-neutral format with native support across Spark, Flink, DuckDB, Trino, and Athena. Data is not locked to any single engine or vendor.

**Local embeddings over OpenAI** — sentence-transformers runs on CPU with no API cost. For production with strict latency requirements, OpenAI embeddings would be preferred.