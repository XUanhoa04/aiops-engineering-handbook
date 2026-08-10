/** Unlock the AES-GCM encrypted MkDocs chapter with a four-digit PIN. */
(function () {
  "use strict";

  var encoder = new TextEncoder();
  var decoder = new TextDecoder();

  function decodeBase64(value) {
    var binary = window.atob(value.trim());
    var bytes = new Uint8Array(binary.length);
    for (var index = 0; index < binary.length; index += 1) {
      bytes[index] = binary.charCodeAt(index);
    }
    return bytes;
  }

  async function decryptChapter(gate, pin) {
    var payload = document.getElementById("pin-protected-payload");
    if (!payload) throw new Error("Missing protected payload");

    var keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      encoder.encode(pin),
      "PBKDF2",
      false,
      ["deriveKey"]
    );
    var key = await window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        hash: "SHA-256",
        salt: decodeBase64(gate.dataset.salt),
        iterations: Number(gate.dataset.iterations),
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"]
    );
    var plaintext = await window.crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: decodeBase64(gate.dataset.nonce),
        additionalData: encoder.encode(gate.dataset.aad),
        tagLength: 128,
      },
      key,
      decodeBase64(payload.textContent)
    );
    return decoder.decode(plaintext);
  }

  function initPinGate() {
    var gate = document.getElementById("pin-protected-chapter");
    if (!gate || gate.dataset.initialized === "true") return;
    gate.dataset.initialized = "true";

    var form = document.getElementById("pin-gate-form");
    var input = document.getElementById("pin-gate-code");
    var button = form.querySelector("button[type='submit']");
    var error = document.getElementById("pin-gate-error");
    var failedAttempts = 0;

    input.addEventListener("input", function () {
      input.value = input.value.replace(/\D/g, "").slice(0, 4);
      error.textContent = "";
      input.removeAttribute("aria-invalid");
    });

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      if (!/^[0-9]{4}$/.test(input.value)) {
        error.textContent = "PIN phải có đúng 4 chữ số.";
        input.setAttribute("aria-invalid", "true");
        input.focus();
        return;
      }

      gate.setAttribute("aria-busy", "true");
      input.disabled = true;
      button.disabled = true;
      button.textContent = "Đang mở...";
      error.textContent = "";

      try {
        var pageHtml = await decryptChapter(gate, input.value);
        var fragment = document.createRange().createContextualFragment(pageHtml);
        gate.replaceWith(fragment);
        document.dispatchEvent(new CustomEvent("aiops:chapter-unlocked"));

        if (window.location.hash) {
          window.requestAnimationFrame(function () {
            var target = document.getElementById(window.location.hash.slice(1));
            if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
          });
        } else {
          window.scrollTo({ top: 0, behavior: "smooth" });
        }
      } catch (unlockError) {
        failedAttempts += 1;
        error.textContent = "PIN chưa đúng. Hãy kiểm tra và thử lại.";
        input.value = "";
        input.setAttribute("aria-invalid", "true");

        var delay = Math.min(failedAttempts * 600, 3000);
        window.setTimeout(function () {
          gate.removeAttribute("aria-busy");
          input.disabled = false;
          button.disabled = false;
          button.textContent = "Mở khóa";
          input.focus();
        }, delay);
      }
    });

    input.focus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPinGate, { once: true });
  } else {
    initPinGate();
  }
})();
