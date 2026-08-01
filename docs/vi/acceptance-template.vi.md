# Acceptance Template chung cho AIOps Engineering Handbook

> **Mọi capability trong handbook chỉ được coi là hoàn tất khi có một contract kiểm chứng được: scope rõ, input có chất lượng, scenario có timeline, output có schema, hard gate không thể bù, metric có threshold và evidence artifact tái tạo được. “Đã cài”, “dashboard xanh” hoặc “demo chạy” không phải acceptance.**

---

## 1. Vì sao toàn sách cần một template chung?

Nếu mỗi chapter dùng một kiểu checklist, đội kỹ thuật gặp ba vấn đề:

- “Pass” ở Data Plane có thể chỉ nghĩa message tới Kafka, trong khi Detection cần event-time và provenance.
- “RCA accuracy cao” có thể bỏ qua concurrent fault hoặc telemetry thiếu.
- “Remediation thành công” có thể chỉ nhìn metric target, không nhìn customer outcome và harm.

Template chung tạo ngôn ngữ xuyên pipeline. Output của chapter trước trở thành input kiểm chứng được của chapter sau; một hard safety violation không bị điểm tổng che.

---

## 2. Năm nguyên tắc không thương lượng

### 2.1 Outcome trước component

Đo lời hứa với khách hàng/on-call trước uptime của tool. Collector, Kafka và model đều xanh không chứng minh incident được page đúng.

### 2.2 Timeline trước snapshot

AIOps xử lý lifecycle. Acceptance phải có event-time, duration, transition, dữ liệu trễ và recovery; một ảnh dashboard không đủ.

### 2.3 Negative control trước kết luận

Mỗi scenario dương cần control hoặc confounder: campaign khỏe, deploy vô tội, service dùng cùng dependency nhưng không lỗi. Không có negative control, engine có thể luôn page và luôn tìm “root cause”.

### 2.4 Hard gate trước weighted score

Data leakage, unauthorized action, missing-as-recovery và duplicate economic effect là fail tuyệt đối. Không dùng accuracy cao để bù.

### 2.5 Evidence trước lời khẳng định

Mọi verdict lưu artifact, version và query/output đủ để tái tạo. “Team đã kiểm tra” không phải evidence.

---

## 3. Acceptance Card một trang

Mỗi capability/change điền các trường sau.

| Trường | Nội dung cần ghi |
|---|---|
| Capability | Hành vi cụ thể đang được chấp nhận |
| Decision owner | Người chịu trách nhiệm cho go/no-go |
| Scope | Service, tenant, region, journey, environment |
| Out of scope | Điều chưa được chứng minh |
| User outcome | Khách hàng/on-call nhận giá trị gì |
| Inputs | Signal, schema, source, freshness và coverage |
| Preconditions | State/topology/policy phải đúng trước test |
| Scenario set | Positive, negative, edge và degraded cases |
| Fault timeline | Trigger, propagation, duration, recovery |
| Expected outputs | Event/decision/lifecycle theo deadline |
| Ground truth | Cause, impact, cohort, uncertainty, safe action |
| Metrics | Công thức, denominator, window và slices |
| Hard gates | Điều xảy ra một lần cũng fail |
| Thresholds | Mức pass và lý do |
| Evidence artifacts | File/report/event chain lưu ở đâu |
| Reproducibility | Version/seed/environment để chạy lại |
| Rollback | Nếu rollout fail thì trở lại thế nào |
| Expiry | Khi nào acceptance không còn hiệu lực |
| Verdict | Pass, Conditional, Shadow Only hoặc Fail |

### 3.1 Capability phải là hành vi

Không viết “triển khai Prometheus”. Viết “customer-impact SLO được tính đúng khi counter reset, traffic giảm và một shard mất scrape”.

### 3.2 Out of scope bắt buộc

Nếu chỉ benchmark stateless service, không được suy rộng sang ledger. Out of scope giúp ngăn một pass nhỏ biến thành quyền tự động hóa rộng.

---

## 4. Scenario Template

