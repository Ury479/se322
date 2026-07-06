#!/usr/bin/env python3
"""
SE322 'Maintain Curriculum' — draw.io sequence diagram generator.

Use case: Maintain Curriculum (main) with includes
  - Logon Validation
  - Create Course
  - Maintain Schedule

N-Tier Architecture:
  Presentation  → Registrar (actor), RegistrarPortal, CurriculumUI
  Application   → CurriculumController, AuthService, CurriculumService,
                  CourseService, ScheduleService
  Data          → CurriculumRepository, CourseRepository,
                  ScheduleRepository, Database

Follows the same coordinate system as generate_drawio.py v9:
  - Absolute sourcePoint/targetPoint edges, relative=1
  - B&W only, raw string concatenation (no XML libs)
"""
import os, re, xml.parsers.expat
from collections import Counter

OUT = "/Users/ury/Documents/se322/Maintain_Curriculum_Sequence_Diagram.drawio"

# ─── Coordinate system ──────────────────────────────────────────────
START_X = 90
GAP_X = 115
PAGE_W = 1450
PAGE_H = 2000

LIFELINE_TOP = 130
LIFELINE_H = 1850
TITLE_Y = 50
TITLE_W = 1100
TITLE_X = (PAGE_W - TITLE_W) / 2
PARTICIPANT_TOP = 80
PARTICIPANT_H = 42

PIDS = ["R", "RP", "UI", "CT", "AS", "CS", "CRS", "SS",
        "CR", "CRR", "SR", "DB"]
LIFELINE_X = {p: START_X + i * GAP_X for i, p in enumerate(PIDS)}

BOX_W = {"actor": 60, "boundary": 120, "control": 120,
         "entity": 120, "external": 120}

# Participant definitions
PARTS = [
    ("R",   "Registrar",                 "actor"),
    ("RP",  "RegistrarPortal",           "boundary"),
    ("UI",  "CurriculumUI",              "boundary"),
    ("CT",  "CurriculumController",      "control"),
    ("AS",  "AuthService",               "control"),
    ("CS",  "CurriculumService",         "control"),
    ("CRS", "CourseService",             "control"),
    ("SS",  "ScheduleService",           "control"),
    ("CR",  "CurriculumRepository",      "entity"),
    ("CRR", "CourseRepository",          "entity"),
    ("SR",  "ScheduleRepository",        "entity"),
    ("DB",  "Database",                  "entity"),
]

# Phase labels (left margin)
PHASES = [
    ("Logon Validation (include)",            140),
    ("Maintain Curriculum (main flow)",       500),
    ("Create Course (include)",               1200),
    ("Maintain Schedule (include)",           1480),
]
PHASE_LABEL_X = 10

# N-Tier sidebar labels (anchored to right margin)
N_TIERS = [
    ("Presentation Tier",  100,  520),
    ("Application Tier",   540, 1000),
    ("Data Tier",         1020, 1500),
]
N_TIER_X = PAGE_W - 130
N_TIER_W = 110

# Activation bars: (pid, y_top, height)
ACTS = [
    # Logon Validation
    ("RP", 160, 50),                       # 160 → 210
    ("UI", 240, 250),                      # 240 → 490
    ("CT", 280, 170),                      # 280 → 450
    ("AS", 320,  90),                      # 320 → 410

    # Maintain Curriculum main
    ("UI", 520, 410),                      # 520 → 930
    ("CT", 560, 650),                      # 560 → 1210
    ("CS", 600, 570),                      # 600 → 1170
    ("CR", 640, 490),                      # 640 → 1130
    ("DB", 680, 410),                      # 680 → 1090

    # Create Course include
    ("CRS", 1240, 210),                    # 1240 → 1450
    ("CRR", 1320,  90),                    # 1320 → 1410
    ("DB",  1360,  50),                    # 1360 → 1410

    # Maintain Schedule include
    ("SS", 1520, 210),                     # 1520 → 1730
    ("SR", 1600,  90),                     # 1600 → 1690
    ("DB",  1640,  50),                    # 1640 → 1690

    # Final return confirmation
    ("UI", 1800,  50),                     # 1800 → 1850
]

