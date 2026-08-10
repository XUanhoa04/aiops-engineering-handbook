# Chapter 21 — AIOps End-to-End: từ một datapoint telemetry đến closed-loop remediation

> **Chapter này nối toàn bộ handbook thành một đường đi có thể kiểm chứng: telemetry → preprocessing → baseline → anomaly → alert → incident → RCA → quyết định → safety gate → action → verification → rollback/escalation → audit. Mục tiêu không phải thêm một danh sách thuật toán, mà là giải thích từng con số, từng state transition và từng nơi hệ thống có thể sai.**

---

## Cách đọc chapter này

Đối tượng chính là intern hoặc engineer junior-to-medium đã biết metric, log, trace, Kubernetes và SLO ở mức nền tảng. Mỗi khái niệm quan trọng được đọc theo năm lớp:

1. **Trực giác:** nó giải quyết nỗi đau vận hành nào?
2. **System view:** component nào nhận input gì và xuất output gì?
3. **Toán học:** con số được tính như thế nào?
4. **Ví dụ:** một bộ số nhỏ đi qua phép tính ra sao?
5. **Production implication:** failure mode, trade-off và guardrail là gì?

Chapter dùng một incident xuyên suốt: connection pool tới database của `payment` bị bão hòa, làm latency `payment` tăng, `checkout` timeout, `api-gateway` trả lỗi và người dùng `frontend` checkout thất bại. Một fault độc lập ở `inventory` sẽ nổ khi incident đầu còn mở để kiểm tra masking. Một case memory leak chưa có trong fault catalog kiểm tra khả năng xử lý lỗi chưa từng thấy.

Sáu câu sau là “lan can tư duy” của toàn bộ thiết kế:

```text
Telemetry không phải Alert.
Anomaly không phải Incident.
Incident symptom không phải Root Cause.
Correlation không phải Causality.
Command success không phải Remediation success.
Remediation chỉ thành công khi telemetry về customer outcome thật sự phục hồi.
```

Các con số benchmark ở cuối chapter được đánh dấu **minh họa**. Chúng chỉ chỉ ra cách đo trên một labeled replay dataset; không phải kết quả production đã được thực nghiệm trong repository này.

---

## 1. Vì sao bài toán end-to-end khó hơn một detector tốt?

Một detector có thể tính modified z-score hoàn hảo nhưng hệ thống AIOps vẫn thất bại. Nó có thể nhận counter reset như error spike, page năm lần cho cùng một cascade, gọi service gần người dùng nhất là root cause, scale nhầm app làm database cạn connection hơn, rồi tuyên bố thành công chỉ vì Kubernetes API trả HTTP 200. Sai lầm không nằm riêng trong công thức; nó nằm ở các contract giữa các bước.

Production đặt ra ba loại yêu cầu đồng thời.

- **Statistical correctness:** “normal” phải đúng với service, tín hiệu, cohort và thời điểm; detector phải bền trước outlier, drift, seasonality và missing data.
- **Operational correctness:** anomaly phải qua persistence, impact, dedup, incident lifecycle và ownership trước khi đánh thức người. Incident dài không được tự biến mất; fault thứ hai không bị fault đầu che.
- **Control correctness:** RCA phải trình bày bằng chứng và uncertainty; automation chỉ được hành động trong policy; verify phải dùng outcome độc lập; failure phải rollback hoặc escalate; mọi quyết định phải tái dựng được.

Một datapoint `payment.p95_latency=980ms` không tự mang nghĩa. Ta cần biết đó là p95 của cửa sổ nào, có bao nhiêu request, timestamp có trễ không, baseline của đúng `payment` lúc đó là bao nhiêu, deploy nào đang diễn ra, SLO checkout bị ảnh hưởng không và trace có dành 900 ms trong child span gọi database hay không. Một giá trị không có identity, context và quality chỉ là số.

### 1.1 Bốn object không được trộn

| Object | Định nghĩa | Ví dụ | Owner chính |
|---|---|---|---|
| Observation | Giá trị đo được kèm thời gian, scope, quality | `payment:p95=980ms`, 18.400 request | Telemetry/data plane |
| Anomaly | Một signal lệch khỏi expectation của chính nó | robust score latency = 7,4 | Detector |
| Alert | Anomaly đủ lâu và đủ ảnh hưởng để cần chú ý | `payment_latency` chuyển `FIRING` | Alert policy |
| Incident | Một hoặc nhiều alert cùng customer impact/context | `INC-102`, checkout degradation | Incident manager |
| Root-cause hypothesis | Candidate giải thích được propagation tốt nhất | `payment-db pool exhaustion`, confidence 0,86 | RCA engine |

Root cause trong bảng là **giả thuyết có hạng**, không phải fact tuyệt đối. Fact là pool utilization đạt 100%, pool wait tăng và trace lỗi ở `acquire_connection`. Inference là pool exhaustion nhiều khả năng tạo cascade.

### 1.2 Tiêu chuẩn thành công

Hệ thống đạt yêu cầu không phải khi “có AI” mà khi chứng minh được:

- bắt fault thật trước deadline với precision/recall có denominator rõ;
- không page traffic spike khỏe hoặc một noise spike;
- giữ `FIRING` xuyên incident dài và tách fault concurrent;
- rank root candidate bằng topology, thời gian, trace và counter-evidence;
- chỉ auto-act khi policy cho phép và input còn fresh;
- xác nhận recovery bằng telemetry thật, rollback khi không cải thiện;
- replay được toàn bộ decision chain từ immutable audit events.

---

## 2. Bản đồ end-to-end và hợp đồng của từng box

```text
Application / Kubernetes / Cloud billing
        │
        ├── metrics ──┐
        ├── logs ─────┼──> OTel/metric collectors
        └── traces ───┘           │
                                  v
                         Stream + telemetry stores
                                  │
                                  v
                     Normalize / clean / aggregate
                                  │
                                  v
                   Per-service feature extraction
                                  │
                                  v
           Baseline state ──> Anomaly detector ──> anomaly events
                                  │
                                  v
                       Alert qualification
                                  │
                                  v
                Incident correlation / partitioning
                                  │
                                  v
             Topology + traces ─> RCA evidence ranking
                                  │
                                  v
                    Incident summary + decision
                                  │
                                  v
             Policy / safety guard / dry-run / lease
                                  │
                                  v
                         Action executor
                                  │
                                  v
                 Post-action telemetry verification
                         │                  │
                     success            failure
                         │                  │
                    recover       rollback / escalate
                         └──────────┬───────┘
                                    v
                         append-only audit log
```

Mỗi box phải có input/output/state/trigger/failure mode rõ ràng:

| Box | Input | Output | State phải giữ | Cách chạy | Failure mode điển hình |
|---|---|---|---|---|---|
| Collector | raw metric/log/span | record có resource identity | queue, retry cursor | event-driven | drop, backpressure, clock skew |
| Preprocessor | records nhiều schema | feature bucket đã chuẩn hóa | watermark, counter predecessor | stream + interval | reset thành spike, missing thành zero |
| Baseline engine | accepted historical samples | center, scale, quantile, quality | ring buffer/sketch, freeze epoch | mỗi 45 giây và incremental ingest | contamination, stale baseline |
| Detector | current feature + baseline | anomaly event/score | state per service-signal | interval 45 giây | MAD bằng 0, noisy flip |
| Qualifier | anomaly + SLO/traffic | alert transition | persistence counters, cooldown | mỗi evaluation | page spike, suppress fault thật |
| Correlator | alert events + graph | incident revision | membership, partition | event-driven | false merge, false split |
| RCA | incident + evidence | ranked candidates | evidence ledger, topology revision | fast/deep revisions | correlation thành causation |
| Decision/safety | root hypothesis + policy | approved action envelope | attempts, lease, cooldown | event-driven | stale/unsafe action |
| Executor | immutable action envelope | execution result | idempotency key, before-state | controller reconcile loop | duplicate mutation, partial action |
| Verifier | pre/post/control telemetry | success/fail/inconclusive | verification windows | interval | traffic drop tạo false success |
| Audit | mọi transition | reconstructable event chain | append-only records | event-driven | audit outage, missing version |

### 2.1 Event-time và processing-time

`event_time` là lúc hiện tượng xảy ra tại nguồn; `ingest_time` là lúc collector nhận; `processing_time` là lúc engine xử lý. Detector dùng event-time để xếp window, nhưng dùng processing-time cho SLO freshness. Điểm 10:03 đến lúc 10:08 không được giả làm dữ liệu hiện tại. Nó có thể sửa evidence revision, nhưng không được kích hoạt lại action đã hết hiệu lực.

### 2.2 Output là typed event, không phải chuỗi văn bản

Mỗi transition cần stable key, version và provenance. Ví dụ anomaly event tối thiểu:

```json
{
  "event_id": "anom/payment/p95_latency/2026-08-10T10:04:30Z/v1",
  "event_time": "2026-08-10T10:04:30Z",
  "ingest_time": "2026-08-10T10:04:36Z",
  "service": "payment",
  "signal": "p95_latency_ms",
  "current": 275.0,
  "expected": {"median": 121.0, "mad": 14.0, "window": "60m"},
  "score": 7.4,
  "detector_state": "SUSPECT",
  "sample_count": 18400,
  "data_quality": "GOOD",
  "rule_version": "robust-v7"
}
```

Nếu chỉ publish `payment anomaly=true`, downstream không biết score nào, baseline nào, số request bao nhiêu hay có thể replay không.

---

## 3. Hệ thống ví dụ và causal story xuyên chapter

```text
User
  │
  v
Frontend ──> API Gateway ──> Checkout ──> Payment ──> Payment DB
                                  │            │
                                  │            └──> External Provider
                                  ├──> Inventory
                                  └──> Redis
```

Hướng cạnh là caller → callee. `Checkout → Payment` nghĩa là checkout phụ thuộc payment. Causal cascade chính:

```text
Payment DB connection capacity exhausted
    → pool wait và acquire timeout trong Payment
    → Payment p95/error/retry/queue tăng
    → Checkout child spans gọi Payment chậm và timeout
    → API trả 5xx
    → Frontend checkout success giảm
```

Telemetry được theo dõi không chỉ có CPU:

| Nhóm | Feature production-friendly | Ý nghĩa |
|---|---|---|
| Traffic | RPS, completed requests, cohort share | mẫu số và load context |
| Error | 5xx rate, business failure, timeout, retry | user-visible failure và amplification |
| Latency | p50/p95/p99, histogram count | tail latency, không average mù |
| Saturation | CPU throttling, memory pressure, pool utilization | tài nguyên gần giới hạn |
| Queue | depth, oldest age, enqueue/dequeue rate, slope | backlog và time-to-drain |
| Dependency | span duration/error theo edge | propagation caller-callee |
| Cost | CPU-hours/request, DB I/O/request, estimated cost/hour | bất thường hiệu suất/chi phí |
| Change | deploy ID, config, feature flag, autoscaling | confounder hoặc cause candidate |

### 3.1 “Normal” không đồng nghĩa “nhỏ”

`search` có p95 bình thường 700 ms vì query phức tạp; `payment-tokenize` bình thường 40 ms. Giá trị 300 ms bình thường với `search` nhưng là tăng 7,5 lần với `payment-tokenize`. Detector chính phải định danh theo ít nhất `(tenant hoặc environment, service, route/cohort, signal, version semantics)`, không dùng `latency > 500ms` cho mọi service.

Static limit vẫn cần cho ranh giới vật lý hoặc SLO: certificate còn 7 ngày, disk 95%, ready replica bằng 0, burn rate 14,4x. Nó là safety/SLO rule song song, không thay behavioral baseline.

### 3.2 Scenario thứ hai: fault chưa từng thấy

Một phiên bản `inventory` mới giữ reference trong cache theo request ID, tạo memory leak chậm. Không có rule `if inventory_memory_leak_v42`. Detector nhìn behavioral deviation: working set slope tăng, GC pause tăng, p99 tăng trong khi traffic theo seasonal normal. RCA thấy anomaly bắt đầu tại inventory, child spans từ checkout dành phần lớn latency tại inventory và không có callee đỏ. Nó có thể rank `inventory runtime/resource exhaustion` dù chưa gọi đúng class leak. Đây là khác biệt giữa **known fault classification** và **unknown anomaly + evidence-based localization**.

---

## 4. Telemetry ingest: một datapoint thực sự đến từ đâu?

### 4.1 Metrics

Prometheus scrape counters, gauges và histograms từ application/Kubernetes exporters. Với request error rate, raw inputs thường là hai counter:

```text
http_requests_total{service="payment",status_class="5xx"}
http_requests_total{service="payment"}
```

Feature đúng cho bucket 1 phút là:

```text
sum(rate(errors_total[1m])) / sum(rate(requests_total[1m]))
```

Không lấy trung bình error rate của từng pod nếu traffic pod khác nhau. Pod A 1 lỗi/1 request và pod B 0 lỗi/9.999 request cho error rate toàn service 0,01%, không phải trung bình `(100%+0%)/2=50%`.

Latency dùng histogram và tính quantile sau khi aggregate bucket tương thích. Average không thấy tail: 99 request 100 ms và một request 10 s có mean 199 ms, nhưng p99/p99.9 thể hiện pain khác. Histogram boundary và aggregation semantics phải versioned; đổi bucket là schema change.

### 4.2 Logs

Logs bổ sung error class, timeout target, pool exception và deploy revision. Chúng thường được template hóa thành count/rate thay vì đưa raw text vào detector:

```text
log_error_rate{service="payment",template="db_pool_timeout"}
unique_error_templates_5m
new_error_template_flag
```

Raw log có thể chứa PII, secret và attacker-controlled text. Redaction, tenant isolation và provenance diễn ra trước khi summary/RCA dùng nó. Một dòng “Payment DB is root cause” trong log là dữ liệu không tin cậy, không phải fact.

### 4.3 Traces

OpenTelemetry span mang `trace_id`, `span_id`, parent, service, operation, start/end, status và attributes đã allowlist. Từ đó feature plane tạo:

- latency/error theo edge `checkout → payment`;
- tỷ lệ parent span chậm có child span payment chậm;
- critical-path contribution;
- first-error span distribution;
- trace coverage và sampling bias.

Sampling 5% không có nghĩa evidence vô dụng, nhưng confidence phải phản ánh sample size và sampling policy. Tail sampling ưu tiên trace lỗi có thể làm error proportion trong trace cao hơn thực tế; RCA dùng trace để chứng minh đường propagation, không lấy sampled trace ratio làm SLI nếu chưa hiệu chỉnh.

### 4.4 Infrastructure, topology, change và cost

Kubernetes API cung cấp pod readiness, restart, replica, HPA, node/zone và owner reference. Service mesh/traces cung cấp dependency edges. CI/CD gửi deploy event với version, scope và rollout fraction. Cloud billing đến chậm hơn metrics; near-real-time cost thường là ước tính `resource_usage × unit_price`, sau đó reconcile với invoice.

Cost nên normalize theo work unit: `CPU-seconds/request`, `DB-read/request`, `cost/checkout-success`. Cost/hour tăng 5x cùng traffic 5x có thể bình thường; cost/success tăng 5x trong khi traffic không đổi mới đáng nghi.

### 4.5 Contract chất lượng đầu vào

Mỗi record cần:

```text
identity + schema_version + event_time + ingest_time
+ service/route/cohort + value/unit + source
+ freshness + coverage + missingness + provenance
```

Collector phải tự phát telemetry: accepted/dropped records, queue age, export failure, clock offset, cardinality rejected và schema error. Detector “xanh” trên một data plane đang drop 30% points không đáng tin.

---

## 5. Preprocessing: từ raw samples tới feature có thể so sánh

Preprocessing không phải housekeeping phụ. Nhiều false alert bắt nguồn từ đây hơn từ model.

### 5.1 Align theo event-time bucket

Giả sử scrape interval 15 giây nhưng detector evaluate mỗi 45 giây. Feature layer có thể giữ bucket 1 phút theo event-time. Watermark cho phép dữ liệu đến trễ tối đa, ví dụ 90 giây. Bucket chưa đóng được đánh `PARTIAL`; detector không so một partial request count với full bucket rồi gọi traffic drop.

Nếu cần phản ứng nhanh hơn một phút, có thể dùng 45-second bucket hoặc streaming aggregate. Quan trọng là `current` và history có cùng duration/semantics. So rate 15 giây với baseline rate 1 phút tạo variance khác nhau.

### 5.2 Counter reset

Counter Prometheus chỉ tăng cho tới khi pod restart. Raw delta âm không phải “âm 4 triệu request”. `rate()` nhận biết reset trên từng series trước khi sum. Nếu sum counters của nhiều pod rồi mới tính delta, một pod reset có thể bị pod khác che. Quy tắc là **rate per monotonic series, rồi aggregate**.