### Identity

- Scenario ID và version.
- Owner/reviewer.
- Domain pack và service tier.
- Created/reviewed/expiry date.

### System model

- Customer journey.
- Services/dependencies/shared resource.
- Traffic/cohort model.
- Initial baseline, topology và engine versions.

### Fault model

- Trigger và causal mechanism.
- Start/end theo event-time.
- Propagation path.
- Affected/unaffected cohort.
- Legitimate change/confounder.

### Delivery model

- Event loss.
- Delay/reorder.
- Duplicate.
- Clock skew.
- Sampling/coverage change.

### Expected lifecycle

- Khi nào detector Pending/Firing/Recovered.
- Incident merge/split relation.
- RCA ranking theo phase.
- Investigation confidence/abstention.
- Action eligibility/lifecycle.
- Degraded mode/recovery state.

### Oracle

- Fact nào đúng tại từng thời điểm.
- Fact nào chưa thể biết.
- Safe/dangerous action.
- Customer recovery criteria.

---

## 5. Input Quality Contract

Mỗi input cần:

| Thuộc tính | Acceptance question |
|---|---|
| Identity | Source/service/tenant có xác định không? |
| Schema | Version và semantic có rõ không? |
| Event-time | Có clock/skew state không? |
| Freshness | Quyết định còn dùng được không? |
| Coverage | Bao nhiêu population được quan sát? |
| Provenance | Có tái tạo fact không? |
| Cardinality | Có nằm trong budget không? |
| Privacy | PII/secret đã redact không? |
| Missingness | Source mất được biểu diễn hay biến thành zero? |
| Ownership | Ai sửa khi contract hỏng? |

Không pass input contract thì capability downstream phải degrade, không âm thầm tiếp tục với confidence cũ.

---

## 6. Output Quality Contract

Output phải có:

- Stable identity và revision.
- Event-time và processing-time.
- Scope/cohort.
- Decision/state transition.
- Confidence đã calibration nếu có.
- Evidence provenance.
- Reason/contradiction.
- Policy/model/rule/topology version.
- Expiry/TTL nếu output dùng cho action.
- Idempotency/dedup identity.

Văn bản tự do có thể là presentation layer; không được là output contract duy nhất.

---

## 7. Bộ scenario tối thiểu cho mọi capability

### Positive

Failure thật mà capability phải phát hiện/xử lý.

### Negative control

Tín hiệu giống failure nhưng customer outcome khỏe: campaign, deploy vô tội, high utilization hợp lệ.

### Long duration

Incident kéo dài đủ lâu để lộ baseline drift, TTL, state loss và alert fatigue.

### Concurrent fault

Fault B nổ khi A chưa resolve.

### Partial/cohort fault

Global aggregate có thể khỏe nhưng slice nhỏ lỗi nặng.

### Missing/degraded data

Mất một signal, lag, duplicate, reorder hoặc schema mismatch.

### Restart/recovery

Worker/state dependency restart giữa lifecycle.

### Adversarial

Prompt/data injection, cardinality abuse, cross-tenant request hoặc stale action.

### Rollback/failure of the capability

Chính detector/model/executor/verifier hỏng.

Không phải chapter nào cũng thực thi action, nhưng mọi chapter phải có failure-of-the-capability scenario.

---

## 8. Metrics Template

Mỗi metric ghi rõ:

- Tên và mục đích.
- Numerator/denominator.
- Event-time window.
- Population/cohort.
- Missing-data behavior.
- Threshold.
- Slice bắt buộc.
- Trade-off metric.

Ví dụ precision-at-page phải đi cùng recall-at-deadline. Giảm page bằng cách suppress tất cả có precision không có nghĩa.

### Metrics xuyên pipeline

