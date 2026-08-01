# Architecture posters

Các poster Graphviz của handbook được audit và render lại ngày **2026-08-01**. Source được version hóa tại `tools/generate_architecture_diagrams.py`; PNG không còn là artifact “không biết sinh ra từ đâu”. Mermaid vẫn dùng cho timeline, sequence và decision flow nằm sát nội dung từng chapter.

## Chapter map

| File | Decision view | Chapter chính |
|------|---------------|---------------|
| `01-aiops-pipeline.png` | Evidence → stateful intelligence → safe action | 00, 06 |
| `02-observability-pillars.png` | Evidence graph: metrics, logs, traces, synthetics, business SLI, profiles | 01 |
| `11-otel-collection.png` | Thin edge collectors + governed gateways | 02 |
| `12-slo-metrics-engine.png` | Metric contract, SLI, multi-window burn-rate, features | 03 |
| `13-log-evidence.png` | Identity, templates, onset, quality, trace/change links | 04 |
| `14-trace-evidence.png` | Critical path, span-error propagation, coverage | 05 |
| `09-data-plane.png` | Event time, temporal enrichment, quality, revision lineage | 06 |
| `03-kafka-aiops-topics.png` | KRaft transport, data-product topics, isolated consumers | 07 |
| `04-intelligence-layer.png` | Persistent detection, incident state, RCA, investigation | 08 |
| `15-correlation-engine.png` | Dedup, topology/time grouping, overlapping-fault split | 09 |
| `16-rca-engine.png` | First-red, trace propagation, downstream weight, multi-signal rank | 10 |
| `17-investigation-engine.png` | Bounded read-only investigation with provenance | 11 |
| `05-remediation-safety.png` | Proposal, policy gate, canary, verification, rollback | 12 |
| `06-k8s-production.png` | Continuity, durable state, degraded modes, out-of-band page | 13 |
| `18-pattern-library.png` | Pattern contract, acceptance, specialization, lifecycle | 14 |
| `08-payment-critical-path.png` | Payment critical path and domain invariants | 15 |
| `19-benchmark-replay.png` | Deterministic replay and regression gate | 16 |
| `10-topology-change.png` | Temporal topology graph and change ledger | 17 |
| `07-control-vs-data-plane.png` | Business, evidence, decision and safety failure domains | 13, 17 |

## Assumptions cập nhật

- OpenTelemetry signals chính là traces, metrics, logs và baggage; [profiles vẫn Alpha](https://opentelemetry.io/docs/specs/otel/profiles/), nên poster ghi rõ maturity thay vì coi đó là dependency bắt buộc.
- Kubernetes [khuyến nghị Gateway thay cho Ingress và đã freeze Ingress API](https://kubernetes.io/docs/concepts/services-networking/ingress/), nên Gateway API là mặc định greenfield trong poster.
- [Kafka 4.x vận hành hoàn toàn không có ZooKeeper](https://kafka.apache.org/blog/2025/03/18/apache-kafka-4.0.0-release-announcement/); sơ đồ và lệnh quản trị dùng KRaft/`--bootstrap-server`.
- Grafana [Promtail đã EOL ngày 2026-03-02](https://grafana.com/docs/loki/latest/send-data/promtail/); collection path dùng Alloy hoặc OpenTelemetry Collector.
- LLM là thành phần điều tra tùy chọn, không nằm trên critical path của paging hoặc là đường tắt tới remediation.

## Reproduce

Yêu cầu Python, Graphviz `dot` và package trong `requirements-diagrams.txt`:

```text
py -m pip install -r requirements-diagrams.txt
py tools/generate_architecture_diagrams.py
```

Generator kiểm tra mọi edge/note đều trỏ tới node có thật trước khi render, giúp tránh Graphviz âm thầm tạo “phantom node”. Sau khi thay nội dung, cần render lại toàn bộ, xem PNG và chạy `mkdocs build --strict` trước khi commit.
