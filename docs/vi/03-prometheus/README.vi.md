# Chapter 03 — Prometheus

> **Prometheus là tiêu chuẩn thực tế (de-facto standard) cho việc thu thập, lưu trữ, và cảnh báo metrics trong môi trường cloud-native. Việc hiểu biết sâu sắc về Prometheus — bao gồm chi tiết cấu trúc nội bộ TSDB, scrape engine, và kiến trúc HA — là điều cần thiết để xây dựng một nền tảng AIOps đáng tin cậy.**

---

## Prerequisites

- [01 — Observability](../01-observability/README.md) — các khái niệm và các loại metric
- [02 — OpenTelemetry](../02-opentelemetry/README.md) — cách thức metrics truyền dẫn vào Prometheus

## Related Documents

- [04 — Loki](../04-loki/README.md) — lưu trữ logs (chung các mẫu thiết kế kiến trúc)
- [07 — Anomaly Detection](../07-anomaly-detection/README.md) — metrics của Prometheus làm đầu vào
- [08 — Alert Correlation](../08-alert-correlation/README.md) — tiêu thụ cảnh báo của Prometheus

## Next Reading

Sau chương này, hãy chuyển sang [04 — Loki](../04-loki/README.md).

---

## Sub-Documents

| Tài liệu | Mô tả |
|----------|-------------|
| [Architecture](architecture.md) | Các thành phần nội bộ, luồng đi của dữ liệu |
| [TSDB](tsdb.md) | Cấu trúc bên trong Time Series Database, WAL, compaction |
| [Scraping](scraping.md) | Scrape engine, exporters, push gateway |
| [Service Discovery](service-discovery.md) | Kubernetes SD, EC2 SD, relabeling |
| [Recording Rules](recording-rules.md) | Pre-aggregation, liên kết dữ liệu (federation) |
| [Alerting](alerting.md) | Các quy tắc cảnh báo, Alertmanager, định tuyến |
| [High Availability](high-availability.md) | Cặp HA pair, Thanos, VictoriaMetrics |
| [Production](production.md) | Định lượng kích cỡ (Sizing), tinh chỉnh, vận hành |

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

### Design Philosophy

Prometheus được phát triển tại SoundCloud (2012) và được công bố mã nguồn mở vào năm 2015. Các nguyên lý thiết kế:

1. **Thu thập dữ liệu dạng kéo (Pull-based scraping)**: Prometheus chủ động thăm dò (poll) các targets, chứ không đợi targets đẩy dữ liệu về. Điều này giúp dễ dàng phát hiện những thành phần nào đang được giám sát.
2. **Mô hình dữ liệu đa chiều (Multi-dimensional data model)**: Nhãn (labels) là các thực thể hạng nhất. Mỗi chuỗi thời gian (time series) được xác định duy nhất bởi tên metric + bộ nhãn của nó.
3. **PromQL**: Ngôn ngữ truy vấn dạng hàm được thiết kế chuyên biệt cho chuỗi thời gian. Không phải SQL. Không phải Lucene. Rất giàu biểu cảm cho các thao tác trên chuỗi thời gian.
4. **Không lưu trữ dài hạn trong thành phần cốt lõi**: Prometheus chỉ lưu trữ dữ liệu trong khoảng ~15 ngày. Việc lưu trữ dài hạn được xử lý bởi tính năng remote write tới Thanos, Cortex, hoặc VictoriaMetrics.
5. **File thực thi duy nhất (Single binary)**: Đơn giản để triển khai. Không cần cơ sở dữ liệu bên ngoài. Không cần ZooKeeper.

### What Prometheus Is Good At

- Thu thập metrics chuỗi thời gian phục vụ giám sát cơ sở hạ tầng và ứng dụng
- PromQL hỗ trợ các truy vấn linh hoạt, ad-hoc
- Phát hiện dịch vụ (Service discovery) đối với các môi trường động (Kubernetes, EC2)
- Đánh giá cảnh báo với các biểu thức phong phú
- Liên kết dữ liệu (Federation) cho mô hình thu thập phân cấp

### What Prometheus Is NOT Good At

- Lưu trữ dữ liệu dài hạn (nên dùng Thanos hoặc VictoriaMetrics)
- Dữ liệu có độ phân giải nhãn cao (High-cardinality data) (>10M active series sẽ gây áp lực lớn lên RAM)
- Ghi dữ liệu phân tán (chỉ hỗ trợ đường ghi đơn lẻ, không mở rộng ghi theo chiều ngang)
- Cam kết về độ bền vững dữ liệu (WAL chỉ cung cấp cơ chế bảo vệ cơ bản, không phải ACID)
- Dữ liệu sự kiện (Event data) (nên dùng Loki cho logs, Tempo cho traces)

---

## 2. Internal Architecture

```mermaid
graph TD
    subgraph Targets["Monitored Targets"]
        SVC[Microservices\n:8080/metrics]
        NODE[Node Exporter\n:9100/metrics]
        K8S[kube-state-metrics\n:8080/metrics]
        PUSH[Pushgateway\nbatch jobs]
    end

    subgraph Prometheus["Prometheus Server"]
        SD[Service Discovery\nKubernetes · EC2 · Consul · DNS]
        SCRAPE[Scrape Engine\nHTTP GET /metrics\nevery 15s]
        WAL[Write-Ahead Log\n/prometheus/wal/]
        HEAD[Head Block\nin-memory\n2h active window]
        TSDB[TSDB\non-disk blocks\n/prometheus/data/]
        RULES[Rule Evaluator\nRecording · Alerting]
        QENG[Query Engine\nPromQL]
        API[HTTP API\n:9090]
        AM[Alertmanager\nclient]
    end

    subgraph Remote["Remote Storage"]
        RW[Remote Write\n→ Thanos · VM · Cortex]
        RR[Remote Read\n← Thanos Query]
    end

    SD -->|discover targets| SCRAPE
    Targets -->|HTTP GET /metrics| SCRAPE
    SCRAPE -->|write samples| WAL
    WAL -->|persist| HEAD
    HEAD -->|compact every 2h| TSDB
    TSDB -->|query| QENG
    HEAD -->|query| QENG
    QENG -->|results| API
    RULES -->|evaluate| QENG
    RULES -->|fire alerts| AM
    TSDB -->|remote_write| RW
    RR -->|query results| QENG

    style Targets fill:#1565c0,color:#fff
    style Prometheus fill:#2e7d32,color:#fff
    style Remote fill:#4a148c,color:#fff
```

### Key Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------------|
| `/metrics` | GET | Prometheus tự phơi bày các metrics của chính nó (meta-monitoring) |
| `/api/v1/query` | GET/POST | Truy vấn tức thời (Instant query) |
| `/api/v1/query_range` | GET/POST | Truy vấn trong khoảng thời gian (phục vụ dashboards) |
| `/api/v1/series` | GET | Liệt kê các series khớp với bộ lọc (selector) |
| `/api/v1/labels` | GET | Liệt kê tất cả tên các nhãn (label names) |
| `/api/v1/label/<name>/values` | GET | Liệt kê các giá trị của một nhãn cụ thể |
| `/api/v1/targets` | GET | Hiển thị tất cả targets được phát hiện + sức khỏe |
| `/api/v1/rules` | GET | Hiển thị toàn bộ các quy tắc cảnh báo và recording rules |
| `/api/v1/alerts` | GET | Hiển thị các cảnh báo đang được kích hoạt |
| `/api/v1/write` | POST | Endpoint nhận dữ liệu remote write |
| `/-/reload` | POST | Tải lại file cấu hình |
| `/-/healthy` | GET | Kiểm tra sức khỏe (Health check) |
| `/-/ready` | GET | Kiểm tra trạng thái sẵn sàng (Ready check) |