# Messages: (from, to, label, y, type)
# type ∈ {call, retn, self}
MSGS = [
    # ── Phase 1: Logon Validation ──────────────────────────────
    ("R",   "RP",  "1: openPortal()",                         160, "call"),
    ("RP",  "R",   "2: requestLogin()",                      200, "retn"),
    ("R",   "UI",  "3: enterCredentials(id, password)",       240, "call"),
    ("UI",  "CT",  "4: login(id, password)",                  280, "call"),
    ("CT",  "AS",  "5: validate(id, password)",               320, "call"),
    ("AS",  "AS",  "6: validateCredentials()",                360, "self"),
    ("AS",  "CT",  "7: loginResult(success)",                 400, "retn"),
    ("CT",  "UI",  "8: loginStatus(success)",                 440, "retn"),
    ("UI",  "R",   "9: showDashboard()",                      480, "retn"),

    # ── Phase 2: Maintain Curriculum main ──────────────────────
    ("R",   "UI",  "10: selectMaintainCurriculum()",          520, "call"),
    ("UI",  "CT",  "11: maintainCurriculum()",                560, "call"),
    ("CT",  "CS",  "12: getCurriculum()",                     600, "call"),
    ("CS",  "CR",  "13: findAll()",                           640, "call"),
    ("CR",  "DB",  "14: SELECT * FROM curriculum",            680, "call"),
    ("DB",  "CR",  "15: curriculumData",                      720, "retn"),
    ("CR",  "CS",  "16: curriculums",                         760, "retn"),
    ("CS",  "CT",  "17: curriculumList",                      800, "retn"),
    ("CT",  "UI",  "18: displayCurriculum(curriculums)",      840, "retn"),
    ("UI",  "R",   "19: showCurriculumForm()",                880, "retn"),
    ("R",   "UI",  "20: updateCurriculum(info)",              920, "call"),
    ("UI",  "CT",  "21: updateCurriculum(info)",              960, "call"),
    ("CT",  "CS",  "22: saveCurriculum(info)",               1000, "call"),
    ("CS",  "CR",  "23: save(curriculum)",                   1040, "call"),
    ("CR",  "DB",  "24: INSERT INTO curriculum",             1080, "call"),
    ("DB",  "CR",  "25: saved",                              1120, "retn"),
    ("CR",  "CS",  "26: savedCurriculum",                    1160, "retn"),
    ("CS",  "CT",  "27: saveResult(success)",                1200, "retn"),

    # ── Phase 3: Create Course (include) ───────────────────────
    ("CT",  "CRS", "28: createCourse(courseInfo)",           1240, "call"),
    ("CRS", "CRS", "29: validateCourseInfo()",               1280, "self"),
    ("CRS", "CRR", "30: save(course)",                       1320, "call"),
    ("CRR", "DB",  "31: INSERT INTO course",                 1360, "call"),
    ("DB",  "CRR", "32: saved",                              1400, "retn"),
    ("CRR", "CRS", "33: savedCourse",                        1440, "retn"),

    # ── Phase 4: Maintain Schedule (include) ───────────────────
    ("CT",  "SS",  "34: maintainSchedule(scheduleInfo)",     1480, "call"),
    ("SS",  "SS",  "35: checkTimeConflict()",                1520, "self"),
    ("SS",  "SR",  "36: save(schedule)",                     1560, "call"),
    ("SR",  "DB",  "37: INSERT INTO schedule",               1600, "call"),
    ("DB",  "SR",  "38: saved",                              1640, "retn"),
    ("SR",  "SS",  "39: savedSchedule",                      1680, "retn"),
    ("SS",  "CT",  "40: scheduleResult(success)",            1720, "retn"),

    # ── Final confirmation ─────────────────────────────────────
    ("CT",  "UI",  "41: showConfirmation(success)",          1800, "retn"),
    ("UI",  "R",   "42: maintainCurriculumSuccess()",        1840, "retn"),
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
    """Edge with absolute coordinate endpoints, relative=1 geometry."""
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
    """Self-loop edge: exits to the right, loops up and back."""
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
    "<b>Sequence Diagram: Maintain Curriculum</b><br>"
    "<i>(N-Tier Architecture — XYZ Tutoring Center — SE322 — "
    "Use Case with Includes: Logon Validation, Create Course, Maintain Schedule)</i>",
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;"
    "fontFamily=Helvetica;fontSize=14;fontColor=#000000;",
    {"x": str(TITLE_X), "y": str(TITLE_Y),
     "width": str(TITLE_W), "height": "30"})

