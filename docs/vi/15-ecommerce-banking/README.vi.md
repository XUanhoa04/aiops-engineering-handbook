# Chapter 15 — AIOps Domain Packs: e-commerce, banking và payment

> **Core AIOps engine không nên được viết lại cho từng ngành, nhưng policy, business invariant, seasonality, topology, evidence và remediation boundary phải thay đổi theo domain. Domain Pack là lớp cấu hình về semantics và acceptance: nó nói “healthy” nghĩa là gì, fault nào nguy hiểm, dữ liệu nào được phép dùng và action nào tuyệt đối không tự động.**

---

## 1. Domain Pack là gì?

Một nền tảng AIOps chung có thể detect, correlate, RCA, investigate và remediate. Nhưng cùng một metric có ý nghĩa khác nhau:

- Traffic tăng 4× trong flash sale có thể là thành công của e-commerce.
- Transaction volume giảm trong đêm có thể bình thường ở card acquiring nhưng bất thường ở instant payment.
- Latency thấp không có ý nghĩa nếu ledger ghi sai.
- Payment authorization thành công không chứng minh settlement và reconciliation hoàn tất.

Domain Pack bổ sung các semantics mà engine tổng quát không thể tự suy ra.

### 1.1 Cấu trúc chuẩn của một Domain Pack

| Thành phần | Nội dung |
|---|---|
| Business journeys | Những hành trình khách hàng và money path quan trọng |
| Outcome SLO | Success, latency, correctness, freshness và completeness |
| Regimes | Peak, campaign, cutoff, holiday, batch và maintenance |
| Topology overlays | Critical path, shared dependency, external provider |
| Fault taxonomy | Failure mode đặc thù và cách tách fault |
| Detection policy | Baseline, burn windows, cohort và missing-data rule |
| Correlation/RCA policy | Causal path, negative control và domain priors |
| Remediation boundary | Action auto, human, dual-control hoặc prohibited |
| Data policy | PII, payment data, retention, residency và redaction |
| Domain golden set | Replay scenarios và ground truth |
| Ownership | Business, platform, risk, security và operations |
| Acceptance | Hard gates và thresholds trước rollout |

### 1.2 Core engine và Domain Pack phân quyền ra sao?

Core engine chịu trách nhiệm state, event-time, evidence provenance, scoring, idempotency, verifier và audit. Domain Pack không thay thuật toán engine; nó cung cấp:

- Tên journey và business outcome.
- Threshold/policy theo risk.
- Calendar/regime context.
- Invariant và action class.
- Dataset slice và acceptance gate.

Nếu Domain Pack chứa một bản sao detector hoặc remediation engine riêng, tổ chức sẽ tạo nhiều semantics lệch nhau và không thể benchmark chung.

---

## 2. Bản đồ domain: cái gì dùng chung, cái gì không?

| Trục | E-commerce | Banking | Payment processor/fintech |
|---|---|---|---|
| Availability shape | Peak/campaign cực mạnh | Luôn-on + cutoff/batch | Luôn-on, provider-dependent |
| Correctness | Cart/catalog có thể eventual; order/payment chặt | Ledger/reconciliation tuyệt đối quan trọng | Idempotency, routing và settlement |
| External dependencies | PSP, inventory, shipping | Clearing, core banking, HSM | Nhiều PSP/acquirer/network |
| False positive cost | Page fatigue, bỏ lỡ campaign | Operational risk, change restriction | Route flapping, fee và decline |
| False negative cost | Mất GMV/chuyển đổi | Mất tiền, sai sổ, vi phạm | Mất doanh thu, duplicate charge |
| Safe automation | Cache, stateless capacity, retry policy có guard | Rất hạn chế trên money path | Routing/circuit breaker có quota chặt |
| Data sensitivity | PII, order, address | PII, account, transaction, audit | PAN/token/BIN, transaction metadata |
| Recovery proof | Conversion + order completion | Ledger correctness + reconciliation | Authorization + capture/settlement |

---

## 3. Pack A — E-commerce

### 3.1 Business journeys

E-commerce pack khai báo ít nhất:

1. Browse/search.
2. Product detail và pricing.
3. Add-to-cart.
4. Checkout.
5. Inventory reservation.
6. Payment authorization/capture.
7. Order creation.
8. Fulfillment/webhook.

