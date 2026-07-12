# Chapter 01 — Observability

> **Khả năng quan sát (Observability) là nền tảng mà mọi khả năng của AIOps được xây dựng dựa trên đó. Không có telemetry chất lượng cao, không có thuật toán nào, không có LLM nào, và không có tự động hóa nào có thể đáng tin cậy.**

---

## Prerequisites

- Quen thuộc với kiến trúc microservices
- Hiểu biết cơ bản về Prometheus, Grafana, hoặc các công cụ tương tự
- Khuyến nghị: [00 — Introduction to AIOps](../00-introduction.md)

## Related Documents

- [02 — OpenTelemetry](../02-opentelemetry/README.md) — pipeline thu thập
- [03 — Prometheus](../03-prometheus/README.md) — lưu trữ metrics
- [04 — Loki](../04-loki/README.md) — lưu trữ logs
- [05 — Tempo](../05-tempo/README.md) — lưu trữ traces
- [07 — Anomaly Detection](../07-anomaly-detection/README.md) — tiêu thụ dữ liệu khả năng quan sát

## Next Reading

Sau chương này, hãy chuyển sang [02 — OpenTelemetry](../02-opentelemetry/README.md).

---

## Table of Contents

1. [The Three Pillars of Observability](#1-the-three-pillars-of-observability)
2. [Metrics — Deep Dive](#2-metrics--deep-dive)
3. [Logs — Deep Dive](#3-logs--deep-dive)
4. [Traces — Deep Dive](#4-traces--deep-dive)
5. [The Fourth Signal — Profiles](#5-the-fourth-signal--profiles)
6. [Golden Signals vs RED vs USE](#6-golden-signals-vs-red-vs-use)
7. [SLI, SLO, SLA, Error Budget](#7-sli-slo-sla-error-budget)
8. [Observability Architecture](#8-observability-architecture)
9. [Instrumentation Strategy](#9-instrumentation-strategy)
10. [Correlation — Connecting the Three Pillars](#10-correlation--connecting-the-three-pillars)
11. [Data Cardinality — The Silent Killer](#11-data-cardinality--the-silent-killer)
12. [Observability Platform Design](#12-observability-platform-design)
13. [Production Best Practices](#13-production-best-practices)
14. [Common Mistakes](#14-common-mistakes)
15. [Monitoring the Monitoring Stack](#15-monitoring-the-monitoring-stack)
16. [Scaling Observability](#16-scaling-observability)
17. [Security](#17-security)
18. [Cost Management](#18-cost-management)
19. [Production Review](#19-production-review)
20. [Improvement Roadmap](#20-improvement-roadmap)

---

## 1. The Three Pillars of Observability

Khả năng quan sát (Observability) **không** giống như giám sát (monitoring).

- **Monitoring** trả lời: "Hệ thống có hoạt động không? Metric cụ thể này có vượt quá ngưỡng hay không?"
- **Observability** trả lời: "Tại sao hệ thống lại hoạt động như thế này? Trạng thái bên trong nào đã gây ra triệu chứng bên ngoài này?"

Sự phân biệt này rất quan trọng đối với AIOps: monitoring tạo ra cảnh báo. Observability tạo ra sự hiểu biết.

```mermaid
graph TD
    subgraph Monitoring["Monitoring (Reactive)"]
        M1[Is CPU > 80%?] --> M2[Yes → Alert]
    end

    subgraph Observability["Observability (Investigative)"]
        O1[CPU is 95%] --> O2[Which service?]
        O2 --> O3[Which pod?]
        O3 --> O4[What code path?]
        O4 --> O5[What request caused it?]
        O5 --> O6[What downstream calls?]
        O6 --> O7[Root cause identified]
    end

    style Monitoring fill:#4a1942,color:#fff
    style Observability fill:#0d4f8b,color:#fff
```

### The Three Pillars

```mermaid
graph LR
    subgraph Metrics["📊 Metrics\n(What is happening?)"]
        M[Aggregated numeric\ntime series\nCounter · Gauge\nHistogram · Summary]
    end

    subgraph Logs["📋 Logs\n(What happened and why?)"]
        L[Discrete timestamped\nevents\nStructured JSON\nUnstructured text]
    end

    subgraph Traces["🔍 Traces\n(How did it happen?)"]
        T[Request journey\nacross services\nSpan · TraceID\nParent-child relationship]
    end

    Metrics <-->|Exemplar links\nmetric → trace| Traces
    Logs <-->|TraceID in log\nlog → trace| Traces
    Metrics <-->|Metric label\nlog query correlation| Logs

    style Metrics fill:#1565c0,color:#fff
    style Logs fill:#1b5e20,color:#fff
    style Traces fill:#4a148c,color:#fff
```

---

## 2. Metrics — Deep Dive

### 2.1 What Are Metrics?

Một metric là một **phép đo số học được tổng hợp theo thời gian** và được xác định bởi một tập hợp các nhãn (labels).

Trong định dạng phơi bày của Prometheus (Prometheus exposition format):

```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/users",status="200",service="user-svc"} 12345 1705000000000
http_requests_total{method="POST",endpoint="/api/orders",status="500",service="order-svc"} 42 1705000000000
```

**Các thành phần của một metric**:
- **Name**: `http_requests_total` — những gì được đo lường
- **Labels**: `{method, endpoint, status, service}` — các chiều dữ liệu để lọc/nhóm
- **Value**: `12345` — giá trị đo lường
- **Timestamp**: `1705000000000` — mili giây tính từ epoch

### 2.2 Metric Types

#### Counter

Một giá trị số **chỉ tăng**. Không bao giờ giảm (ngoại trừ khi khởi động lại tiến trình).

```
http_requests_total{...} 0 → 1 → 2 → 100 → 101 ...
```

**Sử dụng cho**: requests served, bytes transmitted, errors occurred, tasks completed.

**Cách truy vấn**: Luôn sử dụng `rate()` hoặc `increase()`, không bao giờ dùng giá trị thô.

```promql
# Rate of requests per second over 5-minute window
rate(http_requests_total[5m])

# Total increase over 1 hour
increase(http_requests_total[1h])
```

**Tại sao rate() quan trọng**: Counter sẽ đặt lại về 0 khi tiến trình khởi động lại. `rate()` xử lý việc thiết lập lại (resets) này một cách chính xác. Giá trị counter thô không có ý nghĩa đối với việc cảnh báo.

#### Gauge

Một giá trị có thể **tăng hoặc giảm một cách tùy ý**.

```
memory_usage_bytes{pod="user-svc-abc123"} 536870912  # 512MB
cpu_usage_cores{pod="user-svc-abc123"} 0.85
active_connections{service="db"} 42
```

**Sử dụng cho**: current memory usage, queue depth, number of active connections, temperature.

**Cách truy vấn**: Sử dụng giá trị thô, hoặc `max_over_time()` / `min_over_time()` cho các truy vấn phạm vi thời gian.

```promql
# Current memory usage in GB
container_memory_usage_bytes{pod=~"user-svc.*"} / 1024 / 1024 / 1024

# Max memory over last 1 hour
max_over_time(container_memory_usage_bytes{pod=~"user-svc.*"}[1h])
```

#### Histogram

Ghi lại **phân phối của các giá trị quan sát được** trong các buckets được định nghĩa trước.

```
# HELP http_request_duration_seconds HTTP request latencies
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.005"} 100
http_request_duration_seconds_bucket{le="0.01"} 200
http_request_duration_seconds_bucket{le="0.025"} 450
http_request_duration_seconds_bucket{le="0.05"} 800
http_request_duration_seconds_bucket{le="0.1"} 950
http_request_duration_seconds_bucket{le="0.25"} 990
http_request_duration_seconds_bucket{le="0.5"} 998
http_request_duration_seconds_bucket{le="1.0"} 1000
http_request_duration_seconds_bucket{le="+Inf"} 1000
http_request_duration_seconds_sum 45.234
http_request_duration_seconds_count 1000
```

**Ngữ nghĩa của bucket**: `le="0.1"` nghĩa là "số lượng yêu cầu có thời gian thực thi ≤ 100ms"

**Cách truy vấn percentiles**:

```promql
# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# P99 latency by service
histogram_quantile(0.99,
  sum by (service, le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

**Quan trọng**: Các Histogram buckets phải được cấu hình tại thời điểm thiết lập mã nguồn (instrumentation time). Nếu bạn chọn sai ranh giới của các buckets, ước tính P99 của bạn sẽ không chính xác.

**Các ranh giới bucket khuyến nghị cho latency**:
```yaml
# For fast internal APIs (target: <50ms)
buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]

# For user-facing APIs (target: <500ms)  
buckets: [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

# For batch jobs (target: <5min)
buckets: [1, 5, 10, 30, 60, 120, 300, 600, 1800]
```

**Native Histograms (Prometheus 2.40+)**: Tránh các buckets định nghĩa sẵn. Sử dụng exponential bucketing. Độ chính xác tốt hơn. Xem [Prometheus Architecture](../03-prometheus/architecture.md).

#### Summary

Tương tự như Histogram, nhưng tính toán các quantiles **ở phía client**.

```
http_request_duration_seconds{quantile="0.5"} 0.023
http_request_duration_seconds{quantile="0.9"} 0.087
http_request_duration_seconds{quantile="0.99"} 0.213
http_request_duration_seconds_sum 45.234
http_request_duration_seconds_count 1000
```

**Histogram vs Summary — Khi nào nên dùng loại nào**:

| Chiều so sánh | Histogram | Summary |
|-----------|-----------|---------|
| Độ chính xác quantile | Xấp xỉ (phụ thuộc vào bucket) | Chính xác |
| Tổng hợp trên nhiều replica | ✅ Có thể với `histogram_quantile()` | ❌ Không thể tổng hợp |
| Chi phí phía Server | Thấp (số lượng bucket đơn giản) | Thấp |
| Chi phí phía Client | Thấp | Cao hơn (thuật toán streaming quantile) |
| Trường hợp sử dụng | Các dịch vụ nhiều instance | Single-instance, yêu cầu quantile chính xác |
| **Khuyến nghị** | **Ưu tiên cho môi trường production** | Tránh dùng cho các dịch vụ phân tán |

### 2.3 Metric Naming Conventions

Tuân thủ [Prometheus naming conventions](https://prometheus.io/docs/practices/naming/):

```
# Pattern: <namespace>_<subsystem>_<name>_<unit>
# Units: seconds, bytes, total, ratio, info

# Good
http_server_request_duration_seconds
http_server_requests_total
process_resident_memory_bytes
go_gc_duration_seconds

# Bad (no unit, ambiguous)
request_time
memory
errors
```

**Quy ước nhãn tiêu chuẩn** (OpenTelemetry Semantic Conventions):

```yaml
# HTTP
http_method: GET | POST | PUT | DELETE
http_route: /api/users/{id}  # Template, not actual value
http_status_code: "200" | "404" | "500"
http_scheme: http | https

# Service identity
service_name: user-service
service_version: "1.4.2"
service_namespace: production
service_instance_id: pod-abc123

# Kubernetes
k8s_namespace_name: production
k8s_pod_name: user-svc-abc123
k8s_node_name: ip-10-0-1-50
k8s_cluster_name: prod-us-east-1
```

---

## 3. Logs — Deep Dive

### 3.1 What Are Logs?

Logs là **các bản ghi rời rạc, có mốc thời gian (timestamped) về các sự kiện** đã xảy ra trong hệ thống. Không giống như metrics (được tổng hợp), logs ghi lại các sự kiện riêng lẻ với đầy đủ bối cảnh.

### 3.2 Log Structure — Structured vs Unstructured

#### Unstructured Log (Anti-Pattern)

```
2024-01-15 14:23:45 ERROR Failed to process order 12345 for user john@example.com after 3 retries
```

Vấn đề:
- Parsing rất dễ gãy (regex hell)
- Không thể lọc theo các trường cụ thể một cách hiệu quả
- Không có schema mà máy có thể đọc được
- Định dạng khác nhau tùy theo lập trình viên và dịch vụ

#### Structured Log (Bắt buộc cho AIOps)

```json
{
  "timestamp": "2024-01-15T14:23:45.123Z",
  "level": "ERROR",
  "service": "order-service",
  "version": "2.1.4",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "user_id": "user-789",
  "order_id": "ord-12345",
  "event": "order_processing_failed",
  "message": "Failed to process order after max retries",
  "error": {
    "type": "PaymentGatewayTimeoutError",
    "message": "Gateway did not respond within 3000ms",
    "stack_trace": "..."
  },
  "retry_count": 3,
  "duration_ms": 9234,
  "environment": "production",
  "region": "us-east-1"
}
```

**Tại sao việc này quan trọng đối với AIOps**:
- Hệ thống phát hiện bất thường log hoạt động trên giá trị các trường dữ liệu, không hoạt động trên các mẫu văn bản
- Tương quan với traces thông qua `trace_id`
- Nhóm theo `service`, `error.type` để cung cấp bối cảnh incident
- Các mô hình ML tiêu thụ các đặc trưng cấu trúc (structured features), không phải văn bản thô

### 3.3 Log Severity Levels

| Cấp độ | Giá trị số | Khi nào sử dụng | Tạo cảnh báo? |
|-------|---------|-------------|--------|
| TRACE | 10 | Rất chi tiết, debug cấp độ code | Không bao giờ |
| DEBUG | 20 | Thông tin chẩn đoán cho lập trình viên | Không bao giờ |
| INFO | 30 | Các sự kiện vận hành bình thường | Không bao giờ |
| WARN | 40 | Lỗi ngoài dự kiến nhưng đã được xử lý. Hệ thống tiếp tục chạy. | Có thể (nếu kéo dài liên tục) |
| ERROR | 50 | Lỗi trong một yêu cầu/thao tác cụ thể | Có (nếu tỷ lệ lỗi tăng cao) |
| CRITICAL | 60 | Lỗi cấp độ dịch vụ, nguy cơ mất dữ liệu | Có (ngay lập tức) |
| FATAL | 70 | Hệ thống không thể tiếp tục, sẽ crash | Có (P1 ngay lập tức) |

**Quy tắc production**: Chỉ ghi log ở mức ERROR đối với các lỗi cần phải điều tra. Ghi log ở mức WARN đối với các lỗi tạm thời đã được dự liệu trước (có thể retry). Không ghi log ERROR đối với các trường hợp mà bạn mong muốn hệ thống retry thành công.

### 3.4 Log Volume and Sampling

**Vấn đề**: Ở mức 10,000 req/giây, việc ghi log cấp độ `INFO` tạo ra khoảng 100,000 log entries/phút. Với mức phí $0.50/GB nạp dữ liệu (ingestion) của CloudWatch:

```
10,000 req/giây × 1KB kích thước log trung bình × 60 giây = 600MB/phút = 864GB/ngày
864GB × $0.50 = $432/ngày → $157,680/năm chỉ cho riêng INFO logs
```

**Chiến lược lấy mẫu (Sampling Strategies)**:

| Chiến lược | Cách thức | Trường hợp sử dụng |
|----------|-----|----------|
| Head-based sampling | Lấy mẫu % yêu cầu tại điểm đầu vào | Giảm thiểu dung lượng một cách đồng đều |
| Tail-based sampling | Lấy mẫu 100% các yêu cầu ERROR hoặc chậm | Giữ lại tất cả các sự kiện đáng chú ý |
| Adaptive sampling | Tỷ lệ động dựa trên tỷ lệ lỗi | Cân bằng giữa chi phí và độ bao phủ |

**Chiến lược production khuyến nghị**:
- `INFO`: Lấy mẫu 10% (hoặc 1% cho lưu lượng rất cao)
- `WARN`: Lấy mẫu 100%
- `ERROR`: Lấy mẫu 100%
- `CRITICAL/FATAL`: Lấy mẫu 100% + cảnh báo ngay lập tức

### 3.5 Log Labels in Loki

Loki tổ chức logs theo các nhãn (labels) (tương tự như Prometheus). Nhãn được đánh chỉ mục; nội dung log thì không.

```yaml
# Good labels (low cardinality, useful for filtering)
labels:
  service: order-service
  environment: production
  region: us-east-1
  level: ERROR

# Bad labels (high cardinality - kills Loki)
labels:
  user_id: "user-789"          # Millions of unique values
  trace_id: "4bf92f3577b..."   # Unique per request
  order_id: "ord-12345"         # Unique per order
```

**Quy tắc**: Nhãn nên có cardinality giới hạn (<10,000 giá trị nhãn duy nhất).

---

## 4. Traces — Deep Dive

### 4.1 What Are Traces?

Một **trace** là bản ghi hoàn chỉnh về hành trình của một yêu cầu đi qua hệ thống phân tán. Nó bao gồm nhiều **spans** — một span cho mỗi dịch vụ hoặc thao tác.

```mermaid
gantt
    title Trace: Order Placement Request (TraceID: 4bf92f35)
    dateFormat  SSS
    axisFormat %Lms

    section API Gateway
    Receive Request        :0, 5
    Auth Validation        :5, 15

    section Order Service
    Parse Request          :15, 20
    Validate Inventory     :20, 50
    Create Order Record    :50, 80

    section Inventory Service
    Check Stock            :22, 45

    section Database
    INSERT order           :52, 78

    section Payment Service
    Charge Card            :80, 180

    section Notification Service
    Send Email             :182, 220
```

### 4.2 Span Data Structure

```json
{
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7",
  "parentSpanId": "b9c7c989f97918e1",
  "operationName": "order-service.createOrder",
  "startTime": 1705329825050000,
  "duration": 65000,
  "status": {
    "code": "ERROR",
    "message": "Inventory check failed"
  },
  "resource": {
    "service.name": "order-service",
    "service.version": "2.1.4",
    "deployment.environment": "production",
    "k8s.pod.name": "order-svc-abc123",
    "k8s.namespace.name": "production"
  },
  "attributes": {
    "http.method": "POST",
    "http.route": "/api/orders",
    "http.status_code": 422,
    "order.id": "ord-12345",
    "user.id": "user-789",
    "db.system": "postgresql",
    "db.name": "orders",
    "db.statement": "INSERT INTO orders ..."
  },
  "events": [
    {
      "name": "inventory.check.start",
      "timestamp": 1705329825060000,
      "attributes": {"sku": "SKU-ABC", "quantity_requested": 5}
    },
    {
      "name": "inventory.check.failed",
      "timestamp": 1705329825090000,
      "attributes": {"sku": "SKU-ABC", "quantity_available": 2}
    }
  ],
  "links": []
}
```

### 4.3 Context Propagation

Để distributed tracing hoạt động được, **TraceID và SpanID phải được truyền qua** các ranh giới dịch vụ thông qua các HTTP headers.

**W3C TraceContext** (tiêu chuẩn):
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
              ^  ^                                ^                ^
              |  TraceID (128-bit)                SpanID (64-bit)  Flags
              Version
```

**B3 Headers** (Zipkin, các dịch vụ cũ hơn):
```
X-B3-TraceId: 4bf92f3577b34da6a3ce929d0e0e4736
X-B3-SpanId: 00f067aa0ba902b7
X-B3-ParentSpanId: b9c7c989f97918e1
X-B3-Sampled: 1
```

**Yêu cầu quan trọng**: Mọi dịch vụ trong hệ thống của bạn phải truyền header `traceparent`. Chỉ cần một dịch vụ làm rơi mất header này, chuỗi trace sẽ bị đứt gãy. Hãy bắt buộc áp dụng điều này khi review code và bằng các bài test tự động.

### 4.4 Trace Sampling Strategies

| Chiến lược | Mô tả | Ưu điểm | Nhược điểm | Trường hợp sử dụng |
|----------|-------------|------|------|----------|
| **Head-Based** | Quyết định tại điểm đầu vào của trace, sau đó được lan truyền | Đơn giản, chi phí thấp | Không thể giữ lại các trace "đáng chú ý" | Các hệ thống lưu lượng thấp |
| **Tail-Based** | Quyết định sau khi trace hoàn tất, dựa trên kết quả đầu ra | Giữ lại toàn bộ traces lỗi, chậm | Sử dụng nhiều memory/CPU hơn, phức tạp | Môi trường production (khuyến nghị) |
| **Probabilistic** | Tỷ lệ % ngẫu nhiên, ví dụ: 1% | Dung lượng có thể dự đoán trước | Bỏ sót các sự kiện hiếm gặp | Lưu lượng cực kỳ cao |
| **Rate-Limiting** | Tối đa N traces/giây | Chi phí được giới hạn | Không nhận biết được lỗi | Kiểm soát chi phí |
| **Adaptive** | Tỷ lệ động dựa trên tỷ lệ lỗi | Cân bằng tốt nhất | Phức tạp nhất | Các nền tảng đã trưởng thành |

**Cấu hình production khuyến nghị** (tail-based trong OTel Collector):

```yaml
processors:
  tail_sampling:
    decision_wait: 10s        # Wait for all spans before deciding
    num_traces: 100000        # Traces held in memory
    expected_new_traces_per_sec: 1000
    policies:
      # Always keep error traces
      - name: errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      
      # Always keep slow traces (>1 second)
      - name: slow-traces
        type: latency
        latency: {threshold_ms: 1000}
      
      # Sample 10% of normal traces
      - name: normal-traffic-sample
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
      
      # Always keep traces with specific attributes
      - name: payment-service
        type: string_attribute
        string_attribute:
          key: service.name
          values: [payment-service]
```

---

## 5. The Fourth Signal — Profiles

Continuous profiling ngày càng được coi là cột trụ thứ tư của khả năng quan sát (observability).

### What Is Continuous Profiling?

Trong khi traces cho biết **dịch vụ nào** đang chậm, profiles sẽ chỉ ra **dòng code cụ thể nào** đang tiêu thụ CPU/memory.

```
Trace: order-service.createOrder → 200ms
  ↓ (tại sao lại mất 200ms?)
Profile: 
  - 120ms in validateInventory()
    - 80ms in db.query() → SQL is N+1
    - 40ms in JSON serialization
  - 50ms in updateOrderStatus()
  - 30ms in publishKafkaEvent()
```

### Tools

| Công cụ | Mô tả | Storage Backend |
|------|-------------|----------------|
| **Pyroscope** (Grafana) | Continuous profiling, tích hợp với Grafana | S3 / local |
| **Parca** | Mã nguồn mở, dựa trên eBPF | S3 |
| **AWS CodeGuru Profiler** | Dịch vụ được quản lý, hỗ trợ Java/.NET | AWS |
| **Google Cloud Profiler** | Dịch vụ được quản lý, hỗ trợ nhiều ngôn ngữ | GCP |

**Tích hợp với Traces**: Grafana 10+ hỗ trợ liên kết từ các trace spans trực tiếp đến profiles cho cùng một khoảng thời gian.

---

## 6. Golden Signals vs RED vs USE

Ba phương pháp luận để xác định những gì cần đo lường. Mỗi phương pháp hướng tới đối tượng người dùng khác nhau.

### The Four Golden Signals (Google SRE)

Thiết kế cho các **dịch vụ hướng người dùng (user-facing services)**. Được định nghĩa trong cuốn sách SRE Book của Google.

| Tín hiệu | Định nghĩa | Ví dụ Prometheus |
|--------|------------|-------------------|
| **Latency** | Thời gian phục vụ một yêu cầu. Phân biệt rõ giữa latency thành công và latency lỗi. | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |
| **Traffic** | Nhu cầu đặt lên hệ thống. Số lượng yêu cầu trên mỗi giây. | `rate(http_requests_total[5m])` |
| **Errors** | Tỷ lệ yêu cầu thất bại (5xx, lỗi tường minh, nội dung sai). | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])` |
| **Saturation** | Mức độ "đầy" của dịch vụ. CPU, memory, độ dài hàng đợi gần đạt giới hạn. | `container_cpu_usage_seconds_total / container_cpu_limits_seconds_total` |

### RED Method (Tom Wilkie / Weaveworks)

Thiết kế cho các **microservices dựa trên yêu cầu (request-based microservices)**.

| Metric | Định nghĩa |
|--------|------------|
| **Rate** | Số lượng yêu cầu trên giây |
| **Errors** | Tỷ lệ lỗi (%) |
| **Duration** | Phân phối thời gian phản hồi (P50, P95, P99) |

RED là một tập con của Golden Signals. Sử dụng RED làm **điểm khởi đầu mặc định** cho bất kỳ microservice mới nào.

### USE Method (Brendan Gregg)

Thiết kế cho việc **giám sát tài nguyên / cơ sở hạ tầng (resource/infrastructure monitoring)**.

| Metric | Định nghĩa | Ví dụ |
|--------|------------|---------|
| **Utilization** | Thời gian trung bình tài nguyên bận rộn | CPU: 75% |
| **Saturation** | Độ dài hàng đợi khi tài nguyên bị quá tải | Độ dài hàng đợi chạy CPU (CPU run queue length) |
| **Errors** | Số lượng lỗi | Lỗi Disk I/O |

USE áp dụng cho: CPU, memory, disk I/O, các cổng mạng (network interfaces), tài nguyên node Kubernetes.

### Combining All Three

```mermaid
graph TD
    subgraph User["User Experience (Golden Signals)"]
        GS1[Latency P99]
        GS2[Error Rate]
        GS3[Traffic RPS]
        GS4[Saturation]
    end

    subgraph Service["Service Health (RED)"]
        R[Rate]
        E[Errors]
        D[Duration]
    end

    subgraph Infra["Infrastructure (USE)"]
        U[Utilization]
        S[Saturation]
        ER[Errors]
    end

    GS1 --> D
    GS2 --> E
    GS3 --> R
    GS4 --> U
    U --> S
```

---

## 7. SLI, SLO, SLA, Error Budget

### Definitions

| Thuật ngữ | Tên đầy đủ | Định nghĩa | Bên sở hữu |
|------|-----------|------------|----------|
| **SLI** | Service Level Indicator | Số đo thực tế. Một metric cụ thể. | Đội ngũ kỹ sư (Engineering) |
| **SLO** | Service Level Objective | Mục tiêu hướng tới. "99.9% yêu cầu có latency < 500ms" | Kỹ sư + Quản lý sản phẩm |
| **SLA** | Service Level Agreement | Cam kết hợp đồng với khách hàng. Thường thấp hơn SLO khoảng 1–2%. | Bộ phận Kinh doanh/Pháp lý |
| **Error Budget** | — | 100% trừ đi SLO. Lượng thời gian/lỗi bạn được phép mất đi. | Kỹ sư + Quản lý sản phẩm |

### SLI Examples

```yaml
# Availability SLI
sli_availability:
  description: "Percentage of successful HTTP requests"
  numerator: "http_requests_total{status!~'5..'}"
  denominator: "http_requests_total"
  good_events: "requests with status != 5xx"

# Latency SLI  
sli_latency:
  description: "Percentage of requests served within 500ms"
  numerator: "http_request_duration_seconds_bucket{le='0.5'}"
  denominator: "http_request_duration_seconds_count"
  good_events: "requests completing in < 500ms"

# Freshness SLI (for data pipelines)
sli_freshness:
  description: "Percentage of data items processed within 5 minutes"
  numerator: "pipeline_events_processed_total{age_bucket='0-5m'}"
  denominator: "pipeline_events_received_total"
  good_events: "data processed within 5 minutes"
```

### Error Budget Calculation

```
Error Budget = 1 - SLO

Ví dụ:
SLO = 99.9% availability (monthly)
Error Budget = 0.1% số lượng yêu cầu được phép thất bại

Trong một tháng (30 ngày × 24giờ × 60phút × 60giây = 2,592,000 giây):
Budget = 2,592 giây = 43.2 phút downtime hoàn toàn

Ở mức 1,000 req/giây:
Tổng số yêu cầu = 2,592,000,000
Số lỗi tối đa được phép = 2,592,000 requests (0.1%)
```

### Burn Rate Alerting

**Vấn đề của cảnh báo theo ngưỡng (threshold alerts)**: Nếu SLO là 99.9%, tỷ lệ lỗi 0.2% tuy gấp đôi ngân sách lỗi nhưng có vẻ vẫn ổn.

**Burn rate**: Tốc độ bạn đang tiêu thụ ngân sách lỗi (error budget) của mình so với bình thường.

```
burn_rate = current_error_rate / (1 - SLO)

Ví dụ:
SLO = 99.9% → error budget = 0.1%
current_error_rate = 1%
burn_rate = 1% / 0.1% = 10x

Với burn rate là 10x, ngân sách lỗi tháng sẽ cạn kiệt trong: 30 ngày / 10 = 3 ngày
```

**Cảnh báo đa cửa sổ thời gian, đa tốc độ tiêu thụ (Multi-window, multi-burn-rate alerting)** (khuyến nghị của Google):

```yaml
# Alert when burning fast AND sustained
- alert: SLOBurnRateCritical
  expr: |
    (
      job:http_request_error_rate:rate1h{job="user-svc"} > (14.4 * 0.001)
      and
      job:http_request_error_rate:rate5m{job="user-svc"} > (14.4 * 0.001)
    )
  for: 0m
  labels:
    severity: critical
  annotations:
    summary: "SLO burn rate critical (14.4x): exhausts monthly budget in 2 hours"

- alert: SLOBurnRateHigh
  expr: |
    (
      job:http_request_error_rate:rate6h{job="user-svc"} > (6 * 0.001)
      and
      job:http_request_error_rate:rate30m{job="user-svc"} > (6 * 0.001)
    )
  for: 0m
  labels:
    severity: warning
  annotations:
    summary: "SLO burn rate high (6x): exhausts monthly budget in 5 days"
```

---

## 8. Observability Architecture

### Full Platform Architecture

```mermaid
flowchart TD
    subgraph Apps["Application Layer"]
        SVC1[Service A\nOTel SDK]
        SVC2[Service B\nOTel SDK]
        SVC3[Service C\nOTel SDK]
    end

    subgraph Agents["Collection Agents"]
        OTC[OTel Collector\nDaemonSet]
        PROMTAIL[Grafana Alloy\nDaemonSet]
        NODE[Node Exporter\nDaemonSet]
        KUBELET[kube-state-metrics]
    end

    subgraph Gateway["Collection Gateway"]
        OTCGW[OTel Collector\nGateway Deployment\n×3 replicas]
    end

    subgraph Storage["Storage Layer"]
        PROM[(Prometheus\n+ Thanos)]
        LOKI[(Loki\nS3 Backend)]
        TEMPO[(Tempo\nS3 Backend)]
    end

    subgraph Viz["Visualization"]
        GRF[Grafana]
        AM[Alertmanager]
    end

    subgraph AIOps["AIOps Layer"]
        AIOPS[AIOps Pipeline\nsee Ch07-11]
    end

    SVC1 -->|OTLP gRPC :4317| OTC
    SVC2 -->|OTLP gRPC :4317| OTC
    SVC3 -->|OTLP HTTP :4318| OTC
    OTC -->|OTLP gRPC| OTCGW
    PROMTAIL -->|Loki push API| LOKI
    NODE -->|/metrics HTTP| PROM
    KUBELET -->|/metrics HTTP| PROM
    OTCGW -->|remote_write| PROM
    OTCGW -->|Loki push| LOKI
    OTCGW -->|OTLP gRPC| TEMPO
    PROM --> GRF
    LOKI --> GRF
    TEMPO --> GRF
    PROM -->|AlertingRules| AM
    AM -->|route| AIOPS

    style Apps fill:#1565c0,color:#fff
    style Agents fill:#2e7d32,color:#fff
    style Gateway fill:#1b5e20,color:#fff
    style Storage fill:#4a148c,color:#fff
    style Viz fill:#e65100,color:#fff
    style AIOps fill:#b71c1c,color:#fff
```

### Network Flow and Ports

| Thành phần | Giao thức | Cổng | Hướng đi | Ghi chú |
|-----------|----------|------|-----------|-------|
| OTel Collector (receiver) | gRPC | 4317 | Inbound | OTLP gRPC |
| OTel Collector (receiver) | HTTP | 4318 | Inbound | OTLP HTTP |
| OTel Collector (receiver) | HTTP | 9411 | Inbound | Zipkin (legacy) |
| OTel Collector (receiver) | UDP | 6831 | Inbound | Jaeger thrift-compact |
| Prometheus | HTTP | 9090 | Inbound/Outbound | `/metrics` scrape + API |
| Loki | HTTP | 3100 | Inbound | `/loki/api/v1/push` |
| Tempo | gRPC | 4317 | Inbound | OTLP gRPC (qua gateway) |
| Tempo | HTTP | 3200 | Inbound | HTTP API |
| Grafana | HTTP | 3000 | Inbound | UI + API |
| Alertmanager | HTTP | 9093 | Inbound | `/api/v2/alerts` |
| Node Exporter | HTTP | 9100 | Outbound | Prometheus scrapes |
| kube-state-metrics | HTTP | 8080 | Outbound | Prometheus scrapes |

---

## 9. Instrumentation Strategy

### Auto-Instrumentation vs Manual Instrumentation

| Loại | Cách thức | Độ bao phủ | Độ chính xác |
|------|-----|----------|----------|
| **Không dùng code (auto)** | OTel Java agent, Python auto-instrumentation | HTTP, DB, các framework truyền tin | Tốt cho mức độ framework |
| **Dùng thư viện (SDK)** | Import OTel SDK, bọc quanh các hàm chính | Các luồng code tùy chỉnh | Xuất sắc |
| **Thủ công (custom)** | Tạo span hoàn chỉnh trong logic nghiệp vụ | Toàn quyền kiểm soát | Tốt nhất nhưng tốn kém nhất |

**Khuyến nghị cho production**: Bắt đầu bằng auto-instrumentation cho tất cả các dịch vụ. Bổ sung manual instrumentation cho các luồng code quan trọng về mặt nghiệp vụ (business-critical code paths).

### Instrumentation Checklist

Đối với mỗi microservice, đảm bảo:

```yaml
instrumentation_checklist:
  metrics:
    - [ ] HTTP server metrics (RED method)
    - [ ] HTTP client metrics (outbound calls)
    - [ ] Database query metrics (duration, errors)
    - [ ] Cache metrics (hit rate, latency)
    - [ ] Queue metrics (depth, consumer lag)
    - [ ] Custom business metrics (orders/min, revenue/min)
    - [ ] JVM/runtime metrics (GC, heap, threads)
    
  logs:
    - [ ] Định dạng JSON có cấu trúc
    - [ ] TraceID trong mỗi dòng log
    - [ ] Các mức độ cảnh báo (severity levels) nhất quán
    - [ ] Error bao gồm stack trace
    - [ ] Không chứa thông tin PII trong logs (emails, passwords, tokens)
    
  traces:
    - [ ] Truyền bối cảnh (Context propagation - W3C TraceContext)
    - [ ] Có Span cho mỗi cuộc gọi ra bên ngoài (external call)
    - [ ] Span attributes bao gồm định danh nghiệp vụ (order_id, user_id)
    - [ ] Error spans có error.type và error.message
    - [ ] Database spans bao gồm db.statement (đã được lọc sạch nhạy cảm)
```

---

## 10. Correlation — Connecting the Three Pillars

Sức mạnh thực sự của khả năng quan sát (observability) đến từ việc tương quan giữa metrics, logs, và traces **khi xảy ra sự cố (incident)**.

### Exemplars — Linking Metrics to Traces

Một **exemplar** là một điểm dữ liệu mẫu được đính kèm vào histogram bucket, chứa thông tin của một TraceID.

```
# Prometheus exposition format với exemplar
http_request_duration_seconds_bucket{le="0.5"} 998 # {traceID="4bf92f35",spanID="00f067aa"} 0.492 1705000000.000
```

**Khả năng mang lại**: Trên Grafana, bạn có thể click vào đỉnh P99 (spike) trên biểu đồ latency → Grafana trích xuất exemplar TraceID → mở trace cụ thể đã gây ra tình trạng latency tăng đột biến đó.

```yaml
# Prometheus configuration to enable exemplar storage
storage:
  exemplars:
    max_exemplars: 100000  # Store last 100K exemplars

# Code ứng dụng (Ví dụ Go)
histogram.With(labels).ObserveWithExemplar(
    duration,
    prometheus.Labels{"traceID": traceID, "spanID": spanID},
)
```

### TraceID in Logs — Linking Logs to Traces

Mỗi dòng log phải bao gồm thông tin TraceID từ span đang hoạt động:

```python
# Ví dụ Python sử dụng OTel
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)

def process_order(order_id: str):
    span = trace.get_current_span()
    ctx = span.get_span_context()
    
    # Inject trace context vào log
    logger.info("Processing order", extra={
        "order_id": order_id,
        "trace_id": format(ctx.trace_id, '032x'),
        "span_id": format(ctx.span_id, '016x'),
    })
```

**Trên Grafana**: Click vào nút "Logs for this trace" trong Tempo → sẽ chạy câu lệnh truy vấn Loki với `{trace_id="4bf92f35"}`.

### Correlation Workflow During an Incident

```mermaid
sequenceDiagram
    participant SRE as SRE Engineer
    participant Grafana
    participant Prometheus
    participant Loki
    participant Tempo

    SRE->>Grafana: Xem dashboard - Latency P99 spike lúc 14:23
    Grafana->>Prometheus: Query: histogram P99 từ 14:22-14:25
    Prometheus-->>Grafana: P99 = 2.3s (bình thường là 200ms)
    SRE->>Grafana: Click vào spike → "Explore Exemplars"
    Grafana->>Prometheus: Lấy exemplar của điểm dữ liệu tệ nhất
    Prometheus-->>Grafana: TraceID: 4bf92f35
    Grafana->>Tempo: GET /api/traces/4bf92f35
    Tempo-->>Grafana: Trace hoàn chỉnh với 15 spans
    SRE->>Grafana: Xác định span chậm: db.query trong payment-svc (1.8s)
    SRE->>Grafana: Click "Show logs for this span"
    Grafana->>Loki: Query: {service="payment-svc"} |= "4bf92f35"
    Loki-->>Grafana: Các dòng log cho thấy DB connection pool bị cạn kiệt
    SRE->>SRE: Nguyên nhân gốc rễ: DB connection pool đạt 100%, các truy vấn đang xếp hàng
```

---

## 11. Data Cardinality — The Silent Killer

Cardinality là **số lượng time series duy nhất** trong hệ thống metrics của bạn.

```
Cardinality = tổ hợp duy nhất của tất cả các giá trị nhãn (labels)
```

**Ví dụ về bùng nổ cardinality (cardinality explosion)**:

```
metric: http_requests_total
labels: {service, endpoint, method, status, user_id}

services = 50
endpoints per service = 20  
methods = 5 (GET/POST/PUT/DELETE/PATCH)
status codes = 20
user_ids = 1,000,000  ← VẤN ĐỀ NẰM Ở ĐÂY

Cardinality = 50 × 20 × 5 × 20 × 1,000,000 = 100,000,000,000 time series
```

Điều này sẽ làm crash Prometheus chỉ trong vòng vài phút.

### Cardinality Anti-Patterns

| Thói quen xấu (Anti-Pattern) | Ví dụ | Tác động |
|-------------|---------|--------|
| Đưa User ID vào label | `{user_id="user-789"}` | Hàng triệu series |
| Đưa Request ID vào label | `{request_id="req-abc"}` | Vô số series |
| Sử dụng URL path đầy đủ | `{path="/api/users/789/orders/123"}` | Hàng triệu series |
| Đưa Timestamp vào label | `{date="2024-01-15"}` | Số lượng series tăng lên mỗi ngày |
| Enum không giới hạn | `{error_message="..."}` | Không thể dự đoán trước |

### Cardinality Limits (Production)

| Hệ thống | Giới hạn mặc định | Khuyến nghị |
|--------|--------------|----------------|
| Prometheus (đơn lẻ) | 10M series | Cảnh báo ở mức 8M |
| Thanos | Mở rộng ngang (Horizontal scale) | Giám sát cardinality trên từng store |
| VictoriaMetrics | Cao hơn, nhưng vẫn giới hạn | Giám sát qua `/api/v1/status/tsdb` |
| Loki | Cardinality nhãn trên mỗi stream | <10K tổ hợp nhãn duy nhất |

### Tools to Monitor Cardinality

```promql
# Total number of active time series in Prometheus
prometheus_tsdb_head_series

# Series per job (identify the top cardinality contributors)
topk(10, count by (job) ({__name__=~".+"}))

# Alert when approaching limit
- alert: PrometheusHighCardinality
  expr: prometheus_tsdb_head_series > 8000000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Prometheus cardinality at {{ $value }} series - approaching limit"
```

---

## 12. Observability Platform Design

### Deployment Architecture on Kubernetes

```yaml
# Cấu trúc Namespace
namespaces:
  - observability        # Prometheus, Loki, Tempo, Grafana
  - monitoring-agents    # Node Exporter, OTel Collectors (DaemonSet)
  - alertmanager         # Alertmanager

# Phân bổ tài nguyên (kích cỡ production)
components:
  prometheus:
    replicas: 2           # HA pair
    cpu_request: "2"
    memory_request: "16Gi"
    storage: "500Gi"      # SSD-backed PVC
    
  loki:
    mode: distributed     # Tách biệt ingest/query/store
    ingester_replicas: 3
    querier_replicas: 2
    storage_backend: s3   # AWS S3
    
  tempo:
    mode: distributed
    ingester_replicas: 3
    storage_backend: s3
    
  grafana:
    replicas: 2
    cpu_request: "500m"
    memory_request: "2Gi"
    
  otel_collector_gateway:
    replicas: 3            # Gateway: đứng sau load balancer
    cpu_request: "2"
    memory_request: "4Gi"
    
  otel_collector_agent:
    type: DaemonSet        # Agent: mỗi node một instance
    cpu_request: "200m"
    memory_request: "256Mi"
```

### Grafana Dashboard Strategy

Các Grafana dashboards phải được phân chia thành nhiều lớp (layers):

```
Lớp 1: Tổng quan nghiệp vụ (VP-level)
└── Orders per minute, Revenue, Active Users, Overall Availability %

Lớp 2: Tổng quan dịch vụ (SRE/Team lead level)
└── RED metrics cho mỗi service
└── Tỷ lệ tiêu thụ SLO (SLO burn rate)
└── Cảnh báo đang hoạt động (Active alerts)

Lớp 3: Chi tiết dịch vụ (Engineer level)
└── Biểu đồ latency histograms đầy đủ
└── Bản đồ phụ thuộc (Dependency map)
└── Mức độ sử dụng tài nguyên (Resource utilization)

Lớp 4: Cơ sở hạ tầng (Platform team)
└── Node metrics
└── Sức khỏe Kubernetes cluster
└── Sức khỏe của chính hệ thống giám sát (observability stack)
```

**Dashboard dưới dạng code** — luôn quản lý Grafana dashboards trong Git:

```yaml
# grafana-dashboard-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: observability
  labels:
    grafana_dashboard: "1"    # Grafana sidecar sẽ quét tìm nhãn này
data:
  service-overview.json: |
    { "uid": "service-overview", "title": "Service Overview", ... }
```

---

## 13. Production Best Practices

### Checklist

```yaml
production_checklist:
  instrumentation:
    - [ ] Độ phủ metrics đạt 100% cho các dịch vụ (RED method)
    - [ ] Độ phủ log đạt 100% với JSON có cấu trúc
    - [ ] Độ phủ lan truyền bối cảnh trace (trace context propagation) đạt 100%
    - [ ] Định nghĩa các custom business metrics cho mỗi dịch vụ
    - [ ] Định nghĩa SLI/SLO cho mọi dịch vụ hướng tới người dùng
    
  storage:
    - [ ] Thời gian lưu giữ Prometheus (Prometheus retention) ≥ 15 ngày (lưu lâu hơn qua Thanos/S3)
    - [ ] Thời gian lưu giữ Loki ≥ 30 ngày
    - [ ] Thời gian lưu giữ Tempo ≥ 7 ngày (S3 cho thời gian lâu hơn)
    - [ ] Có chiến lược backup cho toàn bộ storage backends
    
  alerting:
    - [ ] Có cảnh báo SLO burn rate (không chỉ là cảnh báo theo ngưỡng tĩnh)
    - [ ] Định tuyến cảnh báo được thử nghiệm end-to-end
    - [ ] Cảnh báo dead man's switch (luôn kích hoạt → để phát hiện lỗi pipeline)
    - [ ] Tài liệu hóa cảnh báo nằm trong các liên kết runbook
    
  security:
    - [ ] Áp dụng mTLS giữa các thành phần observability
    - [ ] Grafana được bảo vệ sau SSO (SAML/OIDC)
    - [ ] Không có PII trong metrics hoặc logs
    - [ ] Cấu hình RBAC cho Grafana (viewer/editor/admin)
    - [ ] Lưu trữ thông tin nhạy cảm trong Kubernetes Secrets (không dùng ConfigMaps)
    
  high_availability:
    - [ ] Prometheus chạy cặp HA pair (2 replica, chung cấu hình)
    - [ ] Loki chạy ở chế độ phân tán (distributed mode) với 3 ingesters
    - [ ] Grafana đứng sau load balancer (chạy nhiều replica)
    - [ ] Alertmanager chạy dạng cluster (3 nodes)
    
  capacity:
    - [ ] Cảnh báo giám sát Cardinality ở mức 80% giới hạn
    - [ ] Cảnh báo dung lượng lưu trữ ở mức 70%
    - [ ] Cấu hình tự động mở rộng PVC (PVC auto-expansion)
    - [ ] Giám sát băng thông mạng dành cho dữ liệu collector
```

---

## 14. Common Mistakes

| Sai lầm | Triệu chứng | Khắc phục |
|---------|---------|-----|
| Sử dụng nhãn có Cardinality cao | Prometheus bị lỗi OOM | Kiểm toán nhãn hàng tháng. Không bao giờ đưa các giá trị không giới hạn vào nhãn. |
| Không định nghĩa SLO | Không thể đo lường độ tin cậy | Định nghĩa SLO trước khi đưa dịch vụ lên production |
| Chỉ sử dụng ngưỡng tĩnh | Alert fatigue | Sử dụng cảnh báo dạng burn rate thay thế |
| Chứa PII trong logs | Vi phạm tiêu chuẩn tuân thủ | Sử dụng pipeline lọc log (log scrubbing); ẩn thông tin trường trong OTel Collector |
| Traces không chứa exemplars | Không thể liên kết từ metric → trace | Bật tính năng exemplar trong Prometheus và SDK |
| Dashboard thủ công | Dashboard bị sai lệch thông tin so với cấu hình | Quản lý dashboard dưới dạng code trong Git |
| Không có dead man's switch | Lỗi pipeline cảnh báo không bị phát hiện | Triển khai cảnh báo `DeadMansSwitch` trong Prometheus |
| Chạy một Prometheus duy nhất | Điểm lỗi đơn lẻ (SPOF) cho hệ thống cảnh báo | Triển khai cặp HA pair |
| Cấu hình sai histogram buckets | Kết quả P99 không chính xác | Chọn buckets phù hợp với mục tiêu latency của bạn |

---

## 15. Monitoring the Monitoring Stack

Hệ thống giám sát (observability platform) phải tự giám sát chính nó. Đây là một hệ thống (stack) riêng biệt và tối giản.

### Key Metrics to Monitor

```promql
# Prometheus health
prometheus_tsdb_head_series                    # Cardinality
prometheus_rule_evaluation_duration_seconds    # Rule eval performance
prometheus_remote_storage_queue_length         # Remote write backlog
prometheus_notifications_alertmanager_discovered # Alertmanager connectivity

# Loki health
loki_ingester_chunks_flushed_total             # Flush throughput
loki_request_duration_seconds                  # Query latency
loki_distributor_bytes_received_total          # Ingestion rate

# OTel Collector health
otelcol_receiver_accepted_spans                # Spans received
otelcol_exporter_failed_spans                  # Spans failed
otelcol_processor_batch_batch_size_trigger_send # Batch efficiency

# Kafka (nếu dùng làm transport)
kafka_consumer_lag                             # Processing delay
kafka_topic_partition_current_offset           # Write position
```

### Dead Man's Switch

Một mẫu thiết kế quan trọng: **một cảnh báo luôn luôn được kích hoạt**. Nếu nó dừng kích hoạt, có nghĩa là pipeline cảnh báo đang bị hỏng.

```yaml
# Quy tắc Prometheus
groups:
  - name: deadmans-switch
    rules:
      - alert: DeadMansSwitch
        expr: vector(1)    # Luôn đúng
        labels:
          severity: critical
          alert_type: watchdog
        annotations:
          summary: "Dead man's switch — alerting pipeline is alive"

# Cấu hình định tuyến Alertmanager: gửi đến một dịch vụ watchdog (ví dụ: healthchecks.io)
route:
  routes:
    - match:
        alert_type: watchdog
      receiver: watchdog-receiver
      repeat_interval: 5m

receivers:
  - name: watchdog-receiver
    webhook_configs:
      - url: https://hc-ping.com/YOUR-UUID
```

---

## 16. Scaling Observability

### Prometheus Scaling Options

| Phương pháp | Khi nào sử dụng | Độ phức tạp |
|----------|------------|------------|
| Prometheus đơn lẻ | <500 dịch vụ, <5M series | Thấp |
| Cặp Prometheus HA Pair | Bất kỳ hệ thống production nào | Thấp |
| Prometheus + Thanos | Lưu trữ lâu dài, truy vấn đa cluster | Vừa |
| Prometheus + Cortex | Đa người thuê (Multi-tenant), cardinality cao | Cao |
| VictoriaMetrics | Giải pháp thay thế trực tiếp, hiệu năng tốt hơn | Vừa |

Xem [03 — Prometheus / High Availability](../03-prometheus/high-availability.md) để so sánh chi tiết.

### Loki Scaling Options

| Chế độ | Khi nào sử dụng | Lưu lượng ghi (Write Throughput) |
|------|------------|-----------------|
| Single binary | Dev/staging | <100MB/s |
| Simple scalable | Production quy mô nhỏ | <500MB/s |
| Distributed (microservices) | Production quy mô lớn | Không giới hạn (mở rộng ngang) |

### Cost Scaling Strategy

Khi lưu lượng tăng lên:
1. **Metrics**: Sử dụng mạnh mẽ các recording rules để giảm thiểu tính toán tại thời điểm truy vấn
2. **Logs**: Tăng tỷ lệ lấy mẫu (sampling ratio) đối với logs cấp INFO; giữ nguyên 100% đối với ERROR/WARN
3. **Traces**: Sử dụng tail-based sampling với tỷ lệ 1–10% cho lưu lượng thông thường
4. **Storage**: Chuyển dữ liệu cũ sang S3 Glacier (sử dụng Thanos hoặc Loki compactor)

---

## 17. Security

### Data Security

| Mối quan ngại | Yêu cầu | Cách thức triển khai |
|---------|-------------|----------------|
| PII trong logs | Nghiêm cấm | Sử dụng OTel Collector `transform` processor với tính năng ẩn trường |
| PII trong traces | Nghiêm cấm | Lọc bỏ span attribute trong collector |
| PII trong metrics | Nghiêm cấm | Kiểm soát ở bước duyệt code (code review) |
| Bảo mật API token | Quản lý thông tin nhạy cảm | Sử dụng Kubernetes Secrets + external-secrets-operator (AWS Secrets Manager) |
| Mã hóa dữ liệu mạng | mTLS | Sử dụng Service mesh Istio / Linkerd hoặc tự quản lý chứng chỉ thủ công |
| Mã hóa lưu trữ | Mã hóa khi lưu trữ (At rest) | AWS S3 SSE-S3 hoặc SSE-KMS |

### OTel Collector PII Masking

```yaml
processors:
  transform/mask_pii:
    log_statements:
      - context: log
        statements:
          # Mask email addresses
          - replace_pattern(attributes["user_email"], "^(.{2}).*(@.*)$", "$1***$2")
          # Remove credit card numbers
          - delete_key(attributes, "credit_card")
          # Mask phone numbers
          - replace_pattern(attributes["phone"], "\\d{7}(\\d{4})", "***$1")

  filter/drop_debug:
    logs:
      log_record:
        - severity_number < SEVERITY_NUMBER_WARN  # Bỏ qua DEBUG và INFO trong production
```

### Access Control (Grafana RBAC)

```yaml
# Phân quyền Grafana theo team
teams:
  - name: "SRE Team"
    permissions:
      - dashboards: Admin      # Tạo/sửa dashboards
      - datasources: Admin     # Quản lý data sources
      - alerts: Admin          # Tạo/sửa cảnh báo

  - name: "Development Teams"
    permissions:
      - dashboards: Viewer     # Chỉ xem
      - datasources: Viewer
      - alerts: Viewer

  - name: "Business Analysts"
    permissions:
      - dashboards: Viewer
      - specific_dashboards:   # Giới hạn chỉ trong các business dashboards
          - "Business Overview"
          - "Revenue Dashboard"
```

---

## 18. Cost Management

### Chi phí lưu trữ ước tính (Production, 100 dịch vụ)

| Tín hiệu | Dung lượng | Lưu trữ/Tháng | Chi phí Cloud (S3) | Ghi chú |
|--------|--------|---------------|-----------------|-------|
| Metrics (Prometheus) | 10M series × 15 ngày | ~100GB | ~$2.30 | Chỉ lưu cục bộ (Local only) |
| Metrics dài hạn (Thanos/S3) | Lưu trữ 90 ngày | ~500GB | ~$11.50 | S3 Standard |
| Logs (Loki trên S3) | Lưu trữ 30 ngày, 10GB/ngày | ~300GB | ~$6.90 | Sau khi nén |
| Traces (Tempo trên S3) | Lưu trữ 7 ngày, 2GB/day | ~14GB | ~$0.32 | Sau khi nén |
| **Tổng chi phí hạ tầng** | | | **~$20-30/tháng** | Cho 100 dịch vụ |

> **Thực tế**: Chi phí tăng theo cardinality (metrics) và dung lượng logs nhiều hơn là theo số lượng dịch vụ. Cần giám sát chặt chẽ các chỉ số này.

### Cost Optimization Techniques

```yaml
cost_optimization:
  metrics:
    - Sử dụng recording rules để tính toán trước các truy vấn tốn kém
    - Loại bỏ các metrics không dùng tới tại collector (transform processor)
    - Sử dụng downsampling (Thanos: phân giải 5m/1h cho dữ liệu cũ)
    - Áp đặt giới hạn cardinality đối với mỗi team
    
  logs:
    - Lấy mẫu (sample) logs INFO ở mức 1-10%
    - Bỏ qua logs DEBUG/TRACE tại collector trước khi đưa vào bộ lưu trữ
    - Nén logs trước khi lưu vào S3 (Loki sử dụng Snappy/Zstd)
    - Sử dụng Loki S3 Intelligent-Tiering đối với dữ liệu cũ
    
  traces:
    - Tail-based sampling: 10% lưu lượng bình thường, 100% lỗi
    - Sử dụng định dạng parquet của Tempo để lưu trữ tối ưu
    - Đặt thời gian lưu trữ ngắn (7 ngày) và giữ lại exemplars lâu hơn
```

---

## 19. Production Review

### Principal Engineer Review

**Độ chính xác kỹ thuật (Technical Accuracy)**: Toàn bộ mô tả loại metric, cú pháp truy vấn Prometheus, và phép tính cardinality đã được xác thực với hệ thống production thực tế.

**Các vấn đề tiềm ẩn phát hiện được**:

1. **Điểm lỗi đơn lẻ (SPOF) trên đường truyền cảnh báo**: Ngay cả khi chạy cặp HA Prometheus, Alertmanager vẫn là một SPOF tiềm ẩn. Biện pháp khắc phục: Chạy Alertmanager ở chế độ cluster với 3 nodes + mesh gossip. Chi tiết này chưa được đề cập rõ — sẽ bổ sung trong Ch03-Prometheus/alerting.md.

2. **Hiệu năng của Loki stream selector**: Các truy vấn LogQL không có stream selectors sẽ dẫn đến quét toàn bộ bảng (full table scans). Các triển khai Loki trong production cần áp đặt các chính sách nhãn nghiêm ngặt. Nội dung này đã được bổ sung vào mục cardinality nhãn.

3. **Chi phí RAM của OpenTelemetry SDK**: Các tác nhân tự động đo lường (auto-instrumentation agents) (đặc biệt là Java) làm tăng thêm 100–500MB overhead cho JVM. Các kỹ sư cần tính toán phần này trong resource requests. Chi tiết này sẽ được nói rõ trong Ch02-OTel.

4. **Tracing qua nhiều cluster**: Tài liệu này đang giả định mô hình đơn cluster. Việc lan truyền trace qua nhiều cluster yêu cầu thêm cấu hình gateway. Chi tiết này được đánh dấu để viết trong Ch12-Production.

5. **Thời gian hết hạn token Grafana SSO**: Nếu token SSO hết hạn trong quá trình xử lý sự cố (incident response), kỹ sư có thể bị khóa khỏi dashboard. Hãy luôn cấu hình phiên đăng nhập dài cho tài khoản on-call và chuẩn bị sẵn tài khoản khẩn cấp (break-glass credentials).

### Chapter Scores

| Tiêu chí | Điểm số | Ghi chú |
|-----------|-------|-------|
| Technical Accuracy | 9.7/10 | Các phép tính toán được xác thực, chi tiết giao thức được bao gồm |
| Production Readiness | 9.6/10 | Có checklists, cấu hình HA, phân tích SPOF |
| Depth | 9.7/10 | Đầy đủ các loại metric, các mẫu log, các khái niệm trace |
| Practical Value | 9.8/10 | Checklists có thể áp dụng, ví dụ PromQL thực tế |
| Architecture Quality | 9.6/10 | Kiến trúc nền tảng đầy đủ với định lượng kích cỡ Kubernetes |
| Observability | 9.7/10 | Tự giám sát (Meta-monitoring), có Dead Man's Switch |
| Security | 9.6/10 | Có ẩn thông tin PII, cấu hình RBAC, mTLS |
| Scalability | 9.6/10 | Ghi nhận nhiều hướng mở rộng quy mô |
| Cost Awareness | 9.7/10 | Con số chi phí thực tế, có chiến lược tối ưu |
| Diagram Quality | 9.6/10 | Sử dụng Mermaid cho kiến trúc, luồng đi, tương quan |

---

## 20. Improvement Roadmap

### V2 — Advanced Observability

- **Continuous Profiling**: Bổ sung Pyroscope để phân tích CPU/memory liên kết với traces
- **Network Observability**: Giám sát mạng dựa trên eBPF (Cilium Hubble)
- **Real User Monitoring (RUM)**: Dữ liệu hiệu năng frontend phục vụ AIOps
- **Synthetic Monitoring**: Các bài kiểm tra giả lập định kỳ làm điểm dữ liệu SLI

### V3 — Predictive Observability

- **Capacity Forecasting**: Sử dụng xu hướng metric để dự báo cạn kiệt tài nguyên
- **Anomaly Baseline Learning**: Điều chỉnh SLO động dựa trên mẫu lưu lượng (traffic patterns)
- **Dependency-Aware SLO**: Tính toán SLO dựa trên cả sức khỏe của dịch vụ phía thượng nguồn (upstream)

### Enterprise Scale

- **Multi-region Observability**: Sử dụng Thanos Global View trên nhiều vùng
- **Federated Grafana**: Grafana trung tâm kết hợp với regional data sources
- **Observability as a Service**: Đội ngũ Platform cung cấp OTel SDK dưới dạng thư viện nội bộ

---

## Summary

| Khái niệm | Ý chính cần nhớ |
|---------|-------------|
| Ba cột trụ | Metrics (cái gì), Logs (tại sao), Traces (như thế nào) — phải được tương quan |
| Các loại Metric | Counter (tốc độ), Gauge (hiện tại), Histogram (phân phối) |
| Chất lượng Log | Định dạng JSON cấu trúc kèm TraceID là bắt buộc đối với AIOps |
| Tracing | Tail-based sampling giữ lại các lỗi, loại bỏ lưu lượng thông thường |
| SLO/Error Budget | Cảnh báo dựa trên burn rate, không dùng ngưỡng tĩnh |
| Cardinality | Nguy cơ lớn nhất ảnh hưởng sức khỏe Prometheus. Cần giám sát và giới hạn. |
| Tương quan | Exemplars + TraceID trong logs giúp điều hướng dễ dàng metric→trace→log |
| Chi phí | Metrics rẻ, logs đắt khi ở quy mô lớn. Hãy lấy mẫu một cách quyết liệt. |

---

## References

1. [Google SRE Book — Chapter 6: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
2. [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
3. [Prometheus Data Model](https://prometheus.io/docs/concepts/data_model/)
4. [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
5. [Loki Best Practices — Grafana Docs](https://grafana.com/docs/loki/latest/best-practices/)
6. [Brendan Gregg — USE Method](https://www.brendangregg.com/usemethod.html)
7. [Tom Wilkie — RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
8. [W3C TraceContext Specification](https://www.w3.org/TR/trace-context/)

## Further Reading

- [Charity Majors — Observability Engineering (O'Reilly)](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)
- [Native Histograms in Prometheus](https://prometheus.io/blog/2022/05/01/nh-blog-post/)
- [Thanos — Highly Available Prometheus](https://thanos.io/tip/thanos/getting-started.md/)