# 2. Phase labels (left margin)
for tx, py in PHASES:
    vert(f"<b>{tx}</b>",
         "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
         "fontFamily=Helvetica;fontSize=10;fontColor=#888888;",
         {"x": str(PHASE_LABEL_X), "y": str(py),
          "width": "200", "height": "18"})

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
               "fontFamily=Helvetica;fontSize=10;")
    vert(lbl, sty,
         {"x": str(x), "y": str(PARTICIPANT_TOP),
          "width": str(w), "height": str(PARTICIPANT_H)})

# 4. Lifelines (dashed gray)
for pid in PIDS:
    cx = LIFELINE_X[pid]
    vert("",
         "dashed=1;strokeColor=#CCCCCC;verticalAlign=bottom;points=[];",
         {"x": str(cx - 0.5), "y": str(LIFELINE_TOP),
          "width": "1", "height": str(LIFELINE_H)})

# 5. Activation bars (visual only)
for pid, y0, h in ACTS:
    cx = LIFELINE_X[pid]
    vert("",
         "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;"
         "verticalAlign=bottom;noLabel=1;",
         {"x": str(cx - 7), "y": str(y0),
          "width": "14", "height": str(h)})

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
        edge_self(lb, SELF, LIFELINE_X[to], y, LIFELINE_X[to] + 35)
    else:
        sty = CALL if mt == "call" else RETN
        fi = PIDS.index(fr)
        ti = PIDS.index(to)
        # Terminate edges just inside the lifeline (X ± 0.5 px)
        if fi < ti:  # left → right
            x1 = LIFELINE_X[fr] + 0.5
            x2 = LIFELINE_X[to] - 0.5
        else:        # right → left
            x1 = LIFELINE_X[fr] - 0.5
            x2 = LIFELINE_X[to] + 0.5
        edge_exact(lb, sty, x1, y, x2, y)

# 7. N-Tier sidebar labels (right margin, span their tier range)
TIER_STYLE = ("rounded=0;whiteSpace=wrap;html=1;fontFamily=Helvetica;fontSize=9;"
              "fontColor=#444444;fillColor=#FFFFFF;strokeColor=#666666;"
              "strokeWidth=1;align=center;verticalAlign=middle;")
# Top-tier bracket (Presentation)
vert("<b>Presentation Tier</b>", TIER_STYLE,
     {"x": str(N_TIER_X), "y": "100", "width": str(N_TIER_W), "height": "18"})
# Application Tier bracket (mid)
vert("<b>Application Tier</b>", TIER_STYLE,
     {"x": str(N_TIER_X), "y": "540", "width": str(N_TIER_W), "height": "18"})
# Data Tier bracket (bottom)
vert("<b>Data Tier</b>", TIER_STYLE,
     {"x": str(N_TIER_X), "y": "1020", "width": str(N_TIER_W), "height": "18"})

# ═══ ASSEMBLE ═══
L = []
L.append('<mxfile host="app.diagrams.net" agent="SE322" version="24.2.5">\n')
L.append('  <diagram id="seq-diagram-02" name="Maintain Curriculum">\n')
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

ret = os.system('drawio --export --format png --output /tmp/maintain_curriculum.png "'
                + OUT + '" 2>/dev/null')
print(f"{'✅' if ret == 0 else '❌'} draw.io export "
      f"{'succeeded' if ret == 0 else 'failed'}")

if ret == 0:
    import subprocess
    r = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight',
                        '/tmp/maintain_curriculum.png'],
                       capture_output=True, text=True)
    for line in r.stdout.strip().split('\n'):
        if 'pixel' in line:
            print(f"   {line.strip()}")