Không gộp tất cả thành “website availability”. Browse có thể degrade mà checkout vẫn giữ; payment khỏe nhưng order creation lỗi vẫn mất đơn.

### 3.2 Outcome contract

| Journey | Success | Latency | Correctness/completeness |
|---|---|---|---|
| Browse | Page/result trả được | p95 theo region/device | Giá/availability không quá stale |
| Cart | Add/update thành công | p95 | Không mất item/session |
| Checkout | Order intent hoàn tất | p95/p99 | Tổng tiền, promotion đúng |
| Inventory | Reservation thành công | deadline | Không oversell vượt policy |
| Payment | Auth/capture đúng | p95 | Không duplicate charge |
| Fulfillment | Event được xử lý | age/backlog | Không mất/nhân webhook |

### 3.3 Regime catalog

E-commerce có regime thay đổi nhanh:

- Daily/weekly seasonality.
- Flash sale.
- Black Friday, 11.11, Tết.
- Influencer/campaign traffic.
- New-product launch.
- Bot/scraper wave.
- Inventory drop.
- PSP maintenance.

Mỗi regime có expected traffic range, tenant/product cohort, capacity plan, valid time window và owner. Campaign flag không được suppress customer outcome.

### 3.4 Worked case: traffic tăng hợp lệ và overload thật

Lúc 20:00, traffic từ 8.000 lên 30.000 request/phút.

| Tín hiệu | Campaign khỏe | Overload thật |
|---|---:|---:|
| Browse volume | 30.000/min | 30.000/min |
| Checkout success | 98,9% | 86,2% |
| Cart p95 | 310 ms | 2.900 ms |
| Inventory queue age | 12 s | 8 phút |
| DB pool wait | 24 ms | 1.430 ms |
| Campaign context | Hợp lệ | Hợp lệ |

Volume anomaly ở cả hai case không đủ page. Outcome, queue và saturation tách chúng. Campaign khỏe được ghi contextual event; overload page theo checkout journey. Đây là Regime-aware baseline kết hợp Multi-window burn.

### 3.5 Fault taxonomy e-commerce

#### Flash-sale thundering herd

Nhiều client cùng truy cập SKU, cache miss, inventory lock và retry tạo feedback loop. Root không nhất thiết là database; có thể là cache invalidation hoặc retry policy.

Evidence cần:

- Request amplification trên mỗi customer action.
- Cache hit/miss theo SKU cohort.
- Inventory lock/queue.
- DB acquire và query timing.
- Success/count theo SKU.

Không auto scale toàn hệ thống nếu downstream headroom không đủ.

#### Cache stampede

Latency origin tăng ngay sau expiry đồng loạt. Pattern phù hợp là single-flight, jittered expiry hoặc stale-while-revalidate; AIOps action chỉ an toàn nếu có catalog và verifier origin load.

#### Inventory oversell

Success kỹ thuật có thể xanh trong khi business correctness hỏng. Detection phải so reservation, order và stock ledger; remediation không tự sửa stock counts.

#### Webhook retry storm

Provider/client retry nhân event. Metric request rate tăng nhưng unique business event không tăng. Correlation theo idempotency/business key, không theo HTTP count.

#### Partial PSP outage

Chỉ một BIN, payment method hoặc region lỗi. Global success có thể vẫn 97%; cohort affected chỉ 55%. Pack bắt buộc slice theo provider, method, region và BIN range đã bảo vệ privacy.

### 3.6 Correlation và RCA overlay

E-commerce pack ưu tiên journey graph:

- Browse/search symptoms không tự merge với checkout nếu không có shared cause.
- Payment timeout có thể lan tới checkout, inventory release và webhook retry.
- Product campaign deploy chỉ là candidate khi affected cohort khớp.
- External PSP health phải có control theo method/provider.

Business impact weighting dùng lost successful checkouts và affected GMV band, không dùng raw alert count.

### 3.7 Remediation policy e-commerce

| Action | Default tier | Hard guard |
|---|---|---|
| Scale stateless browse/search | Auto-canary có điều kiện | Downstream headroom, cost, sample |
| Enable stale cache | Human/auto-canary theo catalog | Price/inventory freshness |
| Reduce retry | Human-approved canary | Order completion, permanent error |
| Shed bot/non-critical traffic | Auto-canary | Không chặn checkout/customer |
| Shift PSP traffic | Human-approved progressive | Provider capacity, fee, decline |
| Change inventory count | Prohibited autonomous | Business correctness/audit |
| Re-run fulfillment webhook | Human/catalog bounded | Idempotency và duplicate shipment |

