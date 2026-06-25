
# Revenue Leakage Radar — Design System v1.0

> **Design Principles:** Apple precision • Hermès restraint • Stripe clarity • Squarespace whitespace • Enterprise credibility

----------

# 1. Brand Personality

Attribute

Rule

Overall Feel

Premium, minimalist, editorial

Visual Density

Low

Motion

Subtle, purposeful

Color Usage

Conservative

Shadows

Soft, never dramatic

Borders

Preferred over shadows

Rounded Corners

Moderate (not playful)

Icons

Thin outline only

Charts

Minimal, muted

----------

# 2. Color Tokens

## Neutral Palette

Token

Hex

Usage

White

#FFFFFF

Cards

Gray-25

#FCFCFD

App Background

Gray-50

#F8FAFC

Secondary Background

Gray-100

#F1F5F9

Borders

Gray-200

#E2E8F0

Inputs

Gray-300

#CBD5E1

Disabled

Gray-400

#94A3B8

Secondary Text

Gray-500

#64748B

Labels

Gray-700

#334155

Body Text

Gray-900

#0F172A

Headings

----------

## Primary Palette

Token

Hex

Primary

#0F172A

Primary Hover

#1E293B

Primary Active

#020617

Primary Light

#F8FAFC

----------

## Accent Palette

Token

Hex

Usage

Blue

#2563EB

Primary CTA

Blue Hover

#1D4ED8

Hover

Blue Light

#EFF6FF

Selected States

----------

## Semantic Tokens

### Success

Token

Hex

Success

#16A34A

Success BG

#F0FDF4

----------

### Warning

Token

Hex

Warning

#D97706

Warning BG

#FFFBEB

----------

### Error

Token

Hex

Error

#DC2626

Error BG

#FEF2F2

----------

### Info

Token

Hex

Info

#0284C7

Info BG

#F0F9FF

----------

## Revenue Opportunity Colors

Severity

Color

Critical (>100k ARR)

#991B1B

High

#DC2626

Medium

#EA580C

Low

#CA8A04

Informational

#0284C7

----------

## Verification Status

State

Color

Passed

Success

Issue Found

Error

Needs Review

Warning

Not Run

Gray-300

----------

# 3. Typography

## Font Family

Primary

Inter

Fallback

system-ui

----------

## Font Scale

Token

Size

Weight

Line Height

Display XL

4rem

700

1.0

Display

3rem

700

1.05

H1

2.25rem

700

1.1

H2

1.875rem

650

1.2

H3

1.5rem

650

1.25

H4

1.25rem

600

1.3

Large

1.125rem

500

1.5

Body

1rem

400

1.6

Small

.875rem

400

1.5

Caption

.75rem

500

1.4

----------

## Letter Spacing

Element

Tracking

Display

-.04em

H1

-.03em

H2

-.025em

H3

-.02em

Body

-.01em

Small

0

----------

# 4. Spacing Scale

Base Unit

4px

----------

Token

REM

1

.25

2

.5

3

.75

4

1

5

1.25

6

1.5

8

2

10

2.5

12

3

16

4

20

5

24

6

----------

## Layout Rules

Container Max

1280px

Reading Width

760px

Card Padding

2rem

Section Padding

6rem vertical

Page Margin

2rem

Gap Small

1rem

Gap Medium

2rem

Gap Large

4rem

----------

# 5. Grid

Desktop

12 columns

Gap

32px

----------

Tablet

8 columns

Gap

24px

----------

Mobile

4 columns

Gap

16px

----------

# 6. Border Radius

Component

Radius

Buttons

12px

Cards

18px

Inputs

12px

Tables

16px

Badges

999px

Modals

24px

----------

# 7. Borders

Default

1px solid Gray-100

Hover

Gray-200

Focused

Blue

Error

Error

Success

Success

----------

# 8. Shadow Tokens

None by default.

----------

Card

0 1px 3px rgba(15,23,42,.05)

----------

Hover

0 10px 30px rgba(15,23,42,.08)

----------

Modal

0 30px 60px rgba(15,23,42,.12)

----------

Dropdown

0 12px 24px rgba(15,23,42,.08)

----------

# 9. Motion

Duration

150ms

200ms

300ms

Only.

----------

Easing

ease-out

----------

Hover

translateY(-2px)

----------

Cards

Scale

1.01

