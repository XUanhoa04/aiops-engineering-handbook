# AIOps Engineering Handbook

**Production-grade** reference for building Autonomous Intelligent Operations on AWS, Kubernetes, and cloud-native stacks.

| | |
|--|--|
| **Languages** | [Tiếng Việt](vi/00-introduction.vi.md) · [English](en/00-introduction.md) |
| **Chapters** | System Foundations S/S2 · shared sequence 00–17 · Vietnamese production/capstone extension 18–21 |
| **Repo** | [github.com/XUanhoa04/aiops-engineering-handbook](https://github.com/XUanhoa04/aiops-engineering-handbook) |
| **Curriculum** | [CURRICULUM.md](CURRICULUM.md) |

---

## Architecture

![AIOps Platform Pipeline](assets/diagrams/01-aiops-pipeline.png)

![Telemetry Data Plane](assets/diagrams/09-data-plane.png)

![Topology & Change](assets/diagrams/10-topology-change.png)

---

## Learning path

```mermaid
graph LR
    SF[S-S2 System Foundations] --> A[00-01 Foundation]
    A --> B[02-05 Collect]
    B --> C[06 Data plane]
    C --> D[07 Kafka]
    D --> H[08 Topology + Change]
    H --> E[09-13 Intelligence + Action]
    E --> F[14 Production]
    F --> G[15-17 Reuse + Replay]
    G --> I[18 Predictive Ops]
    I --> J[19 Incident Ops]
    J --> K[20 Governance]
    K --> L[21 End-to-End Closed Loop]
    H --> C
```

1. **System foundations** — Core mechanics (S), then advanced failure and evidence reasoning (S2)
2. **Foundation** — Why AIOps, observability thinking
3. **Collect** — OTel, Prometheus, Loki, Tempo
4. **Data plane** — Normalize, enrich, store, feature store (**when to use**)
5. **Transport** — Kafka
6. **Topology & change** — Graph + deploy/change bus feeding enrichment and intelligence
7. **Intelligence + action** — Detect → correlate → RCA → investigate → remediate
8. **Production + reuse** — Production engine, patterns, domain packs and benchmark replay
9. **Proactive operations + governance** — Predict capacity risk, coordinate incidents and control AI authority
10. **End-to-end capstone** — Follow telemetry through baseline, detection, incident, RCA, safe remediation, verification and audit

---

## Start reading

### Tiếng Việt

- [S — System Fundamentals](vi/system-fundamentals/README.vi.md)
- [S2 — System Fundamentals Next](vi/system-fundamentals-next/README.vi.md)
- [00 — Giới thiệu](vi/00-introduction.vi.md)
- [06 — Data Plane](vi/06-data-plane/README.vi.md)
- [08 — Topology & Change](vi/08-topology-change/README.vi.md)
- [18 — Predictive Operations](vi/18-predictive-operations/README.vi.md)
- [19 — Incident Operations](vi/19-incident-operations/README.vi.md)
- [20 — Governance & Model Risk](vi/20-aiops-governance/README.vi.md)
- [21 — AIOps End-to-End Closed Loop](vi/21-end-to-end-aiops/README.vi.md)

### English

- [00 — Introduction](en/00-introduction.md)
- [06 — Data Plane](en/06-data-plane/README.md)
- [08 — Topology & Change](en/08-topology-change/README.md)

---

## Local build

```bash
pip install -r requirements-docs.txt
mkdocs serve
# open http://127.0.0.1:8000
```

Site deploys automatically to GitHub Pages on every push to `main`.