Nếu reset metadata thiếu, bucket nhận `COUNTER_RESET_SUSPECTED`; error rate có thể vẫn tính nếu numerator/denominator đủ, nhưng confidence hạ. Không biến missing/error counter thành zero.

### 5.3 Missing, duplicate, late và out-of-order

- Missing là `null + reason`, không là 0.
- Duplicate được bỏ bằng `(source_id, series, event_time, sequence)` hoặc idempotency key.
- Late point trước watermark cập nhật bucket; sau watermark tạo revision và quality flag.
- Out-of-order được sắp theo event-time trong stateful window, không theo arrival.

Nếu 40% request series mất nhưng error series còn, tỷ lệ error không còn mẫu số tin cậy. Detector chuyển `DATA_INSUFFICIENT`, giữ incident đang active và page telemetry pipeline nếu cần; tuyệt đối không coi missing là recovery.

### 5.4 Cleaning không được xóa sự cố

Winsorize hoặc clip có thể giúp model không nổ số, nhưng không được xóa raw value. Giữ hai trường:

```text
observed_raw = 12000 ms
model_input = min(log1p(observed_raw), configured_cap)
```

Một spike đơn có thể là noise, nhưng quyết định đó thuộc persistence/quality, không phải lặng lẽ drop mọi outlier. Nếu preprocessor loại chính điểm bất thường, detector không thể có recall.

### 5.5 Feature extraction theo semantics

| Signal | Feature chính | Context/gate bổ sung | Sai lầm thường gặp |
|---|---|---|---|
| Latency | p95/p99, `log1p(latency)` | request count, route mix | average mọi route |
| Error | errors/requests | minimum requests, Wilson interval | 1/1 = page 100% |
| Saturation | utilization, throttle time | desired replicas, limits | CPU cao = incident |
| Queue | depth, oldest age, slope | arrival/service rate | chỉ nhìn level |
| Cost | cost/work unit, rate of change | business volume, price change | cost/hour không normalize |
| Traffic | RPS residual theo season | campaign/calendar | traffic cao = xấu |

`queue_depth=10.000` có thể ổn nếu consumer drain 5.000/s; `queue_depth=500` có thể nguy hiểm nếu oldest age 20 phút và drain bằng 0. Vì vậy vẫn có detector univariate cho từng signal, nhưng qualification kết hợp semantics.

### 5.6 Output của feature plane

```text
FeaturePoint {
  key: (environment, service, route, signal),
  event_window: [start, end),
  value, unit,
  numerator?, denominator?,
  sample_count,
  quality: GOOD | PARTIAL | STALE | MISSING | RESET_SUSPECTED,
  context: {traffic, deploy_id, version, region},
  provenance: query_hash + source_offsets
}
```

Feature plane tự monitor freshness p50/p99, late ratio, dropped cardinality, bucket revisions và query errors. Khi feature semantics đổi, version mới warm up song song; không nối lịch sử v1 với v2 như cùng phân phối.

---

## 6. Baseline: “normal” được định nghĩa thế nào?

Baseline là một **expectation có điều kiện**, không chỉ một số trung bình. Với key `prod/payment/POST_checkout/p95_latency`, baseline có thể chứa:

```text
center = rolling median
scale = MAD đã hiệu chỉnh
upper_quantile = rolling p95 của feature
trend = EWMA residual
seasonal_slot = Monday 10:00 ± 15m
quality = sample count, missing ratio, age
update_policy = accepted/quarantined/frozen
version = baseline-v12
```

Normal toán học là vùng giá trị có residual đủ nhỏ so với scale kỳ vọng, **trong đúng context**. Một dạng đơn giản:

```text
residual_t = x_t - expected_t
score_t = directional(residual_t) / robust_scale_t
normal nếu score_t < fire_threshold và quality đủ tốt
```

Với error/latency/queue, ta thường quan tâm upper anomaly; latency giảm không xấu. Với traffic, cả tăng và giảm đều có thể bất thường. Với cost/request, tăng là xấu còn giảm cần kiểm tra correctness. Hàm `directional()` phải theo semantics, không luôn lấy trị tuyệt đối.

### 6.1 So sánh các baseline phổ biến

| Method | Cách tính | Ưu điểm | Nhược điểm | Khi dùng | Failure mode |
|---|---|---|---|---|---|
| Static threshold | `x > T` | rẻ, audit dễ, phù hợp physical/SLO limit | không hiểu service/context | disk, cert, ready=0, burn rate | báo oan service chậm bình thường; bỏ sót service nhanh bị chậm |
| Mean + standard deviation | `z=(x-μ)/σ` | incremental dễ, quen thuộc | mean/σ bị outlier kéo | dữ liệu gần Gaussian, sạch | incident nâng cả center và spread, tự che |
| Median + MAD | `median`, `median(|x-median|)` | robust, explainable | MAD=0; không tự hiểu mùa | default cho per-key rolling baseline | gradual drift/seasonality; window nhỏ |
| EWMA | `S_t=αx_t+(1-α)S_{t-1}` | nhẹ, theo trend nhanh | dễ học anomaly; phụ thuộc α | smooth trend/residual, fast path | sustained incident trở thành normal |
| Rolling quantile | p95/p99 của history | không giả Gaussian, hợp tail | cần đủ mẫu/sketch; quantile rung | latency/queue skewed | low volume và merge sketch sai |
| Seasonal baseline | so cùng slot ngày/tuần | hiểu daily/weekly traffic | cần tuần lịch sử, holiday khác | traffic, business cycles | event đặc biệt hoặc DST/calendar shift |
| Holt-Winters/STL | level + trend + season | tách seasonal/trend | tuning, history, missing phức tạp | series mùa rõ | regime change và contaminated season |
| Change-point | xác nhận phân phối đổi regime | phân biệt shift lâu dài | không nói shift tốt hay xấu | deploy/drift confirmation | incident dài bị gọi regime mới |

Không có thuật toán thắng mọi series. Baseline production nên là ensemble nhỏ, có semantics rõ:

```text
rolling median + MAD (60m accepted samples)
+ fast 5m residual/persistence
+ EWMA trend chậm
+ seasonal reference khi đủ lịch sử
+ traffic/data-quality gates
+ freeze/quarantine khi incident
```

### 6.2 Mean/standard deviation và masking

Giả sử `[100, 101, 99, 100, 100, 100, 800]`. Mean tăng lên 200; standard deviation cũng phình mạnh. Một điểm 500 tiếp theo có z-score không lớn như trực giác vì chính outlier 800 đã kéo baseline. Đây là **masking** trong cùng series. Median vẫn 100; MAD vẫn rất nhỏ. Robust estimator không giải quyết mọi masking, nhưng giảm khả năng một spike làm spread lớn tới mức che fault sau.

### 6.3 EWMA và ý nghĩa của alpha

```text
S_t = αx_t + (1-α)S_(t-1)
```

`α=0,2` nghĩa observation mới chiếm 20%, lịch sử nén chiếm 80%. Alpha lớn phản ứng nhanh nhưng học cả noise/anomaly; alpha nhỏ ổn định nhưng chậm theo legitimate change. EWMA nên cập nhật từ **accepted samples**, hoặc có fast và slow EWMA để nhìn divergence. Nó không phải phép màu tự biết điểm nào xấu.

### 6.4 Seasonal expectation

Traffic ví dụ 09:00=2k RPS, 12:00=8k, 20:00=3k. Rolling 60 phút lúc 12:00 có thể coi 8k là bất thường mỗi ngày. Seasonal baseline so Tuesday 12:00 với các Tuesday/weekday 12:00 trước, dùng median theo slot và MAD across weeks. Calendar feature đánh dấu payday/campaign/holiday. Nếu chỉ có hai tuần dữ liệu hoặc business vừa đổi, seasonal confidence thấp và detector dùng fallback bảo thủ.

---

## 7. Baseline riêng cho từng service và từng signal

Đơn vị state tối thiểu là:

```text
DetectorKey = environment + service + route/cohort + signal
```

Ví dụ:

```text
payment:p95_latency      → median 120 ms, MAD 14 ms, upper-only
payment:error_rate       → median 0,18%, MAD 0,07%, min 500 req
payment:queue_oldest_age → median 2,1 s, MAD 0,8 s, upper-only
checkout:p95_latency     → median 180 ms, MAD 20 ms
checkout:error_rate      → median 0,35%, MAD 0,11%
inventory:memory_slope   → median 0,3 MiB/min, MAD 0,2 MiB/min
```

Nếu tạo baseline quá thô theo service, route hiếm bị route phổ biến che. Nếu tạo quá mịn theo pod, method, status, customer ID, cardinality và sparse data bùng nổ. Production thường có hierarchy:

1. service-level detector luôn có;
2. route/journey cho critical path;
3. region/tenant slice theo risk và đủ volume;
4. pod-level dùng cho diagnosis, không page trực tiếp trừ safety invariant.

Cold key có thể shrink về baseline cha: route mới dùng prior của service với threshold rộng và state `WARMING`, thay vì giả vờ đã biết normal. Khi đủ accepted samples, weight chuyển dần về local baseline.

### 7.1 Baseline signal-specific

Latency thường lệch phải, nên dùng `log1p(x)` hoặc rolling quantile; error rate là tỷ lệ có uncertainty phụ thuộc denominator; CPU bounded 0–100 và có thể tốt khi cao; queue cần level + slope/age; cost cần normalize workload. Cùng một công thức robust score có thể dùng, nhưng scale, direction, gate và interpretation khác nhau.

### 7.2 Baseline không phải training set bất biến

State phân ba lớp:

- **candidate sample:** vừa quan sát, chưa biết sạch;
- **accepted sample:** quality tốt, không thuộc confirmed anomaly/maintenance bất thường;
- **quarantined sample:** nằm trong incident hoặc context chưa xác nhận.

Baseline active chỉ cập nhật bằng accepted samples. Quarantine vẫn lưu để forensic và có thể promote sau khi change được xác nhận legitimate. Không xóa evidence.

---

## 8. Rolling median + MAD: tính từng con số

Xét mười bucket latency bình thường của `payment`:

```text
100, 102, 98, 101, 99, 100, 103, 98, 101, 100 (ms)
```

Sắp xếp:

```text
98, 98, 99, 100, 100, 100, 101, 101, 102, 103
```

Vì có 10 điểm, median là trung bình điểm thứ 5 và 6: `(100+100)/2=100 ms`. Median là “người đứng giữa”; một điểm cực lớn ít kéo nó hơn mean.

Absolute deviations so với median 100:

| x | `|x-100|` |
|---:|---:|
| 100 | 0 |
| 102 | 2 |
| 98 | 2 |
| 101 | 1 |
| 99 | 1 |
| 100 | 0 |
| 103 | 3 |
| 98 | 2 |
| 101 | 1 |
| 100 | 0 |

Sắp deviations: `0,0,0,1,1,1,2,2,2,3`. Median của deviations là `(1+1)/2=1 ms`. Vậy `MAD=1 ms`.

Robust score:

```text
score(x) = |x - median| / (1.4826 × MAD + ε)
```

Với `ε` rất nhỏ, ví dụ 1 ms theo floor semantics của metric:

| Current x | Residual | Denominator nếu ε≈0 | Robust score xấp xỉ |
|---:|---:|---:|---:|
| 103 | 3 | 1,4826 | 2,02 |
| 180 | 80 | 1,4826 | 53,96 |
| 210 | 110 | 1,4826 | 74,19 |
| 250 | 150 | 1,4826 | 101,17 |

Các score rất lớn vì chuỗi đồ chơi quá ổn định; production có noise cao hơn và dùng scale floor. `1,4826` là hệ số làm MAD có cùng scale xấp xỉ standard deviation nếu dữ liệu thật sự Gaussian. Không nhân hệ số này vẫn xếp hạng được, nhưng threshold “3 sigma” không còn cùng trực giác.

`ε` ngăn chia cho 0 khi mọi điểm bằng nhau. Tuy nhiên chọn `ε=10^-9` cho latency khiến 100→101 ms tạo score khổng lồ vô nghĩa. Production dùng:

```text
effective_scale = max(1.4826 × MAD, signal_scale_floor)
```

Ví dụ floor latency là `5 ms` hoặc tỷ lệ 5% center. Khi đó 180 có score `80/5=16`, vẫn bất thường; 101 có `1/5=0,2`, không báo. Epsilon đảm bảo số học; scale floor biểu diễn resolution/noise tối thiểu. Hai vai trò khác nhau.

### 8.1 Threshold không trực tiếp đồng nghĩa page

Giả sử `suspect_threshold=3,5`, `fire_threshold=4,0`. Điểm 180 vượt rất mạnh nhưng vẫn chỉ tạo một evaluation bất thường. Qualifier có thể yêu cầu 3/5 evaluations hoặc kết hợp SLO impact. Một spike 180 rồi về 100 không page; chuỗi 180,210,250 khiến state đi `SUSPECT→FIRING`.

### 8.2 MAD bằng 0 và discrete metric

Ready replicas thường `[6,6,6,...]`, MAD=0. Đây là metric discrete có invariant rõ; dùng static rule `ready < desired`, không ép robust z-score. Error rate có thể 0 phần lớn thời gian; dùng count model/minimum traffic, rolling upper quantile hoặc floor theo statistical uncertainty. Detector phải chọn theo semantics.

### 8.3 Một outlier có che anomaly sau không?

Median/MAD chịu được dưới khoảng 50% contamination về lý thuyết trung tâm, nhưng rolling window dài incident sẽ dần có đa số điểm xấu. Khi đó median chuyển lên 800 ms và detector tự nuốt sự cố. Robust statistic chỉ trì hoãn contamination; baseline freeze/quarantine ở phần sau mới bảo vệ lifecycle.

---

## 9. Cửa sổ 60 phút chạy mỗi 45 giây: chính xác chuyện gì xảy ra?

Cấu hình:

```text
evaluation_interval = 45 seconds
lookback_window = 60 minutes
raw_scrape_interval = 15 seconds
```

Timeline half-open để tránh đếm trùng boundary:

```text
10:00:00 evaluate samples in (09:00:00, 10:00:00]
10:00:45 evaluate samples in (09:00:45, 10:00:45]
10:01:30 evaluate samples in (09:01:30, 10:01:30]
```

Nếu raw point đúng mỗi 15 giây, lần 10:00 giữ khoảng 240 points. Sang 10:00:45, ba điểm 09:00:15, 09:00:30, 09:00:45 rời cửa sổ theo boundary đã chọn và ba điểm 10:00:15, 10:00:30, 10:00:45 được thêm; điểm 09:00:00 vốn không nằm trong interval half-open. Implementation phải thống nhất boundary với query engine; khác một dấu `<=` gây double count khó thấy.

Nếu feature là bucket 1 phút, không nên giả mỗi 45 giây có đúng một bucket mới. Evaluation 10:00:45 có bucket 10:00–10:01 đang partial; policy có thể chỉ dùng last closed bucket 09:59–10:00 làm `current`, hoặc dùng streaming partial nhưng so với partial baseline tương ứng. Thiết kế trong chapter chọn feature bucket 45 giây cho fast detector và bucket 1 phút cho SLO/baseline ổn định.

### 9.1 Baseline cũ và baseline mới

Một bảng nhỏ dùng cửa sổ đồ chơi 5 điểm để nhìn cơ chế:

| Evaluation | Window accepted | Điểm rời | Điểm thêm | Median | MAD | Current score với scale floor 2 ms |
|---|---|---:|---:|---:|---:|---:|
| 10:00:00 | 98, 99, 100, 101, 102 | — | 102 | 100 | 1 | 1,0 |
| 10:00:45 | 99, 100, 101, 102, 180 | 98 | 180 | 101 | 1 | 39,5 |
| 10:01:30 | 100, 101, 102, 180, 210 | 99 | 210 | 102 | 2 | 36,4 |
| 10:02:15 | 101, 102, 180, 210, 250 | 100 | 250 | 180 | 78 | 0,61 |

Ở dòng cuối, median đã thành 180 và MAD thành 78; score của 250 tụt xuống `70/(1,4826×78)=0,61`. Đây chính là contamination: ba trên năm điểm là incident. Trong cửa sổ 60 phút thật, quá trình chậm hơn nhưng vẫn xảy ra. Implementation/report phải gọi cùng một hàm scorer thay vì copy phép tính tay sang nhiều nơi.

### 9.2 Recompute toàn bộ hay incremental?

Với mean/variance, thêm/bớt có công thức incremental. Với exact median/MAD, remove một điểm và add một điểm cần ordered multiset; MAD còn phụ thuộc median mới nên khó hơn. Ba lựa chọn:

