#!/usr/bin/env python3
"""
Generate UML Deployment Diagram for SE322 Case Study:
"Student Opinion Collection System"

Case Study Requirements:
- Student application installed on PC client (sw1, sw2)
- Manager application installed on PC client (manager's office)
- One or more servers with DataBase and course management components

Deployment Diagram shows:
- Hardware nodes (3D boxes): Client Stud, Client Man, Server
- Communication paths (TCP/IP)
- Artifacts (<<artifact>> stereotypes) deployed on each node

Rules (from AGENTS.md + drawio conventions):
- Raw string concatenation ONLY
- relative="1" on edge geometry
- Absolute sourcePoint/targetPoint
- Pure B&W academic style
"""

import os

OUT = os.path.join(os.path.dirname(__file__), "Deployment_Diagram.drawio")

W, H = 1200, 950
cells = []


def esc(s):
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def add_cell(cid, xml):
    cells.append((str(cid), xml))


# Node positions (3D box = cube shape)
NODE_W, NODE_H = 280, 200

nodes = {
    "ClientStud": {"x": 60, "y": 250, "label": "Client Stud<br><i>(sw1, sw2)</i>"},
    "Server":     {"x": 460, "y": 250, "label": "Server<br><i>(DB + Course Mgmt)</i>"},
    "ClientMan":  {"x": 860, "y": 250, "label": "Client Man<br><i>(Manager's Office)</i>"},
}

# Artifacts inside each node
artifacts = {
    "ClientStud": ["Stud (Student App)"],
    "Server": ["DB (Database)", "DBAccess", "SecStud (Security)", "CourseIs2", "CourseArch"],
    "ClientMan": ["Office (Manager App)", "Manager", "SecurityServer", "SecMan"],
}

# ---- Title ----
add_cell("100", (
    f'        <mxCell id="100" value="{esc("<b>Deployment Diagram: Student Opinion Collection System</b><br><i>(SE322 Case Study)</i>")}" '
    f'style="text;html=1;align=center;verticalAlign=top;strokeColor=none;fillColor=none;'
    f'fontFamily=Helvetica;fontSize=14;fontColor=#000000;" vertex="1" parent="1">\n'
    f'          <mxGeometry x="200" y="40" width="800" height="40" as="geometry" />\n'
    f'        </mxCell>\n'
))

# ---- Nodes (3D cubes) ----
node_ids = {}
cid = 200

for key, info in nodes.items():
    style = ("shape=cube;whiteSpace=wrap;html=1;"
             "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"
             "fontFamily=Helvetica;fontSize=12;fontColor=#000000;"
             "darkOpacity=0.15;size=14;align=center;verticalAlign=top;spacingTop=8;")
    label = f"<b>&lt;&lt;node&gt;&gt;</b><br>{info['label']}"
    xml = (
        f'        <mxCell id="{cid}" value="{esc(label)}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{info["x"]}" y="{info["y"]}" width="{NODE_W}" height="{NODE_H}" as="geometry" />\n'
        f'        </mxCell>\n'
    )
    node_ids[key] = cid
    add_cell(cid, xml)
    cid += 1

# ---- Artifacts (rectangles with <<artifact>> stereotype) inside nodes ----
artifact_ids = {}

for node_key, arts in artifacts.items():
    nx = nodes[node_key]["x"]
    ny = nodes[node_key]["y"]
    for i, art_name in enumerate(arts):
        ay = ny + 55 + i * 28
        style = ("rounded=0;whiteSpace=wrap;html=1;"
                 "fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;"
                 "fontFamily=Helvetica;fontSize=9;fontColor=#000000;"
                 "dashed=0;align=left;spacingLeft=8;verticalAlign=middle;")
        label = f"&lt;&lt;artifact&gt;&gt; {art_name}"
        xml = (
            f'        <mxCell id="{cid}" value="{esc(label)}" style="{style}" vertex="1" parent="1">\n'
            f'          <mxGeometry x="{nx + 20}" y="{ay}" width="{NODE_W - 40}" height="22" as="geometry" />\n'
            f'        </mxCell>\n'
        )
        artifact_ids[f"{node_key}_{art_name}"] = cid
        add_cell(cid, xml)
        cid += 1

