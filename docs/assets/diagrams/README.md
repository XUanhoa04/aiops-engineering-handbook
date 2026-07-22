# Architecture posters (PNG)

Hero architecture diagrams for the AIOps Engineering Handbook.

| File | Topic | Used in |
|------|--------|---------|
| `01-aiops-pipeline.png` | End-to-end AIOps platform | Ch.00, README |
| `02-observability-pillars.png` | Metrics / Logs / Traces correlation | Ch.01 |
| `03-kafka-aiops-topics.png` | Kafka / MSK transport topics | Ch.06 |
| `04-intelligence-layer.png` | Detect → correlate → RCA → LLM | Ch.07–10 |
| `05-remediation-safety.png` | Safety gates + allow-listed actions | Ch.11 |
| `06-k8s-production.png` | K8s production sketch | Ch.12 |
| `07-control-vs-data-plane.png` | Resilience / break-glass | Ch.12, Ch.15 |
| `08-payment-critical-path.png` | Checkout / payment path | Ch.14 |

**Notes**

- Images only are versioned in git (no Diagrams Python sources).
- Generated with [Diagrams](https://diagrams.mingrammer.com/) + Graphviz for icon-rich cloud architecture views.
- Flowcharts, sequences, gantt, and decision trees remain **Mermaid** inside chapters.
- Prefer these PNGs for slides, README, and “hero” architecture sections.
