\# Revenue Leakage Radar, UI Source of Truth



\## Priority



The files in this directory are the ONLY authoritative source for UI, UX, layout, spacing, typography, colors, animations, and component styling.



These references intentionally replace every previous design document.



Ignore any conflicting guidance found in:



\* design-system.md

\* ui-rules.md

\* product-spec.md (visual sections)

\* previous prompts

\* previous generated components



If there is any conflict:



The files inside `/docs/design` always win.



\---



\## Implementation Rules



Do not redesign.



Do not reinterpret.



Do not "improve."



Instead:



\* Extract the common visual language.

\* Build a reusable component system from these references.

\* Reproduce spacing, proportions, hierarchy, motion, typography, and interaction patterns as faithfully as possible.



When creating new pages:



Reuse the same design language.



Do not invent new visual styles.



Everything should look like it belongs to the same product family.



\---



\## Consistency Rules



Maintain:



\* identical spacing rhythm

\* identical typography hierarchy

\* identical button styling

\* identical border radii

\* identical animation language

\* identical hover behavior

\* identical color usage

\* identical shadows

\* identical layout philosophy



If unsure:



Prefer copying an existing pattern over inventing a new one.



Consistency is more important than creativity.



