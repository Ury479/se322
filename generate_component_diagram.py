#!/usr/bin/env python3
"""
Generate UML Component Diagram for SE322 Case Study:
"Student Opinion Collection System"

Case Study Requirements:
- Student app (PC clients sw1, sw2): Read, Insert, Update courses in schedule
- Manager app (manager's office PC): View statistics only
- Server(s): Database + course management components
- Security: Security Server mediates access

Components & Interfaces (following course solution pattern on p80):
- Student (client apps: pStud1, pStud2, pStud3)
- Manager (client app)
- SecurityServer: provides iSecForStud, iSecForMan
- DBAccess: provides iDBAforStud, iDBAforCourse, iDBAforMan
- CourseArchitetture: provides iCourseForStud, iCourseForMan
- Office: provides iOFF

Rules (from AGENTS.md + drawio-sequence-diagram skill):
- Raw string concatenation ONLY (never XML libraries)
- relative="1" on edge geometry
- Absolute sourcePoint/targetPoint on all edges
- Pure B&W academic style
- Unique integer mxCell IDs
"""

import os

OUT = os.path.join(os.path.dirname(__file__), "Component_Diagram.drawio")

# Canvas
W, H = 1400, 1050

cells = []  # list of (id, xml_string)


def esc(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def add_cell(cid, xml):
    cells.append((str(cid), xml))
    return str(cid)


def component(cid, name, stereotype, x, y, w=170, h=70):
    """UML Component box with <<component>> stereotype and icon."""
    label = f"<b>{name}</b><br>&lt;&lt;{stereotype}&gt;&gt;"
    style = ("shape=component;align=center;html=1;whiteSpace=wrap;"
             "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
             "fontFamily=Helvetica;fontSize=11;fontColor=#000000;")
    xml = (
        f'        <mxCell id="{cid}" value="{esc(label)}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        f'        </mxCell>\n'
    )
    return add_cell(cid, xml)


def provided_interface(cid, name, x, y):
    """Provided interface (ball/lollipop): small circle with line."""
    # The ball
    ball_style = ("ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;"
                  "strokeColor=#000000;strokeWidth=1;fontFamily=Helvetica;fontSize=9;")
    xml = (
        f'        <mxCell id="{cid}" value="{esc(name)}" style="{ball_style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="14" height="14" as="geometry" />\n'
        f'        </mxCell>\n'
    )
    return add_cell(cid, xml)


def required_interface(cid, name, x, y):
    """Required interface (socket): half circle."""
    socket_style = ("shape=halfEllipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;"
                    "strokeColor=#000000;strokeWidth=1;fontFamily=Helvetica;fontSize=9;"
                    "direction=west;")
    xml = (
        f'        <mxCell id="{cid}" value="{esc(name)}" style="{socket_style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="14" height="14" as="geometry" />\n'
        f'        </mxCell>\n'
    )
    return add_cell(cid, xml)


def interface_label(cid, text, x, y, w=110, h=16):
    """Text label for an interface name."""
    style = ("text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;"
             "fillColor=none;strokeColor=none;fontFamily=Helvetica;fontSize=9;fontColor=#444444;")
    xml = (
        f'        <mxCell id="{cid}" value="{esc(text)}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        f'        </mxCell>\n'
    )
    return add_cell(cid, xml)


def edge_exact(cid, x1, y1, x2, y2, style, label=""):
    """Edge with absolute sourcePoint/targetPoint, relative=1."""
    vs = f' value="{esc(label)}"' if label else ""
    xml = (
        f'        <mxCell id="{cid}"{vs} style="{style}" edge="1" parent="1">\n'
        f'          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{x1}" y="{y1}" as="sourcePoint" />\n'
        f'            <mxPoint x="{x2}" y="{y2}" as="targetPoint" />\n'
        f'          </mxGeometry>\n'
        f'        </mxCell>\n'
    )
    return add_cell(cid, xml)


# ---- Styles ----
LINE = ("endArrow=none;html=1;strokeColor=#000000;strokeWidth=1;"
        "fontFamily=Helvetica;fontSize=9;")
DEP = ("endArrow=open;endFill=0;dashed=1;html=1;strokeColor=#000000;"
       "strokeWidth=1;fontFamily=Helvetica;fontSize=9;verticalAlign=bottom;labelBackgroundColor=#FFFFFF;")

# ---- Layout ----
# Components arranged in tiers
# Row 1 (y=180): Client tier - Student, Manager
# Row 2 (y=400): Security Server
# Row 3 (y=600): Course Management, DB Access
# Row 4 (y=850): Office

# Component positions (center X, top Y)
COMP_W, COMP_H = 180, 75

positions = {
    "Student":      (150, 180),
    "Manager":      (1050, 180),
    "Security":     (600, 380),
    "CourseMgmt":   (300, 600),
    "DBAccess":     (850, 600),
    "Office":       (1050, 850),
}

# Title
add_cell(100, (
    f'        <mxCell id="100" value="{esc("<b>Component Diagram: Student Opinion Collection System</b><br><i>(SE322 Case Study — N-Tier with Security Server)</i>")}" '
    f'style="text;html=1;align=center;verticalAlign=top;strokeColor=none;fillColor=none;'
    f'fontFamily=Helvetica;fontSize=14;fontColor=#000000;" vertex="1" parent="1">\n'
    f'          <mxGeometry x="250" y="50" width="900" height="40" as="geometry" />\n'
    f'        </mxCell>\n'
))

# Tier labels
def tier_label(cid, text, y):
    style = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;"
             "strokeWidth=1;align=center;verticalAlign=middle;fontFamily=Helvetica;"
             "fontSize=9;fontColor=#444444;")
    xml = (
        f'        <mxCell id="{cid}" value="{esc(f"<b>{text}</b>")}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="20" y="{y}" width="100" height="20" as="geometry" />\n'
        f'        </mxCell>\n'
    )
    return add_cell(cid, xml)

