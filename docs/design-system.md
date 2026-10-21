# Revenue Leakage Radar, Design System

> **Single source of truth** for UI in this product.
>
> **Design direction:** A light, large-scale SaaS product. Geist everywhere. Near-black type. Forest green as the only accent. White surfaces on a pale green field. A thin solid nav. Pages where the headline and the number do the work.
>
> **Principles:** Stripe's scale and clarity. Vercel's restraint. Linear's precision. Take the composition, the scarce color, and the confidence. Do not copy their dark canvases, gradients, marks, or illustrations.

Token implementation lives in `apps/web/app/globals.css` and `apps/web/tailwind.config.ts`. If this document and the code disagree, update this document to match the code, then keep new UI on these tokens.

The folders under `docs/design/` (`revenue-leakage-radar`, `optimus-the-ai-platform-to-build-and-ship`, `compute-the-platform-to-build-and-ship-ai-agents`) are historical prototypes. Do not copy their type, color, motion, or layout. `docs/design/design-language.md` describes the current system and defers to this file.

---

## 1. What this product should feel like

Finance leaders should trust the product within 10 seconds. The interface is calm, spacious, precise, and current. Type and numbers do the work. Decoration does not.

| Take from the references | Leave behind |
|--------------------------|--------------|
| Large sans headlines, short supporting lines | Dark canvases, black hero sections |
| One accent used rarely, like Stripe's purple | Color ribbons, aurora, mesh gradients |
| Thin solid nav: logo left, links beside it, actions right | Frosted nav, blur, centered spring pills |
| Hairline rules and whitespace as structure | Glass, glow, dashed frames, card lift |
| Product UI that looks like a real tool, not a poster | Serif display faces, italic headline words, tracked uppercase eyebrows |

The interface is never a generic widget dashboard, a dark hacker theme, or a playful consumer site.

### Priorities

1. Trust. The next step is obvious.
2. Clarity. Evidence and dollars are legible.
3. Hierarchy. One hero number, one primary action.
4. Whitespace. Breathing room over chrome.
5. Response. Hover and progress change color. Motion stays quiet.

### One primary action

Each page has one filled primary button. Other actions are outline, ghost, or text links.

---

## 2. Color

Forest green is the only accent. Use it on the primary button, links, key figures, step indexes, and short rules that separate a list. Do not paint body copy green. Do not add a second brand color.

| Token | Value | Use |
|-------|--------|-----|
| `background`, `card`, `popover` | `oklch(1 0 0)` | Page canvas, cards, nav, menus |
| `foreground` | `oklch(0.18 0.01 160)` | Headlines and primary text |
| `primary` | `oklch(0.4 0.085 163)` | Buttons, links, hero figures, emphasis |
| `primary-foreground` | `oklch(0.99 0 0)` | Text on primary |
| `field` | `oklch(0.955 0.028 163)` | Pale green band: page intros, alternating sections, footer |
| `secondary` | `oklch(0.965 0.014 163)` | Hover fills, quiet tints |
| `muted` | `oklch(0.96 0.01 163)` | Subtle fills |
| `muted-foreground` | `oklch(0.46 0.02 160)` | Supporting copy |
| `destructive` | `oklch(0.55 0.2 25)` | Errors and danger |
| `leak` | `oklch(0.62 0.14 55)` | Semantic amber for leakage warnings only |
| `line`, `border`, `input` | `oklch(0.9 0 0)` | 1px hairlines |
| `ring` | same as `primary` | Focus ring |

### How color breaks up a page

- White is the default surface.
- `bg-field` is a full-bleed band behind a page intro, a quiet section, or the footer. It is flat. No gradient, no blur, no radial wash.
- White cards and white control tiles sit on `field` so they read as surfaces.
- Do not stack two `field` bands with nothing white between them. The footer is `field`, so the section above it stays white.
- Hero and result figures that represent money use `text-primary` with tabular numerals.
- A list that would otherwise be a gray hairline can use a 2px `border-primary` top rule, or a 2px left rule on a card.
- Selection color is `primary` with `primary-foreground`.