- recompute/sort toàn bộ: đơn giản, đúng, phù hợp số key nhỏ;
- balanced tree/two heaps + rebuild deviations: nhanh hơn nhưng code/state phức tạp;
- quantile sketch như t-digest/KLL: scale lớn, xấp xỉ và merge được, nhưng remove sliding point khó; thường dùng time-bucket sketches rồi merge các bucket còn sống.

Production thực dụng chia 60 phút thành 60 bucket một phút, giữ raw/compact values theo key, merge/recompute mỗi 45 giây. Với 10.000 key × 60 points, exact median vẫn khả thi nếu shard đúng; với millions high-cardinality series, dùng sketches và chỉ detector ở service/route level.

### 9.3 Snapshot consistency

Baseline version tại evaluation phải immutable trong decision. `current`, median, MAD và sample membership cùng watermark. Không query current lúc 10:00:45 rồi median từ store đã nhận thêm point 10:01:02. Anomaly event lưu `baseline_snapshot_id` để replay.

### 9.4 Window overlap không phải năm evidence độc lập

Các evaluation cách 45 giây nhưng lookback 60 phút chồng 98,75% dữ liệu. Rule 3/5 không có nghĩa năm mẫu thống kê độc lập; nó chỉ là persistence theo thời gian. Calibration phải replay đúng overlap, không dùng giả định binomial độc lập.

---

## 10. Window size: nhanh, ổn định và theo mùa

| Window | Điều nhìn tốt | Giá phải trả | Vai trò đề xuất |
|---|---|---|---|
| 5 phút | step/spike mới, lead time thấp | noisy, ít mẫu | fast residual + persistence |
| 15 phút | queue/slope, short burn | còn nhạy route mix | confirmation |
| 60 phút | robust local normal | incident dài contamination, không hiểu ngày | median/MAD active baseline |
| 24 giờ | daily range/trend | chậm, deploy/regime mixed | drift context |
| 7 ngày+ | weekday seasonality | cần history, holiday sai | seasonal reference |

Một cửa sổ không thể vừa phản ứng nhanh vừa ổn định. Thiết kế đề xuất giữ ba clock:

```text
fast detector:       residual/persistence 5m
local baseline:      accepted median/MAD 60m
seasonal reference:  same slot over 4–8 weeks
```

Fast path phát hiện; local baseline đo deviation gần; seasonal path hỏi tải này có bình thường theo lịch không. Nếu fast/local nói bất thường nhưng seasonal nói traffic đúng campaign và customer SLI khỏe, alert hạ severity. Nếu SLO burn cao, seasonal traffic hợp lệ không suppress symptom.

Gradual degradation 100→110→...→300 có thể bị rolling baseline đuổi theo. Thêm slope/CUSUM/change detector trên residual so với slow/seasonal baseline. CUSUM trực giác là cộng dồn các lệch nhỏ cùng hướng; mỗi điểm chưa đủ lớn nhưng tổng “nợ lệch” vượt ngưỡng. Nó tăng recall cho slow burn, đổi lại cần reset và tuning để không báo trend legitimate.

---

## 11. Anomaly scoring theo semantics của từng signal

Điểm anomaly cần trả lời “giá trị hiện tại lệch bao nhiêu đơn vị dao động bình thường?”, nhưng không phải mọi feature có cùng phân phối. Core vẫn là univariate per-key; scorer được chọn theo signal type.

### 11.1 Latency

Latency lệch phải và có tail. Hai cách dễ vận hành:

```text
score = (log1p(current_p95) - median(log1p(history_p95))) / robust_scale
```

hoặc score trực tiếp p95 với rolling median/MAD và scale floor. Log transform làm tăng từ 100→200 và 1.000→2.000 có residual gần cùng tỷ lệ, phù hợp trực giác “gấp đôi”. Luôn giữ request count/histogram quality. p99 trên 20 requests không ổn định bằng p95 trên 20.000 requests.

Latency score upper-only:

```text
latency_score = max(0, (x - center) / effective_scale)
```

Latency giảm có thể là tốt, hoặc traffic bị mất. Traffic/throughput detector sẽ xử lý vế sau.

### 11.2 Error rate

Tỷ lệ 5% trên 20 requests và 5% trên 200.000 requests không có cùng bằng chứng. Minimum traffic gate là bước đầu:

```text
if requests < 100 in evaluation window:
    state = LOW_TRAFFIC
    do not page from rate alone
```

Tốt hơn, dùng Wilson/Beta-binomial interval để biểu diễn uncertainty. Trực giác: số mẫu ít tạo interval rộng, nên cần tỷ lệ cực đoan/kéo dài hơn. Core MVP có thể dùng count + rate:

```text
bad_excess = max(0, observed_error_rate - baseline_error_rate)
score_rate = bad_excess / max(robust_scale, rate_floor)
score_count = log1p(error_count)
```

Qualifier yêu cầu cả score_rate và volume/SLI impact, tránh `1/1=100%` page P1.

### 11.3 Saturation

CPU utilization 95% không mặc định xấu. Scorer đo deviation, nhưng severity cần symptom:

```text
saturation_evidence = robust_score(cpu_throttle_or_pool_util)
```

Pool utilization từ 65% lên 100%, pool wait và timeout cùng tăng là mạnh. CPU 95% nhưng latency/error/SLO khỏe có thể là hệ tận dụng tài nguyên tốt; chỉ warning/capacity signal. Với Kubernetes, CPU throttling time thường causal hơn raw CPU vì limit có thể chặn workload.

### 11.4 Queue

Queue có ba univariate detector độc lập:

- level `depth` lệch khỏi baseline;
- `oldest_message_age` phản ánh customer wait;
- slope hoặc imbalance `arrival_rate - service_rate` dự đoán backlog.

Nếu depth cao nhưng slope âm và oldest age giảm, queue đang drain; severity hạ. Nếu depth vừa phải nhưng slope dương liên tục và time-to-exhaustion ngắn, alert sớm.

### 11.5 Cost/resource consumption

Cost detector không page từ invoice tăng đơn thuần:

```text
cost_per_success = estimated_cost / successful_business_transactions
resource_per_request = cpu_seconds / completed_requests
```

Baseline theo service và traffic band. Cost/request tăng 80%, retry tăng và success giảm là incident efficiency. Price change của cloud provider là metadata/change event; nếu toàn fleet cost tăng cùng hệ số mà usage không đổi, RCA nên rank billing/config, không mọi service.

### 11.6 Score normalization và clipping

Raw robust score có thể 100 như ví dụ MAD nhỏ. Multi-signal aggregation không nên để một score 100 nuốt mọi evidence. Chuẩn hóa:

```text
normalized_score = min(raw_score / 8.0, 1.0)
```

hoặc sigmoid có calibration. Giữ cả raw và normalized. Raw giải thích mức lệch; normalized dùng weighted combination. Score không phải probability nếu chưa calibration trên labels. Không gọi `0,86` là 86% xác suất chỉ vì chia score cho tổng.

---

## 12. Detector state machine: anomaly kéo dài không được chớp tắt

```text
           score/persistence đủ
 NORMAL ─────────────────────────> SUSPECT
    ^                                  │
    │ false/noise                      │ 3/5 + impact/gate
    └──────────────────────────────────┤
                                       v
                                    FIRING
                                       │
                         score dưới recovery threshold
                                       v
                                  RECOVERING
                                  │         │
                       xấu lại ───┘         └── khỏe N lần ──> NORMAL
```

| State | Ý nghĩa | Baseline update | Notification |
|---|---|---|---|
| `WARMING` | chưa đủ history | nhận sample quality tốt | không page behavioral anomaly |
| `NORMAL` | trong expectation | update accepted | không |
| `SUSPECT` | lệch mới, chưa đủ persistence | quarantine điểm nghi ngờ | event nội bộ |
| `FIRING` | alert đã qualify | freeze/quarantine | page một transition, update có rate limit |
| `RECOVERING` | metric hạ nhưng chưa ổn | vẫn freeze | không resolve vội |
| `DATA_INSUFFICIENT` | thiếu/stale input | không update | data-quality alert; incident cũ vẫn active |

Cấu hình minh họa:

```text
NORMAL → SUSPECT:     score >= 3.5 trong 2 evaluation liên tiếp
SUSPECT → FIRING:     score >= 4.0 ở 3/5 evaluations
                     và traffic/impact gate hợp lệ
SUSPECT → NORMAL:     score < 2.5 ở 3 evaluations, chưa từng fire
FIRING → RECOVERING:  score < 2.0 và SLI/burn cải thiện
RECOVERING → NORMAL:  khỏe 7/8 evaluations và ít nhất 5 phút
RECOVERING → FIRING:  score >= 3.0 hoặc burn xấu lại
```

### 12.1 Persistence

`3/5` chịu một điểm missing/noise và không cần ba điểm liên tiếp. Với interval 45 giây, sớm nhất ba evaluation mất khoảng 90 giây từ evaluation đầu; cộng alignment/ingestion lag thành detection lead time. Critical SLO burn có fast path `2/2` để không chờ quá lâu. Persistence là product trade-off giữa recall deadline và precision-at-page.

### 12.2 Hysteresis

Fire threshold 4 và recover threshold 2 tạo vùng đệm. Nếu dùng cùng threshold 4, score 3,9/4,1 khiến `FIRING↔NORMAL` mỗi 45 giây. Hysteresis không tự đủ; recovery còn cần duration và customer SLI.

### 12.3 State transition, không phải alert lặp

Khi đã `FIRING`, evaluation tiếp theo phát `FIRING_UPDATE` cùng `alert_id`, không tạo alert mới. Notification router gửi opening page một lần, periodic summary theo policy, severity escalation nếu impact tăng, và resolved khi recovery confirmed. Cooldown không được làm “khoảng câm”: nó chặn notification trùng, không ngừng detector evaluate hay audit update.

### 12.4 Missing khi đang firing

Nếu telemetry mất, state chuyển quality `UNKNOWN` nhưng incident không resolve. Có thể giữ `FIRING_DEGRADED` trong TTL và page observability pipeline. Sau TTL, human escalation nói rõ “impact chưa xác định”; không phát `RECOVERED` từ absence.

---

## 13. Pseudocode detector loop production-grade

```python
def evaluate_key(key, now):
    lease = state_store.lock(key, ttl="30s")
    if not lease:
        return  # một owner evaluate key tại một thời điểm

    state = state_store.load_or_rebuild(key)
    snapshot = feature_store.window(
        key=key,
        start=now - minutes(60),
        end=now,
        event_time=True,
        watermark=seconds(90),
    )

    quality = assess_quality(snapshot)
    if quality.is_stale or quality.coverage < key.min_coverage:
        state.mark_data_insufficient(now, quality)
        # Không reset FIRING; missing không phải recovery.
        emit_transition_if_changed(state)
        checkpoint(state)
        return

    current = latest_closed_feature(snapshot)
    if current.denominator is not None and current.denominator < key.min_traffic:
        state.mark_low_traffic(now)
        # Có thể dùng count/invariant detector riêng, không page rate.
        checkpoint(state)
        return

    baseline = baseline_store.snapshot(key, at=now)
    if baseline.accepted_count < key.min_baseline_samples:
        state.transition("WARMING")
        maybe_add_accepted_sample(current, context="warmup")
        checkpoint(state)
        return

    raw_score = score_by_signal_semantics(current, baseline)
    slo = slo_store.current(key.service, now)
    context = load_context(key, now)  # traffic, deploy, maintenance
    state.observe(raw_score, slo, context, now)

    if state.phase in {"SUSPECT", "FIRING", "RECOVERING"}:
        baseline_store.quarantine(key, current, reason=state.phase)
    else:
        baseline_store.accept(key, current)

    if state.phase == "FIRING":
        baseline_store.freeze(key, incident_id=state.incident_id)

    event = build_anomaly_event(
        key, current, baseline, raw_score, state, quality, context
    )
    outbox.publish_idempotent(event.id, event)
    checkpoint_transactionally(state, event.offset, baseline.version)
```

Scheduler gọi các shard mỗi 45 giây, nhưng process là long-running controller. `load_or_rebuild` đọc persisted state; nếu checkpoint hỏng, nó replay anomaly events và telemetry trong bounded history. Outbox/offset transaction ngăn state đã chuyển nhưng event chưa publish, hoặc publish hai lần sau crash.

### 13.1 Observability của detector

Theo dõi:

- evaluation lag p95/p99 và keys skipped;
- baseline age/frozen duration/quarantine ratio;
- state transition rate và flapping;
- data-insufficient keys, MAD-zero/floor usage;
- anomaly event publish failure/duplicate;
- score distribution theo service tier;
- time từ event-time tới `SUSPECT`, `FIRING`, page.

Alert của detector platform không được phụ thuộc duy nhất vào chính detector đang hỏng; dùng static watchdog/blackbox path độc lập.

---

## 14. Chống anomaly tự nuốt chính nó

Incident ví dụ:

```text
10:00 latency 100 ms
10:05 latency 800 ms
10:10 latency 850 ms
10:20 latency 830 ms
10:40 latency 840 ms
```

Nếu mọi point vào rolling 60m baseline, sau khoảng nửa cửa sổ median dịch lên vùng incident; MAD có thể co quanh 830; score giảm dù người dùng vẫn lỗi. Hệ phải tách **detection window** khỏi **learning eligibility**.

### 14.1 Freeze hoàn toàn

```text
if state in {FIRING, RECOVERING}:
    do_not_update_active_baseline()
```

Ưu: đơn giản, đảm bảo incident không thành normal. Nhược: incident kéo dài nhiều giờ làm baseline stale; traffic seasonal hợp lệ vẫn đổi. Sau recovery, so với baseline cũ có thể tạo false alert.

### 14.2 Quarantine anomalous samples

Mọi point suspect/firing vào quarantine; active baseline vẫn có thể nhận signal/context được chứng minh khỏe. Ví dụ traffic tăng theo campaign nhưng latency incident: traffic baseline có thể tiếp tục học nếu customer traffic quality tốt, còn payment latency/error baseline freeze. Ưu: ít stale hơn. Nhược: quyết định sample sạch phức tạp; false positive lâu có thể chặn legitimate drift.

### 14.3 Freeze theo key, không theo incident toàn cục

`payment:p95_latency` firing không đóng baseline `inventory:error_rate`. Ngay trong payment, cost baseline có thể có policy khác. Freeze scope quá rộng là nguyên nhân masking fault thứ hai và drift giả.

### 14.4 Recovery và unfreeze an toàn

1. `FIRING→RECOVERING` khi score dưới 2, SLI và burn rate cải thiện.
2. Giữ baseline frozen trong recovery confirmation 5 phút.
3. Các point khỏe vào `candidate-recovery`, chưa trộn ngay.
4. Khi `NORMAL`, unfreeze với learning rate chậm hoặc weight cap, ví dụ tối đa 10% samples mới mỗi cycle.
5. Nếu baseline freeze quá `max_freeze=6h`, không tự học incident; chuyển `STALE_FROZEN`, dùng seasonal/last-known-good và require review/change-point evidence.

### 14.5 Trade-off không thể xóa

Freeze giảm false recovery nhưng tăng stale baseline. Quarantine giảm contamination nhưng selection bias: chỉ học điểm detector thích. Vì vậy theo dõi freeze duration, candidate-vs-active distribution và chạy shadow baseline luôn nhận data để **quan sát** regime mới, nhưng shadow baseline không được tự resolve alert. Change-point trên shadow có thể đề nghị rebase; policy/human hoặc healthy outcome confirmation mới promote.

---

## 15. Data drift, seasonality và baseline adaptation

### 15.1 Legitimate drift và incident contamination

| Dấu hiệu | Legitimate drift | Incident contamination |
|---|---|---|
| Customer SLI | khỏe | xấu/burn tăng |
| Nhiều signal | traffic/capacity cùng đổi hợp lý | latency/error/queue propagation |
| Change context | campaign, capacity, accepted deploy | change đáng ngờ hoặc không có |
| Topology/cohort | rộng, dự kiến | causal path/cohort cụ thể |
| Duration | regime ổn định sau transition | kéo dài tới mitigation |
| Control | canary/control cũng khỏe | affected cohort khác control |

Không có rule tuyệt đối. Deploy có thể legitimate shift từ 100→120 ms nhưng vẫn trong SLO; cũng có thể là regression. Change event là context, không auto-whitelist.

### 15.2 Dual baseline

```text
short-term candidate:  60m, thích nghi nhanh, không có quyền resolve
long-term reference:   4–8 tuần theo seasonal slot, thích nghi chậm
```

Nếu short lệch long nhưng customer outcome khỏe, change-point ổn định 30–60 phút và control cohorts tương tự, hệ đề nghị legitimate rebase. Nếu outcome xấu, freeze long baseline. Dual baseline làm lộ disagreement thay vì cho một model tự quyết định.

