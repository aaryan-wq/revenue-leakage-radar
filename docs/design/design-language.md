# Revenue Leakage Radar, Extracted Design Language

> **Authority:** This document distills the shared visual DNA from every reference in `/docs/design`.  
> When implementing UI, follow this language first. Individual reference implementations are canonical examples, copy patterns from them; do not invent new ones.

---

## 1. Design Philosophy (Common DNA)

All three references share a **premium editorial product** feel. They are not generic SaaS dashboards. They feel like:

- A **financial instrument** or consulting deliverable (Radar)
- A **creative platform launch** with editorial typography (Optimus)
- A **technical infrastructure product** with cinematic restraint (Compute)

### What makes them feel premium

| Principle | Expression |
|-----------|------------|
| **Restraint** | Thin borders, no heavy shadows, no decorative gradients (except hero accents in platform refs) |
| **Typography as architecture** | Headlines carry the layout; whitespace does the rest |
| **Tactile objects** | Upload zones, buttons, and cards behave like physical things, they respond to cursor and press |
| **Evidence-first hierarchy** | Numbers and labels are never buried; financial data is always hero-sized |
| **Intentional motion** | Everything moves with purpose, reveal, stagger, spring, never bounce or flash |
| **Hairline structure** | Sections divide with 1px rules, not boxes-with-shadows |
| **Dual type pairing** | Serif/display for authority + sans for utility + mono for metadata |

### What to avoid

- Widget-grid dashboards
- Heavy glassmorphism, aurora blobs, loud gradients
- Arbitrary colors outside the token system
- Inventing new button shapes, radii, or animation curves
- Placeholder-as-label forms
- Blank loading states

---

## 2. Reference Roles

| Reference | Role in the family |
|-----------|-------------------|
| **`revenue-leakage-radar/`** | **Primary product reference.** All app pages (landing, upload, processing, report, workspace) must match this implementation. |
| **`optimus-the-ai-platform-to-build-and-ship/`** | Light-mode platform patterns: scroll-reactive nav, mega-type hero, marquee stats, numbered feature rows, pricing grid. |
| **`compute-the-platform-to-build-and-ship-ai-agents/`** | Dark-mode platform patterns: cinematic hero, bento features, process steps, particle/reactive surfaces. |

When building **Revenue Leakage Radar** pages, default to the Radar reference. Borrow Optimus/Compute patterns only where Radar has no equivalent (e.g. mobile nav overlay structure).

---

## 3. Layout Principles

### Container widths

| Context | Max width | Horizontal padding |
|---------|-----------|-------------------|
| Marketing / landing sections | `max-w-[78rem]` – `max-w-[80rem]` | `px-6 md:px-10` |
| Platform landing (Optimus/Compute) | `max-w-[1400px]` | `px-6 lg:px-12` |
| Upload / focused flows | `max-w-[64rem]` | `px-6 md:px-10` |
| Report / editorial content | `max-w-[68rem]` | `px-6 md:px-10` |
| Processing (centered instrument) | `max-w-[60rem]` | `px-6 md:px-10` |

### Page structure

Every page follows:

```
Header (sticky nav)
  → Primary content (hero or page title block)
  → Supporting sections (border-separated bands)
  → Footer / bottom actions
```

### Grid patterns

- **Hero:** `grid-cols-1 lg:grid-cols-2`, copy left, interactive object right
- **Upload:** `lg:grid-cols-[1.4fr_1fr]`, primary action + sidebar checklist
- **Stats band:** `grid-cols-2 md:grid-cols-4` with `gap-px bg-line` hairline grid
- **Report metrics:** `md:grid-cols-[1.3fr_1fr]`, dominant figure + 2×2 stat grid
- **Workspace:** `lg:grid-cols-[20rem_1fr]`, index rail + detail surface
- **Feature rows (platform):** numbered row with `border-b border-foreground/10`

### Section rhythm