### 3.8 E-commerce golden scenarios

1. Flash sale khỏe: không page volume-only.
2. Flash sale overload: page customer journey trong deadline.
3. Cache stampede: RCA cache expiry trước database CPU symptom.
4. Partial PSP outage: cohort detection không bị global average che.
5. Inventory oversell: correctness alert dù latency xanh.
6. Webhook duplication: business event dedup đúng.
7. Retry storm 65 phút: không silent gap.
8. Auth fault nổ chồng: tách incident.

### 3.9 Acceptance E-commerce Pack

- Campaign context không suppress customer-impact SLO.
- Checkout/GMV count được đo cùng success ratio.
- Partial provider/method fault recall đạt ngưỡng theo cohort.
- Duplicate order/charge/shipment guardrail không bao giờ missing-as-zero.
- Action scale/retry/cache có downstream và correctness verification.
- Inventory/data mutation không nằm trong autonomous catalog.

---

## 4. Pack B — Banking

### 4.1 Money path trước infrastructure path

Banking pack bắt đầu từ lifecycle nghiệp vụ:

Initiation → Authentication → Authorization → Posting → Clearing → Settlement → Reconciliation

Một giao dịch có thể trả “accepted” nhưng chưa post ledger, hoặc post nhưng chưa settlement. Availability không thể đại diện correctness/completeness.

### 4.2 Invariants không được thương lượng

- Tổng debit và credit cân bằng theo ledger rule.
- Một business instruction không tạo nhiều economic effect.
- Transaction state tiến theo transition hợp lệ.
- Reconciliation difference nằm trong threshold và deadline.
- Audit chain đầy đủ, không sửa/xóa tùy ý.
- Data residency và access policy được giữ.
- Time/cutoff semantics chính xác.

Nếu invariant fail, hệ thống có thể vẫn trả HTTP 200 nhưng incident severity cao.

### 4.3 Outcome contract banking

| Stage | Availability | Correctness | Timeliness |
|---|---|---|---|
| Initiation | Request accepted | Payload/identity đúng | Response deadline |
| Authorization | Decision trả được | Rule, balance, limit đúng | Network SLA |
| Posting | Ledger entry tạo | Double-entry/invariant | Posting lag |
| Clearing | File/message đầy đủ | Count/amount control total | Cutoff |
| Settlement | Obligation hoàn tất | Amount/currency đúng | Settlement window |
| Reconciliation | Compare hoàn tất | Break được phân loại | End-of-day deadline |

### 4.4 Worked case: authorization xanh, ledger đỏ

| Tín hiệu | 10:00 | 10:20 |
|---|---:|---:|
| Authorization success | 99,3% | 99,1% |
| Posting success | 99,2% | 96,0% |
| Posting lag p95 | 2 s | 11 phút |
| Accepted-but-unposted | 120 | 18.400 |
| Ledger imbalance | 0 | 0 |
| Reconciliation backlog | 300 | 19.100 |

HTTP/auth dashboard gần xanh nhưng money-path completeness đang hỏng. Incident phải page theo accepted-but-unposted và posting lag. Auto retry có thể tạo duplicate economic effect nếu idempotency semantics không chắc; remediation mặc định Human Only.

### 4.5 Fault taxonomy banking

#### Partial posting

Một bên debit/credit hoặc downstream journal chưa hoàn tất. Engine cần transaction-state graph, không chỉ service topology.

#### Ghost transaction

Client timeout nhưng backend đã commit. Retrying từ transport layer có thể duplicate. Evidence phải nối idempotency key, authorization ID, ledger reference và response state.

#### Reconciliation break

Count hoặc amount giữa internal ledger và external network khác nhau. Detection theo control totals và aging bucket; RCA có thể là missing file, duplicate, timezone hoặc mapping.

#### Cutoff/batch failure

Volume thấp ban đêm có thể bình thường; một file không đến trước cutoff là incident dù error rate bằng zero. Pack dùng expected-arrival SLI và deadline state.

#### Clock/timezone error

Timestamp sai có thể làm causal order, interest, cutoff hoặc duplicate window sai. Time sync và business timezone là critical dependency.

