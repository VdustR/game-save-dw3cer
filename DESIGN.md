---
name: DW3CER Save Patch
description: A local save workbench with a green-black game-menu identity.
colors:
  paper: "#121714"
  ink: "#eee8d7"
  muted: "#b5b9a7"
  rule: "#465044"
  accent: "#e0bd77"
  wash: "#1c2620"
  red: "#8e302e"
  red-hover: "#ab3d36"
  success: "#a9c99b"
  error: "#ffada0"
  disabled: "#353d31"
  selected: "#293324"
typography:
  display:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "42px"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Fraunces, Georgia, serif"
    fontSize: "27px"
    fontWeight: 400
    lineHeight: 1.25
  body:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "16px"
    lineHeight: 1.6
  control:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "16px"
    fontWeight: 600
  preset-title:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "20px"
    fontWeight: 600
  hash:
    fontFamily: "monospace"
    fontSize: "12px"
    lineHeight: 1.7
rounded:
  control: "2px"
spacing:
  control-gap: "12px"
  mobile-gutter: "22px"
  section-gap: "40px"
  desktop-gutter: "48px"
components:
  button-primary:
    backgroundColor: "{colors.red}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.red-hover}"
  button-file:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.paper}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "12px 20px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "12px 20px"
  button-disabled:
    backgroundColor: "{colors.disabled}"
    textColor: "{colors.muted}"
  preset:
    rounded: "{rounded.control}"
    padding: "17px 16px"
  preset-selected:
    backgroundColor: "{colors.selected}"
  result:
    backgroundColor: "{colors.wash}"
    padding: "28px"
---

# Design System: DW3CER Save Patch

## Overview

**Creative North Star: "The Campaign Workbench"**

A simple community save tool uses limited game-menu cues: green-black surfaces, antique gold, ivory text, crimson actions, and fine rectangular frames. The palette draws on the official DW3 Remastered Lu Bu reference described in [the visual direction](docs/visual-direction.md). Character artwork belongs only in the OG image, not the operating interface.

The continuous workspace supports choosing a local file, selecting a preset, and downloading a patched copy. Serif headings provide restrained game identity while readable sans-serif controls, persistent status, and a results ledger keep operation clear. Installation guidance and verification limits remain part of the interface.

**Key Characteristics:**

- Dark tonal surfaces and fine rectangular frames.
- Gold file selection and navigation; crimson patch and download actions.
- Serif identity paired with compact, readable native controls.
- Visible processing states, experimental labels, and verification limits.

This document records `src/style.css` and `index.html`. It is an implemented system, not a generated visual seed or a claim of completed Impeccable gates.

## Colors

### Primary

- **Antique Gold** (`accent`): title emphasis, file selection, links, selection borders, and focus outlines.
- **Crimson** (`red`, `red-hover`): patch and patched-save download actions.

### Neutral

- **Green Black** (`paper`): page background and dark text on gold buttons.
- **Ivory** (`ink`): main text and crimson-button labels.
- **Muted Sage** (`muted`): explanations, metadata, and inactive status.
- **Dark Green Wash** (`wash`): file well, results, and hover surfaces.
- **Frame Green** (`rule`): section dividers and neutral control borders.
- **Selected Green** (`selected`): selected preset surface.
- **Disabled Green** (`disabled`): unavailable buttons and file selection.

Success and error tokens communicate processing outcomes. Error text accompanies the state indicator; color alone does not carry the message.

**The Action Color Rule.** Gold identifies file selection and navigation; crimson identifies patching and patched-output download. Keep these roles consistent.

## Typography

- **Display Font:** Fraunces, with Georgia and serif fallbacks.
- **Body Font:** Source Sans 3, with a sans-serif fallback.
- **Hash Font:** Monospace.

The serif gives the task heading and section headings their identity. Sans-serif text carries instructions, controls, presets, and status. Hashes use a compact monospace treatment and wrap rather than expanding the page.

The frontmatter records the desktop roles. Below 760px, the main heading reduces to 32px. Verification headings use 30px on desktop and 27px on mobile. Introductory and instructional copy use 16px; supporting text uses the observed 13–15px range.

