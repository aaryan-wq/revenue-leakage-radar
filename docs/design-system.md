
# Revenue Leakage Radar, Design System v2.0

> **Single source of truth** for every UI component, page, and interaction in the application.
>
> **Design direction:** Apple built Stripe for enterprise finance teams.
>
> **Principles:** Apple precision • visionOS depth • Stripe clarity • Hermès restraint • Squarespace whitespace • itsoffbrand fluidity

This document supersedes Design System v1.0 entirely. Treat this as a design evolution, not a patch. Every visual decision must trace to a token defined here.

---

## 0. Preamble

### Purpose

Revenue Leakage Radar is premium financial software. Users are CFOs, VPs of Finance, and RevOps leaders evaluating recoverable revenue. The interface must feel **expensive before it feels technical**, calm, confident, executive, and trustworthy within 10 seconds.

### Tech Stack Assumptions

| Layer | Technology |
|-------|------------|
| Framework | Next.js 15 |
| Styling | Tailwind CSS |
| Components | shadcn/ui |
| Motion | Framer Motion |
| Icons | Lucide |
| Toasts | Sonner |
| Smooth scroll | Lenis |
| Font | Inter |

Token implementation lives in `apps/web/tailwind.config.ts` and `apps/web/app/globals.css`. This document defines the canonical values those files must mirror.

### What Changed in v2

| v1 | v2 |
|----|-----|
| Border-first, flat surfaces | Soft glass with layered depth |
| Motion for state only | Motion as first-class design primitive |
| Conservative radii | Large, premium border radii |
| Static interface | Reactive, alive interface |
| Generic enterprise UI | Executive workspace + consulting-grade reports |

---

## 1. Design Philosophy

### North Star

The application should feel like **Apple built Stripe for enterprise finance teams**.

### Primary Inspirations

Capture principles, never copy any website.

| Inspiration | What We Take |
|-------------|--------------|
| Apple hardware & visionOS | Precision, glass, depth, intentional motion |
| Stripe Dashboard | Clarity, density when needed, strong hierarchy |
| itsoffbrand.com | Fluid interactions, reactive layouts, delightful motion |
| Hermès | Luxury through restraint |
| Squarespace | Editorial whitespace, large typography |

### Overall Feel

The interface is:

- Premium
- Calm
- Modern
- Smooth
- Confident
- Executive
- Minimal

The interface is never:

- Corporate or generic SaaS
- Dark hacker aesthetic
- Loud gradients or glowing blobs
- Busy dashboards with widget grids
- Playful or consumer-flashy

### Design Priorities

Every screen optimizes for, in order:

1. **Trust**, the user never wonders what happens next
2. **Clarity**, financial evidence is immediately legible
3. **Hierarchy**, one hero metric, one primary action
4. **Whitespace**, breathing room over chrome
5. **Responsiveness**, the UI reacts to the user with subtle life

### Premium Rules

- One **primary CTA** per page maximum
- Maximum **three accent colors** visible on any screen
- Maximum **two elevation levels** visible simultaneously
- Prefer whitespace over dividers
- Every metric card emphasizes **one number only**
- All financial values use tabular numerals
- Motion is intentional and subtle, never flashy
- Soft glass only, no heavy glassmorphism, no visual noise

---

## 2. Visual Language, Soft Glass

### Concept

Adopt a **soft glass** system: frosted surfaces, layered depth, soft lighting, and extremely subtle transparency. Surfaces feel physical, like precision-machined hardware, without decorative effects.

### Surface Layers

```text
Layer 4  Toast / modal content     surface/glass-elevated + elevation/3–4
Layer 3  Modal backdrop            rgba(15,23,42,0.24) + blur/lg
Layer 2  Dropdowns, popovers        surface/glass-elevated + elevation/2
Layer 1  Cards, panels, nav         surface/glass + blur/lg + elevation/1
Layer 0  App background             surface/base
```

### Glass Recipe (Default Card)

| Property | Token | Value |
|----------|-------|-------|
| Background | `surface/glass` | `rgba(255, 255, 255, 0.72)` |
| Backdrop blur | `blur/lg` | `24px` |
| Border | `border/glass` | `1px solid rgba(255, 255, 255, 0.24)` |
| Inner highlight |, | `1px inset rgba(255, 255, 255, 0.50)` top edge |
| Shadow | `elevation/1` | See elevation tokens |
| Radius | `radius/card` | `24px` |

### Lighting

- Ambient light reads from top-left (subtle top inset highlight on glass)
- Hover brightens glass opacity by ~8% (`surface/glass` → `0.80`)
- Focus adds blue ring, never neon glow
- Cursor-aware lighting on hero cards and upload zone (optional, max 15% luminance shift)

### Anti-Patterns

Never use:

- Heavy glassmorphism (high blur + high transparency + strong borders stacked)
- Glowing blobs or aurora backgrounds
- Loud multi-stop gradients
- Neumorphism
- Oversized decorative icons
- Parallax that competes with content
- Bouncy or elastic animations
- Spinning logos as loading indicators

---

## 3. Design Tokens

Every visual decision maps to a token. Never invent arbitrary values in components.

