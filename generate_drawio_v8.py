#!/usr/bin/env python3
"""
SE322 'Register for Courses' — v8: precise horizontal edges via
sourcePoint/targetPoint mxPoint anchors, no shape-anchored edges.

Eliminates the "asymmetrical rectangles" bug by decoupling edges from
lifeline/activation-bar anchor calculations. Each arrow gets explicit
absolute coordinate endpoints with relative="1" to prevent canvas bloat.
"""
import os, re, xml.parsers.expat
from collections import Counter

OUT = "/Users/ury/Documents/se322/Register_for_Courses_Sequence_Diagram.drawio"

# Layout constants
GAP = 140
START = 140
PID_ORDER = ["S", "UI", "CT", "SV", "CR", "RR", "BS", "BL"]
CX = {pid: START + i * GAP for i, pid in enumerate(PID_ORDER)}

# Participant (pid, label, stereotype)
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

# Activation bars as VISUAL rects only (not edge anchors)
ACTS = [
    ("UI", 100, 135), ("CT", 130, 75),               # Auth
    ("UI", 280, 215), ("CT", 310, 155), ("SV", 340, 95), ("CR", 370, 30),  # Browse
    ("UI", 530, 505), ("CT", 560, 445), ("SV", 590, 385), ("CR", 620, 30),  # Register
    ("RR", 690, 40),  ("SV", 755, 35),  ("RR", 790, 30),
    ("BS", 840, 100), ("BL", 870, 30),
]

# Messages (from_pid, to_pid, label, y_pos, type)
MSGS = [
    ("S",  "UI", "1: enterCredentials(id, password)",     100,  "call"),
    ("UI", "CT", "2: login(id, password)",                130,  "call"),
    ("CT", "CT", "3: validateCredentials()",              160,  "self"),
    ("CT", "UI", "4: loginResult(success)",               195,  "retn"),
    ("UI", "S",  "5: showDashboard()",                    220,  "retn"),
    ("S",  "UI", "6: browseCourses()",                    280,  "call"),
    ("UI", "CT", "7: getCourseCatalog()",                 310,  "call"),
    ("CT", "SV", "8: getAvailableCourses()",              340,  "call"),
    ("SV", "CR", "9: findAll()",                          370,  "call"),
    ("CR", "SV", "10: courses",                           400,  "retn"),
    ("SV", "CT", "11: availableCourses",                  430,  "retn"),
    ("CT", "UI", "12: displayCatalog(courses)",           460,  "retn"),
    ("UI", "S",  "13: showCourses(courses)",              490,  "retn"),
    ("S",  "UI", "14: selectCourses(courses)",            530,  "call"),
    ("UI", "CT", "15: register(studentId, courses)",      560,  "call"),
    ("CT", "SV", "16: processRegistration(studentId, courses)", 590, "call"),
    ("SV", "CR", "17: checkExists(courseId)",             620,  "call"),
    ("CR", "SV", "18: exists(true/false)",                650,  "retn"),
    ("SV", "RR", "19: checkExisting(studentId)",          690,  "call"),
    ("RR", "SV", "20: existingRegs",                      725,  "retn"),
    ("SV", "CR", "21: checkCapacity(courseId)",           755,  "call"),
    ("CR", "SV", "22: capacityOK(true/false)",            780,  "retn"),
    ("SV", "RR", "23: save(registration)",                790,  "call"),
    ("RR", "SV", "24: savedReg",                          815,  "retn"),
    ("SV", "BS", "25: generateInvoice(studentId, regNo)", 840,  "call"),
    ("BS", "BL", "26: createInvoice(data)",               870,  "call"),
    ("BL", "BS", "27: invoiceConfirmation",               900,  "retn"),
    ("BS", "SV", "28: billingResult",                     930,  "retn"),
    ("SV", "CT", "29: registrationResult(success)",       960,  "retn"),
    ("CT", "UI", "30: showConfirmation()",                990,  "retn"),
    ("UI", "S",  "31: confirmation(details)",             1020, "retn"),
]

LIFELINE_TOP = 76
LIFELINE_H = 1000


def esc(v):
    return v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


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
    """
    Create an edge with EXACT absolute coordinate endpoints using
    sourcePoint/targetPoint mxPoint children, relative=1 on geometry.
    """
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


def edge_self(val, style, x_line, y1, y2, loop_x):
    """
    Create a self-loop edge with two intermediate waypoints.
    x_line = lifeline X, y1 = exit Y, y2 = entry Y (y2 < y1),
    loop_x = the horizontal position of the loop turn.
    """
    cid = str(len(cells) + 2)
    vs = f' value="{esc(val)}"' if val else ""
    ss = f' style="{esc(style)}"' if style else ""
    cells.append((cid,
        f'        <mxCell id="{cid}"{vs}{ss} edge="1" parent="1">\n'
        f'          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{x_line}" y="{y1}" as="sourcePoint" />\n'
        f'            <mxPoint x="{x_line}" y="{y2}" as="targetPoint" />\n'
        f'            <Array as="points">\n'
        f'              <mxPoint x="{loop_x}" y="{y1}" />\n'
        f'              <mxPoint x="{loop_x}" y="{y2}" />\n'
        f'            </Array>\n'
        f'          </mxGeometry>\n'
        f'        </mxCell>\n'))
    return cid