#### Fraud-model confounder

Decline tăng có thể do fraud policy đúng sau attack, hoặc model/rule lỗi. Infra engine không được tự tối ưu approval rate mà bỏ risk outcome.

### 4.6 Correlation và RCA overlay banking

Banking cần hai graph:

- Service/dependency graph.
- Transaction-state/money-flow graph.

Một queue delay sau authorization có thể không gây HTTP error upstream nhưng tạo posting lag. RCA weighting ưu tiên first invalid state transition và control-total divergence. Change correlation gồm rule, limit, HSM key, calendar, file mapping và reference data, không chỉ application deploy.

### 4.7 Detection policy banking

- Burn-rate cho availability/latency.
- Deadline/expected-arrival cho batch/file.
- Invariant detector cho ledger/reconciliation.
- Cohort detector theo channel, product, currency, region và network.
- Volume floor và denominator guard.
- Calendar-aware baseline với holiday/cutoff.
- Data-quality incident khi lineage hoặc control totals thiếu.

### 4.8 Remediation boundary banking

| Action | Default |
|---|---|
| Restart stateless channel instance | Human-approved canary hoặc auto-canary đã chứng minh |
| Scale read-only API | Auto-canary với downstream guard |
| Reduce transport retry | Human-approved, cần idempotency evidence |
| Requeue transaction | Dual control, per-transaction audit |
| Modify ledger entry | Prohibited autonomous |
| Change fraud/limit rule | Dual control + model/risk owner |
| Rotate HSM/root key | Dual control/break-glass procedure |
| Re-run settlement file | Dual control + control totals |

### 4.9 Audit và evidence

Audit phải tái dựng:

- Incident revision và evidence tại thời điểm quyết định.
- Người/máy đề xuất, policy và approval.
- Transaction population bị ảnh hưởng, đã token hóa.
- Action target, desired state và outcome.
- Reconciliation trước/sau.
- External communication và regulator escalation nếu có.

Không đưa PAN/account raw vào LLM hoặc general incident store.

### 4.10 Banking golden scenarios

1. Accepted-but-unposted tăng trong khi API success xanh.
2. Duplicate transport delivery nhưng một economic effect.
3. Missing settlement file trước cutoff.
4. Partial currency/region outage bị global average che.
5. Fraud attack làm decline tăng hợp lệ.
6. Fraud rule lỗi làm decline tăng sai.
7. Clock skew đảo transaction-state timeline.
8. Audit/verifier hỏng: remediation chuyển Detection Only.
9. Rollback action fail: dual escalation và immutable state.

### 4.11 Acceptance Banking Pack

- Mọi critical journey có availability, correctness, completeness và timeliness SLI.
- Money invariant là hard gate, không bị score trung bình bù.
- Reconciliation và expected-arrival được xem first-class telemetry.
- Transaction-state graph tham gia RCA.
- Data/ledger mutation không autonomous.
- Dual-control và audit reconstruction pass 100% golden scenarios.
- Missing evidence không bao giờ được coi là zero financial harm.

---

## 5. Pack C — Payment processor và fintech

Payment processor nằm giữa merchant, network, acquirer, issuer và ledger. Domain này kết hợp peak e-commerce với correctness banking và phụ thuộc external provider.

### 5.1 Journeys

- Tokenization.
- Authorization.
- Capture.
- Void/refund.
- Routing/failover.
- Dispute/chargeback.
- Merchant webhook.
- Settlement/reconciliation.

### 5.2 Idempotency là business invariant

Exactly-once transport hiếm khi có; mục tiêu là một economic effect cho một business intent. Pack khai báo:

- Idempotency key scope và TTL.
- State transition hợp lệ.
- Duplicate response semantics.
- Provider reference mapping.
- Recovery khi client timeout sau commit.

### 5.3 Worked case: partial PSP outage

| Cohort | Volume | Success trước | Success lúc lỗi |
|---|---:|---:|---:|
| PSP-A Visa region A | 42% | 98,7% | 51,0% |
| PSP-A Mastercard | 18% | 98,5% | 97,9% |
| PSP-B Visa | 25% | 98,2% | 97,8% |
| Các cohort khác | 15% | 98,6% | 98,3% |
| Global | 100% | 98,6% | 78,7% |