### 3.1 Colors, Neutral Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `white` | `#FFFFFF` | Solid surfaces, text on dark |
| `gray-25` | `#FCFCFD` | Elevated solid fallback |
| `gray-50` | `#F8FAFC` | App background fallback |
| `gray-100` | `#F1F5F9` | Secondary backgrounds, table headers |
| `gray-200` | `#E2E8F0` | Solid borders |
| `gray-300` | `#CBD5E1` | Disabled borders, not-run status |
| `gray-400` | `#94A3B8` | Placeholder, disabled text |
| `gray-500` | `#64748B` | Secondary text, labels |
| `gray-700` | `#334155` | Supporting body text |
| `gray-900` | `#0F172A` | Headings, primary text |

### 3.2 Colors, Primary Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#0F172A` | Primary button background, headings |
| `primary-hover` | `#1E293B` | Primary button hover |
| `primary-active` | `#020617` | Primary button pressed |
| `primary-light` | `#F8FAFC` | Inverted text backgrounds |

### 3.3 Colors, Accent Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `blue` | `#2563EB` | Primary CTA, links, focus rings |
| `blue-hover` | `#1D4ED8` | CTA hover |
| `blue-light` | `#EFF6FF` | Selected rows, info backgrounds |

### 3.4 Colors, Semantic Palette

| Token | Hex | Background Token | Usage |
|-------|-----|------------------|-------|
| `success` | `#16A34A` | `success-bg` `#F0FDF4` | Passed, positive values |
| `warning` | `#D97706` | `warning-bg` `#FFFBEB` | Needs review, caution |
| `error` | `#DC2626` | `error-bg` `#FEF2F2` | Errors, critical findings |
| `info` | `#0284C7` | `info-bg` `#F0F9FF` | Informational states |

### 3.5 Colors, Surface Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `surface/base` | `#F8FAFC` with optional `radial-gradient(ellipse 80% 50% at 50% -20%, rgba(37,99,235,0.03), transparent)` | App background |
| `surface/glass` | `rgba(255, 255, 255, 0.72)` | Default cards, panels |
| `surface/glass-elevated` | `rgba(255, 255, 255, 0.88)` | Navigation, modals, dropdowns |
| `surface/glass-subtle` | `rgba(255, 255, 255, 0.48)` | Secondary panels, nested cards |
| `surface/glass-hover` | `rgba(255, 255, 255, 0.80)` | Interactive card hover |
| `surface/glass-active` | `rgba(255, 255, 255, 0.92)` | Pressed glass surfaces |

### 3.6 Colors, Border Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `border/default` | `rgba(15, 23, 42, 0.08)` | Hairline on base surfaces |
| `border/strong` | `rgba(15, 23, 42, 0.12)` | Emphasized dividers |
| `border/glass` | `rgba(255, 255, 255, 0.24)` | Glass surface edges |
| `border/focus` | `#2563EB` | Focus ring color |
| `border/error` | `#DC2626` | Validation errors |
| `border/success` | `#16A34A` | Success confirmation |

### 3.7 Colors, Glass Opacity Scale

| Token | Opacity | Usage |
|-------|---------|-------|
| `glass/opacity-subtle` | `0.48` | Nested, de-emphasized panels |
| `glass/opacity-default` | `0.72` | Standard cards |
| `glass/opacity-elevated` | `0.88` | Nav, modals |
| `glass/opacity-solid` | `0.96` | Near-opaque overlays |

### 3.8 Colors, Border Opacity Scale

| Token | Opacity | Usage |
|-------|---------|-------|
| `border-opacity/hairline` | `0.08` | Default hairlines |
| `border-opacity/medium` | `0.12` | Strong dividers |
| `border-opacity/glass` | `0.24` | Glass edge highlights |
| `border-opacity/focus` | `1.00` | Focus rings (solid) |

### 3.9 Colors, Revenue Severity

| Severity | Color | ARR Threshold |
|----------|-------|---------------|
| Critical | `#991B1B` | > $100k |
| High | `#DC2626` |, |
| Medium | `#EA580C` |, |
| Low | `#CA8A04` |, |
| Informational | `#0284C7` |, |

### 3.10 Colors, Verification Status

| State | Color Token |
|-------|-------------|
| Passed | `success` |
| Issue Found | `error` |
| Needs Review | `warning` |
| Not Run | `gray-300` |

### 3.11 Colors, Confidence Indicators

| Range | Color |
|-------|-------|
| 95–100% | `success` |
| 90–94% | `blue` |
| 80–89% | `warning` |
| < 80% | `gray-500` |

### 3.12 Typography, Font Family

| Token | Value |
|-------|-------|
| `font/sans` | Inter, system-ui, sans-serif |

### 3.13 Typography, Scale

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| `display-hero` | 5rem (80px) | 700 | 1.0 | -0.04em | Landing hero only |
| `display-xl` | 4rem (64px) | 700 | 1.0 | -0.04em | Report hero headlines |
| `display` | 3rem (48px) | 700 | 1.05 | -0.04em | Section heroes |
| `metric-xl` | 3rem (48px) | 700 | 1.0 | -0.03em | Dashboard hero metric (tabular-nums) |
| `h1` | 2.25rem (36px) | 700 | 1.1 | -0.03em | Page titles |
| `h2` | 1.875rem (30px) | 650 | 1.2 | -0.025em | Section headings |
| `h3` | 1.5rem (24px) | 650 | 1.25 | -0.02em | Subsection headings |
| `h4` | 1.25rem (20px) | 600 | 1.3 | -0.02em | Card titles |
| `large` | 1.125rem (18px) | 500 | 1.5 | -0.01em | Lead paragraphs |
| `body` | 1rem (16px) | 400 | 1.6 | -0.01em | Default body |
| `small` | 0.875rem (14px) | 400 | 1.5 | 0 | Secondary text |
| `caption` | 0.75rem (12px) | 500 | 1.4 | 0 | Metadata, timestamps |
| `overline` | 0.75rem (12px) | 600 | 1.4 | 0.08em | Section labels (uppercase) |

