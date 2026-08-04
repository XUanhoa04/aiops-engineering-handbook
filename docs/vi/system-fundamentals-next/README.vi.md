# Chapter S2 — System Fundamentals Next: từ kernel signal đến failure mechanics

> **Mục tiêu:** đi sâu hơn Chapter S, nối hành vi của CPU, memory, network, storage, distributed system, Kubernetes và AI infrastructure thành một mô hình điều tra thống nhất. Chương này không dạy thuộc lòng metric; nó dạy cách suy luận từ **cơ chế → dấu hiệu → giả thuyết → phép kiểm chứng → hành động an toàn**.

## Prerequisites

- Đã đọc [Chapter S — Nền tảng hệ thống](../system-fundamentals/README.vi.md).
- Hiểu process, container, Kubernetes Pod, TCP, database và ba loại telemetry cơ bản.
- Có thể đọc histogram, rate, counter, gauge và trace waterfall.

## Kết quả đầu ra

Sau chương này, bạn có thể:

1. giải thích tại sao utilization thấp vẫn có tail latency cao;
2. phân biệt CPU-bound, memory-bound, lock-bound, network-bound và storage-bound;
3. lần theo một request qua conntrack, NAT, TLS, load balancer, queue và database;
4. nhận ra failure do durability, consistency, fencing hoặc retry thay vì chỉ nhìn error rate;
5. xây evidence pack đủ mạnh để AIOps không kết luận từ một metric đơn lẻ;
6. chọn mitigation làm giảm tải mà không mở rộng blast radius.

> [!IMPORTANT]
> Các ngưỡng trong chương chỉ là điểm bắt đầu điều tra. Production alert phải dựa trên baseline theo workload, hardware, SLO và traffic shape; không copy một con số cố định cho mọi hệ thống.

## Mental model xuyên suốt

```mermaid
flowchart LR
    W[Workload arrival] --> Q[Queue / scheduler]
    Q --> E[Execution]
    E --> D[Dependency wait]
    D --> R[Response]

    C[Capacity] --> Q
    P[Policy: quota, timeout, retry] --> Q
    P --> D
    T[Topology and placement] --> E
    T --> D

    Q --> O[Observable signals]
    E --> O
    D --> O
    O --> H[Hypothesis]
    H --> X[Discriminating test]
    X --> M[Mitigation]
```

Mọi sự cố hiệu năng đều có thể bắt đầu bằng năm câu hỏi:

| Câu hỏi | Evidence ưu tiên |
|---|---|
| Work đến nhanh cỡ nào? | arrival rate, concurrency, burst size, fan-out |
| Work đang chờ ở đâu? | run queue, lock wait, socket queue, pool wait, device queue |
| Capacity thực dụng là bao nhiêu? | quota, throttling, memory bandwidth, IOPS, connection limit |
| Policy có khuếch đại tải không? | retry, timeout, autoscaling, health check, eviction |
| Failure có cùng phạm vi không? | node, zone, tenant, version, route, shard, dependency |

## Mục lục

1. CPU pipeline, cache và branch behavior
2. NUMA, memory locality và bandwidth
3. Lock contention, futex và scheduler interaction
4. Event loop, async runtime và coordinated omission
5. Conntrack, NAT và ephemeral port exhaustion
6. MTU, fragmentation và packet path
7. TLS, HTTP/2, HTTP/3 và head-of-line blocking
8. Load balancing, locality và connection reuse
9. Page cache, writeback và `fsync`
10. Filesystem, inode và copy-on-write amplification
11. WAL, checkpoint và database durability
12. LSM tree, B-tree, compaction và storage amplification
13. Quorum, consensus, lease và fencing
14. Idempotency, deduplication và transactional outbox
15. Tail latency, fan-out và hedged requests
16. Admission control, load shedding và retry budget
17. Kubernetes control-plane failure mechanics
18. Scheduling, placement, disruption và rollout safety
19. Identity, certificate và secret delivery path
20. GPU memory hierarchy và interconnect
21. LLM serving: batching, KV cache và queue policy
22. Cross-layer evidence graph
23. Incident playbooks
24. Production readiness checklist

