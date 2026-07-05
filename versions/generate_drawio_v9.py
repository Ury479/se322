#!/usr/bin/env python3
"""
SE322 'Register for Courses' — v9: matches user's manually-corrected layout.

Coordinate space is taken from Assignment1.drawio (originally GW1.drawio)
which the user edited in app.diagrams.net. See USER_INTERFACE_MODIFICATIONS.md
for the rationale.

Key rules:
  - Pure B&W (fillColor=#FFFFFF, strokeColor=#000000).
  - Lifelines centered on box X (offset by -0.5 px).
  - All edges use absolute sourcePoint/targetPoint, relative=1.
  - No Python XML libraries — raw string concatenation only.
"""
import os, re, xml.parsers.expat
from collections import Counter

OUT = "/Users/ury/Documents/se322/Register_for_Courses_Sequence_Diagram.drawio"

# ─── User-corrected coordinate space ─────────────────────────────────
START_X = 1132.45
GAP_X   = 140
LIFELINE_TOP = 1679.99
LIFELINE_H   = 1000
TITLE_Y      = 1605.99
PARTICIPANT_TOP = 1631.99
PARTICIPANT_H   = 42
TITLE_W = 800
TITLE_X = 1142.95
PHASE_LABEL_X = 1002.95
N_TIER_LABEL_X = 1067.95
N_TIER_LABEL_W = 105

PIDS = ["S", "UI", "CT", "SV", "CR", "RR", "BS", "BL"]
LIFELINE_X = {p: START_X + i * GAP_X for i, p in enumerate(PIDS)}
# Actor box (Student) is narrower than the others.
BOX_W = {"actor": 60, "boundary": 130, "control": 130,
         "entity": 130, "external": 130}

# Participants (pid, label, stereotype)
PARTS = [
    ("S",  "Student",               "actor"),
    ("UI", "RegistrationUI",        "boundary"),
    ("CT", "RegistrationController", "control"),
    ("SV", "RegistrationService",   "control"),
    ("CR", "CourseRepository",      "entity"),
    ("RR", "RegistrationRepository", "entity"),
    ("BS", "BillingService",        "control"),
    ("BL", "BillingSystem",         "external"),
]

# Phase labels (left-margin grouping)
PHASES = [
    ("Authentication",        1703.99),
    ("Browse Courses",        1883.99),
    ("Register for Courses",  2133.99),
]

# N-Tier sidebar labels
N_TIERS = [
    ("Presentation Tier", 1698.99),
    ("Application Tier",  1913.99),
    ("Data Tier",         2293.99),
    ("External System",   2473.99),
]

# Activation bars: (pid, y0, height) — taken from user-corrected file.
ACTS = [
    ("UI", 1703.99, 135),   # Auth: UI active 1703.99 → 1838.99
    ("CT", 1740.00,  60),   # Auth: CT active 1740 → 1800
    ("UI", 1883.99, 215),   # Browse: UI active 1883.99 → 2098.99
    ("CT", 1913.99, 155),   # Browse: CT active 1913.99 → 2068.99
    ("SV", 1943.99,  95),   # Browse: SV active 1943.99 → 2038.99
    ("CR", 1973.99,  30),   # Browse: CR active 1973.99 → 2003.99
    ("UI", 2133.99, 505),   # Register: UI active 2133.99 → 2638.99
    ("CT", 2170.00, 445),   # Register: CT active 2170 → 2615
    ("SV", 2200.00, 385),   # Register: SV active 2200 → 2585
    ("CR", 2222.00,  30),   # Register: CR checkExists activation
    ("RR", 2293.99,  40),   # Register: RR checkExisting activation
    ("SV", 2364.99,  35),   # Register: SV (between RR calls)
    ("RR", 2380.00,  30),   # Register: RR save activation
    ("BS", 2450.00, 100),   # Register: BS generateInvoice activation
    ("BL", 2479.99,  30),   # Register: BL createInvoice activation
]

