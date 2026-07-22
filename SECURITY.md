# Security Policy

## This repository is documentation

The AIOps Engineering Handbook is **educational documentation**. It does not ship a runnable multi-tenant production service by default.

Still:

- Do **not** open issues that paste real production secrets, tokens, customer PII, or internal runbooks.
- Example configs in chapters are **illustrative** — harden before any real deployment (authn/z, network policy, encryption, least privilege).

## Reporting a vulnerability

If you find a security issue in **published example configs** that could mislead readers into insecure defaults:

1. Open a GitHub issue with label `security` **without** exploit details that harm third parties, **or**
2. Contact the maintainer via GitHub (@XUanhoa04).

We will correct the documentation promptly.

## Preferred secure patterns (handbook stance)

- Never freeform shell from LLMs for remediation (see Ch.12)
- Dual-control / human gates for high blast-radius actions
- Redact PII before logs enter shared pipelines (see Ch.06, Ch.15)
- Break-glass out-of-band access independent of the impaired control plane (see Ch.16)
