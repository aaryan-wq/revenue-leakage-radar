# Revenue Leakage Radar, Design Language

> **Authority:** [docs/design-system.md](../design-system.md) is the source of truth. This file is the short version of the same system. The app in `apps/web` is the reference implementation.
>
> The folders next to this file are historical prototypes. Do not copy them.

---

## 1. What it should feel like

A light, large-scale SaaS product.

- Stripe's scale: big type, one accent, the product UI is the illustration
- Vercel's restraint: thin chrome, almost no decoration
- Linear's precision: alignment, tight type, nothing extra

Stay on a white canvas. Forest green is the accent, the way Stripe uses purple. Do not copy dark canvases, gradients, triangles, or color ribbons.

The page should feel calm and current. Headlines and numbers do the work.

---

## 2. Language

| Choice | Rule |
|--------|------|
| Type | Geist for headlines and body. Geist Mono for IDs. No serif, no italic headline word |
| Labels | Sentence case. Class `text-overline` has no uppercase tracking |
| Canvas | White (`background`) |
| Band | Pale green `field` behind intros, a quiet section, and the footer |
| Accent | `primary` forest green on the filled button, links, key figures, and short rules |
| Surfaces | White, 1px `border-line`, 8px radius |
| Hover | Background color or button brightness. No lift, scale, or tilt |
| Motion | Content is just there. No blur fades, count-ups, or spring pills |
| Nav | `h-16`, solid white, logo left, links beside it, actions right |

Use `text-display`, `text-h1` through `text-h4`, `text-body`, `text-small`, `text-caption`, and `text-metric-xl`. Money uses tabular numerals.

---

## 3. Page rhythm

```text
White nav
  → Field intro
  → White content
  → Field band, when the page needs a break
  → White content
  → Field footer
```

Do not put two field bands against each other. The footer is already field, so the block above it stays white.

Landing: field hero with the headline on the left and the green leakage figure plus slider on the right. The business-type tiles are white and full width under both columns. Stats are white with green numbers. Security is a field band with white cards. The report preview is white.

Other marketing pages open with a field intro, then white cards or forms.

Upload: field headline, flat bordered drop target on white. The drop zone is not the landing centerpiece.

---

## 4. Controls

One filled primary button per page. Everything else is outline, ghost, or a link.

Primary is solid forest green, 8px radius, about 40px tall, no glow. Outline is white with a hairline. Focus ring is forest green, 2px, with a 2px offset.

Icons are Lucide outlines. They sit next to labels.

---

## 5. Copy

No em dashes in interface copy. Use a comma, colon, period, or two sentences. Ranges use "to" or a hyphen.

---

## 6. Do not restore

Fraunces or any display serif. Warm paper. Tracked uppercase eyebrows. Glass, blur, glow, dashed frames. Pill buttons. Blue focus rings. Card lift. Count-up numbers. Dark hero sections. Patterns from the prototype folders in this directory.