Never invent Tailwind palette colors (`bg-green-600`, `text-slate-500`, arbitrary hex). Never exceed the accent plus semantic success, warning, and error on one screen.

---

## 3. Typography

One family. Geist for headlines, body, and UI. Geist Mono for IDs and references. `.font-heading` is Geist at medium weight with `-0.025em` tracking. It is not a serif.

| Class | Size | Use |
|-------|------|-----|
| `text-display` | clamp(2.5rem, 5vw, 4rem), line-height 1.02 | Landing headline |
| `text-h1` | clamp(2.25rem, 4vw, 3.25rem), line-height 1.08 | Page titles |
| `text-h2` | clamp(1.75rem, 2.6vw, 2.25rem) | Section titles |
| `text-h3` | 1.5rem | Subsection titles |
| `text-h4` | 1.125rem | Card titles |
| `text-body` | 1rem / 1.6 | Paragraphs |
| `text-small` | 0.875rem | Secondary copy |
| `text-caption` | 0.8125rem | Footnotes |
| `text-overline` | 0.875rem, weight 500 | Sentence-case labels. No uppercase, no letter-spacing |
| `text-metric-xl` | clamp(2.5rem, 4.5vw, 3.5rem) | The one big number |

Headlines are medium weight, not bold black and not light. No italic word inside a headline. No second display face.

Financial numbers use `tabular-nums` (class `tnum` or `tabular-nums`).

Currency: `$1,234`, `$12,345`, `$1,234,567`. Percentages: `12.4%`. Dates: `MMM D, YYYY`.

---

## 4. Surfaces, radius, elevation

Default surfaces are flat.

- White background
- 1px `border-line`
- `--radius` is `0.5rem` (8px) on controls and cards
- No blur, no glow, no dashed frames, no radial washes, no backdrop filters
- Hover changes background color (`secondary` or `muted`). Cards do not lift, scale, or tilt
- Modals and dropdowns are the same white surface with a hairline border

Do not add soft glass, frosted nav, inner highlights, or stacked shadows. Depth comes from the field band against white, not from blur.

---

## 5. Layout

| Context | Width | Padding |
|---------|--------|---------|
| Marketing sections | `max-w-marketing` (1280px) | `px-6 md:px-10` |
| Readable prose | `max-w-reading` (about 760px) | `px-6 md:px-10` |
| Upload | `max-w-upload` | `px-6 md:px-10` |

Page structure:

```text
Sticky nav
  → Field intro (headline, sometimes the main tool)
  → White content (cards, tables, lists)
  → Field band where a section needs a break
  → White content
  → Field footer
```

Section padding is generous: `py-14` to `py-24` on marketing, more on a hero. Prefer whitespace over boxes. When a divider is needed, use a 1px `border-line`, or a 2px primary rule on a step or card.

Nav height is `h-16` (64px). Sticky offsets that clear the nav use `top-16` or `4rem`.

Desktop first, then tablet, then mobile. Do not hide primary actions on small screens. Below `lg`, marketing links move into the menu, and Sample report plus Free scan lead that menu.

---

## 6. Navigation

Top bar only. Sticky. Solid `background`. 1px bottom `border-line`. No blur.

- Logo left, vertically centered, `h-7` inside the `h-16` bar
- Links beside the logo: How it works, Calculator, Pricing, Security
- Actions right: Sample report (outline), Free scan (primary), then Sign in
- No centered pill, no spring indicator, no sidebar in the MVP marketing site

Demo, FAQ, and Feedback live in the footer, not the primary nav.

---

## 7. Controls

| Variant | Treatment |
|---------|-----------|
| Primary | Solid `primary`, white text, `hover:brightness-110`, no shadow |
| Outline / secondary | White fill, 1px border, hover `bg-secondary` |
| Ghost | Transparent, muted text, hover `bg-muted` |
| Danger | Solid `destructive` |
| Link | `text-primary`, underline on hover |

Sizes: `sm` is 32px tall, `md` and `lg` are 40px tall. Radius 8px. No pills, no glow. A press scales the control to 0.98 for 150ms. Hover does not scale or lift.

There is no Glass button variant.