- Section vertical padding: `py-20` to `py-28` (marketing), `py-24 lg:py-32` (platform)
- Title block → content gap: `mt-12` to `mt-20`
- Use `border-y border-line` or `border-t border-line` to create editorial bands
- Alternate subtle backgrounds: `bg-secondary/30`, `bg-secondary/40`, never loud fills

---

## 4. Spacing System

### Scale (Tailwind tokens used across references)

```
2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28
```

### Recurring spacing pairs

| Use | Values |
|-----|--------|
| Nav height | `h-16` (Radar) · `h-14`–`h-20` scroll-reactive (platform) |
| Card internal padding | `p-5` – `p-8` · hero panels `py-16`–`py-20` |
| Section header → body | `mt-4` – `mt-7` for overline→headline, `mt-10`–`mt-16` for headline→content |
| Inline stat groups | `gap-x-8 gap-y-3` or `gap-x-10` |
| CTA rows | `gap-4` |
| Finding / ledger rows | `py-5` – `py-12` with `border-t border-line` |

### Whitespace rule

Prefer whitespace over separators. When separation is needed, use hairlines, not card shadows.

---

## 5. Typography Hierarchy

### Font stacks

| Role | Radar | Platform refs |
|------|-------|---------------|
| **Display / headings** | Fraunces (`font-heading`) | Instrument Serif (`font-display`) |
| **Body / UI** | Geist Sans (`font-sans`) | Instrument Sans (`font-sans`) |
| **Metadata / IDs** | Geist Mono (`font-mono`) | JetBrains Mono (`font-mono`) |

**Product implementation uses the Radar stack.**

### Type scale (semantic levels)

| Level | Classes / pattern | Usage |
|-------|-------------------|-------|
| **Overline** | `text-[0.72rem]–text-[0.78rem] uppercase tracking-[0.14em]–tracking-[0.18em] text-muted-foreground` | Section labels, metadata, step indicators. Often prefixed with `h-px w-8 bg-primary/50` or `bg-foreground/30` rule. |
| **Display hero** | `font-heading text-[clamp(2.6rem,5.5vw,4.4rem)] leading-[0.95] tracking-tight` | Landing H1 |
| **Page title** | `font-heading text-[clamp(2.1rem,5vw,3.4rem)] leading-[1.02] tracking-tight text-balance` | Upload, focused flows |
| **Report title** | `font-heading text-[clamp(2.4rem,6vw,4.4rem)] leading-[0.98] tracking-tight` | Report cover |
| **Section heading** | `font-heading text-[clamp(1.7rem,3.5vw,2.6rem)] leading-[1.05] tracking-tight text-balance` | In-page sections |
| **Hero metric** | `font-heading text-[clamp(3rem,9vw,6rem)] leading-none tracking-tight tnum` | Recoverable revenue figure |
| **Supporting metric** | `font-heading text-2xl`–`text-4xl tracking-tight tnum` | Stat cards, inline metrics |
| **Body** | `text-[1.05rem]` or `text-lg leading-relaxed text-muted-foreground text-pretty` | Descriptions |
| **Small / caption** | `text-sm` or `text-xs text-muted-foreground` | Hints, footnotes |
| **Nav links** | `text-[0.8rem] tracking-wide` | Navigation items |

### Financial numbers

Always apply tabular numerals:

```css
.tnum {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum';
}
```

Use `font-heading` + `tnum` for all currency, percentages, and counts.

### Emphasis patterns

- **Italic primary phrase** in headlines: `<span className="italic text-primary">`
- **Mono references:** finding IDs, step numbers (`01`, `02`)
- **Muted second line** in platform heroes: `text-muted-foreground` or opacity steps (`text-white/30`)

---

## 6. Color System

### Token architecture

All references use **OKLCH CSS variables** mapped through Tailwind `@theme inline`. Never use arbitrary Tailwind color classes.

### Radar (product) palette