---

# SECTION 1 — COMPUTE, MEMORY VÀ RUNTIME

## 1. CPU pipeline, cache và branch behavior

### 1.1 CPU utilization không phải throughput

CPU hiện đại thực thi nhiều instruction song song, dự đoán nhánh và nạp dữ liệu qua nhiều tầng cache. Hai process cùng dùng `60% CPU` có thể cho throughput rất khác:

- workload A có working set nằm trong L1/L2 cache;
- workload B liên tục miss LLC và chờ DRAM;
- workload C bị branch misprediction làm pipeline flush;
- workload D chạy vectorized instruction và hoàn thành nhiều work hơn mỗi cycle.

Vì vậy, `CPU%` chỉ trả lời CPU có bận hay không; nó không trả lời CPU có **tiến triển hữu ích** hay không.

### 1.2 Bộ evidence tối thiểu

| Signal | Câu hỏi nó trả lời | Diễn giải thận trọng |
|---|---|---|
| instructions / cycle | mỗi cycle hoàn thành bao nhiêu work | IPC giảm có thể do cache miss, branch miss hoặc dependency chain |
| cycles | CPU đã tiêu bao nhiêu cycle | cần chuẩn hóa theo request hoặc unit of work |
| cache misses | dữ liệu có gần compute không | miss rate tăng sau deploy thường gợi ý working-set/layout đổi |
| branch misses | control flow có khó dự đoán không | hay gặp ở parser, interpreter, polymorphic dispatch |
| run queue | thread runnable có phải chờ CPU không | queue cao kéo dài mới là saturation evidence mạnh |
| throttled time | quota có chặn execution không | utilization trung bình thấp vẫn có thể throttle theo từng period |

Ví dụ quan sát trên Linux:

```bash
perf stat -e cycles,instructions,cache-references,cache-misses,branches,branch-misses -p <pid>
pidstat -u -w -p <pid> 1
cat /proc/pressure/cpu
```

Không chạy profiling tần suất cao trên toàn fleet. Bắt đầu bằng counter rẻ, sau đó profile có mục tiêu trên canary hoặc trong cửa sổ ngắn.

### 1.3 Failure pattern: CPU bận nhưng request không tiến triển

```mermaid
flowchart TD
    A[p99 tăng] --> B{Run queue tăng?}
    B -->|Có| C[CPU scheduling saturation]
    B -->|Không| D{IPC giảm?}
    D -->|Có| E{Cache/branch miss tăng?}
    E -->|Cache| F[Memory locality / working set]
    E -->|Branch| G[Control-flow regression]
    D -->|Không| H[Kiểm tra lock, GC, syscall và dependency wait]
```

Mitigation an toàn thường là giảm concurrency, rollback code path gây regression, tách noisy neighbor hoặc tăng capacity đúng loại. Tăng CPU limit không chữa được cache locality kém hay global lock.

## 2. NUMA, memory locality và bandwidth

### 2.1 Tại sao NUMA xuất hiện như một gray failure

Trên máy nhiều socket, mỗi CPU truy cập local memory nhanh hơn remote memory. Container có thể được schedule CPU ở NUMA node 0 nhưng phần lớn page lại nằm ở node 1. Không có crash; chỉ có latency tăng, throughput giảm và symptom thay đổi theo placement.

Các nguồn gây lệch locality:

- process khởi tạo memory trước khi worker thread được pin;
- Pod đổi CPU set nhưng page không migrate tương ứng;
- memory reclaim làm page placement thay đổi;
- device/GPU/PCIe nằm gần một NUMA node khác;
- huge page bị phân mảnh hoặc cấp phát từ node xa.

### 2.2 Phân biệt capacity và bandwidth

Memory còn trống không có nghĩa memory subsystem còn khả năng phục vụ. Workload analytics, compression, model inference và packet processing có thể chạm trần memory bandwidth trước khi CPU đạt 100%.

```bash
numactl --hardware
numastat -p <pid>
cat /proc/<pid>/numa_maps
```

Evidence pack nên có:

- CPU set và memory set của cgroup;
- local/remote page ratio;
- memory bandwidth theo socket nếu hardware counter hỗ trợ;
- latency theo node placement;
- version, instance type và topology của device.

> [!TIP]
> Nếu cùng image, cùng traffic nhưng chỉ một nhóm node chậm, hãy group theo NUMA topology, CPU model, kernel và device placement trước khi kết luận application regression.

## 3. Lock contention, futex và scheduler interaction

### 3.1 Utilization thấp vẫn có thể lock-bound

Thread chờ mutex thường ngủ qua `futex`; CPU utilization giảm trong khi latency tăng. Nếu lock holder bị deschedule, mọi waiter bị kéo dài dù machine còn CPU idle. Đây là **lock convoy**.

Các pattern phổ biến:

| Pattern | Dấu hiệu | Ví dụ |
|---|---|---|
| global mutex | throughput không scale theo core | cache map hoặc allocator dùng lock chung |
| lock convoy | nhiều thread wake/sleep quanh một lock | critical section có I/O hoặc page fault |
| priority inversion | work quan trọng chờ thread ưu tiên thấp | lock holder bị CPU pressure |
| false sharing | CPU cao, cache coherence traffic cao | counter của nhiều thread chung một cache line |
| deadlock | progress dừng, waiter ổn định | lock ordering không nhất quán |

### 3.2 Evidence và phép kiểm chứng

```bash
perf lock record -p <pid> -- sleep 10
perf lock report
perf sched record -p <pid> -- sleep 10
perf sched timehist
```

Trong runtime có managed thread, kết hợp native evidence với thread dump, blocked-time histogram và span quanh critical section. Một thread dump đơn lẻ là snapshot; lấy vài snapshot cách nhau mới phân biệt waiter thoáng qua với contention kéo dài.

Mitigation ưu tiên:

1. loại I/O và blocking call khỏi critical section;
2. shard lock theo key hoặc tenant;
3. giảm concurrency trước khi tăng replica nếu dependency chung đang bão hòa;
4. rollback thay đổi data structure/allocator;
5. chỉ thay lock-free algorithm khi đã chứng minh contention, vì correctness cost rất cao.

## 4. Event loop, async runtime và coordinated omission

### 4.1 Event loop lag là một queue

Async runtime không loại bỏ waiting; nó gom waiting vào event loop, executor, callback queue và connection pool. Một callback CPU-heavy hoặc synchronous syscall có thể chặn mọi request dùng chung loop.

Các signal cần tách:

- event-loop lag;
- runnable task count;
- executor queue depth;
- active và pending connection;
- GC pause;
- request concurrency và service time;
- time spent trước khi handler bắt đầu chạy.

### 4.2 Coordinated omission làm histogram “đẹp giả”

Nếu load generator chỉ gửi request mới sau khi request trước hoàn thành, lúc server đứng 5 giây nó cũng ngừng gửi. Histogram bỏ sót chính khoảng thời gian tệ nhất. Production traffic theo open-loop arrival thường không lịch sự như vậy.

Để benchmark đáng tin:

- mô hình arrival độc lập với completion;
- ghi cả queue delay và service time;
- giữ intended send time để hiệu chỉnh coordinated omission;
- kiểm tra histogram theo route, tenant và payload size;
- báo cả throughput bị từ chối, không chỉ latency request thành công.

### 4.3 Cây quyết định runtime

```mermaid
flowchart TD
    A[Latency tăng] --> B{Event-loop lag tăng?}
    B -->|Có| C{CPU / GC tăng?}
    C -->|CPU| D[Callback hoặc serialization nặng]
    C -->|GC| E[Allocation pressure / heap policy]
    C -->|Không| F[Blocking syscall hoặc lock]
    B -->|Không| G{Executor/pool queue tăng?}
    G -->|Có| H[Worker hoặc dependency saturation]
    G -->|Không| I[Đi tiếp network/storage/dependency path]
```

---

**Checkpoint Section 1:** trước khi gọi một workload là “CPU issue”, phải trả lời được nó đang chờ scheduler, memory, lock, runtime queue hay thực sự tiêu instruction hữu ích.
