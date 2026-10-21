# Design references

## What to follow

The product UI is defined by:

1. [docs/design-system.md](../design-system.md)
2. [docs/design/design-language.md](design-language.md)
3. The implementation in `apps/web`

Those three agree. Build new screens to match them.

Influences are Stripe, Vercel, and Linear: scale, restraint, and precision on a light canvas, with forest green as the single accent. Do not copy their dark canvases, gradients, or marks.

## What not to follow

These folders are historical prototypes. They predate the current system. Do not copy their type, color, motion, glass, or layout.

- `revenue-leakage-radar/` used a serif display face and warm paper
- `optimus-the-ai-platform-to-build-and-ship/` is a separate marketing prototype
- `compute-the-platform-to-build-and-ship-ai-agents/` is a dark prototype

If a prototype disagrees with `docs/design-system.md`, the design system wins.
