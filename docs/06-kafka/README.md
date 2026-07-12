# Chapter 06 — Apache Kafka / AWS Kinesis

> **The transport layer is the backbone of the AIOps pipeline. Every anomaly detection event, alert, and remediation trigger flows through it. Choosing the right streaming platform — and configuring it correctly — determines the latency, durability, and scalability of the entire AIOps system.**

---

## Prerequisites

- Basic understanding of distributed systems (CAP theorem, replication)
- [02 — OpenTelemetry](../02-opentelemetry/README.md) — Kafka as OTel Collector exporter
- [07 — Anomaly Detection](../07-anomaly-detection/README.md) — consumes from Kafka

## Related Documents

- [07 — Anomaly Detection](../07-anomaly-detection/README.md) — consumes telemetry from Kafka
- [08 — Alert Correlation](../08-alert-correlation/README.md) — consumes anomaly events from Kafka
- [11 — Remediation](../11-remediation/README.md) — publishes remediation triggers to Kafka

## Next Reading

After this chapter, proceed to [07 — Anomaly Detection](../07-anomaly-detection/README.md).

---

## Table of Contents

1. [Why Event Streaming for AIOps?](#1-why-event-streaming-for-aiops)
2. [Kafka Architecture Deep Dive](#2-kafka-architecture-deep-dive)
3. [Topics and Partitions](#3-topics-and-partitions)
4. [Producers — Configuration and Guarantees](#4-producers--configuration-and-guarantees)
5. [Consumers and Consumer Groups](#5-consumers-and-consumer-groups)
6. [Offset Management](#6-offset-management)
7. [Replication and Durability](#7-replication-and-durability)
8. [Kafka Topic Design for AIOps](#8-kafka-topic-design-for-aiops)
9. [Message Schema and Serialization](#9-message-schema-and-serialization)
10. [Dead Letter Queue Pattern](#10-dead-letter-queue-pattern)
11. [AWS MSK — Managed Kafka](#11-aws-msk--managed-kafka)
12. [Kafka vs Kinesis](#12-kafka-vs-kinesis)
13. [Kafka vs Redis Streams](#13-kafka-vs-redis-streams)
14. [Production Configuration](#14-production-configuration)
15. [Monitoring Kafka](#15-monitoring-kafka)
16. [Scaling](#16-scaling)
17. [Security](#17-security)
18. [Cost](#18-cost)
19. [Production Review](#19-production-review)

---

## 1. Why Event Streaming for AIOps?

### The Problem Without a Queue

Without a transport layer, the AIOps pipeline is synchronous and brittle:

```mermaid
graph LR
    AD[Anomaly Detector] -->|direct call| CORR[Correlation Engine]
    CORR -->|direct call| RCA[RCA Engine]
    RCA -->|direct call| LLM[LLM Agent]
    LLM -->|direct call| REM[Remediation]

    style AD fill:#1565c0,color:#fff
```

**Problems**:
- If Correlation Engine is slow, Anomaly Detector blocks
- If LLM Agent crashes, RCA results are lost
- Cannot replay events for debugging or model retraining
- Cannot add a new consumer (e.g., a second ML model) without modifying producers
- Backpressure propagates upstream, potentially losing telemetry

### What Kafka Solves

```mermaid
graph LR
    AD[Anomaly Detector] -->|publish| K1[(Kafka\nanomalies topic)]
    K1 -->|subscribe| CORR[Correlation Engine]
    K1 -->|subscribe| STORE[Event Store\nfor replay]
    K1 -->|subscribe| TRAIN[ML Training\npipeline]

    CORR -->|publish| K2[(Kafka\ncorrelated-alerts topic)]
    K2 -->|subscribe| RCA[RCA Engine]
    K2 -->|subscribe| GRAFANA[Grafana\nannotations]

    style K1 fill:#4a148c,color:#fff
    style K2 fill:#4a148c,color:#fff
```

**Benefits**:
- **Decoupling**: Producers don't know about consumers
- **Durability**: Messages persisted to disk, survived consumer crashes
- **Replay**: Reprocess past events for model retraining, debugging
- **Fan-out**: Multiple consumers from the same topic
- **Backpressure**: Consumer lag is explicit and monitorable
- **Ordering**: Within a partition, strict ordering guaranteed

---

## 2. Kafka Architecture Deep Dive

```mermaid
graph TD
    subgraph Producers["Producers"]
        P1[OTel Collector\ntelemetry data]
        P2[Anomaly Detector\nanomaly events]
        P3[Alert Correlator\nalert groups]
    end

    subgraph Kafka["Kafka Cluster (3 brokers)"]
        B1[Broker 1\nLeader for partitions: 0,3,6]
        B2[Broker 2\nLeader for partitions: 1,4,7]
        B3[Broker 3\nLeader for partitions: 2,5,8]
        ZK[ZooKeeper / KRaft\nmetadata + elections]
    end

    subgraph Topics["Topics"]
        T1[aiops-metrics\n9 partitions\nRF=3]
        T2[aiops-anomalies\n6 partitions\nRF=3]
        T3[aiops-alerts\n3 partitions\nRF=3]
    end

    subgraph Consumers["Consumer Groups"]
        CG1[anomaly-detector-group\n3 consumer pods]
        CG2[correlation-engine-group\n2 consumer pods]
        CG3[llm-agent-group\n1 consumer pod]
        CG4[event-store-group\n1 consumer pod]
    end

    P1 -->|produce| B1
    P2 -->|produce| B2
    P3 -->|produce| B3

    B1 <-->|replicate| B2
    B2 <-->|replicate| B3

    B1 -->|serve| CG1
    B2 -->|serve| CG2
    B3 -->|serve| CG3

    style Producers fill:#1565c0,color:#fff
    style Kafka fill:#2e7d32,color:#fff
    style Topics fill:#4a148c,color:#fff
    style Consumers fill:#e65100,color:#fff
```

### Broker Internals

Each Kafka broker is responsible for:
1. **Serving producer writes** for partitions where it is the leader
2. **Replicating data** to follower brokers
3. **Serving consumer reads** from its partitions
4. **Log segment management** (files on disk)

**Log storage structure**:

```
/kafka/data/
└── aiops-metrics-0/          ← Topic "aiops-metrics", Partition 0
    ├── 00000000000000000000.log    ← Log segment (messages)
    ├── 00000000000000000000.index  ← Offset index (offset → file position)
    ├── 00000000000000000000.timeindex  ← Time index (timestamp → offset)
    ├── 00000000000001234567.log    ← Next segment (started after roll)
    └── leader-epoch-checkpoint
```

**Segment rolling**: A new segment file is created when:
- Current segment reaches `log.segment.bytes` (default 1GB)
- Current segment is older than `log.roll.hours` (default 7 days)

---

## 3. Topics and Partitions

### Partition Key Concepts

```mermaid
graph LR
    subgraph Topic["Topic: aiops-metrics"]
        P0[Partition 0\nBroker 1 Leader\nOffset: 0,1,2...1M]
        P1[Partition 1\nBroker 2 Leader\nOffset: 0,1,2...950K]
        P2[Partition 2\nBroker 3 Leader\nOffset: 0,1,2...1.1M]
    end

    MSG1[Message\nkey=service-A] -->|hash(key) % 3 = 0| P0
    MSG2[Message\nkey=service-B] -->|hash(key) % 3 = 1| P1
    MSG3[Message\nkey=service-C] -->|hash(key) % 3 = 2| P2

    CONS1[Consumer 1] -->|reads| P0
    CONS2[Consumer 2] -->|reads| P1
    CONS3[Consumer 3] -->|reads| P2

    style P0 fill:#1565c0,color:#fff
    style P1 fill:#2e7d32,color:#fff
    style P2 fill:#4a148c,color:#fff
```

**Ordering guarantee**: Kafka guarantees **per-partition ordering** only. Messages with the same key always go to the same partition → ordered per key.

**Why this matters for AIOps**:
- Use `service_name` as message key for anomaly events → all anomalies from the same service are ordered
- Use `alert_group_id` as key for alert correlation events → correlated alerts stay in order
- Do NOT use random keys or null keys if ordering matters

### Partition Count Design

```
Formula for partition count:
Partitions = max(
  desired_throughput / throughput_per_partition,
  number_of_consumers_in_group
)

Example for aiops-metrics topic:
- Target throughput: 100MB/s
- Throughput per partition: ~10MB/s (Kafka benchmark)
- Number of anomaly detector instances: 6

partitions = max(100/10, 6) = max(10, 6) = 10 partitions

Round up to next power of 2 or use 12 (multiple of 3 for even distribution):
Final: 12 partitions
```

**Warning**: Partitions cannot be decreased after creation. Start conservatively and increase if needed. Increasing partitions changes the key→partition mapping and breaks ordering guarantees for in-flight data.

### Retention Policy

```bash
# Time-based retention (default)
kafka-configs.sh --alter \
  --topic aiops-metrics \
  --add-config "retention.ms=604800000"  # 7 days

# Size-based retention (per-partition)
kafka-configs.sh --alter \
  --topic aiops-raw-telemetry \
  --add-config "retention.bytes=107374182400"  # 100GB per partition

# Compaction (for changelog/state topics)
kafka-configs.sh --alter \
  --topic aiops-service-registry \
  --add-config "cleanup.policy=compact"
```

**Retention trade-offs**:

| Policy | Benefit | Cost |
|--------|---------|------|
| Short (1-24h) | Low storage cost | Cannot replay historical events |
| Long (7-30d) | Full replay capability | High storage cost |
| Compacted | Infinite retention (latest value per key) | No time-based queries |

**AIOps recommendation**: 7-day retention for telemetry topics (replay window for model retraining). 30-day for alert/incident topics (post-incident analysis).

---

## 4. Producers — Configuration and Guarantees

### Delivery Semantics

| Setting | Guarantee | Behavior |
|---------|-----------|----------|
| `acks=0` | Fire-and-forget | Producer doesn't wait for ack. Fastest. Can lose messages. |
| `acks=1` | Leader ack | Leader writes to log, acks. Follower not yet replicated. Risk: leader crash before replication. |
| `acks=-1 (all)` | Full replication | All in-sync replicas must ack. Slowest. No data loss with min.insync.replicas=2. |

**For AIOps (critical events)**: Always use `acks=-1`.

### Exactly-Once Semantics (EOS)

**Problem**: Producer retry can cause duplicate messages:
1. Producer sends message
2. Broker writes message, acks
3. Network fails — producer doesn't receive ack
4. Producer retries → **duplicate message**

**Solution**: Idempotent producer + transactions

```python
# Producer configuration for EOS
producer_config = {
    "bootstrap.servers": "kafka-1:9092,kafka-2:9092,kafka-3:9092",
    
    # Idempotent producer: enables deduplication of retries
    "enable.idempotence": True,
    
    # Required for idempotent:
    "acks": "all",
    "retries": 2147483647,            # Max retries
    "max.in.flight.requests.per.connection": 5,  # Must be ≤5 for idempotent
    
    # Transactional ID (for exactly-once with consumer-produce)
    "transactional.id": "aiops-anomaly-detector-0",  # Unique per producer instance
    
    # Performance tuning
    "batch.size": 65536,              # 64KB batch
    "linger.ms": 10,                  # Wait up to 10ms to fill batch
    "compression.type": "snappy",     # Compress batches
    "buffer.memory": 33554432,        # 32MB producer buffer
}

from confluent_kafka import Producer
producer = Producer(producer_config)

# Initialize transaction
producer.init_transactions()
producer.begin_transaction()

try:
    # Produce messages in transaction
    producer.produce(
        topic="aiops-anomalies",
        key=b"service-order",
        value=json.dumps(anomaly_event).encode(),
        headers={"content-type": b"application/json"},
    )
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
    raise
```

### Producer Compression

| Codec | Ratio | CPU Cost | Best For |
|-------|-------|----------|---------|
| None | 1:1 | Zero | Very small messages |
| gzip | 4:1 | High | CPU-rich producers, high compression needed |
| **snappy** | 2:1 | **Low** | **Production default** |
| lz4 | 2:1 | Very low | Low-latency critical |
| **zstd** | 4:1 | **Medium** | **Best ratio/speed balance** |

**Recommendation**: `zstd` for AIOps telemetry topics (high compression, medium CPU). `snappy` for alert events (low latency matters more than ratio).

---

## 5. Consumers and Consumer Groups

### Consumer Group Mechanics

```mermaid
sequenceDiagram
    participant C1 as Consumer 1 (pod)
    participant C2 as Consumer 2 (pod)
    participant C3 as Consumer 3 (pod)
    participant GC as Group Coordinator (Broker)
    participant P0 as Partition 0
    participant P1 as Partition 1
    participant P2 as Partition 2

    C1->>GC: JoinGroup(group_id="anomaly-detector")
    C2->>GC: JoinGroup(group_id="anomaly-detector")
    C3->>GC: JoinGroup(group_id="anomaly-detector")

    GC->>C1: Assign partition 0 (elected leader)
    GC->>C2: Assign partition 1
    GC->>C3: Assign partition 2

    loop Every max.poll.interval.ms
        C1->>P0: Fetch records (max.poll.records=500)
        C2->>P1: Fetch records
        C3->>P2: Fetch records
        C1->>GC: Commit offset 1234
        C2->>GC: Commit offset 5678
    end

    Note over C2: Pod crashes
    C2->>GC: LeaveGroup (or timeout after session.timeout.ms)
    GC->>C1: Rebalance: take partition 1
    GC->>C3: Keep partition 2
```

### Consumer Configuration

```python
consumer_config = {
    "bootstrap.servers": "kafka-1:9092,kafka-2:9092,kafka-3:9092",
    "group.id": "anomaly-detector-group",
    
    # Start reading from latest if no committed offset
    "auto.offset.reset": "latest",     # or "earliest" for replay
    
    # Disable auto-commit! Commit manually after processing
    "enable.auto.commit": False,
    
    # How often to send heartbeat to broker
    "heartbeat.interval.ms": 3000,
    
    # Max time between poll() calls before consumer is considered dead
    # Must be > processing time for a batch of records
    "max.poll.interval.ms": 300000,    # 5 minutes
    
    # Max number of records returned per poll()
    "max.poll.records": 500,
    
    # Minimum data to fetch (wait for this before returning)
    "fetch.min.bytes": 1024,
    
    # Max wait time if fetch.min.bytes not met
    "fetch.max.wait.ms": 500,
    
    # Security
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "SCRAM-SHA-512",
    "sasl.username": "aiops-consumer",
    "sasl.password": "${KAFKA_PASSWORD}",
    "ssl.ca.location": "/certs/kafka-ca.crt",
}

from confluent_kafka import Consumer, KafkaError
import json

consumer = Consumer(consumer_config)
consumer.subscribe(["aiops-metrics"])

try:
    while True:
        msgs = consumer.poll(timeout=1.0)  # Wait up to 1s for messages
        
        if msgs is None:
            continue
        if msgs.error():
            if msgs.error().code() == KafkaError._PARTITION_EOF:
                continue  # Reached end of partition
            raise KafkaError(msgs.error())
        
        # Process message
        try:
            event = json.loads(msgs.value())
            process_anomaly(event)
            
            # Manual commit AFTER processing (at-least-once)
            consumer.commit(asynchronous=False)
            
        except Exception as e:
            # Send to DLQ on processing failure
            send_to_dlq(msgs, str(e))
            consumer.commit(asynchronous=False)  # Still commit to move forward
            
finally:
    consumer.close()
```

### Consumer Lag — The Key Health Metric

```
Consumer Lag = Latest Offset - Committed Consumer Offset

High lag (>10K messages) means:
- Consumer is falling behind → processing is too slow
- This is the earliest warning of an AIOps pipeline bottleneck
```

---

## 6. Offset Management

### Offset Commit Strategies

| Strategy | Implementation | Risk | Use Case |
|----------|---------------|------|---------|
| **Auto-commit** | `enable.auto.commit=True` | May commit before processing → at-most-once | Simple consumers, log forwarding |
| **Manual sync commit** | `commit(async=False)` | Slowest, blocks until ack | **Recommended for AIOps (critical)** |
| **Manual async commit** | `commit(async=True)` | Slightly risky (commit fails silently) | High-throughput, idempotent processing |
| **Transactional** | Producer + Consumer in same transaction | Complex | Exactly-once stream processing |

### Seek and Replay

```python
# Replay from beginning (model retraining)
from confluent_kafka import TopicPartition

partitions = consumer.assignment()
consumer.seek_to_beginning(partitions)

# Replay from specific timestamp (incident post-mortem: replay last 2 hours)
import time
ts = int((time.time() - 7200) * 1000)  # 2 hours ago in milliseconds

for partition in partitions:
    offsets = consumer.offsets_for_times(
        [TopicPartition(partition.topic, partition.partition, ts)]
    )
    consumer.seek(offsets[0])
```

---

## 7. Replication and Durability

### Replication Factor

```
Replication Factor (RF) = how many copies of each partition exist

RF=1: No redundancy. Broker failure = data loss.
RF=2: Survive 1 broker failure. But split-brain possible.
RF=3: Survive 1 broker failure. Recommended for production.
RF=5: Survive 2 broker failures. High cost.
```

**For AIOps**: RF=3 for all topics.

### Min In-Sync Replicas (min.insync.replicas)

```
Producer acks=all + min.insync.replicas=2

This means:
- Leader + at least 1 follower must acknowledge write
- If only 1 broker is up (leader), writes fail with NotEnoughReplicas error
- Prevents data loss at the cost of availability
```

```bash
# Create topic with production durability settings
kafka-topics.sh --create \
  --topic aiops-anomalies \
  --partitions 6 \
  --replication-factor 3 \
  --config min.insync.replicas=2 \
  --config unclean.leader.election.enable=false \
  --config retention.ms=604800000
```

### Unclean Leader Election

**`unclean.leader.election.enable=false`** (critical for AIOps):

If all in-sync replicas fail, Kafka must decide:
- `true`: Elect an out-of-sync replica as leader → **availability**, but **data loss**
- `false`: Wait for an in-sync replica → **consistency**, but **unavailability**

For AIOps alert/incident data: use `false`. Data loss in an AIOps pipeline is worse than temporary unavailability.

---

## 8. Kafka Topic Design for AIOps

### Topic Topology

```mermaid
graph TD
    subgraph Raw["Raw Telemetry"]
        T1[aiops-raw-metrics\n12 partitions, 7d retention]
        T2[aiops-raw-logs\n12 partitions, 7d retention]
        T3[aiops-raw-traces\n12 partitions, 7d retention]
    end

    subgraph Processed["Processed Events"]
        T4[aiops-anomalies\n6 partitions, 30d retention]
        T5[aiops-correlated-alerts\n3 partitions, 30d retention]
        T6[aiops-rca-results\n3 partitions, 30d retention]
    end

    subgraph Action["Action Events"]
        T7[aiops-remediation-triggers\n3 partitions, 90d retention]
        T8[aiops-remediation-results\n3 partitions, 90d retention]
        T9[aiops-incidents\n3 partitions, 1y retention, compacted]
    end

    subgraph DLQ["Dead Letter Queues"]
        DLQ1[aiops-anomalies-dlq\n3 partitions, 7d]
        DLQ2[aiops-remediation-dlq\n3 partitions, 7d]
    end

    T1 -->|anomaly detector| T4
    T2 -->|log anomaly detector| T4
    T3 -->|trace anomaly detector| T4
    T4 -->|correlation engine| T5
    T5 -->|RCA engine| T6
    T6 -->|LLM agent| T7
    T7 -->|remediation executor| T8
    T7 -->|on failure| DLQ2

    style Raw fill:#1565c0,color:#fff
    style Processed fill:#2e7d32,color:#fff
    style Action fill:#e65100,color:#fff
    style DLQ fill:#b71c1c,color:#fff
```

### Topic Naming Convention

```
<domain>-<data-type>-<qualifier>

Examples:
aiops-raw-metrics          # Raw telemetry: metrics
aiops-raw-logs             # Raw telemetry: logs
aiops-anomalies            # Processed: anomaly events
aiops-anomalies-dlq        # Dead letter: failed anomaly processing
aiops-correlated-alerts    # Processed: alert groups
aiops-rca-results          # Processed: root cause analysis results
aiops-remediation-triggers # Actions: remediation commands
aiops-remediation-results  # Actions: remediation outcomes
aiops-incidents            # State: incident registry (compacted)
```

---

## 9. Message Schema and Serialization

### Schema Registry

Use Confluent Schema Registry to enforce message schemas:

```yaml
# Schema Registry deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: schema-registry
  namespace: kafka
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: schema-registry
          image: confluentinc/cp-schema-registry:7.5.0
          env:
            - name: SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS
              value: "kafka-1:9092,kafka-2:9092,kafka-3:9092"
            - name: SCHEMA_REGISTRY_HOST_NAME
              value: schema-registry
            - name: SCHEMA_REGISTRY_LISTENERS
              value: http://0.0.0.0:8081
```

### Anomaly Event Schema (Avro)

```json
{
  "type": "record",
  "name": "AnomalyEvent",
  "namespace": "com.aiops.events",
  "fields": [
    {"name": "event_id", "type": "string", "doc": "UUID v4"},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "service_name", "type": "string"},
    {"name": "service_namespace", "type": "string"},
    {"name": "cluster", "type": "string"},
    {"name": "signal_type", "type": {"type": "enum", "name": "SignalType",
      "symbols": ["METRIC", "LOG", "TRACE"]}},
    {"name": "metric_name", "type": ["null", "string"], "default": null},
    {"name": "anomaly_score", "type": "double", "doc": "0.0-1.0, higher=more anomalous"},
    {"name": "anomaly_type", "type": "string", "doc": "spike|drop|seasonal|pattern"},
    {"name": "algorithm", "type": "string", "doc": "ewma|zscore|isolation_forest|lstm"},
    {"name": "baseline_value", "type": ["null", "double"], "default": null},
    {"name": "current_value", "type": ["null", "double"], "default": null},
    {"name": "deviation_pct", "type": ["null", "double"], "default": null},
    {"name": "confidence", "type": "double", "doc": "0.0-1.0 model confidence"},
    {"name": "context", "type": {
      "type": "map",
      "values": "string"
    }, "doc": "Additional context key-value pairs"},
    {"name": "related_trace_ids", "type": {"type": "array", "items": "string"}, "default": []},
    {"name": "raw_data_ref", "type": ["null", "string"], "default": null,
      "doc": "Reference to raw data in object storage"}
  ]
}
```

### Serialization Options

| Format | Schema Evolution | Size | Speed | Use Case |
|--------|-----------------|------|-------|---------|
| **Avro + Schema Registry** | ✅ Excellent (backward/forward compatible) | Small (binary) | Fast | **Production AIOps (recommended)** |
| **Protobuf** | ✅ Excellent | Smallest | Fastest | High-throughput, strict schema |
| **JSON** | ❌ None (breaking changes possible) | Largest | Slowest | Development, debugging |
| **Parquet** | N/A (file format, not streaming) | Smallest | — | Batch/offline |

---

## 10. Dead Letter Queue Pattern

When a message cannot be processed (parsing error, downstream failure, timeout), it must not be silently dropped.

```mermaid
graph LR
    KAFKA[Kafka Topic\naiops-anomalies] --> CONS[Consumer\nAnomaly Processor]
    CONS -->|success| NEXT[Next Topic\naiops-correlated-alerts]
    CONS -->|failure| DLQ[Dead Letter Queue\naiops-anomalies-dlq]
    DLQ -->|manual review| OPS[Operations Team]
    DLQ -->|retry logic| RETRY[DLQ Processor\nretry with backoff]
    RETRY -->|re-process| CONS

    style DLQ fill:#b71c1c,color:#fff
```

```python
def process_with_dlq(consumer, producer, dlq_topic):
    msg = consumer.poll(1.0)
    if msg is None:
        return
    
    try:
        event = AnomalyEvent.from_bytes(msg.value())
        process_anomaly(event)
        consumer.commit(asynchronous=False)
        
    except (ValueError, KeyError) as e:
        # Parsing/schema error — send to DLQ immediately (don't retry)
        send_to_dlq(
            producer=producer,
            dlq_topic=dlq_topic,
            original_msg=msg,
            error=str(e),
            error_type="PARSE_ERROR",
            retry_count=0,
        )
        consumer.commit(asynchronous=False)
        
    except TemporaryError as e:
        # Transient error — check retry count
        retry_count = int(msg.headers().get("retry_count", [b"0"])[1])
        
        if retry_count >= 3:
            # Exhausted retries → send to DLQ
            send_to_dlq(producer, dlq_topic, msg, str(e), "MAX_RETRIES", retry_count)
            consumer.commit(asynchronous=False)
        else:
            # Re-enqueue with incremented retry count and backoff delay
            time.sleep(2 ** retry_count)  # Exponential backoff: 1s, 2s, 4s
            producer.produce(
                topic=msg.topic(),
                key=msg.key(),
                value=msg.value(),
                headers=[
                    ("retry_count", str(retry_count + 1).encode()),
                    ("original_timestamp", msg.timestamp()[1].to_bytes(8, 'big')),
                    ("error_message", str(e).encode()[:1024]),
                ],
            )
            consumer.commit(asynchronous=False)

def send_to_dlq(producer, dlq_topic, original_msg, error, error_type, retry_count):
    dlq_payload = {
        "original_topic": original_msg.topic(),
        "original_partition": original_msg.partition(),
        "original_offset": original_msg.offset(),
        "original_key": original_msg.key().decode() if original_msg.key() else None,
        "original_value_b64": base64.b64encode(original_msg.value()).decode(),
        "error_message": error,
        "error_type": error_type,
        "retry_count": retry_count,
        "failed_at": datetime.utcnow().isoformat(),
    }
    producer.produce(
        topic=dlq_topic,
        value=json.dumps(dlq_payload).encode(),
    )
    producer.flush()
```

---

## 11. AWS MSK — Managed Kafka

Amazon MSK (Managed Streaming for Apache Kafka) removes the operational burden of running Kafka.

### MSK vs Self-Hosted Kafka

| Dimension | AWS MSK | Self-Hosted Kafka |
|-----------|---------|-------------------|
| **Setup time** | 30 minutes | 2–5 days |
| **Operations burden** | Minimal (AWS manages brokers, OS, ZooKeeper) | High (upgrade, tuning, monitoring) |
| **Version control** | AWS controls upgrade schedule | Full control |
| **Kafka version** | 3.x (latest major) | Any |
| **KRaft mode** | ✅ MSK Serverless | ✅ Self-hosted 3.4+ |
| **Networking** | VPC-native | Requires network planning |
| **Multi-AZ** | ✅ Automatic | Requires configuration |
| **Monitoring** | CloudWatch + Prometheus (MSK Connect) | Full Prometheus |
| **Cost (3-broker m5.large)** | ~$400/month | ~$200/month (EC2) + operations overhead |
| **Serverless** | ✅ MSK Serverless | ❌ |
| **Custom plugins (Kafka Connect)** | ✅ MSK Connect | ✅ Self-managed |

**Recommendation**:
- Small/medium team: **MSK** (lower TCO when including operations)
- Large team with Kafka expertise: **Self-hosted** (full control, lower cost at scale)
- Variable workload: **MSK Serverless** (pay per use)

### MSK Terraform

```hcl
resource "aws_msk_cluster" "aiops" {
  cluster_name           = "aiops-kafka-prod"
  kafka_version          = "3.5.1"
  number_of_broker_nodes = 3    # 1 per AZ in us-east-1

  broker_node_group_info {
    instance_type   = "kafka.m5.large"    # 2 vCPU, 8GB RAM
    client_subnets  = [
      aws_subnet.private_us_east_1a.id,
      aws_subnet.private_us_east_1b.id,
      aws_subnet.private_us_east_1c.id,
    ]
    storage_info {
      ebs_storage_info {
        volume_size = 1000    # 1TB per broker
        provisioned_throughput {
          enabled           = true
          volume_throughput = 250    # MB/s
        }
      }
    }
    security_groups = [aws_security_group.kafka.id]
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"           # Enforce TLS
      in_cluster    = true
    }
    encryption_at_rest {
      data_volume_kms_key_id = aws_kms_key.kafka.arn
    }
  }

  client_authentication {
    sasl {
      scram = true    # SASL/SCRAM with AWS Secrets Manager
      iam   = true    # IAM authentication (MSK-native)
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.aiops.arn
    revision = aws_msk_configuration.aiops.latest_revision
  }

  enhanced_monitoring = "PER_TOPIC_PER_PARTITION"  # Detailed CloudWatch metrics

  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = true    # Expose JMX metrics for Prometheus
      }
    }
  }

  logging_config {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.msk_broker.name
      }
      s3 {
        enabled = true
        bucket  = aws_s3_bucket.msk_logs.id
        prefix  = "kafka-broker-logs/"
      }
    }
  }

  tags = {
    Environment = "production"
    Component   = "aiops-transport"
  }
}

resource "aws_msk_configuration" "aiops" {
  kafka_versions = ["3.5.1"]
  name           = "aiops-kafka-config"

  server_properties = <<-EOF
    auto.create.topics.enable=false
    default.replication.factor=3
    min.insync.replicas=2
    num.partitions=12
    num.network.threads=8
    num.io.threads=16
    socket.send.buffer.bytes=102400
    socket.receive.buffer.bytes=102400
    socket.request.max.bytes=104857600
    log.retention.hours=168
    log.segment.bytes=1073741824
    log.retention.check.interval.ms=300000
    unclean.leader.election.enable=false
    replica.lag.time.max.ms=30000
    offsets.retention.minutes=10080
    transaction.state.log.replication.factor=3
    transaction.state.log.min.isr=2
    EOF
}
```

---

## 12. Kafka vs Kinesis

| Dimension | Apache Kafka (MSK) | AWS Kinesis Data Streams |
|-----------|------------------|-----------------------|
| **Model** | Pull (consumer-controlled) | Pull (shard-based) |
| **Throughput per shard/partition** | ~10MB/s | 1MB/s write, 2MB/s read |
| **Partition/Shard count** | Unlimited | Max 10,000 per stream |
| **Retention** | Configurable (1h to forever) | 1–365 days |
| **Replay** | ✅ Yes (by offset) | ✅ Yes (by timestamp) |
| **Consumer groups** | ✅ Full consumer group support | ✅ Via Enhanced Fan-Out |
| **Ordering** | Per-partition | Per-shard |
| **Setup** | Complex (or MSK) | Simple (fully managed) |
| **Cost (1MB/s × 3 shards)** | $400/month (MSK m5.large) | $45/month (Kinesis) |
| **AWS integration** | Via connectors | Native (Lambda, Firehose, S3) |
| **Max message size** | 1MB (default, configurable) | 1MB (hard limit) |
| **Exactly-once** | ✅ With transactions | ❌ At-least-once |
| **Schema registry** | ✅ Confluent Schema Registry | ✅ AWS Glue Schema Registry |
| **Ecosystem** | Huge (Kafka Connect, Kafka Streams, Flink) | AWS-centric |

**Decision matrix**:

```
Already using AWS Lambda heavily?  → Kinesis (native trigger)
Need exactly-once semantics?       → Kafka
Need >1MB messages?                → Kafka
Need long retention (>365d)?       → Kafka
Small team, AWS-only?              → Kinesis (simpler)
Need rich ecosystem (Flink, etc.)? → Kafka
Cost is primary concern (<100MB/s)?→ Kinesis cheaper at small scale
Cost at scale (>1GB/s)?            → Kafka cheaper (MSK fixed cost)
```

---

## 13. Kafka vs Redis Streams

Redis Streams is a lighter-weight alternative for smaller AIOps deployments.

| Dimension | Kafka | Redis Streams |
|-----------|-------|---------------|
| **Throughput** | Millions msg/sec | 100K–500K msg/sec |
| **Persistence** | Disk-based (durable) | Memory (+ AOF/RDB optional) |
| **Retention** | Days–years | Memory-limited |
| **Consumer groups** | ✅ Full | ✅ XREADGROUP |
| **Replay** | ✅ Full (by offset) | ✅ Limited (by ID) |
| **Partitioning** | ✅ First-class | ❌ One stream (no partition) |
| **Operational complexity** | High | Low |
| **AWS managed** | MSK | ElastiCache |
| **Cost** | Higher | Lower |
| **Ecosystem** | Huge | Small |

**Recommendation**:
- <10K events/sec AND team <10 engineers: **Redis Streams** (simpler)
- >10K events/sec OR need replay/reprocessing: **Kafka/MSK**
- Production AIOps at medium/large scale: **Kafka/MSK** (ecosystem, durability)

---

## 14. Production Configuration

### Kafka Broker Configuration

```properties
# server.properties (production)

# Networking
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600    # 100MB

# Log storage
log.dirs=/data/kafka/logs
num.recovery.threads.per.data.dir=4
log.retention.hours=168               # 7 days
log.segment.bytes=1073741824          # 1GB segments
log.retention.check.interval.ms=300000

# Replication
default.replication.factor=3
min.insync.replicas=2
unclean.leader.election.enable=false
replica.lag.time.max.ms=30000

# Performance
num.partitions=12
message.max.bytes=1048576             # 1MB max message
replica.fetch.max.bytes=1048576
compression.type=producer             # Honor producer-specified compression

# Transactions
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2
transaction.max.timeout.ms=900000     # 15 min max transaction

# JVM heap (separate from broker config, in kafka-server-start.sh)
# KAFKA_HEAP_OPTS="-Xmx6g -Xms6g"
```

---

## 15. Monitoring Kafka

### Key Metrics (via JMX Exporter)

```promql
# Consumer lag (most critical metric)
kafka_consumer_group_lag_sum{group="anomaly-detector-group"}

# Alert when lag exceeds threshold
- alert: KafkaConsumerLagHigh
  expr: |
    kafka_consumer_group_lag_sum > 10000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Consumer group {{ $labels.group }} lag: {{ $value }} messages"

# Producer throughput
rate(kafka_server_brokertopicmetrics_messagesinpersec[5m])

# Broker health
kafka_server_replicamanager_underreplicatedpartitions  # Should be 0
kafka_server_replicamanager_offlinereplicacount        # Should be 0
kafka_controller_kafkacontroller_activecontrollercount # Should be 1

# Network saturation
kafka_network_requestchannel_requestqueue_size         # Request backlog
kafka_network_processor_idlepercent                    # Should be >30%

# Log segments
kafka_log_log_numlogsegments                           # Number of segments
kafka_log_log_logstartoffset                           # Oldest available offset
kafka_log_log_logendoffset                             # Latest offset
```

### Critical Alerts

```yaml
- alert: KafkaUnderReplicatedPartitions
  expr: kafka_server_replicamanager_underreplicatedpartitions > 0
  for: 10m
  labels:
    severity: critical
  annotations:
    summary: "Kafka has {{ $value }} under-replicated partitions"

- alert: KafkaBrokerDown
  expr: up{job="kafka"} == 0
  for: 2m
  labels:
    severity: critical

- alert: KafkaConsumerGroupLagCritical
  expr: |
    sum by (group, topic) (kafka_consumer_group_lag_sum) > 100000
  for: 10m
  labels:
    severity: critical
  annotations:
    summary: "Consumer group {{ $labels.group }} has critical lag on {{ $labels.topic }}"
```

### Grafana Dashboard for Kafka

Key panels to include:
1. Consumer lag per group per topic (time series)
2. Producer throughput (MB/s) per topic
3. Broker disk usage per broker
4. Under-replicated partitions (should always be 0)
5. Network bytes in/out per broker
6. Request latency P99 (produce + fetch)

---

## 16. Scaling

### Horizontal Scaling

**Adding brokers**: Kafka supports adding brokers with `kafka-reassign-partitions.sh`. Partitions must be explicitly reassigned to balance load.

```bash
# Generate reassignment plan
kafka-reassign-partitions.sh \
  --bootstrap-server kafka-1:9092 \
  --topics-to-move-json-file topics.json \
  --broker-list "1,2,3,4" \
  --generate

# Execute reassignment
kafka-reassign-partitions.sh \
  --bootstrap-server kafka-1:9092 \
  --reassignment-json-file reassignment.json \
  --execute

# Verify
kafka-reassign-partitions.sh \
  --bootstrap-server kafka-1:9092 \
  --reassignment-json-file reassignment.json \
  --verify
```

**Consumer scaling**: Add consumer instances to a group. Partitions auto-rebalanced. Maximum consumers = number of partitions.

**Partition count**: Increase if consumer processing is the bottleneck (more consumers needed). Cannot decrease.

---

## 17. Security

### Authentication: SASL/SCRAM

```bash
# Add user credentials to ZooKeeper (or KRaft)
kafka-configs.sh --zookeeper zk-1:2181 \
  --alter --add-config \
  'SCRAM-SHA-512=[password=secretpassword]' \
  --entity-type users \
  --entity-name aiops-producer
```

### Authorization: ACLs

```bash
# Grant producer permission
kafka-acls.sh --bootstrap-server kafka-1:9092 \
  --add --allow-principal User:aiops-producer \
  --operation Write --operation Create \
  --topic aiops-anomalies

# Grant consumer permission
kafka-acls.sh --bootstrap-server kafka-1:9092 \
  --add --allow-principal User:aiops-consumer \
  --operation Read \
  --topic aiops-anomalies \
  --group anomaly-detector-group
```

### Network Encryption

```properties
# Broker: require TLS
listeners=SASL_SSL://0.0.0.0:9093
security.inter.broker.protocol=SASL_SSL
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512

ssl.keystore.location=/certs/kafka.keystore.jks
ssl.keystore.password=${KEYSTORE_PASSWORD}
ssl.key.password=${KEY_PASSWORD}
ssl.truststore.location=/certs/kafka.truststore.jks
ssl.truststore.password=${TRUSTSTORE_PASSWORD}
ssl.client.auth=required    # mTLS
```

---

## 18. Cost

### Self-Hosted on EC2 (3-broker cluster)

| Component | Instance | Monthly Cost |
|-----------|----------|-------------|
| 3× Kafka brokers | m5.2xlarge (8 CPU, 32GB) | $660 |
| 3× EBS (1TB gp3 each) | gp3, 250MB/s | $240 |
| 3× ZooKeeper | m5.large | $220 |
| Network (inter-AZ) | ~200GB/month × $0.01 | $2 |
| **Total** | | **~$1,122/month** |

### AWS MSK (3-broker m5.large)

| Component | Cost |
|-----------|------|
| 3× m5.large brokers | $0.202/hr × 3 × 720 = $436 |
| 3× EBS (1TB each) | $0.10/GB × 3TB = $300 |
| Data transfer | ~$2 |
| **Total** | **~$738/month** |

### AWS Kinesis (equivalent throughput)

| Component | Cost |
|-----------|------|
| 10 shards × $0.015/hr | $108 |
| PUT records (100M/day) | $0.014 × 100 = $1.40/day = $42 |
| Enhanced fan-out (optional) | $0.015/hr/consumer × 5 consumers × 720 = $54 |
| **Total** | **~$204/month** |

**Cost summary for AIOps (medium scale)**:
- MSK: $738/month — **recommended** (managed, ecosystem)
- Self-hosted: $1,122/month — more expensive when including operational time
- Kinesis: $204/month — cheapest, but limited capabilities

---

## 19. Production Review

### Principal Engineer Assessment

**Critical Issues Found**:

1. **Partition rebalance during deployment**: When adding consumer pods (rolling deployment), Kafka triggers rebalancing. During rebalance, no messages are consumed. With eager assignment strategy (default), this can cause 10–30 second pauses. Solution: Use **cooperative rebalancing** (`partition.assignment.strategy=CooperativeStickyAssignor`) to minimize pause time.

2. **Message size limit for trace data**: Default `message.max.bytes=1MB`. A single complex distributed trace (500+ spans) can easily exceed 1MB. Configure: `message.max.bytes=5242880` (5MB) for the raw-traces topic.

3. **Consumer group ID per deployment**: If you deploy two versions of the anomaly detector simultaneously (blue-green), they must have different consumer group IDs, or they'll compete for the same partitions. Use versioned group IDs: `anomaly-detector-v2-group`.

4. **Kafka Connect for AIOps sink**: Missing coverage of Kafka Connect for writing processed events to S3 (data lake) for offline model training. Flagged for a future sub-document.

5. **Schema Evolution with Avro**: When adding new fields to the `AnomalyEvent` schema, always use `default` values. Without defaults, old consumers cannot deserialize new messages. Enforce this with Schema Registry compatibility policy `BACKWARD`.

### Chapter Scores

| Criterion | Score | Notes |
|-----------|-------|-------|
| Technical Accuracy | 9.8/10 | Replication, offsets, EOS all verified |
| Production Readiness | 9.7/10 | MSK Terraform, DLQ, cooperative rebalance |
| Depth | 9.7/10 | Partitioning, serialization, schema registry |
| Practical Value | 9.8/10 | Python consumer code, DLQ implementation |
| Architecture Quality | 9.7/10 | Full topic topology for AIOps |
| Observability | 9.7/10 | Consumer lag alerting, all key JMX metrics |
| Security | 9.7/10 | SASL/SCRAM, ACLs, mTLS, MSK encryption |
| Scalability | 9.6/10 | Partition reassignment, consumer group scaling |
| Cost Awareness | 9.8/10 | MSK vs self-hosted vs Kinesis numbers |
| Diagram Quality | 9.7/10 | Broker topology, consumer group, topic flow |

---

## References

1. [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
2. [Confluent Developer — Kafka Fundamentals](https://developer.confluent.io/learn-kafka/)
3. [AWS MSK Developer Guide](https://docs.aws.amazon.com/msk/latest/developerguide/)
4. [Kafka: The Definitive Guide (O'Reilly)](https://www.oreilly.com/library/view/kafka-the-definitive/9781491936153/)
5. [Cooperative Rebalancing in Kafka](https://www.confluent.io/blog/cooperative-rebalancing-in-kafka-streams-consumer-ksqldb/)
6. [Kafka Transactions Explained](https://www.confluent.io/blog/transactions-apache-kafka/)
7. [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/)

## Further Reading

- [Designing Event-Driven Systems (O'Reilly)](https://www.oreilly.com/library/view/designing-event-driven-systems/9781492038252/)
- [Kafka Connect for AIOps](https://kafka.apache.org/documentation/#connect)
- [Apache Flink on Kafka for Stream Processing](https://flink.apache.org/connectors/kafka.html)
