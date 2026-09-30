/**
 * skip-nav.js
 *
 * WCAG 2.4.1 — Bypass Blocks
 *
 * Injects a "Skip to main content" link as the very first focusable element
 * in the page.  The link is visually hidden until it receives keyboard focus,
 * at which point it appears at the top of the viewport (styled by
 * accessibility.css .skip-nav).
 *
 * The link targets the landmark <main> element that MkDocs Material renders
 * as the primary content region (role="main" / <main>).  If a more specific
 * anchor is needed the href can be changed to "#content" and an
 * id="content" attribute added to the appropriate element via a theme override.
 */
document.addEventListener("DOMContentLoaded", function () {
  var link = document.createElement("a");
  link.href = "#content";
  link.className = "skip-nav";
  link.textContent = "Skip to main content";

  /* Insert as the very first child of <body> so it is the first tab stop */
  var body = document.body;
  if (body.firstChild) {
    body.insertBefore(link, body.firstChild);
  } else {
    body.appendChild(link);
  }

  /*
   * MkDocs Material wraps content in a <div class="md-content"> container.
   * Add id="content" to that element so the skip link has a valid target.
   * If the element is not found we fall back gracefully — the link still
   * works as a "skip to top" shortcut.
   */
  var main = document.querySelector('[data-md-component="content"]') ||
             document.querySelector(".md-content") ||
             document.querySelector("main") ||
             document.querySelector('[role="main"]');

  if (main && !main.id) {
    main.id = "content";
  }
});