| Stage | Primary metrics | Guard metrics |
|---|---|---|
| Telemetry | Coverage, freshness, causal continuity | Cost, cardinality, privacy |
| Data plane | Loss, duplicate, lag, replay | Ordering, schema, RPO |
| Detection | Recall-at-deadline, precision-at-page | Silent gap, recovery precision |
| Correlation | False merge/split, compression | Concurrent-fault recall |
| RCA | Top-k, time-to-candidate | Calibration, contradiction recall |
| Investigation | Fact precision, provenance | Query budget, abstention quality |
| Remediation | Time-to-safe-mitigation | Harm, false success, rollback |
| Production | End-to-end SLO, convergence | Degraded-mode correctness |

---

## 9. Hard Gate Template

Hard gates chung:

- Không cross-tenant leakage.
- Không secret/PII xuất hiện ngoài policy.
- Không unauthorized/freeform action.
- Không stale action execution.
- Không missing telemetry bị coi recovery.
- Không duplicate production/economic effect.
- Không làm mất incident active qua restart.
- Không bỏ fault concurrent critical.
- Không tuyên bố success khi customer outcome chưa đạt.
- Mọi action có audit chain tái dựng được.

Domain Pack thêm hard gate riêng: ledger balance, inventory correctness, settlement completeness hoặc data residency.

---

## 10. Threshold và verdict

### Pass

Mọi hard gate pass; primary/guard metrics đạt trên tất cả mandatory slices; evidence và reproducibility đầy đủ.

### Conditional

Hard gates pass nhưng một non-critical slice hoặc performance target chưa đạt. Rollout chỉ trong scope đã chứng minh, có expiry và owner.

### Shadow Only

Capability có ích để quan sát nhưng chưa đủ calibration/safety để tác động decision hoặc production.

### Fail

Bất kỳ hard gate fail, evidence không tái tạo được hoặc regression so incumbent vượt tolerance.

Không dùng “pass with known hard safety issue”.

---

## 11. Evidence Pack Template

Mỗi acceptance run xuất một evidence pack:

1. Acceptance Card đã điền.
2. Scenario/version/seed.
3. Engine và dependency artifact versions.
4. Input quality summary.
5. Decision timeline.
6. Metric/hard-gate report theo slice.
7. Diff với incumbent.
8. Failure drill-down.
9. Audit/provenance links.
10. Reviewer verdict và expiry.

Evidence pack là immutable snapshot. Dashboard live có thể thay đổi và không thay thế artifact.

---

## 12. Chapter Acceptance Matrix

| Chapter | Capability phải chứng minh | Scenario bắt buộc | Evidence chính |
|---|---|---|---|
| 00 Introduction | Luồng end-to-end và boundary đúng | Payment 65 phút + auth chồng | Stage contract và verdict |
| 01 Observability | Question → signal → decision | Customer impact vs infra-only | SLI coverage map |
| 02 OpenTelemetry | Causal context liên tục | Orphan spans, sampling loss, skew | Trace coverage/provenance |
| 03 Prometheus | SLO/metric semantics đúng | Counter reset, missing shard, volume drop | Query result + denominator |
| 04 Loki | Log signature hữu dụng/an toàn | Duplicate, rate limit, PII | Signature/coverage/redaction |
| 05 Tempo | Trace path và error propagation | Partial sampling, async boundary | Span path/cohort comparison |
| 06 Data Plane | Event contract bền | Late, duplicate, schema evolution | Loss/lag/replay report |
| 07 Kafka | Transport không làm mất semantics | Lag, rebalance, DLQ, restart | Offset/watermark/convergence |
| 17 Topology & Change | Graph/change fresh và có ownership | Missing edge, stale graph, innocent deploy | Graph revision/coverage |
| 08 Anomaly Detection | Detect dài hạn không nhiễu | Freeze baseline, regime shift | Recall/silent gap/precision |
| 09 Alert Correlation | Nén storm, giữ fault mới | Duplicate + concurrent fault | False merge/split/member trail |
| 10 RCA | Rank cause, loại correlation | Temporal confounder, missing trace | Top-k/calibration/evidence |
| 11 Investigation | Fact/hypothesis có kỷ luật | Contradiction, injection, abstain | Ledger/provenance/query trace |
| 12 Remediation | Action giới hạn và verified | Stale, duplicate, false recovery, rollback fail | Action/audit/verification chain |
| 13 Production | AIOps tự degrade/recover | Dependency loss + state restart | Mode transition/convergence |
| 14 Pattern Library | Pattern có context và do-not-use | Pattern composition/failure | Pattern card acceptance |
| 15 Domain Packs | Domain invariant được giữ | Peak, ledger, partial PSP | Domain conformance report |
| 16 Benchmark Replay | Regression chạy lặp lại | Full mandatory suite | Reproducible benchmark pack |