**The Readable Control Rule.** Keep controls in Source Sans 3; reserve Fraunces for headings and game identity. Use tabular numbers for the file ledger.

## Layout

The page is one centered continuous workspace with a 1280px maximum width and desktop gutters from the spacing tokens. Thin rules separate the header, page navigation, workbench, guidance, verification, and footer.

The introduction is a short task heading followed by the game and platform, with 32px top and 28px bottom padding. The desktop header has a 76px minimum height. The workbench uses a 1:1.05 ratio, a dividing rule, and 40px of padding beside that rule. Guidance and footer use 1:2 columns with a 40px gap. Source text stays within 48ch; introductory and guidance text stay within 72ch.

Below 760px, the page uses mobile gutters and one-column sections. The introduction uses 24px vertical padding. Page navigation remains available and wraps. The mobile file well uses 18px by 16px padding, no minimum height, and no decorative file icon. Download buttons expand to full width.

## Elevation & Depth

There are no box shadows. Depth comes from green tonal layering, contrasting frames, and fine dividers. The result panel has a success-colored top rule. Avoid introducing floating cards into the continuous workbench.

**The Framed Surface Rule.** Use a border or tonal surface to group related content; preserve the flat menu structure.

## Shapes

Large surfaces are rectangular. Buttons and preset rows use the control radius in the frontmatter. Numbered steps are square frames; circular status dots are reserved for processing state. Borders are generally 1px; the result's top rule and focus outlines are 2px. The file well uses a dashed frame to distinguish file selection from preset selection.

## Components

### Buttons

Gold file selection, crimson primary actions, and transparent secondary actions share the control typography, padding, and radius. Buttons have a 48px minimum height. Gold hover and pressed states lighten and deepen the gold; crimson states use the red hover token and a deeper pressed red. Background and text transitions last 0.18s. Disabled controls use the disabled and muted tokens and a disallowed cursor.

Keyboard focus uses a gold outline offset by 4px. The hidden native file input instead outlines its visible label with a 5px offset. Reduced-motion preferences remove button transitions.

### File Selection

The native file input is visually hidden behind a gold label. The desktop well uses a green wash, dashed frame, centered file icon, and filename text that wraps. Its focused label and visible loading/error message carry state independently of the icon.

### Preset Rows and Options

Native radios sit beside a title, explanatory copy, and gold detail line. Rows use a fine frame, 13px internal gap, and the preset padding from the frontmatter. Hover adds a green wash; selection adds selected green and a gold border. Native checkbox controls use the same accent color. Experimental status stays in text beside the affected choice.

### Navigation

The wordmark uses the same game icon as the favicon, displayed at 32px beside the product name. Page navigation is a horizontal row between fine rules, with 48px minimum link height and gold hover text. It wraps on mobile. Links, the skip link, and disclosure summaries retain visible keyboard focus.

### Status and Results

Status uses an 8px dot beside readable text. Busy state pulses over 1.5s; success and error use their respective tokens. Reduced motion removes the pulse. The result surface uses the green wash, success top rule, hash ledger, and wrapping download row; it remains hidden until output exists.

### Disclosures and Ledgers

A native details element starts closed and exposes included changes on demand, with a 44px minimum-height summary. File and result ledgers use fine row dividers, muted labels, and wrapped hashes. Preserve native semantics and text labels when extending these patterns.

## Do's and Don'ts

### Do:

- **Do** preserve the gold file-selection and crimson output-action roles.
- **Do** use fine frames and tonal surfaces to organize the continuous workspace.
- **Do** keep native controls, visible focus, readable state text, and reduced-motion behavior.
- **Do** preserve the short introduction and compact mobile file-selection well.
- **Do** state experimental and verification limits beside the affected behavior.

### Don't:

- **Don't** restore the former warm-paper editorial palette as the default world.
- **Don't** add shadows, rounded floating cards, or character artwork to the website UI. Character artwork is reserved for the OG image.
- **Don't** imply official endorsement, guaranteed compatibility, or unverified gameplay benefits.
- **Don't** document unavailable artwork, generated compositions, or formal gate success as implemented assets.
