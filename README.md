# AIOps Engineering Handbook

> **A production-grade reference for building Autonomous Intelligent Operations platforms on AWS, Kubernetes, and Cloud Native infrastructure.**

[![Status](https://img.shields.io/badge/status-active-brightgreen)](.)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Audience](https://img.shields.io/badge/audience-SRE%20%7C%20DevOps%20%7C%20Platform%20Engineer%20%7C%20ML%20Engineer-orange)](.)

---

## What Is This Handbook?

This handbook documents the **complete architecture, design decisions, algorithms, operational practices, and production lessons** for building an AIOps platform from first principles.

It is written at the **Principal Engineer / Staff SRE** level. It assumes:

- You are comfortable with distributed systems
- You understand Kubernetes and container orchestration
- You have operational AWS experience
- You want to understand **why**, not just **how**

Each chapter covers: **Why → What → How → Trade-offs → Production Best Practices → Common Mistakes → Monitoring → Scaling → Security → Cost → Improvement**.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph Sources["Data Sources"]
        SVC[Microservices]
        K8S[Kubernetes]
        AWS[AWS Services]
        INFRA[Infrastructure]
    end

    subgraph Collection["Collection Layer"]
        OTC[OpenTelemetry Collector]
        PROM[Prometheus]
        LOKI[Loki]
        TEMPO[Tempo]
    end

    subgraph Transport["Transport Layer"]
        KAFKA[Apache Kafka / AWS MSK]
    end

    subgraph Intelligence["AIOps Intelligence Layer"]
        AD[Anomaly Detection Engine]
        AC[Alert Correlation Engine]
        RCA[Root Cause Analysis]
        LLM[LLM Investigation Agent]
    end

    subgraph Action["Action Layer"]
        DE[Decision Engine]
        REM[Remediation Engine]
        KB[Knowledge Base]
    end

    subgraph Observe["Observability"]
        GRF[Grafana]
        AM[Alertmanager]
        PD[PagerDuty / Slack]
    end

    Sources --> Collection
    Collection --> Transport
    Transport --> Intelligence
    Intelligence --> Action
    Action --> Observe
    Action --> Sources

    style Sources fill:#1a1a2e,color:#e0e0e0
    style Collection fill:#16213e,color:#e0e0e0
    style Transport fill:#0f3460,color:#e0e0e0
    style Intelligence fill:#533483,color:#e0e0e0
    style Action fill:#e94560,color:#fff
    style Observe fill:#1a1a2e,color:#e0e0e0
```

---

## Learning Roadmap

```mermaid
graph LR
    A[00 Introduction] --> B[01 Observability]
    B --> C[02 OpenTelemetry]
    C --> D[03 Prometheus]
    C --> E[04 Loki]
    C --> F[05 Tempo]
    D --> G[06 Kafka]
    E --> G
    F --> G
    G --> H[07 Anomaly Detection]
    H --> I[08 Alert Correlation]
    I --> J[09 Root Cause Analysis]
    J --> K[10 LLM Agent]
    K --> L[11 Remediation]
    L --> M[12 Production]

    style A fill:#2d3561,color:#fff
    style M fill:#e94560,color:#fff
```

---

## Table of Contents

### 📖 Foundation

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 00 | [Introduction](docs/00-introduction.md) | AIOps philosophy, ROI, maturity model | ✅ Done |
| 01 | [Observability](docs/01-observability/README.md) | Three Pillars, Metric types, Logs, Traces, SLO/SLA, Cardinality | ✅ Done |

### 📡 Telemetry Stack

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 02 | [OpenTelemetry](docs/02-opentelemetry/README.md) | OTLP protocol, Collector architecture, all receivers/processors/exporters | ✅ Done |
| 03 | [Prometheus](docs/03-prometheus/README.md) | TSDB internals, PromQL, HA, Thanos, CloudWatch vs VictoriaMetrics | ✅ Done |
| 04 | [Loki](docs/04-loki/README.md) | Architecture, LogQL deep-dive, S3 backend, ELK comparison, cost | ✅ Done |
| 05 | [Tempo](docs/05-tempo/README.md) | Parquet storage, TraceQL, SpanMetrics, Jaeger/X-Ray comparison | ✅ Done |

### 🚌 Transport Layer

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 06 | [Kafka / Kinesis](docs/06-kafka/README.md) | Producer/consumer, EOS, MSK, Kinesis vs Kafka, DLQ, Schema Registry | ✅ Done |

### 🧠 Intelligence Layer

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 07 | [Anomaly Detection](docs/07-anomaly-detection/README.md) | 12 algorithms: EWMA→STL→IF→LSTM→Transformer→Drain→DeepLog, ensemble, production | ✅ Done |
| 08 | [Alert Correlation](docs/08-alert-correlation/README.md) | 5-stage pipeline, topology correlation, temporal cross-correlation, semantic similarity | ✅ Done |
| 09 | [Root Cause Analysis](docs/09-root-cause-analysis/README.md) | Topology traversal, PC algorithm, Bayesian network, GNN (MicroRCA), trace+log analysis | ✅ Done |
| 10 | [LLM Investigation Agent](docs/10-llm-agent/README.md) | RAG, LangGraph/ReAct, tool use, SRE prompting, safety gates, HITL, cost analysis | ✅ Done |

### ⚙️ Action Layer

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 11 | [Automated Remediation](docs/11-remediation/README.md) | Action catalog (Tier 1-3), K8s executor, SSM, canary rollout, safety gates, audit log | ✅ Done |

### 🏭 Production

| # | Document | Description | Status |
|---|----------|-------------|--------|
| 12 | [Production Operations](docs/12-production/README.md) | HA, DR, chaos engineering, cost governance (~$9,364/month), security, 49x ROI analysis | ✅ Done |

---

## Document Dependency Graph

```mermaid
graph TD
    INTRO[00-introduction] --> OBS[01-observability]
    OBS --> OTEL[02-opentelemetry]
    OTEL --> PROM[03-prometheus]
    OTEL --> LOKI[04-loki]
    OTEL --> TEMPO[05-tempo]
    PROM --> KAFKA[06-kafka]
    LOKI --> KAFKA
    TEMPO --> KAFKA
    KAFKA --> AD[07-anomaly-detection]
    AD --> AC[08-alert-correlation]
    AC --> RCA[09-root-cause-analysis]
    RCA --> LLM[10-llm-agent]
    LLM --> REM[11-remediation]
    REM --> PROD[12-production]

    OBS --> PROM
    OBS --> LOKI
    OBS --> TEMPO
    PROM --> AD
    AD --> LLM
```

---

## Repository Progress

```
Foundation          ████████████████████  100% (2/2)   ✅
Telemetry Stack     ████████████████████  100% (4/4)   ✅
Transport Layer     ████████████████████  100% (1/1)   ✅
Intelligence Layer  ████████████████████  100% (4/4)   ✅
Action Layer        ████████████████████  100% (1/1)   ✅
Production          ████████████████████  100% (1/1)   ✅

Overall Progress    ████████████████████  100% (13/13 chapters)  🎉 COMPLETE
```

---

## How to Use This Handbook

### If you are a **DevOps/SRE Engineer**
Start with [Observability](docs/01-observability/README.md) → [Prometheus](docs/03-prometheus/README.md) → [Kafka](docs/06-kafka/README.md) → [Remediation](docs/11-remediation/README.md)

### If you are a **Platform Engineer**
Start with [OpenTelemetry](docs/02-opentelemetry/README.md) → [Prometheus](docs/03-prometheus/README.md) → [Loki](docs/04-loki/README.md) → [Tempo](docs/05-tempo/README.md)

### If you are an **ML Engineer**
Start with [Anomaly Detection](docs/07-anomaly-detection/README.md) → [Alert Correlation](docs/08-alert-correlation/README.md) → [RCA](docs/09-root-cause-analysis/README.md) → [LLM Agent](docs/10-llm-agent/README.md)

### If you are a **Cloud Architect**
Start with [Introduction](docs/00-introduction.md) → [Production](docs/12-production/README.md) → [Kafka/MSK](docs/06-kafka/README.md)

---

## Tech Stack Reference

| Layer | Primary | Alternative | AWS Managed |
|-------|---------|-------------|-------------|
| Metrics | Prometheus | VictoriaMetrics | CloudWatch |
| Logs | Loki | ELK Stack | CloudWatch Logs |
| Traces | Tempo | Jaeger | AWS X-Ray |
| Collection | OpenTelemetry Collector | Fluent Bit | FireLens |
| Streaming | Apache Kafka | Redis Streams | AWS Kinesis / MSK |
| Storage | S3 + Parquet | Thanos | S3 |
| ML Inference | Python (scikit-learn) | TorchServe | SageMaker |
| LLM | Claude / GPT-4 | Llama 3 (self-hosted) | Amazon Bedrock |
| Remediation | AWS SSM Automation | Rundeck | SSM / Lambda |
| Visualization | Grafana | Kibana | CloudWatch Dashboards |
| Alerting | Alertmanager | Grafana Alerting | CloudWatch Alarms |

---

## Contributing

This is an evolving document. Each chapter follows the same quality bar:
- **Technical Accuracy**: Verified against production deployments
- **Depth**: Principal Engineer level, no hand-waving
- **Trade-offs**: Every architectural decision is justified
- **Production-Ready**: Includes failure modes, monitoring, scaling