Matrix là minimum. Chapter hoặc domain có thể thêm scenario nhưng không được bỏ hard gates chung.

---

## 13. Cách dùng template khi viết chapter

Mỗi claim quan trọng nên dẫn đến một acceptance statement:

- Claim: “Freeze baseline ngăn detector tự nuốt anomaly.”
- Scenario: incident error rate 65 phút, daily load vẫn đổi.
- Expected: alert Firing liên tục, baseline đúng scope không trôi.
- Metric: silent-gap duration và false page ở control.
- Hard gate: missing window không được tạo recovery.
- Evidence: incident timeline + baseline revisions.

Nếu không viết được scenario và expected output, claim đang quá mơ hồ.

---

## 14. Cách dùng template khi review PR

Reviewer hỏi theo thứ tự:

1. Capability/decision nào thay đổi?
2. Scenario nào có thể regression?
3. Ground truth có hindsight leakage không?
4. Negative control và missing-data case có chưa?
5. Hard gate nào liên quan?
6. Metric có denominator/window/slice rõ không?
7. Candidate so với incumbent thế nào?
8. Evidence pack có tái tạo được không?
9. Rollout scope có vượt acceptance scope không?
10. Expiry/review owner là ai?

Không review chỉ bằng diff code hoặc ảnh dashboard.

---

## 15. Cách dùng template sau incident

Postmortem chuyển bài học thành benchmark:

- Failure mechanism mới → scenario mới.
- Detector im lặng → long-duration/missing case.
- Correlation merge sai → fault partition ground truth.
- RCA đổ lỗi deploy vô tội → negative control.
- Action làm hại → hard gate/guardrail.
- Recovery mất state → convergence scenario.

Action item “cải thiện monitoring” không hoàn tất cho tới khi scenario mới fail trên incumbent, pass trên candidate và được đưa vào regression suite.

---

## 16. Definition of Done toàn sách

Một chapter/capability chỉ đạt chuẩn production khi:

- Giải thích vấn đề bằng failure thật, không chỉ lợi ích.
- Có input semantics và quality contract.
- Có decision/lifecycle rõ.
- Có dãy số hoặc timeline worked example.
- Nêu khi nào không dùng.
- Nêu failure mode của chính giải pháp.
- Có positive, negative, long, concurrent và degraded scenario phù hợp.
- Có outcome metric và trade-off metric.
- Có hard gate.
- Có evidence pack và reproducibility.
- Có owner, scope và expiry.
- Có rollout/rollback hoặc handoff boundary.

Đây là chuẩn chung cho toàn bộ handbook, không phụ thuộc implementation hay vendor.

---

## Kết luận

Acceptance Template biến toàn bộ sách từ nội dung “nên làm gì” thành hệ thống “chứng minh đã làm đúng”. Nó nối telemetry quality tới detection, incident state tới RCA, evidence tới action và production recovery tới benchmark.

Khi một capability pass template, người review biết chính xác phạm vi nào đã được chứng minh, artifact nào tái tạo được và điều gì vẫn ngoài scope. Khi fail, đội biết failure nằm ở input, decision, safety hay recovery — thay vì tranh luận bằng cảm giác.

## Liên kết nhanh

- [14 — Pattern Library](14-aiops-pattern-library/README.vi.md)
- [15 — Domain Packs](15-aiops-domain-packs/README.vi.md)
- [16 — Benchmark Replay](16-aiops-benchmark-replay/README.vi.md)
- [13 — Production Engine](13-production-engine/README.vi.md)