Financial numbers always use `font-variant-numeric: tabular-nums`.

### 3.14 Spacing Scale

Base unit: **4px**

| Token | REM | PX |
|-------|-----|-----|
| `space/1` | 0.25 | 4 |
| `space/2` | 0.5 | 8 |
| `space/3` | 0.75 | 12 |
| `space/4` | 1 | 16 |
| `space/5` | 1.25 | 20 |
| `space/6` | 1.5 | 24 |
| `space/8` | 2 | 32 |
| `space/10` | 2.5 | 40 |
| `space/12` | 3 | 48 |
| `space/16` | 4 | 64 |
| `space/20` | 5 | 80 |
| `space/24` | 6 | 96 |

### 3.15 Layout Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `layout/container-max` | 1280px | Page container |
| `layout/reading-width` | 760px | Long-form text, report narrative |
| `layout/card-padding` | 2rem (32px) | Default card interior |
| `layout/section-padding` | 6rem (96px) vertical | Standard sections |
| `layout/section-hero` | 8rem (128px) vertical | Landing hero sections |
| `layout/page-margin` | 2rem (32px) | Horizontal page margin |
| `layout/gap-sm` | 1rem (16px) | Tight groups |
| `layout/gap-md` | 2rem (32px) | Card grids |
| `layout/gap-lg` | 4rem (64px) | Section separation |

### 3.16 Grid

| Breakpoint | Columns | Gutter |
|------------|---------|--------|
| Desktop (≥1024px) | 12 | 32px |
| Tablet (768–1023px) | 8 | 24px |
| Mobile (<768px) | 4 | 16px |

### 3.17 Breakpoints

| Token | Value |
|-------|-------|
| `breakpoint/sm` | 640px |
| `breakpoint/md` | 768px |
| `breakpoint/lg` | 1024px |
| `breakpoint/xl` | 1280px |
| `breakpoint/2xl` | 1536px |

### 3.18 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius/button` | 14px | Buttons |
| `radius/input` | 14px | Inputs, selects |
| `radius/card` | 24px | Cards, panels |
| `radius/table` | 20px | Table containers |
| `radius/modal` | 32px | Modals, dialogs |
| `radius/hero` | 40px | Landing upload zone, hero panels |
| `radius/pill` | 999px | Badges, chips |

### 3.19 Elevation & Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `elevation/0` | none | Flat on base |
| `elevation/1` | `0 1px 2px rgba(15,23,42,0.04), 0 4px 16px rgba(15,23,42,0.04)` | Card resting |
| `elevation/2` | `0 4px 12px rgba(15,23,42,0.06), 0 12px 32px rgba(15,23,42,0.08)` | Card hover, dropdown |
| `elevation/3` | `0 8px 24px rgba(15,23,42,0.08), 0 24px 48px rgba(15,23,42,0.12)` | Modal |
| `elevation/4` | `0 12px 32px rgba(15,23,42,0.10), 0 32px 64px rgba(15,23,42,0.14)` | Toast |

Legacy aliases (for migration): `shadow/card` = `elevation/1`, `shadow/card-hover` = `elevation/2`, `shadow/modal` = `elevation/3`.

### 3.20 Blur

| Token | Value | Usage |
|-------|-------|-------|
| `blur/sm` | 8px | Subtle frosting |
| `blur/md` | 16px | Inputs, nested glass |
| `blur/lg` | 24px | Default glass surfaces |
| `blur/xl` | 40px | Hero overlays, modal backdrop |

### 3.21 Motion, Durations

| Token | Value | Usage |
|-------|-------|-------|
| `duration/instant` | 100ms | Button press, micro-feedback |
| `duration/fast` | 150ms | Hover transitions, toasts |
| `duration/normal` | 200ms | Card hover, focus, sort |
| `duration/moderate` | 300ms | Page enter, modal, charts |
| `duration/slow` | 400ms | Staggered reveals |
| `duration/reveal` | 500ms | Hero entrances, section reveals |

### 3.22 Motion, Easing

| Token | Value | Usage |
|-------|-------|-------|
| `ease/out` | `cubic-bezier(0.16, 1, 0.3, 1)` | Default exit/hover |
| `ease/in-out` | `cubic-bezier(0.45, 0, 0.55, 1)` | Page transitions |
| `ease/linear` | `linear` | Shimmer, progress fill |
| `spring/snappy` | `stiffness: 400, damping: 30` | Buttons, toggles |
| `spring/gentle` | `stiffness: 260, damping: 28` | Cards, modals, upload |

### 3.23 Motion, Stagger

| Token | Value | Usage |
|-------|-------|-------|
| `stagger/fast` | 40ms | List items, table rows |
| `stagger/normal` | 60ms | Card grids |
| `stagger/slow` | 80ms | Hero text lines |

### 3.24 Z-Index

