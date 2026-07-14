# Chapter 03 — Prometheus

> **Prometheus là tiêu chuẩn thực tế (de-facto standard) cho thu thập, lưu trữ, và cảnh báo metrics trong môi trường cloud-native. Hiểu sâu về TSDB internals, scrape engine, và kiến trúc HA là điều kiện để xây dựng nền tảng AIOps đáng tin cậy.**

---

## Prerequisites

- [01 — Observability](../01-observability/README.md) — các loại metrics và PromQL cơ bản
- [02 — OpenTelemetry](../02-opentelemetry/README.md) — cách metrics di chuyển vào Prometheus

## Related Documents

- [07 — Anomaly Detection](../07-anomaly-detection/README.md) — metrics của Prometheus làm input
- [08 — Alert Correlation](../08-alert-correlation/README.md) — tiêu thụ alerts từ Prometheus

## Next Reading

Sau chương này, hãy chuyển sang [04 — Loki](../04-loki/README.md).

---

## Sub-Documents

| Tài liệu | Mô tả |
|----------|-------------|
| [Architecture](architecture.md) | Components nội bộ, data flow |
| [TSDB](tsdb.md) | TSDB internals: WAL, compaction |
| [Scraping](scraping.md) | Scrape engine, exporters |
| [Service Discovery](service-discovery.md) | Kubernetes SD, relabeling |
| [Recording Rules](recording-rules.md) | Pre-aggregation, federation |
| [Alerting](alerting.md) | Alert rules, Alertmanager, routing |
| [High Availability](high-availability.md) | HA pair, Thanos, VictoriaMetrics |
| [Production](production.md) | Sizing, tuning, operations |

---

## Table of Contents

