# Changelog

All notable changes to this handbook are documented here.

## [1.1.0] — 2026-07-22

### Added

- **Ch.17 Topology & Change Data Plane** (VI + EN) — service graph, sync freshness, change/deploy events, freezes, integration with enrich/correlation/RCA/remediation
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