| Token | Value | Layer |
|-------|-------|-------|
| `z/base` | 0 | Default content |
| `z/sticky` | 10 | Sticky navigation |
| `z/dropdown` | 20 | Dropdowns, popovers |
| `z/modal` | 30 | Modal backdrop |
| `z/modal-content` | 40 | Modal content |
| `z/toast` | 50 | Toasts (Sonner) |

---

## 4. Motion System

Motion is a **first-class design primitive**. Every interaction should feel responsive, intentional, and subtle. Use **Framer Motion** for all UI animation.

### 4.1 Principles

- Motion communicates hierarchy, state, and confidence, not decoration
- Duration stays within token scale, never exceed 500ms for UI transitions
- Prefer `ease/out` and `spring/gentle` over bouncy springs
- Always provide `prefers-reduced-motion` fallbacks
- Use `AnimatePresence` for mount/unmount transitions
- Use `layout` prop for list reordering and sort changes

### 4.2 Page Transitions

| Property | Value |
|----------|-------|
| Enter | `opacity: 0 → 1`, `y: 8 → 0` |
| Exit | `opacity: 1 → 0`, `y: 0 → -4` |
| Duration | `duration/moderate` (300ms) |
| Easing | `ease/out` |
| Implementation | `AnimatePresence` + `motion.div` on route wrapper |

**Reduced motion:** opacity only, `duration/fast` (150ms), no vertical shift.

### 4.3 Card Hover

| Property | Value |
|----------|-------|
| Translate Y | `0 → -4px` |
| Shadow | `elevation/1 → elevation/2` |
| Glass opacity | `surface/glass → surface/glass-hover` |
| Duration | `duration/normal` (200ms) |
| Optional tilt | Max 2° on pointer position, `spring/gentle` |

**Reduced motion:** shadow change only, no translate or tilt.

### 4.4 Button Press

| Property | Value |
|----------|-------|
| Hover | `filter: brightness(1.04)` |
| Active / tap | `scale: 0.98` |
| Duration | `duration/instant` (100ms) tap, `duration/fast` (150ms) hover |
| Easing | `spring/snappy` for tap |

### 4.5 Table Sorting

| Element | Motion |
|---------|--------|
| Sort chevron | `rotate: 0 → 180°`, 200ms |
| Row reorder | `layout` animation on tbody rows |
| Active column header | `color` transition to `blue`, 150ms |

**Reduced motion:** instant reorder, no layout animation.

### 4.6 Modal Opening

| Element | Motion |
|---------|--------|
| Backdrop | `opacity: 0 → 1`, 200ms |
| Backdrop blur | `blur: 0 → 24px`, 200ms |
| Content | `opacity: 0 → 1`, `scale: 0.96 → 1`, `spring/gentle` |
| Exit | Reverse, `duration/fast` |

**Reduced motion:** opacity only on backdrop and content.

### 4.7 Upload Progress

| Stage | Motion |
|-------|--------|
| Drag enter | Border color → `blue`, glass brighten, `duration/fast` |
| Drag active | Subtle scale `1 → 1.01`, border pulse (opacity oscillation) |
| Step progress | Horizontal fill animation, `duration/moderate`, `ease/linear` |
| Step complete | Checkmark scale-in `0 → 1`, `spring/snappy` |
| Success | Icon morph to green check, content crossfade |
| Error | Subtle shake `x: [0, -4, 4, -4, 0]`, once, 300ms |

### 4.8 Loading Transitions

| Pattern | Spec |
|---------|------|
| Skeleton shimmer | Gradient sweep left-to-right, 1.5s loop, `ease/linear` |
| Content reveal | Skeleton crossfade to content, `opacity`, 200ms |
| Inline spinner | Never use for page-level loading |
| Progress bar | Determinate fill with stage labels |

### 4.9 Skeleton Loading

| Surface | Skeleton |
|---------|----------|
| Metric card | One large rectangle (value) + two small (label, support) |
| Table | 8 rows, alternating widths |
| Card grid | Match card aspect ratio |
| Report section | Heading bar + 3 paragraph lines |

Shimmer uses `gray-100` → `gray-50` → `gray-100` sweep.

### 4.10 Scroll Animations

| Pattern | Spec |
|---------|------|
| Section reveal | `whileInView: { opacity: 1, y: 0 }`, initial `{ opacity: 0, y: 24 }` |
| Trigger | `viewport: { once: true, margin: "-80px" }` |
| Stagger children | `staggerChildren: 0.06` |
| Duration | `duration/moderate` per child |

**Reduced motion:** elements appear at full opacity with no transform.

### 4.11 Staggered Reveals

Use for card grids, metric rows, feature lists, and hero text lines.

```text
Parent: staggerChildren 0.06, delayChildren 0.1
Child:  opacity 0→1, y 16→0, duration/moderate, ease/out
```

### 4.12 Metric Counters

| Property | Value |
|----------|-------|
| Trigger | `whileInView`, once |
| Animation | Count from 0 to value over 800ms |
| Easing | `ease/out` |
| Format | Tabular nums, locale currency |

**Reduced motion:** display final value immediately.

### 4.13 Toast (Sonner)

| Property | Value |
|----------|-------|
| Position | Top right |
| Enter | Slide up 8px + fade in, `duration/fast` |
| Exit | Fade out, `duration/fast` |
| Auto-dismiss | 4 seconds |
| Stack | Max 3 visible |