Global đã đủ đỏ trong ví dụ này, nhưng fault partition vẫn cần Visa/region/provider để route đúng. Với cohort chỉ 5% volume, global có thể vẫn trên SLO trong khi merchant cụ thể chịu outage nặng.

### 5.4 Smart routing không phải remediation đơn giản

Shift PSP có forces:

- Provider B còn capacity không?
- Approval/decline mix có tương đương?
- Fee và currency support?
- Token/vault compatibility?
- Fraud signal hoặc regulatory routing?
- Settlement/reconciliation downstream?

Canary route 5% affected cohort, không 5% toàn traffic. Verify authorization outcome, latency, decline reason, duplicate charge và settlement reference.

### 5.5 Fault taxonomy payment

- Provider partial outage theo BIN/method/region.
- Timeout sau commit tạo unknown state.
- Retry amplification.
- Webhook duplicate/out-of-order.
- Token vault/HSM latency.
- Fraud false-positive wave.
- Routing oscillation/flapping.
- Capture/settlement lag sau auth recovery.

### 5.6 Remediation policy payment

| Action | Policy |
|---|---|
| Shift small affected cohort | Human-approved canary; route budget |
| Open circuit cho failing provider | Có fallback và correctness guard |
| Reduce retry | Có idempotency/unknown-state handling |
| Replay webhook | Per-event idempotency và merchant rate limit |
| Replay unknown payment | Không autonomous nếu commit state chưa xác định |
| Change fraud threshold | Risk owner + dual control |
| Change settlement data | Prohibited autonomous |

### 5.7 Payment golden scenarios

1. Cohort 3% lỗi, global vẫn xanh.
2. Provider timeout sau commit.
3. Route shift làm provider B bão hòa.
4. Circuit breaker flapping.
5. Authorization hồi nhưng capture backlog tăng.
6. Webhook duplicate/out-of-order.
7. Fraud attack và fraud-model regression có cùng decline symptom.

### 5.8 Acceptance Payment Pack

- Detection slice theo provider/method/region/merchant tier với privacy guard.
- Unknown transaction state không auto-retry mù.
- Routing action có capacity, fee, decline và settlement verification.
- Authorization recovery không đóng incident khi capture/settlement còn backlog.
- Idempotency/economic-effect oracle pass toàn bộ replay duplication.

---

## 6. Cross-domain overlays

### 6.1 Data classification

| Class | Ví dụ | Xử lý |
|---|---|---|
| Public operational | Service health aggregate | Có thể vào incident brief |
| Internal | Topology, config revision | Access theo team |
| Sensitive PII | Email, address, account metadata | Redact/tokenize |
| Payment restricted | PAN, CVV, secrets, raw account | Không vào LLM/general logs |
| Audit evidence | Decision/action record | Append-only, retention policy |

### 6.2 External dependency overlay

External provider cần:

- Provider status nhưng không coi đó là source duy nhất.
- Synthetic/control request.
- Contract/SLA và escalation path.
- Cohort mapping.
- Rate/capacity/fee constraint.
- Failover eligibility.
- Evidence khi provider status page trễ.

### 6.3 Change calendar overlay

Domain calendar gồm campaign, holiday, payroll, market open/close, clearing cutoff, provider maintenance và internal freeze. Calendar là context, không phải suppression blanket.

### 6.4 Ownership overlay

Một incident money path có business owner, service owner, platform on-call, risk/fraud, security và settlement/reconciliation owner. Domain Pack định nghĩa ai có quyền approve action class nào.

---

## 7. Domain Pack inheritance và override

Một tổ chức có marketplace + wallet có thể ghép:

- Core AIOps contract.
- E-commerce pack cho browse/cart/order.
- Payment pack cho authorization/routing.
- Banking overlay cho wallet ledger/reconciliation.

Override phải rõ mức ưu tiên. Ví dụ e-commerce cho phép auto replay webhook, nhưng payment overlay cấm nếu unknown economic state; policy nghiêm hơn thắng.

Không copy nguyên pack rồi sửa riêng vì sẽ drift. Dùng version, owner và conformance replay.

---

## 8. Domain intake trước khi bật AIOps

### Business

- Journey nào tạo/mất tiền?
- Correctness quan trọng hơn availability ở đâu?
- Partial success nghĩa là gì?
- Cutoff/deadline nào không thể bù sau?

### Data