### 15.3 Deployment-aware transition

Không reset baseline về rỗng ngay sau deploy. Chạy version-aware shadow:

- version cũ giữ last-known-good;
- version mới nhận canary data với `WARMING`;
- so canary với control và SLO;
- nếu rollout khỏe, promote baseline mới dần;
- nếu rollback, loại candidate samples version lỗi khỏi active history.

Nếu kiến trúc thay đổi semantics metric, bắt buộc baseline version mới. Nếu chỉ latency tăng nhẹ vì code path đổi, change-point + healthy outcome cho phép rebase.

### 15.4 Slow adaptation

EWMA baseline chỉ update accepted point và cap step:

```text
delta = clip(x - baseline, -max_step, +max_step)
baseline_next = baseline + alpha_slow * delta
```

Cap ngăn một điểm kéo center. Nhưng degradation tăng 1 ms/phút vẫn có thể bị hấp thụ. Detector slope/CUSUM so với long-term/seasonal reference là guard bổ sung.

### 15.5 Warm-up

Service mới không có lịch sử. Trong 30–60 phút đầu:

- giữ static safety/SLO rules;
- dùng hierarchical prior từ service class/template với confidence thấp;
- không auto-remediate từ behavioral anomaly đơn lẻ;
- collect accepted samples theo traffic bands;
- chuyển `WARMING→NORMAL` khi đủ count, coverage và thời span, không chỉ đủ 60 points trong 60 giây.

---

## 16. Multi-signal detection: bonus có explainability

Sàn là mỗi `(service, signal)` có detector/state độc lập. Sau đó service evidence composer gom normalized scores:

```text
service_score =
    0.30 × latency_score
  + 0.30 × error_score
  + 0.15 × saturation_score
  + 0.15 × queue_score
  + 0.10 × cost_efficiency_score
  + interaction_bonus
```

Không cộng mù. `interaction_bonus` biểu diễn pattern có ý nghĩa:

```text
latency + error + queue          → +0.15
pool saturation + pool wait     → +0.15
high CPU alone, SLI healthy     → severity cap WARNING
cost high because traffic high  → no bonus after normalization
```

### 16.1 Voting và logical rules

Production-friendly nhất là voting:

```text
FIRE service evidence nếu:
  (latency AND error) OR
  (queue_age AND timeout) OR
  (SLO fast burn) OR
  (một invariant critical)
```

Output liệt kê signal nào vote, signal nào phản bác. Đây thường tốt hơn autoencoder khó giải thích cho MVP.

### 16.2 Correlation và covariance

CPU và RPS thường tăng cùng nhau. CPU 80% tại RPS cao có thể normal; CPU 80% tại RPS thấp mới lạ. Một multivariate baseline có thể học vector `[RPS, CPU, latency, error]` và covariance. Mahalanobis distance:

```text
D² = (x - μ)ᵀ Σ⁻¹ (x - μ)
```

Trực giác: không chỉ đo từng feature cách center bao xa, mà đo hướng kết hợp đó có thường xuất hiện không. Input là vector đã scale, output là distance. Failure modes: covariance singular khi features trùng/ít data; outlier làm μ/Σ bẩn; drift; khó giải thích; missing feature. Cần robust covariance/regularization và lưu feature contribution.

### 16.3 Isolation Forest/Autoencoder

Isolation Forest tách điểm hiếm bằng cây ngẫu nhiên; điểm cần ít nhát cắt thường lạ. Autoencoder học tái tạo pattern normal; reconstruction error cao là anomaly. Chúng bắt interaction phi tuyến nhưng cần training data sạch, drift monitoring, calibration per cohort và explainability phụ. Chỉ deploy khi replay chứng minh simple ensemble bỏ lỡ failure class quan trọng. Không nâng quyền auto-action chỉ vì model phức tạp hơn.

---

## 17. Alert qualification: anomaly chưa đáng đánh thức người

Qualification nhận anomaly events, traffic, SLO, service tier và incident context. Nó áp dụng các “van”:

### 17.1 Persistence và debounce

Một spike score 16 rồi bình thường không page nếu không vi phạm invariant/SLO tức thời. `3/5` hoặc duration 2 phút debounce noise. Với money correctness hoặc ready replicas=0, static critical rule có thể bypass persistence vì cost chờ cao hơn false positive.

### 17.2 Hysteresis và cooldown

Hysteresis giữ lifecycle ổn định. Cooldown ví dụ 10 phút chặn gửi lại cùng notification, nhưng update incident timeline vẫn liên tục. Severity tăng WARNING→CRITICAL được phép bypass cooldown vì thông tin mới có ý nghĩa.

### 17.3 Deduplication

```text
alert_key = environment + service + route/cohort + signal + anomaly_type
```

Same key phát revision, không alert mới. Pod identity thường không nằm trong page key để rolling restart không tạo 30 alerts; pod list nằm trong evidence. Dedup TTL không được ngắn hơn incident dài.

### 17.4 Minimum traffic và uncertainty

Rate detector không page 1 request lỗi. Nhưng sparse critical workflow có thể dùng synthetic probe, count-over-long-window hoặc “expected event absent” rule. Minimum traffic gate không đồng nghĩa bỏ quan sát service ít traffic.

### 17.5 Severity theo impact

Một hàm policy dễ audit:

```text
severity = f(
  user_visible_SLI,
  error_budget_burn,
  affected_requests_or_revenue,
  service_criticality,
  blast_radius,
  anomaly_confidence,
  data_quality
)
```

| Tình huống | Severity gợi ý | Lý do |
|---|---|---|
| CPU 100%, latency/error/SLO khỏe | WARNING/ticket | capacity risk, chưa có impact |
| p99 tăng, 1 spike, burn bình thường | observe | chưa persistence |
| error + latency + 14x burn trên checkout | CRITICAL/page | user-visible và budget tiêu nhanh |
| anomaly mạnh nhưng 50% telemetry mất | UNKNOWN/escalate data | confidence bị cap |
| cost/request tăng 3x, SLI khỏe | WARNING/FinOps | economic impact, không page P1 mặc định |

Alert policy phải ưu tiên symptom user-visible; resource signal chủ yếu hỗ trợ diagnosis. Nếu chỉ page nguyên nhân nội bộ, một failure kiểu traffic biến mất có thể làm CPU đẹp trong lúc người dùng không checkout được.

---

## 18. Error-budget burn rate và multi-window alert

SLO 99,9% cho phép bad-event rate 0,1% = 0,001. Nếu quan sát error 1%=0,01:

```text
burn_rate = observed_bad_rate / allowed_bad_rate
          = 0.01 / 0.001
          = 10x
```

Burn 10x nghĩa nếu tốc độ đó kéo dài, budget bị tiêu nhanh gấp 10 lần tốc độ “đều” cho cả objective period. Burn rate không phải anomaly baseline; nó là impact budget có semantics SLO và thường dùng static ratio đúng chỗ.

### 18.1 Vì sao hai cửa sổ?

```text
fast page:   5m burn > 14.4x AND 1h burn > 14.4x
slow page:  30m burn > 6x    AND 6h burn > 6x
```

Các threshold chỉ là ví dụ phải chọn theo SLO/budget policy. Short window bắt nhanh nhưng một spike có thể làm rate cao. Long window xác nhận budget thực sự đang cháy. Dùng `AND` tránh page spike ngắn; các cặp fast/slow bắt outage lớn và slow burn.

Ví dụ 5 phút vừa qua error 2% nhưng 1 giờ chỉ 0,08%: fast burn 20x, long burn 0,8x; chưa page fast multi-window, trừ invariant critical. Nếu error 2% kéo dài đủ để 1h rate lên 1,5%, hai cửa sổ đều vượt và page.

### 18.2 Burn rate và anomaly score bổ sung nhau

- Anomaly score nói “lạ so với chính service”.
- Burn rate nói “nguy hiểm với lời hứa khách hàng”.

Service baseline error 5% trên best-effort route có anomaly thấp nhưng SLO có thể vốn sai; governance cần sửa SLO/service. Service baseline 0,001% tăng lên 0,05% có robust anomaly rất cao nhưng vẫn trong SLO 99,9%; có thể warning sớm. Severity ghép cả hai.

### 18.3 Denominator và low traffic

Burn rate ở traffic thấp cũng bất định. Dùng bad-event count gate hoặc longer window. Với availability SLO theo request, no traffic không phải 100% success; nó là no observation. Synthetic/expected throughput SLI xử lý outage làm mất toàn request.

---

## 19. Incident dài, masking và fault nổ chồng

### 19.1 Giữ detection liên tục

Khi alert `FIRING`, detector vẫn chạy mỗi 45 giây, emit score/SLI/quality revision và giữ baseline frozen. Notification không lặp nhưng incident timeline không có khoảng câm. `last_evaluated_at` và `last_bad_evidence_at` được audit; watchdog page nếu active detector không evaluate quá SLO.

Recovery cần metric cause **và** customer outcome. Payment latency về baseline nhưng checkout success chưa hồi có thể còn queue/retry cascade; incident ở `RECOVERING`, chưa resolve.

### 19.2 Per-service/per-signal isolation

State keys độc lập:

```text
payment:p95_latency = FIRING
payment:pool_wait   = FIRING
inventory:error    = NORMAL
inventory:latency  = NORMAL
```

Mười lăm phút sau, inventory dependency timeout:

```text
inventory:error    = SUSPECT → FIRING
```

Không có global `incident_active => stop_detection`. Baseline payment freeze không ảnh hưởng inventory. Correlation chỉ chạy **sau** detection; nó có quyền liên kết, không có quyền disable detector.

### 19.3 Masking trong aggregation

Global checkout error 8% có thể che region nhỏ tăng 0→20% hoặc ngược lại. Theo dõi critical slices và cohort contribution. Một anomaly cực lớn ở payment không được max-normalize mọi service theo incident; normalized score là per-key calibrated. Incident view có top-k, không dùng một global scale dựa trên max hiện tại.

### 19.4 Fault partition, không merge mù

Incident A payment và Incident B inventory chỉ merge nếu có evidence:

- temporal proximity hợp lý;
- dependency path/trace propagation;
- cùng affected request cohort;
- shared dependency/change;
- một candidate giải thích được cả hai.

Nếu payment fault bắt đầu 10:03, inventory 10:18, trace checkout requests tới inventory lỗi độc lập và không có path payment→inventory, correlator tạo `INC-B` hoặc `related_concurrent`, không nhập tất cả vào `INC-A` chỉ vì cùng checkout.

---

## 20. Incident correlation: từ nhiều alert thành đúng số incident

Input là alert transitions, không phải raw anomaly. Correlator duy trì graph tạm thời giữa alerts. Edge weight có thể là:

```text
correlation_weight =
    0.25 × time_proximity
  + 0.30 × topology_path
  + 0.25 × trace_cohort_overlap
  + 0.10 × shared_change
  + 0.10 × symptom_similarity
```

Weight là heuristic cần benchmark, không phải causal probability. Cluster phải có merge/split threshold và evidence.

### 20.1 Payment cascade

Alerts:

```text
10:05:15 payment latency/pool/queue
10:05:30 checkout timeout
10:06:00 api-gateway 5xx
10:06:10 frontend checkout failure
```

Graph có path `frontend→api→checkout→payment→db`; traces cùng cohort `/checkout`; temporal propagation thuận hướng. Correlator tạo một incident:

```text
INC-102
members: payment, checkout, api, frontend alerts
affected journey: checkout
candidate origin region: payment/payment-db
```

Nó chưa tuyên root cause; đó là RCA.

### 20.2 False merge và false split

False merge nhập hai fault độc lập, khiến RCA/action sai. False split tạo nhiều incident/page cho cùng cascade. Correlator nên bảo thủ với action: nếu partition ambiguity cao, không auto-remediate cả cluster. Late trace có thể tạo incident revision/split; stable incident IDs và parent/child relation giữ audit.

### 20.3 Incident lifecycle

Incident mở khi ít nhất một qualified alert có impact hoặc nhiều alert tương quan. Nó cập nhật affected services/severity/evidence; chuyển recovering khi mọi user-impact alert recovering; resolve khi recovery confirmation hoàn tất. Resource warning còn lại có thể thành follow-up ticket, không giữ P1 vô hạn.

Incident key không chỉ là minute bucket. Dedup theo journey/environment/fault partition và active lifecycle; outage 60 phút vẫn là một incident. Nếu customer đã recover rồi fault tái phát sau recovery grace/cooldown, policy quyết định reopen hay new incident và ghi relation.

---

## 21. RCA: tìm candidate giải thích cascade, không đếm service đỏ

RCA nhận incident revision và trả:

```text
Which component/failure mode is most likely the origin?
What observed evidence supports it?
What contradicts it?
What data is missing?
What cheap, safe test could discriminate candidates?
```

Output đúng dạng:

```text
Probable root candidate: payment-db / connection capacity exhaustion
Calibrated confidence: 0.86
Evidence quality: 0.82
Alternative: payment retry amplification, 0.54
```

Không phải `Payment red, Checkout red, API red`. Càng gần người dùng, service càng dễ có symptom mạnh vì nó tổng hợp failure downstream. Root candidate là node giải thích được nhiều affected callers, xuất hiện theo thứ tự hợp lý, có mechanism tương thích và bản thân ít được một dependency đỏ khác giải thích.

### 21.1 Facts và inference

**Observed facts:**

- `payment-db.pool_utilization` 65%→100% lúc 10:03:15;
- `payment.p95` 120→980 ms lúc 10:03:45;
- checkout timeout tăng 55 giây sau;
- 74% sampled failed checkout traces có child span `payment/acquire_connection` timeout;
- không có anomaly ở external provider trước 10:03.

**Inference:**

- payment DB connection exhaustion có khả năng là origin của checkout degradation.

Summary/UI phải gắn nhãn `observed`, `inferred`, `missing`, `contradicting`. LLM có thể viết câu dễ đọc từ evidence ledger, nhưng không được sinh fact ngoài ledger.

### 21.2 Fast path và deep path

- Fast path trong vài giây: topology, temporal order, anomaly strength, trace edge/error, recent changes.
- Deep path trong 30–90 giây: log templates, cohort analysis, counterfactual/control, historical cases.

Mỗi lần evidence mới tới tạo `rca_revision`. Rank có thể đổi; audit ghi vì sao. Action envelope pin revision và expiry để không dùng root candidate cũ sau khi late traces đổi kết luận.

---

## 22. Dependency graph và downstream weighting

Biểu diễn topology `G=(V,E)`, trong đó node là service/component và cạnh caller→callee:

```text
Frontend → API → Checkout → Payment → Payment DB
                       └──→ Inventory
```

Trong causal language của chapter, “ảnh hưởng downstream tới người dùng” đi ngược cạnh call: DB fault ảnh hưởng Payment rồi Checkout/API/Frontend. Để tránh nhập nhằng, implementation dùng hai từ rõ:

- `dependencies(node)`: callees mà node gọi;
- `affected_callers(node)`: callers có đường gọi tới node và đỏ sau nó.

### 22.1 Sinh candidate

Candidate không chỉ là service có alert. Bao gồm:

- anomalous services/resources;
- dependency trực tiếp như DB/cache/provider;
- first-error span target;
- recent change trong blast radius;
- shared infrastructure AZ/node/DNS nếu giải thích nhiều branch.

Topology snapshot phải là tại event-time. Graph hiện tại sau rollback/scale có thể khác graph khi incident bắt đầu. Mỗi edge có source, observed time, call volume và confidence.

### 22.2 Duyệt vùng đỏ

Với mỗi symptom gần người dùng, traverse theo caller→callee. Node mạnh khi:

1. tự nó có anomaly nội tại như pool wait, not chỉ caller timeout;
2. affected callers đỏ sau node;
3. dependencies của node khỏe hoặc không giải thích được nó;
4. trace latency/error dừng hoặc phát sinh tại node/edge đó.

Trong scenario, `checkout` error mạnh nhưng có dependency `payment` đỏ trước và child span payment chiếm 79% latency; checkout bị `upstream_explanation` (theo nghĩa dependency/callee explanation) trừ điểm. Payment lại được payment DB saturation giải thích, nên nếu DB là node trong graph, DB rank cao hơn payment service.

### 22.3 Downstream impact không thiên vị hub

Đếm số affected callers thô làm shared hub luôn thắng. Dùng weighted reach:

```text
impact(candidate) = Σ affected_journey_weight × propagation_confidence / path_length_penalty
```

Critical checkout journey nặng hơn internal batch; edge có 2% call volume nhẹ hơn edge mang 90% requests. Candidate DNS toàn cluster có reach lớn nhưng nếu unaffected control services cùng DNS vẫn khỏe, counter-evidence giảm điểm.