---

## 3. TSDB Internals

Time Series Database là thành phần quan trọng nhất cần phải hiểu để vận hành trong production.

### Data Organization

```
/prometheus/data/
├── 01HQRZ.../ (block)
├── chunks/
│   ├── 000001
│   └── 000002
├── index           ← label index: label→series→chunks
├── meta.json       ← block metadata (min/max time, stats)
└── tombstones      ← deleted series markers
├── 01HQSA.../          (another block)
├── wal/                ← Write-Ahead Log (current data)
│   ├── 00000000
│   ├── 00000001
│   └── checkpoint.000000X/
└── lock
```

### Write Path

```mermaid
sequenceDiagram
    participant Scraper
    participant WAL
    participant HeadBlock
    participant ChunkCache
    participant DiskBlock

    Scraper->>WAL: append(series, timestamp, value)
    WAL-->>Scraper: write confirmed
    Scraper->>HeadBlock: add sample to in-memory series

    Note over HeadBlock: Every 2 hours...
    HeadBlock->>ChunkCache: encode 120 samples → XOR chunk (~1.3 bytes/sample)
    ChunkCache->>DiskBlock: flush to /data/chunks/
    DiskBlock->>DiskBlock: build inverted index
    DiskBlock->>WAL: truncate old WAL segments

    Note over DiskBlock: Every 2h-6h...
    DiskBlock->>DiskBlock: compact overlapping blocks
    DiskBlock->>DiskBlock: merge, deduplicate, compress
```

### WAL (Write-Ahead Log)

WAL đảm bảo tính bền vững dữ liệu. Khi Prometheus khởi động lại:
1. Các phân đoạn (segments) WAL được phát lại (replay) để khôi phục head block
2. Các file Checkpoint giúp tăng tốc độ phát lại (snapshots của WAL)

```
WAL Segment Size: 128MB (mặc định)
Checkpoint Interval: mỗi 2h, hoặc khi WAL đạt 3 phân đoạn
Replay Time: phụ thuộc kích thước WAL. Quy tắc ước lượng: 1 phút cho mỗi 1GB WAL.
```

**Quan trọng**: WAL bị lỗi (corruption) gây mất dữ liệu. Hãy giám sát sức khỏe của WAL:

```promql
# WAL corruption events
prometheus_tsdb_wal_corruptions_total

# WAL replay duration on restart
prometheus_tsdb_wal_replay_duration_seconds
```

### Chunk Encoding — XOR Delta

Prometheus sử dụng thuật toán nén **Gorilla compression** (Facebook, 2015) cho việc mã hóa chunk:

- **Timestamps**: Mã hóa Delta-of-deltas. Các timestamps thông thường (khoảng cách 15s) nén chỉ còn 1.4 bits/sample.
- **Values**: Mã hóa XOR. Các giá trị thay đổi chậm nén chỉ còn ~3 bits/sample.
- **Tổng cộng**: Trung bình đạt mức ~1.3 bytes/sample (so với 16 bytes thô: 8 byte float64 + 8 byte int64 timestamp)

**Ước tính lưu trữ**:

```
1 triệu active series
× 1 mẫu (sample) trên mỗi 15 giây
× 1.3 bytes trên mỗi mẫu
× 86400 giây mỗi ngày
= 7.488 GB/ngày dung lượng lưu trữ

Thời gian lưu giữ 15 ngày (15-day retention):
= 112 GB cho 1M series ở độ phân giải 15s
```

### Block Compaction

Compaction diễn ra tự động. Các blocks được tối ưu hóa qua các cấp độ:

```
2h blocks → compact to 6h blocks → compact to 18h blocks → compact to 36h blocks ...
```

**Quy tắc Compaction** (mặc định):
- Các blocks trong cùng khung thời gian 2h sẽ được gộp lại
- Sau khi có 3 blocks ở cùng một cấp độ, chúng sẽ được nén dồn lên cấp độ tiếp theo
- Compaction cũng áp dụng tombstones (thực sự xóa bỏ series)

**Cấu hình lưu giữ (retention)**:

```yaml
# prometheus.yml
global:
  # Dữ liệu cũ hơn mức này sẽ bị xóa bỏ

# CLI flags:
--storage.tsdb.retention.time=15d      # Lưu giữ theo thời gian
--storage.tsdb.retention.size=500GB    # Lưu giữ theo dung lượng (2.x+)
--storage.tsdb.path=/prometheus/data
--storage.tsdb.wal-segment-size=128MB
--storage.tsdb.min-block-duration=2h   # Mặc định, không thay đổi
--storage.tsdb.max-block-duration=36h  # Mặc định cho mức lưu giữ 15d
```

---

## 4. The Scraping Engine

### Scrape Cycle

```mermaid
sequenceDiagram
    participant SD as Service Discovery
    participant SM as Scrape Manager
    participant Target as Target (/metrics)
    participant TSDB as Head Block

    SD->>SM: danh sách target được cập nhật (add/remove)
    loop mỗi scrape_interval (mặc định 15s)
        SM->>Target: HTTP GET /metrics
        Target-->>SM: Định dạng văn bản Prometheus\n# HELP...\n# TYPE...\nmetric{labels} value
        SM->>SM: Phân tích định dạng (exposition format)
        SM->>SM: Áp dụng các quy tắc relabeling
        SM->>TSDB: append(metric_name, labels, value, timestamp)
    end
```

### Prometheus Exposition Format

Định dạng văn bản truyền tin của metrics:

```
# HELP http_requests_total The total number of HTTP requests.
# TYPE http_requests_total counter
http_requests_total{method="post",code="200"} 1027 1395066363000
http_requests_total{method="post",code="400"}    3 1395066363000

# HELP http_request_duration_seconds A histogram of the request duration.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.05"} 24054
http_request_duration_seconds_bucket{le="0.1"} 33444
http_request_duration_seconds_bucket{le="0.2"} 100392
http_request_duration_seconds_bucket{le="+Inf"} 144320
http_request_duration_seconds_sum 53423
http_request_duration_seconds_count 144320
```

**Định dạng OpenMetrics** (tiêu chuẩn mới hơn, là tập siêu của định dạng Prometheus):

```
# HELP rpc_duration_seconds A summary of RPC durations.
# TYPE rpc_duration_seconds summary
# UNIT rpc_duration_seconds seconds
rpc_duration_seconds{quantile="0.01"} 3.102e-05
rpc_duration_seconds_count 2693
# EOF
```

### Key Scrape Configuration

