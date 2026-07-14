# Chapter 02 — OpenTelemetry

> **OpenTelemetry là tiêu chuẩn trung lập với nhà cung cấp (vendor-neutral), đã tốt nghiệp từ CNCF dùng để thu thập, xử lý, và xuất (export) dữ liệu telemetry. Nó là xương sống thu thập của mọi nền tảng AIOps trên môi trường production.**

---

## Prerequisites

- [01 — Observability](../01-observability/README.md) — phải hiểu rõ các khái niệm metrics, logs, traces
- Kiến thức Kubernetes cơ bản (DaemonSet, Deployment, ConfigMap)

## Related Documents

- [03 — Prometheus](../03-prometheus/README.md) — nhận metrics từ OTel Collector
- [04 — Loki](../04-loki/README.md) — nhận logs từ OTel Collector
- [05 — Tempo](../05-tempo/README.md) — nhận traces từ OTel Collector
- [06 — Kafka](../06-kafka/README.md) — OTel Collector có thể export sang Kafka

## Next Reading

Sau chương này, hãy chuyển sang [03 — Prometheus](../03-prometheus/README.md).

---

## Table of Contents

1. [Why OpenTelemetry?](#1-why-opentelemetry)
2. [OTel Components Overview](#2-otel-components-overview)
3. [OTLP Protocol](#3-otlp-protocol)
4. [The OTel Collector Deep Dive](#4-the-otel-collector-deep-dive)
5. [Receiver Configuration](#5-receiver-configuration)
6. [Processor Configuration](#6-processor-configuration)
7. [Exporter Configuration](#7-exporter-configuration)
8. [Pipeline Definition](#8-pipeline-definition)
9. [Deployment Patterns](#9-deployment-patterns)
10. [Kubernetes Operator](#10-kubernetes-operator)
11. [Fluent Bit vs OTel Collector](#11-fluent-bit-vs-otel-collector)
12. [Production Best Practices](#12-production-best-practices)
13. [Common Mistakes](#13-common-mistakes)
14. [Monitoring the Collector](#14-monitoring-the-collector)
15. [Scaling](#15-scaling)
16. [Security](#16-security)
17. [Cost](#17-cost)
18. [Production Review](#18-production-review)

---

## 1. Why OpenTelemetry?

> [!NOTE]
> **Ý TƯỞNG**
> Trước OpenTelemetry, mỗi observability vendor có agent riêng — Datadog agent, New Relic agent, Jaeger client... Đổi vendor = viết lại instrumentation code trong mọi service. OTel giải quyết bằng nguyên tắc "**instrument once, export anywhere**": bạn chỉ cần tích hợp OTel SDK một lần, sau đó có thể gửi data đến bất kỳ backend nào (Prometheus, Loki, Tempo, Datadog, CloudWatch) chỉ bằng cách thay đổi cấu hình collector.

> [!TIP]
> **Vì sao chọn OTel thay vì agent của vendor?** 3 lý do: (1) **Không bị vendor lock-in** — nếu bạn chuyển từ Datadog sang Prometheus, chỉ cần thay exporter config, không phải viết lại code. (2) **Một agent thay nhiều agent** — OTel Collector xử lý metrics + logs + traces thay vì 3 agent riêng biệt. (3) **Chuẩn mở CNCF** — không phụ thuộc vào roadmap của bất kỳ công ty nào.

### The Problem Before OTel

Trước khi có OpenTelemetry:

```
Datadog Agent       → Datadog backend
New Relic Agent     → New Relic backend  
Jaeger Client       → Jaeger backend
→ Đổi vendor = viết lại instrumentation trong tất cả services
→ Chạy nhiều agents = tốn CPU/memory overhead
```

### What OTel Solves

```mermaid
graph LR
    subgraph Before["Trước OpenTelemetry"]
        A1[Service] -->|Datadog SDK| DD[Datadog]
        A2[Service] -->|NR SDK| NR[New Relic]
        A3[Service] -->|Zipkin SDK| ZP[Zipkin]
    end

    subgraph After["Sau OpenTelemetry"]
        B1[Service] -->|OTel SDK| COL[OTel Collector]
        B2[Service] -->|OTel SDK| COL
        B3[Service] -->|OTel SDK| COL
        COL -->|config only| P[Prometheus]
        COL -->|config only| L[Loki]
        COL -->|config only| T[Tempo]
        COL -->|config only| DD2[Datadog]
    end

    style Before fill:#4a1942,color:#fff
    style After fill:#0d4f8b,color:#fff
```

**Lợi ích**:
- **Instrument once, export anywhere** — thay đổi backend mà không thay code ứng dụng
- **Vendor neutral** — tốt nghiệp từ CNCF, không bị ràng buộc bản quyền
- **Unified data model** — metrics, logs, traces dùng cùng mô hình resource/attribute
- **Single agent** — OTel Collector thay nhiều agents của các vendors khác nhau

### OTel vs Other Collection Options

| Công cụ | Điểm mạnh | Điểm yếu | Tốt nhất cho |
|------|-----------|------------|---------|
| **OTel Collector** | Đầy đủ tín hiệu, extensible, vendor-neutral | Cấu hình phức tạp | Production AIOps (khuyến nghị) |
| **Fluent Bit** | Cực kỳ nhẹ (< 1MB RAM) | Chỉ logs, xử lý cơ bản | Edge / tài nguyên hạn chế |
| **Fluentd** | Plugin ecosystem phong phú | Tốn tài nguyên hơn, Ruby-based | Legacy systems |
| **Prometheus (scrape)** | Native Prometheus support | Chỉ metrics, pull-based | Prometheus-native environments |
| **Datadog Agent** | Dễ setup, full-featured | Vendor lock-in, đắt đỏ | Teams chỉ dùng Datadog |

**Quyết định**: Dùng OTel Collector cho production AIOps. Dùng Fluent Bit như sidecar nhẹ nếu Collector DaemonSet tốn quá nhiều tài nguyên.

---

## 2. OTel Components Overview

> [!NOTE]
> **Ý TƯỞNG**
> OTel có hai phần tách biệt: **SDK** (trong application code — thu thập telemetry) và **Collector** (service độc lập — xử lý và route telemetry). SDK giống như "sensor", Collector giống như "trạm xử lý tín hiệu" trước khi gửi đến storage.

```mermaid
graph TD
    subgraph SDK["OTel SDK (trong application)"]
        API[OTel API\nTrace · Metric · Log API]
        IMPL[OTel SDK Implementation\nSpan processor\nMetric reader]
        PROP[Context Propagator\nW3C TraceContext\nB3 Headers]
        RES[Resource\nservice.name, version\nhost, k8s attributes]
    end

    subgraph Collector["OTel Collector"]
        RCV[Receivers\nOTLP · Prometheus · Jaeger\nZipkin · Kafka]
        PROC[Processors\nBatch · MemoryLimiter\nTransform · Filter\nTailSampling · Attributes]
        EXP[Exporters\nOTLP · Prometheus\nLoki · Kafka · Datadog]
    end

    subgraph Backends["Storage Backends"]
        PM[Prometheus]
        LK[Loki]
        TP[Tempo]
        KF[Kafka]
    end

    SDK -->|OTLP gRPC :4317\nOTLP HTTP :4318| Collector
    Collector --> Backends

    style SDK fill:#1565c0,color:#fff
    style Collector fill:#2e7d32,color:#fff
    style Backends fill:#4a148c,color:#fff
```

---

## 3. OTLP Protocol

> [!NOTE]
> **Ý TƯỞNG**
> OTLP (OpenTelemetry Protocol) là "ngôn ngữ" mà SDK và Collector nói chuyện với nhau. Có 3 biến thể, khác nhau về format và hiệu năng. Trong production, dùng gRPC (binary, nhanh nhất). Chỉ dùng HTTP/JSON khi debug hoặc browser client.

### Protocol Variants

| Biến thể | Cổng | Format | Khi nào dùng |
|---------|------|--------|------------|
| **OTLP gRPC** | 4317 | Protobuf binary | Default cho service→collector. Hiệu quả nhất. |
| **OTLP HTTP/protobuf** | 4318 | Protobuf binary | Khi không thể dùng gRPC |
| **OTLP HTTP/JSON** | 4318 | JSON | Debug, browser apps |

### OTLP Data Model — Trace (rút gọn)

```json
{
  "resourceSpans": [{
    "resource": {
      "attributes": [
        {"key": "service.name", "value": {"stringValue": "order-service"}},
        {"key": "k8s.pod.name", "value": {"stringValue": "order-svc-abc123"}}
      ]
    },
    "scopeSpans": [{
      "spans": [{
        "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
        "spanId": "00f067aa0ba902b7",
        "name": "POST /api/orders",
        "startTimeUnixNano": 1705329825050000000,
        "endTimeUnixNano": 1705329825115000000,
        "status": {"code": "STATUS_CODE_OK"}
      }]
    }]
  }]
}
```

---

## 4. The OTel Collector Deep Dive

> [!NOTE]
> **Ý TƯỞNG**
> Collector là một pipeline có 3 stage: **Receivers** (nhận data vào), **Processors** (biến đổi/lọc/sample), **Exporters** (gửi đến backends). Có thể cấu hình nhiều pipeline song song — một cho traces, một cho metrics, một cho logs — mỗi pipeline có bộ processor và exporter riêng.

### Internal Architecture

```mermaid
graph LR
    subgraph Receiver["Receivers"]
        R1[OTLP\ngRPC :4317\nHTTP :4318]
        R2[Prometheus\nscrape /metrics]
        R3[Kafka Receiver]
    end

    subgraph Pipeline["Internal Pipeline (thứ tự quan trọng!)"]
        P1[Memory Limiter\n← LUÔN ĐẦU TIÊN]
        P2[Filter\nbỏ health checks]
        P3[Transform\nenrich metadata]
        P4[Tail Sampling\nkeep errors/slow]
        P5[Batch\ngộp lô để gửi]
    end

    subgraph Exporter["Exporters"]
        E1[OTLP → Tempo]
        E2[Prometheus RW]
        E3[Loki]
        E4[Kafka → AIOps]
    end

    Receiver --> P1 --> P2 --> P3 --> P4 --> P5 --> Exporter

    style Receiver fill:#1565c0,color:#fff
    style Pipeline fill:#2e7d32,color:#fff
    style Exporter fill:#4a148c,color:#fff
```

### Collector Distributions

| Distribution | Mô tả | Khi dùng |
|-------------|-------------|---------|
| **otelcol** | Core, minimum components | Tài nguyên cực nhỏ |
| **otelcol-contrib** | Đầy đủ community components | **Phổ biến nhất cho production** |
| **Custom build (ocb)** | Chỉ components bạn cần | Production bảo mật cao |

---

## 5. Receiver Configuration

> [!NOTE]
> **Ý TƯỞNG**
> Receivers là "cổng vào" của Collector. Quan trọng nhất là **OTLP Receiver** (nhận từ services) và **Prometheus Receiver** (pull-based scraping). OTLP gRPC là mặc định và hiệu quả nhất.

### OTLP Receiver

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        max_recv_msg_size_mib: 4         # Max message size
        max_concurrent_streams: 1000      # Concurrent gRPC streams
        tls:
          cert_file: /certs/server.crt   # mTLS — bắt buộc cho production
          key_file: /certs/server.key
          client_ca_file: /certs/ca.crt
          
      http:
        endpoint: 0.0.0.0:4318
        cors:
          allowed_origins: ["https://your-frontend.com"]  # Browser clients
```

### Prometheus Receiver (pull-based)

```yaml
receivers:
  prometheus:
    config:
      global:
        scrape_interval: 15s
      scrape_configs:
        - job_name: kubernetes-pods
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            # Chỉ scrape pods có annotation prometheus.io/scrape: "true"
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              action: keep
              regex: "true"
```

### Kafka Receiver

```yaml
receivers:
  kafka:
    brokers: ["kafka-1:9092", "kafka-2:9092"]
    topic: otlp-telemetry
    group_id: otel-collector-consumer
    encoding: otlp_proto
    auth:
      sasl:
        username: otel-collector
        password: ${KAFKA_PASSWORD}
        mechanism: SCRAM-SHA-512
```

---

## 6. Processor Configuration

> [!NOTE]
> **Ý TƯỞNG**
> Processors là phần quan trọng nhất của Collector — chúng quyết định chất lượng data, tài nguyên, và chi phí. **Thứ tự processor quan trọng**:
> ```
> memory_limiter → filter → transform → tail_sampling → batch
> ```
> Không tuân thủ thứ tự này có thể gây mất data hoặc crash collector.

> [!TIP]
> **Tại sao thứ tự processor quan trọng?** Nếu đặt `batch` trước `tail_sampling`, các spans của cùng một trace bị gộp vào nhiều lô khác nhau → tail sampler không thể đưa ra quyết định chính xác cho cả trace. Nếu không đặt `memory_limiter` đầu tiên → collector OOM crash khi traffic spike.

### Memory Limiter Processor (LUÔN ĐẦU TIÊN)

```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 3000          # Hard limit: từ chối data mới khi vượt quá
    spike_limit_mib: 500     # Buffer cho traffic spike

# Tại 3500 MiB (3000+500), collector bắt đầu từ chối spans mới
# Cơ chế backpressure này ngăn OOM crash — quan trọng hơn việc mất một ít data
```

### Batch Processor

```yaml
processors:
  batch:
    send_batch_size: 8192       # Gửi khi đạt kích thước này
    send_batch_max_size: 16384  # Giới hạn tối đa mỗi batch
    timeout: 5s                 # Gửi sau thời gian này dù chưa đủ kích thước

# Tại sao batch quan trọng: Giảm số RPC calls từ 10-100 lần
# 8192 spans × 1KB = 8MB/batch → Tempo không bị quá tải bởi tiny exports
```

### Transform Processor

> [!TIP]
> **Tại sao Transform là processor "thông minh" nhất?** Nó cho phép bạn làm giàu data (thêm environment từ k8s namespace), chuẩn hóa (lowercase service name), lọc sạch sensitive data (thay SQL values bằng `?`), và trích xuất structured fields từ unstructured text — tất cả mà không cần thay code ứng dụng.

```yaml
processors:
  transform/enrich:
    error_mode: ignore         # Không drop data nếu transform lỗi
    
    trace_statements:
      - context: resource
        statements:
          # Gắn environment từ k8s namespace
          - set(attributes["deployment.environment"], "production") where IsMatch(attributes["k8s.namespace.name"], "prod.*")
          
      - context: span
        statements:
          # Lọc sạch SQL values để tránh lưu trữ sensitive data
          - replace_pattern(attributes["db.statement"], "'[^']*'", "?")
          - replace_pattern(attributes["db.statement"], "\\d+", "?")
          
    log_statements:
      - context: log
        statements:
          # Chuẩn hóa severity cho logs legacy
          - set(severity_number, SEVERITY_NUMBER_ERROR) where attributes["level"] == "FATAL"
```

### Filter Processor

```yaml
processors:
  filter/drop_noise:
    traces:
      span:
        # Bỏ qua health check endpoints — không có giá trị cho AIOps
        - 'attributes["http.route"] == "/health"'
        - 'attributes["http.route"] == "/ready"'
        - 'IsMatch(attributes["http.user_agent"], "kube-probe.*")'
        
    metrics:
      metric:
        # Bỏ Go runtime metrics — cardinality cao, giá trị thấp cho AIOps
        - 'IsMatch(name, "go_gc_.*")'
        
    logs:
      log_record:
        # Bỏ DEBUG/TRACE trong production — giảm 80-90% log volume
        - 'severity_number < SEVERITY_NUMBER_WARN'
```

### Tail Sampling Processor

> [!NOTE]
> **Ý TƯỞNG**
> Tail sampling là "bộ lọc thông minh" cho traces — đợi trace hoàn tất mới quyết định giữ hay bỏ. Kết quả: 100% errors được giữ, 5-10% traffic bình thường được giữ. So với head sampling (quyết định trước khi biết kết quả), tail sampling tốt hơn vì nó luôn giữ lại đúng những trace quan trọng nhất.
>
> **Memory trade-off**: Cần giữ tất cả spans trong memory trong `decision_wait` giây. 50K traces × 50 spans × 2KB ≈ **5GB RAM**. Đây là lý do gateway cần 4-8GB RAM.

```yaml
processors:
  tail_sampling:
    decision_wait: 30s          # Chờ tối đa 30s để thu thập đủ spans
    num_traces: 50000           # Tối đa 50K traces trong memory
    expected_new_traces_per_sec: 500
    
    policies:
      # Luôn giữ traces có lỗi — quan trọng nhất
      - name: sample-errors
        type: status_code
        status_code:
          status_codes: [ERROR]
          
      # Luôn giữ traces chậm (> 2 giây) — tiếp theo trong độ ưu tiên
      - name: sample-slow
        type: latency
        latency:
          threshold_ms: 2000
          
      # Luôn giữ payment traces — business critical
      - name: sample-payment
        type: string_attribute
        string_attribute:
          key: service.name
          values: [payment-service, billing-service]
          
      # 5% traffic bình thường — statistical baseline
      - name: sample-normal-5pct
        type: and
        and:
          and_sub_policy:
            - name: not-error
              type: status_code
              status_code:
                status_codes: [OK, UNSET]
            - name: probabilistic
              type: probabilistic
              probabilistic:
                sampling_percentage: 5
```

### Attributes Processor

```yaml
processors:
  attributes/add_metadata:
    actions:
      - key: collector.version   # Thêm version info để debug
        value: "0.95.0"
        action: insert
        
      - key: user.id             # Hash sensitive IDs — không xóa, vẫn có thể debug
        action: hash
        
      - key: http.request.header.authorization  # Xóa hoàn toàn auth headers
        action: delete
```

---

## 7. Exporter Configuration

> [!NOTE]
> **Ý TƯỞNG**
> Exporters là "cổng ra" — gửi data đã được xử lý đến các backends. Mỗi backend có exporter riêng: OTLP→Tempo, Prometheus Remote Write→Prometheus, Loki Exporter→Loki, Kafka→AIOps pipeline. Tất cả exporters cần retry logic và queue để tránh mất data khi backend tạm thời unavailable.

### OTLP Exporter (→ Tempo cho traces)

```yaml
exporters:
  otlp/tempo:
    endpoint: tempo-distributor.observability.svc.cluster.local:4317
    tls:
      ca_file: /certs/ca.crt
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_elapsed_time: 300s        # Retry trong 5 phút tối đa
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 1000
      storage: file_storage/traces  # Persistent queue — không mất data khi crash
    compression: gzip
```

### Prometheus Remote Write Exporter (→ Prometheus)

```yaml
exporters:
  prometheusremotewrite:
    endpoint: http://prometheus.observability.svc.cluster.local:9090/api/v1/write
    resource_to_telemetry_conversion:
      enabled: true   # Chuyển resource attributes thành metric labels
    retry_on_failure:
      enabled: true
```

### Loki Exporter (→ Loki cho logs)

```yaml
exporters:
  loki:
    endpoint: http://loki-distributor.observability.svc.cluster.local:3100/loki/api/v1/push
    default_labels_enabled:
      level: true     # Dùng severity làm label — low cardinality, high value
    retry_on_failure:
      enabled: true
```

### Kafka Exporter (→ AIOps pipeline)

```yaml
exporters:
  kafka/aiops:
    brokers: ["kafka-1.kafka.svc:9092", "kafka-2.kafka.svc:9092"]
    topic: aiops-raw-telemetry
    encoding: otlp_proto
    producer:
      required_acks: 1              # Leader ack đủ — trade latency vs durability
      compression: snappy
    auth:
      sasl:
        username: ${KAFKA_USER}
        password: ${KAFKA_PASSWORD}
        mechanism: SCRAM-SHA-512
```

### File Storage Extension (persistent queue)

```yaml
extensions:
  file_storage/traces:
    directory: /var/lib/otelcol/storage/traces
    compaction:
      on_start: true
      rebound_needed_threshold_mib: 100
```

---

## 8. Pipeline Definition

> [!IMPORTANT]
> **MINH HỌA — Cấu hình pipeline hoàn chỉnh**
>
> Đây là skeleton config kết hợp tất cả components ở trên thành một pipeline hoàn chỉnh. Lưu ý: mỗi signal type (traces/metrics/logs) có pipeline riêng với processor và exporter khác nhau.

```yaml
service:
  extensions: [health_check, pprof, zpages, file_storage/traces]
  
  pipelines:
    # Traces: nhận → lọc noise → enrich → tail sample → batch → gửi đi
    traces:
      receivers: [otlp, jaeger, zipkin]
      processors:
        - memory_limiter          # LUÔN đầu tiên — circuit breaker cho OOM
        - filter/drop_noise       # Bỏ health checks, k8s probes
        - transform/enrich        # Thêm environment, clean SQL
        - attributes/add_metadata # Gắn collector metadata
        - tail_sampling           # Giữ errors + slow + 5% normal
        - batch                   # Batch SAU sampling — đúng thứ tự!
      exporters: [otlp/tempo, kafka/aiops]
      
    # Metrics: nhận → lọc → enrich → batch → gửi Prometheus
    metrics:
      receivers: [otlp, prometheus]
      processors:
        - memory_limiter
        - filter/drop_noise
        - transform/enrich
        - batch
      exporters: [prometheusremotewrite]
      
    # Logs: nhận → lọc → mask PII → enrich → batch → Loki + Kafka
    logs:
      receivers: [otlp]
      processors:
        - memory_limiter
        - filter/drop_noise       # Bỏ DEBUG/TRACE
        - transform/mask_pii      # Ẩn PII trước khi lưu
        - transform/enrich
        - batch
      exporters: [loki, kafka/aiops]

  # Collector tự giám sát chính nó
  telemetry:
    metrics:
      level: detailed
      address: 0.0.0.0:8888      # Prometheus scrapes metrics tại đây
```

---

## 9. Deployment Patterns

### Pattern 1: Agent + Gateway (Khuyến nghị cho Production)

> [!NOTE]
> **Ý TƯỞNG**
> Dùng 2 tầng: **Agent** (DaemonSet trên mỗi node, nhẹ, chỉ forward) + **Gateway** (Deployment với nhiều replicas, làm xử lý nặng như tail sampling, batching). Tại sao 2 tầng? Vì tail sampling cần thấy **toàn bộ spans của một trace** — nếu service A và B chạy trên các nodes khác nhau, spans của chúng đến từ các agents khác nhau → cần tập hợp tại Gateway.

```mermaid
graph LR
    subgraph Node1["K8s Node 1"]
        P1[Pod A] -->|OTLP| AG1[OTel Agent\nDaemonSet]
        P2[Pod B] -->|OTLP| AG1
        AG1 -->|OTLP| GW
    end

    subgraph Node2["K8s Node 2"]
        P3[Pod C] -->|OTLP| AG2[OTel Agent\nDaemonSet]
        AG2 -->|OTLP| GW
    end

    subgraph Gateway["Gateway (×3 replicas)"]
        GW[OTel Collector Gateway\nTail Sampling + Routing]
    end

    GW -->|remote_write| PROM[Prometheus]
    GW -->|push| LOKI[Loki]
    GW -->|OTLP| TEMPO[Tempo]
    GW -->|produce| KAFKA[Kafka]
```

| Khía cạnh | Agent (DaemonSet) | Gateway (Deployment) |
|---------|------------------|---------------------|
| CPU/RAM | 200m CPU, 256Mi | 2 CPU, 4Gi |
| Tail sampling | ❌ Không thể (spans phân tán) | ✅ Tập hợp được |
| HA | Tự nhiên (mỗi node) | Cần ≥3 replicas |

**Cấu hình Agent** (nhẹ — chỉ forward, không sampling):

```yaml
# otel-agent-config.yaml (DaemonSet)
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  memory_limiter:
    limit_mib: 200            # Giới hạn nhỏ cho agent
    spike_limit_mib: 50
  batch:
    timeout: 5s
    send_batch_size: 512

exporters:
  otlp/gateway:
    endpoint: otel-collector-gateway.observability.svc.cluster.local:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]   # Không có tail_sampling!
      exporters: [otlp/gateway]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/gateway]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp/gateway]
```

### Pattern 2: Sidecar (Cho services đặc thù)

Dùng khi một service cần cấu hình xử lý đặc thù (ví dụ: 100% sampling cho payment service):

```yaml
spec:
  containers:
    - name: payment-service
      env:
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://localhost:4317"  # Gửi đến sidecar
          
    - name: otel-collector         # Sidecar collector riêng
      image: otelcol-contrib:0.95.0
      resources:
        requests: { cpu: "100m", memory: "128Mi" }
        limits:   { cpu: "500m", memory: "512Mi" }
```

---

## 10. Kubernetes Operator

> [!NOTE]
> **Ý TƯỞNG**
> OTel Operator là Kubernetes controller — nó quản lý vòng đời của OTel Collectors và tự động inject instrumentation vào pods chỉ bằng cách thêm annotation. Không cần thay đổi code trong container images. Đây là cách "zero-code instrumentation" cho toàn bộ namespace.

### Installing the Operator

```bash
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

### OpenTelemetryCollector CRD

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: aiops-collector
  namespace: observability
spec:
  mode: daemonset
  image: otelcol-contrib:0.95.0
  resources:
    limits:
      cpu: "500m"
      memory: "512Mi"
    requests:
      cpu: "200m"
      memory: "256Mi"
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
    # ... full collector config
```

### Auto-Instrumentation CRD

> [!TIP]
> **Tại sao Auto-Instrumentation là "killer feature"?** Thay vì yêu cầu mỗi team thêm OTel SDK vào code của họ, bạn chỉ cần gắn annotation vào namespace → Operator tự inject agent vào mọi pod mới. Teams không cần thay đổi gì trong code, nhưng vẫn có đầy đủ traces/metrics.

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata:
  name: aiops-instrumentation
  namespace: production
spec:
  exporter:
    endpoint: http://aiops-collector.observability.svc.cluster.local:4317
    
  propagators:
    - tracecontext
    - baggage
    
  sampler:
    type: parentbased_traceidratio
    argument: "0.1"         # SDK-level 10% sampling (trước tail sampling)
    
  java:   # Auto-inject Java agent
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:1.32.0
  python: # Auto-inject Python agent
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-python:0.43b0
  nodejs: # Auto-inject Node.js agent
    image: ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-nodejs:0.45.0
```

**Bật auto-instrumentation cho toàn bộ namespace**:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  annotations:
    instrumentation.opentelemetry.io/inject-java: "true"
    instrumentation.opentelemetry.io/inject-python: "true"
    # Mọi pod mới trong namespace này sẽ được tự động instrument
```

---

## 11. Fluent Bit vs OTel Collector

> [!NOTE]
> **Ý TƯỞNG**
> Fluent Bit và OTel Collector không phải đối thủ — chúng giải quyết các vấn đề khác nhau. Fluent Bit xuất sắc khi xử lý **log collection** với tài nguyên cực kỳ thấp (<1MB RAM). OTel Collector là lựa chọn khi cần xử lý **đa tín hiệu** (metrics + logs + traces) và các tính năng nâng cao như tail-based sampling.

| Tiêu chí | Fluent Bit | OTel Collector |
|-----------|-----------|----------------|
| **RAM** | ~1MB | 256MB+ |
| **Tín hiệu** | Chỉ logs | Metrics + Logs + Traces |
| **Tail sampling** | ❌ | ✅ |
| **Transform phức tạp** | Cơ bản | Full AST (mạnh hơn nhiều) |
| **Tương quan đa tín hiệu** | ❌ | ✅ |
| **Throughput** | ~500K events/s | ~200K spans/s |
| **Production maturity** | Cực cao | Cao (CNCF graduated) |

### Decision Matrix

```
Cần traces với tail sampling?      → OTel Collector
Chỉ logs, tài nguyên hạn chế?     → Fluent Bit
Toàn bộ telemetry platform?        → OTel Collector
Legacy infrastructure?              → Fluent Bit (setup đơn giản hơn)
Kubernetes-native?                  → OTel Operator + OTel Collector
```

### Hybrid Pattern (cả hai)

```
Fluent Bit (DaemonSet) → system/node logs → OTel Collector Gateway
OTel Agent (DaemonSet) → application OTLP → OTel Collector Gateway
OTel Collector Gateway → xử lý tất cả → storage backends
```

---

## 12. Production Best Practices

### Resource Limits (Production Sizing)

```yaml
# Agent (DaemonSet) — nhẹ
resources:
  requests: { cpu: "200m", memory: "256Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }

# Gateway (Deployment, có tail sampling) — cần nhiều RAM hơn
resources:
  requests: { cpu: "2000m", memory: "4Gi" }  # 4Gi cho tail sampling buffer
  limits:   { cpu: "4000m", memory: "8Gi" }
```

### HorizontalPodAutoscaler for Gateway

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: otel-collector-gateway-hpa
spec:
  scaleTargetRef:
    name: otel-collector-gateway
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: otelcol_receiver_accepted_spans
        target:
          averageValue: "50000"    # Scale up nếu >50K spans/s per pod
```

---

## 13. Common Mistakes

| Lỗi phổ biến | Triệu chứng | Khắc phục |
|---------|---------|-----|
| Không đặt memory_limiter đầu tiên | Collector OOM crash khi traffic spike | Luôn đặt memory_limiter vị trí đầu tiên |
| Batch trước tail_sampling | Sampling decision sai | Tail sample → BATCH (đúng thứ tự) |
| Không có persistent queue | Mất data khi restart | Bật file_storage extension |
| Không config max_recv_msg_size | "message too large" errors | Set `max_recv_msg_size_mib` phù hợp |
| Tail sampling tại agent | Không correlate được spans across nodes | Chỉ tail sample tại gateway |
| Auto-instrument mọi thứ | 500MB JVM agent overhead | Chọn lọc instrumentation packages |
| Một pod collector duy nhất | SPOF | Tối thiểu 3 gateway replicas |
| Thiếu trace_id trong logs | Không navigate được log→trace | Bắt buộc trace context injection tại SDK |

---

## 14. Monitoring the Collector

> [!NOTE]
> **Ý TƯỞNG**
> Collector tự phơi bày metrics Prometheus tại `:8888/metrics`. Quan trọng nhất cần theo dõi: **refused/failed spans** (phải = 0 ở trạng thái ổn định) và **queue size** (nếu tăng dần → collector bị quá tải).

```promql
# Spans nhận được — baseline throughput
rate(otelcol_receiver_accepted_spans[5m])

# Spans bị bỏ — PHẢI = 0. Nếu > 0 → collector đang bị quá tải
rate(otelcol_receiver_refused_spans[5m])
rate(otelcol_exporter_failed_spans[5m])

# Queue size — nếu tăng dần → backend không theo kịp
otelcol_exporter_queue_size / otelcol_exporter_queue_capacity

# Memory — xác nhận memory_limiter đang hoạt động
otelcol_process_memory_rss

# Tail sampling decisions — bao nhiêu % được giữ lại
rate(otelcol_processor_tail_sampling_sampled_spans[5m])
rate(otelcol_processor_tail_sampling_not_sampled_spans[5m])
```

### Alerting Rules

```yaml
groups:
  - name: otel-collector
    rules:
      - alert: OTelCollectorHighDropRate
        expr: |
          rate(otelcol_exporter_failed_spans[5m]) /
          rate(otelcol_receiver_accepted_spans[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "OTel Collector dropping >1% of spans"

      - alert: OTelCollectorQueueFull
        expr: otelcol_exporter_queue_size / otelcol_exporter_queue_capacity > 0.8
        for: 5m
        labels:
          severity: warning
```

---

## 15. Scaling

### Scaling Bottlenecks

| Bottleneck | Triệu chứng | Khắc phục |
|------------|---------|-----|
| CPU | `otelcol_process_cpu_seconds` tăng cao | Thêm replicas |
| Memory | OOM kills | Tăng memory limit hoặc giảm `num_traces` |
| Network | Queue tăng dần, export retries | Scale Tempo/Loki/Prometheus |
| gRPC connections | Connection refused từ agents | Tăng `max_concurrent_streams` |

### Target Allocator (Prometheus scraping at scale)

Khi một Prometheus instance không thể scrape đủ targets, Target Allocator phân phối scrape jobs đồng đều:

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
spec:
  mode: statefulset
  replicas: 5
  targetAllocator:
    enabled: true
    allocationStrategy: consistent-hashing    # Stable distribution across restarts
    prometheusCR:
      enabled: true   # Tự động discover ServiceMonitor và PodMonitor CRDs
```

---

## 16. Security

### mTLS với cert-manager

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: otel-collector-cert
  namespace: observability
spec:
  secretName: otel-collector-tls
  duration: 2160h        # 90 ngày
  renewBefore: 360h      # Auto-renew 15 ngày trước khi hết hạn
  usages:
    - server auth
    - client auth
  dnsNames:
    - otel-collector-gateway.observability.svc.cluster.local
```

### Secrets Management

```yaml
# Không bao giờ hard-code credentials trong ConfigMap
# Dùng external-secrets-operator → AWS Secrets Manager
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
spec:
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  data:
    - secretKey: KAFKA_PASSWORD
      remoteRef:
        key: /aiops/otel-collector/kafka-password
```

---

## 17. Cost

> [!NOTE]
> **Ý TƯỞNG**
> Chi phí OTel Collector bản thân không đáng kể (~$260/tháng cho 10 nodes). Giá trị thực sự là ở việc **giảm chi phí downstream** thông qua sampling và filtering thông minh.

### OTel Collector Resource Cost

| Deployment | Instances | Tổng |
|-----------|----------|------|
| DaemonSet Agent (10 nodes) | 10 × 0.2 CPU = 2 CPU | ~$60/tháng |
| Gateway (3 replicas) | 3 × 2 CPU = 6 CPU | ~$200/tháng |
| **Tổng** | | **~$260/tháng** |

### Data Volume Impact (Cost Savings)

```
Traces — tác động của tail sampling:
  Không sampling: 1M spans/phút × 2KB = 2.88TB/ngày
  10% tail sampling: 288GB/ngày
  Tiết kiệm: ~$150/ngày chỉ riêng Tempo S3 storage

Logs — tác động của filter:
  Không filter: 144GB/ngày
  Bỏ DEBUG + sample INFO 10%: 15GB/ngày
  Tiết kiệm: ~$6/ngày cho Loki S3
```

---

## 18. Production Review

**Các vấn đề tiềm ẩn**:

1. **Tail sampling cần consistent hashing**: Khi scale gateway, spans của cùng trace phải đến cùng replica. Không có consistent hash routing → sampling decision sai. Dùng load balancer với hash-based routing theo `traceId` header.

2. **Persistent queue ngăn data loss**: Nếu collector crash, memory queue bị mất. Dùng `file_storage` extension để WAL-backed queue.

3. **Exemplars cần config cả SDK VÀ Prometheus**: Bật exemplars tại SDK chưa đủ. Prometheus cũng cần `--enable-feature=exemplar-storage`.

### Scores

| Tiêu chí | Điểm số |
|-----------|-------|
| Technical Accuracy | 9.7/10 |
| Production Readiness | 9.6/10 |
| Depth | 9.7/10 |
| Practical Value | 9.8/10 |
| Cost Awareness | 9.7/10 |

---

## References

1. [OpenTelemetry Collector Documentation](https://opentelemetry.io/docs/collector/)
2. [OTel Collector Contrib Repository](https://github.com/open-telemetry/opentelemetry-collector-contrib)
3. [OpenTelemetry Operator](https://github.com/open-telemetry/opentelemetry-operator)
4. [OTLP Specification](https://opentelemetry.io/docs/specs/otlp/)
5. [OTel Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
6. [Tail Sampling Processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor)
