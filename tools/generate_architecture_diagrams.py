"""Render the handbook's reproducible Graphviz architecture posters.

Run from the repository root:
    python tools/generate_architecture_diagrams.py

The Graphviz `dot` executable must be available on PATH.
"""

from pathlib import Path

from graphviz import Digraph


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "diagrams"

COLORS = {
    "ink": "#172033",
    "muted": "#526075",
    "edge": "#738198",
    "blue": "#E8F1FF",
    "cyan": "#E6F8FA",
    "green": "#EAF7EE",
    "amber": "#FFF4D6",
    "red": "#FDECEC",
    "violet": "#F1ECFF",
    "white": "#FFFFFF",
}


def poster(filename, title, stages, edges, notes=()):
    node_ids = {
        node_id
        for _, _, _, nodes in stages
        for node_id, _, _ in nodes
    }
    for source, target, _, _ in edges:
        if source not in node_ids or target not in node_ids:
            raise ValueError(f"{filename}: unknown edge endpoint {source!r} -> {target!r}")
    for note_id, _, target in notes:
        if note_id in node_ids or target not in node_ids:
            raise ValueError(f"{filename}: invalid note {note_id!r} -> {target!r}")

    graph = Digraph(name=filename)
    graph.attr(
        rankdir="LR",
        bgcolor="white",
        pad="0.25",
        nodesep="0.38",
        ranksep="0.72",
        splines="polyline",
        outputorder="edgesfirst",
        fontname="Arial",
        labelloc="t",
        label=title,
        fontsize="24",
        fontcolor=COLORS["ink"],
        dpi="180",
    )
    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#AAB5C4",
        fillcolor=COLORS["white"],
        fontname="Arial",
        fontcolor=COLORS["ink"],
        fontsize="11",
        margin="0.16,0.10",
        penwidth="1.2",
    )
    graph.attr(
        "edge",
        color=COLORS["edge"],
        fontname="Arial",
        fontcolor=COLORS["muted"],
        fontsize="9",
        arrowsize="0.72",
        penwidth="1.15",
    )

    for index, stage in enumerate(stages):
        key, label, color, nodes = stage
        with graph.subgraph(name=f"cluster_{key}") as cluster:
            cluster.attr(
                label=label,
                style="rounded,filled",
                color="#C7D0DC",
                fillcolor=COLORS[color],
                fontname="Arial Bold",
                fontcolor=COLORS["ink"],
                fontsize="13",
                margin="16",
                rank="same",
            )
            for node_id, node_label, node_color in nodes:
                cluster.node(node_id, node_label, fillcolor=COLORS[node_color])

    for source, target, label, style in edges:
        attrs = {"style": style} if style else {}
        graph.edge(source, target, label=label, **attrs)

    for note_id, note_label, target in notes:
        graph.node(
            note_id,
            note_label,
            shape="note",
            style="filled",
            fillcolor="#FFFBEA",
            color="#D6B44C",
            fontsize="9",
        )
        graph.edge(note_id, target, style="dashed", arrowhead="none")

    target = OUT / filename
    graph.render(filename=target.stem, directory=OUT, format="png", cleanup=True)