### 22.4 Graph stale hoặc thiếu

Thiếu edge không có nghĩa không dependency. RCA cap evidence quality/confidence, tìm trace edges động và có thể trả `uncertain`. Không auto-act high risk khi topology freshness quá SLO. Với missing graph, temporal/log/change vẫn cho shortlist nhưng không tuyên causal path chắc chắn.

---

## 23. Thứ tự thời gian: evidence cần thiết nhưng không đủ

“Cái đỏ đầu tiên là root” thất bại khi:

- detector service A nhạy hơn B;
- scrape interval khác nhau;
- clock skew/late telemetry;
- upstream victim có metric phản ứng trước resource cause;
- một noise spike vô can xuất hiện sớm.

Temporal feature dùng interval uncertainty:

```text
payment-db onset: [10:03:10, 10:03:20]
payment onset:    [10:03:40, 10:03:50]
checkout onset:   [10:04:35, 10:04:45]
```

Nếu intervals không overlap và thuận topology, precedence mạnh. Nếu overlap do ±60 giây skew, feature gần trung tính. Trace parent-child ordering đáng tin hơn host wall clock nếu span timestamps được hiệu chỉnh, nhưng instrumentation lỗi vẫn cần quality flag.

Một temporal score đơn giản:

```text
precedence(c) = weighted_fraction_of_affected_callers_starting_after(c)
```

Không cho bonus chỉ vì sớm hơn một service không có path. Recommendation CPU tăng 10:01 không liên quan Payment 10:03 nếu không có topology/trace/shared resource hợp lý.

### 23.1 Change events

Deploy 2 phút trước incident là evidence proximity, không là guilt. Kiểm tra scope: version mới có ở affected pods/cohort không? Canary mới lỗi, control cũ khỏe không? Error class có semantic match không? Nếu deploy recommendation cùng lúc nhưng payment không phụ thuộc recommendation, correlation penalty lớn.

---

## 24. Trace span propagation: evidence gần causal mechanism hơn correlation metric

Một trace:

```text
Checkout span 1.20 s ERROR
└── Payment child span 1.10 s ERROR timeout
    └── acquire_connection 0.94 s ERROR pool_timeout
```

Payment child chiếm 91,7% checkout duration. Trên hàng nghìn trace, ta tính:

```text
propagation_ratio =
  failed_or_slow_parent_traces_with_slow_child(edge)
  / failed_or_slow_parent_traces_with_edge_observed
```

Nếu 74% failed checkout traces có payment timeout nhưng chỉ 2% healthy checkout traces có pattern đó, edge evidence mạnh hơn hai metric đơn thuần cùng tăng.

### 24.1 First-error và critical path

First-error span là span sớm nhất phát failure status theo trace path, không phải timestamp global đầu tiên. Critical-path contribution đo thời gian child thực sự chặn parent; tổng child duration mù có thể double-count spans song song. RCA ưu tiên synchronous blocking dependency hơn fire-and-forget span.

### 24.2 Retry amplification

Checkout có thể gọi payment ba lần. Trace cho thấy original payment timeout, sau đó retries tăng load/pool exhaustion. Root mechanism có thể là DB capacity + retry amplification; không đơn giản “payment error”. RCA giữ candidate component và failure mode riêng.

### 24.3 Missing/sampled traces

Nếu trace coverage 8%, output nói `trace evidence based on 412/5.150 failed requests, tail-sampled`. Không có trace không phải evidence service vô tội. RCA chuyển weight sang topology/metrics/logs và cap confidence. Nếu instrumentation payment mất đúng lúc incident, absence còn có thể là telemetry anomaly.

---

## 25. Không nhầm correlation thành causality

RCA dùng năm bộ lọc:

1. **Dependency path:** có đường kỹ thuật hợp lý từ candidate tới symptom?
2. **Direction/time:** candidate/change có trước propagation trong uncertainty không?
3. **Mechanism semantics:** CPU recommendation có thể gây payment error qua shared node không, hay chỉ cùng traffic?
4. **Control/cohort:** service/region cùng exposure nhưng không lỗi có phản bác không?
5. **Intervention/recovery:** khi candidate được giảm tải/rollback, symptom có cải thiện với độ trễ hợp lý không?

Ví dụ campaign tăng traffic cùng lúc làm CPU `recommendation` và Payment error tăng. Recommendation không nằm trên checkout payment path; các request không gọi recommendation vẫn payment lỗi; tắt recommendation không đổi payment SLI. Đây là correlation tình cờ/confounder load, không causation.

### 25.1 Counter-evidence là first-class

Mỗi candidate có supporting và contradicting evidence. Ví dụ payment DB candidate bị phản bác nếu pool saturation chỉ xuất hiện **sau** retries, database control queries vẫn nhanh và external provider spans đã lỗi trước. Confidence không chỉ cộng tín hiệu đỏ; nó phải giảm khi facts không khớp.

### 25.2 Intervention evidence không tuyệt đối

Scale payment xong latency giảm không chắc scale chữa root: traffic có thể tự giảm cùng lúc. So pre/post với control, traffic normalization và expected lag. Một action làm outcome đổi đúng direction, đúng scope và mechanism signal cải thiện là evidence mạnh, nhưng vẫn ghi inference.

### 25.3 Causal graph và model phức tạp

Causal/Bayesian/GNN có thể hỗ trợ khi topology lớn, nhưng không thay data contracts. Causal discovery từ observational telemetry dễ dính common-cause traffic và sampling. Dùng model để đề xuất/rank, giữ hard topology/semantic constraints, calibration và abstention. Không cho neural score không giải thích trực tiếp mở quyền production.

---

## 26. RCA scoring có thể audit

Một score production-friendly:

```text
RCA_raw(c) =
    0.20 × anomaly_strength(c)
  + 0.15 × temporal_precedence(c)
  + 0.20 × affected_caller_impact(c)
  + 0.20 × trace_propagation(c)
  + 0.10 × topology_consistency(c)
  + 0.10 × change_or_mechanism_fit(c)
  + 0.05 × recovery_intervention(c)
  - 0.20 × dependency_explanation(c)
  - 0.15 × unrelated_correlation_penalty(c)
  - 0.10 × contradictory_evidence(c)
```

Features được normalize 0–1; weights là versioned configuration phải tune/calibrate trên replay. `dependency_explanation(c)` cao khi một callee/upstream resource khác đỏ trước và giải thích c. `unrelated_correlation_penalty` cao khi không path/cohort/mechanism.

### 26.1 Ví dụ điểm minh họa

| Candidate | Strength | Time | Impact | Trace | Topology | Bị dependency giải thích | Counter | Raw/rank minh họa |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| payment-db | 0,95 | 0,90 | 0,88 | 0,86 | 0,95 | 0,05 | 0,10 | 1 / 0,86 calibrated |
| payment | 0,92 | 0,78 | 0,85 | 0,82 | 0,90 | 0,72 | 0,15 | 2 / 0,58 |
| checkout | 0,90 | 0,42 | 0,65 | 0,18 | 0,85 | 0,92 | 0,20 | 3 / 0,31 |
| recommendation | 0,70 | 0,95 | 0,05 | 0,00 | 0,05 | 0,00 | 0,90 | loại / 0,06 |

`0,86 calibrated` chỉ hợp lệ nếu mapping raw→probability được fit và kiểm tra reliability diagram/Brier score trên labeled incidents tương tự. Nếu chưa calibration, gọi là `confidence score`, không gọi xác suất.

### 26.2 Pseudocode RCA

```python
def diagnose(incident, evidence_time):
    graph = topology.snapshot(at=incident.start_time)
    candidates = generate_candidates(
        anomalous_nodes=incident.nodes,
        dependencies=graph,
        first_error_spans=traces.first_errors(incident),
        recent_changes=changes.in_scope(incident),
    )

    ranked = []
    for c in candidates:
        positive = {
            "strength": anomaly_strength(c),
            "time": temporal_precedence(c, uncertainty=True),
            "impact": affected_caller_impact(c, graph),
            "trace": trace_propagation(c, coverage_adjusted=True),
            "topology": topology_consistency(c, graph),
            "mechanism": semantic_fit(c),
            "intervention": recovery_evidence(c),
        }
        negative = {
            "explained_by_dependency": dependency_explanation(c, graph),
            "unrelated": unrelated_correlation(c, graph),
            "contradictions": contradictory_evidence(c),
        }
        raw = versioned_weighted_score(positive, negative)
        quality = evidence_quality(c, graph, traces, clocks=True)
        confidence = calibrate_and_cap(raw, quality)
        ranked.append(hypothesis(c, confidence, positive, negative))

    ranked.sort(key=lambda h: h.confidence, reverse=True)
    if ranked[0].confidence < AUTO_DIAGNOSE_THRESHOLD:
        return abstain_with_discriminating_queries(ranked)
    return ranked[:3]
```

### 26.3 Ambiguity và multi-root

Nếu candidate A=0,56, B=0,48, system nói ambiguous và đề xuất query phân biệt. Nếu payment và inventory là fault độc lập, correlator/RCA tạo hai root partitions, không ép một node giải thích mọi thứ. Top-1 accuracy không đủ; đo top-k, false merge/split và calibration.

---

## 27. Fault chưa từng thấy: localization trước classification

Catalog rule hữu ích cho known fault:

```text
pool_wait + saturation + acquire_timeout → pool exhaustion runbook
bad deploy + canary/control divergence   → rollback candidate
queue slope + consumer saturation        → scale consumers candidate
```

Nhưng hệ không được phụ thuộc hoàn toàn vào class name. Với memory leak mới ở inventory:

1. per-signal detector thấy memory slope, GC pause và p99 lệch khỏi baseline;
2. impact qualifier thấy checkout latency trên cohort gọi inventory;
3. topology/trace đặt origin quanh inventory;
4. không dependency nào của inventory đỏ;
5. RCA output `inventory runtime/resource degradation`, confidence 0,71, failure class unknown;
6. decision engine không có allowlisted autonomous fix đủ chắc, nên recommend bounded canary restart hoặc escalate tùy policy.

Đây là khả năng generalize theo behavior và propagation, không “học tủ” fault label. Hệ có thể đúng component mà chưa đúng mechanism; audit phải phân biệt component top-1, failure-mode top-1 và safe-action eligibility.

---

## 28. Incident summary tự sinh nhưng không hallucinate

Summary generator chỉ đọc structured incident/evidence ledger. Template:

```text
Incident: INC-2026-102, revision 7
Started: 10:03:15 event-time
State: FIRING / CRITICAL

Observed customer impact:
- Checkout success 99.7% → 82.4% on prod/SEA.
- Fast/long SLO burn: 18.2x / 15.1x.

Observed affected components:
- Payment p95 121 ms → 982 ms; DB pool 65% → 100%.
- Checkout timeout rose 55 s later; API 5xx rose 31 s after that.

Inferred probable origin:
- payment-db connection capacity exhaustion.
- Confidence score 0.86; evidence quality 0.82.

Supporting evidence:
- 74% of sampled failed Checkout traces contain Payment acquire timeout.
- Payment/DB degraded before affected callers.

Contradicting/missing evidence:
- DB CPU is normal; trace coverage is 8% tail-sampled.

Proposed mitigation:
- Bound Payment concurrency; do not scale app upward until DB headroom is checked.
```

Summary gửi Slack/Teams/PagerDuty bằng idempotency key `incident_id + revision + transition`. Channel delivery result vào audit; gửi thất bại retry/backoff và fallback route. Tự sinh summary không đồng nghĩa tự act. Observed numbers link query/snapshot; inference luôn có confidence và alternatives.

---

## 29. Remediation decision engine: chọn hành động từ hypothesis và policy

Closed loop:

```text
Detect → Diagnose → Decide → Safety Check → Act → Verify
                                               │
                              success <────────┴────────> fail
                                 │                         │
                              resolve              rollback/escalate
```

Action catalog là versioned typed templates, không là shell tự do:

| Failure evidence | Candidate action | Preconditions | Không làm khi |
|---|---|---|---|
| CPU-bound + SLI bad + replicas scalable | scale replicas +1/+2 | downstream headroom, quota | DB/pool đã saturated |
| Consumer lag + consumers saturated | scale consumers | partition parallelism/headroom | poison message/callee bottleneck |
| New deploy + canary worse | rollback release | previous artifact healthy | schema migration irreversible |
| Một pod stuck, peers khỏe | restart one pod | PDB/ready capacity | singleton/state unsafe |
| Feature cohort errors | disable flag | kill switch/versioned flag | flag affects correctness transition |
| DB pool exhausted by retry | cap concurrency/retry, shed load | policy/runbook tested | money operation unsafe to drop |

Decision score xét:

```text
eligibility =
  root_confidence
  × evidence_quality
  × action_match_confidence
  × reversibility
```

Nhưng hard gates không được bù bằng score. Scope unauthorized, stale topology, audit unavailable cho high-risk action hoặc budget attempts hết là deny dù eligibility 0,99.

### 29.1 Action không xuất phát từ anomaly đơn

`CPU high → restart` là anti-pattern. CPU có thể cao vì traffic tốt; restart giảm capacity. Action cần probable mechanism, user impact, expected causal effect và verification plan. Nếu RCA chỉ biết “payment resource issue” nhưng DB headroom chưa biết, decision có thể chọn read-only query hoặc load shedding bảo thủ thay vì scale.

### 29.2 Action envelope

```json
{
  "action_id": "act/INC-102/attempt-1",
  "incident_revision": 7,
  "catalog_id": "payment.limit-concurrency.v3",
  "target": {"cluster":"prod-sea","namespace":"shop","service":"payment"},
  "desired_change": {"max_inflight":{"from":200,"to":160}},
  "preconditions": ["db_headroom<5%", "checkout_burn>10x"],
  "blast_radius": {"traffic_percent":10,"duration":"5m"},
  "verification_plan":"verify/payment-pool-and-checkout-sli/v4",
  "rollback_plan":"restore max_inflight=200",
  "expires_at":"2026-08-10T10:12:00Z",
  "idempotency_key":"INC-102/payment/concurrency/attempt-1"
}
```

Envelope pin incident/RCA/policy/topology revision. Executor không nhận prompt “hãy sửa payment”; nó nhận mutation có scope và bounds.

---

## 30. Safety guardrails trước mọi action

Safety là một lớp policy độc lập với RCA/model. Ít nhất:

### 30.1 Dry-run và current-state diff

Dry-run gọi API validation/server-side dry-run khi có, rồi hiển thị before/after. Nó phát hiện target không tồn tại, policy schema sai hoặc desired state đã khác. Dry-run không chứng minh runtime safe; nó chỉ là gate cú pháp/phạm vi.

### 30.2 Scope validation

Target phải khớp allowlist cluster/namespace/service/tenant và ownership. Resolve UID, không chỉ name dễ bị recreate. Credential broker cấp least privilege cho action cụ thể và TTL ngắn; model không giữ admin token.

### 30.3 Blast-radius limit

Ví dụ scale tối đa `+2 replicas/lần`, restart tối đa một pod, canary 10% traffic, config delta trong bound. Không scale 6→60 hoặc restart toàn deployment. Kiểm tra quota và downstream capacity; scale app khi DB saturated có thể tăng hại.

### 30.4 Cooldown, max attempts và lease

Không cùng action/service trong 10 phút; tối đa 2 attempts/incident. Distributed lease ngăn hai controller cùng act. Attempt fail vẫn tính budget nếu đã tạo effect. Retry transport chỉ dùng cùng idempotency key, không thành attempt kinh tế mới.

### 30.5 Availability/correctness safety

Tôn trọng PodDisruptionBudget, ready replicas, quorum, leader state, AZ distribution, in-flight transaction và business constraints. Không drop/retry money operation nếu semantics chưa idempotent. Dependency safety kiểm tra downstream headroom trước scale.

### 30.6 Reversibility và before-state

Lưu exact before-state/version, không giả rollback là “trừ phần vừa cộng”. Trong lúc verify, HPA/human có thể thay đổi replicas; rollback dùng compare-and-set và ownership field để không đè thay đổi hợp lệ. Irreversible action không autonomous ở MVP.

### 30.7 Freshness, confidence và audit availability

Root confidence, evidence quality, topology/policy freshness đều qua threshold. Action expired bị deny. Nếu append-only audit không ghi được, high-risk mutation fail closed; read-only diagnosis có thể tiếp tục với local durable buffer theo policy.

### 30.8 Safety matrix

| Gate | Pass example | Fail behavior |
|---|---|---|
| Dry-run | API diff đúng 160 inflight | không execute, audit reason |
| Scope | prod-sea/shop/payment allowlisted | deny + security event |
| Blast radius | 10% canary, +2 max | clamp hoặc deny, không tự nới |
| Cooldown | last action 14 phút trước | defer/escalate |
| Attempts | attempt 1/2 | deny attempt 3 |
| Dependency | DB action reduces load | deny scale-up làm DB tệ hơn |
| Reversibility | before-state và rollback tested | recommend/human only |
| Freshness | RCA/topology <2 phút | re-diagnose |
| Audit | durable append acknowledged | fail closed theo risk tier |