### 4.14 Smooth Scroll (Lenis)

| Context | Lenis |
|---------|-------|
| Landing page | Enabled |
| Report reading view | Enabled |
| Dashboard with data tables | Disabled |
| Modal open | Disabled |

Duration: ~1.2s equivalent feel. Respect `prefers-reduced-motion`, disable Lenis entirely.

### 4.15 Reduced Motion Policy

When `prefers-reduced-motion: reduce` is active:

- Disable: tilt, scroll reveals, counters, Lenis, idle float loops
- Keep: opacity transitions ≤ 150ms for essential state feedback
- Keep: focus rings, error border color changes
- Never: remove loading indicators, swap animation for static skeleton

---

## 5. Reactive Interface

The UI subtly responds to the user. Everything feels alive without distracting from financial content.

### 5.1 Reactive Patterns

| Pattern | Behavior | Where |
|---------|----------|-------|
| Card lift | `y: -4px` + elevation on hover | Clickable cards |
| Cursor-aware lighting | Radial highlight follows pointer, max 15% luminance | Hero upload zone, feature cards |
| Gentle tilt | Max 2° rotateX/Y from pointer | Landing feature cards only |
| Interactive upload zone | Border pulse, glass brighten on drag | Upload flow |
| Animated progress | Staged stepper with fill | Analysis pipeline |
| Metric counters | Count-up on viewport entry | Dashboard hero metric |
| Smooth transitions | Crossfade between states | Loading → content |
| Link underline | Width grow left-to-right on hover | Inline links |

### 5.2 Alive-but-Calm Rules

- Maximum one ambient animation per viewport (e.g., upload zone idle float OR background subtlety, not both)
- Idle loops must be ≤ 2px amplitude, ≥ 4s period
- Reactive effects never shift layout or obscure text
- Disable all reactive effects under `prefers-reduced-motion`

---

## 6. Layout & Grid

### 6.1 Page Anatomy

Every page follows:

```text
Header (sticky nav)
  ↓
Primary Content (hero metric or headline)
  ↓
Secondary Content (supporting cards, tables)
  ↓
Footer / Actions
```

### 6.2 Container Rules

- Centered container, max `layout/container-max` (1280px)
- Readable narrative content max `layout/reading-width` (760px)
- Avoid edge-to-edge layouts on desktop
- Consistent `layout/section-padding` between major sections
- Desktop first, then tablet, then mobile, layout changes only, never business logic

### 6.3 Navigation

- Top navigation only during MVP
- Sticky, 72px height
- `surface/glass-elevated` + `blur/lg`
- Hairline `border/default` bottom border
- Logo left, actions right
- Navigation never competes with page content
- No sidebar unless explicitly specified

---

## 7. Component Specifications

Each component spec includes: Role, Anatomy, Variants, Layout, States, Motion, Accessibility, Do/Don't.

---

### 7.1 Buttons

**Role:** Trigger actions. One primary per page.

**Variants:** Primary · Secondary · Ghost · Danger · Glass

| Variant | Background | Text | Border |
|---------|------------|------|--------|
| Primary | `primary` | `white` | none |
| Secondary | `surface/glass` | `gray-900` | `border/default` |
| Ghost | transparent | `gray-700` | none |
| Danger | `error` | `white` | none |
| Glass | `surface/glass-subtle` | `gray-900` | `border/glass` |

**Layout:**

| Size | Height | Padding X | Font |
|------|--------|-----------|------|
| Small | 40px | 16px | `small` |
| Medium | 48px | 20px | `body` |
| Large | 56px | 24px | `large` |

Radius: `radius/button` (14px).

**States:**

| State | Appearance |
|-------|------------|
| Default | As variant table |
| Hover | Primary → `primary-hover`; others → brightness +4% |
| Focus | `2px solid border/focus`, 2px offset ring |
| Active | `scale: 0.98` |
| Disabled | `gray-100` bg, `gray-400` text, no pointer |
| Loading | Label replaced by spinner dot pulse; disabled interaction |

**Motion:** Hover brightness 150ms; tap scale `spring/snappy`; loading fade 150ms.

**Accessibility:** Min 44px touch target; `aria-busy` when loading; visible focus ring.

**Do:** One primary CTA per page. **Don't:** Multiple competing primary buttons. Blue-filled primary (reserve blue for links/CTA accent on secondary actions).

---

### 7.2 Cards

**Role:** Primary layout primitive for metrics, findings, and content grouping.

**Anatomy:** Glass surface · optional header · body · optional footer action

**Layout:**

- Padding: `layout/card-padding` (32px)
- Gap between internal elements: `space/4` (16px)
- Radius: `radius/card` (24px)
- Background: `surface/glass` + `blur/lg`
- Border: `1px border/glass`
- Inner highlight: top inset `rgba(255,255,255,0.50)`

**States:**

| State | Appearance |
|-------|------------|
| Default | `elevation/1` |
| Hover (clickable) | `y: -4`, `elevation/2`, `surface/glass-hover` |
| Focus | Focus ring on clickable cards |
| Selected | `blue-light` background tint |
| Disabled | Reduced opacity 0.6 |

**Motion:** Hover lift 200ms; enter stagger with parent; optional 2° tilt on landing feature cards.

**Accessibility:** Clickable cards are `<button>` or `<a>` with clear label; not div-only click targets.