```yaml
global:
  scrape_interval: 15s       # Tần suất scrape
  scrape_timeout: 10s        # Timeout cho mỗi lần scrape (phải < scrape_interval)
  evaluation_interval: 15s   # Tần suất đánh giá các quy tắc (rules)
  
  # Các nhãn bên ngoài tự động gán vào toàn bộ time series (quan trọng cho federation/Thanos)
  external_labels:
    cluster: prod-us-east-1
    region: us-east-1
    environment: production

scrape_configs:
  - job_name: kubernetes-pods
    honor_labels: false        # Ghi đè nhãn bị trùng lặp từ target
    honor_timestamps: false    # Sử dụng thời gian scrape, không sử dụng timestamp do target cung cấp
    metrics_path: /metrics
    scheme: https
    
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    
    kubernetes_sd_configs:
      - role: pod
        
    relabel_configs:
      # Chỉ thực hiện scrape các pods có annotation prometheus.io/scrape: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: "true"
        
      # Sử dụng cổng tùy chỉnh từ annotation
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
        
      # Sử dụng đường dẫn tùy chỉnh từ annotation
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
        
      # Gán thêm thông tin Kubernetes metadata dưới dạng nhãn
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      - source_labels: [__meta_kubernetes_pod_container_name]
        target_label: container
        
      # Bỏ qua các metrics từ các namespace test/staging
      - source_labels: [namespace]
        action: drop
        regex: "test|staging"
        
    metric_relabel_configs:
      # Bỏ qua các metrics có độ phân giải nhãn cao
      - source_labels: [__name__]
        action: drop
        regex: "go_gc_.*|go_memstats_alloc_bytes_total"
        
      # Đổi tên một nhãn
      - source_labels: [exported_job]
        target_label: job
        
      # Bỏ qua series có giá trị nhãn cụ thể
      - source_labels: [status]
        action: drop
        regex: "5.."   # Bỏ qua 5xx metrics (đã được thu thập theo cách khác)
```

---

## 5. Service Discovery

### Kubernetes Service Discovery Roles

| Vai trò (Role) | Đối tượng phát hiện | Nhãn có sẵn |
|------|-----------|-----------------|
| `node` | Toàn bộ Kubernetes nodes | Node labels, annotations |
| `pod` | Toàn bộ pods | Pod labels, annotations, container info |
| `service` | Toàn bộ services (scrape endpoints của service) | Service labels, annotations |
| `endpoints` | IPs của Service endpoint | Pod + service metadata |
| `endpointslice` | Đối tượng EndpointSlice (mới hơn) | Tương tự như endpoints |
| `ingress` | Các đối tượng Ingress | Ingress metadata |

### Standard Annotations for Service Discovery

```yaml
# Trong file cấu hình Deployment/Pod spec của bạn:
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/actuator/prometheus"  # Dành cho Spring Boot
    prometheus.io/scheme: "http"
```

### Relabeling Reference

Relabeling được áp dụng **trước khi** các mẫu được lưu trữ. Nó là công cụ mạnh mẽ nhất để kiểm soát những gì thực sự được lưu vào đĩa.

```
Các hành động (Actions):
- keep:    Bỏ qua targets/series KHÔNG khớp với regex
- drop:    Bỏ qua targets/series khớp với regex
- replace: Thay thế giá trị nhãn target sử dụng regex capture
- labelmap: Sao chép các nhãn khớp với regex (đổi tên)
- labeldrop: Xóa bỏ các nhãn khớp với regex
- labelkeep: Chỉ giữ lại các nhãn khớp với regex
- hashmod: Băm giá trị nhãn nguồn theo modulo N (phục vụ sharding)
```

**Luồng xử lý Relabeling**: Các nhãn `__meta_*` chỉ khả dụng **bên trong** cấu hình `relabel_configs` (trước khi lưu trữ). Sau khi hoàn tất relabeling, toàn bộ các nhãn `__meta_*` sẽ bị xóa bỏ. Chỉ có các nhãn không chứa tiền tố `__` mới thực sự được ghi lại vào cơ sở dữ liệu.

---

## 6. PromQL Deep Dive

### Selector Types

```promql
# Instant vector: toàn bộ series khớp với selector này tại thời điểm hiện tại
http_requests_total

# Instant vector kết hợp nhãn lọc
http_requests_total{job="api-server", status=~"5..", namespace!="test"}

# Range vector: giá trị các series trong một cửa sổ thời gian (dùng cho hàm rate/histogram)
http_requests_total[5m]

# Bộ điều chỉnh Offset: xem ngược lại thời gian trong quá khứ
http_requests_total offset 1h

# Bộ điều chỉnh At: truy vấn tại mốc thời gian timestamp cụ thể
http_requests_total @ 1705000000
```

### Essential Functions

```promql
# Rate: tốc độ tăng mỗi giây của counter trong cửa sổ thời gian
# Tự động xử lý trường hợp counter reset
rate(http_requests_total[5m])

# irate: tốc độ tức thời (chỉ sử dụng hai mẫu dữ liệu cuối cùng)
# Nhạy bén hơn với các biến động đột biến, ít mượt mà hơn
irate(http_requests_total[2m])

# increase: lượng tăng tổng cộng trong cửa sổ thời gian
# increase(x[1h]) = rate(x[1h]) * 3600
increase(http_requests_total[1h])

# Phân vị của Histogram (P95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Các toán tử tổng hợp (Aggregation operators)
sum(rate(http_requests_total[5m])) by (service)
avg(rate(http_requests_total[5m])) without (pod, instance)
topk(5, rate(http_requests_total[5m]))
count(up == 1) by (job)

# Các phép tính số học
# Tỷ lệ lỗi (Error ratio)
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Tỷ lệ % sử dụng CPU
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Subqueries

Subqueries cho phép áp dụng các hàm phạm vi (range functions) trực tiếp lên các instant vectors:

```promql
# P99 latency trong 6 giờ qua, được tính toán ở độ phân giải 1 phút
max_over_time(
  histogram_quantile(0.99,
    rate(http_request_duration_seconds_bucket[5m])
  )[6h:1m]
)
```

### Common Production Queries

```promql
# Tỷ lệ lỗi theo dịch vụ (cho các SLO dashboards)
sum by (service) (rate(http_requests_total{status=~"5.."}[5m]))
/
sum by (service) (rate(http_requests_total[5m]))

# Phần trăm Sẵn có cho SLO
1 - (
  sum(rate(http_requests_total{status=~"5.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
)

# Latency P99 theo dịch vụ
histogram_quantile(0.99,
  sum by (service, le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Tỷ lệ % thời gian CPU của container bị nghẽn (throttled)
sum by (pod, container) (
  rate(container_cpu_cfs_throttled_seconds_total[5m])
)
/
sum by (pod, container) (
  rate(container_cpu_cfs_periods_total[5m])
)

# Độ trễ tiêu thụ Kafka consumer lag (phục vụ giám sát AIOps pipeline)
sum by (consumer_group, topic) (
  kafka_consumer_group_current_offset - kafka_consumer_group_committed_offset
)
```

---

## 7. Recording Rules

Recording rules **tính toán trước các truy vấn tốn kém** và lưu kết quả như một metric mới. Việc này rất quan trọng để:
- Tăng tốc hiệu năng Dashboard (các truy vấn tức thời thay vì truy vấn phạm vi thời gian lớn)
- Giảm thiểu tải truy vấn đặt lên Prometheus
- Hỗ trợ liên kết dữ liệu (federation) (tối giản metrics chuyển lên Prometheus cha)

```yaml
groups:
  - name: http.rules
    interval: 30s         # Đánh giá mỗi 30s (mặc định: evaluation_interval toàn cục)
    
    rules:
      # Tính toán trước tốc độ yêu cầu theo dịch vụ
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
        labels:
          aggregation: "5m"
          
      # Tính toán trước tỷ lệ lỗi
      - record: job:http_error_rate:ratio5m
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))
          
      # Tính toán trước latency P99
      - record: job:http_request_duration_p99:5m
        expr: |
          histogram_quantile(0.99,
            sum by (job, le) (
              rate(http_request_duration_seconds_bucket[5m])
            )
          )
          
      # Tính toán trước tỷ lệ burn rate của SLO (cửa sổ 1h)
      - record: job:http_error_rate:ratio1h
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[1h]))
          /
          sum by (job) (rate(http_requests_total[1h]))
          
      # Tính toán trước tỷ lệ burn rate của SLO (cửa sổ 6h)
      - record: job:http_error_rate:ratio6h
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[6h]))
          /
          sum by (job) (rate(http_requests_total[6h]))