Safety controller tự có metrics: denied by reason, stale envelope, duplicate idempotency, lease contention, dry-run mismatch, policy latency và unauthorized probe. Game day phải cố bypass từng hard gate.

---

## 31. Executor là reconcile controller, không phải script chạy một lần

State machine:

```text
PROPOSED → SAFETY_APPROVED → ACTION_PENDING → ACTION_RUNNING
                                      │             │
                                      │          effect observed
                                      │             v
                                      └────────> VERIFYING
                                                   │     │
                                               SUCCESS  FAILED/INCONCLUSIVE
                                                   │     │
                                                CLOSED  ROLLBACK → ESCALATED
```

Executor reconcile desired action với current state. Nó ghi intent trước mutation, dùng idempotency key, timeout và compare-and-set. API success chỉ chuyển `ACTION_RUNNING→VERIFYING`; không chuyển incident resolved.

Nếu controller crash sau API call nhưng trước ghi result, khi restart nó đọc action intent và current state. Nếu desired effect đã có, ghi `execution_reconciled`; không gọi lần hai. Nếu partial, policy quyết định complete/rollback. Đây là lý do cần persistent state và idempotency.

Human vẫn có thể override/kill switch. “Không cần người bấm” nghĩa eligible low-risk action tự đi qua policy, không nghĩa con người mất quyền dừng. Automation ngoài confidence/policy tự abstain và escalate.

---

## 32. Verification: command chạy được chưa chứng minh incident đỡ

Trước action lưu baseline verification snapshot:

```text
Payment p95       1.20 s
Payment error     18.0%
DB pool wait      820 ms
Queue depth       12,000
Checkout success  82.4%
SLO burn          18.2x
Traffic           7.8k RPS
```

Sau bounded action, chờ effect lag và đo nhiều evaluation:

```text
Payment p95       220 ms
Payment error     1.1%
DB pool wait      35 ms
Queue depth       3,000 and falling
Checkout success  99.2%
SLO burn          falling
Traffic           7.6k RPS
```

Verification plan gồm ba lớp:

1. **Mechanism:** metric root mechanism như pool wait/saturation cải thiện.
2. **Customer outcome:** success/latency/burn phục hồi.
3. **Harm/control:** correctness, unaffected cohort và adjacent dependencies không xấu.

```text
SUCCESS nếu trong 7/8 evaluations và ít nhất 5 phút:
  payment_latency_score < 2
  AND payment_error within recovery band
  AND checkout_success >= SLO recovery target
  AND burn_rate is falling below policy threshold
  AND no harm guardrail breached
  AND data quality GOOD
```

### 32.1 Pre/post không đủ

Traffic tự giảm có thể làm latency đỡ dù action vô ích. Normalize theo RPS/cohort, so canary với control nếu có và kiểm tra mechanism. Queue cần thời gian drain; level chưa về baseline nhưng slope âm mạnh có thể là `IMPROVING`, chưa `SUCCESS`.

### 32.2 Verification result ba giá trị

- `SUCCESS`: evidence đủ, outcome và harm đạt.
- `FAILED`: không cải thiện hoặc xấu rõ.
- `INCONCLUSIVE`: data missing, traffic đổi quá nhiều, effect lag chưa hết.

Inconclusive không được coi success. Policy có thể kéo dài bounded window một lần hoặc escalate; không lặp action mù.

### 32.3 Recovery và baseline

Verifier thành công đưa incident `RECOVERING`, không unfreeze ngay. Detector xác nhận khỏe thêm N evaluations rồi resolve và slow relearn. Verification plan không tự sửa baseline để làm điều kiện pass dễ hơn; nó pin last-known-good expectation.

---

## 33. Rollback và escalation khi verify fail

Khi failed:

1. đánh dấu attempt thất bại với evidence;
2. khóa lặp cùng catalog action bằng cooldown/attempt budget;
3. nếu action gây side effect và rollback safe, thực thi rollback envelope đã pin;
4. verify rollback/harm containment;
5. cập nhật RCA với intervention evidence;
6. thử alternative chỉ khi policy rõ và budget còn, nếu không escalate human.

Rollback cũng là action, phải safety check. Ví dụ rollback config về before-state có thể xung đột deploy mới của human. Compare current resource version; nếu conflict, stop/escalate thay vì đè.

### 33.1 Không phải mọi action cần hoàn tác

Scale-out tạm thời có thể không gây harm nhưng không chữa root; giữ replicas trong lúc incident có thể an toàn hơn rollback ngay. Policy phân biệt:

- **harmful change:** rollback tức thì;
- **neutral/no effect:** giữ hoặc revert sau stabilization/cost check;
- **partially successful:** giữ phần tốt, escalate phần còn lại với audit;
- **irreversible/unknown:** không auto-act từ đầu.

### 33.2 Escalation package

Human nhận incident summary, ranked candidates, actions/attempts, before/after telemetry, safety/verification failures và suggested discriminating query. Không chỉ “automation failed”. Paging route thật có delivery acknowledgment và fallback.

### 33.3 Pseudocode closed loop production-grade

Đoạn rút gọn `detect→act→verify` thường che ba vấn đề: incident revision có thể đổi trong lúc quyết định, action có thể hết hạn trước lúc execute, và verifier có thể thiếu data. Vòng thực tế phải reconcile persistent state:

```python
def reconcile_incident(incident_id):
    incident = incident_store.load_latest(incident_id)
    if incident.state not in {"FIRING", "MITIGATING", "RECOVERING"}:
        return

    if incident.state == "FIRING" and not incident.active_attempt:
        rca = rca_engine.diagnose(
            incident=incident,
            evidence_cutoff=clock.event_watermark(),
        )
        incident_store.append_rca_revision(rca)

        if rca.confidence < policy.min_diagnosis_confidence:
            escalate(incident, reason="RCA_UNCERTAIN", evidence=rca)
            return

        proposal = decision_engine.choose_from_catalog(incident, rca)
        if proposal is None:
            escalate(incident, reason="NO_ALLOWLISTED_ACTION", evidence=rca)
            return

        envelope = safety_controller.evaluate_and_seal(
            proposal=proposal,
            incident_revision=incident.revision,
            topology_revision=rca.topology_revision,
            include_dry_run=True,
        )
        audit.append(envelope.decision_event)
        if not envelope.approved:
            escalate(incident, reason=envelope.denial_reason)
            return

        # Re-read để không act trên incident đã recover hoặc RCA đã đổi.
        current = incident_store.load_latest(incident_id)
        if current.revision != envelope.incident_revision:
            expire(envelope, reason="STALE_INCIDENT_REVISION")
            return

        attempt = executor.apply_idempotent(envelope)
        incident_store.attach_attempt(attempt)
        # API success chỉ dẫn tới VERIFYING.

    attempt = incident_store.active_attempt(incident_id)
    if attempt and attempt.state == "VERIFYING":
        observations = verifier.collect(
            plan=attempt.verification_plan,
            pre_snapshot=attempt.pre_snapshot,
            current_event_time=clock.event_watermark(),
        )
        result = verifier.decide(observations)
        audit.append(result.event)

        if result.status == "SUCCESS":
            incident_store.transition(incident_id, "RECOVERING")
            detector.keep_baseline_frozen(incident.fault_keys)
        elif result.status == "FAILED":
            action_budget.block_repeat(attempt.catalog_id, incident_id)
            if attempt.rollback_envelope and rollback_is_still_safe(attempt):
                rollback_result = executor.apply_idempotent(
                    attempt.rollback_envelope
                )
                verify_rollback(rollback_result)
            rca_engine.add_intervention_evidence(incident_id, result)
            escalate(incident, reason="MITIGATION_FAILED", evidence=result)
        else:  # INCONCLUSIVE
            if verifier.extension_budget_available(attempt):
                verifier.extend_once(attempt)
            else:
                escalate(incident, reason="VERIFY_INCONCLUSIVE")

    if incident_store.load_latest(incident_id).state == "RECOVERING":
        recovery = verifier.check_sustained_customer_health(incident_id)
        if recovery.confirmed and recovery.data_quality == "GOOD":
            incident_store.transition(incident_id, "RESOLVED")
            detector.unfreeze_with_slow_relearning(incident.fault_keys)
        elif recovery.regressed:
            incident_store.transition(incident_id, "FIRING")
```

Hàm trên vẫn là pseudocode: transaction boundaries, retries và authorization cần implementation cụ thể. Điều quan trọng là mọi nhánh có state durable và audit event; `INCONCLUSIVE` không rơi vào success; baseline chỉ unfreeze sau sustained customer health; revision stale không được act. Controller gọi lại hàm sau event/timer/restart nên mỗi operation phải idempotent.

---

## 34. Audit trail: tái dựng từ trigger tới outcome

Audit là append-only event chain, không chỉ một JSON cuối bị overwrite. Các event:

```text
ANOMALY_EVALUATED
ALERT_STATE_CHANGED
INCIDENT_CREATED/REVISED/SPLIT/MERGED
RCA_HYPOTHESIS_RANKED
ACTION_PROPOSED
SAFETY_CHECK_PASSED/DENIED
ACTION_EXECUTED/RECONCILED
VERIFICATION_OBSERVED/DECIDED
ROLLBACK_EXECUTED
INCIDENT_RECOVERED/RESOLVED/ESCALATED
```

Mỗi event có actor (`detector-v7`, `policy-v4`, human ID), event/processing time, input refs/hashes, rule/model/topology/policy version, previous/new state, reason, idempotency và correlation IDs.

```json
{
  "event_type": "VERIFICATION_DECIDED",
  "incident_id": "INC-102",
  "action_id": "act/INC-102/attempt-1",
  "actor": "verifier-v4",
  "event_time": "2026-08-10T10:10:00Z",
  "inputs": {
    "pre_snapshot": "telemetry://snap/pre-102-a1",
    "post_snapshot": "telemetry://snap/post-102-a1",
    "query_hashes": ["sha256:..."],
    "data_quality": "GOOD"
  },
  "decision": "SUCCESS",
  "observed": {
    "payment_p95_ms": {"before":1200,"after":220},
    "checkout_success": {"before":0.824,"after":0.992},
    "queue_depth": {"before":12000,"after":3000,"slope":"falling"}
  },
  "rule_version": "verify/payment-pool-and-checkout-sli/v4",
  "previous_event_hash": "sha256:..."
}
```

Audit phải trả lời được:

- datapoint/query nào trigger và baseline snapshot nào được dùng?
- vì sao alert qualify và incident gom/tách?
- bằng chứng thuận/nghịch nào tạo RCA rank?
- policy nào cho phép action, exact diff gì?
- executor có duplicate/partial không?
- telemetry nào chứng minh outcome?
- rollback/escalation có xảy ra không?

Retention, access control, PII redaction và tamper evidence là bắt buộc. Audit outage behavior được game-day; không để chính incident làm mất lịch sử cần điều tra.

### 34.1 Một cuộc replay audit thực tế

Reviewer chọn `action_id`, đi ngược `previous_event_hash` tới incident và anomaly. Baseline snapshot liệt kê đúng 60 bucket accepted, ba point quarantine và freeze epoch. Query hashes tái tạo pre/post values trên immutable dataset revision. RCA revision cho thấy DB từ hạng hai lên hạng một vì 312 late spans, không phải model âm thầm đổi ý. Policy bundle chứng minh catalog action được phép ở namespace đó tại thời điểm execute; target UID và before-state khớp API audit. Verification lưu cả traffic/control nên reviewer loại khả năng metric đỡ chỉ vì traffic giảm.

Nếu thiếu một mắt xích, verdict là “không tái dựng được”, không tự điền bằng lời kể on-call. Audit completeness nên đo bằng sampling định kỳ và replay tự động, không chờ postmortem mới phát hiện query retention đã hết hoặc model artifact đã bị xóa.

---

## 35. Data structure và state persistence

State không chỉ nằm trong RAM của pod.

```text
DetectorState {
  key, phase, phase_since,
  baseline_snapshot_id, active_center, active_scale,
  persistence_ring[5], recovery_ring[8],
  firing_since, last_evaluated_at, last_good_data_at,
  baseline_frozen, freeze_epoch, quarantine_cursor,
  notification_cooldown_until,
  detector_version, checkpoint_version
}

Incident {
  id, revision, state, start_time, last_update,
  member_alert_ids[], fault_partitions[],
  affected_services[], affected_journeys[],
  slo_impact, anomaly_events[],
  root_candidates[], probable_root, confidence,
  evidence_ledger_ref, summary_revisions[],
  action_attempt_ids[]
}

RemediationAttempt {
  action_id, incident_revision, catalog_version,
  target_uid, before_state, desired_state,
  safety_results[], lease, idempotency_key,
  execution_result, verification_plan,
  verification_observations[], verification_result,
  rollback_envelope, rollback_result,
  started_at, expires_at, attempt_number
}
```

Hot state/ring buffers có thể ở Redis/RocksDB state backend; durable truth ở PostgreSQL/event log; time-series ở Prometheus-compatible store; audit ở append-only database/object store. Tên sản phẩm có thể đổi, semantics không đổi.

### 35.1 Restart recovery

Pod restart lúc `FIRING`:

1. nhận shard lease sau khi instance cũ hết lease;
2. load checkpoint gồm phase/freeze/persistence/offset;
3. replay events sau checkpoint từ stream/outbox;
4. query bounded telemetry để lấp window nếu cần;
5. tiếp tục cùng alert/incident ID;
6. không gửi opening page hoặc execute action trùng.

Nếu state store mất hoàn toàn, rebuild từ durable anomaly/incident events và last-known-good baseline snapshot. Trong lúc rebuild, state là `RECOVERING_STATE`, automation write bị hạ quyền; SLO/static alert path vẫn hoạt động.

### 35.2 Idempotency và ordering

Event consumer commit offset cùng state/outbox transaction hoặc dùng exactly-once-equivalent semantics bằng idempotent keys. Late event tạo revision monotonic, không quay state machine lùi tùy tiện. `incident_revision=8` không bị result revision 7 overwrite. Action pin revision nhưng executor vẫn re-check current incident trước mutation.

### 35.3 Retention của state

Baseline snapshots cần đủ để replay decision; raw high-resolution samples có retention ngắn hơn derived/audit. Resolved incident giữ tombstone/dedup TTL để late events không mở duplicate. Quarantine có expiry và incident reference; expiry không được xóa audit provenance.

---

## 36. Production architecture và cách chạy liên tục trên trunk

```text
Apps / K8s / Cloud
  ├── Prometheus / remote-write ─────────────┐
  ├── OTel Collector → Tempo/Jaeger traces ─┼─> Feature/Data Plane
  ├── Logs → Loki/OpenSearch subset ─────────┤         │
  └── Deploy/topology/cost events ───────────┘         v
                                                Kafka/event stream
                                                       │
                         ┌─────────────────────────────┼──────────────┐
                         v                             v              v
                  Detector Service              SLO/Burn Engine  Topology Builder
                         │                             │              │
                         └──── anomaly/alert events ──┴──────┬───────┘
                                                            v
                                                  Incident Manager
                                                            │
                                                            v
                                      RCA Engine ↔ Metrics/Trace/Log queries
                                                            │
                                              summary + action proposal
                                                            v
                                             Policy/Safety Controller
                                                            │
                                                            v
                                              Remediation Controller
                                                            │
                                              Kubernetes/flag/config API
                                                            │
                                                            v
                                                   Verification Engine
                                                            │
                          PostgreSQL/state store <───────────┼──> Audit event store
                                                            └──> Slack/PagerDuty/Teams
```

### 36.1 Workload model

Detector là Kubernetes `Deployment`, ví dụ 2–3 replicas, shard keys bằng consistent hash hoặc Kafka partitions. Mỗi key có một active evaluator; replica khác sẵn sàng takeover. Nếu scheduler toàn cục, dùng leader election chỉ cho việc phân shard, không làm một leader tính mọi series thành bottleneck.

Health endpoints:

- liveness: process/event loop còn hoạt động;
- readiness: state store/stream/query dependencies đủ cho assigned role;
- startup: checkpoint/replay hoàn tất;
- business health: evaluation lag, key coverage và event publish success.

Liveness không restart pod chỉ vì Prometheus tạm lỗi, tránh restart storm; readiness/degraded mode phù hợp hơn.

### 36.2 State và HA