tier_label(101, "Client Tier", 210)
tier_label(102, "Security Tier", 410)
tier_label(103, "Application Tier", 630)
tier_label(104, "Data / External", 880)

# ---- Components ----
comp_ids = {}
cid_counter = 200

def next_cid():
    global cid_counter
    cid_counter += 1
    return cid_counter

# Student (client apps pStud1-3)
comp_ids["Student"] = component(next_cid(), "Student<br>(sw1, sw2)", "client", *positions["Student"])

# Manager
comp_ids["Manager"] = component(next_cid(), "Manager", "client", *positions["Manager"])

# SecurityServer
comp_ids["Security"] = component(next_cid(), "SecurityServer", "subsystem", *positions["Security"])

# CourseArchitetture
comp_ids["CourseMgmt"] = component(next_cid(), "CourseArchitetture", "subsystem", *positions["CourseMgmt"])

# DBAccess
comp_ids["DBAccess"] = component(next_cid(), "DBAccess", "entity", *positions["DBAccess"])

# Office
comp_ids["Office"] = component(next_cid(), "Office", "entity", *positions["Office"])

# ---- Interfaces ----
# For each interface, we create a ball (provided) or socket (required)
# and a connecting line to its component.

# Interface definitions: (name, provided_by_component_centerX, provided_by_Y, side)
# Provided interfaces (balls) - attached to components that OFFER the service
# Required interfaces (sockets) - attached to components that NEED the service

def make_provided(name, comp_key, offset_x, offset_y, label_offset_x=0, label_offset_y=-20):
    """Create a provided interface (ball) on a component."""
    cx, cy = positions[comp_key]
    ix = cx + offset_x
    iy = cy + offset_y
    ball = provided_interface(next_cid(), "", ix, iy)
    interface_label(next_cid(), name, ix - 50 + label_offset_x, iy + label_offset_y)
    # Line from component edge to ball
    edge_exact(next_cid(), cx + COMP_W // 2 if offset_x > 0 else cx,
               cy + offset_y + 7,
               ix + 7, iy + 7, LINE)
    return ix, iy, ball

def make_required(name, comp_key, offset_x, offset_y, label_offset_x=0, label_offset_y=-20):
    """Create a required interface (socket) on a component."""
    cx, cy = positions[comp_key]
    ix = cx + offset_x
    iy = cy + offset_y
    socket = required_interface(next_cid(), "", ix, iy)
    interface_label(next_cid(), name, ix - 50 + label_offset_x, iy + label_offset_y)
    # Line from component to socket
    edge_exact(next_cid(),
               cx + COMP_W if offset_x > 0 else cx,
               cy + offset_y + 7,
               ix + 7, iy + 7, LINE)
    return ix, iy, socket