# ========== BUILD ==========

# 1. Title
vert(
    "<b>Sequence Diagram: Register for Courses</b><br>"
    "<i>(N-Tier Architecture — XYZ Tutoring Center — SE322)</i>",
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;"
    "fontFamily=Helvetica;fontSize=14;fontColor=#000000;",
    {"x": "150", "y": "2", "width": "800", "height": "28"})

# 2. Phase labels
for tx, py in [("Authentication", 100), ("Browse Courses", 280), ("Register for Courses", 530)]:
    vert(f"<b>{tx}</b>",
         "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
         "fontFamily=Helvetica;fontSize=10;fontColor=#888888;",
         {"x": "10", "y": str(py), "width": "100", "height": "18"})

# 3. Participant boxes (B&W)
BW = {"actor": 60, "boundary": 130, "control": 130, "entity": 130, "external": 130}
for pid, lab, stereo in PARTS:
    cx = CX[pid]
    w = BW[stereo]
    x = cx - w // 2
    if stereo == "actor":
        lbl = lab
        sty = ("shape=umlActor;perimeter=actorPerimeter;whiteSpace=wrap;html=1;"
               "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontFamily=Helvetica;fontSize=11;")
    else:
        lbl = f"{lab}&#xa;&lt;&lt;{stereo}&gt;&gt;"
        sty = ("rounded=1;whiteSpace=wrap;html=1;"
               "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontFamily=Helvetica;fontSize=11;")
    vert(lbl, sty, {"x": str(x), "y": "28", "width": str(w), "height": "42"})

# 4. Lifelines (dashed gray)
for pid, lab, stereo in PARTS:
    cx = CX[pid]
    vert("",
         "dashed=1;strokeColor=#CCCCCC;verticalAlign=bottom;points=[];",
         {"x": str(cx - 0.5), "y": str(LIFELINE_TOP), "width": "1", "height": str(LIFELINE_H)})

# 5. Activation bars — purely visual, centered on lifeline X
for pid, y0, h in ACTS:
    cx = CX[pid]
    vert("",
         "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;verticalAlign=bottom;noLabel=1;",
         {"x": str(cx - 8), "y": str(y0), "width": "16", "height": str(h)})

# 6. Edges with EXACT absolute coordinates
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
        # Self-loop: exit right side of lifeline, loop up and back
        edge_self(lb, SELF, CX[to], y, y - 30, CX[to] + 40)
    else:
        if mt == "call":
            sty = CALL
        else:
            sty = RETN

        # Arrow endpoints: offset from lifeline center so arrows have room
        # Left→right: source at right edge of from-lifeline, target at left edge of to-lifeline
        # Right→left: source at left edge of from-lifeline, target at right edge of to-lifeline
        fi = PID_ORDER.index(fr)
        ti = PID_ORDER.index(to)

        x1 = CX[fr]
        x2 = CX[to]

        # Add small offset so arrowheads sit neatly against lifelines
        if fi < ti:  # left → right
            x1 = CX[fr] + 0.5
            x2 = CX[to] - 0.5
        else:  # right → left
            x1 = CX[fr] - 0.5
            x2 = CX[to] + 0.5

        edge_exact(lb, sty, x1, y, x2, y)

# 7. N-Tier sidebar labels (B&W outline)
for tx, ty in [("Presentation Tier", 95), ("Application Tier", 310),
               ("Data Tier", 690), ("External System", 870)]:
    vert(f"<b>{tx}</b>",
         "rounded=0;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=9;fontColor=#444444;"
         "fillColor=#FFFFFF;strokeColor=#666666;strokeWidth=1;align=center;verticalAlign=middle;",
         {"x": "75", "y": str(ty), "width": "105", "height": "18"})

# ========== ASSEMBLE ==========
PAGE_W, PAGE_H = 1200, 1150
L = []
L.append('<mxfile host="app.diagrams.net" agent="SE322" version="24.2.5">\n')
L.append('  <diagram id="seq-diagram-01" name="Register for Courses">\n')
L.append(f'    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" '
         f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{PAGE_W}" '
         f'pageHeight="{PAGE_H}" background="#FFFFFF" math="0" shadow="0">\n')
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

ret = os.system('drawio --export --format png --output /tmp/test_v8.png "' + OUT + '" 2>/dev/null')
print(f"{'✅' if ret == 0 else '❌'} draw.io export {'succeeded' if ret == 0 else 'failed'}")

if ret == 0:
    import subprocess
    r = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', '/tmp/test_v8.png'],
                       capture_output=True, text=True)
    for line in r.stdout.strip().split('\n'):
        if 'pixel' in line:
            print(f"   {line.strip()}")