| Token | Role |
|-------|------|
| `--background` | Warm paper `oklch(0.985 0.005 95)` |
| `--foreground` | Ink `oklch(0.235 0.012 75)` |
| `--primary` | Deep emerald `oklch(0.455 0.078 165)` |
| `--primary-foreground` | Light on primary |
| `--secondary` | Soft warm gray |
| `--muted` / `--muted-foreground` | Surfaces and secondary text |
| `--leak` | Amber/terracotta, revenue leakage signal only |
| `--line` | Editorial hairline (slightly stronger than `--border`) |
| `--border` | Standard borders |
| `--destructive` | Error states |

### Semantic usage

| Meaning | Color |
|---------|-------|
| Primary actions | `bg-primary text-primary-foreground` |
| Revenue leakage / critical severity | `text-leak` |
| Elevated severity | `text-primary` |
| Monitor / neutral severity | `text-muted-foreground` |
| Hairlines & dividers | `border-line` |
| Subtle section bands | `bg-secondary/30` – `bg-secondary/40` |
| Hover wash on upload | `color-mix(in oklch, var(--primary) 6–8%, transparent)` radial gradient |

### Platform refs (Optimus / Compute)

- **Optimus:** Monochrome, `primary` equals near-black foreground on warm white
- **Compute:** Inverted, near-black background, white foreground
- Both share identical token structure; only values differ

### Selection

```css
::selection {
  background: var(--primary);
  color: var(--primary-foreground);
}
```

---

## 7. Border Radius

| Token | Radar | Platform |
|-------|-------|----------|
| Base `--radius` | `0.5rem` | `0.25rem` |
| Cards / upload zones | `rounded-xl`, `rounded-2xl` | `rounded-2xl` (nav pill) |
| Primary CTAs | **`rounded-full`** (pill) | **`rounded-full`** |
| Secondary buttons | `rounded-full` or `rounded-lg` | `rounded-md` (shadcn default) |
| Stat grids | `rounded-xl` |, |
| Nav active pill | `rounded-full` |, |

**Product rule:** Primary CTAs are always pill-shaped (`rounded-full`).

---

## 8. Component Patterns

### Navigation

**Radar pattern (product):**
- `sticky top-0 z-50`
- Frosted backdrop: `bg-background/70 backdrop-blur-xl`
- Height: `h-16`
- Logo: pulsing primary dot + `font-heading` wordmark
- Links: `text-[0.8rem] tracking-wide text-muted-foreground`
- Active: shared `layoutId="nav-pill"` spring pill on `bg-secondary`
- CTA: `rounded-full bg-primary` with colored shadow on hover

**Platform pattern (when needed):**
- Fixed, scroll-reactive shrink (`h-20` → `h-14`)
- Scrolled state: floating bar with `rounded-2xl border shadow-lg`
- Link hover: underline grows from left (`w-0 → w-full` over 300ms)
- Mobile: full-screen overlay, `text-5xl font-display` links, staggered reveal

### Buttons

**Primary CTA (canonical):**
```
rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground
transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50
```

**With arrow affordance:**
```
group → child span: group-hover:translate-x-1 transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]
```

**Secondary / ghost:**
```
rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem]
transition-colors hover:bg-secondary
```
or inverted hover: `hover:bg-foreground hover:text-background`

**Press behavior:**
```
whileTap={{ scale: 0.96–0.97 }}
transition={{ type: 'spring', stiffness: 400, damping: 26–28 }}
```

**Magnetic wrapper:** Apply to primary CTAs (`strength={0.25–0.35}`).

### Cards & surfaces

- Background: `bg-card` or `bg-background`
- Border: `border border-line`, single hairline, no shadow
- Padding: generous (`p-5` minimum, `p-8` for hero panels)
- Hover (data rows): `hover:bg-background` on `group` rows
- Info callout: `rounded-xl border border-line bg-secondary/40 p-5`

### Upload object

