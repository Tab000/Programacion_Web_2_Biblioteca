---
name: Academic Nexus
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#444651'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#757682'
  outline-variant: '#c5c5d3'
  surface-tint: '#4059aa'
  primary: '#00236f'
  on-primary: '#ffffff'
  primary-container: '#1e3a8a'
  on-primary-container: '#90a8ff'
  inverse-primary: '#b6c4ff'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#003120'
  on-tertiary: '#ffffff'
  tertiary-container: '#004a32'
  on-tertiary-container: '#4ac08f'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164e'
  on-primary-fixed-variant: '#264191'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  code-catalog:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style
The design system embodies academic rigor, structural clarity, and administrative efficiency. Built for researchers, faculty, library administrators, and students, the interface prioritizes high-trust utility, seamless catalog discoverability, and friction-free circulation workflows.

The visual direction follows **Corporate / Modern** principles adapted for academia:
- **Tone:** Authoritative, reliable, organized, and quietly sophisticated.
- **Visual Texture:** Uncluttered white and slate surfaces with high functional contrast, subtle structural dividers, and purposeful status signals.
- **Emotional Impact:** A sense of calm order, institutional integrity, and intellectual focus, avoiding loud ornamentation in favor of precision typography and ergonomic density.

## Colors
The color palette communicates institutional stability and provides unambiguous semantic feedback across library cataloging and circulation states:

- **Primary (`#1e3a8a` Deep Navy):** Used for navigation headers, institutional identity, high-level structural framing, and primary CTA anchors.
- **Secondary (`#2563eb` Royal Blue):** Used for interactive triggers, focused input outlines, active tabs, and secondary actions.
- **Semantic Status Signals:**
  - **Success / Available (`#059669` Emerald, background `#d1fae5`):** Denotes physical item availability, successful checkouts, and valid return verifications.
  - **Warning / Due Soon (`#d97706` Amber, background `#fef3c7`):** Marks upcoming loan expiries, reservation waiting queues, and threshold alerts.
  - **Danger / Fines / Critical (`#dc2626` Crimson, background `#fee2e2`):** Highlights overdue fines, restricted administrative locks, and lost item reports.
- **Neutrals & Surfaces:**
  - **App Canvas:** `#f8fafc` (Slate 50) provides a soft, low-glare backdrop for prolonged reading and data processing.
  - **Cards & Surfaces:** `#ffffff` pure white.
  - **Borders & Dividers:** `#e2e8f0` (Slate 200) for clean containment.
  - **Text Neutral Primary:** `#0f172a` (Slate 900) for crisp readability.
  - **Text Neutral Muted:** `#64748b` (Slate 500) for metadata, call numbers, and shelf tags.

## Typography
Inter delivers mechanical clarity, high x-height, and legible tabular numbers essential for ISBNs, Dewey Decimal / LC Call Numbers, and circulation timestamps.

- **Numerics:** Open tabular figures (`tnum`) must be enforced on tables, stock counts, and fine balances.
- **Hierarchy:** Reserve `display-lg` and `headline-lg` for system landing pages and module dashboards. Administrative operational views rely on compact `headline-md` and `headline-sm` headers to maximize screen utility.
- **Metadata Handling:** Catalog classifications, barcodes, and rack locations use `label-md` or `label-sm` with upper tracking to establish immediate differentiation from publication titles and author names.

## Layout & Spacing
The layout follows a 12-column responsive fluid grid designed to support dense workflows on desktop terminals and focused single-column interactions on mobile catalog searches:

- **Desktop (1024px+):** 12-column grid with a fixed collapsible 260px administrative navigation sidebar. Content area uses `gutter-desktop: 1.5rem` and outer margins of `2rem`.
- **Tablet (768px - 1023px):** 8-column layout with fluid reflow; sidebars collapse into a slide-over panel. Gutters shift to `1.5rem`.
- **Mobile (<768px):** 4-column layout with `1rem` margins and `1rem` gutters. Data tables switch to card lists or horizontal swipe containers.
- **Rhythm:** An 8-point baseline governs spacing tokens (`space-xs` = 4px, `space-sm` = 8px, `space-md` = 16px, `space-lg` = 24px, `space-xl` = 32px). Interior card groupings leverage tight `0.5rem` to `1rem` relations to maintain contextual proximity between book metadata and checkout actions.

## Elevation & Depth
Depth in the system is understated and structural, preserving an uncluttered environment suitable for long operational shifts:

- **Layer 0 (Canvas):** `#f8fafc` baseline background.
- **Layer 1 (Cards, Data Panels, Form Sections):** `#ffffff` surfaces bordered with a 1px solid line (`#e2e8f0`) and backed by a subtle ambient shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.03)`.
- **Layer 2 (Hovered Cards, Dropdowns, Flyouts):** Surfaces lift slightly using `0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`.
- **Layer 3 (Modals, Checkout Confirmation Drawers):** High-level overlays framed with `0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.04)` over a 40% opacity slate backdrop (`rgba(15, 23, 42, 0.4)`).
- **Interactive Depth:** Elements never use skeuomorphic extrusion; physical response is indicated by crisp 1px borders transitioning to `#2563eb` with a 2px focus ring (`rgba(37, 99, 235, 0.15)`).

## Shapes
The system employs a crisp, disciplined shape language (`roundedness: 1`):
- **Base Components:** Standard inputs, buttons, table cells, and badges carry `0.25rem` (4px) corner radii.
- **Containers & Panels:** Cards, search filter blocks, and modals use `rounded-lg` at `0.5rem` (8px).
- **Pill Exceptions:** Status badges and item availability chips use fully rounded pill geometry (`rounded-full` / `9999px`) to create clear visual divergence between interactive inputs (squared corners) and read-only status indicators.

## Components

### Buttons
- **Primary:** Background `#1e3a8a`, text `#ffffff`, border 1px solid `#1e3a8a`. Hover shifts to `#2563eb`. Focused with a 2px ring in `rgba(37, 99, 235, 0.25)`.
- **Secondary:** Background `#ffffff`, text `#1e3a8a`, border 1px solid `#cbd5e1`. Hover shifts to `#f8fafc` and border `#94a3b8`.
- **Destructive:** Background `#dc2626`, text `#ffffff`. Hover `#b91c1c`. Used strictly for fine cancellations, record purges, or user blocking.
- **Height & Spacing:** Compact height of 36px for operational density; 40px for primary form submit actions.

### Badges & Chips
- **Available:** Text `#065f46`, background `#d1fae5`, border 1px solid `#a7f3d0`.
- **Reserved / Due Soon:** Text `#92400e`, background `#fef3c7`, border 1px solid `#fde68a`.
- **Overdue / Fined / Restricted:** Text `#991b1b`, background `#fee2e2`, border 1px solid `#fecaca`.
- **Metadata Chips (Subjects, Genres):** Text `#475569`, background `#f1f5f9`, border 1px solid `#e2e8f0`.

### Data Tables (High-Density Catalog & Circulation)
- **Header:** Background `#f8fafc`, text `#475569`, font `label-sm`, uppercase tracking, bottom border 1px solid `#cbd5e1`.
- **Rows:** Alternating rows optional; standard uses `#ffffff` with 1px `#f1f5f9` bottom divider. Row hover effect uses `#f8fafc`.
- **Padding:** 10px vertical cell padding for compact administrative scanning, 16px horizontal gutter. Numeric and call number columns align right.

### Input Fields & Search Bars
- **Catalog Search Field:** Height 44px, leading icon (magnifier), trailing keyboard shortcut tag (`Ctrl+K` / `⌘K`). Border 1px solid `#cbd5e1`, border radius `0.375rem`.
- **Form Inputs:** 1px solid `#cbd5e1`, background `#ffffff`, padding `0.5rem 0.75rem`. Focus transition brings a border of `#2563eb` and shadow ring `0 0 0 3px rgba(37, 99, 235, 0.12)`.
- **Helper Texts & Validation:** Micro-copy uses `body-sm`. Error text in `#dc2626` paired with an inline circular alert icon; valid confirmations use `#059669`.

### Cards & Book Items
- **Structure:** `#ffffff` surface, 1px solid `#e2e8f0` border, `0.5rem` radius.
- **Book Item Card:** Left slot hosts thumbnail or barcode placeholder; right area stacks title (`headline-sm`), author (`body-md`), call number badge (`code-catalog`), and current availability badge.
- **Footer Section:** Border-top 1px solid `#f1f5f9`, housing quick actions like "Reserve", "Renew", or "View History".

### Checkboxes & Radios
- Size 16px × 16px, border 1.5px solid `#94a3b8`, radius 3px (checkbox) or 50% (radio).
- Active state fills with `#2563eb` with a white checkmark or dot.