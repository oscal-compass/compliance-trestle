# Accessibility

Compliance Trestle is committed to making both the project site and its results
accessible to persons with disabilities where it is reasonable to do so.  This
document describes the accessibility measures taken, the guidelines followed, and
known limitations.

---

## Project type and scope

Compliance Trestle is primarily a **command-line application and Python library**.
Command-line interfaces are generally accessible as-is because they work with any
terminal emulator, including those used by screen-reader users (e.g. a Braille
terminal, or NVDA with a console window).

The project also publishes a **documentation website** built with
[MkDocs Material](https://squidfunk.github.io/mkdocs-material/).  The
accessibility measures below apply to that site.

---

## Guidelines followed

The documentation site targets conformance with
**[Web Content Accessibility Guidelines (WCAG) 2.0](https://www.w3.org/TR/WCAG20/)**
Level AA.  The specific criteria addressed are:

| WCAG criterion | Measure taken |
|---|---|
| **1.1.1 Non-text content** — text alternatives for images | All informative images in the documentation carry descriptive `alt` text that conveys the same information as the visual.  Decorative images use descriptive context. |
| **1.4.1 Use of colour** — colour not used as the only means of conveying information | Code blocks use syntax labels and/or contextual prose in addition to colour highlighting. |
| **1.4.3 Contrast (Minimum)** — text contrast ≥ 4.5:1 | The documentation site ships a **light/dark theme toggle** (respecting `prefers-color-scheme`) so users can choose the scheme that provides adequate contrast for them.  Both the default (light) and slate (dark) palettes use black primary headings against a white/dark background, meeting the 4.5:1 requirement. |
| **2.1.1 Keyboard** — all functionality available from keyboard | MkDocs Material's navigation is keyboard-accessible.  A **"Skip to main content"** link is injected as the first focusable element on every page so keyboard-only users can bypass the navigation bar. |
| **2.4.1 Bypass blocks** | Skip-navigation link provided (see above). |
| **2.4.7 Focus visible** | A high-contrast focus ring (3 px solid `#005eb8`) is applied to all interactive elements via `docs/css/accessibility.css`. |
| **3.1.1 Language of page** | `<html lang="en">` is set via the `language: en` MkDocs theme option. |

### Reduced-motion

Users who have enabled the operating-system "reduce motion" preference will
experience disabled CSS transitions and animations on the documentation site,
in line with the `prefers-reduced-motion` media query.

---

## Screen-reader testing

The documentation site has been verified for basic screen-reader compatibility
using **Orca** (GNOME, Linux) against the rendered HTML.  The skip-navigation
link and ARIA landmark structure provided by MkDocs Material allow Orca users
to reach the main content without traversing the full navigation sidebar.

If you encounter a problem reading the documentation with a different
screen-reader, please [open an issue](https://github.com/oscal-compass/compliance-trestle/issues)
so it can be investigated.

---

## Command-line interface accessibility

The `trestle` CLI:

- Outputs plain text to `stdout` / `stderr`, which works with any terminal
  screen-reader or Braille display.
- Does not rely on colour alone to signal success or failure: every status
  message carries a textual prefix (`INFO`, `WARNING`, `ERROR`) that is
  meaningful without colour.
- Supports `--help` on all sub-commands, providing a full description of
  options and arguments in plain text.
- Does not use cursor-positioning (`ncurses`-style) TUI elements that can
  cause screen-reader overdraw.

---

## Known limitations

- The architecture diagram (`docs/assets/Canonical_trestle_auditree_workflows.png`)
  is a complex `.drawio` export.  A textual description of that diagram is
  available in the accompanying `docs/architecture.md` page.
- The MkDocs Material version-selector dropdown (provided by the `mike`
  plugin) may have limited keyboard accessibility depending on the browser.
- Third-party badge images served from `shields.io` embed their text in SVG;
  screen-readers may not announce them consistently.  All badges on the
  project home page carry `alt` text that conveys the same information.

---

## Feedback

If you discover an accessibility barrier not listed here, please
[open an issue](https://github.com/oscal-compass/compliance-trestle/issues)
with the label `accessibility`.  We welcome pull requests that improve
accessibility.