# Provided interfaces (balls) - who OFFERS the service
# SecurityServer provides: iSecForStud, iSecForMan
sec_cx, sec_cy = positions["Security"]
# Left side ball: iSecForStud (for Student to use)
iSecStud_ball_x = sec_cx - 30
iSecStud_ball_y = sec_cy + 20
provided_interface(next_cid(), "", iSecStud_ball_x, iSecStud_ball_y)
interface_label(next_cid(), "iSecForStud", iSecStud_ball_x - 70, iSecStud_ball_y + 16, w=80)
edge_exact(next_cid(), iSecStud_ball_x + 14, iSecStud_ball_y + 7, sec_cx, iSecStud_ball_y + 7, LINE)

# Right side ball: iSecForMan (for Manager to use)
iSecMan_ball_x = sec_cx + COMP_W + 16
iSecMan_ball_y = sec_cy + 20
provided_interface(next_cid(), "", iSecMan_ball_x, iSecMan_ball_y)
interface_label(next_cid(), "iSecForMan", iSecMan_ball_x, iSecMan_ball_y + 16, w=80)
edge_exact(next_cid(), sec_cx + COMP_W, iSecMan_ball_y + 7, iSecMan_ball_x, iSecMan_ball_y + 7, LINE)

# DBAccess provides: iDBAforStud, iDBAforCourse, iDBAforMan
dba_cx, dba_cy = positions["DBAccess"]
# Left ball: iDBAforCourse (for CourseMgmt)
iDBACourse_ball_x = dba_cx - 30
iDBACourse_ball_y = dba_cy + 15
provided_interface(next_cid(), "", iDBACourse_ball_x, iDBACourse_ball_y)
interface_label(next_cid(), "iDBAforCourse", iDBACourse_ball_x - 90, iDBACourse_ball_y + 16, w=85)
edge_exact(next_cid(), iDBACourse_ball_x + 14, iDBACourse_ball_y + 7, dba_cx, iDBACourse_ball_y + 7, LINE)

# Top ball: iDBAforStud (for SecurityServer to delegate to Student access)
iDBAStud_ball_x = dba_cx + 30
iDBAStud_ball_y = dba_cy - 30
provided_interface(next_cid(), "", iDBAStud_ball_x, iDBAStud_ball_y)
interface_label(next_cid(), "iDBAforStud", iDBAStud_ball_x - 10, iDBAStud_ball_y - 16, w=80)
edge_exact(next_cid(), iDBAStud_ball_x + 7, iDBAStud_ball_y + 14, iDBAStud_ball_x + 7, dba_cy, LINE)

# Right ball: iDBAforMan
iDBAMan_ball_x = dba_cx + COMP_W + 16
iDBAMan_ball_y = dba_cy + 15
provided_interface(next_cid(), "", iDBAMan_ball_x, iDBAMan_ball_y)
interface_label(next_cid(), "iDBAforMan", iDBAMan_ball_x, iDBAMan_ball_y + 16, w=80)
edge_exact(next_cid(), dba_cx + COMP_W, iDBAMan_ball_y + 7, iDBAMan_ball_x, iDBAMan_ball_y + 7, LINE)

# CourseArchitetture provides: iCourseForStud, iCourseForMan
cm_cx, cm_cy = positions["CourseMgmt"]
# Top-left ball: iCourseForStud (delegated to Student via Security)
iCourseStud_ball_x = cm_cx + 30
iCourseStud_ball_y = cm_cy - 30
provided_interface(next_cid(), "", iCourseStud_ball_x, iCourseStud_ball_y)
interface_label(next_cid(), "iCourseForStud", iCourseStud_ball_x - 15, iCourseStud_ball_y - 16, w=90)
edge_exact(next_cid(), iCourseStud_ball_x + 7, iCourseStud_ball_y + 14, iCourseStud_ball_x + 7, cm_cy, LINE)

# Top-right ball: iCourseForMan
iCourseMan_ball_x = cm_cx + COMP_W + 16
iCourseMan_ball_y = cm_cy + 30
provided_interface(next_cid(), "", iCourseMan_ball_x, iCourseMan_ball_y)
interface_label(next_cid(), "iCourseForMan", iCourseMan_ball_x, iCourseMan_ball_y + 16, w=90)
edge_exact(next_cid(), cm_cx + COMP_W, iCourseMan_ball_y + 7, iCourseMan_ball_x, iCourseMan_ball_y + 7, LINE)