# Messages: (from, to, label, y, type)
# Y values match the user-corrected file (exact sourcePoint y values).
MSGS = [
    ("S",  "UI", "1: enterCredentials(id, password)",        1703.9861738416885, "call"),
    ("UI", "CT", "2: login(id, password)",                   1733.9861738416885, "call"),
    ("CT", "CT", "3: validateCredentials()",                 1763.9861738416885, "self"),
    ("CT", "UI", "4: loginResult(success)",                  1799.9961738416885, "retn"),
    ("UI", "S",  "5: showDashboard()",                       1823.9861738416885, "retn"),
    ("S",  "UI", "6: browseCourses()",                       1883.9861738416885, "call"),
    ("UI", "CT", "7: getCourseCatalog()",                    1922.5561738416884, "call"),
    ("CT", "SV", "8: getAvailableCourses()",                 1943.9861738416885, "call"),
    ("SV", "CR", "9: findAll()",                             1973.9861738416885, "call"),
    ("CR", "SV", "10: courses",                              2003.9861738416885, "retn"),
    ("SV", "CT", "11: availableCourses",                     2033.9861738416885, "retn"),
    ("CT", "UI", "12: displayCatalog(courses)",              2049.9961738416887, "retn"),
    ("UI", "S",  "13: showCourses(courses)",                 2093.9861738416885, "retn"),
    ("S",  "UI", "14: selectCourses(courses)",               2133.9861738416885, "call"),
    ("UI", "CT", "15: register(studentId, courses)",         2189.9961738416887, "call"),
    ("CT", "SV", "16: processRegistration(studentId, courses)", 2210.0,         "call"),
    ("SV", "CR", "17: checkExists(courseId)",                2222.0961738416886, "call"),
    ("CR", "SV", "18: exists(true/false)",                   2262.0961738416886, "retn"),
    ("SV", "RR", "19: checkExisting(studentId)",             2314.0861738416884, "call"),
    ("RR", "SV", "20: existingRegs",                         2337.0961738416886, "retn"),
    ("SV", "CR", "21: checkCapacity(courseId)",              2367.0961738416886, "call"),
    ("CR", "SV", "22: capacityOK(true/false)",               2389.9961738416887, "retn"),
    ("SV", "RR", "23: save(registration)",                   2402.0961738416886, "call"),
    ("RR", "SV", "24: savedReg",                             2427.0961738416886, "retn"),
    ("SV", "BS", "25: generateInvoice(studentId, regNo)",    2452.0961738416886, "call"),
    ("BS", "BL", "26: createInvoice(data)",                  2479.9961738416887, "call"),
    ("BL", "BS", "27: invoiceConfirmation",                  2509.9961738416887, "retn"),
    ("BS", "SV", "28: billingResult",                        2542.0961738416886, "retn"),
    ("SV", "CT", "29: registrationResult(success)",          2569.9961738416887, "retn"),
    ("CT", "UI", "30: showConfirmation()",                   2585.0,             "retn"),
    ("UI", "S",  "31: confirmation(details)",                2623.9861738416885, "retn"),
]