**Do:** One hero metric per card. **Don't:** Clutter with multiple large numbers.

---

### 7.3 Tables

**Role:** Display findings, audit data, and evidence lists.

**Layout:**

- Container: glass wrapper, `radius/table` (20px)
- Row height: 64px
- Header: `gray-100` background, `small` weight 600
- Borders: horizontal only (`border/default`)
- No vertical borders

**States:**

| State | Appearance |
|-------|------------|
| Default | White/glass row |
| Hover | `gray-25` background |
| Selected | `blue-light` background |
| Sorted column | Header text `blue`, chevron rotated |
| Empty | Full empty state component inside table |

**Motion:** Sort chevron rotate 200ms; `layout` row reorder; row enter stagger 40ms.

**Accessibility:** `<th scope="col">`; sortable headers are buttons; sticky header on long tables.

**Do:** Support empty, loading (8 skeleton rows), and error states. **Don't:** Dense compact rows below 56px.

---

### 7.4 Inputs

**Role:** Form fields, search, filters.

**Layout:**

- Height: 48px
- Padding: 16px horizontal
- Radius: `radius/input` (14px)
- Background: `surface/glass-subtle` (~60% opacity)
- Border: `border/default`

**States:**

| State | Appearance |
|-------|------------|
| Default | As layout |
| Hover | Border → `border/strong` |
| Focus | `border/focus` + `box-shadow: 0 0 0 3px rgba(37,99,235,0.20)` |
| Error | `border/error` + error message below in `error` color |
| Disabled | `gray-100` bg, `gray-400` text |
| Placeholder | `gray-400` |

**Motion:** Border and ring transition `duration/fast` (150ms).

**Accessibility:** Always pair with visible `<label>`; never placeholder-only labels; `aria-invalid` on error; `aria-describedby` for helper/error text.

---

### 7.5 Badges

**Role:** Severity, status, and category labels.

**Layout:**

- Height: 28px
- Padding: 0 12px
- Radius: `radius/pill`
- Font: `caption`

**Variants:** Success · Warning · Error · Info · Gray · Severity (Critical/High/Medium/Low)

| Variant | Background | Text |
|---------|------------|------|
| Success | `success-bg` | `success` |
| Warning | `warning-bg` | `warning` |
| Error | `error-bg` | `error` |
| Info | `info-bg` | `info` |
| Gray | `gray-100` | `gray-700` |

**States:** Static on hover. Subtle `scale: 0.95 → 1` on appear.

**Motion:** Appear scale-in `spring/snappy`. No hover animation.

---

### 7.6 Metrics

**Role:** Hero financial numbers, the product's primary trust signal.

**Anatomy:** Label · Value · Supporting text · optional trend

**Layout:**

| Element | Typography |
|---------|------------|
| Label | `overline` or `caption`, `gray-500` |
| Value | `metric-xl` or `display`, `gray-900`, tabular-nums |
| Supporting | `small`, `gray-500` |
| Trend | `small`, green (positive) or red (negative) |

Dashboard hero metric card: min height 180px, single large value at 48px+.

**Motion:** Counter count-up on viewport entry; trend arrow fade-in.

**Do:** One dominant number per card. **Don't:** Multiple competing large figures.

---

### 7.7 Navigation

**Role:** Global wayfinding. Minimal chrome.

**Layout:**

- Height: 72px
- Background: `surface/glass-elevated` + `blur/lg`
- Border bottom: `border/default`
- Position: sticky, `z/sticky`
- Logo left, nav links center or left, actions right

**States:**

| State | Appearance |
|-------|------------|
| Default | Glass elevated bar |
| Link hover | Text `gray-900`, subtle underline grow |
| Active route | Text `gray-900` weight 600, 2px bottom indicator `primary` |
| Scrolled | Slightly increased `elevation/1` (optional) |

**Motion:** Link underline width 0→100%, 150ms; active indicator slide between routes.

---

### 7.8 Upload Areas

**Role:** Centerpiece of the landing and upload flow. The product's front door.

**Layout:**

- Min height: 320px desktop, 240px mobile
- Radius: `radius/hero` (40px)
- Background: `surface/glass` + `blur/lg`
- Border: `2px dashed border/default`
- Icon: Lucide upload, 48px, `gray-400`
- Headline: `h3`
- Supporting: `body`, `gray-500`

**States:**

| State | Appearance | Motion |
|-------|------------|--------|
| Idle | Dashed border, upload icon | Optional 2px float loop, 4s |
| Drag enter | `blue` border, `blue-light` tint | Scale 1.01, glass brighten |
| Uploading | Progress bar + stage label | Determinate fill animation |
| Processing | 6-step stepper with animated fill | Step checkmarks scale-in |
| Uploaded | Green check, filename, replace/delete | Check morph |
| Error | `error` border, message, retry button | Shake once |

**Accessibility:** Drop zone is a focusable button; keyboard accessible file picker; `aria-describedby` for instructions; progress `aria-valuenow`.

**Do:** Make upload the visual centerpiece on landing. **Don't:** Hide upload below fold on desktop.

---

### 7.9 Dialogs

**Role:** Confirmations, detail drawers, focused tasks.

**Layout:**

- Max width: 640px (confirmation), 800px (detail)
- Padding: 32px
- Radius: `radius/modal` (32px)
- Background: `surface/glass-elevated` + `blur/lg`
- Backdrop: `rgba(15,23,42,0.24)` + `blur/lg`

