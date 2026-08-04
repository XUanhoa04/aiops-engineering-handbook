# Contributing to AIOps Engineering Handbook

Cảm ơn bạn quan tâm đóng góp. Handbook này là tài liệu **production-grade** (VI + EN), ưu tiên **tư duy + edge case** hơn dump code.

Thanks for contributing. This is a **production-grade** dual-language handbook (VI + EN). Prefer **thinking + edge cases** over code dumps.

---

## Ways to help

| Type | Examples |
|------|----------|
| Fix | Broken links, typos, wrong chapter numbers after renumber |
| Clarity | Stronger “when to use / when not” sections |
| Edge cases | Real production failure modes (blameless, no employer secrets) |
| Diagrams | Suggest hero architecture posters (PNG under `docs/assets/diagrams/`) |
| Translate | Keep VI ↔ EN parity for the same section |
| Structure | Cross-links between shared chapters 00–17 and Vietnamese extensions 18–20 |

---

## Chapter map (source of truth)

See [docs/CURRICULUM.md](docs/CURRICULUM.md).

**Order:** Collect (02–05) → **Data plane (06)** → Kafka (07) → Topology (08) → Intelligence (09–13) → Production and evidence (14–17) → Vietnamese operations and governance extensions (18–20).

---

## Style guide

1. **Why before how** — every non-trivial choice needs a trade-off.
2. **When to use** — add decision criteria, not only definitions.
3. **Callouts** — `> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`  
   - VI: `Ý TƯỞNG` · EN: `KEY IDEA`
4. **Mermaid** for logic/sequence/gantt · **PNG posters** for cloud architecture (images only; no Diagrams Python source in repo).
5. **No secrets** — no real customer data, tokens, or private postmortems.
6. **Dual language** — if you change meaning in VI, update EN (or open an issue to track parity).

---

## PR checklist

- [ ] Links resolve under `docs/vi/` and/or `docs/en/` (folder numbers match curriculum)
- [ ] No new dependency required to *read* the handbook
- [ ] If you add a diagram: PNG under `docs/assets/diagrams/` + row in that folder’s README
- [ ] Chapter H1 number matches folder prefix (`06-data-plane` → Chapter 06)
- [ ] Blameless language for incidents

---

## Local preview

Any Markdown viewer is enough (GitHub, VS Code, Obsidian).  
Mermaid renders on GitHub. PNG posters render everywhere.

---

## License

By contributing, you agree your contributions are under the MIT License ([LICENSE](LICENSE)).