DIAGRAMS = [
    (
        "01-aiops-pipeline.png",
        "AIOps platform — evidence to safe decision (2026)",
        [
            ("signals", "Signals", "blue", [("sli", "User journey + SLO", "white"), ("telemetry", "Metrics · logs · traces\nprofiles (alpha) · events", "white")]),
            ("collect", "Collection", "cyan", [("edge", "OTel SDK / auto-instrumentation\nOTel Collector / Grafana Alloy", "white"), ("policy", "Redaction · sampling\ncardinality limits", "white")]),
            ("evidence", "Evidence plane", "green", [("raw", "Immutable raw + durable buffer", "white"), ("dq", "Identity · event time · DQ\ncanonical revisions + features", "white"), ("context", "Versioned topology + change", "white")]),
            ("engines", "Intelligence engines", "violet", [("detect", "Persistent detection\nbaseline freeze + burn rate", "white"), ("corr", "Incident correlation", "white"), ("rca", "Multi-signal RCA", "white"), ("invest", "Read-only investigation", "white")]),
            ("decision", "Decision & action", "amber", [("safety", "Policy + safety gates\nconfidence is not authorization", "white"), ("human", "Operator brief / approval", "white"), ("act", "Canary action · verify\nexpand or rollback", "white")]),
        ],
        [("sli", "edge", "", ""), ("telemetry", "edge", "", ""), ("edge", "policy", "", ""), ("policy", "raw", "", ""), ("raw", "dq", "replayable", ""), ("dq", "detect", "quality propagated", ""), ("context", "corr", "temporal snapshot", ""), ("context", "rca", "", ""), ("detect", "corr", "", ""), ("corr", "rca", "", ""), ("rca", "invest", "ranked hypotheses", ""), ("invest", "safety", "proposal + evidence", ""), ("safety", "human", "risk tier", ""), ("human", "act", "", ""), ("act", "raw", "outcome feedback", "dashed")],
        [("n1", "Missing telemetry ≠ healthy\nEvery decision carries provenance", "dq")],
    ),
    (
        "02-observability-pillars.png",
        "Observability evidence graph — beyond the three-pillar slogan",
        [
            ("intent", "User & intent", "blue", [("journey", "Synthetic + real user journey", "white"), ("slo", "SLI / SLO + business invariant", "white")]),
            ("stable", "Stable OTel signals", "cyan", [("metrics", "Metrics", "white"), ("logs", "Structured logs + events", "white"), ("traces", "Traces + exemplars", "white")]),
            ("emerging", "Additional evidence", "green", [("profiles", "Continuous profiles\nOTel Profiles: alpha", "white"), ("changes", "Deploy / flag / config changes", "white"), ("topology", "Runtime topology", "white")]),
            ("identity", "Correlation contract", "violet", [("resource", "service.name · namespace\nenv · region · tenant", "white"), ("keys", "trace/span ID · deployment ID\nevent time · schema version", "white")]),
            ("outcome", "Operator outcome", "amber", [("evidence", "Evidence timeline", "white"), ("decision", "Page · investigate · verify", "white")]),
        ],
        [("journey", "slo", "", ""), ("slo", "metrics", "", ""), ("metrics", "resource", "", ""), ("logs", "resource", "", ""), ("traces", "keys", "", ""), ("profiles", "keys", "optional", "dashed"), ("changes", "keys", "", ""), ("topology", "resource", "", ""), ("resource", "evidence", "", ""), ("keys", "evidence", "", ""), ("evidence", "decision", "", "")],
        [("n2", "A signal is useful only when it can be\njoined, timed and trusted", "resource")],
    ),
    (
        "03-kafka-aiops-topics.png",
        "AIOps event transport — contracts, replay and isolation",
        [
            ("producers", "Producers", "blue", [("collectors", "OTel / Alloy gateways", "white"), ("rules", "SLO rules + detectors", "white"), ("changeprod", "CI/CD · flags · catalog", "white")]),
            ("rawtopics", "Ingress topics", "cyan", [("rawtele", "telemetry.raw.*", "white"), ("rawchange", "change.raw · topology.raw", "white")]),
            ("processing", "Contract processors", "green", [("normalize", "Normalize + identity", "white"), ("watermark", "Event time + watermark", "white"), ("quality", "Validate · quarantine · revision", "white")]),
            ("products", "Data-product topics", "violet", [("canonical", "telemetry.canonical.*", "white"), ("features", "features.* · quality.events", "white"), ("incidents", "anomalies · incidents · decisions", "white")]),
            ("consumers", "Isolated consumer groups", "amber", [("enginegroups", "Detection · correlation · RCA\ninvestigation", "white"), ("audit", "Audit / replay / benchmark", "white"), ("remediation", "Safety engine only\n(no direct raw → action)", "white")]),
        ],
        [("collectors", "rawtele", "", ""), ("rules", "rawtele", "", ""), ("changeprod", "rawchange", "", ""), ("rawtele", "normalize", "partition by stable identity", ""), ("rawchange", "normalize", "", ""), ("normalize", "watermark", "", ""), ("watermark", "quality", "", ""), ("quality", "canonical", "", ""), ("quality", "features", "", ""), ("canonical", "enginegroups", "", ""), ("features", "enginegroups", "", ""), ("enginegroups", "incidents", "versioned output", ""), ("incidents", "audit", "", ""), ("incidents", "remediation", "proposal only", "")],
        [("n3", "Kafka 4.x: KRaft, no ZooKeeper\nAt-least-once + idempotent sinks", "rawtele")],
    ),
    (
        "04-intelligence-layer.png",
        "AIOps intelligence — stateful engines, not a model conveyor belt",
        [
            ("input", "Evidence", "blue", [("signals", "Canonical signals + DQ", "white"), ("ctx", "Topology/change snapshot", "white")]),
            ("detect", "Detection", "cyan", [("cheap", "Freshness · SLO burn\nrobust statistics", "white"), ("heavy", "Optional multivariate / sequence", "white"), ("state", "Persistent incident candidate\nfreeze baseline while alerting", "white")]),
            ("corr", "Correlation", "green", [("group", "Temporal + semantic + topology", "white"), ("split", "Late join · split/merge\nper-service isolation", "white")]),
            ("rca", "RCA", "violet", [("causal", "First-red order · span errors\ndownstream weighting", "white"), ("score", "Multi-signal score + counterevidence", "white")]),
            ("invest", "Investigation", "amber", [("tools", "Bounded read-only queries", "white"), ("brief", "Provenance-rich operator brief", "white")]),
        ],
        [("signals", "cheap", "", ""), ("ctx", "group", "", ""), ("cheap", "state", "", ""), ("heavy", "state", "adds evidence", "dashed"), ("state", "group", "", ""), ("group", "split", "", ""), ("split", "causal", "incident state", ""), ("ctx", "causal", "", ""), ("causal", "score", "", ""), ("score", "tools", "ranked hypotheses", ""), ("tools", "brief", "", ""), ("brief", "state", "operator feedback", "dashed")],
        [("n4", "No LLM or deep model may veto\na hard liveness / SLO signal", "state")],
    ),
    (
        "05-remediation-safety.png",
        "Remediation safety — propose, gate, canary, verify",
        [
            ("proposal", "Proposal", "blue", [("incident", "Open incident + evidence", "white"), ("action", "Typed action proposal\npreconditions · rollback · TTL", "white")]),
            ("gates", "Fail-closed gates", "red", [("qualitygate", "Identity / freshness / DQ", "white"), ("riskgate", "Policy · blast radius\nchange freeze · rate limit", "white"), ("approval", "Human approval when required", "white")]),
            ("execute", "Bounded execution", "amber", [("ledger", "Idempotency + action ledger", "white"), ("canary", "Canary cohort", "white")]),
            ("verify", "Independent verification", "green", [("control", "Canary vs control\nSLI + guardrails", "white"), ("decision", "Expand · hold · rollback", "white")]),
            ("escape", "Emergency controls", "violet", [("kill", "Out-of-band kill switch", "white"), ("audit", "Immutable audit + escalation", "white")]),
        ],
        [("incident", "action", "", ""), ("action", "qualitygate", "", ""), ("qualitygate", "riskgate", "AND", ""), ("riskgate", "approval", "risk tier", ""), ("approval", "ledger", "authorized", ""), ("ledger", "canary", "", ""), ("canary", "control", "", ""), ("control", "decision", "", ""), ("decision", "audit", "outcome", ""), ("decision", "ledger", "expand/rollback revision", "dashed"), ("kill", "ledger", "stop new actions", "dashed")],
        [("n5", "Confidence ranks a proposal;\nit never grants permission", "riskgate")],
    ),
    (
        "06-k8s-production.png",
        "Production AIOps — continuity and degraded modes",
        [
            ("traffic", "Workload plane", "blue", [("gateway", "Gateway API / load balancer", "white"), ("apps", "Services across zones", "white"), ("telemetryp", "Local telemetry buffer", "white")]),
            ("platform", "AIOps platform", "cyan", [("ingest", "Multi-zone collectors + bus", "white"), ("enginesp", "Stateful engines\ncheckpoint + replay", "white"), ("modes", "Healthy · DetectionOnly\nHumanOnly · Recovery", "white")]),
            ("statep", "Durable state", "green", [("events", "Raw/canonical event log", "white"), ("incidentstore", "Incident + decision ledger", "white"), ("artifacts", "Versioned rules/models/prompts", "white")]),
            ("external", "Independent safety path", "red", [("classic", "Classic SLO/burn-rate paging", "white"), ("deadman", "External dead-man switch", "white"), ("breakglass", "Out-of-band break-glass", "white")]),
            ("ops", "Operator outcome", "amber", [("page", "Page continuity", "white"), ("recover", "Replay without duplicate\nincident or action", "white")]),
        ],
        [("gateway", "apps", "", ""), ("apps", "telemetryp", "", ""), ("telemetryp", "ingest", "", ""), ("ingest", "enginesp", "", ""), ("enginesp", "modes", "dependency health", ""), ("ingest", "events", "", ""), ("enginesp", "incidentstore", "checkpoint", ""), ("artifacts", "enginesp", "pinned version", ""), ("apps", "classic", "independent", "dashed"), ("classic", "page", "", ""), ("deadman", "page", "platform blind", ""), ("breakglass", "modes", "", "dashed"), ("modes", "page", "capability banner", ""), ("incidentstore", "recover", "", ""), ("events", "recover", "", "")],
        [("n6", "Three replicas sharing DNS, IAM or one bus\nare still one failure domain", "modes")],
    ),
    (
        "07-control-vs-data-plane.png",
        "Resilience boundaries — business, evidence and decision planes",
        [
            ("business", "Business data plane", "blue", [("request", "Customer request path", "white"), ("service", "Gateway → services → datastore", "white")]),
            ("evidenceplane", "Evidence plane", "cyan", [("observe", "Collectors + durable telemetry", "white"), ("classicpage", "Independent SLO page path", "white")]),
            ("decisionplane", "AIOps decision plane", "violet", [("analyze", "Detect · correlate · RCA\ninvestigate", "white"), ("safemode", "Degraded mode + safety policy", "white")]),
            ("outband", "Out-of-band control", "red", [("dead", "External dead-man", "white"), ("manual", "Break-glass + kill switch", "white")]),
            ("result", "Resilient outcome", "green", [("operator", "Operator still receives signal", "white"), ("restore", "Checkpointed recovery + replay", "white")]),
        ],
        [("request", "service", "", ""), ("service", "observe", "telemetry", ""), ("observe", "classicpage", "", ""), ("observe", "analyze", "", ""), ("analyze", "safemode", "", ""), ("classicpage", "operator", "bypass", ""), ("safemode", "operator", "", ""), ("dead", "operator", "", ""), ("manual", "safemode", "", "dashed"), ("observe", "restore", "event log", ""), ("analyze", "restore", "state", "")],
        [("n7", "Never place the bypass behind the same\nKafka, DNS, IAM or region", "classicpage")],
    ),
    (
        "08-payment-critical-path.png",
        "Payment domain pack — money path and invariants",
        [
            ("edgepay", "Customer edge", "blue", [("shopper", "Shopper", "white"), ("gatewaypay", "Gateway / checkout API", "white")]),
            ("corepay", "Synchronous money path", "cyan", [("checkout", "Checkout", "white"), ("auth", "Identity / auth", "white"), ("payment", "Payment orchestration", "white"), ("ledgerpay", "Idempotency + ledger", "white"), ("psp", "PSP / card network", "white")]),
            ("sidepay", "Dependent domains", "green", [("risk", "Risk / fraud", "white"), ("orders", "Order + inventory", "white"), ("events", "Async settlement / webhooks", "white")]),
            ("contractpay", "Domain evidence", "violet", [("invariants", "No double charge · ledger balanced\nauth success · settlement lag", "white"), ("critical", "Critical-path traces + business SLI", "white"), ("policy", "Dual control · audit retention", "white")]),
            ("aiopspay", "AIOps consumers", "amber", [("detectpay", "Per-service detection", "white"), ("rcapay", "Topology/change-aware RCA", "white"), ("safepay", "Risk-tiered remediation", "white")]),
        ],
        [("shopper", "gatewaypay", "", ""), ("gatewaypay", "checkout", "", ""), ("checkout", "auth", "", ""), ("auth", "payment", "", ""), ("payment", "ledgerpay", "idempotency key", ""), ("ledgerpay", "psp", "", ""), ("payment", "risk", "", ""), ("payment", "orders", "", ""), ("psp", "events", "async", ""), ("ledgerpay", "invariants", "", ""), ("psp", "critical", "", ""), ("events", "critical", "", ""), ("invariants", "detectpay", "", ""), ("critical", "rcapay", "", ""), ("policy", "safepay", "", "")],
        [("n8", "Business invariants outrank infrastructure\nCPU as customer-impact evidence", "invariants")],
    ),
    (
        "09-data-plane.png",
        "Data quality & feature plane — telemetry becomes replayable evidence",
        [
            ("rawdp", "Immutable ingress", "blue", [("rawsignal", "Raw metrics · logs · spans\nchanges · topology", "white"), ("receive", "Receive time + raw reference", "white")]),
            ("contractdp", "Deterministic contracts", "cyan", [("identitydp", "Identity + unit + schema", "white"), ("timedp", "Event time + watermark", "white"), ("enrichdp", "Point-in-time topology/change", "white")]),
            ("qualitydp", "Quality gates", "red", [("validatedp", "Accept · partial · quarantine", "white"), ("revisiondp", "Quality event + revision lineage", "white")]),
            ("productsdp", "Versioned data products", "green", [("canonicaldp", "Canonical events", "white"), ("featuredp", "Online/offline feature parity", "white"), ("incidentdp", "Incident + audit evidence", "white")]),
            ("servedp", "Consumers", "amber", [("enginesdp", "Detection · correlation · RCA", "white"), ("replaydp", "Benchmark · retrain · replay", "white")]),
        ],
        [("rawsignal", "receive", "", ""), ("receive", "identitydp", "", ""), ("identitydp", "timedp", "", ""), ("timedp", "enrichdp", "", ""), ("enrichdp", "validatedp", "", ""), ("validatedp", "revisiondp", "", ""), ("revisiondp", "canonicaldp", "", ""), ("revisiondp", "featuredp", "", ""), ("canonicaldp", "enginesdp", "quality propagated", ""), ("featuredp", "enginesdp", "feature version", ""), ("canonicaldp", "replaydp", "", ""), ("incidentdp", "replaydp", "labels/outcomes", "")],
        [("n9", "Unknown unit is quarantined — never guessed\nLate data creates a revision, not a rewrite", "validatedp")],
    ),
    (
        "10-topology-change.png",
        "Topology & change engine — temporal graph, confidence and blast radius",
        [
            ("sourcet", "Evidence sources", "blue", [("catalog", "Service catalog / ownership", "white"), ("runtime", "Traces · mesh · eBPF · DNS", "white"), ("infra", "Gateway · cloud · database", "white"), ("changet", "CI/CD · config · flags · manual", "white")]),
            ("resolvet", "Identity resolution", "cyan", [("alias", "Canonical service/resource IDs", "white"), ("conflict", "Source precedence + disagreement", "white")]),
            ("grapht", "Temporal graph product", "green", [("edges", "Typed edges + evidence", "white"), ("confidence", "Confidence · freshness · valid interval", "white"), ("snapshot", "Versioned point-in-time snapshots", "white")]),
            ("changestore", "Change ledger", "violet", [("changeevent", "Typed change events", "white"), ("risk", "Change risk + rollback reference", "white")]),
            ("consumerst", "AIOps consumers", "amber", [("enricht", "Ch.06 point-in-time enrichment", "white"), ("correlt", "Ch.09 grouping / split", "white"), ("rcat", "Ch.10 downstream weighting", "white"), ("safet", "Ch.12 blast radius / freeze", "white")]),
        ],
        [("catalog", "alias", "", ""), ("runtime", "alias", "", ""), ("infra", "conflict", "", ""), ("alias", "conflict", "", ""), ("conflict", "edges", "", ""), ("edges", "confidence", "", ""), ("confidence", "snapshot", "", ""), ("changet", "changeevent", "", ""), ("changeevent", "risk", "", ""), ("snapshot", "enricht", "", ""), ("snapshot", "correlt", "", ""), ("snapshot", "rcat", "", ""), ("snapshot", "safet", "", ""), ("risk", "rcat", "confounder evidence", ""), ("risk", "safet", "", "")],
        [("n10", "Stale graph forces degraded behavior;\nit must never look authoritative", "confidence")],
    ),
]