Canonical tactile upload zone:
- `rounded-2xl border-2 border-dashed border-line` (empty) → `border-primary/30` (filled)
- Radial hover wash from top
- Icon in `bg-primary/10 rounded-lg` container
- Pulsing border ring on hover (`scale: [1, 1.22, 1]`, infinite while hovered)
- Spring scale on drag: `scale: 1.008–1.012`
- File list: `rounded-xl border border-line bg-card` with row dividers
- Validated badge: `text-xs uppercase tracking-wider text-primary`

### Stats / metrics band

```
grid grid-cols-2 gap-px bg-line md:grid-cols-4
→ child: bg-background px-6 py-10 md:px-10
→ value: font-heading text-3xl md:text-4xl tnum
→ label: mt-3 text-[0.82rem] text-muted-foreground
```

Use `<CountUp />` for animated values on viewport entry.

### Report / findings ledger

**Cover block:** overline metadata with dot separators → H1 → body paragraph

**Headline figure:** left dominant metric + right 2×2 stat grid
```
grid gap-px overflow-hidden rounded-xl border border-line bg-line
→ cell: bg-card px-5 py-6
```

**Finding row:**
```
grid md:grid-cols-[auto_1fr_auto] border-t border-line py-12
→ severity label (uppercase tracking)
→ title (font-heading text-2xl)
→ evidence metadata (uppercase micro-labels + tnum values)
→ remedy block: border-l-2 border-primary/40 pl-4
→ annualized figure right-aligned (font-heading text-3xl tnum)
```

**Category bars:** 1px track (`bg-line`), 1px fill (`bg-primary`), scaleX animation on enter.

### Workspace

- Left index rail: `border-r border-line`, active indicator `layoutId` 2px primary bar
- Severity dots: `bg-leak` / `bg-primary` / `bg-muted-foreground/50`
- Detail panel: `AnimatePresence mode="wait"` crossfade with blur
- Evidence grid: same gap-px hairline grid as report stats

### Processing / loading

- Circular progress instrument with breathing concentric rings
- Phase label with `AnimatePresence` blur crossfade
- Phase ticks: spring-animated width bars
- Never show blank screen, always stage label + progress

### Platform-only patterns (borrow carefully)

| Pattern | Source | Use when |
|---------|--------|----------|
| Marquee stats | Optimus | Social proof strip on marketing |
| Mega-type hero | Optimus/Compute | Only if Radar landing evolves |
| Numbered feature rows | All three | Method / how-it-works sections |
| Pricing grid | Optimus | Pricing page |
| Bento feature card | Compute | Feature marketing only |

---

## 9. Animation Language

### Core easing

**Glide (primary, use everywhere in product UI):**
```
cubic-bezier(0.16, 1, 0.3, 1)
```
Export as `const glide = [0.16, 1, 0.3, 1] as const`

**Secondary easings (platform refs):**
- `cubic-bezier(0.22, 1, 0.36, 1)`, character reveals
- `cubic-bezier(0.34, 1.56, 0.64, 1)`, hover lift (subtle overshoot)
- `cubic-bezier(0.77, 0, 0.175, 1)`, line reveal clip

### Duration scale

| Token | Duration | Use |
|-------|----------|-----|
| Instant | 150–350ms | Hover color, icon shift |
| Normal | 450–600ms | State crossfades |
| Reveal | 900–1100ms | Section enter, hero lines |
| Ambient | 2.6–3.4s | Pulse rings, logo dot |

### Motion primitives (implement once, reuse)

| Primitive | Behavior |
|-----------|----------|
| **Reveal** | `opacity: 0 → 1`, `y: 24 → 0`, optional `blur(6px) → 0`, `whileInView`, `once: true` |
| **Stagger** | Container staggers children `0.06–0.08s` apart |
| **StaggerItem** | Same as Reveal per child |
| **Magnetic** | Cursor-attracted spring return (`stiffness: 150, damping: 15`) |
| **PressButton** | `whileHover scale: 1.015`, `whileTap scale: 0.965` |
| **Tilt** | Max 6° perspective response (landing cards only) |
| **CountUp** | Ease-out quartic count on viewport entry |
| **layoutId** | Shared element transitions for nav pills, workspace active bar |

