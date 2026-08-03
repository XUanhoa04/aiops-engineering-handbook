# Changelog

All notable changes to this handbook are documented here.

## [1.2.0] — 2026-08-03

### Added

- **Ch.S System Architecture Fundamentals** (VI + EN) — 6 major sections: Compute & Runtime (process model, cgroups v2, container internals, K8s pod lifecycle, CPU throttling, OOMKilled, eBPF), Networking (request lifecycle, TCP internals, DNS, service mesh, connection pools, circuit breaking), Data & Storage (caching dynamics, cache failure patterns, DB connections, replication lag, I/O fundamentals), Distributed Systems (tracing internals, cascading failures, gray failures), AI/ML Infrastructure 2026 (GPU saturation, LLM inference mechanics, KV cache, vector DB), Synthesis (USE/RED methods, cross-layer correlation, anti-patterns)

### Changed

- `mkdocs.yml`: new "Nền tảng hệ thống / System Fundamentals" nav section
- README: updated TOC, roadmap, dependency graph, chapter count
- CURRICULUM: added System Fundamentals entry

## [1.1.0] — 2026-07-22

### Added

- **Ch.08 Topology & Change Data Plane** (VI + EN) — service graph, sync freshness, change/deploy events, freezes, integration with enrich/correlation/RCA/remediation
- **Ch.18 Predictive Operations & Capacity Risk Engine** (VI) — multi-horizon uncertainty, dependency bottlenecks, time-to-exhaustion and proactive acceptance
- **Ch.19 Incident Operations Control Plane** (VI) — command state, role leases, concurrent faults, action locks and multi-hour handoff
- **Ch.20 AIOps Governance & Model Risk Engine** (VI) — capability risk tiers, decision envelopes, runtime gates, drift and revocation
- **MkDocs Material** site (`mkdocs.yml`, `requirements-docs.txt`, `docs/index.md`)
- **GitHub Actions** workflow [`.github/workflows/docs.yml`](.github/workflows/docs.yml) → GitHub Pages
- Poster `docs/assets/diagrams/10-topology-change.png`

### Changed

- Curriculum / README / site home: **18 chapters** (00–17)
- Pipeline diagrams include topology & change side plane

## [1.0.0] — 2026-07-22

### Added

- **17 chapters × 2 languages** (Vietnamese + English)
- **Ch.06 Telemetry Data Plane** — normalize, enrich, validate, multi-tier storage, retention matrix, feature store, lifecycle, when-to-use decision trees
- Architecture **PNG posters** under `docs/assets/diagrams/` (pipeline, pillars, Kafka, intelligence, remediation, K8s, control-plane, payment, data-plane)
- Dual-language README with full TOC and learning paths by role
- `docs/CURRICULUM.md` — canonical chapter order
- `CONTRIBUTING.md`, issue/PR templates, `CODE_OF_CONDUCT.md`, `SECURITY.md`

### Changed

- Renumbered former Ch.06–15 → **Ch.07–16** (Kafka through Famous Incidents) to insert Data Plane after collection
- Intro pipeline diagrams include explicit **Data Plane** stage
- Hybrid diagram strategy: Mermaid for logic; PNG for cloud architecture heroes

### Removed

- Standalone English-only tree at `docs/0x-*` (content lives under `docs/en/`)
- Temporary achievement-practice files

## Earlier history

See git log for pre-1.0 commits (`feat: add vietnamese docs`, handbook upgrades, English translation, architecture posters).