Inputs: visible label, helper text, validation, error. Do not use the placeholder as the label. Focus is a 2px `ring` in forest green with a 2px offset. No blue glow.

Icons are Lucide, outline, about 1.75px stroke. They support a label. They do not replace it.

---

## 8. Page patterns

### Landing

Split hero on `bg-field`. Left: one sans headline, one short sentence, two compact buttons (filled scan, outline sample report). Right: leakage figure in `text-primary`, ARR slider on a white track. Under both columns, still on the field: the business-type question as three equal white tiles.

Then a white stat band with green figures. Then the method on white, each step opened by a 2px primary rule and a green index. Then a `field` security band with white cards. Then the report preview on white, with annualized amounts in `text-primary`. Then the `field` footer.

No upload drop zone on the landing page. Upload is one click away.

### Other marketing pages

The first block is a `bg-field` intro: headline and one short paragraph. The working content (cards, pricing grid, FAQ, form) sits on white underneath. Cards that need separation get a primary top or left rule. The footer is `field`.

### Pricing

Field intro. White cards. The recommended plan uses a 2px `border-primary`, a `primary` badge, a green price, and green check marks. Other prices stay near-black.

### Calculator

The start screen is a `field` band with a white card for the first question. Later steps keep the question in a white card on `field`. The result figure is `text-primary` on a `field` card.

### Upload

Field band for the headline only. The drop target below is a flat bordered rectangle on white. Hover changes the border color. No pulse, tilt, or radial wash.

### Workspace and reports

Same tokens. The recoverable figure can sit on `field` in `text-primary`. Evidence tables stay on white with horizontal rules. Do not restyle a report into a marketing poster. Decoration stays behind the evidence.

### Sample report

A `field` banner states that the data is a sample. The report body stays white.

---

## 9. Motion

One quiet language. Durations: 150ms press, 200ms hover, 280ms appear, 300ms route change. Easing is `cubic-bezier(0.16, 1, 0.3, 1)`.

- Press: buttons and tiles scale to 0.98 while held.
- Hover: background or border color. Arrows shift 2px. Nav underlines grow from the left. Cards do not lift.
- Appear: `Reveal` and `Stagger` fade in and rise 8px, once. Lists stagger by about 40ms. No blur.
- Route: marketing and audit pages fade and rise 8px through `PageTransition`.
- Loading: skeletons shimmer. They do not count up.
- Toasts (Sonner) slide up and fade, top right, and dismiss in about 4 seconds.

`prefers-reduced-motion` removes transforms, route fades, and reveal motion. No flashing above 3Hz.

Do not add blur fades, line-by-line headline reveals, count-up stats, spring nav pills, card lift, tilt, or cursor lighting.

---

## 10. Copy

Never use an em dash in user-facing copy, UI text, placeholders, emails, or generated narratives. Use a comma, a colon, a period, parentheses, or two sentences. For ranges, use "to" or a hyphen (`1 to 12`).

Section labels are sentence case.

---

## 11. States

Every async surface has empty, loading, processing, success, error, and retry. Loading uses skeletons, not a blank screen. Errors say what happened and how to fix it, without a stack trace.

Empty states have a headline, supporting text, and one primary action.

---

## 12. Do not bring these back

- Fraunces, Instrument Serif, or any second display face
- Warm paper or cream backgrounds
- Uppercase tracked eyebrows
- Italic words inside headlines
- Glass, backdrop blur, glow, and dashed cards
- Pill buttons
- Blue as a brand or focus color
- Card lift, hover scale, or tilt. A 0.98 press scale is part of the motion language
- Count-up metrics and line-by-line reveals
- Dark mode canvases copied from Vercel or Linear
- The upload zone as the landing centerpiece
- Copying layout, type, or color from `docs/design/revenue-leakage-radar`, Optimus, or Compute

---

## 13. Before shipping UI

- Tokens come from this document and `globals.css`
- One filled primary action
- Field bands and white surfaces alternate
- Money uses tabular numerals
- Responsive, including the nav actions
- Focus visible, contrast at WCAG AA, touch targets at least 44px
- Empty, loading, and error states exist
- No em dashes in the copy