State store replicated và backed up; detector checkpoints versioned; consumer lag autoscaling có bound. Incident/action state cần transactional durability cao hơn ephemeral score cache. Multi-zone nhưng không active-active mutation cùng target nếu chưa có lease/fencing token. Fencing ngăn controller cũ sống lại sau network partition và act với lease hết hạn.

### 36.3 Degraded modes

| Dependency hỏng | Detection | RCA | Auto-action |
|---|---|---|---|
| Trace store | metric detector tiếp tục | hạ confidence, no trace claim | chỉ action không cần trace nếu policy cho |
| Topology stale | per-key tiếp tục | shortlist với cap | high-risk deny |
| State store read-only | dùng cache bounded | incident update buffer | write action deny |
| Audit unavailable | observe/read-only tùy tier | summary có warning | fail closed high-risk |
| Notification channel | incident vẫn active | summary retry/fallback | action policy độc lập nhưng page fallback bắt buộc theo tier |

### 36.4 Code trên trunk, không phải notebook

Repository production chứa service/controller, schema migrations, policy/catalog, replay fixtures, dashboards và runbook. Pipeline CI:

```text
lint/unit → deterministic algorithm tests → schema compatibility
→ labeled replay regression → safety policy tests → container scan
→ shadow/canary → merge main/trunk → continuous Deployment
```

Notebook dùng research nhưng model/rule được đóng gói versioned artifact và chạy qua cùng contract. Deployment manifest có resources, PDB, service account least privilege, probes và rollback. “Chạy `python detect.py` một lần” không đạt continuous detection. Merge vào main chỉ là điều kiện phân phối; production acceptance còn cần shadow/canary/game day.

### 36.5 SLO cho chính AIOps plane

Ví dụ SLO nội bộ:

- 99,9% eligible keys evaluate không muộn quá 90 giây;
- 99,99% incident/action transitions không mất;
- 100% autonomous actions có complete audit envelope;
- p95 fast RCA revision dưới 30 giây;
- notification opening delivery dưới 60 giây theo tier.

Đo end-to-end từ telemetry event-time, không chỉ service uptime. Detector API 100% up nhưng evaluation lag 20 phút là down về outcome.

---

## 37. Đánh giá detector, RCA và remediation trên labeled cases

Không lấy vài dashboard đẹp làm bằng chứng. Dataset nhỏ nhưng phải có timeline, ground truth, negative control, delivery faults và expected lifecycle. Mỗi case pin data/rule/topology versions; replay theo event-time để engine không nhìn tương lai.

### 37.1 Bộ case tối thiểu

| Case | Ground truth | Expected detection/correlation/RCA/action |
|---|---|---|
| C1 Payment DB saturation | incident thật; DB origin | page checkout impact, một incident, DB top rank |
| C2 Checkout memory leak | incident mới/chưa catalog | detect gradual resource+latency, localize checkout, abstain unsafe action |
| C3 Traffic campaign 5x khỏe | negative | traffic baseline/context đổi; không page P1 |
| C4 Inventory dependency timeout | incident thật | inventory origin, trace edge evidence |
| C5 Single 45s spike | noise negative | `SUSPECT` rồi normal, không alert |
| C6 Payment incident + Inventory fault phút 15 | hai incidents/partitions thật | giữ A firing; bắt/tách B; không masking |
| C7 Missing scrape/traces | data fault, impact unknown | `DATA_INSUFFICIENT`, không false recovery/RCA claim |
| C8 Gradual degradation | incident thật | slope/CUSUM phải bắt trước SLO deadline |
| C9 Healthy deploy shift 100→120 ms | legitimate drift negative | warm/change-point/rebase; không page |

Mỗi case còn có unaffected cohort/control. C6 kiểm tra detector state độc lập và false merge. C7 kiểm tra hard gate missing-as-recovery. C9 phân biệt drift khỏi contamination.

### 37.2 Matching prediction với label

Một predicted page là TP nếu scope/journey khớp labeled incident và opening time nằm trong `[fault_start, detection_deadline]`. Page không match là FP. Labeled incident không có page đúng deadline là FN. Nhiều notification cùng incident không tạo nhiều TP; duplicate là metric spam riêng. Một incident hai root partition phải match hai labels.

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 × Precision × Recall / (Precision + Recall)
```

Precision hỏi “trong pages đã gửi, bao nhiêu đúng?”. Recall hỏi “trong incidents cần bắt, bao nhiêu được bắt?”. Suppress mọi thứ làm không có FP nhưng recall 0; page mọi anomaly làm recall cao nhưng precision thấp.

### 37.3 Kết quả minh họa, không phải số production

Giả sử C1, C2, C4, C6-A, C6-B được bắt; C8 bị miss; C9 bị page giả; C3/C5/C7 không page sai. Có 6 labeled incidents thật, 6 predicted pages (5 đúng, 1 sai):

```text
TP = 5, FP = 1, FN = 1
Precision = 5 / (5 + 1) = 83,3%
Recall    = 5 / (5 + 1) = 83,3%
F1        = 83,3%
```

Đây là ví dụ minh họa cách tính, không phải claim. Review C8 phải dẫn tới detector slope/threshold change; C9 dẫn tới deployment-aware rebase. Sau sửa, chạy lại toàn suite để tránh đổi precision lấy recall ở case khác.

### 37.4 Metric ngoài Precision/Recall

| Stage | Metric | Điều nó bắt |
|---|---|---|
| Detection | detection delay, recall-at-2m/5m | nhanh đúng deadline |
| Lifecycle | silent-gap seconds, recovery precision, flap count | incident dài liên tục |
| Alert | pages/incident, duplicate notification | spam |
| Correlation | false merge/split, compression ratio | đúng số incident |
| RCA | top-1/top-3 component, mechanism accuracy | localization/ranking |
| RCA | calibration/Brier, contradiction recall | confidence trung thực |
| Remediation | eligible-action precision, mitigation success | chọn đúng action |
| Safety | unsafe action escape rate | hard gate, mục tiêu 0 trong test |
| Verification | false success/false rollback | outcome đúng |
| End-to-end | time-to-safe-mitigation, customer bad minutes | giá trị thực |

Slice theo service tier, traffic volume, region, fault class, missing-data và known/unknown. Global 90% có thể che sparse service recall 20%.

### 37.5 RCA ground truth và partial credit

Đánh riêng component top-1/top-3, failure mechanism, causal path edge precision, fact/provenance correctness, confidence calibration và abstention khi evidence thiếu. RCA rank đúng payment service nhưng bỏ DB resource là partial, không full. Case ambiguous có allowed top-k/abstain; không ép một đáp án giả.

### 37.6 Remediation evaluation

Replay/canary phải biết safe action, prohibited action, expected lag và rollback. Command accepted không tính success. Đo:

```text
mitigation_success = customer outcome recovered AND no harm
false_success = verifier says success but ground truth outcome not recovered
harm_rate = attempts breaching correctness/availability guardrail / attempts
rollback_success = rollback restored safe before-state and contained harm
```

Một unsafe action escape là hard fail dù average detection F1 cao.

---

## 38. Detection delay và MTTD before/after

Định nghĩa trong chapter:

```text
detection_delay = aiops_detected_at - actual_incident_start
legacy_MTTD     = legacy_alert_at - actual_incident_start
lead_over_legacy = legacy_alert_at - aiops_detected_at
```

Từ “lead time” đôi khi mang dấu âm trong forecasting; ghi công thức tránh tranh cãi. MTTD aggregate chỉ trên incidents được detect; FN phải báo riêng hoặc gán deadline penalty, nếu không hệ bỏ case khó sẽ làm MTTD trông đẹp.

### 38.1 Một phép tính cụ thể

```text
Actual start:  10:03:40
AIOps detect:  10:04:15 → delay 35 s
Legacy alert:  10:08:30 → delay 4 m 50 s
Lead gained:   10:08:30 - 10:04:15 = 4 m 15 s
```

### 38.2 Bảng minh họa năm incident bắt được

| Incident | Actual start | AIOps firing | AIOps delay | Legacy page | Legacy delay | Lead gained |
|---|---|---|---:|---|---:|---:|
| C1 | 10:03:40 | 10:04:15 | 0:35 | 10:08:30 | 4:50 | 4:15 |
| C2 | 11:00:00 | 11:03:00 | 3:00 | 11:12:00 | 12:00 | 9:00 |
| C4 | 12:00:00 | 12:01:30 | 1:30 | 12:05:00 | 5:00 | 3:30 |
| C6-A | 13:00:00 | 13:01:30 | 1:30 | 13:06:00 | 6:00 | 4:30 |
| C6-B | 13:15:00 | 13:16:30 | 1:30 | 13:22:00 | 7:00 | 5:30 |

Minh họa:

```text
Median AIOps MTTD = 1m30s
Median legacy MTTD = 6m00s
Median per-case lead gained = 4m30s

