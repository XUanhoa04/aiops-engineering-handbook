"""Encrypt the interview chapter during MkDocs build and render a PIN gate.

This is client-side protection for a static site.  It prevents the chapter body
from being shipped as plaintext HTML or added to MkDocs search, but a four-digit
PIN is not a substitute for server-side authentication.
"""

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


PROTECTED_SOURCE_URI = "vi/22-aiops-interview-scenarios/README.vi.md"
CHAPTER_PIN = "1902"
PBKDF2_ITERATIONS = 240_000


def _b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _derive_key(pin: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(pin.encode("utf-8"))


def _gate_html(page_html: str, pin: str) -> str:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    aad = PROTECTED_SOURCE_URI.encode("utf-8")
    ciphertext = AESGCM(_derive_key(pin, salt)).encrypt(
        nonce,
        page_html.encode("utf-8"),
        aad,
    )

    return f"""
<section
  id="pin-protected-chapter"
  class="pin-gate"
  data-salt="{_b64(salt)}"
  data-nonce="{_b64(nonce)}"
  data-aad="{PROTECTED_SOURCE_URI}"
  data-iterations="{PBKDF2_ITERATIONS}"
  aria-labelledby="pin-gate-title"
>
  <div class="pin-gate__card">
    <div class="pin-gate__lock" aria-hidden="true">&#128274;</div>
    <p class="pin-gate__eyebrow">PROTECTED CHAPTER</p>
    <h1 id="pin-gate-title">Bộ câu hỏi phỏng vấn AIOps</h1>
    <p class="pin-gate__description">
      Chapter này được bảo vệ. Nhập mã PIN 4 chữ số để đọc 70 tình huống
      Intern/Junior và các framework trả lời.
    </p>
    <form id="pin-gate-form" class="pin-gate__form" novalidate>
      <label for="pin-gate-code">Mã PIN</label>
      <div class="pin-gate__controls">
        <input
          id="pin-gate-code"
          class="pin-gate__input"
          name="pin"
          type="password"
          inputmode="numeric"
          pattern="[0-9]{{4}}"
          minlength="4"
          maxlength="4"
          autocomplete="off"
          aria-describedby="pin-gate-help pin-gate-error"
          required
        >
        <button class="md-button md-button--primary pin-gate__button" type="submit">
          Mở khóa
        </button>
      </div>
      <p id="pin-gate-help" class="pin-gate__help">Chỉ nhập 4 chữ số.</p>
      <p id="pin-gate-error" class="pin-gate__error" role="alert" aria-live="polite"></p>
    </form>
  </div>
  <script id="pin-protected-payload" type="application/octet-stream">{_b64(ciphertext)}</script>
  <noscript>Trình duyệt cần bật JavaScript để mở chapter này.</noscript>
</section>
""".strip()


def on_page_content(html: str, page, **kwargs) -> str:
    """Replace the protected page body before search/template rendering."""

    if page.file.src_uri.replace("\\", "/") != PROTECTED_SOURCE_URI:
        return html

    # Do not leak the question headings through Material's server-rendered TOC.
    hidden_sections = page.meta.setdefault("hide", [])
    if "toc" not in hidden_sections:
        hidden_sections.append("toc")
    # Material also nests page headings below the active item in the primary
    # navigation. Clearing the generated TOC keeps those titles out of source.
    page.toc.items.clear()

    return _gate_html(html, CHAPTER_PIN)