----------

Buttons

Brightness

102%

----------

Loading

Opacity pulse

No spinning logos.

----------

Page Transition

Fade

150ms

----------

Modal

Opacity

↓

Scale 98→100

----------

Toast

Slide Up

Fade

----------

# 10. Buttons

Primary

Dark background

White text

----------

Secondary

White

Border

Dark text

----------

Ghost

Transparent

----------

Danger

Red

----------

Button Heights

Small

40px

Medium

48px

Large

56px

----------

# 11. Inputs

Height

48px

Padding

16px

Border

Gray-200

----------

Focus

Blue border

Soft blue glow

----------

Placeholder

Gray-400

----------

Disabled

Gray-100

----------

Error

Red border

Error message

----------

# 12. Upload Component

Idle

Large dashed border

Upload icon

Instruction text

----------

Drag Active

Blue border

Blue background

----------

Uploaded

Green check

Filename

Replace button

Delete button

----------

Error

Red border

Message

Retry

----------

# 13. Cards

Padding

32px

Gap

16px

----------

Hover

Shadow

Lift 2px

----------

Clickable

Cursor pointer

----------

# 14. Tables

Row Height

64px

----------

Header

Gray-50

Bold

----------

Hover

Gray-25

----------

Selected

Blue Light

----------

Borders

Horizontal only

----------

# 15. Badges

Height

28px

Radius

Full

Padding

12px

----------

Variants

Success

Warning

Error

Info

Gray

----------

# 16. Progress Indicator

Horizontal.

6 steps.

Animated fill.

Checkmark on completion.

----------

# 17. Charts

No gradients.

No 3D.

----------

Bar

Primary Blue

----------

Revenue

Blue

----------

Recovered

Green

----------

Risk

Red

----------

Background

Gray-50

----------

# 18. Navigation

Top Nav

72px

----------

Logo Left

----------

Actions Right

----------

Sticky

Yes

----------

Border Bottom

Gray-100

----------

# 19. Dashboard Cards

Height

180px

----------

Large Metric

48px

----------

Label

Small

----------

Supporting Text

Gray-500

----------

# 20. Findings Cards

Top

Priority Badge

----------

Middle

ARR

----------

Bottom

Confidence

Accounts

Expand CTA

----------

# 21. Report Layout

Hero

Executive Summary

↓

Opportunity Breakdown

↓

Verification Checks

↓

Findings

↓

Recommendations

↓

Downloads

----------

# 22. Loading States

Skeletons.

Never blank pages.

----------

Metrics

Animated shimmer.

----------

Tables

8 skeleton rows.

----------

Cards

Gray placeholders.

----------

# 23. Empty States

Illustration

Minimal outline.

----------

Headline

Clear.

----------

CTA

Always present.

----------

# 24. Toasts

Top Right.

----------

Success

Green

----------

Error

Red

----------

Info

Blue

----------

Auto-dismiss

4s

----------

# 25. Modal Specs

Max Width

640px

----------

Padding

32px

----------

Dismiss

ESC

Outside click

----------

Animation

Fade + Scale

----------

# 26. Icons

Lucide

1.75px stroke

24px default

----------

# 27. Data Severity Indicators

Level

Badge

Critical

Red

High

Orange

Medium

Yellow

Low

Blue

Passed

Green

----------

# 28. Confidence Indicators

95–100%

Green

90–94%

Blue

80–89%

Amber

<80%

Gray

----------

# 29. Accessibility

Contrast

AA Minimum

----------

Minimum Target

44px

----------

Keyboard Navigation

Required

----------

Visible Focus Ring

Always

----------

Reduced Motion

Supported

----------

# 30. Premium UI Rules

-   Never use more than **one primary CTA** per page.
    
-   Maximum **3 accent colors** visible on any screen.
    
-   Never exceed **2 shadow levels** simultaneously.
    
-   Prefer whitespace over dividers.
    
-   Every metric card must emphasize **one number only**.
    
-   All financial values use tabular numerals (`font-variant-numeric: tabular-nums`).
    
-   Animations communicate state changes only; never decorative.
    
-   Avoid glassmorphism, gradients, neumorphism, excessive borders, or oversized icons.
    
-   UI should feel calm, precise, and trustworthy—not playful.
    
-   The report should resemble a board-level financial document more than a traditional SaaS dashboard.