**States:** Default · open · closing

**Motion:**

- Backdrop fade 200ms
- Content `scale: 0.96 → 1` + opacity, `spring/gentle`
- Exit reverse, `duration/fast`

**Dismiss:** ESC key · outside click · explicit close button

**Accessibility:** Focus trap; return focus on close; `role="dialog"` + `aria-modal="true"` + `aria-labelledby`.

---

### 7.10 Charts

**Role:** Visualize revenue opportunity and audit coverage in reports.

**Rules:**

- No gradients, no 3D, no decorative legends
- Muted palette: `blue` (revenue), `success` (recovered), `error` (risk)
- Background: `gray-50` or glass panel
- Types: bar, line, simple donut only

**Layout:** Embed in glass panel with `layout/card-padding`. Generous margin around chart area.

**Motion:** Restrained enter, bar grow from baseline, 300ms, `ease/out`. No continuous animation.

**Do:** Prioritize readability for executive presentation. **Don't:** Animate on every data refresh.

---

### 7.11 Toasts

**Role:** Transient feedback via Sonner.

| Variant | Icon color | Border |
|---------|------------|--------|
| Success | `success` | `success-bg` |
| Error | `error` | `error-bg` |
| Info | `info` | `info-bg` |

Position: top right. Auto-dismiss: 4s. Max 3 stacked.

**Motion:** Slide up 8px + fade, `duration/fast`.

---

### 7.12 Progress Indicator

**Role:** Multi-step analysis pipeline feedback.

- Horizontal stepper, 6 steps
- Steps: Upload → Validate → Map → Analyze → Verify → Report
- Active step: `blue` fill animation
- Completed: green checkmark scale-in
- Labels below each step in `caption`

**Motion:** Fill width `ease/linear`; checkmark `spring/snappy`.

---

### 7.13 Icons

| Property | Value |
|----------|-------|
| Library | Lucide only |
| Default size | 24px |
| Stroke | 1.75px |
| Style | Outline |

Icons support text, never replace labels. Never mix icon packs.

---

### 7.14 Findings Cards

**Role:** Surface revenue leakage findings with financial impact first.

**Layout (top to bottom):**

1. Priority / severity badge
2. ARR impact (hero number, tabular-nums)
3. Confidence score + affected accounts
4. Evidence summary (truncated)
5. Expand CTA

**Motion:** Staggered enter in list; expand/collapse height animation 300ms `ease/out`.

---

## 8. Page Patterns

### 8.1 Landing Page

Premium product-launch experience. Upload is the centerpiece.

**Structure:**

```text
Sticky nav (glass)
  ↓
Hero, display-hero headline, h3 subhead, single primary CTA
  ↓
Upload zone, above fold, hero radius, interactive glass panel
  ↓
Trust strip, logos or metrics in glass cards
  ↓
Feature sections, editorial layout, staggered scroll reveals
  ↓
Social proof / testimonial
  ↓
Footer CTA
```

**Typography:** `display-hero` for headline. Large, confident, minimal words.

**Motion:**

- Hero text: staggered fade-up, `stagger/normal`
- Upload zone: cursor-aware lighting; optional idle float ≤2px
- Features: `whileInView` stagger on scroll
- Page transition: fade + rise on route enter

**Layout:** Editorial whitespace. Asymmetric allowed. Max one visual focal point per viewport.

---

### 8.2 Executive Dashboard

Not a traditional SaaS dashboard. An executive workspace.

**Priority order (above fold):**

1. Revenue recovered, `metric-xl` hero
2. High-impact findings, top 3, severity-sorted
3. Audit coverage, percentage + scope summary
4. Next recommended actions, single clear CTA

**Layout rules:**

- One hero metric, 2–3 supporting glass cards maximum above fold
- No dense widget grids
- No sidebar
- Section gaps: `space/16` to `space/20`
- Large typography, breathing room, minimal chrome

**Motion:** Metric counter on load; finding cards stagger enter; subtle card hover lift.

---

### 8.3 Reports (Consulting Presentation)

Reports resemble McKinsey or Bain slide decks, evidence-first, executive-friendly.

**Structure (preserved flow):**

```text
Hero, Executive Summary
  ↓
Opportunity Breakdown
  ↓
Verification Checks
  ↓
Findings (evidence-first)
  ↓
Recommendations
  ↓
Downloads (PDF, CSV)
```

**Layout rules:**

- `layout/reading-width` for narrative; full width for tables and charts
- Large whitespace between sections (`layout/section-padding`)
- Typography-driven hierarchy, decoration last
- Charts in glass panels with generous padding
- Print/PDF: high contrast, no blur reliance (solid white fallback)

**Motion:** Section scroll reveals; chart enter animations; minimal otherwise.

---

## 9. UX & Trust Principles

The interface optimizes for trust. The user must never wonder **"What happens next?"**

### 9.1 Required States

Every async surface, data fetch, and user action must implement applicable states:

| State | User Sees | Motion |
|-------|-----------|--------|
| **Empty** | Illustration + headline + supporting text + primary CTA | Fade in |
| **Loading** | Skeleton matching content shape + context copy | Shimmer |
| **Processing** | Staged progress with labels (not generic spinner) | Step fill animation |
| **Success** | Confirmation message + clear next step | Check morph |
| **Error** | What happened + why + how to fix + retry button | Subtle shake (1×) or border pulse |
| **Retry** | Restored to prior actionable state |, |

