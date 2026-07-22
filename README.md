# Cẩm nang Kỹ thuật AIOps (AIOps Engineering Handbook)

> **Tài liệu tham chiếu chuẩn sản xuất (production-grade) để xây dựng các nền tảng Vận hành Thông minh Tự động (Autonomous Intelligent Operations) trên AWS, Kubernetes và hạ tầng Cloud Native.**

[![Status](https://img.shields.io/badge/status-active-brightgreen)](.)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Languages](https://img.shields.io/badge/languages-VI%20%7C%20EN-red)](.)
[![Chapters](https://img.shields.io/badge/chapters-16%20%C3%97%202-blue)](docs/)
[![Audience](https://img.shields.io/badge/audience-SRE%20%7C%20DevOps%20%7C%20Platform%20%7C%20ML-orange)](.)
[![GitHub](https://img.shields.io/badge/github-XUanhoa04%2Faiops--engineering--handbook-black)](https://github.com/XUanhoa04/aiops-engineering-handbook)

| | |
|---|---|
| **Languages** | Tiếng Việt (`docs/vi/`) · English (`docs/en/`) |
| **Chapters** | 16 per language (Foundation → Case Studies) |
| **Level** | Staff / Principal SRE |
| **Repo** | [github.com/XUanhoa04/aiops-engineering-handbook](https://github.com/XUanhoa04/aiops-engineering-handbook) |
| **VI content** | [docs/vi/](docs/vi/) |
| **EN content** | [docs/en/](docs/en/) — full translation of the Vietnamese edition |

---

## Handbook này là gì?

Tài liệu ghi nhận **kiến trúc, quyết định thiết kế, thuật toán, thực tiễn vận hành và bài học production** để xây dựng nền tảng AIOps từ nguyên lý cơ bản.

Viết ở cấp độ **Principal Engineer / Staff SRE**. Giả định:

- Bạn quen hệ thống phân tán
- Bạn hiểu Kubernetes và container orchestration
- Bạn có kinh nghiệm vận hành AWS / cloud native
- Bạn muốn hiểu **tại sao (why)**, không chỉ **làm thế nào (how)**

Mỗi chương theo khung: **Why → What → How → Trade-offs → Edge Cases → Problem-Solving → Production Practices → Common Mistakes → Monitoring → Scaling → Security → Cost → Improvement**.

Trọng tâm bản này: **tư duy vận hành** — mental models, decision trees, edge case production, case study Big Tech / e-commerce / banking, và postmortem sự cố công khai. Mục tiêu không chỉ “chạy được code”, mà hiểu **vì sao pipeline AIOps được thiết kế như vậy** và **khi nào nó thất bại**.

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
    M --> N[13 Big Tech AIOps]
    N --> O[14 Ecommerce Banking]
    O --> P[15 Famous Incidents]

    style A fill:#2d3561,color:#fff
    style M fill:#e94560,color:#fff
    style N fill:#0f766e,color:#fff
    style O fill:#0f766e,color:#fff
    style P fill:#0f766e,color:#fff
```

**Lộ trình tư duy (khuyến nghị):**

1. **Nền tảng** (00–01): alert fatigue, OODA, SLO, observability trước AI  
2. **Telemetry** (02–06): thu thập đúng → transport bền; cardinality, lag, sampling  
3. **Intelligence** (07–10): detect → correlate → RCA → LLM; hỏi “khi nào model sai?”  
4. **Action + Production** (11–12): remediation an toàn, dogfood, DR control plane  
5. **Case study thực chiến** (13–15): Big Tech patterns, domain e-com/bank, postmortem  

---

## Table of contents (dual language)

Same 16 chapters in both languages. English is a faithful translation of the Vietnamese edition.

### 📖 Foundation

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 00 | [Introduction](docs/vi/00-introduction.vi.md) | [Introduction](docs/en/00-introduction.md) | AIOps philosophy, OODA, ROI, maturity, edge cases |
| 01 | [Observability](docs/vi/01-observability/README.vi.md) | [Observability](docs/en/01-observability/README.md) | 3 pillars, SLO, cardinality, brownout |

### 📡 Telemetry Stack

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 02 | [OpenTelemetry](docs/vi/02-opentelemetry/README.vi.md) | [OpenTelemetry](docs/en/02-opentelemetry/README.md) | OTLP, Collector SPOF, context propagation |
| 03 | [Prometheus](docs/vi/03-prometheus/README.vi.md) | [Prometheus](docs/en/03-prometheus/README.md) | Pull model, high-cardinality, Thanos |
| 04 | [Loki](docs/vi/04-loki/README.vi.md) | [Loki](docs/en/04-loki/README.md) | Index-labels-only, LogQL, noisy neighbor |
| 05 | [Tempo](docs/vi/05-tempo/README.vi.md) | [Tempo](docs/en/05-tempo/README.md) | Sampling paradox, trace RCA, cost vs coverage |

### 🚌 Transport Layer

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 06 | [Kafka / Kinesis](docs/vi/06-kafka/README.vi.md) | [Kafka / Kinesis](docs/en/06-kafka/README.md) | Backpressure, lag-as-signal, poison message |

### 🧠 Intelligence Layer

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 07 | [Anomaly Detection](docs/vi/07-anomaly-detection/README.vi.md) | [Anomaly Detection](docs/en/07-anomaly-detection/README.md) | Ensemble, drift, when **not** to use ML |
| 08 | [Alert Correlation](docs/vi/08-alert-correlation/README.vi.md) | [Alert Correlation](docs/en/08-alert-correlation/README.md) | Topology stale, cascade vs multi-fail |
| 09 | [Root Cause Analysis](docs/vi/09-root-cause-analysis/README.vi.md) | [Root Cause Analysis](docs/en/09-root-cause-analysis/README.md) | Causation traps, multi-root, time budget |
| 10 | [LLM Investigation Agent](docs/vi/10-llm-agent/README.vi.md) | [LLM Investigation Agent](docs/en/10-llm-agent/README.md) | Hallucination, prompt injection, AI SRE |

### ⚙️ Action Layer

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 11 | [Automated Remediation](docs/vi/11-remediation/README.vi.md) | [Automated Remediation](docs/en/11-remediation/README.md) | Automation paradox, dual-control |

### 🏭 Production

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 12 | [Production Operations](docs/vi/12-production/README.vi.md) | [Production Operations](docs/en/12-production/README.md) | HA/DR, dogfood AIOps, RACI, game days |

### 🌍 Case Studies & Lessons

| # | Tiếng Việt | English | Topic |
|---|------------|---------|--------|
| 13 | [Big Tech AIOps](docs/vi/13-bigtech-aiops/README.vi.md) | [Big Tech AIOps](docs/en/13-bigtech-aiops/README.md) | Google, Netflix, AWS, Meta, Uber |
| 14 | [E-commerce & Banking](docs/vi/14-ecommerce-banking/README.vi.md) | [E-commerce & Banking](docs/en/14-ecommerce-banking/README.md) | BFCM, core banking, PCI, multi-PSP |
| 15 | [Famous Incidents](docs/vi/15-famous-incidents/README.vi.md) | [Famous Incidents](docs/en/15-famous-incidents/README.md) | S3 2017, DynamoDB DNS, Meta 2021, Cloudflare |

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
    PROD --> BIG[13-bigtech-aiops]
    BIG --> DOM[14-ecommerce-banking]
    DOM --> INC[15-famous-incidents]

    OBS --> PROM
    OBS --> LOKI
    OBS --> TEMPO
    PROM --> AD
    AD --> LLM
    INC -.->|game days| PROD
    BIG -.->|patterns| AD
```

---

## How to use / Cách dùng

> For each section, answer three questions before continuing: (1) What real problem is this solving? (2) What is the trade-off? (3) Which edge case breaks this design?

Pick **[English](docs/en/)** or **[Tiếng Việt](docs/vi/)** — same chapter numbers.

### DevOps / SRE
EN: [Observability](docs/en/01-observability/README.md) → [Prometheus](docs/en/03-prometheus/README.md) → [Kafka](docs/en/06-kafka/README.md) → [Remediation](docs/en/11-remediation/README.md) → [Incidents](docs/en/15-famous-incidents/README.md)  
VI: [Observability](docs/vi/01-observability/README.vi.md) → … (same order under `docs/vi/`)

### Platform Engineer
EN: [OpenTelemetry](docs/en/02-opentelemetry/README.md) → [Prometheus](docs/en/03-prometheus/README.md) → [Loki](docs/en/04-loki/README.md) → [Tempo](docs/en/05-tempo/README.md) → [Production](docs/en/12-production/README.md)

### ML Engineer
EN: [Anomaly Detection](docs/en/07-anomaly-detection/README.md) → [Alert Correlation](docs/en/08-alert-correlation/README.md) → [RCA](docs/en/09-root-cause-analysis/README.md) → [LLM Agent](docs/en/10-llm-agent/README.md) → [Big Tech](docs/en/13-bigtech-aiops/README.md)

### Cloud Architect / Tech Lead
EN: [Introduction](docs/en/00-introduction.md) → [Production](docs/en/12-production/README.md) → [Big Tech](docs/en/13-bigtech-aiops/README.md) → [E-commerce & Banking](docs/en/14-ecommerce-banking/README.md)

### On-call / Incident Commander
EN: [Famous Incidents](docs/en/15-famous-incidents/README.md) → [Alert Correlation](docs/en/08-alert-correlation/README.md) → [RCA](docs/en/09-root-cause-analysis/README.md) → [Remediation](docs/en/11-remediation/README.md)

---

## Tech Stack Reference

| Lớp | Giải pháp chính | Thay thế | AWS Managed |
|-----|-----------------|----------|-------------|
| Metrics | Prometheus | VictoriaMetrics | CloudWatch |
| Logs | Loki | ELK Stack | CloudWatch Logs |
| Traces | Tempo | Jaeger | AWS X-Ray |
| Collection | OpenTelemetry Collector | Fluent Bit | FireLens |
| Streaming | Apache Kafka | Redis Streams | Kinesis / MSK |
| Storage | S3 + Parquet | Thanos | S3 |
| ML Inference | Python (scikit-learn) | TorchServe | SageMaker |
| LLM | Claude / GPT-4 | Llama 3 (self-host) | Amazon Bedrock |
| Remediation | AWS SSM Automation | Rundeck | SSM / Lambda |
| Visualization | Grafana | Kibana | CloudWatch Dashboards |
| Alerting | Alertmanager | Grafana Alerting | CloudWatch Alarms |

---

## Contributing

Mỗi chương nên đạt:

- **Độ chính xác kỹ thuật** — bám thực tiễn production / tài liệu public
- **Độ sâu** — cấp Staff/Principal, có trade-off rõ
- **Edge cases** — khi thiết kế vỡ và cách phòng
- **Production-ready** — monitoring, scaling, security, cost

Issue / PR: [github.com/XUanhoa04/aiops-engineering-handbook](https://github.com/XUanhoa04/aiops-engineering-handbook)

---

## License

MIT License — xem [LICENSE](LICENSE).

---

## Maintainers

- **[@XUanhoa04](https://github.com/XUanhoa04)** — AIOps / SRE / Cloud Native handbook