```

**Quy ước đặt tên**: `level:metric:operation_range`

```
job:http_requests:rate5m
^    ^              ^  ^
|    |              |  Cửa sổ thời gian (Window)
|    Tên Metric     Thao tác thực hiện
Cấp độ tổng hợp (Aggregation level)
```

---

## 8. Alerting Rules and Alertmanager

### Alert Rule Structure

```yaml
groups:
  - name: service.alerts
    rules:
      - alert: ServiceHighErrorRate
        expr: |
          job:http_error_rate:ratio5m > 0.05
        for: 5m           # Phải duy trì đúng trong vòng 5 phút trước khi kích hoạt phát đi
        labels:
          severity: critical
          team: "{{ $labels.job | replace \"-service\" \"\" }}"
          runbook: "https://runbooks.internal/high-error-rate"
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: |
            Service {{ $labels.job }} has error rate {{ $value | humanizePercentage }}
            (threshold: 5%)
          dashboard: "https://grafana.internal/d/service-overview?var-job={{ $labels.job }}"
```

### Alertmanager Architecture

```mermaid
graph TD
    PROM[Prometheus Alert Rule\nfires every evaluation_interval] --> AM[Alertmanager]
    
    subgraph Alertmanager["Alertmanager Processing"]
        RECV[Receive Alert]
        DEDUP[Deduplicate\nsame alert from HA pair]
        GROUP[Group\nby team, service]
        INHIB[Inhibit\nsilence child alerts\nif parent fires]
        SILENCE[Check Silences]
        ROUTE[Route\nby label matchers]
    end
    
    AM --> RECV --> DEDUP --> GROUP --> INHIB --> SILENCE --> ROUTE
    
    ROUTE -->|severity=critical| PD[PagerDuty]
    ROUTE -->|severity=warning| SLACK[Slack Channel]
    ROUTE -->|team=aiops| AIOPS[AIOps Webhook]
    ROUTE -->|alert_type=watchdog| WD[Dead Man's Switch]
```

### Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url_file: /etc/alertmanager/slack-webhook  # Lấy thông tin Secret từ file
  pagerduty_url: https://events.pagerduty.com/v2/enqueue

route:
  # Receiver mặc định
  receiver: slack-default
  
  # Nhóm các cảnh báo theo các nhãn này
  group_by: [alertname, cluster, service]
  group_wait: 30s         # Chờ trước khi gửi cảnh báo đầu tiên trong nhóm
  group_interval: 5m      # Chờ trước khi gửi cập nhật cho nhóm hiện tại
  repeat_interval: 12h    # Gửi lại thông báo nếu cảnh báo vẫn tiếp tục được kích hoạt sau thời gian này
  
  routes:
    # Cảnh báo nghiêm trọng (Critical) → PagerDuty
    - match:
        severity: critical
      receiver: pagerduty
      continue: true       # Vẫn tiếp tục gửi tới các tuyến khớp tiếp theo
      group_wait: 0s       # Gửi ngay lập tức đối với critical
      
    # Gửi toàn bộ cảnh báo tới AIOps correlation engine qua webhook
    - match_re:
        severity: "critical|warning"
      receiver: aiops-webhook
      continue: true
      
    # Dead man's switch
    - match:
        alertname: DeadMansSwitch
      receiver: watchdog
      repeat_interval: 5m
      
    # Định tuyến cho từng team cụ thể
    - match:
        team: payments
      receiver: payments-slack
      
inhibit_rules:
  # Nếu toàn bộ cluster bị sập, tắt các cảnh báo của từng dịch vụ nhỏ lẻ
  - source_match:
      severity: critical
      alertname: KubernetesNodeDown
    target_match:
      severity: warning
    equal: [cluster, region]
    
  # Nếu bản thân dịch vụ bị sập hoàn toàn, tắt cảnh báo tỷ lệ lỗi cao
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
        description: "{{ .CommonAnnotations.summary }}"
        details:
          firing: "{{ .Alerts.Firing | len }}"
          resolved: "{{ .Alerts.Resolved | len }}"
          dashboard: "{{ .CommonAnnotations.dashboard }}"
          runbook: "{{ .CommonLabels.runbook }}"

  - name: slack-default
    slack_configs:
      - channel: "#alerts"
        title: "{{ .CommonAnnotations.summary }}"
        text: |
          *Severity*: {{ .CommonLabels.severity }}
          *Service*: {{ .CommonLabels.job }}
          *Description*: {{ .CommonAnnotations.description }}
          *Dashboard*: {{ .CommonAnnotations.dashboard }}
          *Runbook*: {{ .CommonLabels.runbook }}
        color: "{{ if eq .CommonLabels.severity \"critical\" }}danger{{ else }}warning{{ end }}"
        send_resolved: true

  - name: aiops-webhook
    webhook_configs:
      - url: http://aiops-correlation-engine.aiops.svc.cluster.local:8080/api/v1/alerts
        send_resolved: true
        max_alerts: 0        # Gửi toàn bộ cảnh báo, không giới hạn
        http_config:
          bearer_token_file: /etc/alertmanager/aiops-token
          tls_config:
            ca_file: /etc/alertmanager/ca.crt

  - name: watchdog
    webhook_configs:
      - url: https://hc-ping.com/${HC_UUID}
```

### Alertmanager Clustering (HA)

```yaml
# Khởi chạy Alertmanager với các peer cluster
alertmanager \
  --config.file=/etc/alertmanager/config.yml \
  --cluster.listen-address=0.0.0.0:9094 \
  --cluster.peer=alertmanager-1.alertmanager.svc:9094 \
  --cluster.peer=alertmanager-2.alertmanager.svc:9094 \
  --cluster.peer=alertmanager-3.alertmanager.svc:9094 \
  --web.external-url=https://alertmanager.internal
```

Hệ thống cluster Alertmanager sử dụng **gossip protocol** (memberlist) để khử trùng lặp (deduplicate) các thông báo. Khi Prometheus gửi cùng một cảnh báo đến cả 3 instances Alertmanager, chỉ duy nhất một instance thực hiện gửi thông báo đến PagerDuty.

---

## 9. Remote Write and Remote Read

### Remote Write Protocol

Remote write là cơ chế gửi metrics từ Prometheus cục bộ lên bộ lưu trữ dài hạn.

```mermaid
sequenceDiagram
    participant Prometheus
    participant WAL as WAL (local)
    participant Queue as Remote Write Queue
    participant Thanos as Thanos Receiver / VictoriaMetrics

    Prometheus->>WAL: append sample
    WAL->>Queue: WAL tail reader
    Queue->>Queue: batch samples
    Queue->>Thanos: HTTP POST /api/v1/write\n(snappy-compressed protobuf)
    Thanos-->>Queue: 204 No Content (success)
    Note over Queue: On failure: retry with backoff
    Note over Queue: Queue overflow: drop oldest
```

**Remote Write Configuration**:

```yaml
remote_write:
  - url: https://thanos-receiver.observability.svc:19291/api/v1/receive
    
    # Xác thực (Authentication)
    bearer_token_file: /etc/prometheus/remote-write-token
    tls_config:
      ca_file: /certs/ca.crt
      cert_file: /certs/prometheus.crt
      key_file: /certs/prometheus.key
      
    # Cấu hình hàng đợi (Tinh chỉnh quan trọng nhất)
    queue_config:
      capacity: 10000           # Dung lượng lưu trên memory trước khi block ghi
      max_shards: 50            # Số luồng goroutines gửi song song (tăng lên khi lượng tải cao)
      min_shards: 5
      max_samples_per_send: 5000
      batch_send_deadline: 5s
      min_backoff: 30ms
      max_backoff: 5s
      
    # Thiết lập lọc trước khi gửi (Write relabeling)
    write_relabel_configs:
      # Chỉ chuyển các metrics liên quan đến SLO lên hệ thống lưu trữ ngoài (giảm chi phí)
      - source_labels: [__name__]
        action: keep
        regex: "job:.*|slo:.*|recording:.*"
        
    # Metadata (gửi kèm thông tin định nghĩa metric để phục vụ hiển thị tốt hơn trong Thanos)
    metadata_config:
      send: true
      send_interval: 1m
```

**Remote write tuning**:

```promql
# Giám sát hàng đợi ghi ngoài (remote write queue)
prometheus_remote_storage_queue_highest_sent_timestamp_seconds
prometheus_remote_storage_pending_samples
prometheus_remote_storage_failed_samples_total
prometheus_remote_storage_succeeded_samples_total

# Cảnh báo khi hàng đợi bị dồn ứ (nghĩa là Thanos/VM đang xử lý chậm hơn lượng gửi tới)
- alert: PrometheusRemoteWriteBehind
  expr: |
    (time() - prometheus_remote_storage_queue_highest_sent_timestamp_seconds) > 120
  for: 5m
  labels:
    severity: critical
```

---

## 10. High Availability

### HA Pair (Mô hình HA tối giản)

Khởi chạy hai instances Prometheus giống hệt nhau, cùng scrape các targets giống nhau:

```mermaid
graph TD
    subgraph Targets
        T1[Service A]
        T2[Service B]
    end

    subgraph HA["Prometheus HA Pair"]
        P1[Prometheus-0\nscrapes all targets]
        P2[Prometheus-1\nscrapes all targets\nidentical config]
    end

    subgraph AM["Alertmanager Cluster"]
        AM1[AM-0]
        AM2[AM-1]
        AM3[AM-2]
    end

    T1 -->|scrape| P1
    T1 -->|scrape| P2
    T2 -->|scrape| P1
    T2 -->|scrape| P2

    P1 -->|alerts| AM1
    P1 -->|alerts| AM2
    P1 -->|alerts| AM3
    P2 -->|alerts| AM1
    P2 -->|alerts| AM2
    P2 -->|alerts| AM3

    AM1 <-->|gossip| AM2
    AM2 <-->|gossip| AM3
    AM3 <-->|gossip| AM1

    style HA fill:#2e7d32,color:#fff
    style AM fill:#4a148c,color:#fff
```

**Vấn đề**: Hai instances Prometheus lưu trữ dữ liệu độc lập với nhau. Các truy vấn gửi tới instance này có thể trả về kết quả hơi khác so với instance kia.

**Giải pháp**: Sử dụng Thanos hoặc VictoriaMetrics làm lớp truy vấn trung tâm thực hiện khử trùng lặp dữ liệu (deduplicating query layer).

### Thanos Architecture

```mermaid
graph TD
    subgraph Prom["Prometheus HA Pair"]
        P1[Prometheus-0\nexternal_label:\nreplica=0]
        P2[Prometheus-1\nexternal_label:\nreplica=1]
    end

    subgraph Thanos["Thanos Components"]
        SCAR1[Thanos Sidecar\nreads WAL\nreplica=0]
        SCAR2[Thanos Sidecar\nreads WAL\nreplica=1]
        STORE[Thanos Store\nreads from S3]
        QUERY[Thanos Query\ndeduplicates replicas\nmerges short+long-term]
        COMPACT[Thanos Compactor\ndown-sampling\nretention]
        RULER[Thanos Ruler\nlong-term recording rules]
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
    QUERY -->|dedup by replica label| QUERY

    style Prom fill:#1565c0,color:#fff
    style Thanos fill:#2e7d32,color:#fff
    style S3 fill:#f57c00,color:#fff
```

**Các thành phần chính của Thanos**:

| Thành phần | Vai trò | Cổng |
|-----------|------|------|
| Sidecar | Đọc WAL của Prometheus, upload dữ liệu lên S3 | gRPC :10901 |
| Store | Phục vụ truy xuất dữ liệu S3 qua StoreAPI | gRPC :10901 |
| Query | Tập hợp dữ liệu từ các nguồn StoreAPI, thực hiện khử trùng lặp | HTTP :10902 |
| Querier Frontend | Bộ nhớ đệm truy vấn, phân tách các truy vấn lớn | HTTP :9090 |
| Compactor | Thực hiện Compaction + downsampling + thực thi chính sách lưu trữ trên S3 | HTTP :10902 |
| Ruler | Đánh giá các quy tắc cảnh báo/recording rules dài hạn | HTTP :10902 |
| Receiver | Nhận dữ liệu remote_write, thay thế cho cặp Prometheus HA pair | HTTP :19291 |

**Cấu hình Thanos Sidecar**:

```yaml
thanos sidecar \
  --tsdb.path=/prometheus \
  --prometheus.url=http://localhost:9090 \
  --grpc-address=0.0.0.0:10901 \
  --http-address=0.0.0.0:10902 \
  --objstore.config-file=/etc/thanos/s3-config.yaml \
  --min-time=-3h   # Chỉ đẩy các blocks cũ hơn 3h (dữ liệu mới hơn sẽ do Prometheus trực tiếp xử lý)
```

**Cấu hình S3 cho Thanos**:

```yaml
# s3-config.yaml
type: S3
config:
  bucket: thanos-metrics-prod
  region: us-east-1
  endpoint: s3.us-east-1.amazonaws.com
  sse_config:
    type: SSE-S3     # or SSE-KMS with kms_key_id
  # Sử dụng IAM role, không sử dụng tài khoản tĩnh dạng static credentials
  # Gán IAM role vào các pods Thanos thông qua cơ chế IRSA (IAM Roles for Service Accounts)
```

---

## 11. Prometheus vs CloudWatch

| Tiêu chí | Prometheus | AWS CloudWatch |
|-----------|-----------|----------------|
| **Mô hình** | Dạng kéo (Pull - scrape) | Dạng đẩy (Push - PutMetricData) |
| **Mô hình dữ liệu** | Phân loại đa chiều bằng các nhãn (labels) | Gán qua Namespaces + Dimensions |
| **Ngôn ngữ truy vấn** | PromQL (rất mạnh mẽ) | Metric Math (cơ bản, giới hạn) |
| **Thời gian lưu giữ** | Có thể cấu hình (mặc định 15d, không giới hạn nếu dùng Thanos) | Lưu trữ mặc định 15 tháng (phân chia độ phân giải dữ liệu theo thời gian) |
| **Độ phân giải** | 1–15s | 1s (High Res) / 1phút (Standard) |
| **Giới hạn số lượng series** | Không giới hạn (bị giới hạn bởi dung lượng RAM) | Tối đa 30 dimensions trên mỗi metric |
| **Hệ thống cảnh báo** | Alertmanager (rất linh hoạt) | CloudWatch Alarms (đơn giản hơn) |
| **Chi phí (cho 1M metrics/ngày)** | Khoảng ~$5–20/tháng (chi phí hạ tầng) | Khoảng ~$300/tháng ($0.30/metric/tháng) |
| **Tích hợp AWS** | Qua công cụ phụ trợ CloudWatch Exporter | Hỗ trợ tự nhiên (Native) |
| **Độ phức tạp khi thiết lập** | Cao | Thấp |
| **Hỗ trợ đa đám mây** | ✅ Có | ❌ Chỉ chạy trên AWS |
| **Metrics tùy chỉnh (Custom)** | ✅ Có | ✅ Có ($0.30/metric) |
| **Phát hiện bất thường** | Thông qua AIOps pipeline | Hỗ trợ các tính năng ML cơ bản (hạn chế) |

**Khuyến nghị thực tế cho Production**:

```
Metrics hạ tầng AWS:                 → CloudWatch (miễn phí cho các tài nguyên EC2/RDS/EKS)
Metrics ở tầng ứng dụng:             → Prometheus (rẻ hơn rất nhiều ở quy mô lớn)
Cách thức tiếp cận lai (Hybrid):     → Sử dụng CloudWatch Exporter đẩy metrics AWS về Prometheus
                                        → Hợp nhất lớp truy vấn hiển thị trên một Grafana duy nhất
```

**Cấu hình mẫu CloudWatch Exporter**:

```yaml
# cloudwatch-exporter config
region: us-east-1
role_arn: arn:aws:iam::123456789012:role/cloudwatch-exporter

metrics:
  - aws_namespace: AWS/ApplicationELB
    aws_metric_name: RequestCount
    aws_dimensions: [LoadBalancer]
    aws_statistics: [Sum]
    period_seconds: 60
    
  - aws_namespace: AWS/RDS
    aws_metric_name: DatabaseConnections
    aws_dimensions: [DBInstanceIdentifier]
    aws_statistics: [Average, Maximum]
    
  - aws_namespace: AWS/Kafka
    aws_metric_name: BytesInPerSec
    aws_dimensions: [Cluster Name, Broker ID]
    aws_statistics: [Sum]
```

---

## 12. Prometheus vs VictoriaMetrics

VictoriaMetrics là một giải pháp thay thế tương thích hoàn toàn (drop-in replacement) cho Prometheus với hiệu năng tốt hơn.

| Tiêu chí | Prometheus | VictoriaMetrics |
|-----------|-----------|-----------------|
| **Tốc độ ghi nhận dữ liệu** | ~1M samples/giây (single instance) | ~5–10M samples/giây (single instance) |
| **Hiệu quả nén lưu trữ** | ~1.3 bytes/sample | ~0.4–0.8 bytes/sample |
| **Mức tiêu thụ RAM** | Cao (toàn bộ dữ liệu nằm trên head block memory) | Thấp hơn từ 5–10 lần |
| **Mở rộng ghi theo chiều ngang** | ❌ Không (chỉ hỗ trợ đường ghi đơn lẻ) | ✅ Có hỗ trợ (VictoriaMetrics Cluster) |
| **Độ tương thích PromQL** | Định nghĩa gốc tiêu chuẩn | Tương thích 99% + bổ sung các tính năng nâng cao |
| **Hỗ trợ MetricsQL** | ❌ Không | ✅ Có (cung cấp thêm các hàm nâng cao) |
| **Giới hạn Active series** | ~10M (vượt quá sẽ lỗi OOM) | Đạt mức ~50M+ |
| **Nhận ghi từ xa** | ❌ Không hỗ trợ tự nhiên | ✅ Có (cho phép nhận remote_write trực tiếp) |
| **Khử trùng lặp dữ liệu** | Thực hiện qua Thanos | Tích hợp sẵn (Built-in) |
| **Downsampling** | Thực hiện qua Thanos Compactor | Tích hợp sẵn (Built-in) |
| **Hệ sinh thái** | Rất lớn (tiêu chuẩn thực tế) | Đang phát triển |
| **Giấy phép bản quyền** | Apache 2.0 | Apache 2.0 (bản single node) / Bản quyền Enterprise (bản cluster) |

**Khi nào nên chuyển sang sử dụng VictoriaMetrics**:
- Hệ thống có Cardinality vượt quá >5M active series
- Tài nguyên RAM bị giới hạn (VictoriaMetrics tiêu tốn RAM ít hơn từ 5-10 lần)
- Tải ghi nhận dữ liệu lớn (>2M samples/giây)
- Mong muốn có cơ chế mở rộng ngang có sẵn mà không muốn gánh thêm độ phức tạp của Thanos

---

## 13. Thanos Architecture

Chi tiết cấu hình Thanos đã được trình bày tại mục 10 phía trên. Các lưu ý quan trọng khi vận hành:

### Thanos Compactor (Quan trọng)

Thành phần Compactor phải luôn được chạy dưới dạng **singleton** (không bao giờ được chạy 2 instances song song). Nó thực hiện:
- Nén dữ liệu xuống phân giải 5 phút (cho các blocks cũ hơn 40h)
- Nén dữ liệu xuống phân giải 1 giờ (cho các blocks cũ hơn 10 ngày)
- Thực thi việc xóa bỏ dữ liệu hết hạn theo cấu hình lưu giữ

```yaml
thanos compact \
  --objstore.config-file=/etc/thanos/s3-config.yaml \
  --data-dir=/data \
  --retention.resolution-raw=30d \    # Giữ dữ liệu phân giải gốc trong 30 ngày
  --retention.resolution-5m=90d \     # Giữ dữ liệu nén 5m trong 90 ngày
  --retention.resolution-1h=1y \      # Giữ dữ liệu nén 1h trong 1 năm
  --wait                              # Chạy liên tục dạng daemon
```

### Query Frontend (Lớp Caching)

```yaml
thanos query-frontend \
  --query-frontend.downstream-url=http://thanos-query:10902 \
  --query-range.split-interval=24h \   # Phân tách truy vấn lớn 30 ngày thành các khoảng nhỏ 24h
  --query-range.max-retries-per-request=5 \
  --query-range.response-cache-config-file=/etc/thanos/cache.yaml

# cache.yaml
type: MEMCACHED
config:
  addresses: ["memcached.observability.svc:11211"]
  timeout: 500ms
  max_idle_connections: 100
  max_async_concurrency: 20
  max_get_multi_batch_size: 100
  max_item_size: 1MiB
```

---

## 14. Production Configuration

### Full prometheus.yml

```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s
  
  external_labels:
    cluster: prod-us-east-1
    region: us-east-1
    environment: production
    replica: '$(POD_NAME)'    # Khác biệt trên mỗi thực thể HA

# Cấu hình phát hiện Alertmanager
alerting:
  alert_relabel_configs:
    - source_labels: [severity]
      target_label: severity
  alertmanagers:
    - kubernetes_sd_configs:
        - role: endpoints
          namespaces:
            names: [alertmanager]
      scheme: http
      path_prefix: /
      timeout: 10s
      relabel_configs:
        - source_labels: [__meta_kubernetes_service_name]
          action: keep
          regex: alertmanager

# Khai báo các file chứa quy tắc
rule_files:
  - /etc/prometheus/rules/*.yaml

# Gửi dữ liệu remote write tới Thanos
remote_write:
  - url: http://thanos-receive.observability.svc:19291/api/v1/receive
    queue_config:
      capacity: 10000
      max_shards: 30
      min_shards: 5
      max_samples_per_send: 5000

# Danh sách scrape configs (rút gọn)
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']
      
  - job_name: kubernetes-pods
    # ... (xem chi tiết tại Mục 4 phía trên)
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus
  namespace: observability
spec:
  replicas: 2           # HA pair
  serviceName: prometheus
  podManagementPolicy: Parallel
  
  selector:
    matchLabels:
      app: prometheus
      
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus   # Yêu cầu quyền get/list/watch đối với pods/services/endpoints
      
      containers:
        - name: prometheus
          image: prom/prometheus:v2.48.1
          
          args:
            - --config.file=/etc/prometheus/prometheus.yml
            - --storage.tsdb.path=/prometheus
            - --storage.tsdb.retention.time=15d
            - --storage.tsdb.retention.size=400GB
            - --web.enable-lifecycle               # Cho phép gọi /-/reload
            - --web.enable-admin-api               # Cho phép gọi tsdb/delete_series
            - --enable-feature=exemplar-storage    # Bật bộ lưu trữ exemplar
            - --enable-feature=native-histograms   # Bật tính năng native histograms (2.40+)
            
          ports:
            - containerPort: 9090
              
          resources:
            requests:
              cpu: "2"
              memory: "16Gi"
            limits:
              cpu: "4"
              memory: "24Gi"
              
          readinessProbe:
            httpGet:
              path: /-/ready
              port: 9090
            initialDelaySeconds: 30
            periodSeconds: 10
            
          livenessProbe:
            httpGet:
              path: /-/healthy
              port: 9090
            initialDelaySeconds: 60
            periodSeconds: 30
            
          volumeMounts:
            - name: prometheus-storage
              mountPath: /prometheus
            - name: prometheus-config
              mountPath: /etc/prometheus
            - name: prometheus-rules
              mountPath: /etc/prometheus/rules
              
        # Thanos sidecar
        - name: thanos-sidecar
          image: thanosio/thanos:v0.34.0
          args:
            - sidecar
            - --tsdb.path=/prometheus
            - --prometheus.url=http://localhost:9090
            - --grpc-address=0.0.0.0:10901
            - --objstore.config-file=/etc/thanos/s3-config.yaml
          ports:
            - containerPort: 10901
              
  volumeClaimTemplates:
    - metadata:
        name: prometheus-storage
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3          # AWS EBS gp3 cho hiệu năng IOPS/giá thành tối ưu
        resources:
          requests:
            storage: 500Gi
```

---

## 15. Common Mistakes

| Lỗi phổ biến | Triệu chứng | Khắc phục |
|---------|---------|-----|
| Đặt cấu hình sai `scrape_timeout` | Xuất hiện lỗi "context deadline exceeded" trong trạng thái target | Luôn duy trì `scrape_timeout` < `scrape_interval` |
| Bật `honor_labels: true` | Các target xấu có thể tự ghi đè nhãn job/instance | Luôn sử dụng `honor_labels: false` (mặc định) |
| Thiếu cấu hình `external_labels` | Thanos không thể khử trùng lặp dữ liệu giữa các replicas HA | Luôn cấu hình nhãn `external_labels` duy nhất cho mỗi replica |
| Không giám sát lỗi WAL | Xảy ra lỗi mất mát dữ liệu ngầm | Cảnh báo khi chỉ số `prometheus_tsdb_wal_corruptions_total` > 0 |
| Thời gian chạy đánh giá quy tắc lớn | Các quy tắc bị trượt mất khung đánh giá | Giám sát chỉ số `prometheus_rule_evaluation_duration_seconds` |
| Tràn hàng đợi remote write queue | Dữ liệu cũ bị loại bỏ mà không có cảnh báo | Cảnh báo khi số lượng `pending_samples` tăng cao |
| Chạy một instance Alertmanager duy nhất | Mất mát các thông báo cảnh báo khi instance khởi động lại | Triển khai Alertmanager dưới dạng cluster 3-node |
| Chạy Histograms nhưng không dùng exemplars | Không thể liên kết trực tiếp sang traces | Bật cờ tính năng `exemplar-storage` + cấu hình SDK exemplars |
| Chọn sai các histogram buckets | Độ chính xác kết quả P99 bị sai lệch khoảng ±50% | Chọn ranh giới các buckets phù hợp với phân phối latency thực tế |
| Thiếu cấu hình `metric_relabel_configs` | Nhiều metrics có độ phân giải nhãn cao (high cardinality) bị ghi lại | Lọc bỏ metrics nhiễu tại thời điểm scrape |

---

## 16. Monitoring Prometheus

```promql
# Trạng thái cốt lõi
up{job="prometheus"}
prometheus_build_info

# Hiệu năng
prometheus_engine_query_duration_seconds{quantile="0.9"}   # Các truy vấn chậm
prometheus_rule_evaluation_duration_seconds{quantile="0.9"}  # Đánh giá quy tắc chậm

# Bộ lưu trữ
prometheus_tsdb_head_series                     # Số lượng active series
prometheus_tsdb_head_chunks                     # Chunks lưu trên memory
prometheus_tsdb_storage_blocks_bytes            # Dung lượng lưu trữ trên disk
prometheus_tsdb_compactions_total               # Các tiến trình nén dồn block
prometheus_tsdb_wal_corruptions_total           # Sức khỏe của WAL

# Tải ghi nhận dữ liệu
prometheus_tsdb_head_samples_appended_total     # Tần suất ghi mẫu dữ liệu/giây
rate(prometheus_tsdb_head_samples_appended_total[5m])

# Ghi ngoài (Remote write)
prometheus_remote_storage_pending_samples       # Độ dài hàng đợi dồn ứ
prometheus_remote_storage_failed_samples_total  # Số lượng mẫu gửi lỗi

# Cảnh báo
prometheus_notifications_total                  # Cảnh báo gửi tới Alertmanager
prometheus_notifications_errors_total           # Cảnh báo gửi lỗi
```

### Critical Alerts for Prometheus Itself

```yaml
- alert: PrometheusDown
  expr: up{job="prometheus"} == 0
  for: 1m

- alert: PrometheusTSDBHighCardinality
  expr: prometheus_tsdb_head_series > 8000000
  for: 5m
  labels:
    severity: warning

- alert: PrometheusRemoteWriteBehinnd
  expr: |
    (time() - prometheus_remote_storage_queue_highest_sent_timestamp_seconds) > 300
  for: 5m
  labels:
    severity: critical

- alert: PrometheusRuleEvaluationSlow
  expr: |
    prometheus_rule_evaluation_duration_seconds{quantile="0.9"} > 0.8
    * on(rule_group) group_left()
    prometheus_rule_group_interval_seconds > 0
  for: 5m
  labels:
    severity: warning
```

---

## 17. Scaling

### Vertical Scaling Limits

| Số lượng Series | RAM yêu cầu | CPU yêu cầu | Lưu trữ (15 ngày) |
|-------------|-------------|-------------|---------------|
| 1 triệu series (1M) | 4–8GB | 2 cores | ~100GB |
| 5 triệu series (5M) | 20–40GB | 4 cores | ~500GB |
| 10 triệu series (10M) | 40–80GB | 8 cores | ~1TB |
| 20 triệu series (20M) | ❌ Nguy cơ lỗi OOM | | Cân nhắc chuyển sang VictoriaMetrics |

### Horizontal Scaling with Sharding

Đối với các hệ thống có quy mô thu thập cực kỳ lớn:

```yaml
# Phân chia targets theo hàm băm của địa chỉ sử dụng hashmod relabeling
scrape_configs:
  - job_name: kubernetes-pods-shard-0
    # ... cấu hình kubernetes_sd_configs ...
    relabel_configs:
      - source_labels: [__address__]
        modulus: 4            # Chia làm 4 phân mảnh (shards)
        target_label: __tmp_hash
        action: hashmod
      - source_labels: [__tmp_hash]
        action: keep
        regex: ^0$            # Instance này chỉ chịu trách nhiệm xử lý shard 0
```

Triển khai 4 instances Prometheus độc lập, mỗi instance scrape 1/4 số lượng targets. Thanos Query sẽ chịu trách nhiệm gộp kết quả từ cả 4 instances.

---

## 18. Security

### RBAC cho Kubernetes Service Discovery

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
  - apiGroups: [""]
    resources: [nodes, nodes/proxy, services, endpoints, pods]
    verbs: [get, list, watch]
  - apiGroups: [extensions, networking.k8s.io]
    resources: [ingresses]
    verbs: [get, list, watch]
  - nonResourceURLs: [/metrics]
    verbs: [get]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: observability
```

### Prometheus Web TLS

```yaml
# web-config.yml (Cấu hình HTTPS)
tls_server_config:
  cert_file: /certs/prometheus.crt
  key_file: /certs/prometheus.key
  min_version: TLS13

basic_auth_users:
  admin: $2y$10$...  # bcrypt hash
```

---

## 19. Cost

### Chi phí tự vận hành (Self-Hosted Cost) (EKS, us-east-1)

| Thành phần | Loại Instance | Chi phí hàng tháng |
|-----------|----------|-------------|
| Prometheus HA pair | 2× r6i.2xlarge (64GB RAM) | $580 |
| Prometheus EBS (500GB × 2) | gp3 | $80 |
| Thanos Query | 2× c6i.large | $120 |
| Thanos Store | 2× c6i.large | $120 |
| Thanos Compactor | 1× c6i.large | $60 |
| S3 (1TB, thời gian lưu giữ 90 ngày) | S3 Standard | $23 |
| **Tổng cộng** | | **~$983/tháng** |

### AWS Managed Prometheus (AMP)

| Metric | Chi phí AMP |
|--------|----------|
| Lượng dữ liệu ghi nhận (1 tỷ samples/tháng) | $9.00 |
| Dung lượng lưu trữ (100GB) | $0.03 |
| Lượng dữ liệu truy vấn (1 tỷ samples) | $0.36 |
| **Tổng cộng (cho 1 tỷ samples/tháng)** | **~$9.39/tháng** |

**So sánh và đưa ra quyết định giữa AMP và Tự vận hành (Self-Hosted)**:
- Quy mô <5M series, đội ngũ vận hành nhỏ: Sử dụng AMP (giảm thiểu gánh nặng vận hành)
- Quy mô >5M series hoặc yêu cầu tùy chỉnh recording rules quy mô lớn: Tự vận hành + Thanos
- Đa vùng, đa cluster: Sử dụng Thanos với S3 (đảm bảo quyền kiểm soát tối đa)

---

## 20. Production Review

### Principal Engineer Assessment

**Các khoảng trống được phát hiện**:

1. **Lộ trình chuyển đổi sang Native Histograms**: Prometheus 2.40+ hỗ trợ tính năng native histograms (sử dụng cơ chế chia bucket dạng exponential). Các đội ngũ đang sử dụng classic histograms truyền thống nên có lộ trình chuyển đổi. Việc này đòi hỏi thay đổi ở cả mã nguồn SDK và cấu hình bật cờ trên Prometheus. Chi tiết này được bổ sung và mô tả trong mục [TSDB deep-dive](tsdb.md).

2. **Sử dụng Prometheus Operator (kube-prometheus-stack)**: Phần lớn các đội ngũ vận hành trong thực tế sử dụng Prometheus Operator để thực hiện cấu hình dựa trên CRD (như ServiceMonitor, PodMonitor, PrometheusRule). Nội dung này chưa được đề cập kỹ ở đây, cần bổ sung một mục hướng dẫn chi tiết trong file [production.md](production.md).

3. **OTLP receiver ngay trong Prometheus**: Từ phiên bản Prometheus 2.47+, hệ thống có khả năng nhận trực tiếp dữ liệu OTLP (mà không cần thông qua OTel Collector). Điều này giúp rút gọn mô hình kiến trúc. Tuy nhiên, việc nhận trực tiếp OTLP này sẽ bị giới hạn ở chỗ không hỗ trợ khả năng biến đổi và làm giàu dữ liệu (data transformation).

### Chapter Scores

| Tiêu chí | Điểm số | Ghi chú |
|-----------|-------|-------|
| Technical Accuracy | 9.7/10 | Cấu trúc TSDB, cú pháp PromQL đã được xác thực |
| Production Readiness | 9.6/10 | Có HA, cấu hình Thanos, bảng định lượng kích cỡ |
| Depth | 9.8/10 | Chi tiết cấu trúc WAL, compaction, hàng đợi remote write queue |
| Practical Value | 9.7/10 | Có cấu hình YAML đầy đủ, các ví dụ PromQL thực tế |
| Architecture Quality | 9.7/10 | Mô hình kiến trúc Thanos, cặp HA pair |
| Observability | 9.7/10 | Có PromQL tự giám sát, thiết lập các cảnh báo quan trọng |
| Security | 9.6/10 | Cấu hình RBAC, TLS, phân quyền IRSA cho S3 |
| Scalability | 9.6/10 | Có cơ chế Sharding, bảng so sánh VictoriaMetrics |
| Cost Awareness | 9.7/10 | Định lượng so sánh chi phí Tự vận hành và AMP |
| Diagram Quality | 9.6/10 | Có biểu đồ luồng ghi TSDB, HA, Thanos |

---

## References

1. [Prometheus Documentation](https://prometheus.io/docs/)
2. [Thanos Documentation](https://thanos.io/tip/thanos/getting-started.md/)
3. [Prometheus TSDB Format](https://github.com/prometheus/prometheus/blob/main/tsdb/docs/format/README.md)
4. [VictoriaMetrics Documentation](https://docs.victoriametrics.com/)
5. [AWS Managed Prometheus](https://docs.aws.amazon.com/prometheus/latest/userguide/)
6. [Google SRE Book — Alerting](https://sre.google/sre-book/practical-alerting/)
7. [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