- Business key nào nối telemetry mà không lộ PII?
- Source of truth cho outcome/correctness?
- Dữ liệu đến trễ bao lâu?
- Retention/residency ra sao?

### Topology

- Critical path và shared dependency?
- External provider và async boundary?
- Transaction-state graph có ở đâu?

### Operations

- Incident owner và escalation?
- Action nào đã có rollback reliability?
- Dual-control/freeze?
- Manual change được quan sát thế nào?

### Benchmark

- Incident lịch sử nào đại diện?
- Negative control hợp lệ?
- Fault chồng và telemetry loss?
- Ground truth có đủ causal mechanism?

Không trả lời được các câu này thì chỉ nên chạy observe/shadow.

---

## 9. Domain Pack lifecycle

### Draft

Domain owner và platform xác định journey, invariant, cohort và action boundary.

### Replay

Chạy golden scenarios trên core engine. Hard invariant fail thì không được bù bằng điểm detection/RCA cao.

### Shadow

Domain policy tạo decision song song với vận hành hiện tại. So false page, missed cohort, RCA và action eligibility.

### Canary

Bật cho một journey/service/tenant không phải bằng cách bỏ risk, mà giới hạn blast radius.

### Active

Pack có owner, version, telemetry contract, benchmark score và expiry/review date.

### Retired

Khi journey, provider, regulation hoặc data semantics đổi, pack cũ không được âm thầm dùng tiếp.

---

## 10. Domain Pack acceptance scorecard

| Cổng | E-commerce | Banking | Payment |
|---|---|---|---|
| Customer journey coverage | Browse→fulfillment | Initiation→reconciliation | Auth→settlement |
| Correctness invariant | Price/order/inventory | Ledger/control totals | Economic effect/idempotency |
| Regime coverage | Campaign/peak | Cutoff/holiday/batch | Provider/market/peak |
| Partial-fault slices | SKU/region/PSP | Product/channel/currency | Provider/BIN/method/merchant |
| Missing-data behavior | Không suppress impact | Không coi missing là zero break | Không auto-retry unknown state |
| Remediation boundary | Data mutation cấm | Ledger/risk dual control | Route bounded, settlement protected |
| Golden replay | Peak, stampede, oversell | Posting, reconcile, cutoff | Partial PSP, timeout-after-commit |

Mỗi pack phải điền đầy đủ [Acceptance Template chung](../acceptance-template.vi.md), có owner và evidence artifact. “Đã review tài liệu” không thay replay result.

---

## 11. Anti-patterns domain

### Một SLO global cho mọi journey

Browse volume lớn che checkout lỗi; authorization xanh che posting lag.

### Infra metric thay business outcome

CPU/latency khỏe không chứng minh order, ledger hoặc settlement đúng.

### Calendar suppress mọi alert

Peak hợp lệ vẫn có thể overload thật.

### Tự động hóa theo tên action

“Retry” an toàn ở read API nhưng nguy hiểm với unknown payment commit.

### Global average

Provider/BIN/tenant nhỏ có thể bị outage mà aggregate xanh.

### Domain logic trong prompt

Invariant và policy không được chỉ tồn tại trong văn bản cho LLM; phải là input deterministic của engine.

### Copy pack mà không version

Policy drift khiến cùng action có nghĩa khác giữa team và không benchmark được.

---

## Kết luận

Domain Pack là cầu nối giữa engine kỹ thuật và hậu quả nghiệp vụ. Nó không làm core engine phức tạp hơn bằng code riêng; nó làm semantics rõ hơn:

- E-commerce phân biệt traffic thành công với overload, bảo vệ conversion, inventory và order correctness.
- Banking đặt ledger, reconciliation, deadline và dual control cao hơn metric hạ tầng.
- Payment processor tách partial provider cohort, unknown commit state, routing capacity và economic idempotency.

Pattern chỉ được coi là áp dụng thành công khi Domain Pack có golden replay và hard gates. Chapter 16 biến chính các scenarios này thành benchmark chạy lặp lại cho mọi thay đổi của AIOps engine.

## Đọc tiếp

- [14 — Pattern Library](../14-bigtech-aiops/README.vi.md)
- [16 — Benchmark Replay](../16-famous-incidents/README.vi.md)
- [Acceptance Template chung](../acceptance-template.vi.md)

--8<-- "docs/includes/acceptance-footer.vi.md"