# Office provides: iOFF
off_cx, off_cy = positions["Office"]
iOFF_ball_x = off_cx + COMP_W + 16
iOFF_ball_y = off_cy + 30
provided_interface(next_cid(), "", iOFF_ball_x, iOFF_ball_y)
interface_label(next_cid(), "iOFF", iOFF_ball_x, iOFF_ball_y + 16, w=50)
edge_exact(next_cid(), off_cx + COMP_W, iOFF_ball_y + 7, iOFF_ball_x, iOFF_ball_y + 7, LINE)

# ---- Assembly Connectors (ball-to-socket wiring) ----
# These are solid lines connecting a required interface (socket) to a provided interface (ball)
# We simplify: draw <<use>> dependency arrows between components

# Student → SecurityServer (uses iSecForStud)
stu_cx, stu_cy = positions["Student"]
edge_exact(next_cid(),
           stu_cx + COMP_W, stu_cy + COMP_H // 2,
           iSecStud_ball_x, iSecStud_ball_y + 7,
           DEP, "&lt;&lt;use&gt;&gt; iSecForStud")

# Manager → SecurityServer (uses iSecForMan)
man_cx, man_cy = positions["Manager"]
edge_exact(next_cid(),
           man_cx, man_cy + COMP_H // 2,
           iSecMan_ball_x + 7, iSecMan_ball_y + 7,
           DEP, "&lt;&lt;use&gt;&gt; iSecForMan")

# SecurityServer → DBAccess (delegates to iDBAforStud)
edge_exact(next_cid(),
           sec_cx + COMP_W // 2, sec_cy + COMP_H,
           iDBAStud_ball_x + 7, iDBAStud_ball_y,
           DEP, "&lt;&lt;delegate&gt;&gt;")

# SecurityServer → DBAccess (iDBAforMan)
edge_exact(next_cid(),
           sec_cx + COMP_W, sec_cy + COMP_H,
           iDBAMan_ball_x, iDBAMan_ball_y + 7,
           DEP, "&lt;&lt;delegate&gt;&gt;")

# CourseArchitetture → DBAccess (uses iDBAforCourse)
edge_exact(next_cid(),
           cm_cx + COMP_W, cm_cy + COMP_H // 2,
           iDBACourse_ball_x, iDBACourse_ball_y + 7,
           DEP, "&lt;&lt;use&gt;&gt;")

# SecurityServer → CourseArchitetture (delegates iCourseForStud)
edge_exact(next_cid(),
           sec_cx, sec_cy + COMP_H,
           iCourseStud_ball_x + 7, iCourseStud_ball_y,
           DEP, "&lt;&lt;delegate&gt;&gt; iCourseForStud")

# Manager → Office (uses iOFF via direct access)
edge_exact(next_cid(),
           man_cx + COMP_W // 2, man_cy + COMP_H,
           off_cx + COMP_W // 2, off_cy,
           DEP, "&lt;&lt;use&gt;&gt; iOFF")

# ---- Legend ----
legend_y = 950
# Ball legend
provided_interface(next_cid(), "", 200, legend_y)
interface_label(next_cid(), "= Provided Interface (ball)", 220, legend_y - 2, w=180)
# Socket legend
required_interface(next_cid(), "", 450, legend_y)
interface_label(next_cid(), "= Required Interface (socket)", 470, legend_y - 2, w=190)
# Dependency legend
edge_exact(next_cid(), 720, legend_y + 7, 780, legend_y + 7, DEP)
interface_label(next_cid(), "= <<use>> / <<delegate>>", 790, legend_y - 2, w=160)

# ---- Build XML ----
cells_xml = "".join(xml for _, xml in cells)

xml = f'''<mxfile host="app.diagrams.net" agent="SE322-ComponentDiagram" version="24.2.5">
  <diagram id="comp-diagram-01" name="Component Diagram">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="{W}" pageHeight="{H}"
                  background="#FFFFFF" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
{cells_xml}      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(xml)

print(f"Generated: {OUT}")
print(f"Total mxCells: {len(cells)}")

# Validate IDs unique
ids = [cid for cid, _ in cells]
dupes = [x for x in ids if ids.count(x) > 1]
if dupes:
    print(f"WARNING: Duplicate IDs: {set(dupes)}")
else:
    print("✓ All IDs unique")