# ---- Communication paths (edges between nodes) ----
LINE_LABEL = ("endArrow=none;html=1;strokeColor=#000000;strokeWidth=1.5;"
              "fontFamily=Helvetica;fontSize=10;fontColor=#000000;"
              "verticalAlign=bottom;align=center;labelBackgroundColor=#FFFFFF;")

# ClientStud → Server (TCP/IP)
cs = nodes["ClientStud"]
sv = nodes["Server"]
add_cell(cid, (
    f'        <mxCell id="{cid}" value="{esc("TCP/IP")}" style="{LINE_LABEL}" edge="1" parent="1">\n'
    f'          <mxGeometry relative="1" as="geometry">\n'
    f'            <mxPoint x="{cs["x"] + NODE_W}" y="{cs["y"] + NODE_H // 2}" as="sourcePoint" />\n'
    f'            <mxPoint x="{sv["x"]}" y="{sv["y"] + NODE_H // 2}" as="targetPoint" />\n'
    f'          </mxGeometry>\n'
    f'        </mxCell>\n'
))
cid += 1

# Server → ClientMan (TCP/IP)
cm = nodes["ClientMan"]
add_cell(cid, (
    f'        <mxCell id="{cid}" value="{esc("TCP/IP")}" style="{LINE_LABEL}" edge="1" parent="1">\n'
    f'          <mxGeometry relative="1" as="geometry">\n'
    f'            <mxPoint x="{sv["x"] + NODE_W}" y="{sv["y"] + NODE_H // 2}" as="sourcePoint" />\n'
    f'            <mxPoint x="{cm["x"]}" y="{cm["y"] + NODE_H // 2}" as="targetPoint" />\n'
    f'          </mxGeometry>\n'
    f'        </mxCell>\n'
))
cid += 1

# ---- Legend ----
ly = 720
add_cell(cid, (
    f'        <mxCell id="{cid}" value="{esc("<b>&lt;&lt;node&gt;&gt;</b><br>Hardware Node")}" '
    f'style="shape=cube;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;'
    f'strokeWidth=1;fontFamily=Helvetica;fontSize=9;darkOpacity=0.15;size=8;" vertex="1" parent="1">\n'
    f'          <mxGeometry x="100" y="{ly}" width="100" height="50" as="geometry" />\n'
    f'        </mxCell>\n'
))
cid += 1

add_cell(cid, (
    f'        <mxCell id="{cid}" value="{esc("&lt;&lt;artifact&gt;&gt;")}" '
    f'style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;'
    f'strokeWidth=1;fontFamily=Helvetica;fontSize=9;" vertex="1" parent="1">\n'
    f'          <mxGeometry x="300" y="{ly + 10}" width="120" height="30" as="geometry" />\n'
    f'        </mxCell>\n'
))
cid += 1

add_cell(cid, (
    f'        <mxCell id="{cid}" value="{esc("Communication Path")}" style="{LINE_LABEL}" edge="1" parent="1">\n'
    f'          <mxGeometry relative="1" as="geometry">\n'
    f'            <mxPoint x="500" y="{ly + 25}" as="sourcePoint" />\n'
    f'            <mxPoint x="600" y="{ly + 25}" as="targetPoint" />\n'
    f'          </mxGeometry>\n'
    f'        </mxCell>\n'
))

# ---- Build XML ----
cells_xml = "".join(xml for _, xml in cells)

xml = f'''<mxfile host="app.diagrams.net" agent="SE322-DeploymentDiagram" version="24.2.5">
  <diagram id="deploy-diagram-01" name="Deployment Diagram">
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

ids = [c for c, _ in cells]
dupes = [x for x in ids if ids.count(x) > 1]
if dupes:
    print(f"WARNING: Duplicate IDs: {set(dupes)}")
else:
    print("✓ All IDs unique")
