# Chapter 11 — Automated Remediation

> **Khắc phục tự động (Automated remediation) là lớp thực thi hành động để khép kín chu trình xử lý sự cố. Nó chuyển hóa các chẩn đoán RCA và đề xuất của LLM thành các hành động an toàn, có thể kiểm toán, và có thể đảo ngược trên hạ tầng production. Thử thách kỹ thuật cốt lõi ở đây không phải là "chúng ta có thể tự động hóa việc này không?" mà là "làm sao để tự động hóa một cách an toàn mà không làm sự cố tồi tệ hơn?".**

---

## Prerequisites

- [09 — Root Cause Analysis](../09-root-cause-analysis/README.vi.md) — sinh ra các tín hiệu kích hoạt khắc phục sự cố; **RCA sai → action sai**
- [10 — LLM Agent](../10-llm-agent/README.vi.md) — đề xuất hành động; **không bao giờ freeform shell**
- [06 — Kafka](../06-kafka/README.vi.md) — lớp vận chuyển cho tín hiệu kích hoạt và kết quả khắc phục

## Related Documents

- [03 — Prometheus](../03-prometheus/README.vi.md) — xác thực kết quả khắc phục qua metrics (verification loop)
- [12 — Production Operations](../12-production/README.vi.md) — runbook, GitOps, chaos, change freeze
- [14 — E-commerce & Banking](../14-ecommerce-banking/README.vi.md) — dual-control, audit log cho regulator
- [15 — Famous Incidents](../15-famous-incidents/README.vi.md) — bài học S3, thundering herd, cascade failure

## Next Reading

Sau chương này, hãy chuyển sang [12 — Production Operations](../12-production/README.vi.md), rồi [14 — E-commerce & Banking](../14-ecommerce-banking/README.vi.md) và [15 — Famous Incidents](../15-famous-incidents/README.vi.md).

---

## Table of Contents