Mean AIOps MTTD = (35+180+90+90+90)/5 = 97s = 1m37s
Mean legacy MTTD = (290+720+300+360+420)/5 = 418s = 6m58s
Mean reduction = 321s = 5m21s, khoảng 76,8%
```

Phải report cùng `FN=1` ở C8. Không được viết “MTTD 1m37” rồi giấu gradual incident không detect. So before/after trên cùng cases, cùng fault start và delivery model; không so incident dễ của model mới với incident khó của legacy.

---

## 39. Edge cases bắt buộc và trade-off

### 39.1 Sparse traffic

**Sai gì:** 1 lỗi/1 request thành 100%, p99 vô nghĩa. **Vì sao:** denominator nhỏ làm variance cực lớn. **Giảm thiểu:** minimum count, Wilson/Beta interval, window dài hơn, synthetic probe và expected-event rule. **Trade-off:** detection chậm; synthetic không đại diện mọi cohort. Critical low-volume money flow nên dùng correctness invariant/count, không chỉ rate.

### 39.2 Cold start

**Sai gì:** service mới không có baseline hoặc học startup burst làm normal. **Giảm thiểu:** `WARMING`, hierarchical prior, static SLO/safety rules, minimum time span và version-aware canary. **Trade-off:** giảm recall behavioral trong warm-up; prior service class có thể không hợp. Không auto-act dựa vào low-confidence baseline.

### 39.3 Missing telemetry

**Sai gì:** missing biến thành zero/healthy, incident tự resolve. **Vì sao:** query functions và dashboard thường fill zero. **Giảm thiểu:** explicit null/reason, coverage/freshness, `DATA_INSUFFICIENT`, hold active incident, independent watchdog. **Trade-off:** có thể giữ incident lâu khi observability hỏng; đó là uncertainty trung thực hơn false recovery.

### 39.4 Counter reset

**Sai gì:** negative/huge delta tạo rate spike/drop. **Giảm thiểu:** detect reset per series trước aggregate, use `rate`, join pod restart metadata, quality flag. **Trade-off:** bucket quanh restart có thể bị loại/hạ confidence; quá nhiều ephemeral pods làm effective coverage thấp.

### 39.5 Cardinality explosion

**Sai gì:** customer/request IDs tạo millions detector keys, memory/compute/state chết. **Giảm thiểu:** label allowlist, budgets, aggregate service/critical route, heavy-hitter/cohort drilldown, reject/quarantine unknown labels. **Trade-off:** aggregation có thể che tenant nhỏ; giữ curated risk slices và on-demand investigation.

### 39.6 Single spike

**Sai gì:** robust score rất cao dẫn page giả; outlier kéo mean/σ. **Giảm thiểu:** persistence/debounce, median/MAD, raw retention, invariant bypass cho truly critical. **Trade-off:** thêm 45–135 giây detection delay; rule bypass phải rất ít và audit được.

### 39.7 Long-running anomaly 40 phút hoặc nhiều giờ

**Sai gì:** rolling baseline học incident, score biến mất; cooldown bị hiểu nhầm thành stop evaluate. **Giảm thiểu:** freeze/quarantine per key, persistent `FIRING`, periodic evidence update, max-freeze/stale mode, recovery confirmation. **Trade-off:** baseline stale; cần shadow baseline và slow re-learning, không auto-promote.

### 39.8 Gradual degradation

**Sai gì:** local center theo dõi 100→110→...→300, mỗi residual nhỏ. **Giảm thiểu:** slope, CUSUM, fast-vs-slow divergence, seasonal/last-known-good, SLO slow burn. **Trade-off:** legitimate optimization/load trend dễ báo; change/calendar context và longer confirmation cần thiết.

### 39.9 Traffic spike hợp lệ

**Sai gì:** CPU/queue/cost/hour cùng tăng, detector tưởng incident. **Giảm thiểu:** seasonal traffic baseline, cost/resource per request, latency/error/SLO gates, campaign metadata, control cohort. **Trade-off:** campaign metadata có thể sai; không suppress user-visible SLO chỉ vì calendar nói campaign.

### 39.10 Deployment-induced baseline shift

**Sai gì:** healthy 100→120 ms page mãi, hoặc reset baseline che regression. **Giảm thiểu:** canary/control, version-aware shadow baseline, change-point + healthy outcome confirmation, gradual promote. **Trade-off:** giữ baseline theo version tốn state; rollout nhỏ thiếu mẫu. Deploy là context, không whitelist.

### 39.11 Incident thứ hai khi incident đầu active

**Sai gì:** global freeze/global incident merge nuốt Inventory fault trong Payment outage. **Giảm thiểu:** state per service/signal/cohort; detector luôn chạy; correlation after detection; graph/cohort/time partition và false-merge threshold. **Trade-off:** có thể false split; UI cần related incidents và merge revision có evidence.

### 39.12 Nhiều dependent services đỏ cùng lúc

**Sai gì:** page mọi service hoặc gọi frontend root vì error lớn nhất. **Giảm thiểu:** correlate bằng topology/trace/cohort, RCA traverse dependency, downstream-impact weighting và dependency-explanation penalty. **Trade-off:** graph stale làm rank sai; cap confidence/auto-action và giữ top-k.

### 39.13 Clock skew và delayed telemetry

**Sai gì:** temporal order đảo, first-red sai; late event mở/page/action lại. **Giảm thiểu:** event/ingest time, NTP offset, watermarks, uncertainty intervals, monotonic revisions và action expiry. **Trade-off:** watermark dài tăng latency; ngắn tăng revisions. Critical fast path có provisional result với confidence thấp.

### 39.14 Missing traces

**Sai gì:** absence bị coi dependency khỏe hoặc RCA vẫn tuyên trace evidence. **Giảm thiểu:** trace coverage/sampling metadata, fallback metric/topology/log, confidence cap, telemetry fault event. **Trade-off:** RCA ít chắc, nhiều abstention. Không bịa causal path để giữ UX đẹp.

### 39.15 False root do correlated load

**Sai gì:** mọi service CPU tăng vì traffic; service first-red vô can bị rank root. **Giảm thiểu:** dependency path, request cohort, semantic mechanism, unaffected controls, normalize by load và intervention evidence. **Trade-off:** control không luôn tồn tại; causal conclusion chậm hơn simple correlation nhưng an toàn hơn cho automation.

### 39.16 Recovery oscillation

**Sai gì:** score quanh threshold gây firing/resolved liên tục, baseline unfreeze/refreeze. **Giảm thiểu:** hysteresis, 7/8 healthy + minimum 5 phút, SLI/burn recovery, cooldown notification và same incident reopen grace. **Trade-off:** resolve chậm; UI nên hiển thị improving/recovering để on-call biết hệ không treo.

### 39.17 MAD bằng 0 và metric bounded/discrete

**Sai gì:** chia zero hoặc thay đổi nhỏ thành score vô hạn. **Giảm thiểu:** scale floor theo unit/resolution, count model, static invariant cho replicas/quorum, rolling quantile. **Trade-off:** floor quá lớn bỏ anomaly nhỏ; benchmark từng signal class, không một epsilon toàn hệ.

### 39.18 Route mix và Simpson's paradox

**Sai gì:** service aggregate latency tăng vì tỷ trọng route chậm hợp lệ tăng, dù từng route khỏe; hoặc aggregate khỏe che route critical lỗi. **Giảm thiểu:** critical route/cohort baselines, traffic-mix features và weighted expected aggregate. **Trade-off:** cardinality/state tăng; chỉ slice theo business risk và đủ samples.

---

## 40. Walkthrough hoàn chỉnh: Payment DB saturation tới recovery

Baseline trước incident cho `payment:p95_latency`: median 121 ms, MAD 14 ms, effective scale `1,4826×14=20,76 ms`. Fire threshold raw 4, persistence 3/5. Baseline error 0,18%; DB pool 65%; checkout success 99,7%.

### 10:00:00 — healthy

Evaluation query event-time `(09:00,10:00]`, quality GOOD, 60 closed one-minute features. Current p95 124 ms:

```text
score = (124-121)/20,76 = 0,14
```

State `NORMAL`; sample accepted; baseline snapshot v330. SLO burn 0,7x.

### 10:03:15 — mechanism bắt đầu

DB connection usage tăng 65→96%, pool wait 18→140 ms. Bucket chưa đủ persistence; pool detector `SUSPECT`. Raw telemetry, source offsets và deploy context được giữ. Không page.

### 10:03:45 — payment latency lệch

Current p95 220 ms:

```text
raw score = (220-121)/20,76 = 4,77
```

Latency `NORMAL→SUSPECT`; point 220 vào quarantine, không vào active baseline. Pool utilization đạt 100%; error bắt đầu tăng. Đây là evaluation 1/5.

### 10:04:30 — nhiều evidence hơn

Payment p95 275 ms, robust score `154/20,76=7,42`; queue slope dương; pool wait 430 ms. Latency persistence 2 evaluations; pool/queue vote. SLO short burn mới 5x, chưa long confirmation. State vẫn `SUSPECT`; baseline v330 frozen candidate, chưa opening page.

### 10:05:15 — alert firing

Payment p95 480 ms, raw score 17,3; 3/5 thỏa. Error volume đủ 14.000 requests; timeout và queue cùng tăng. Checkout success bắt đầu giảm và fast burn vượt policy. Alert `payment-latency` chuyển `FIRING`; baseline chính thức freeze tại v330; notification opening/dedup key được tạo một lần.

### 10:05:30–10:06:15 — cascade và correlation

Checkout child spans gọi Payment timeout; API 5xx và Frontend checkout failure theo sau. Mỗi service detector riêng chuyển state, không copy payment score. Correlator thấy time proximity, path `frontend→api→checkout→payment→db`, cùng `/checkout` cohort và trace propagation, gom vào `INC-102`. Năm alerts thành một incident, vẫn giữ từng anomaly evidence.

### 10:06:30–10:06:45 — RCA revisions

Fast RCA rank ban đầu payment 0,82, DB 0,79 vì trace coverage thấp. Late DB spans/log template `pool_acquire_timeout` tới; DB saturation đỏ trước payment, payment bị dependency explanation. Revision mới:

```text
1. payment-db connection capacity exhaustion: 0.86
2. payment retry amplification:              0.54
3. checkout:                                 0.31
```

Trace cho thấy payment child chiếm 79% checkout critical path; 74% failed sampled traces có acquire timeout. Summary phân facts/inference, gửi channel thật.

### 10:07:00–10:07:30 — decide và act an toàn

RCA chỉ ra DB headroom thấp nên decision **không scale payment lên**. Catalog chọn cap max in-flight/retry trên canary 10% để giảm pressure. Dry-run, target UID, PDB, money-operation idempotency, cooldown, max attempts, audit availability và rollback plan đều pass. Executor ghi intent, apply config, nhận API success rồi vào `VERIFYING`; incident chưa resolved.

### 10:08:00–10:10:00 — verify bằng telemetry

Canary pool wait giảm trước; payment p95 1,2 s→220 ms; error 18%→1,1%; queue 12k→3k và slope âm; checkout success 82,4→99,2%; traffic gần như giữ 7,8k→7,6k RPS. Control không xấu; no correctness harm. 7/8 evaluations và minimum window thỏa; verifier `SUCCESS`.

### 10:11:00–10:14:15 — recovery, resolve, learn chậm

Incident `FIRING→RECOVERING`; detector baseline vẫn v330 frozen. Sau 5 phút healthy, alerts resolve, incident closed. Recovery samples được promote có weight cap; active baseline unfreeze/slow re-learn. Audit chain nối raw snapshots, score/state, RCA revisions, safety result, exact config diff, verification và delivery receipt. MTTD tính từ 10:03:15 mechanism hoặc labeled user-impact start theo benchmark contract, không tùy chọn timestamp có lợi.

### 10:18:00 — fault độc lập không bị che

Nếu Inventory timeout nổ lúc payment còn recovering, `inventory:*` state vẫn evaluate. Trace/cohort không support cùng origin; correlator tạo `INC-103 related_concurrent`, không nhét vào INC-102. Đây là acceptance cho per-service isolation và overlapping incident.

---

## 41. Walkthrough remediation thất bại: scale app làm DB tệ hơn

Giả sử RCA revision sớm chỉ rank `payment saturation` 0,72 và policy cũ cho scale 6→8 replicas. Đây là action reversible, bounded +2, dry-run/scope pass; nhưng hypothesis mechanism chưa đủ sâu.

### 41.1 Trước action

```text
payment replicas = 6
app CPU = 88%
DB active connections = 196/200
pool wait = 600 ms
payment p95 = 900 ms
checkout error = 12%
```

Scale làm mỗi replica mở pool mới. Kubernetes API trả success, 8 pods Ready. Execution thành công về control plane, nhưng verification thấy:

```text
DB connections 196 → 200/200
pool wait       600 → 940 ms
payment p95     900 → 1,350 ms
checkout error  12% → 19%
burn rate       14x → 21x
```

Traffic không tăng và control region không xấu; mechanism/harm đều đi sai direction. Verifier trả `FAILED_HARM`, không chờ hết 5 phút vì early-abort guardrail.

### 41.2 Rollback và re-diagnose

Controller lấy before-state 6, kiểm tra HPA/human chưa đổi ownership, scale 8→6 theo rollback envelope. Nó verify ready capacity và DB connection giảm; không tuyên incident healed. Same `scale-payment` action bị block bởi cooldown/max attempt.

Intervention evidence cập nhật RCA: scale app tăng DB pressure, làm hypothesis DB bottleneck mạnh hơn. Rank mới:

```text
payment-db max_connections/pool exhaustion: 0.89
payment CPU capacity:                       0.28
```

Policy chọn alternative allowlisted: cap concurrency/retries hoặc load shed bounded. Nếu money-path semantics/DB change không đủ chắc, escalate DBA/on-call với package đầy đủ. Không tự tăng `max_connections` nếu memory/headroom/transaction risk chưa kiểm chứng.

### 41.3 Điều case này chứng minh

- dry-run pass không đảm bảo causal action đúng;
- API success không phải remediation success;
- verify cần mechanism + customer outcome + harm;
- rollback cũng cần compare-and-set/safety;
- failed intervention là evidence cho RCA, không là lý do lặp action;
- automation an toàn biết dừng và escalate.

---

## 42. Recommended MVP: đơn giản, giải thích được, chạy được

### Detection MVP

```text
key: environment + service + critical route + signal
signals: RPS, error, p95/p99, saturation/pool, queue age/slope, cost/work
baseline: rolling median + MAD 60m accepted samples
fast path: 5m residual; seasonal reference khi đủ 4–8 tuần
gates: quality, minimum traffic, persistence 3/5, hysteresis
lifecycle: NORMAL/SUSPECT/FIRING/RECOVERING/DATA_INSUFFICIENT
protection: per-key quarantine/freeze, max freeze, slow relearn
```

### Alert/incident MVP

```text
severity: user SLI + multi-window burn + blast radius + criticality
dedup: stable alert key; notification on transitions
cooldown: suppress duplicate delivery, never stop evaluation
correlation: time + topology + trace cohort
overlap: per-key detection, conservative incident partition/split
```

### RCA MVP

```text
dependency graph snapshot
+ temporal precedence with uncertainty
+ affected-caller/downstream weighting
+ trace first-error/critical-path propagation
+ multi-signal mechanism evidence
- dependency explanation/correlation/counter-evidence penalties
→ top-3 hypotheses + confidence + observed/inferred/missing
```

Không cần GNN/autoencoder trước khi replay chứng minh heuristic bỏ lỡ material incidents.

### Remediation MVP

```text
typed allowlisted action catalog
+ confidence/evidence/action-match threshold
+ dry-run + exact scope + bounded blast radius
+ cooldown + max attempts + lease/idempotency
+ pre-pinned verification and rollback plans
→ autonomous only for reversible low-risk actions
```

### Rollout

1. Offline replay và unit/property tests.
2. Shadow: detect/diagnose, không page/action.
3. Page assist: summary/RCA cho human.
4. Recommend action + dry-run.
5. Bounded autonomous canary cho action class đã acceptance.
6. Mở scope từng service/tier; expiry và kill switch luôn có.

### 42.1 Những anti-pattern cần chặn ngay ở design review

| Anti-pattern | Vì sao nguy hiểm | Thay bằng |
|---|---|---|
| Một threshold latency cho toàn fleet | bỏ khác biệt service/route | baseline per-key + SLO limit riêng |
| Recompute baseline từ mọi point | incident dài tự thành normal | accepted/quarantine/freeze lifecycle |
| `anomaly=true` gửi thẳng PagerDuty | spike/noise tạo alert fatigue | persistence + impact qualification |
| Cooldown bằng cách ngừng detector | tạo silent gap, che fault mới | evaluate liên tục, chỉ rate-limit delivery |
| Global incident lock | service khác không còn được detect | detector state độc lập, correlate sau |
| Merge mọi alert gần thời gian | fault concurrent thành một root giả | topology/cohort/path + split support |
| Service đỏ nhất là root | downstream symptom thường đỏ nhất | dependency explanation + trace propagation |
| First-red là causal proof | clock/skew/sensitivity làm sai order | time uncertainty + topology + semantics |
| Confidence score tự gọi probability | tạo quyền giả cho automation | calibration, evidence-quality cap, abstain |
| LLM đọc raw log rồi tự chọn lệnh | injection, hallucination, scope vô hạn | structured ledger + typed action catalog |
| Dry-run pass nghĩa action safe | chỉ chứng minh API chấp nhận diff | blast-radius/dependency/harm gates |
| Kubernetes API success = resolved | control plane success không phải outcome | post-action telemetry verification |
| Verify mỗi target CPU | có thể tối ưu metric nhưng hại user | mechanism + customer SLI + harm/control |
| Rollback bằng phép toán ngược | đè thay đổi human/HPA xảy ra sau | saved before-state + compare-and-set |
| State chỉ trong pod | restart quên firing/action, tạo duplicate | checkpoint + event replay + idempotency |
| Chỉ báo average accuracy | che sparse cohort/FN/harm | slices + deadline + hard safety gates |

Một design review tốt yêu cầu engineer điền “nếu assumption này sai thì hệ sẽ làm gì?”. Ví dụ, nếu trace mất, RCA phải hạ confidence chứ không thay missing bằng evidence khỏe; nếu audit store mất, high-risk action fail closed; nếu traffic tự giảm sau action, verifier phải nhận ra confounder. Các nhánh degraded/failure quan trọng ngang happy path vì incident thật thường làm hỏng chính telemetry và control plane mà automation phụ thuộc.

---

## 43. Acceptance matrix cho chapter

| Capability | Scenario/evidence bắt buộc | Pass condition khởi đầu |
|---|---|---|
| Per-service baseline | A 40 ms, B 700 ms; cùng point 300 | decision dựa deviation, không global threshold |
| 45s/60m mechanics | replay boundary/add/remove/late | snapshot/recompute đúng, reproducible |
| Spike/noise | C5 | không page; raw evidence giữ |
| Traffic legitimate | C3 | không P1 nếu SLI/burn khỏe |
| Long incident | ≥40 phút | không silent gap/false recovery; baseline frozen |
| Concurrent incident | C6 | bắt B đúng deadline, false merge trong threshold |
| Missing/sparse | C7 + low volume | no missing-as-recovery; uncertainty rõ |
| Alert quality | labeled suite | precision/recall/F1/duplicate có denominator |
| Burn-rate | synthetic SLO timelines | short+long behavior đúng |
| RCA | cascade + confounder | root top-k, evidence/counter-evidence/provenance |
| Unknown fault | C2 | localize hợp lý hoặc abstain; không học tủ |
| Summary | incident revision | facts/inference tách, không unsupported claim |
| Safety | bypass/game-day matrix | unsafe action escape = 0 trong acceptance |
| Verification | success + traffic drop control | không command-success/false-success |
| Failed action | DB scale case | early fail, rollback/escalate, no repeat |
| Restart | detector/executor crash giữa lifecycle | same IDs/state; no duplicate page/action |
| Audit | chọn ngẫu nhiên decision chains | tái dựng input/version/reason/effect 100% |
| Trunk/workload | CI + Deployment evidence | long-running HA, replay gate, merged main |

Threshold cụ thể phải do owner/SLO/risk tier phê duyệt; bảng là starting contract, không là giấy phép auto-action chung. Hard fails: missing được coi recovery, unauthorized/stale action chạy, duplicate economic effect, false success, mất active incident qua restart hoặc audit không tái dựng được action.

---

## 44. Checklist triển khai cho engineer

- [ ] Mọi feature có identity, unit, event-time, quality, denominator và provenance.
- [ ] Counter tính rate per series trước aggregate; missing không fill zero.
- [ ] Mỗi service/signal/critical cohort có state/baseline riêng.
- [ ] Median/MAD có scale floor, direction và minimum samples theo semantics.
- [ ] Window boundary, watermark và snapshot ID được test.
- [ ] Persistence, hysteresis, debounce, dedup và cooldown tách nghĩa.
- [ ] Baseline quarantine/freeze theo key; recovery mới slow relearn.
- [ ] Drift dùng shadow/dual/seasonal/change context, không auto-reset mù.
- [ ] SLO multi-window burn và customer symptom quyết severity.
- [ ] Active incident vẫn evaluate; concurrent service không bị disable.
- [ ] Correlation hỗ trợ split/multi-root, không merge theo time đơn thuần.
- [ ] RCA có topology revision, time uncertainty, trace coverage và counter-evidence.
- [ ] Summary tách observed/inferred/missing/contradicting.
- [ ] Action dùng catalog/envelope, không shell/prompt tự do.
- [ ] Dry-run, scope, blast radius, cooldown, attempts, lease, expiry đều là gates.
- [ ] API success chỉ bắt đầu verification.
- [ ] Verify mechanism, customer outcome, harm và data quality.
- [ ] Failed/inconclusive không thành success; rollback có safety riêng.
- [ ] State durable, restart replay idempotent, notification/action không trùng.
- [ ] Audit append-only pin mọi version và snapshot.
- [ ] Replay có positive, negative, long, concurrent, missing, restart và failed action.
- [ ] Report Precision/Recall/F1/MTTD cùng FN, slices và illustrative/production label.
- [ ] Detector là workload thường trực, có SLO và được release từ main/trunk.

---

## 45. Key takeaways

Một AIOps production đáng tin không bắt đầu bằng deep learning. Nó bắt đầu bằng telemetry contract đúng, baseline riêng cho đúng service/signal, state machine bền, SLO impact và evidence có provenance. Median/MAD giúp chống outlier nhưng không tự chống incident contamination; freeze/quarantine và lifecycle mới giữ sự cố dài. Correlation giảm spam nhưng phải biết split fault concurrent. RCA là ranking probabilistic có topology, thời gian, trace, mechanism và phản chứng; service đỏ nhất không mặc định là root.

Closed loop chỉ khép khi action đi qua hard safety gates, effect được kiểm tra bằng telemetry customer thật và failure tự rollback/escalate. Kubernetes trả success chỉ nói command được nhận. Audit phải kể lại được hệ thấy gì, kỳ vọng gì, suy luận gì, được phép làm gì, đã thay đổi gì và outcome ra sao.

Mental model cuối cùng:

```text
Observe faithfully
  → understand normal in context
  → detect deviation per service/signal
  → qualify persistent customer impact
  → correlate without masking concurrent faults
  → rank causes with evidence and uncertainty
  → choose only an allowed reversible action
  → act inside a bounded blast radius
  → verify mechanism + customer outcome + harm
  → recover, rollback or escalate
  → preserve the entire decision chain for replay and learning
```

Nếu một datapoint không truy được nguồn, baseline không nói được nó đã học mẫu nào, RCA không nêu phản chứng, hoặc remediation không có verification plan, hệ chưa sẵn sàng tự vận hành production — bất kể dashboard hay model trông thông minh đến đâu.

## Tài liệu liên quan trong handbook

- [06 — Telemetry Data & Feature Plane](../06-data-plane/README.vi.md)
- [09 — Persistent Anomaly Detection](../09-anomaly-detection/README.vi.md)
- [10 — Alert Correlation](../10-alert-correlation/README.vi.md)
- [11 — Root Cause Analysis](../11-root-cause-analysis/README.vi.md)
- [13 — Remediation Safety Engine](../13-remediation-safety-engine/README.vi.md)
- [14 — Production Engine](../14-production-engine/README.vi.md)
- [17 — AIOps Benchmark Replay](../17-aiops-benchmark-replay/README.vi.md)
- [19 — Incident Operations](../19-incident-operations/README.vi.md)
- [20 — Governance & Model Risk](../20-aiops-governance/README.vi.md)

--8<-- "docs/includes/acceptance-footer.vi.md"