### 9.2 Long-Running Operations

- Show meaningful progress stages, not indeterminate spinners
- Label each stage: "Validating billing data…", "Running verification rules…"
- Preserve user context, never navigate away without confirmation
- On completion, animate transition to results

### 9.3 Error Copy Rules

- Explain what happened in plain language
- Explain why (when known)
- Explain how to fix
- Provide retry when possible
- Never expose stack traces or technical error codes

### 9.4 Empty States

Every empty state includes:

- Minimal outline illustration
- Clear headline
- Supporting text
- Primary CTA

Never leave blank pages or empty containers without guidance.

---

## 10. Accessibility

Maintain **WCAG 2.1 AA** compliance across all glass and motion treatments.

### 10.1 Contrast

- Body text on glass: minimum `glass/opacity-default` (0.72) with `gray-900` text
- Secondary text: `gray-500` only on backgrounds ≥ `glass/opacity-elevated`
- Interactive elements: 4.5:1 contrast minimum
- Never rely on color alone for severity, always pair with text label

### 10.2 Keyboard Navigation

- All interactive elements reachable via Tab
- Logical tab order matches visual order
- Modals trap focus
- Escape closes modals and dropdowns

### 10.3 Focus

- Visible `:focus-visible` ring on all interactive elements
- Ring: `2px solid border/focus`, 2px offset
- Never remove focus outlines without replacement

### 10.4 Touch Targets

- Minimum 44×44px for all interactive elements
- Adequate spacing between adjacent targets

### 10.5 Motion Accessibility

- Respect `prefers-reduced-motion: reduce` (see Section 4.15)
- No flashing content > 3 times per second
- Essential state feedback remains without animation

### 10.6 Semantics

- Semantic HTML elements (`<button>`, `<nav>`, `<main>`, `<table>`)
- ARIA labels where visual context is insufficient
- Form fields always have visible labels

---

## 11. Financial Data Formatting

### 11.1 Currency

| Magnitude | Format | Example |
|-----------|--------|---------|
| Standard | `$#,###` | $1,234 |
| Thousands | `$#,###` | $12,345 |
| Millions | `$#,###,###` | $1,234,567 |

Always use tabular numerals. Consistent decimal precision per context.

### 11.2 Percentages

Format: `12.4%`, one decimal place unless context requires otherwise.

### 11.3 Dates

Format: `MMM D, YYYY`, e.g., `Jun 25, 2026`

### 11.4 Positive & Negative Values

| Sign | Color |
|------|-------|
| Positive / recovered | `success` (green) |
| Negative / leakage | `error` (red) |

---

## 12. Implementation Notes

This section guides the follow-up token implementation phase. Do not deviate from token values above.

### 12.1 CSS Custom Properties (`globals.css`)

Define under `:root`:

- `--surface-glass`, `--surface-glass-elevated`, `--surface-glass-subtle`
- `--border-default`, `--border-glass`
- `--blur-lg`, `--elevation-1` through `--elevation-4`
- `--duration-fast`, `--duration-normal`, `--ease-out`

### 12.2 Tailwind Extension (`tailwind.config.ts`)

Extend `theme.extend` with:

- New radius tokens (`hero: 40px`, updated card/modal)
- `boxShadow` elevation scale
- `backdropBlur` scale
- `zIndex` stack
- `transitionDuration` and `transitionTimingFunction`
- Glass opacity utilities via CSS variables

### 12.3 shadcn/ui

- Theme shadcn via CSS variables mapped to design tokens
- Apply Clerk appearance theme to match shadcn tokens
- Customize radius, border, and shadow through tokens, do not rewrite core components

### 12.4 Framer Motion Conventions

- Shared animation variants in `lib/motion/variants.ts`
- Page wrapper: `lib/motion/page-transition.tsx`
- Reusable: `fadeUp`, `staggerContainer`, `cardHover`, `modalContent`
- Wrap client components only; respect Server Component boundaries

### 12.5 Dependencies to Add

| Package | Purpose |
|---------|---------|
| `framer-motion` | All UI animation |
| `lenis` | Smooth scroll (landing, reports) |
| `sonner` | Toast notifications |

### 12.6 Component Checklist

Before any component is complete:

- [ ] Uses tokens only, no arbitrary Tailwind values
- [ ] Glass surface per spec (where applicable)
- [ ] All required states implemented
- [ ] Motion with reduced-motion fallback
- [ ] Responsive (desktop → tablet → mobile)
- [ ] Accessible (focus, contrast, touch target)
- [ ] Single primary CTA per page (page-level)

---

## Appendix A, Premium Feel Checklist

Every completed screen must feel:

- Calm
- Spacious
- Precise
- Expensive
- Trustworthy
- Executive-ready
- Alive (subtle reactivity)
- Motion-safe (reduced-motion respected)

If the page feels busy, remove elements rather than adding them.

---

## Appendix B, Final Principle

The UI should disappear.

Users should focus on discovering recoverable revenue, not on learning how to use the software.

Every interface decision should increase trust, reduce friction, and help a finance leader reach an evidence-backed decision as quickly as possible.

The interface should feel **expensive before it feels technical**.