EXTRA_DIAGRAMS = [
    ("11-otel-collection.png", "OpenTelemetry collection — thin edge, governed gateways", [("apps", "Applications", "blue", [("sdk", "OTel SDK / auto-instrumentation", "white"), ("legacy", "Legacy logs + Prometheus endpoints", "white")]), ("agents", "Node / workload edge", "cyan", [("otelagent", "OTel Collector or Alloy agent", "white"), ("edgepolicy", "Batch · memory guard\nminimal parsing", "white")]), ("gateways", "Regional gateways", "green", [("otlp", "OTLP receive + load balance", "white"), ("govern", "Redaction · transform · tail sample\ncardinality policy", "white")]), ("backends", "Destinations", "violet", [("metricsb", "Prometheus-compatible metrics", "white"), ("logsb", "Loki / selected search", "white"), ("tracesb", "Tempo / object storage", "white"), ("busb", "Durable raw/canonical bus", "white")])], [("sdk", "otelagent", "OTLP", ""), ("legacy", "otelagent", "", ""), ("otelagent", "edgepolicy", "", ""), ("edgepolicy", "otlp", "", ""), ("otlp", "govern", "", ""), ("govern", "metricsb", "", ""), ("govern", "logsb", "", ""), ("govern", "tracesb", "", ""), ("govern", "busb", "", "")], [("n11", "Profiles remain an optional/alpha OTel path;\ndo not make them a hard dependency", "govern")]),
    ("12-slo-metrics-engine.png", "Metrics & SLO engine — from measurement to page", [("instrument", "Measurement", "blue", [("redgold", "RED / USE / business SLI", "white"), ("syntheticm", "Synthetic + black-box probes", "white")]), ("ingestm", "Ingestion", "cyan", [("scrape", "Prometheus scrape", "white"), ("otlpm", "Governed OTLP metrics", "white")]), ("storem", "Metrics product", "green", [("tsdb", "HA TSDB + long-term blocks", "white"), ("exemplar", "Exemplars + resource identity", "white")]), ("decidem", "Decision", "violet", [("rulesm", "Recording rules", "white"), ("burn", "Multi-window burn rate", "white"), ("anomalym", "Optional anomaly evidence", "white")]), ("outm", "Outcome", "amber", [("pagem", "Actionable page", "white"), ("verify", "Remediation verifier", "white")])], [("redgold", "scrape", "", ""), ("syntheticm", "scrape", "", ""), ("redgold", "otlpm", "", "dashed"), ("scrape", "tsdb", "", ""), ("otlpm", "tsdb", "", ""), ("tsdb", "exemplar", "", ""), ("tsdb", "rulesm", "", ""), ("rulesm", "burn", "", ""), ("tsdb", "anomalym", "", ""), ("burn", "pagem", "hard signal", ""), ("anomalym", "pagem", "adds confidence", "dashed"), ("burn", "verify", "", "")], [("n12", "Missing samples and stale scrapes are evidence\nquality failures — not zero values", "tsdb")]),
    ("13-log-evidence.png", "Log evidence plane — structured, redacted and purpose-tiered", [("sourcel", "Sources", "blue", [("applog", "Application / platform logs", "white"), ("auditlog", "Audit / security events", "white")]), ("collectl", "Collection", "cyan", [("alloyl", "OTel Collector / Alloy", "white"), ("parsel", "Multiline · parse · redact\nPII policy version", "white")]), ("routel", "Purpose routing", "green", [("lokil", "Loki hot operations path", "white"), ("searchl", "Selected full-text / IR index", "white"), ("coldl", "Immutable cold archive", "white")]), ("productl", "AIOps products", "violet", [("templatel", "Template / failure-family events", "white"), ("referencel", "Bounded evidence references", "white")]), ("consumel", "Consumers", "amber", [("detectl", "Log anomaly evidence", "white"), ("investl", "RCA / investigation", "white")])], [("applog", "alloyl", "", ""), ("auditlog", "alloyl", "", ""), ("alloyl", "parsel", "", ""), ("parsel", "lokil", "default", ""), ("parsel", "searchl", "allow-listed subset", ""), ("parsel", "coldl", "retention/audit", ""), ("parsel", "templatel", "", ""), ("lokil", "referencel", "query window", ""), ("templatel", "detectl", "", ""), ("referencel", "investl", "", "")], [("n13", "JSON is not structured unless fields, types\nand semantics are stable", "parsel")]),
    ("14-trace-evidence.png", "Trace evidence plane — sampled paths, derived signals and causality", [("sourcetr", "Trace sources", "blue", [("sdktr", "OTel SDK / auto-instrumentation", "white"), ("meshtr", "Mesh / gateway spans", "white")]), ("collecttr", "Collection", "cyan", [("gatewaytr", "Load-balanced OTel gateways", "white"), ("sampletr", "Tail sampling by error, latency\nand business criticality", "white")]), ("storetr", "Trace product", "green", [("tempotr", "Tempo + object storage", "white"), ("coverage", "Coverage / sampling quality", "white")]), ("derivetr", "Derived evidence", "violet", [("spanmetric", "Span metrics + exemplars", "white"), ("servicegraph", "Runtime service graph", "white"), ("errorspan", "Error-span propagation events", "white")]), ("consumetr", "Consumers", "amber", [("debugtr", "Operator path reconstruction", "white"), ("rcatr", "Correlation + RCA", "white")])], [("sdktr", "gatewaytr", "OTLP", ""), ("meshtr", "gatewaytr", "", ""), ("gatewaytr", "sampletr", "", ""), ("sampletr", "tempotr", "", ""), ("sampletr", "coverage", "", ""), ("tempotr", "spanmetric", "", ""), ("tempotr", "servicegraph", "", ""), ("tempotr", "errorspan", "", ""), ("spanmetric", "debugtr", "", ""), ("servicegraph", "rcatr", "", ""), ("errorspan", "rcatr", "", "")], [("n14", "A missing span lowers confidence; it does not\nprove that the dependency was healthy", "coverage")]),
    ("15-correlation-engine.png", "Correlation engine — preserve evidence, reduce cognitive cardinality", [("inputc", "Candidate events", "blue", [("anomalyc", "Anomalies + SLO alerts", "white"), ("contextc", "Topology/change + DQ", "white")]), ("candidatec", "Candidate generation", "cyan", [("windowc", "Event-time windows", "white"), ("keyc", "Stable identity + failure family", "white")]), ("scorec", "Pair/group scoring", "green", [("tempc", "Temporal proximity", "white"), ("semanticc", "Semantic similarity", "white"), ("topoc", "Topology distance + direction", "white")]), ("statec", "Incident state", "violet", [("mergec", "Merge + late join", "white"), ("splitc", "Split fault-on-fault\nper-service isolation", "white"), ("revisionc", "Revisions + preserved evidence", "white")]), ("outputc", "Operator unit", "amber", [("cardc", "One incident card", "white"), ("rawc", "Expandable raw evidence", "white")])], [("anomalyc", "windowc", "", ""), ("contextc", "keyc", "", ""), ("windowc", "tempc", "", ""), ("keyc", "semanticc", "", ""), ("contextc", "topoc", "", ""), ("tempc", "mergec", "", ""), ("semanticc", "mergec", "", ""), ("topoc", "splitc", "", ""), ("mergec", "revisionc", "", ""), ("splitc", "revisionc", "", ""), ("revisionc", "cardc", "", ""), ("revisionc", "rawc", "", "")], [("n15", "Correlation compresses presentation;\nit never deletes source alerts", "revisionc")]),
    ("16-rca-engine.png", "RCA engine — temporal causality, graph impact and counterevidence", [("incidentr", "Incident evidence", "blue", [("timeliner", "First-red event timeline", "white"), ("spansr", "Span-error propagation", "white"), ("signalsr", "Metrics · logs · SLO · changes", "white")]), ("graphr", "Dependency graph", "cyan", [("snapshotr", "Point-in-time typed graph", "white"), ("downstreamr", "Downstream impact weighting", "white")]), ("candidatesr", "Candidate causes", "green", [("causer", "Earliest plausible upstream fault", "white"), ("changer", "Recent change with causal window", "white"), ("sharedr", "Shared-fate infrastructure", "white")]), ("scoringr", "Multi-signal scoring", "violet", [("support", "Supporting evidence", "white"), ("counter", "Counterevidence + confounders", "white"), ("uncertainty", "Coverage-aware confidence", "white")]), ("outputr", "RCA result", "amber", [("rankedr", "Ranked hypotheses, not one verdict", "white"), ("testr", "Next discriminating test", "white")])], [("timeliner", "causer", "", ""), ("spansr", "causer", "", ""), ("signalsr", "changer", "", ""), ("snapshotr", "downstreamr", "", ""), ("downstreamr", "causer", "", ""), ("snapshotr", "sharedr", "", ""), ("causer", "support", "", ""), ("changer", "support", "", ""), ("sharedr", "counter", "", ""), ("support", "uncertainty", "", ""), ("counter", "uncertainty", "", ""), ("uncertainty", "rankedr", "", ""), ("rankedr", "testr", "", "")], [("n16", "Correlation alone is not causation;\nnegative controls must change the ranking", "counter")]),
    ("17-investigation-engine.png", "Investigation engine — bounded read-only tests with provenance", [("starti", "Inputs", "blue", [("incidenti", "Incident state + RCA hypotheses", "white"), ("policyi", "Tenant / RBAC / time budget", "white")]), ("plani", "Investigation plan", "cyan", [("questionsi", "Discriminating questions", "white"), ("budgeti", "Bounded query plan", "white")]), ("toolsi", "Read-only tools", "green", [("metrici", "Metrics / logs / traces", "white"), ("topoi", "Topology / change / catalog", "white"), ("kbi", "Versioned runbooks / postmortems", "white")]), ("evidencei", "Evidence handling", "violet", [("provi", "Citation + timestamp + query", "white"), ("conflicti", "Conflicts / missing / stale flags", "white"), ("injectioni", "Treat telemetry text as untrusted", "white")]), ("briefi", "Operator brief", "amber", [("summaryi", "What happened / impact / uncertainty", "white"), ("nexti", "Ranked cause + next safe step", "white")])], [("incidenti", "questionsi", "", ""), ("policyi", "budgeti", "", ""), ("questionsi", "metrici", "", ""), ("budgeti", "topoi", "", ""), ("questionsi", "kbi", "", ""), ("metrici", "provi", "", ""), ("topoi", "conflicti", "", ""), ("kbi", "injectioni", "", ""), ("provi", "summaryi", "", ""), ("conflicti", "summaryi", "", ""), ("injectioni", "nexti", "", ""), ("summaryi", "nexti", "", "")], [("n17", "The investigation engine does not execute shell\nor mutate production", "metrici")]),
    ("18-pattern-library.png", "Pattern library — reusable decision contracts, not recipes", [("problemp", "Observed problem", "blue", [("failurep", "Recurring failure mode", "white"), ("contextp", "Context + constraints", "white")]), ("patternp", "Pattern contract", "cyan", [("mechanismp", "Mechanism + data contract", "white"), ("forcesp", "Trade-offs + when not to use", "white"), ("fallbackp", "Degraded mode + ownership", "white")]), ("acceptp", "Acceptance", "green", [("scenario", "Positive timeline scenario", "white"), ("negative", "Negative control / edge cases", "white"), ("threshold", "Measured thresholds + artifacts", "white")]), ("specialp", "Specialization", "violet", [("domainp", "Domain pack invariants", "white"), ("configp", "Versioned parameters", "white")]), ("lifep", "Lifecycle", "amber", [("replayp", "Benchmark replay", "white"), ("promotep", "Promote · revise · retire", "white")])], [("failurep", "mechanismp", "", ""), ("contextp", "forcesp", "", ""), ("mechanismp", "scenario", "", ""), ("forcesp", "negative", "", ""), ("fallbackp", "threshold", "", ""), ("scenario", "domainp", "", ""), ("negative", "domainp", "", ""), ("domainp", "configp", "", ""), ("configp", "replayp", "", ""), ("replayp", "promotep", "", "")], [("n18", "A pattern without a negative control and\nretirement rule becomes cargo cult", "mechanismp")]),
    ("19-benchmark-replay.png", "Benchmark replay — prove behavior before promotion", [("corp", "Scenario corpus", "blue", [("eventsrep", "Versioned event stream + labels", "white"), ("faultrep", "Long incident · overlap · late data\nmissing signal · stale graph", "white")]), ("harness", "Deterministic harness", "cyan", [("clockrep", "Virtual event-time clock", "white"), ("injectrep", "Fault / dependency injection", "white"), ("repeatrep", "Seeded repeat + artifacts", "white")]), ("candidates", "Compared engines", "green", [("baselinerep", "Production baseline", "white"), ("candidaterep", "Candidate rule/model/prompt", "white")]), ("measures", "Acceptance metrics", "violet", [("detectrep", "Recall · FPR · detection deadline", "white"), ("continuityrep", "Incident continuity + overlap split", "white"), ("rcarep", "RCA rank + evidence quality", "white"), ("safetyrep", "Unsafe/duplicate action = zero", "white")]), ("gaterep", "Release decision", "amber", [("diffrep", "Decision diff + regression budget", "white"), ("releaserep", "Promote · shadow longer · reject", "white")])], [("eventsrep", "clockrep", "", ""), ("faultrep", "injectrep", "", ""), ("clockrep", "repeatrep", "", ""), ("injectrep", "repeatrep", "", ""), ("repeatrep", "baselinerep", "same input", ""), ("repeatrep", "candidaterep", "same input", ""), ("baselinerep", "detectrep", "", ""), ("candidaterep", "detectrep", "", ""), ("baselinerep", "continuityrep", "", ""), ("candidaterep", "rcarep", "", ""), ("candidaterep", "safetyrep", "", ""), ("detectrep", "diffrep", "", ""), ("continuityrep", "diffrep", "", ""), ("rcarep", "diffrep", "", ""), ("safetyrep", "diffrep", "hard gate", ""), ("diffrep", "releaserep", "", "")], [("n19", "A demo proves possibility; replay proves\nrepeatable behavior under failure", "repeatrep")]),
]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for definition in DIAGRAMS + EXTRA_DIAGRAMS:
        poster(*definition)
    print(f"Rendered {len(DIAGRAMS) + len(EXTRA_DIAGRAMS)} posters to {OUT}")