def esc(v):
    return (v.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


cells = []


def vert(val, style, geo, parent="1"):
    cid = str(len(cells) + 2)
    gs = " ".join(f'{k}="{esc(v)}"' for k, v in geo.items())
    vs = f' value="{esc(val)}"' if val else ""
    ss = f' style="{esc(style)}"' if style else ""
    cells.append((cid,
        f'        <mxCell id="{cid}"{vs}{ss} vertex="1" parent="{parent}">\n'
        f'          <mxGeometry {gs} as="geometry" />\n'
        f'        </mxCell>\n'))
    return cid


def edge_exact(val, style, x1, y1, x2, y2):
    """Edge with EXACT absolute coordinate endpoints, relative=1."""
    cid = str(len(cells) + 2)
    vs = f' value="{esc(val)}"' if val else ""
    ss = f' style="{esc(style)}"' if style else ""
    cells.append((cid,
        f'        <mxCell id="{cid}"{vs}{ss} edge="1" parent="1">\n'
        f'          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{x1}" y="{y1}" as="sourcePoint" />\n'
        f'            <mxPoint x="{x2}" y="{y2}" as="targetPoint" />\n'
        f'          </mxGeometry>\n'
        f'        </mxCell>\n'))
    return cid


def edge_self(val, style, x_line, y, loop_x):
    """Self-loop edge: exits right side, loops out and back."""
    cid = str(len(cells) + 2)
    vs = f' value="{esc(val)}"' if val else ""
    ss = f' style="{esc(style)}"' if style else ""
    cells.append((cid,
        f'        <mxCell id="{cid}"{vs}{ss} edge="1" parent="1">\n'
        f'          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{x_line}" y="{y}" as="sourcePoint" />\n'
        f'            <mxPoint x="{x_line}" y="{y}" as="targetPoint" />\n'
        f'            <Array as="points">\n'
        f'              <mxPoint x="{loop_x}" y="{y + 15}" />\n'
        f'              <mxPoint x="{loop_x}" y="{y - 30}" />\n'
        f'            </Array>\n'
        f'          </mxGeometry>\n'
        f'        </mxCell>\n'))
    return cid


# ═══ BUILD ═══

# 1. Title
vert(
    "<b>Sequence Diagram: Register for Courses</b><br>"
    "<i>(N-Tier Architecture — XYZ Tutoring Center — SE322)</i>",
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;"
    "fontFamily=Helvetica;fontSize=14;fontColor=#000000;",
    {"x": str(TITLE_X), "y": str(TITLE_Y),
     "width": str(TITLE_W), "height": "28"})

# 2. Phase labels (left margin)
for tx, py in PHASES:
    vert(f"<b>{tx}</b>",
         "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
         "fontFamily=Helvetica;fontSize=10;fontColor=#888888;",
         {"x": str(PHASE_LABEL_X), "y": str(py), "width": "100", "height": "18"})

# 3. Participant boxes
for pid, lab, stereo in PARTS:
    cx = LIFELINE_X[pid]
    w = BOX_W[stereo]
    x = cx - w / 2
    if stereo == "actor":
        lbl = lab
        sty = ("shape=umlActor;perimeter=actorPerimeter;whiteSpace=wrap;html=1;"
               "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;"
               "fontFamily=Helvetica;fontSize=11;")
    else:
        lbl = f"{lab}&#xa;&lt;&lt;{stereo}&gt;&gt;"
        sty = ("rounded=1;whiteSpace=wrap;html=1;"
               "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;"
               "fontFamily=Helvetica;fontSize=11;")
    vert(lbl, sty,
         {"x": str(x), "y": str(PARTICIPANT_TOP),
          "width": str(w), "height": str(PARTICIPANT_H)})

# 4. Lifelines (dashed gray, on lifeline X)
for pid in PIDS:
    cx = LIFELINE_X[pid]
    vert("",
         "dashed=1;strokeColor=#CCCCCC;verticalAlign=bottom;points=[];",
         {"x": str(cx - 0.5), "y": str(LIFELINE_TOP),
          "width": "1", "height": str(LIFELINE_H)})

# 5. Activation bars — purely visual, centered on lifeline X, 16px wide
for pid, y0, h in ACTS:
    cx = LIFELINE_X[pid]
    vert("",
         "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;"
         "verticalAlign=bottom;noLabel=1;",
         {"x": str(cx - 8), "y": str(y0), "width": "16", "height": str(h)})

# 6. Edges with absolute coordinates
CALL = ("fontFamily=Helvetica;fontSize=10;verticalAlign=bottom;align=center;"
        "labelBackgroundColor=#FFFFFF;endArrow=blockThin;endFill=1;"
        "strokeColor=#000000;strokeWidth=1;")
RETN = ("fontFamily=Helvetica;fontSize=10;verticalAlign=bottom;align=center;"
        "labelBackgroundColor=#FFFFFF;endArrow=open;endFill=0;"
        "strokeColor=#666666;dashed=1;strokeWidth=1;")
SELF = ("fontFamily=Helvetica;fontSize=10;verticalAlign=bottom;align=center;"
        "labelBackgroundColor=#FFFFFF;endArrow=blockThin;endFill=1;"
        "strokeColor=#000000;strokeWidth=1;")

for fr, to, lb, y, mt in MSGS:
    if mt == "self":
        # Self-loop on the CT lifeline — exit right, loop up and back.
        edge_self(lb, SELF, LIFELINE_X[to], y, LIFELINE_X[to] + 40)
    else:
        sty = CALL if mt == "call" else RETN
        fi = PIDS.index(fr)
        ti = PIDS.index(to)

        # Terminate edges just inside the lifeline (X ± 0.5 px) so
        # arrowheads sit neatly against the dashed line.
        if fi < ti:  # left → right
            x1 = LIFELINE_X[fr] + 0.5
            x2 = LIFELINE_X[to] - 0.5
        else:        # right → left
            x1 = LIFELINE_X[fr] - 0.5
            x2 = LIFELINE_X[to] + 0.5
        edge_exact(lb, sty, x1, y, x2, y)

# 7. N-Tier sidebar labels
for tx, ty in N_TIERS:
    vert(f"<b>{tx}</b>",
         "rounded=0;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=9;"
         "fontColor=#444444;fillColor=#FFFFFF;strokeColor=#666666;"
         "strokeWidth=1;align=center;verticalAlign=middle;",
         {"x": str(N_TIER_LABEL_X), "y": str(ty),
          "width": str(N_TIER_LABEL_W), "height": "18"})

# ═══ ASSEMBLE ═══
PAGE_W, PAGE_H = 1169, 1169
L = []
L.append('<mxfile host="app.diagrams.net" agent="SE322" version="24.2.5">\n')
L.append('  <diagram id="seq-diagram-01" name="Register for Courses">\n')
L.append(f'    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" '
         f'tooltips="1" connect="1" arrows="1" fold="1" page="1" '
         f'pageScale="1" pageWidth="{PAGE_W}" pageHeight="{PAGE_H}" '
         f'background="#FFFFFF" math="0" shadow="0">\n')
L.append('      <root>\n')
L.append('        <mxCell id="0" />\n')
L.append('        <mxCell id="1" parent="0" />\n')
for _, x in cells:
    L.append(x)
L.append('      </root>\n')
L.append('    </mxGraphModel>\n')
L.append('  </diagram>\n')
L.append('</mxfile>\n')

final = "".join(L)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(final)
sz = len(final)
print(f"✅ File saved: {OUT} ({sz} bytes)")

xml.parsers.expat.ParserCreate().Parse(final.encode("utf-8"), True)
mxids = re.findall(r'<mxCell[^>]*id="(\d+)"', final)
dups = {k for k, v in Counter(mxids).items() if v > 1}
print(f"✅ XML valid · {len(mxids)} mxCells · "
      f"{'❌ dup:' + str(dups) if dups else '✅ unique IDs'}")

ret = os.system('drawio --export --format png --output /tmp/test_v9.png "'
                + OUT + '" 2>/dev/null')
print(f"{'✅' if ret == 0 else '❌'} draw.io export "
      f"{'succeeded' if ret == 0 else 'failed'}")

if ret == 0:
    import subprocess
    r = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight',
                        '/tmp/test_v9.png'], capture_output=True, text=True)
    for line in r.stdout.strip().split('\n'):
        if 'pixel' in line:
            print(f"   {line.strip()}")