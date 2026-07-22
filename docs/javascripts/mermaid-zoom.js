/**
 * Mermaid UX for MkDocs Material:
 * 1) Prefer natural diagram size (no shrink-to-fit)
 * 2) Horizontal scroll when wider than content column
 * 3) Click diagram → fullscreen lightbox (scroll / pan-friendly)
 * 4) Esc / backdrop / button to close
 */
(() => {
  const HINT = "Click to enlarge · Cuộn ngang nếu sơ đồ dài";

  function ensureModal() {
    let modal = document.getElementById("mermaid-lightbox");
    if (modal) return modal;

    modal = document.createElement("div");
    modal.id = "mermaid-lightbox";
    modal.className = "mermaid-lightbox";
    modal.setAttribute("hidden", "");
    modal.innerHTML = `
      <div class="mermaid-lightbox__backdrop" data-close="1"></div>
      <div class="mermaid-lightbox__panel" role="dialog" aria-modal="true" aria-label="Mermaid diagram">
        <div class="mermaid-lightbox__toolbar">
          <span class="mermaid-lightbox__title">Diagram</span>
          <div class="mermaid-lightbox__actions">
            <button type="button" class="mermaid-lightbox__btn" data-zoom="out" title="Zoom out">−</button>
            <button type="button" class="mermaid-lightbox__btn" data-zoom="reset" title="Reset">100%</button>
            <button type="button" class="mermaid-lightbox__btn" data-zoom="in" title="Zoom in">+</button>
            <button type="button" class="mermaid-lightbox__btn mermaid-lightbox__btn--close" data-close="1" title="Close">✕</button>
          </div>
        </div>
        <div class="mermaid-lightbox__stage">
          <div class="mermaid-lightbox__canvas"></div>
        </div>
        <p class="mermaid-lightbox__hint">Scroll to pan · Esc to close · +/− zoom</p>
      </div>
    `;
    document.body.appendChild(modal);

    let scale = 1;
    const canvas = modal.querySelector(".mermaid-lightbox__canvas");
    const resetLabel = modal.querySelector('[data-zoom="reset"]');

    const applyScale = () => {
      const svg = canvas.querySelector("svg");
      if (!svg) return;
      svg.style.transform = `scale(${scale})`;
      svg.style.transformOrigin = "top left";
      if (resetLabel) resetLabel.textContent = `${Math.round(scale * 100)}%`;
    };

    modal.addEventListener("click", (e) => {
      const t = e.target;
      if (t.closest("[data-close]")) {
        closeModal();
        return;
      }
      if (t.closest('[data-zoom="in"]')) {
        scale = Math.min(scale + 0.15, 3);
        applyScale();
      } else if (t.closest('[data-zoom="out"]')) {
        scale = Math.max(scale - 0.15, 0.4);
        applyScale();
      } else if (t.closest('[data-zoom="reset"]')) {
        scale = 1;
        applyScale();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !modal.hasAttribute("hidden")) closeModal();
    });

    modal._setContent = (svgNode) => {
      scale = 1;
      canvas.innerHTML = "";
      const clone = svgNode.cloneNode(true);
      clone.removeAttribute("width");
      clone.removeAttribute("height");
      // Prefer intrinsic size from viewBox
      clone.style.maxWidth = "none";
      clone.style.width = "auto";
      clone.style.height = "auto";
      clone.style.display = "block";
      canvas.appendChild(clone);
      applyScale();
    };

    return modal;
  }

  function openModal(svg) {
    const modal = ensureModal();
    modal._setContent(svg);
    modal.removeAttribute("hidden");
    document.documentElement.classList.add("mermaid-lightbox-open");
  }

  function closeModal() {
    const modal = document.getElementById("mermaid-lightbox");
    if (!modal) return;
    modal.setAttribute("hidden", "");
    document.documentElement.classList.remove("mermaid-lightbox-open");
    const canvas = modal.querySelector(".mermaid-lightbox__canvas");
    if (canvas) canvas.innerHTML = "";
  }

  function wrapDiagram(host) {
    if (host.dataset.zoomReady === "1") return;
    const svg = host.querySelector("svg");
    if (!svg) return;

    host.dataset.zoomReady = "1";
    host.classList.add("mermaid--zoomable");

    // Prevent Material/CSS from forcing tiny shrink
    svg.style.maxWidth = "none";
    svg.removeAttribute("width");
    // keep height auto from viewBox

    let shell = host.closest(".mermaid-scroll");
    if (!shell) {
      shell = document.createElement("div");
      shell.className = "mermaid-scroll";
      host.parentNode.insertBefore(shell, host);
      shell.appendChild(host);

      const badge = document.createElement("button");
      badge.type = "button";
      badge.className = "mermaid-expand-hint";
      badge.textContent = "🔍 Enlarge diagram";
      badge.title = HINT;
      shell.insertBefore(badge, host);

      badge.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const s = host.querySelector("svg");
        if (s) openModal(s);
      });
    }

    host.style.cursor = "zoom-in";
    host.title = HINT;
    host.addEventListener("click", (e) => {
      // Avoid hijacking links inside labels
      if (e.target.closest("a")) return;
      const s = host.querySelector("svg");
      if (s) openModal(s);
    });
  }

  function enhanceAll(root) {
    const scope = root || document;
    // Material may render as pre.mermaid or div.mermaid
    scope.querySelectorAll("pre.mermaid, div.mermaid, .mermaid").forEach((el) => {
      // only if contains svg already rendered
      if (el.querySelector("svg")) wrapDiagram(el);
    });
  }

  function configureMermaid() {
    if (typeof mermaid === "undefined") return;
    try {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "loose",
        // Do not squash wide graphs into the column width
        flowchart: {
          useMaxWidth: false,
          htmlLabels: true,
          curve: "basis",
          padding: 12,
          nodeSpacing: 40,
          rankSpacing: 50,
        },
        sequence: { useMaxWidth: false, actorMargin: 40 },
        gantt: { useMaxWidth: false },
        journey: { useMaxWidth: false },
        class: { useMaxWidth: false },
        state: { useMaxWidth: false },
        er: { useMaxWidth: false },
        pie: { useMaxWidth: true },
        mindmap: { useMaxWidth: false },
        timeline: { useMaxWidth: false },
        themeVariables: {
          fontSize: "16px",
          primaryColor: "#dbeafe",
          primaryTextColor: "#1e293b",
          primaryBorderColor: "#93c5fd",
          secondaryColor: "#dcfce7",
          tertiaryColor: "#f3e8ff",
          lineColor: "#64748b",
          background: "#ffffff",
          mainBkg: "#f8fafc",
          nodeBorder: "#94a3b8",
          clusterBkg: "#f1f5f9",
          titleColor: "#0f172a",
          edgeLabelBackground: "#f8fafc",
        },
      });
    } catch (_) {
      /* Material may already have initialized; CSS still helps */
    }
  }

  // Initial
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      configureMermaid();
      // wait a tick for mermaid render
      setTimeout(() => enhanceAll(), 100);
      setTimeout(() => enhanceAll(), 600);
    });
  } else {
    configureMermaid();
    setTimeout(() => enhanceAll(), 100);
    setTimeout(() => enhanceAll(), 600);
  }

  // Material Instant Navigation
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(() => {
      configureMermaid();
      setTimeout(() => enhanceAll(), 50);
      setTimeout(() => enhanceAll(), 400);
      setTimeout(() => enhanceAll(), 1200);
    });
  }

  // MutationObserver for late SVG inject
  const mo = new MutationObserver(() => enhanceAll());
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();