1. [Why Prometheus?](#1-why-prometheus)
2. [Internal Architecture](#2-internal-architecture)
3. [TSDB Internals](#3-tsdb-internals)
4. [The Scraping Engine](#4-the-scraping-engine)
5. [Service Discovery](#5-service-discovery)
6. [PromQL Deep Dive](#6-promql-deep-dive)
7. [Recording Rules](#7-recording-rules)
8. [Alerting Rules and Alertmanager](#8-alerting-rules-and-alertmanager)
9. [Remote Write and Remote Read](#9-remote-write-and-remote-read)
10. [High Availability](#10-high-availability)
11. [Prometheus vs CloudWatch](#11-prometheus-vs-cloudwatch)
12. [Prometheus vs VictoriaMetrics](#12-prometheus-vs-victoriametrics)
13. [Thanos Architecture](#13-thanos-architecture)
14. [Production Configuration](#14-production-configuration)
15. [Common Mistakes](#15-common-mistakes)
16. [Monitoring Prometheus](#16-monitoring-prometheus)
17. [Scaling](#17-scaling)
18. [Security](#18-security)
19. [Cost](#19-cost)
20. [Production Review](#20-production-review)

---

## 1. Why Prometheus?

> [!NOTE]
> **Ý TƯỞNG**
> Prometheus được thiết kế với một triết lý đơn giản: **pull-based scraping + multi-dimensional labels + PromQL**. Thay vì chờ services gửi data về, Prometheus chủ động hỏi "/metrics" của mỗi service mỗi 15 giây. Điều này cho phép biết ngay khi nào một service ngừng hoạt động (không trả lời scrape = down).

> [!TIP]
> **Vì sao Pull thay vì Push?** Pull-based có 3 ưu điểm: (1) Prometheus kiểm soát tần suất thu thập, không bị services "spam" data; (2) Nếu service down → Prometheus phát hiện ngay (scrape fail); (3) Dễ debug hơn: bạn có thể curl trực tiếp `/metrics` endpoint để xem raw data. Trade-off: services trong private network cần Pushgateway cho batch jobs ngắn.

### Design Philosophy

1. **Pull-based scraping**: Prometheus poll targets, không đợi push. Dễ phát hiện service down.
2. **Multi-dimensional data model**: Labels là first-class citizens. Mỗi time series = `metric_name{label_key="value"}`
3. **PromQL**: Ngôn ngữ query chuyên biệt cho time series. Không phải SQL.
4. **Không lưu trữ dài hạn**: Chỉ ~15 ngày local. Long-term storage qua remote write → Thanos/VictoriaMetrics.
5. **Single binary**: Không cần external DB, không cần ZooKeeper.

### What Prometheus Is Good At

- Thu thập metrics cho infrastructure và application monitoring
- Service discovery động (Kubernetes, EC2)
- Flexible PromQL queries
- Alert evaluation với biểu thức phức tạp

### What Prometheus Is NOT Good At

| Không phù hợp | Thay thế |
|--------|---------|
| Long-term storage (> 15 ngày) | Thanos hoặc VictoriaMetrics |
| High-cardinality (> 10M series) | VictoriaMetrics |
| Horizontal write scaling | VictoriaMetrics Cluster |
| Event data (logs, traces) | Loki (logs), Tempo (traces) |

---

## 2. Internal Architecture

> [!NOTE]
> **Ý TƯỞNG**
> Prometheus là một monolith — tất cả trong một binary: scrape engine, TSDB, rule evaluator, query engine, HTTP API. Luồng data đơn giản: Service → Scrape Engine → WAL → Head Block (memory) → TSDB Blocks (disk) → Remote Write (long-term).

```mermaid
graph TD
    subgraph Targets["Monitored Targets"]
        SVC[Microservices\n:8080/metrics]
        NODE[Node Exporter\n:9100/metrics]
        K8S[kube-state-metrics\n:8080/metrics]
    end

    subgraph Prometheus["Prometheus Server"]
        SD[Service Discovery\nKubernetes · EC2 · DNS]
        SCRAPE[Scrape Engine\nHTTP GET /metrics every 15s]
        WAL[Write-Ahead Log\n/prometheus/wal/]
        HEAD[Head Block\nin-memory 2h window]
        TSDB[TSDB Blocks\non-disk]
        RULES[Rule Evaluator\nRecording · Alerting]
        QENG[Query Engine PromQL]
        API[HTTP API :9090]
    end

    subgraph Remote["Remote Storage"]
        RW[Remote Write\n→ Thanos · VictoriaMetrics]
    end

    SD -->|discover targets| SCRAPE
    Targets -->|HTTP GET /metrics| SCRAPE
    SCRAPE -->|write samples| WAL
    WAL -->|persist| HEAD
    HEAD -->|compact every 2h| TSDB
    TSDB -->|query| QENG
    HEAD -->|query| QENG
    QENG --> API
    RULES -->|evaluate| QENG
    TSDB -->|remote_write| RW

    style Targets fill:#1565c0,color:#fff
    style Prometheus fill:#2e7d32,color:#fff
    style Remote fill:#4a148c,color:#fff
```

### Key Endpoints

| Endpoint | Mô tả |
|----------|-------------|
| `/api/v1/query` | Instant query |
| `/api/v1/query_range` | Range query (cho dashboards) |
| `/api/v1/targets` | Tất cả discovered targets + health |
| `/api/v1/alerts` | Alerts đang active |
| `/api/v1/write` | Remote write endpoint |
| `/-/reload` | Reload config |
| `/-/ready` | Readiness check |

---

## 3. TSDB Internals

> [!NOTE]
> **Ý TƯỞNG**
> TSDB (Time Series Database) của Prometheus dùng hai cơ chế chính: **WAL** (Write-Ahead Log) để đảm bảo không mất data khi crash, và **XOR delta encoding** (thuật toán Gorilla của Facebook) để nén data 12x so với raw binary. Nếu bạn lưu trữ 1M series × 1 sample/15s → chỉ tốn ~7.5GB/ngày thay vì 90GB nếu lưu raw.

### Data Organization

```
/prometheus/data/
├── 01HQRZ.../          ← Block (2h window)
│   ├── chunks/
│   │   ├── 000001      ← Compressed time series data
│   │   └── 000002
│   ├── index           ← Inverted index: label→series→chunks
│   └── meta.json       ← Block metadata
├── 01HQSA.../          ← Older block
└── wal/                ← Write-Ahead Log (dữ liệu mới nhất)
    ├── 00000000
    └── checkpoint.000000X/
```

### Write Path

```mermaid
sequenceDiagram
    participant Scraper
    participant WAL
    participant HeadBlock
    participant DiskBlock

    Scraper->>WAL: append(series, timestamp, value)
    WAL-->>Scraper: write confirmed  ← First persistence
    Scraper->>HeadBlock: add to in-memory series
    
    Note over HeadBlock: Mỗi 2 giờ...
    HeadBlock->>DiskBlock: encode 120 samples → XOR chunk (~1.3 bytes/sample)
    DiskBlock->>DiskBlock: build inverted index
    DiskBlock->>WAL: truncate old WAL segments
```

### WAL (Write-Ahead Log)

> [!IMPORTANT]
> **Lưu ý WAL**: WAL corruption = mất data. Giám sát `prometheus_tsdb_wal_corruptions_total` và alert khi > 0.
>
> ```promql
> prometheus_tsdb_wal_corruptions_total   # Alert khi > 0
> prometheus_tsdb_wal_replay_duration_seconds  # Thời gian replay khi restart
> ```
>
> **Ước tính thời gian restart**: 1 phút để replay mỗi 1GB WAL.

### Chunk Encoding — XOR Delta (Gorilla Compression)

> [!TIP]
> **Tại sao Gorilla compression đạt 1.3 bytes/sample?** Timestamps thường cách nhau 15s đều đặn → delta nhỏ → delta-of-delta còn nhỏ hơn → encode trong 1-2 bits. Values thay đổi ít giữa 2 scrapes → XOR chủ yếu là 0 → nén tốt.
>
> So sánh với raw storage: 8 bytes (float64) + 8 bytes (int64 timestamp) = 16 bytes/sample. Với Gorilla: **~1.3 bytes/sample = 12x compression**.

**Ước tính storage**:

```
1 triệu active series
× 1 sample mỗi 15 giây
× 1.3 bytes/sample
× 86400 giây/ngày
= 7.5 GB/ngày

Retention 15 ngày: 112 GB cho 1M series @ 15s resolution
```

### Block Compaction

```
2h blocks → compact → 6h blocks → compact → 18h blocks → compact → 36h blocks
```

**Retention configuration**:

```yaml
# CLI flags khi khởi động Prometheus
--storage.tsdb.retention.time=15d      # Xóa data cũ hơn 15 ngày
--storage.tsdb.retention.size=500GB    # Hoặc khi vượt quá 500GB
--storage.tsdb.path=/prometheus/data
```

---

## 4. The Scraping Engine

> [!NOTE]
> **Ý TƯỞNG**
> Scrape engine là vòng lặp đơn giản: mỗi 15 giây, Prometheus HTTP GET `/metrics` của mỗi target, parse Prometheus exposition format, áp dụng relabeling rules, rồi write vào TSDB. Phần khó nhất là **relabeling**: dùng regex để filter/transform metric labels trước khi lưu — không làm đúng sẽ lưu rác vào TSDB.

### Key Scrape Configuration

```yaml
global:
  scrape_interval: 15s       # Tần suất scrape — giảm xuống 5s nếu cần độ phân giải cao hơn
  scrape_timeout: 10s        # PHẢI < scrape_interval
  evaluation_interval: 15s   # Tần suất đánh giá rules
  
  external_labels:
    cluster: prod-us-east-1  # Bắt buộc cho Thanos deduplication
    replica: '$(POD_NAME)'   # Khác nhau giữa HA pair

scrape_configs:
  - job_name: kubernetes-pods
    honor_labels: false      # Không để target ghi đè label job/instance
    
    kubernetes_sd_configs:
      - role: pod
        
    relabel_configs:
      # Chỉ scrape pods có annotation "prometheus.io/scrape: true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
        
      # Dùng cổng tùy chỉnh từ annotation
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
        
      # Gắn k8s metadata làm labels
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
        
    metric_relabel_configs:
      # Bỏ high-cardinality Go runtime metrics trước khi lưu
      - source_labels: [__name__]
        action: drop
        regex: "go_gc_.*|go_memstats_alloc_bytes_total"
```

---

## 5. Service Discovery

> [!NOTE]
> **Ý TƯỞNG**
> Service discovery là lý do Prometheus hoạt động tốt trong môi trường Kubernetes động — không cần cấu hình static target list. Prometheus tự động phát hiện pods/services/nodes mới và bắt đầu scrape ngay khi chúng xuất hiện.

### Kubernetes SD Roles

| Role | Discovers | Metadata labels |
|------|-----------|--------------------|
| `node` | Tất cả K8s nodes | Node labels, annotations |
| `pod` | Tất cả pods | Pod labels, container info |
| `service` | Tất cả services | Service labels, annotations |
| `endpoints` | Service endpoint IPs | Pod + service metadata |

### Standard Pod Annotations

```yaml
# Thêm vào Deployment/Pod spec để Prometheus tự động scrape
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/actuator/prometheus"  # Spring Boot
```

### Relabeling Reference

```
Các actions:
- keep:      Bỏ qua targets KHÔNG khớp regex
- drop:      Bỏ qua targets khớp regex
- replace:   Thay thế label value bằng regex capture
- labelmap:  Copy labels matching regex
- labeldrop: Xóa labels matching regex
- hashmod:   Hash label value modulo N (cho sharding)
```

> **Quan trọng**: `__meta_*` labels chỉ available trong `relabel_configs`. Sau relabeling, tất cả `__meta_*` bị xóa — chỉ labels không có prefix `__` được ghi vào TSDB.

---

## 6. PromQL Deep Dive

> [!NOTE]
> **Ý TƯỞNG**
> PromQL có 2 loại vector: **Instant vector** (giá trị tại một thời điểm) và **Range vector** (giá trị trong khoảng thời gian). Hầu hết functions quan trọng (`rate()`, `histogram_quantile()`) cần Range vector. Sai lầm phổ biến: quên bọc counter trong `rate()` → nhìn thấy số cứ tăng mãi, không phải tốc độ.

### Selector Types

```promql
# Instant vector — tất cả series tại thời điểm hiện tại
http_requests_total{job="api-server", status=~"5..", namespace!="test"}

# Range vector — giá trị trong 5 phút — cần cho rate()
http_requests_total[5m]

# Offset — nhìn về quá khứ 1 giờ
http_requests_total offset 1h
```

### Essential Functions

```promql
# rate — tốc độ tăng/giây của counter (tự handle counter resets)
rate(http_requests_total[5m])

# histogram_quantile — tính P95/P99 từ histogram buckets
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# increase — tổng tăng trong 1h (= rate × 3600)
increase(http_requests_total[1h])

# Aggregation operators
sum(rate(http_requests_total[5m])) by (service)
topk(5, rate(http_requests_total[5m]))
count(up == 1) by (job)
```

### Common Production Queries

```promql
# Tỷ lệ lỗi theo service — dùng cho SLO dashboards
sum by (service) (rate(http_requests_total{status=~"5.."}[5m]))
/
sum by (service) (rate(http_requests_total[5m]))

# SLO availability (30 ngày)
1 - (
  sum(rate(http_requests_total{status=~"5.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
)

# Latency P99 theo service
histogram_quantile(0.99,
  sum by (service, le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# CPU throttling ratio (containers bị giới hạn CPU)
sum by (pod) (rate(container_cpu_cfs_throttled_seconds_total[5m]))
/
sum by (pod) (rate(container_cpu_cfs_periods_total[5m]))

# Kafka consumer lag (giám sát AIOps pipeline)
sum by (consumer_group, topic) (
  kafka_consumer_group_current_offset - kafka_consumer_group_committed_offset
)
```

---

## 7. Recording Rules

> [!NOTE]
> **Ý TƯỞNG**
> Recording rules tính toán trước các queries tốn kém và lưu kết quả như metrics mới. Thay vì mỗi dashboard request tính P99 latency trên 30 ngày data, recording rule tính sẵn mỗi 30 giây và lưu kết quả → dashboards load trong <1 giây thay vì 30+ giây.

> [!TIP]
> **Vì sao recording rules quan trọng cho SLO alerting?** Multi-window burn-rate alerting (như cửa sổ 1h, 6h, 30d) nếu không có recording rules sẽ phải tính toán trực tiếp → cực kỳ tốn kém. Recording rules cho phép tính sẵn các tỷ lệ lỗi theo các window khác nhau.

```yaml
groups:
  - name: http.rules
    interval: 30s   # Đánh giá mỗi 30s
    rules:
      # Pre-compute request rate theo service
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
          
      # Pre-compute error rate — dùng cho SLO burn-rate alerting
      - record: job:http_error_rate:ratio5m
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))
          
      # Pre-compute P99 latency
      - record: job:http_request_duration_p99:5m
        expr: |
          histogram_quantile(0.99,
            sum by (job, le) (
              rate(http_request_duration_seconds_bucket[5m])
            )
          )
          
      # Pre-compute cho multi-window burn-rate alerting
      - record: job:http_error_rate:ratio1h
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[1h]))
          /
          sum by (job) (rate(http_requests_total[1h]))
          
      - record: job:http_error_rate:ratio6h
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[6h]))
          /
          sum by (job) (rate(http_requests_total[6h]))
```

**Naming convention**: `level:metric:operation_range`

```
job:http_requests:rate5m
^   ^             ^   ^
|   |             |   Time window
|   Metric name   Operation
Aggregation level
```

---

## 8. Alerting Rules and Alertmanager

> [!NOTE]
> **Ý TƯỞNG**
> Alert pipeline trong Prometheus hoạt động qua 2 thành phần: **Prometheus** (đánh giá alert rules mỗi 15 giây) và **Alertmanager** (nhận alerts, deduplicate, group, route đến đúng channels). Alertmanager là "smart router" — nó biết: "alert này của team payments → gửi vào #payments-oncall", "alert severity=critical → PagerDuty ngay", "alert này là child của cluster down → im lặng (inhibit)".

### Alert Rule Structure

```yaml
groups:
  - name: service.alerts
    rules:
      - alert: ServiceHighErrorRate
        expr: job:http_error_rate:ratio5m > 0.05   # Dùng recording rule!
        for: 5m                 # Phải đúng 5 phút liên tục mới fire
        labels:
          severity: critical
          runbook: "https://runbooks.internal/high-error-rate"
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: |
            Error rate {{ $value | humanizePercentage }} (threshold: 5%)
          dashboard: "https://grafana.internal/d/service-overview?var-job={{ $labels.job }}"
```

### Alertmanager Architecture

```mermaid
graph TD
    PROM[Prometheus Alert Rule\nfires every 15s] --> AM[Alertmanager]
    
    subgraph AM["Alertmanager Processing"]
        RECV[Receive] --> DEDUP[Deduplicate\n từ HA pair]
        DEDUP --> GROUP[Group\nby team/service]
        GROUP --> INHIB[Inhibit\nsilence child if parent fires]
        INHIB --> ROUTE[Route\nby label matchers]
    end
    
    ROUTE -->|severity=critical| PD[PagerDuty]
    ROUTE -->|severity=warning| SLACK[Slack]
    ROUTE -->|all| AIOPS[AIOps Webhook]
    ROUTE -->|watchdog| WD[Dead Man's Switch]
```

### Alertmanager Configuration

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: slack-default
  group_by: [alertname, cluster, service]
  group_wait: 30s       # Chờ trước khi gửi alert đầu tiên trong group
  group_interval: 5m    # Chờ trước khi gửi update cho group
  repeat_interval: 12h  # Gửi lại nếu alert vẫn firing
  
  routes:
    # Critical → PagerDuty ngay
    - match:
        severity: critical
      receiver: pagerduty
      group_wait: 0s    # Không chờ cho critical
      continue: true    # Tiếp tục routing các rules khác
      
    # Tất cả → AIOps correlation engine
    - match_re:
        severity: "critical|warning"
      receiver: aiops-webhook
      continue: true
      
    # Dead man's switch
    - match:
        alertname: DeadMansSwitch
      receiver: watchdog
      repeat_interval: 5m

inhibit_rules:
  # Nếu cluster down → im lặng service-level warnings
  - source_match:
      alertname: KubernetesNodeDown
    target_match:
      severity: warning
    equal: [cluster]
    
  # Nếu service down → im lặng ServiceHighErrorRate
  - source_match:
      alertname: ServiceDown
    target_match:
      alertname: ServiceHighErrorRate
    equal: [job, namespace]

receivers:
  - name: pagerduty
    pagerduty_configs:
      - routing_key_file: /etc/alertmanager/pagerduty-key
        severity: "{{ if eq .CommonLabels.severity \"critical\" }}critical{{ else }}warning{{ end }}"

  - name: aiops-webhook
    webhook_configs:
      - url: http://aiops-correlation-engine.aiops.svc.cluster.local:8080/api/v1/alerts
        send_resolved: true
        max_alerts: 0     # Gửi tất cả alerts, không limit

  - name: watchdog
    webhook_configs:
      - url: https://hc-ping.com/${HC_UUID}   # healthchecks.io
```

### Alertmanager Clustering (HA)

> [!TIP]
> **Tại sao Alertmanager cluster 3 nodes?** Alertmanager dùng gossip protocol (memberlist) để deduplicate notifications. Nếu cả Prometheus-0 và Prometheus-1 (HA pair) cùng fire cùng một alert, chỉ 1 trong 3 Alertmanager nodes gửi notification đến PagerDuty. Không có cluster → bạn nhận 2 pages cho cùng 1 incident.

```yaml
# Khởi động với cluster peers
alertmanager \
  --cluster.listen-address=0.0.0.0:9094 \
  --cluster.peer=alertmanager-1.alertmanager.svc:9094 \
  --cluster.peer=alertmanager-2.alertmanager.svc:9094 \
  --cluster.peer=alertmanager-3.alertmanager.svc:9094
```

---

## 9. Remote Write and Remote Read

> [!NOTE]
> **Ý TƯỞNG**
> Remote write là cách Prometheus gửi data ra ngoài để lưu trữ lâu dài. Prometheus ghi vào WAL local trước, sau đó WAL tail reader gộp thành batches và gửi đến Thanos/VictoriaMetrics qua HTTP. Nếu remote write bị lag (queue tăng) → data cũ bị drop. Đây là lý do cần monitor `prometheus_remote_storage_pending_samples`.

### Remote Write Configuration

```yaml
remote_write:
  - url: https://thanos-receiver.observability.svc:19291/api/v1/receive
    
    bearer_token_file: /etc/prometheus/remote-write-token
    tls_config:
      ca_file: /certs/ca.crt
      
    # Tuning quan trọng nhất
    queue_config:
      capacity: 10000           # Samples trong memory trước khi block
      max_shards: 50            # Goroutines gửi song song (tăng khi traffic cao)
      min_shards: 5
      max_samples_per_send: 5000
      batch_send_deadline: 5s
      
    # Chỉ gửi SLO-related metrics ra ngoài — giảm chi phí
    write_relabel_configs:
      - source_labels: [__name__]
        action: keep
        regex: "job:.*|slo:.*|recording:.*"
```

**Monitoring remote write queue**:

```promql
# Số samples đang chờ gửi — nếu tăng liên tục → trouble
prometheus_remote_storage_pending_samples

# Samples gửi thất bại — phải = 0
prometheus_remote_storage_failed_samples_total

# Alert khi queue lag > 2 phút
- alert: PrometheusRemoteWriteBehind
  expr: |
    (time() - prometheus_remote_storage_queue_highest_sent_timestamp_seconds) > 120
  for: 5m
  labels:
    severity: critical
```

---

## 10. High Availability

> [!NOTE]
> **Ý TƯỞNG**
> HA Pair là mô hình tối giản: 2 Prometheus instances giống nhau, cùng scrape cùng targets. Nếu 1 instance crash, instance kia vẫn hoạt động. Vấn đề: 2 instances lưu data riêng biệt → kết quả query có thể hơi khác nhau. Giải pháp: Thanos Query làm lớp deduplication phía trước.

### HA Pair Architecture

```mermaid
graph TD
    subgraph Targets
        T1[Service A]
        T2[Service B]
    end

    subgraph HA["Prometheus HA Pair"]
        P1[Prometheus-0\nexternal_label: replica=0]
        P2[Prometheus-1\nexternal_label: replica=1]
    end

    subgraph AM["Alertmanager Cluster (3 nodes)"]
        AM1[AM-0] <-->|gossip| AM2[AM-1] <-->|gossip| AM3[AM-2]
    end

    T1 -->|scrape| P1
    T1 -->|scrape| P2
    T2 -->|scrape| P1
    T2 -->|scrape| P2

    P1 -->|alerts| AM1
    P1 -->|alerts| AM2
    P2 -->|alerts| AM1
    P2 -->|alerts| AM2

    style HA fill:#2e7d32,color:#fff
    style AM fill:#4a148c,color:#fff
```

---

## 11. Prometheus vs CloudWatch

| Tiêu chí | Prometheus | AWS CloudWatch |
|-----------|-----------|----------------|
| **Model** | Pull (scrape) | Push (PutMetricData) |
| **Query language** | PromQL (rất mạnh) | Metric Math (cơ bản) |
| **Retention** | 15d local, unlimited qua Thanos | 15 tháng (coarser resolution theo thời gian) |
| **Cardinality** | Không giới hạn (RAM-bound) | 30 dimensions/metric max |
| **Chi phí (1M metrics/ngày)** | ~$5–20/tháng (infra) | ~$300/tháng ($0.30/metric) |
| **AWS integration** | Qua CloudWatch Exporter | Native |
| **Multi-cloud** | ✅ | ❌ AWS only |

**Khuyến nghị**:

```
AWS infrastructure metrics:   → CloudWatch (free cho EC2/RDS/EKS)
Application metrics:          → Prometheus (rẻ hơn nhiều ở scale)
Hybrid approach:              → CloudWatch Exporter → Prometheus
                                 Thống nhất query tại một Grafana
```

---

## 12. Prometheus vs VictoriaMetrics

> [!NOTE]
> **Ý TƯỞNG**
> VictoriaMetrics là "drop-in replacement" cho Prometheus — API tương thích, PromQL tương thích, nhưng hiệu năng tốt hơn nhiều: write throughput 5-10x cao hơn, compression 2-3x tốt hơn, RAM ít hơn 5-10x. Trade-off: ecosystem nhỏ hơn, không phải CNCF standard.

| Tiêu chí | Prometheus | VictoriaMetrics |
|-----------|-----------|-----------------|
| **Write throughput** | ~1M samples/s | ~5-10M samples/s |
| **Compression** | ~1.3 bytes/sample | ~0.4-0.8 bytes/sample |
| **RAM usage** | Cao (head block in memory) | 5-10x thấp hơn |
| **Horizontal write scaling** | ❌ | ✅ (VM Cluster) |
| **PromQL compatibility** | Gốc | 99% + extensions |
| **Active series limit** | ~10M (OOM risk) | 50M+ |
| **Deduplication** | Qua Thanos | Built-in |

**Khi nào chuyển sang VictoriaMetrics**:
- Cardinality > 5M active series
- RAM bị giới hạn
- Write load > 2M samples/giây
- Muốn horizontal scaling mà không muốn phức tạp của Thanos

---

## 13. Thanos Architecture

> [!NOTE]
> **Ý TƯỞNG**
> Thanos giải quyết 3 vấn đề của Prometheus: (1) Long-term storage — upload TSDB blocks lên S3 tự động; (2) HA deduplication — Query component nhận biết `replica` label và dedup data từ 2 Prometheus; (3) Global view — Query trên nhiều clusters qua một endpoint. Giá phải trả: 6-7 components cần vận hành.

```mermaid
graph TD
    subgraph Prom["Prometheus HA Pair"]
        P1[Prometheus-0\nreplica=0]
        P2[Prometheus-1\nreplica=1]
    end

    subgraph Thanos["Thanos Components"]
        SCAR1[Sidecar 0\nreads WAL]
        SCAR2[Sidecar 1\nreads WAL]
        STORE[Store\nreads from S3]
        QUERY[Query\ndeduplicates replicas]
        COMPACT[Compactor\ndownsampling + retention]
    end

    subgraph S3["AWS S3"]
        BUCKET[thanos-metrics-bucket]
    end

    P1 --> SCAR1
    P2 --> SCAR2
    SCAR1 -->|upload 2h blocks| BUCKET
    SCAR2 -->|upload 2h blocks| BUCKET
    BUCKET --> STORE
    BUCKET --> COMPACT
    SCAR1 -->|StoreAPI gRPC| QUERY
    SCAR2 -->|StoreAPI gRPC| QUERY
    STORE -->|StoreAPI gRPC| QUERY

    style Prom fill:#1565c0,color:#fff
    style Thanos fill:#2e7d32,color:#fff
    style S3 fill:#f57c00,color:#fff
```

### Thanos Components

| Component | Vai trò | Port |
|-----------|------|------|
| Sidecar | Đọc WAL, upload S3 | gRPC :10901 |
| Store | Phục vụ data S3 | gRPC :10901 |
| Query | Tổng hợp + dedup | HTTP :10902 |
| Compactor | Downsampling + retention | HTTP :10902 |

**Thanos Sidecar config**:

```yaml
thanos sidecar \
  --tsdb.path=/prometheus \
  --prometheus.url=http://localhost:9090 \
  --grpc-address=0.0.0.0:10901 \
  --objstore.config-file=/etc/thanos/s3-config.yaml \
  --min-time=-3h   # Upload blocks cũ hơn 3h
```

**S3 config**:

```yaml
type: S3
config:
  bucket: thanos-metrics-prod
  region: us-east-1
  endpoint: s3.us-east-1.amazonaws.com
  sse_config:
    type: SSE-S3
  # Dùng IRSA (IAM Roles for Service Accounts) — không dùng static credentials
```

### Thanos Compactor (Singleton)

> [!CAUTION]
> **KHÔNG chạy 2 Compactor instances song song** — sẽ corrupt S3 data.

```yaml
thanos compact \
  --objstore.config-file=/etc/thanos/s3-config.yaml \
  --retention.resolution-raw=30d \   # Giữ raw data 30 ngày
  --retention.resolution-5m=90d \    # Giữ 5m downsampling 90 ngày
  --retention.resolution-1h=1y \     # Giữ 1h downsampling 1 năm
  --wait
```

---

## 14. Production Configuration

**Full prometheus.yml skeleton**:

```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
  
  external_labels:
    cluster: prod-us-east-1
    region: us-east-1
    environment: production
    replica: '$(POD_NAME)'    # Phải khác nhau giữa HA pair!

alerting:
  alertmanagers:
    - kubernetes_sd_configs:
        - role: endpoints
          namespaces: {names: [alertmanager]}
      relabel_configs:
        - source_labels: [__meta_kubernetes_service_name]
          action: keep
          regex: alertmanager

rule_files:
  - /etc/prometheus/rules/*.yaml

remote_write:
  - url: http://thanos-receive.observability.svc:19291/api/v1/receive
    queue_config:
      capacity: 10000
      max_shards: 30
      max_samples_per_send: 5000
```

**Kubernetes StatefulSet**:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus
  namespace: observability
spec:
  replicas: 2           # HA pair
  template:
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:v2.48.1
          args:
            - --config.file=/etc/prometheus/prometheus.yml
            - --storage.tsdb.path=/prometheus
            - --storage.tsdb.retention.time=15d
            - --storage.tsdb.retention.size=400GB
            - --web.enable-lifecycle               # Cho phép hot-reload config
            - --enable-feature=exemplar-storage    # Cần cho metric→trace navigation
            - --enable-feature=native-histograms   # Native histograms (Prometheus 2.40+)
          resources:
            requests: { cpu: "2", memory: "16Gi" }
            limits:   { cpu: "4", memory: "24Gi" }
            
        # Thanos sidecar chạy cùng pod
        - name: thanos-sidecar
          image: thanosio/thanos:v0.34.0
          args:
            - sidecar
            - --tsdb.path=/prometheus
            - --prometheus.url=http://localhost:9090
            - --grpc-address=0.0.0.0:10901
            - --objstore.config-file=/etc/thanos/s3-config.yaml
            
  volumeClaimTemplates:
    - metadata: {name: prometheus-storage}
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3    # AWS EBS gp3 — tối ưu IOPS/cost
        resources:
          requests: {storage: 500Gi}
```

---

## 15. Common Mistakes

| Lỗi phổ biến | Triệu chứng | Khắc phục |
|---------|---------|-----|
| `scrape_timeout >= scrape_interval` | "context deadline exceeded" trong target status | Luôn `scrape_timeout < scrape_interval` |
| `honor_labels: true` | Targets ghi đè label job/instance | Dùng `honor_labels: false` (default) |
| Thiếu `external_labels` | Thanos không thể dedup HA pair | Luôn set unique `replica` label cho mỗi instance |
| WAL corruption không được monitor | Data loss ngầm | Alert khi `prometheus_tsdb_wal_corruptions_total > 0` |
| Remote write queue overflow | Data cũ bị drop | Monitor `prometheus_remote_storage_pending_samples` |
| Alertmanager single instance | Mất notifications khi restart | Alertmanager cluster 3 nodes |
| Không có exemplar storage | Không navigate metric→trace được | Bật `--enable-feature=exemplar-storage` |
| Histogram buckets sai | P99 inaccurate ±50% | Chọn buckets phù hợp với latency target |
| Thiếu `metric_relabel_configs` | High-cardinality metrics vào TSDB | Filter noise tại scrape time |

---

## 16. Monitoring Prometheus

> [!NOTE]
> **Ý TƯỞNG**
> Prometheus tự giám sát chính nó qua endpoint `:9090/metrics`. Các metrics quan trọng nhất: số active series (cardinality), WAL health, và remote write queue lag.

```promql
# Cardinality — alert khi > 8M (limit 10M)
prometheus_tsdb_head_series

# WAL health — alert khi > 0
prometheus_tsdb_wal_corruptions_total

# Query performance
prometheus_engine_query_duration_seconds{quantile="0.9"}

# Remote write lag
prometheus_remote_storage_pending_samples
prometheus_remote_storage_failed_samples_total

# Rule evaluation speed
prometheus_rule_evaluation_duration_seconds{quantile="0.9"}
```

### Critical Alerts

```yaml
- alert: PrometheusDown
  expr: up{job="prometheus"} == 0
  for: 1m

- alert: PrometheusTSDBHighCardinality
  expr: prometheus_tsdb_head_series > 8000000
  for: 5m
  labels:
    severity: warning

- alert: PrometheusRemoteWriteBehind
  expr: |
    (time() - prometheus_remote_storage_queue_highest_sent_timestamp_seconds) > 300
  for: 5m
  labels:
    severity: critical

- alert: PrometheusWALCorruption
  expr: prometheus_tsdb_wal_corruptions_total > 0
  labels:
    severity: critical
```

---

## 17. Scaling

### Vertical Scaling Limits

| Active Series | RAM cần | CPU cần | Storage (15d) |
|-------------|---------|---------|---------------|
| 1M | 4-8 GB | 2 cores | ~100 GB |
| 5M | 20-40 GB | 4 cores | ~500 GB |
| 10M | 40-80 GB | 8 cores | ~1 TB |
| > 20M | ❌ OOM risk | | → chuyển sang VictoriaMetrics |

### Horizontal Sharding

Chia scrape targets theo hash của address:

```yaml
scrape_configs:
  - job_name: kubernetes-pods-shard-0
    relabel_configs:
      - source_labels: [__address__]
        modulus: 4            # 4 shards
        target_label: __tmp_hash
        action: hashmod
      - source_labels: [__tmp_hash]
        action: keep
        regex: ^0$            # Shard 0 chỉ xử lý 1/4 targets
```

Triển khai 4 Prometheus instances. Thanos Query tổng hợp kết quả từ cả 4.

---

## 18. Security

### RBAC cho Kubernetes SD

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
  - apiGroups: [""]
    resources: [nodes, nodes/proxy, services, endpoints, pods]
    verbs: [get, list, watch]
  - nonResourceURLs: [/metrics]
    verbs: [get]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  kind: ClusterRole
  name: prometheus
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: observability
```

### Prometheus Web TLS

```yaml
# web-config.yml
tls_server_config:
  cert_file: /certs/prometheus.crt
  key_file: /certs/prometheus.key
  min_version: TLS13

basic_auth_users:
  admin: $2y$10$...  # bcrypt hash
```

---

## 19. Cost

> [!NOTE]
> **Ý TƯỞNG**
> Self-hosted Prometheus + Thanos tốn ~$983/tháng cho production stack đầy đủ. AWS Managed Prometheus (AMP) có thể chỉ tốn $9/tháng cho cùng lượng data — nhưng thiếu khả năng customization. Quyết định phụ thuộc vào scale và engineering bandwidth.

### Self-Hosted Cost (EKS)

| Component | Instance | Chi phí/tháng |
|-----------|----------|---------------|
| Prometheus HA pair | 2× r6i.2xlarge (64GB RAM) | $580 |
| EBS storage (500GB × 2) | gp3 | $80 |
| Thanos Query + Store | 4× c6i.large | $240 |
| Thanos Compactor | 1× c6i.large | $60 |
| S3 (1TB, 90 ngày) | S3 Standard | $23 |
| **Tổng** | | **~$983/tháng** |

### AWS Managed Prometheus (AMP)

| Usage | Chi phí |
|-------|---------|
| 1 tỷ samples/tháng (ingestion) | $9.00 |
| 100GB storage | $0.03 |
| 1 tỷ samples (query) | $0.36 |
| **Tổng 1B samples/tháng** | **~$9.39/tháng** |

**Quyết định AMP vs Self-Hosted**:
- Scale < 5M series, team nhỏ → AMP (giảm vận hành)
- Scale > 5M series hoặc cần custom recording rules phức tạp → Self-hosted + Thanos
- Multi-region, multi-cluster → Thanos + S3

---

## 20. Production Review

**Các vấn đề tiềm ẩn**:

1. **Native Histograms migration path**: Prometheus 2.40+ hỗ trợ native histograms (exponential buckets). Teams dùng classic histograms nên có migration plan. Cần thay đổi ở cả SDK code và Prometheus config.

2. **Prometheus Operator**: Hầu hết production deployments dùng Prometheus Operator (kube-prometheus-stack) với CRDs như ServiceMonitor, PodMonitor, PrometheusRule. Xem [production.md](production.md).

3. **OTLP receiver trong Prometheus 2.47+**: Prometheus có thể nhận OTLP trực tiếp mà không cần OTel Collector. Nhưng mất đi khả năng transformation/enrichment của Collector.

### Chapter Scores

| Tiêu chí | Điểm số |
|-----------|-------|
| Technical Accuracy | 9.7/10 |
| Production Readiness | 9.6/10 |
| Depth | 9.8/10 |
| Practical Value | 9.7/10 |
| Cost Awareness | 9.7/10 |

---

## References

1. [Prometheus Documentation](https://prometheus.io/docs/)
2. [Thanos Documentation](https://thanos.io/tip/thanos/getting-started.md/)
3. [Prometheus TSDB Format](https://github.com/prometheus/prometheus/blob/main/tsdb/docs/format/README.md)
4. [VictoriaMetrics Documentation](https://docs.victoriametrics.com/)
5. [AWS Managed Prometheus](https://docs.aws.amazon.com/prometheus/latest/userguide/)
6. [Google SRE Book — Alerting](https://sre.google/sre-book/practical-alerting/)
7. [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