1. [Why Automated Remediation?](#1-why-automated-remediation)
2. [Remediation Architecture](#2-remediation-architecture)
3. [Remediation Action Catalog](#3-remediation-action-catalog)
4. [Kubernetes-Based Remediation](#4-kubernetes-based-remediation)
5. [AWS SSM Automation](#5-aws-ssm-automation)
6. [Safety Framework](#6-safety-framework)
7. [Blast Radius Calculation](#7-blast-radius-calculation)
8. [Rollback Design](#8-rollback-design)
9. [Canary-Based Remediation](#9-canary-based-remediation)
10. [GitOps Remediation](#10-gitops-remediation)
11. [Verification Pipeline](#11-verification-pipeline)
12. [Audit Logging](#12-audit-logging)
13. [Production Configuration](#13-production-configuration)
14. [Common Mistakes](#14-common-mistakes)
15. [Monitoring Remediation](#15-monitoring-remediation)
16. [Scaling](#16-scaling)
17. [Security](#17-security)
18. [Cost](#18-cost)
19. [Risk Decision Matrix](#19-risk-decision-matrix)
20. [Circuit Breakers, Rate Limits & Dual-Control](#20-circuit-breakers-rate-limits--dual-control)
21. [Runbook-as-Code vs LLM Freeform](#21-runbook-as-code-vs-llm-freeform)
22. [Human Approval UX (On-Call 3am)](#22-human-approval-ux-on-call-3am)
23. [Edge Cases: Retry Storms & Wrong RCA](#23-edge-cases-retry-storms--wrong-rca)
24. [Chaos Testing of Remediation](#24-chaos-testing-of-remediation)
25. [Case Studies — Famous Incidents](#25-case-studies--famous-incidents)
26. [Production Checklist (40+)](#26-production-checklist-40)
27. [Production Review](#27-production-review)

---

## 1. Why Automated Remediation?

![Remediation Safety Pipeline](../../assets/diagrams/05-remediation-safety.png)

*Poster: confidence / risk gates → allow-listed executors → verify + circuit breaker + audit.*

### MTTR Economics

```
MTTR thủ công (thông thường): 45-90 phút
MTTR tự động (thông thường): 3-10 phút
Hiệu quả: nhanh hơn 10-15 lần

Chi phí downtime (thương mại điện tử, quy mô vừa): $5,000/phút
Số lượng sự cố hàng tháng (P1/P2): ~20

Thực hiện thủ công: 20 × 60 phút × $5,000 = $6,000,000/tháng
Thực hiện tự động: 20 × 5 phút × $5,000 = $500,000/tháng
Tiết kiệm: $5,500,000/tháng (mức tối đa lý thuyết)

Thực tế (30% số sự cố có thể tự động khắc phục): Tiết kiệm $1,650,000/tháng
```

> [!NOTE]
> **Ý TƯỞNG — MTTR ≠ rủi ro**
> Giảm MTTR bằng automation chỉ có giá trị khi **sai lầm cũng bị giới hạn**. Một hành động sai trong 3 giây có thể đắt hơn 90 phút điều tra thủ công. Luôn đo song song: *success rate*, *rollback rate*, *blast radius realized*, không chỉ *time-to-action*.

### The Automation Paradox & Ironies of Automation (Bainbridge)

Tự động hóa càng nhiều thì rủi ro tiềm ẩn càng lớn:

```
Không có tự động hóa: Con người có thể mắc lỗi, nhưng hiểu rõ hậu quả hành động
Có tự động hóa:      Thực thi nhanh hơn, nhưng lỗi lan rộng cũng nhanh hơn
                     Vấn đề "Thundering herd tự động khắc phục":
                     Tất cả 50 services đồng loạt restart khiến sự cố tồi tệ hơn
```

**Lisanne Bainbridge (1983) — *Ironies of Automation*** vẫn đúng với AIOps remediation:

| Irony | Ý nghĩa vận hành | Hệ quả cho remediation |
|-------|------------------|------------------------|
| Irony 1 | Automation lấy đi công việc “dễ”, để lại công việc khó cho con người | On-call 3am phải phê duyệt action hiếm, phức tạp, ít “cơ bắp trí nhớ” |
| Irony 2 | Con người kém giám sát passive system lâu dài | Dashboard xanh ≠ an toàn; cần active verification loop |
| Irony 3 | Khi automation fail, skill operator đã teo | Runbook-as-code + drills bắt buộc; không chỉ LLM gợi ý |
| Irony 4 | Automation che giấu trạng thái hệ thống | Mọi action phải emit audit + metric + “why this action” |

```
Mức độ automation ↑
  ├─ Skill on-call ↓ (ít thực hành tay)
  ├─ Tốc độ lỗi ↑ (máy không “do dự”)
  ├─ Phụ thuộc correctness của RCA/LLM ↑
  └─ Chi phí một false-positive action ↑↑
```

> [!WARNING]
> **Paradox cốt lõi**
> Hệ thống remediation “thông minh” nhất thường là hệ thống **từ chối hành động** nhiều nhất. Auto-remediate 100% alert là anti-pattern. Mục tiêu production: *high confidence subset* + *fail-closed gates*.

> [!TIP]
> **Nguyên tắc thiết kế**
> 1) Bắt đầu 100% reversible + whitelist hẹp. 2) Đo rollback rate 30–90 ngày. 3) Chỉ nới tier khi rollback < ngưỡng (ví dụ <5%) **và** không có SEV-1 do remediation. 4) Dual-control cho mọi action “không hoàn toàn reversible”.

**Nguyên tắc**: Tự động hóa một cách thận trọng. Bắt đầu với các hành động an toàn 100% (chỉ đọc + có thể đảo ngược). Chỉ bổ sung các hành động rủi ro hơn sau nhiều tháng xác thực thành công. Chi tiết ma trận quyết định: [§19 Risk Decision Matrix](#19-risk-decision-matrix).

### Decision Mindset (trước khi bấm “Execute”)

```
1. Reversible bao lâu?  2. Blast radius nếu sai?
3. Confidence + evidence độc lập?  4. Compliance / freeze / dual-control?
5. Biết fix work thế nào (metric, window, metastable)?
6. Risk retry storm / capacity cliff?
```

Cross-link: [09 — RCA](../09-root-cause-analysis/README.vi.md) · [10 — LLM](../10-llm-agent/README.vi.md) · [15 — Incidents](../15-famous-incidents/README.vi.md).

---

## 2. Remediation Architecture

```mermaid
flowchart TD
    subgraph Trigger["Triggers"]
        KAFKA[Kafka: aiops-rca-results\nLLM recommended action]
        WEBHOOK[Slack Approval Webhook\nhuman-approved action]
        RULE[Rule Engine\nstateless pattern rules]
    end

    subgraph Engine["Remediation Engine"]
        PARSE[Action Parser\nvalidate schema]
        GATE[Safety Gate\nblast radius + whitelist]
        
        subgraph Execution["Execution Layer"]
            K8S[Kubernetes Executor\nkubectl wrapper]
            SSM[AWS SSM Executor\nSSM Automation]
            GITOPS[GitOps Executor\nPR to config repo]
        end
        
        VERIFY[Verification Agent\ncheck metrics post-action]
        ROLLBACK[Rollback Handler\nauto-revert on failure]
    end

    subgraph Storage["State"]
        AUDIT[Audit Log\nDynamoDB / Postgres]
        STATE[Action State\nRedis]
        HISTORY[Remediation History\nfor pattern matching]
    end

    subgraph Output["Output"]
        RESULT[Kafka: aiops-remediation-results]
        NOTIFY[Slack Notification\nsuccess / failure]
        PROM[Prometheus metrics]
    end

    Trigger --> PARSE --> GATE
    GATE -->|approved| Execution
    GATE -->|blocked| NOTIFY
    Execution --> VERIFY
    VERIFY -->|success| RESULT
    VERIFY -->|failed| ROLLBACK
    ROLLBACK --> RESULT
    Execution --> AUDIT
    AUDIT --> HISTORY

    style Trigger fill:#1565c0,color:#fff
    style Engine fill:#4a148c,color:#fff
    style Storage fill:#2e7d32,color:#fff
    style Output fill:#e65100,color:#fff
```

> [!NOTE]
> **Ý TƯỞNG — Safety Gate trước Execution**
> Mọi path (Kafka RCA, Slack approve, Rule Engine) **bắt buộc** đi qua `PARSE → GATE`. Không có “emergency bypass” im lặng trong code path production. Bypass (nếu có) phải dual-control + audit event riêng + time-boxed.

> [!TIP]
> **State tách biệt**
> `Action State` (Redis) phục vụ idempotency + advisory lock theo service. `Audit Log` (DynamoDB/Postgres append-only) phục vụ regulator. Đừng trộn hai concern: Redis có thể mất; audit **không được** mất.

---

## 3. Remediation Action Catalog

### Tier 1: Tự động hoàn toàn (Không cần phê duyệt)

Các hành động này an toàn, có thể đảo ngược và ít rủi ro:

| Hành động | Failure Mode | Bán kính ảnh hưởng tối đa |
|--------|-------------|-----------------|
| Tăng replicas của deployment | cạn kiệt tài nguyên, traffic tăng đột biến | 1 service |
| Tăng biến môi trường (pool size, cache size) | cạn kiệt pool kết nối | 1 service, rolling restart |
| Rolling restart các pods | rò rỉ bộ nhớ, tiến trình zombie | 1 service, restart từng pod một |
| Ép buộc chạy GC (JVM services qua JMX) | áp lực bộ nhớ | 1 pod |
| Xóa cache ứng dụng (qua API) | cache cũ gây lỗi dữ liệu | 1 service |
| Kích hoạt circuit breaker (open → half-open) | khôi phục lỗi cascading | 1 service |

### Tier 2: Cần con người phê duyệt (Thời gian duyệt < 5 phút)

| Hành động | Failure Mode | Rủi ro |
|--------|-------------|------|
| Rollback deployment về phiên bản trước | deployment bị lỗi regression | Trung bình — mất tính năng mới |
| Giảm replicas của deployment | lãng phí tài nguyên dư thừa | Trung bình — có thể gây thiếu năng lực xử lý |
| Thay đổi cấu hình HPA min/max replicas | tải hệ thống thay đổi dài hạn | Trung bình |
| Bật/tắt feature flag | lỗi do tính năng mới | Trung bình |
| Drain node Kubernetes | lỗi phần cứng ở cấp độ node | Trung bình — làm gián đoạn workload |
| Nâng cấp instance class của RDS | nghẽn cổ chai database | Cao — gây gián đoạn dịch vụ ngắn |

### Tier 3: Cần quy trình quản lý thay đổi (Hàng giờ/Hàng ngày)

| Hành động | Failure Mode | Rủi ro |
|--------|-------------|------|
| Chạy database schema migration | lỗi cấu trúc dữ liệu | Cao |
| Thay đổi network policy | cấu hình sai bảo mật | Cao |
| Thay đổi IAM role | lỗi phân quyền | Nghiêm trọng |
| Nâng cấp phiên bản cluster | lỗi tương thích | Nghiêm trọng |

> [!IMPORTANT]
> **Chỉ scale UP tự động; scale DOWN cần người**
> Scale down khi “traffic tạm lắng” sau spike thường tạo capacity cliff ngay khi traffic trở lại — pattern kinh điển (xem [§23](#23-edge-cases-retry-storms--wrong-rca) và bài học kiểu S3 capacity removal). Tier 1 **không** bao gồm scale down.

> [!TIP]
> **Ánh xạ tier → executor**
> Tier 1 → K8s/SSM executor + verification. Tier 2 → Slack/PagerDuty dual-control (hoặc single approve + canary). Tier 3 → GitOps PR + change ticket ([§10](#10-gitops-remediation), [12 — Production](../12-production/README.vi.md)).

### Mapping action → failure mode (tư duy quyết định)

| Action | “Đúng nhưng hại” khi… | Verify sau action |
|--------|----------------------|-------------------|
| Scale up | Upstream DB/CPU bão hòa | error_rate↓ **và** DB CPU không vọt |
| Rolling restart | Leak → restart storm | restart_count ổn định 15–30m |
| Flush cache | Herd về origin | origin RPS + error_rate 5m |
| Open CB / rollback | Cắt sớm hoặc version-coupled flag | dependency + business SLI |

---

## 4. Kubernetes-Based Remediation

### Kubernetes Remediation Executor

```python
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import logging

logger = logging.getLogger(__name__)

class KubernetesRemediationExecutor:
    def __init__(
        self,
        kubeconfig_path: str = None,  # None = sử dụng in-cluster config
        dry_run: bool = False,
    ):
        if kubeconfig_path:
            config.load_kube_config(kubeconfig_path)
        else:
            config.load_incluster_config()
        
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.autoscaling_v2 = client.AutoscalingV2Api()
        self.dry_run = dry_run
        
    # ===== Scale Deployment =====
    def scale_deployment(
        self,
        name: str,
        namespace: str,
        replicas: int,
        max_replicas: int = 20,
    ) -> dict:
        """
        Scale một deployment tới số lượng replicas mục tiêu.
        An toàn: giới hạn tối đa ở mức max_replicas.
        """
        replicas = min(replicas, max_replicas)
        
        # Lấy trạng thái hiện tại (phục vụ rollback)
        current = self.apps_v1.read_namespaced_deployment(name, namespace)
        original_replicas = current.spec.replicas
        
        if self.dry_run:
            return {
                "action": "scale_deployment",
                "dry_run": True,
                "would_change": f"{original_replicas} → {replicas}",
            }
        
        # Áp dụng thay đổi scale
        patch = {"spec": {"replicas": replicas}}
        self.apps_v1.patch_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=patch,
        )
        
        logger.info(f"Scaled {namespace}/{name}: {original_replicas} → {replicas}")
        
        return {
            "action": "scale_deployment",
            "service": f"{namespace}/{name}",
            "original_replicas": original_replicas,
            "new_replicas": replicas,
            "rollback": lambda: self.scale_deployment(name, namespace, original_replicas),
        }
    
    # ===== Update Environment Variable =====
    def set_env_var(
        self,
        deployment_name: str,
        namespace: str,
        env_var_name: str,
        env_var_value: str,
        allowed_vars: list = None,
    ) -> dict:
        """
        Thiết lập biến môi trường cho một deployment.
        Rolling restart sẽ được kích hoạt tự động sau đó.
        """
        # Kiểm tra danh sách whitelist
        if allowed_vars and env_var_name not in allowed_vars:
            raise ValueError(f"Env var '{env_var_name}' not in allowed list")
        
        # Lấy giá trị hiện tại phục vụ rollback
        deployment = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)
        containers = deployment.spec.template.spec.containers
        
        original_value = None
        for container in containers:
            for env in (container.env or []):
                if env.name == env_var_name:
                    original_value = env.value
                    break
        
        if self.dry_run:
            return {
                "action": "set_env_var",
                "dry_run": True,
                "env_var": env_var_name,
                "current": original_value,
                "new": env_var_value,
            }
        
        # Xây dựng cấu trúc patch
        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": containers[0].name,
                                "env": [{"name": env_var_name, "value": str(env_var_value)}],
                            }
                        ]
                    }
                }
            }
        }
        
        self.apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=patch,
        )
        
        logger.info(f"Updated {namespace}/{deployment_name}: {env_var_name}={env_var_value}")
        
        return {
            "action": "set_env_var",
            "service": f"{namespace}/{deployment_name}",
            "env_var": env_var_name,
            "original_value": original_value,
            "new_value": env_var_value,
            "rollback": lambda: self.set_env_var(
                deployment_name, namespace, env_var_name,
                original_value or "", allowed_vars
            ),
        }
    
    # ===== Rolling Restart =====
    def rolling_restart(self, deployment_name: str, namespace: str) -> dict:
        """
        Kích hoạt rolling restart bằng cách cập nhật annotation.
        Kubernetes sẽ tự động restart từng pod một cách tuần tự.
        """
        if self.dry_run:
            return {"action": "rolling_restart", "dry_run": True}
        
        # Thêm annotation restart (kỹ thuật chuẩn của k8s)
        patch = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                        }
                    }
                }
            }
        }
        
        self.apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=patch,
        )
        
        logger.info(f"Rolling restart triggered: {namespace}/{deployment_name}")
        
        return {
            "action": "rolling_restart",
            "service": f"{namespace}/{deployment_name}",
            "rollback": None,  # Rolling restart không thể đảo ngược một cách dễ dàng
        }
    
    # ===== Rollback Deployment =====
    def rollback_deployment(
        self,
        deployment_name: str,
        namespace: str,
        revision: int = 0,  # 0 = phiên bản trước đó gần nhất
    ) -> dict:
        """
        Roll back về phiên bản deployment trước đó.
        Yêu cầu phê duyệt từ con người trước khi thực hiện.
        """
        if self.dry_run:
            return {"action": "rollback_deployment", "dry_run": True}
        
        # Sử dụng lệnh kubectl rollout undo qua subprocess (sạch sẽ hơn gọi API trực tiếp)
        import subprocess
        
        cmd = [
            "kubectl", "rollout", "undo",
            f"deployment/{deployment_name}",
            "-n", namespace,
        ]
        if revision > 0:
            cmd.extend([f"--to-revision={revision}"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise RuntimeError(f"Rollback failed: {result.stderr}")
        
        logger.warning(f"ROLLBACK executed: {namespace}/{deployment_name}")
        
        return {
            "action": "rollback_deployment",
            "service": f"{namespace}/{deployment_name}",
            "revision": revision,
            "output": result.stdout,
        }
    
    # ===== Wait for Rollout =====
    def wait_for_rollout(
        self,
        deployment_name: str,
        namespace: str,
        timeout_seconds: int = 300,
    ) -> bool:
        """
        Chờ cho tiến trình deployment rollout hoàn tất.
        Trả về True nếu thành công, False nếu quá thời gian chờ.
        """
        deadline = time.time() + timeout_seconds
        
        while time.time() < deadline:
            deployment = self.apps_v1.read_namespaced_deployment(deployment_name, namespace)
            status = deployment.status
            
            if (status.updated_replicas == status.replicas and
                status.available_replicas == status.replicas and
                status.unavailable_replicas in (None, 0)):
                return True
            
            logger.info(
                f"Waiting for {namespace}/{deployment_name}: "
                f"updated={status.updated_replicas}/{status.replicas}, "
                f"available={status.available_replicas}/{status.replicas}"
            )
            time.sleep(10)
        
        return False  # Quá thời gian chờ
```

> [!WARNING]
> **Không `subprocess` freeform shell từ LLM**
> Ví dụ `kubectl rollout undo` ở trên là **command cố định trong code**, tham số đã validate (name/namespace/revision). LLM chỉ được chọn `action_type` + tham số schema — không được sinh chuỗi shell tùy ý. Xem [§21 Runbook-as-Code](#21-runbook-as-code-vs-llm-freeform).

> [!TIP]
> **Idempotency**
> Gọi `scale_deployment` hai lần với cùng `replicas` phải an toàn. Lưu `execution_id` / `idempotency_key` từ incident trước khi patch API.

---

## 5. AWS SSM Automation

Đối với các tài nguyên không chạy trên Kubernetes (RDS, ElastiCache, EC2), sử dụng AWS SSM Automation:

```python
import boto3
import time
import logging

logger = logging.getLogger(__name__)

class SSMRemediationExecutor:
    def __init__(self, region: str = "us-east-1"):
        self.ssm = boto3.client("ssm", region_name=region)
        self.rds = boto3.client("rds", region_name=region)
        self.ec2 = boto3.client("ec2", region_name=region)

    def run_ssm_document(
        self,
        document_name: str,
        target_instances: list,
        parameters: dict,
        timeout_seconds: int = 300,
    ) -> dict:
        """
        Thực thi một tài liệu SSM Automation document.
        """
        response = self.ssm.start_automation_execution(
            DocumentName=document_name,
            DocumentVersion="$LATEST",
            Parameters=parameters,
            Tags=[
                {"Key": "triggered_by", "Value": "aiops-remediation"},
                {"Key": "timestamp", "Value": str(time.time())},
            ],
        )
        
        execution_id = response["AutomationExecutionId"]
        
        # Chờ cho đến khi hoàn tất
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            status = self.ssm.get_automation_execution(
                AutomationExecutionId=execution_id
            )["AutomationExecution"]["AutomationExecutionStatus"]
            
            if status == "Success":
                return {"status": "success", "execution_id": execution_id}
            elif status in ("Failed", "Cancelled", "TimedOut"):
                return {"status": "failed", "execution_id": execution_id, "error": status}
            
            time.sleep(10)
        
        return {"status": "timeout", "execution_id": execution_id}

    def reboot_rds_instance(
        self,
        db_instance_identifier: str,
        force_failover: bool = False,
    ) -> dict:
        """
        Reboot một instance RDS (ví dụ để giải phóng connection locks).
        force_failover=True: chuyển quyền sang instance standby (cho Multi-AZ, mất ~60s downtime)
        force_failover=False: khởi động lại tại chỗ (mất khoảng ~5 phút downtime)
        """
        logger.warning(f"Rebooting RDS instance: {db_instance_identifier} (failover={force_failover})")
        
        response = self.rds.reboot_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            ForceFailover=force_failover,
        )
        
        return {
            "action": "reboot_rds",
            "instance": db_instance_identifier,
            "failover": force_failover,
            "status": response["DBInstance"]["DBInstanceStatus"],
        }

    def modify_rds_parameter_group(
        self,
        parameter_group_name: str,
        parameters: list,
    ) -> dict:
        """
        Sửa đổi RDS parameter group (ví dụ để tăng max_connections).
        Lưu ý: Một số tham số yêu cầu reboot instance để có hiệu lực.
        """
        response = self.rds.modify_db_parameter_group(
            DBParameterGroupName=parameter_group_name,
            Parameters=parameters,
        )
        
        return {
            "action": "modify_rds_parameter_group",
            "parameter_group": parameter_group_name,
            "parameters_modified": [p["ParameterName"] for p in parameters],
            "response": response["DBParameterGroupName"],
        }


# Định nghĩa sẵn các tài liệu SSM Automation cho các tác vụ phổ biến

CUSTOM_SSM_DOCUMENTS = {
    "aiops-restart-ecs-service": {
        "description": "Restart an ECS service by forcing new deployment",
        "parameters": {
            "ClusterName": {"type": "String"},
            "ServiceName": {"type": "String"},
        },
        "mainSteps": [
            {
                "name": "ForceNewDeployment",
                "action": "aws:executeAwsApi",
                "inputs": {
                    "Service": "ecs",
                    "Api": "UpdateService",
                    "Cluster": "{{ClusterName}}",
                    "Service": "{{ServiceName}}",
                    "ForceNewDeployment": True,
                },
            }
        ],
    },
    "aiops-flush-elasticache": {
        "description": "Flush an ElastiCache cluster (Redis FLUSHALL)",
        "parameters": {
            "ClusterEndpoint": {"type": "String"},
            "Port": {"type": "String", "default": "6379"},
        },
        "mainSteps": [
            {
                "name": "FlushCache",
                "action": "aws:runCommand",
                "inputs": {
                    "DocumentName": "AWS-RunShellScript",
                    "Parameters": {
                        "commands": [
                            "redis-cli -h {{ClusterEndpoint}} -p {{Port}} FLUSHALL ASYNC"
                        ]
                    },
                },
            }
        ],
    },
}
```

> [!CAUTION]
> **SSM `AWS-RunShellScript` là vũ khí hai lưỡi**
> Document `aiops-flush-elasticache` chỉ an toàn nếu parameter đã whitelist + dual-control. **Cấm** cho LLM truyền arbitrary `commands[]`. Banking/PCI: ưu tiên API managed (ElastiCache API) thay vì shell trên bastion — [14 — Banking](../14-ecommerce-banking/README.vi.md).

---

## 6. Safety Framework

```python
from dataclasses import dataclass
from typing import Callable, List, Optional
from enum import Enum
import time

class ActionRisk(Enum):
    LOW = 1      # Tự động thực thi hoàn toàn
    MEDIUM = 2   # Yêu cầu phê duyệt
    HIGH = 3     # Yêu cầu quy trình quản lý thay đổi
    BLOCKED = 4  # Không bao giờ tự động hóa

@dataclass
class SafetyCheck:
    name: str
    check: Callable[[dict], tuple]  # (bool passed, str reason)
    blocks_on_failure: bool = True

@dataclass
class RemediationAction:
    action_type: str
    service: str
    namespace: str
    parameters: dict
    requested_by: str        # "llm-agent" hoặc "human:{slack_user}"
    incident_id: str
    confidence: float        # Từ LLM/RCA (0.0 - 1.0)
    auto_approved: bool = False

class SafetyFramework:
    def __init__(
        self,
        max_actions_per_hour: int = 10,
        max_services_per_action: int = 1,
        blocked_namespaces: list = None,
    ):
        self.max_actions_per_hour = max_actions_per_hour
        self.blocked_namespaces = blocked_namespaces or ["kube-system", "kube-public", "monitoring"]
        self.action_history = []  # Lịch sử các hành động gần đây để giới hạn tần suất

    def _check_namespace(self, action: RemediationAction) -> tuple:
        if action.namespace in self.blocked_namespaces:
            return False, f"Namespace '{action.namespace}' bị bảo vệ"
        return True, "ok"

    def _check_confidence(self, action: RemediationAction) -> tuple:
        if action.confidence < 0.75:
            return False, f"Độ tự tin quá thấp: {action.confidence:.0%} (yêu cầu tối thiểu: 75%)"
        return True, "ok"

    def _check_rate_limit(self, action: RemediationAction) -> tuple:
        current_hour_actions = [
            a for a in self.action_history
            if time.time() - a["timestamp"] < 3600
        ]
        if len(current_hour_actions) >= self.max_actions_per_hour:
            return False, f"Chạm giới hạn tần suất: {self.max_actions_per_hour} hành động/giờ"
        return True, "ok"

    def _check_action_whitelist(self, action: RemediationAction) -> tuple:
        TIER1_WHITELIST = {
            "scale_deployment_up",
            "set_env_var_approved",
            "rolling_restart",
            "toggle_circuit_breaker",
        }
        TIER2_REQUIRE_APPROVAL = {
            "rollback_deployment",
            "scale_deployment_down",
            "update_hpa",
            "drain_node",
        }
        
        if action.action_type in TIER1_WHITELIST:
            return True, "ok"
        elif action.action_type in TIER2_REQUIRE_APPROVAL and action.auto_approved:
            return True, "human_approved"
        elif action.action_type in TIER2_REQUIRE_APPROVAL:
            return False, f"Hành động '{action.action_type}' yêu cầu con người phê duyệt"
        else:
            return False, f"Hành động '{action.action_type}' không nằm trong whitelist"

    def _check_service_health_before(self, action: RemediationAction) -> tuple:
        """
        Không thực thi khắc phục tự động nếu dịch vụ đã sập hoàn toàn.
        Việc tự động xử lý khi đó có thể làm tình hình tồi tệ hơn. Yêu cầu con người can thiệp.
        """
        # Truy vấn Prometheus để kiểm tra sức khỏe dịch vụ
        error_rate = query_current_metric(
            f'rate(http_requests_total{{service="{action.service}",status=~"5.."}}[5m])'
            f' / rate(http_requests_total{{service="{action.service}"}}[5m])'
        )
        
        if error_rate is not None and error_rate > 0.99:
            return False, "Tỷ lệ lỗi của dịch vụ >99% — quá suy thoái để tự động khắc phục"
        
        return True, "ok"

    def evaluate(self, action: RemediationAction) -> tuple:
        """
        Chạy toàn bộ các bước kiểm tra an toàn. Trả về (approved: bool, reason: str).
        """
        checks = [
            self._check_namespace(action),
            self._check_confidence(action),
            self._check_rate_limit(action),
            self._check_action_whitelist(action),
            self._check_service_health_before(action),
        ]
        
        for passed, reason in checks:
            if not passed:
                return False, reason
        
        # Mọi kiểm tra an toàn đều vượt qua
        self.action_history.append({
            "action": action.action_type,
            "service": action.service,
            "timestamp": time.time(),
        })
        
        return True, "approved"
```

> [!NOTE]
> **Ý TƯỞNG — Safety là composition, không phải một if**
> Namespace deny-list, confidence floor, rate limit, whitelist tier, pre-health check là **AND**. Một check fail → fail-closed. Mở rộng: change-freeze calendar, dual-control, circuit breaker remediation, advisory lock service — xem [§20](#20-circuit-breakers-rate-limits--dual-control).

> [!WARNING]
> **Confidence của LLM không phải xác suất vật lý**
> Ngưỡng 0.75 chỉ là policy. Kết hợp evidence score từ [09 — RCA](../09-root-cause-analysis/README.vi.md) (multi-signal) quan trọng hơn một số float từ model. RCA sai + confidence cao = tai nạn nhanh.

### Advisory lock & concurrent incidents

```python
import redis

class ServiceActionLock:
    """Chỉ 1 remediation / service tại một thời điểm (Redis SET NX + TTL)."""
    def __init__(self, redis_url: str, ttl_seconds: int = 600):
        self.r = redis.from_url(redis_url)
        self.ttl = ttl_seconds

    def acquire(self, service: str, execution_id: str) -> bool:
        return bool(self.r.set(
            f"remediation:lock:{service}", execution_id, nx=True, ex=self.ttl,
        ))

    def release(self, service: str, execution_id: str) -> None:
        # Production: compare-and-delete (Lua/WATCH) — chỉ owner được release
        if self.r.get(f"remediation:lock:{service}") == execution_id.encode():
            self.r.delete(f"remediation:lock:{service}")
```

---

## 7. Blast Radius Calculation

Trước khi thực thi bất kỳ hành động khắc phục nào, hãy tính toán bán kính ảnh hưởng của nó:

```python
import networkx as nx

def calculate_blast_radius(
    action: dict,
    dependency_graph: nx.DiGraph,
    current_traffic: dict,
) -> dict:
    """
    Ước lượng tác động xấu nhất nếu hành động khắc phục làm gián đoạn/restart dịch vụ.
    """
    service = action.get("service")
    
    if service not in dependency_graph:
        return {"blast_radius": "unknown", "affected_users": 0}
    
    # Các dịch vụ phụ thuộc vào dịch vụ này (upstream)
    upstream_dependents = list(nx.ancestors(dependency_graph, service))
    
    # Traffic đi qua dịch vụ này
    service_rps = current_traffic.get(service, {}).get("requests_per_second", 0)
    
    # Ước lượng số lượng người dùng bị ảnh hưởng khi dịch vụ restart trong N giây
    # Thời gian chạy rolling restart trung bình: 30-120 giây
    restart_duration_seconds = 60  # Ước lượng an toàn
    affected_requests = service_rps * restart_duration_seconds
    
    # Ước lượng thiệt hại doanh thu (dựa trên tỷ lệ lỗi × doanh thu trên mỗi request)
    revenue_per_request = current_traffic.get(service, {}).get("revenue_per_request", 0)
    estimated_revenue_impact = affected_requests * revenue_per_request
    
    return {
        "service": service,
        "affected_upstream_services": upstream_dependents,
        "service_rps": service_rps,
        "restart_duration_seconds": restart_duration_seconds,
        "affected_requests": affected_requests,
        "estimated_revenue_impact_usd": estimated_revenue_impact,
        "blast_radius_score": len(upstream_dependents) / max(1, len(dependency_graph.nodes)),
        "recommendation": (
            "PROCEED" if len(upstream_dependents) < 5 and estimated_revenue_impact < 1000
            else "REQUIRE_APPROVAL" if len(upstream_dependents) < 10
            else "DO_NOT_AUTO_REMEDIATE"
        ),
    }
```

> [!TIP]
> **Blast radius ≠ chỉ graph topology**
> Thêm: % traffic canary, dependency fan-out, shared DB/queue, multi-tenant blast, regulatory blast (PII path). Banking: action chạm core-ledger luôn `DO_NOT_AUTO_REMEDIATE` bất kể graph score — [14 — Banking](../14-ecommerce-banking/README.vi.md).

---

## 8. Rollback Design

Mỗi hành động khắc phục tự động đều phải đi kèm phương án rollback được định nghĩa rõ ràng:

```python
from dataclasses import dataclass, field
from typing import Callable, Optional
import uuid
import time
import logging

logger = logging.getLogger(__name__)

@dataclass
class RemediationExecution:
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: RemediationAction = None
    status: str = "pending"          # pending | executing | success | failed | rolled_back
    result: dict = field(default_factory=dict)
    rollback_fn: Optional[Callable] = None
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    
    def execute(self, executor) -> bool:
        """Thực thi hành động và lưu lại phương án rollback."""
        self.status = "executing"
        
        try:
            result = executor.execute(self.action)
            self.result = result
            self.rollback_fn = result.get("rollback")
            self.status = "success"
            self.completed_at = time.time()
            return True
        except Exception as e:
            self.result = {"error": str(e)}
            self.status = "failed"
            self.completed_at = time.time()
            return False
    
    def rollback(self) -> bool:
        """Thực hiện rollback nếu có sẵn phương án."""
        if self.rollback_fn is None:
            logger.warning(f"No rollback available for execution {self.execution_id}")
            return False
        
        try:
            self.rollback_fn()
            self.status = "rolled_back"
            logger.info(f"Rolled back execution {self.execution_id}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed for {self.execution_id}: {e}")
            return False


class RollbackMonitor:
    """
    Theo dõi kết quả thực thi khắc phục và tự động rollback nếu các chỉ số metrics không cải thiện.
    """
    def __init__(
        self,
        verification_window_seconds: int = 120,   # Chờ 2 phút để thấy sự cải thiện
        auto_rollback_on_failure: bool = True,
    ):
        self.window = verification_window_seconds
        self.auto_rollback = auto_rollback_on_failure
    
    async def monitor_and_verify(
        self,
        execution: RemediationExecution,
        expected_improvements: dict,
    ) -> bool:
        """
        Giám sát dịch vụ sau khi thực thi hành động.
        expected_improvements: {metric_name: {"direction": "decrease", "threshold": 0.05}}
        
        Trả về True nếu hành động thành công (metrics cải thiện như kỳ vọng).
        """
        logger.info(f"Monitoring execution {execution.execution_id} for {self.window}s")
        
        # Chờ hành động có hiệu lực (rolling restart mất khoảng ~60s)
        await asyncio.sleep(30)
        
        improvement_confirmed = await self._check_metric_improvements(
            execution.action.service,
            expected_improvements,
        )
        
        if improvement_confirmed:
            logger.info(f"Execution {execution.execution_id} verified successful")
            return True
        
        if self.auto_rollback and execution.rollback_fn:
            logger.warning(
                f"Execution {execution.execution_id} did not improve metrics. "
                f"Auto-rolling back."
            )
            success = execution.rollback()
            
            # Thông báo cho kỹ sư trực
            await notify_slack(
                f"⚠️ Auto-remediation for {execution.action.service} did not improve metrics. "
                f"Rolled back automatically. Manual investigation required."
            )
            
            return False
        
        return False
    
    async def _check_metric_improvements(
        self,
        service: str,
        expected: dict,
    ) -> bool:
        """
        Kiểm tra xem các metrics dịch vụ có cải thiện đúng như kỳ vọng sau khi khắc phục hay không.
        """
        improvements_seen = 0
        total_checks = len(expected)
        
        for metric_name, spec in expected.items():
            current_value = await query_current_metric_async(
                f'{metric_name}{{service="{service}"}}'
            )
            
            if current_value is None:
                continue
            
            if spec["direction"] == "decrease" and current_value <= spec["threshold"]:
                improvements_seen += 1
            elif spec["direction"] == "increase" and current_value >= spec["threshold"]:
                improvements_seen += 1
        
        # Yêu cầu ít nhất 60% chỉ số metrics phải cải thiện
        return improvements_seen / total_checks >= 0.6 if total_checks > 0 else False
```

> [!IMPORTANT]
> **Rollback cũng là action nguy hiểm**
> Rollback tự động khi metric chưa ổn định (cold start, deploy lag) có thể tạo flip-flop. Cần: min wait, hysteresis, max_auto_rollback_per_incident=1, sau đó escalate người.

---

## 9. Canary-Based Remediation

Đối với các hành động khắc phục có rủi ro cao hơn, hãy áp dụng thử nghiệm trên một nhóm nhỏ trước:

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

class CanaryRemediationExecutor:
    def __init__(
        self,
        k8s_executor: KubernetesRemediationExecutor,
        canary_fraction: float = 0.1,  # Thử nghiệm trên 10% số pods trước
        verification_seconds: int = 120,
    ):
        self.k8s = k8s_executor
        self.canary_fraction = canary_fraction
        self.verification = verification_seconds
    
    async def execute_with_canary(
        self,
        action: str,
        deployment_name: str,
        namespace: str,
        parameters: dict,
    ) -> dict:
        """
        Thực thi thay đổi trên nhóm canary pods trước, xác thực, sau đó mới rollout cho toàn bộ pods.
        """
        # Lấy thông tin deployment hiện tại
        deployment = self.k8s.apps_v1.read_namespaced_deployment(deployment_name, namespace)
        total_replicas = deployment.spec.replicas
        canary_replicas = max(1, int(total_replicas * self.canary_fraction))
        
        logger.info(
            f"Canary remediation: {deployment_name} "
            f"({canary_replicas}/{total_replicas} pods first)"
        )
        
        # Phase 1: Áp dụng thay đổi cho nhóm canary (ở đây mô phỏng bằng kịch bản rút gọn)
        # Trong môi trường sản xuất thực tế: sử dụng các công cụ canary chuẩn (Argo Rollouts)
        canary_result = self.k8s.execute(action, parameters, dry_run=False)
        
        # Chờ và xác thực sức khỏe nhóm canary
        await asyncio.sleep(self.verification)
        canary_healthy = await self._verify_canary_health(deployment_name, namespace)
        
        if not canary_healthy:
            logger.warning(f"Canary failed for {deployment_name}. Aborting rollout.")
            canary_result.get("rollback", lambda: None)()
            return {"status": "canary_failed", "rolled_back": True}
        
        logger.info(f"Canary successful. Proceeding with full rollout for {deployment_name}")
        
        # Phase 2: Rollout toàn phần
        return {"status": "success", "canary_verified": True}
    
    async def _verify_canary_health(self, deployment_name: str, namespace: str) -> bool:
        """Kiểm tra xem nhóm canary pods có khỏe mạnh không."""
        error_rate = await query_current_metric_async(
            f'rate(http_requests_total{{service="{deployment_name}",status=~"5.."}}[2m])'
            f' / rate(http_requests_total{{service="{deployment_name}"}}[2m])'
        )
        
        # Nếu tỷ lệ lỗi tăng quá 10%, coi như thử nghiệm thất bại
        if error_rate is not None and error_rate > 0.10:
            return False
        
        return True
```

### Progressive rollout of remediation actions

Canary một “nhóm pod” chưa đủ — production nên **progressive + abort criteria**:

```
1% → wait → SLI OK? → 10% → 50% → 100% → soak dài hơn
Abort nếu: error_rate↑, p99↑, saturation xấu, business KPI↓
```

| Phase | Phạm vi | Min wait | Ai approve |
|-------|---------|----------|------------|
| Shadow / dry-run | 0% mutate | log only | auto |
| Canary | 1–10% | 2–5 phút | auto Tier1 / human Tier2 |
| Ramp | 25–50% | 5–15 phút | auto nếu canary xanh |
| Full + soak | 100% | 10 phút–24 giờ | auto + audit; page nếu regress |

> [!TIP]
> **Progressive ≠ chỉ traffic split** — pool size 20→30→50; restart `maxUnavailable`; feature flag theo % cohort.

> [!WARNING]
> **Canary mù metric** — nếu canary không nhận traffic thật, verify luôn “xanh”. Bắt buộc `canary_rps > min_samples`.

---

## 10. GitOps Remediation

Đối với các thay đổi cấu hình cần được lưu vết qua quá trình kiểm duyệt mã nguồn:

```python
import subprocess
import os
from pathlib import Path
import httpx

class GitOpsRemediationExecutor:
    """
    Tạo một Pull Request chứa nội dung thay đổi cấu hình cần khắc phục.
    Cách này áp dụng cho các hành động Tier 2/3 yêu cầu ghi nhận lịch sử thay đổi.
    """
    def __init__(
        self,
        repo_url: str,
        base_branch: str = "main",
        github_token: str = None,
    ):
        self.repo_url = repo_url
        self.base_branch = base_branch
        self.github_token = github_token

    def create_remediation_pr(
        self,
        incident_id: str,
        service: str,
        file_path: str,           # Đường dẫn file trong repository cần sửa đổi
        change_description: str,
        original_content: str,
        new_content: str,
    ) -> dict:
        """
        Tạo Git PR chứa nội dung sửa lỗi tự động.
        """
        branch_name = f"aiops/remediation-{incident_id}"
        
        # Clone repo về local disk
        repo_dir = f"/tmp/{incident_id}"
        subprocess.run(
            ["git", "clone", "--depth=1", self.repo_url, repo_dir],
            check=True,
            env={**os.environ, "GIT_ASKPASS": "echo", "GIT_TERMINAL_PROMPT": "0"},
        )
        
        # Tạo nhánh mới
        subprocess.run(["git", "-C", repo_dir, "checkout", "-b", branch_name], check=True)
        
        # Ghi đè file với nội dung mới
        target_file = Path(repo_dir) / file_path
        target_file.write_text(new_content)
        
        # Commit thay đổi
        subprocess.run(["git", "-C", repo_dir, "add", file_path], check=True)
        subprocess.run(
            ["git", "-C", repo_dir, "commit", "-m",
             f"[AIOps] {change_description}\n\nIncident: {incident_id}\n"
             f"Service: {service}\nAuto-generated by AIOps Remediation Engine"],
            check=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "AIOps Bot",
                "GIT_AUTHOR_EMAIL": "aiops@company.com",
                "GIT_COMMITTER_NAME": "AIOps Bot",
                "GIT_COMMITTER_EMAIL": "aiops@company.com",
            },
        )
        
        # Push nhánh lên remote
        subprocess.run(
            ["git", "-C", repo_dir, "push", "origin", branch_name],
            check=True,
        )
        
        # Gọi GitHub API tạo Pull Request
        pr_response = httpx.post(
            f"https://api.github.com/repos/{self.repo_url.split('github.com/')[1]}/pulls",
            headers={
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github+json",
            },
            json={
                "title": f"[AIOps Remediation] {service}: {change_description}",
                "body": (
                    f"## AIOps Auto-Remediation PR\n\n"
                    f"**Incident**: {incident_id}\n"
                    f"**Service**: {service}\n"
                    f"**Change**: {change_description}\n\n"
                    f"PR này được tạo tự động bởi hệ thống AIOps Remediation Engine.\n"
                    f"Vui lòng rà soát kỹ lưỡng và merge nếu cấu hình chính xác.\n\n"
                    f"**Tự động merge**: PR này sẽ tự động merge sau 30 phút "
                    f"nếu không có ý kiến phản đối nào được ghi nhận."
                ),
                "head": branch_name,
                "base": self.base_branch,
            },
        )
        
        return {
            "pr_url": pr_response.json().get("html_url"),
            "branch": branch_name,
            "status": "pr_created",
        }
```

---

## 11. Verification Pipeline

```python
import asyncio
import time

class RemediationVerificationPipeline:
    """
    Quy trình xác thực cấu trúc nhằm đảm bảo hành động khắc phục thực tế đã xử lý được incident.
    """
    
    VERIFICATION_STEPS = {
        "scale_deployment": [
            {"metric": "error_rate", "direction": "decrease", "target": 0.01, "wait_seconds": 60},
            {"metric": "latency_p99", "direction": "decrease", "target_pct": 0.50, "wait_seconds": 90},
        ],
        "set_env_var": [
            {"metric": "db_connections_active", "direction": "decrease", "target_pct": 0.80, "wait_seconds": 120},
            {"metric": "error_rate", "direction": "decrease", "target": 0.02, "wait_seconds": 120},
        ],
        "rolling_restart": [
            {"metric": "pod_restart_count", "check": "stable", "wait_seconds": 180},
            {"metric": "error_rate", "direction": "decrease", "target": 0.02, "wait_seconds": 120},
        ],
        "rollback_deployment": [
            {"metric": "error_rate", "direction": "decrease", "target": 0.01, "wait_seconds": 120},
            {"metric": "latency_p99", "direction": "decrease", "target_pct": 0.50, "wait_seconds": 120},
        ],
    }
    
    async def verify(self, execution: RemediationExecution) -> dict:
        action_type = execution.action.action_type
        service = execution.action.service
        steps = self.VERIFICATION_STEPS.get(action_type, [])
        
        if not steps:
            return {"status": "unknown", "reason": "no_verification_steps_defined"}
        
        results = []
        
        for step in steps:
            await asyncio.sleep(step.get("wait_seconds", 60))
            
            metric_query = step["metric"].replace("{service}", service)
            current = await query_current_metric_async(metric_query)
            
            if current is None:
                results.append({"step": step, "status": "no_data"})
                continue
            
            target = step.get("target")
            direction = step.get("direction")
            
            if direction == "decrease" and target and current <= target:
                results.append({"step": step, "status": "passed", "value": current})
            elif direction == "increase" and target and current >= target:
                results.append({"step": step, "status": "passed", "value": current})
            else:
                results.append({"step": step, "status": "failed", "value": current, "target": target})
        
        passed = all(r["status"] == "passed" for r in results)
        
        return {
            "execution_id": execution.execution_id,
            "action": action_type,
            "service": service,
            "verification_passed": passed,
            "steps": results,
            "verified_at": time.time(),
        }
```

### Làm sao biết fix đã work? Verification loops

```
pre-snapshot → execute → wait (effect lag) → post-check
  pass → close + learn
  fail → rollback 1 lần → re-check → escalate
  inconclusive → không claim success; giữ soak window
```

**Metastable failures** (lỗi tự duy trì sau khi trigger ban đầu hết):

| Sau “fix” | Ý nghĩa | Verify thêm |
|-----------|---------|-------------|
| Error↓ rồi tăng lại 10–20m | backlog / cold cache / retry storm | soak + queue depth |
| Latency OK, business SLI↓ | silent drop / partial dep | KPI nghiệp vụ, không chỉ 5xx |
| Metric xanh, user đỏ | sampling bias | log error class + trace |
| OOM hết rồi OOM lại | leak | restart_count 30–60m |

> [!NOTE]
> **Success là giả thuyết** — action OK ≠ incident resolved. Chỉ đóng auto khi pre/post hypothesis + soak không regress.

> [!IMPORTANT]
> **Đừng verify quá sớm** (rollout 60–120s, TTL, drain, HPA lag). Verify sớm → false-fail → rollback storm.

---

## 12. Audit Logging

Mọi hành động khắc phục tự động bắt buộc phải được ghi audit log đầy đủ:

```python
import boto3
import json
import time
from datetime import datetime

class RemediationAuditLogger:
    """
    Ghi nhận nhật ký audit log bất biến cho tất cả hành động khắc phục sự cố.
    Sử dụng DynamoDB (thiết kế theo mô hình append-only).
    """
    def __init__(self, table_name: str = "aiops-remediation-audit"):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
    
    def log(
        self,
        execution: RemediationExecution,
        event_type: str,  # "INITIATED", "APPROVED", "EXECUTED", "VERIFIED", "ROLLED_BACK"
        details: dict = None,
    ):
        """
        Thêm một sự kiện audit. Cấu hình append-only trên DynamoDB đảm bảo tính bất biến của nhật ký.
        """
        self.table.put_item(
            Item={
                "execution_id": execution.execution_id,
                "event_id": f"{execution.execution_id}#{event_type}#{int(time.time() * 1000)}",
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "incident_id": execution.action.incident_id,
                "action_type": execution.action.action_type,
                "service": execution.action.service,
                "namespace": execution.action.namespace,
                "parameters": json.dumps(execution.action.parameters),
                "requested_by": execution.action.requested_by,
                "confidence": str(execution.action.confidence),
                "auto_approved": execution.action.auto_approved,
                "details": json.dumps(details or {}),
            },
            ConditionExpression="attribute_not_exists(event_id)",  # Tránh trùng lặp ghi nhận
        )
```

### Audit log cho regulator (banking / PCI / SOX)

Ngoài SRE debug, audit phải **chứng minh control** độc lập:

| Trường | Compliance |
|--------|------------|
| `who` (bot / humans dual) | accountability |
| `what` (action + params sanitize) | reconstruct |
| `when` (UTC, ordered events) | timeline |
| `why` (incident, RCA, confidence) | intent |
| `decision` / `outcome` | effectiveness |
| WORM / hash_chain / deny-delete IAM | integrity |

```
Banking: append-only, retention 1–7 năm, engine GHI / auditor ĐỌC / không ai SỬA,
export SIEM/GRC, che secret, link change ticket Tier2/3.
```

> [!TIP]
> Auditor 3 năm sau phải đọc được *ai / hành động gì / hệ thống nào / vì sự cố nào / kết quả / rollback?*. Thiếu 1 mắt xích = fail. Domain: [14 — Banking](../14-ecommerce-banking/README.vi.md).

---

## 13. Production Configuration

```yaml
# Triển khai remediation-engine
apiVersion: apps/v1
kind: Deployment
metadata:
  name: remediation-engine
  namespace: aiops
spec:
  replicas: 2
  template:
    spec:
      serviceAccountName: remediation-engine  # Tài khoản service account giới hạn quyền RBAC
      containers:
        - name: remediation-engine
          image: aiops/remediation-engine:1.0.0
          env:
            - name: KAFKA_INPUT_TOPIC
              value: "aiops-remediation-triggers"
            - name: KAFKA_OUTPUT_TOPIC
              value: "aiops-remediation-results"
            - name: AUDIT_TABLE
              value: "aiops-remediation-audit"
            - name: MAX_ACTIONS_PER_HOUR
              value: "10"
            - name: DRY_RUN
              value: "false"   # Đặt thành "true" khi chạy trên môi trường staging để test thử
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"

---
# Cấu hình Kubernetes RBAC cho remediation engine
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: remediation-engine
rules:
  # Quyền đọc thông tin (phục vụ kiểm tra xác thực)
  - apiGroups: ["apps", ""]
    resources: ["deployments", "pods", "services", "replicasets"]
    verbs: ["get", "list", "watch"]
  # Quyền ghi thông tin (giới hạn chặt chẽ ở các tác vụ cần thiết)
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["patch", "update"]    # Để scale và chỉnh sửa env vars
  - apiGroups: ["apps"]
    resources: ["deployments/scale"]
    verbs: ["patch"]
  # BỊ CẤM: Không cấp các quyền xóa (delete) hoặc tạo mới (create) để nâng cao tính an toàn

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: remediation-engine
subjects:
  - kind: ServiceAccount
    name: remediation-engine
    namespace: aiops
roleRef:
  kind: ClusterRole
  name: remediation-engine
  apiGroup: rbac.authorization.k8s.io
```

---

## 14. Common Mistakes

| Sai lầm phổ biến | Triệu chứng | Khắc phục |
|---------|---------|-----|
| Thực hiện khắc phục nhưng thiếu kiểm tra xác thực sau đó | Hành động báo thành công nhưng sự cố thực tế vẫn tiếp tục kéo dài | Thiết lập verification pipeline kiểm tra metrics sau khắc phục |
| Không giới hạn bán kính ảnh hưởng | Thao tác restart lan truyền đồng loạt gây gián đoạn chéo trên 50 services | Bắt buộc chạy tính toán blast radius trước khi chạy lệnh |
| Không chuẩn bị phương án rollback | Hành động khắc phục khiến lỗi nặng hơn và không thể rollback tự động | Bắt buộc định nghĩa kịch bản rollback đi kèm cho từng action |
| Tự động co giãn giảm tài nguyên (auto-scaling down) | Hiện tượng nghẽn traffic tạm thời giảm che mắt, hệ thống scale down gây lỗi OOM ngay sau đó | Chỉ tự động co giãn tăng (scale UP), yêu cầu con người phê duyệt khi giảm (scale DOWN) |
| Thiếu nhật ký kiểm toán (audit trail) | Không phục vụ được công tác tuân thủ bảo mật và điều tra lỗi hệ thống sau đó | Ghi nhận toàn bộ sự kiện khắc phục vào kho lưu trữ audit log bất biến |
| Cấp quyền RBAC quá rộng | Remediation engine vô tình thực hiện xóa các tài nguyên production quan trọng | Áp dụng nguyên tắc quyền hạn tối thiểu: chỉ cho phép patch/update, cấm xóa |
| Thiếu giới hạn tần suất thực thi | Bão cảnh báo xảy ra kích hoạt hàng trăm lệnh tự sửa gây hỗn loạn hệ thống | Cấu hình giới hạn cứng (ví dụ: tối đa 10 hành động/giờ) |
| Thiếu cơ chế canary | Thay đổi cấu hình lỗi lập tức ảnh hưởng tới 100% số pods | Áp dụng chạy thử nghiệm canary trước đối với các hành động Tier 2 |
| Bỏ qua độ trễ của quá trình rolling restart | Các kiểm tra xác thực chạy trước khi pod mới thực sự khởi động xong | Thiết lập thời gian chờ tối thiểu 60-120s trước khi chạy xác thực metric |
| LLM freeform shell / kubectl tùy ý | Hành động không lặp lại, không audit được tham số | Chỉ runbook-as-code + schema params ([§21](#21-runbook-as-code-vs-llm-freeform)) |
| Tin RCA một signal | Action “đúng RCA sai” (scale down capacity) | Multi-evidence + human cho capacity removal |
| Verification không đo business SLI | HTTP 200 nhưng checkout fail | Thêm KPI nghiệp vụ vào verification |
| Dual-control yếu (cùng người approve) | SoD (segregation of duties) fail | 2 principals độc lập + break-glass riêng |
| Không chaos-test remediation | Gate “trông an toàn” nhưng fail dưới tải | Game day định kỳ ([§24](#24-chaos-testing-of-remediation)) |

---

## 15. Monitoring Remediation

```promql
# Tải thực thi khắc phục sự cố
rate(aiops_remediation_executions_total[5m])

# Tỷ lệ thực thi khắc phục thành công
rate(aiops_remediation_executions_total{status="success"}[1h])
/
rate(aiops_remediation_executions_total[1h])

# Tỷ lệ kích hoạt rollback (tỷ lệ rollback cao thể hiện giải pháp khắc phục tự động hoạt động kém hiệu quả)
rate(aiops_remediation_rollbacks_total[24h])
/
rate(aiops_remediation_executions_total[24h])

# Cải thiện chỉ số MTTR khi có sự hỗ trợ của khắc phục tự động
histogram_quantile(0.50, rate(aiops_incident_resolution_time_seconds_bucket{
  remediation_type="automated"
}[7d]))

# Số lượt chặn của chốt chặn an toàn
rate(aiops_safety_gate_blocks_total[1h]) by (reason)

# Dual-control / human approval latency (on-call UX)
histogram_quantile(0.95, rate(aiops_remediation_approval_wait_seconds_bucket[1h]))

# Circuit breaker open trên chính remediation engine
aiops_remediation_circuit_state
```

> [!TIP]
> **Alert trên chính remediation**
> Cảnh báo khi: rollback_rate > 10%/24h, safety_blocks spike (có thể RCA/LLM regress), concurrent_actions gần trần, approval_p95 > 10 phút (UX on-call hỏng).

---

## 16. Scaling

Remediation engine được cố ý cấu hình giới hạn tần suất thực thi chặt chẽ. Nó **KHÔNG NÊN** được scale ngang một cách đại trà — việc hai instance của remediation engine cùng chạy các hành động mâu thuẫn trên cùng một tài nguyên là rất nguy hiểm.

```yaml
# Replicas tối đa: 2 (thiết lập theo mô hình active-passive để đảm bảo HA, không nhằm tăng throughput)
autoscaling:
  enabled: false
  
# HA: 2 replicas kết hợp cơ chế leader election (chỉ cho phép tối đa 1 instance hoạt động tại một thời điểm)
leader_election:
  enabled: true
  lease_duration_seconds: 60
  renew_deadline_seconds: 40
```

---

## 17. Security

- **IRSA**: Remediation engine sử dụng IAM Role thông qua cơ chế IRSA để xác thực truy cập vào các AWS API (như SSM, RDS, v.v.).
- **Kubernetes RBAC**: Giới hạn quyền tối đa — chỉ cho phép `patch` và `update` đối với tài nguyên `deployments`. Tuyệt đối không cho phép quyền `delete`, không cấp quyền quản trị cluster-level.
- **Network Policy**: Cấu hình mạng chặn tối đa — remediation engine chỉ được phép kết nối tới Kubernetes API, Kafka, và DynamoDB nội bộ. Không cấp quyền kết nối internet đi ra ngoài.
- **Audit**: Nhật ký audit log được ghi vào DynamoDB đi kèm cấu hình `ConditionExpression` để ngăn chặn hành vi chỉnh sửa hoặc xóa log lịch sử.
- **Bảo mật dữ liệu nhạy cảm**: Không ghi các tham số chứa thông tin tài khoản, mật khẩu, credentials vào hệ thống log.
- **Dual-control / SoD**: Hành động nguy hiểm cần 2 principals; bot không tự approve proposal của chính nó.
- **Không freeform shell**: Executor chỉ gọi API/document đã đăng ký; LLM không sinh argv tùy ý.

---

## 18. Cost

| Thành phần | Chi phí hàng tháng |
|-----------|-------------|
| Remediation Engine (2× t3.large) | $120 |
| DynamoDB (audit log, ~1 triệu lượt ghi/tháng) | $2 |
| Chi phí chạy các lệnh SSM Automation | ~$5 (trả phí theo số lượt chạy) |
| **Tổng cộng** | **~$127/tháng** |

> [!NOTE]
> **Chi phí ẩn**
> Cost engine rẻ; cost *sai action* đắt. Ngân sách “an toàn” (canary thời gian, dual-control on-call, chaos game day) thường ROI cao hơn scale thêm replica remediation.

---

## 19. Risk Decision Matrix

Ma trận quyết định production: **reversibility × blast radius × confidence × compliance**.

### Bốn trục

| Trục | Thấp (an toàn hơn) | Cao (nguy hiểm hơn) |
|------|--------------------|---------------------|
| **Reversibility** | Hoàn tác < 30s, state đầy đủ | Irreversible / data loss / schema |
| **Blast radius** | 1 pod / 1 service non-critical | Shared DB, multi-AZ, payment path |
| **Confidence** | Multi-signal RCA + history match | Single metric / LLM-only |
| **Compliance** | Dev/staging, non-regulated | Banking ledger, PCI, change-freeze |

### Bảng quyết định (rút gọn)

| Reversible? | Blast | Confidence | Compliance OK? | Quyết định |
|-------------|-------|------------|----------------|------------|
| Yes, <1m | 1 service | ≥0.85 multi-signal | Yes | **AUTO** Tier1 + verify |
| Yes | 1 service | 0.75–0.85 | Yes | AUTO canary 10% hoặc human |
| Yes | multi-service | ≥0.85 | Yes | **Human approve** + progressive |
| Partial | bất kỳ | bất kỳ | Yes | Human + dual-control nếu data/IAM |
| No | bất kỳ | bất kỳ | — | **Tier3 / change mgmt** — không auto |
| Bất kỳ | bất kỳ | bất kỳ | Freeze / regulated block | **Block** hoặc break-glass dual-control |

```
risk ≈ w1*(1-rev) + w2*blast + w3*(1-conf) + w4*compliance_flag
→ AUTO | REQUIRE_APPROVAL | BLOCK  (whitelist vẫn bắt buộc)
```

> [!IMPORTANT]
> **Compliance là hard gate** — confidence=0.99 cũng không overrule change-freeze / banking core.

> [!TIP]
> **Ghi 4 trục + quyết định vào audit** — phục vụ postmortem và tuning threshold.

---

## 20. Circuit Breakers, Rate Limits & Dual-Control

### Rate limits (nhiều tầng)

| Tầng | Ví dụ | Mục đích |
|------|-------|----------|
| Global | ≤10/giờ; ≤2 concurrent | chống herd toàn platform |
| Per-service | ≤1/10 phút + Redis lock | chống flip-flop |
| Per-action-type | restart ≤3/service/giờ | chống restart storm |
| Per-incident | max 1 auto-rollback | chống dao động |
| Time-of-day | siết giờ on-call thấp điểm | giảm rủi ro 3am |

### Circuit breaker cho chính remediation engine

```
CLOSED → (rollback_spike / error budget) → OPEN → cooldown → HALF_OPEN (1 test)
OPEN = dry-run + page human only; không mutate prod
Mở khi: rollback_rate cao, bypass attempts, Prometheus/k8s down (không verify được),
        hoặc phát hiện remediation-caused SEV
```

### Dual-control cho dangerous actions

```
propose → SafetyGate → Approver A + B (A ≠ B, SoD) → execute → audit cả hai
Break-glass: time-boxed + security alarm + post-incident review bắt buộc
```

> [!WARNING]
> **Rate limit local-only** — multi-replica cần Redis/store trung tâm cho counter + lock.

> [!NOTE]
> **Breaker OPEN phải page** — “Auto-remediation paused — manual only”. Im lặng là anti-pattern.

---

## 21. Runbook-as-Code vs LLM Freeform

| Mô hình | Mô tả | An toàn? |
|---------|-------|----------|
| **Runbook-as-code** | Action = hàm/document đã review, params schema (JSON Schema), unit test | **Bắt buộc production** |
| **LLM freeform shell** | Model sinh `kubectl ...` / bash | **Cấm** |
| **LLM chọn trong catalog** | Model chọn `action_type` + args validate | Cho phép sau gate |
| **GitOps PR** | LLM/engine propose diff, human merge | Tốt cho Tier2/3 |

```
Pipeline an toàn:
  RCA/LLM → structured intent
         → map sang action_id trong catalog
         → validate JSON Schema (whitelist keys + ranges)
         → SafetyGate + risk matrix
         → Executor implementation cố định trong repo
         → Verify + Audit

Cấm:
  os.system(llm_text)
  subprocess(llm_generated_argv)  # trừ allowlist binary + fixed flags
  SSM commands[] từ raw LLM string
```

> [!CAUTION]
> **Never freeform shell**
> Một prompt injection / hallucination có thể thành `delete namespace`. Catalog + schema + RBAC least privilege là ba lớp độc lập — cần cả ba.

Cross-link: agent tool design ở [10 — LLM Agent](../10-llm-agent/README.vi.md); chaos/runbook platform ở [12 — Production](../12-production/README.vi.md).

---

## 22. Human Approval UX (On-Call 3am)

On-call 3am **không** đọc essay — quyết định <30 giây.

```
[P1] payment-service · conf 0.88 · blast: 1 svc · reversible: 45s
WHY: pool exhausted (logs+metrics+trace) — not DB CPU
ACTION: DB_POOL_SIZE 20 → 40 (whitelist)
RISK: DB load↑; abort if db_cpu>70%
VERIFY: error_rate<1% / 3m; rollback = 20
[Approve] [Reject] [Defer+Page] [Dry-run]
Timeout 15m → escalate; KHÔNG auto-execute
```

| UX rule | Chi tiết |
|---------|----------|
| One thumb | 1 màn hình; không deep-link bắt buộc |
| Fail-closed timeout | hết giờ = không execute |
| Reversibility nổi | “Undo in Xs” + diff params |
| Chống mis-tap | confirm Tier2; dual-control nguy hiểm |
| Link phụ | dashboard/runbook optional |

> [!TIP]
> Card đã có blast + whitelist + dry-run — người chỉ *accept risk*, không làm lại RCA lúc 3am.

> [!WARNING]
> **Rubber-stamp** — >5 approve/đêm ⇒ siết catalog/confidence, đừng train bấm Approve máy móc.

---

## 23. Edge Cases: Retry Storms & Wrong RCA

### Edge A — Remediation gây retry storm / thundering herd

```
flush cache cluster-wide → cold miss đồng loạt → origin/DB RPS ×10
→ latency↑ → client retry → thundering herd → SEV-1 nặng hơn ban đầu
```

| Action nguy cơ herd | Mitigation |
|---------------------|------------|
| Cache flush | prefix/progressive; cấm fan-out toàn cụm |
| Restart nhiều deps | stagger, maxUnavailable, global concurrency |
| Scale 1→50 / traffic 0→100% | step scale, warm pool, ramp |
| Open nhiều CB cùng lúc | per-dependency budget |

### Edge B — Wrong RCA → wrong action (capacity removal / S3-style lesson)

Pattern postmortem hạ tầng lớn: triệu chứng “thừa capacity / lỗi node” → auto **gỡ capacity** → tải dồn → sập lan (positive feedback).

```
RCA nông: error node X → remove capacity
RCA đúng: control plane / dependency / retry storm
Sai: scale-down khi đang quá tải → outage khuếch đại
```

**Luật capacity**: (1) **cấm auto scale-down/remove** khi SEV/error cao; (2) ưu tiên add capacity / shed load / degrade; (3) capacity reduction = Tier2+ dual-control; (4) RCA tách *pool nhỏ* vs *DB chậm* trước khi tăng pool.

> [!CAUTION]
> **Wrong RCA nhanh hơn human** — gate multi-signal + cấm class action nguy hiểm quan trọng hơn model “thông minh”.

Xem [15 — Famous Incidents](../15-famous-incidents/README.vi.md), [09 — RCA](../09-root-cause-analysis/README.vi.md).

---

## 24. Chaos Testing of Remediation

Phải chaos **chính remediation**, không chỉ app:

| Thí nghiệm | Kỳ vọng |
|------------|---------|
| Fake high-confidence bad RCA | SafetyGate block hoặc human; không mutate |
| Duplicate Kafka triggers | Idempotent; 1 execution |
| Two incidents 1 service | Lock; second queued/rejected |
| Prometheus down mid-verify | No blind success; fail-closed / hold |
| Rollback function throws | Page human; state=needs_manual |
| Rate limit saturation | Queue/reject; no silent drop without metric |
| Approver timeout 3am | No auto-execute; escalate |
| Leader election failover mid-action | Không double-execute |
| Canary metric spoof / no traffic | Abort “insufficient samples” |
| Change-freeze flag on | Tier1 có thể giữ; Tier2 block |

```
Game day (quý): tabletop wrong-RCA scale-down → staging inject + real engine
→ đo MTTD bad action, block rate, audit completeness → fix trước khi nới whitelist
```

> [!TIP]
> Chaos platform-wide: [12 — Production Operations](../12-production/README.vi.md).

---

## 25. Case Studies — Famous Incidents

Ánh xạ bài học → control (full: [15 — Famous Incidents](../15-famous-incidents/README.vi.md)).

| Incident pattern | Cơ chế hỏng | Control trong chương này |
|------------------|-------------|---------------------------|
| Cascading retry / herd | Client retry + partial outage | rate limit global, progressive, flush an toàn |
| Capacity removal under load | Gỡ resource khi đang stress | cấm auto scale-down khi SEV; risk matrix |
| Bad deploy + slow rollback | Thiếu verify / rollback | rollback design + verification window |
| Config push global | Blast 100% region | canary + progressive + GitOps |
| IAM / privilege mistake | Quyền rộng | RBAC least privilege, no delete |
| Dependency brownout | Scale app → DB chết | RCA phân biệt pool vs DB slow |
| Automation made it worse | Bainbridge irony | dual-control, circuit breaker engine |
| Audit gap sau sự cố | Thiếu who/what/why | audit banking-grade |

> [!NOTE]
> **Học postmortem, không copy tool** — copy catalog bigtech thiếu gate = tái hiện outage ở scale nhỏ hơn.

---

## 26. Production Checklist (40+)

### Catalog & policy
1. [ ] Action catalog Tier1/2/3 đã review SRE + security
2. [ ] Mỗi action có failure mode + max blast radius ghi rõ
3. [ ] JSON Schema params + range limits (replicas max, env whitelist)
4. [ ] Không có path freeform shell / raw kubectl từ LLM
5. [ ] Scale-down / capacity remove **không** nằm Tier1
6. [ ] Change-freeze calendar tích hợp engine

### Safety gates
7. [ ] Namespace deny-list (kube-system, …)
8. [ ] Confidence + multi-signal RCA floor
9. [ ] Global rate limit + per-service lock (Redis/store trung tâm)
10. [ ] Concurrent action cap
11. [ ] Pre-health check (không auto khi đã 99% down nếu policy cấm)
12. [ ] Risk matrix 4 trục được evaluate và log
13. [ ] Circuit breaker engine (rollback spike → OPEN)
14. [ ] Dual-control cho action nguy hiểm / regulated

### Execution
15. [ ] Dry-run mode staging bắt buộc trước prod
16. [ ] Idempotency key theo incident+action
17. [ ] Leader election active-passive
18. [ ] RBAC: get/list/watch + patch/update only; **no delete/create**
19. [ ] IRSA / least IAM cho SSM/RDS
20. [ ] NetworkPolicy: chỉ k8s API, Kafka, audit store, metrics
21. [ ] Progressive/canary cho Tier2 config changes
22. [ ] maxUnavailable / stagger restart

### Rollback & verification
23. [ ] Mọi Tier1 action có rollback_fn hoặc documented non-rollback
24. [ ] Min wait trước verify (60–120s+ theo action)
25. [ ] Verification multi-metric + business SLI khi có
26. [ ] Soak window cho metastable failures
27. [ ] max 1 auto-rollback / incident rồi escalate
28. [ ] Hysteresis chống flip-flop

### Human & UX
29. [ ] Approval card 3am-friendly (một màn hình)
30. [ ] Timeout approve = fail-closed
31. [ ] SoD: approver ≠ proposer bot; dual khi cần
32. [ ] Break-glass có time-box + security page

### Audit & compliance
33. [ ] Append-only audit (who/what/when/why/decision/outcome)
34. [ ] Retention theo policy (banking: năm)
35. [ ] Deny IAM delete/update audit table
36. [ ] Export SIEM/GRC
37. [ ] Sanitize secrets khỏi params log

### Ops & learning
38. [ ] Metrics: success, rollback, blocks, approval latency
39. [ ] Alert khi rollback_rate cao / breaker open
40. [ ] Chaos/game day remediation mỗi quý
41. [ ] Postmortem bắt buộc nếu remediation gây regress
42. [ ] Whitelist nới lỏng chỉ sau ≥30 ngày dữ liệu an toàn
43. [ ] Cross-check RCA quality với [09](../09-root-cause-analysis/README.vi.md)
44. [ ] Agent tools align [10](../10-llm-agent/README.vi.md) — không tool nguy hiểm lẻ
45. [ ] Banking controls review [14](../14-ecommerce-banking/README.vi.md)

> [!IMPORTANT]
> Checklist là **gate go-live**, không phải tài liệu trang trí. Gắn vào PR template remediation-engine.

---

## 27. Production Review

### Principal Engineer Assessment

**Các vấn đề nghiêm trọng**:

1. **Nguy cơ lỗi thundering herd do khắc phục tự động**: Nếu 50 services đồng loạt kích hoạt hành động "rolling restart" tại cùng một thời điểm, Kubernetes cluster sẽ rơi vào trạng thái mất ổn định nghiêm trọng. Do đó, cơ chế giới hạn tần suất (10 hành động/giờ) bắt buộc phải cấu hình ở mức **toàn cục (GLOBAL)**, chứ không được cấu hình độc lập trên từng service. Hãy bổ sung thêm giới hạn số lượng hành động chạy song song (concurrent actions).

2. **Thiếu khả năng xử lý sự cố ở cấp độ database**: Nguyên nhân phổ biến nhất gây cạn kiệt connection pool thường không nằm ở cấu hình kích hoạt pool size của service, mà do chính database đang phản hồi rất chậm. Việc cố tình tăng pool size trong khi DB đang bị nghẽn cổ chai sẽ chỉ làm tăng tải và làm DB sụp đổ nhanh hơn (nhiều kết nối đồng nghĩa với tải DB tăng vọt). Bộ máy phân tích RCA bắt buộc phải phân biệt rõ lỗi "pool quá nhỏ" với lỗi "DB đang phản hồi chậm" trước khi kích hoạt hành động khắc phục tương ứng — xem [09 — RCA](../09-root-cause-analysis/README.vi.md).

3. **Thiếu cơ chế lock chéo khi có nhiều sự cố**: Nếu có hai incidents độc lập cùng tác động lên một service, chúng có thể cùng kích hoạt hai lệnh khắc phục mâu thuẫn đồng thời gây xung đột hệ thống. Hãy thiết lập cơ chế khóa advisory locks cho từng service (ví dụ sử dụng lệnh Redis SETNX) trước khi cho phép chạy bất kỳ hành động khắc phục nào.

4. **Quản lý khoảng thời gian đóng băng thay đổi (Change freeze)**: Trong các giai đoạn đóng băng thay đổi hệ thống được lên lịch trước (giai đoạn cuối quý, Black Friday), toàn bộ các hành động khắc phục Tier 2 bắt buộc phải được tự động chuyển cấp yêu cầu con người phê duyệt trước khi thực thi, kể cả khi bình thường chúng được phép tự động chạy. Hãy tích hợp remediation engine với lịch quản lý thay đổi chung của doanh nghiệp — [12 — Production](../12-production/README.vi.md).

5. **Ironies of automation (Bainbridge)**: Càng auto nhiều, on-call càng ít “cơ bắp” xử lý tay. Bắt buộc game day + runbook-as-code + UX approve 3am; không ảo tưởng LLM thay thế skill.

6. **Capacity removal / wrong RCA**: Cấm class action gỡ capacity khi đang SEV; map bài học [15 — Famous Incidents](../15-famous-incidents/README.vi.md).

### Chapter Scores

| Tiêu chí | Điểm số | Ghi chú |
|-----------|-------|-------|
| Technical Accuracy | 9.7/10 | Cú pháp gọi k8s API, SSM, cấu hình RBAC chuẩn xác, đã xác thực |
| Production Readiness | 9.8/10 | Canary progressive, dual-control, circuit breaker, checklist 40+ |
| Depth | 9.7/10 | Bainbridge, risk matrix 4 trục, metastable, wrong-RCA edges |
| Practical Value | 9.7/10 | Executor + safety + approval UX + audit banking |
| Architecture Quality | 9.7/10 | Gate, verify, rollback, runbook-as-code |
| Observability | 9.6/10 | Rollback rate, safety blocks, approval latency |
| Security | 9.8/10 | RBAC, IRSA, audit WORM, no freeform shell |
| Scalability | 9.5/10 | Leader election + global rate limit (cố ý không scale throughput) |
| Cost Awareness | 9.7/10 | Engine rẻ; nhấn cost of wrong action |
| Diagram Quality | 9.6/10 | Luồng trigger → gate → execute → verify |

---

## References

1. [Kubernetes Client Python](https://github.com/kubernetes-client/python)
2. [AWS SSM Automation Documents](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-documents.html)
3. [Argo Rollouts — Canary Deployments](https://argoproj.github.io/rollouts/)
4. [GitOps with Flux](https://fluxcd.io/flux/)
5. [Kubernetes RBAC Best Practices](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
6. [AWS DynamoDB Audit Pattern](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/conditions.html)
7. Lisanne Bainbridge — *Ironies of Automation* (1983)
8. [09 — Root Cause Analysis](../09-root-cause-analysis/README.vi.md)
9. [10 — LLM Agent](../10-llm-agent/README.vi.md)
10. [12 — Production Operations](../12-production/README.vi.md)
11. [14 — E-commerce & Banking](../14-ecommerce-banking/README.vi.md)
12. [15 — Famous Incidents](../15-famous-incidents/README.vi.md)