### Hero-specific motion

- Headline lines: clip overflow + `y: 110% → 0` staggered per line
- Upload zone: spring scale on drag, icon float on hover
- Primary CTA arrow: translate-x on group hover

### Reduced motion

When `prefers-reduced-motion: reduce`:
- Disable Magnetic, Tilt, blur filters, CountUp animation
- Keep opacity transitions ≤ 150ms
- Preserve layout and state clarity

---

## 10. Interaction Patterns

| Interaction | Pattern |
|-------------|---------|
| Link hover | `transition-colors hover:text-foreground` (300ms) |
| Nav link hover | Underline grow OR muted→foreground color shift |
| Primary button hover | Colored shadow intensifies + optional arrow shift |
| Secondary button hover | Background fill inversion or `hover:bg-secondary` |
| Button press | Spring scale to 0.96–0.97 |
| Card/row hover | Subtle background shift, no lift shadow |
| Upload drag | Scale 1.008, border warms to `primary/40`, radial wash |
| Focus | `focus-visible:ring-ring/50` (shadcn), 2px ring |
| Selection | Primary fill |

---

## 11. Navigation Structure (Product)

```
Overview (/) · Upload (/upload) · Report (/report) · Workspace (/workspace)
                                                    [Begin audit →]  (primary CTA)
```

- Top navigation only on marketing/product pages
- Workspace uses index rail inside page, not global sidebar
- Footer: editorial CTA block + minimal link row

---

## 12. Visual Rhythm Checklist

Every screen should feel:

- [ ] Calm, one hero element, not competing widgets
- [ ] Spacious, section padding ≥ `py-20`
- [ ] Structured, hairlines, not boxes
- [ ] Typographic, serif/display carries hierarchy
- [ ] Tactile, interactive objects respond to cursor
- [ ] Evidence-first, financial numbers are large and tabular
- [ ] Intentionally animated, Reveal on scroll, spring on press
- [ ] Consistent, same pill buttons, same overline pattern, same glide easing

---

## 13. Migration Rules

When existing app code conflicts with `/docs/design`:

1. **Design references win.** Always.
2. **Copy, don't interpret.** Lift spacing, classes, and component structure from the closest reference page.
3. **Extend, don't invent.** New pages should look like `/upload` or `/report`, not like a new product.
4. **One primary CTA per viewport.** Unlimited secondary actions.
5. **Required states:** empty, loading, processing, success, error, retry, every async surface.

### Migration priority (product pages)

1. Tokens, `globals.css` → Radar reference palette
2. Typography, Fraunces + Geist pairing
3. Navigation, `SiteNav` pattern
4. Motion primitives, `Reveal`, `Stagger`, `Magnetic`, `CountUp`
5. Page-by-page: Landing → Upload → Processing → Report → Workspace

---

## 14. Canonical File Index

| Need | Copy from |
|------|-----------|
| Color tokens | `revenue-leakage-radar/app/globals.css` |
| Motion system | `revenue-leakage-radar/components/motion.tsx` |
| Navigation | `revenue-leakage-radar/components/site-nav.tsx` |
| Hero / landing | `revenue-leakage-radar/components/landing/hero.tsx` |
| Upload | `revenue-leakage-radar/components/upload/upload-object.tsx` |
| Processing | `revenue-leakage-radar/app/processing/page.tsx` |
| Report | `revenue-leakage-radar/app/report/page.tsx` |
| Workspace | `revenue-leakage-radar/components/workspace/workspace-view.tsx` |
| Footer | `revenue-leakage-radar/components/site-footer.tsx` |
| Scroll-reactive nav | `optimus-*/components/landing/navigation.tsx` |
| Feature rows | `optimus-*/components/landing/features-section.tsx` |
| Pricing grid | `optimus-*/components/landing/pricing-section.tsx` |
| Dark hero / process | `compute-*/components/landing/` |

---

*This document is derived from analysis only. Implementation begins after team review of this language.*
