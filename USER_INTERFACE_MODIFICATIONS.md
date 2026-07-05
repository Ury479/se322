# User Interface Modifications — Register for Courses Sequence Diagram

This document records the manual corrections the user applied to
`Assignment1.drawio` (originally titled `GW1.drawio`) using app.diagrams.net.
These changes became the new "correct style" baseline that the generator
must reproduce.

---

## 1. Coordinate Space Translation

The user's manual edits used draw.io's natural canvas model with a
**global offset** different from the original generator output:

| Item                     | Original generator | User-corrected file |
|--------------------------|--------------------|---------------------|
| Top-left of canvas       | (0, 0)             | (0, 0)              |
| First lifeline X (Student) | 140              | **1132.45**         |
| First message Y          | 100                | **1703.99**         |
| Lifeline Y start         | 76                 | **1679.99**         |

The draw.io export is `pageWidth=1169 pageHeight=1169`. The user
shifted everything to position the diagram comfortably within the canvas.

**Effective translation** (subtract to find the original-generator
coordinate of any element):

```
orig_x = user_x - 992.45   (i.e. user_x - 1132.45 + 140)
orig_y = user_y - 1603.99  (i.e. user_y - 1703.99 + 100)
```

Equivalently: **`X_OFFSET = 992.45`, `Y_OFFSET = 1603.99`**.

---

## 2. Layout Constants Captured

### Lifeline horizontal layout

```
START_X = 1132.45     # Student lifeline X
GAP_X   = 140         # uniform spacing
PIDS    = ["S", "UI", "CT", "SV", "CR", "RR", "BS", "BL"]
LIFELINE_X = {p: START_X + i * GAP_X for i, p in enumerate(PIDS)}

# Results
# S  -> 1132.45
# UI -> 1272.45
# CT -> 1412.45
# SV -> 1552.45
# CR -> 1692.45
# RR -> 1832.45
# BS -> 1972.45
# BL -> 2112.45
```

### Vertical layout

```
LIFELINE_TOP = 1679.99
LIFELINE_H   = 1000
TITLE_Y      = 1605.99       # main title
PHASE_LABELS = [
    ("Authentication",        1703.99),
    ("Browse Courses",        1883.99),
    ("Register for Courses",  2133.99),
]
PHASE_LABEL_X = 1002.95      # anchored to the left margin
N_TIER_LABELS = [
    ("Presentation Tier", 1698.99),
    ("Application Tier",  1913.99),
    ("Data Tier",         2293.99),
    ("External System",   2473.99),
]
N_TIER_LABEL_X = 1067.95
N_TIER_LABEL_W = 105
```

### Participant boxes

```
PARTICIPANT_TOP  = 1631.99
PARTICIPANT_H    = 42
ACTOR_W          = 60          # Student
STANDARD_W       = 130        # all others
TITLE_W          = 800
TITLE_X          = 1142.95    # centered between left edge and right edge
```

### Activation bars (user-corrected geometry)

```
ACT_UI_AUTH   y=1703.99  h=135
ACT_CT_AUTH   y=1740.00  h=60
ACT_UI_BROWSE y=1883.99  h=215
ACT_CT_BROWSE y=1913.99  h=155
ACT_SV_BROWSE y=1943.99  h=95
ACT_CR_BROWSE y=1973.99  h=30
ACT_UI_REG    y=2133.99  h=505
ACT_CT_REG    y=2170.00  h=445
ACT_SV_REG    y=2200.00  h=385
ACT_CR_REG    y=2222.00  h=30
ACT_RR_REG1   y=2293.99  h=40
ACT_SV_REG2   y=2364.99  h=35
ACT_RR_REG2   y=2380.00  h=30
ACT_BS_REG    y=2450.00  h=100
ACT_BL_REG    y=2479.99  h=30
```

These positions keep the activation bars growing *rightward* into the
diagram (centered on their lifeline), matching how draw.io's
auto-layout would render them after the user dragged each one into
place.

---

## 3. Message Endpoint Style

User-modified edges use **absolute `sourcePoint` / `targetPoint`
coordinates only**, with `relative="1"` on the geometry. None of them
use `source=` or `target=` attributes. This is the same approach as
generator v8.

**Important:** the user trimmed arrow endpoints so they sit just
*inside* the lifeline width (X ± 0.5) instead of being offset by full
lifeline spacing. Edges terminate at the actual lifeline line, not
some arbitrary offset.

Example from the user-corrected file (edge 1):

```xml
<mxCell id="..." edge="1" parent="...">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="1133.445842133628" y="1703.9861738416885"
             as="sourcePoint" />
    <mxPoint x="1272.445842133628" y="1703.9861738416885"
             as="targetPoint" />
  </mxGeometry>
</mxCell>
```

**Y coordinates are not always at the round `PHASE_LABEL_Y`** — they
shift ±1 px depending on activation-bar end positions, mirroring
what the user nudged in the editor.

---

## 4. Items the User Did NOT Change

- All 31 message labels and types (call / return / self)
- All participant names and stereotypes
- B&W colour scheme — no fills, `strokeColor=#000000`
- All N-Tier label texts
- Lifeline dashed gray style (`strokeColor=#CCCCCC`)

---

## 5. New Lessons for the Generator

1. **Absolute coordinates only** — never mix `source=`/`target=` with
   `sourcePoint`/`targetPoint`. The user never touched the
   `source=`/`target=` fields.
2. **Lifeline X = box center − 0.5** — the offset of 0.5 px aligns the
   dashed line to the centre of the participant rectangle.
3. **Activation-bar height must extend past the last return
   message** — the user stretched each bar so its top sits *just
   above* the outgoing call and its bottom sits *just below* the
   last return (gives the canonical UML look of nested activations).
4. **Self-loop waypoints** still need an explicit `<Array as="points">`
   with two extra mxPoint entries — draw.io does not auto-route loops.

---

## 6. Decision: Generator Must Output the User's Coordinate Space

Going forward `generate_drawio.py` should produce the same coordinate
space as `Assignment1.drawio` (START_X = 1132.45, TITLE_Y = 1605.99)
so the generated diagram renders identically to the user's reference
output, and re-saving in draw.io does not shift anything.