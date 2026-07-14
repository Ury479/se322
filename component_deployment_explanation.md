# Component Diagram & Deployment Diagram
## SE322 Case Study: Student Opinion Collection System

---

## 1. Case Study Summary

An application for collecting students' opinions about courses:

| Actor | Capabilities | Deployment |
|-------|-------------|------------|
| **Student** | Read, Insert, Update, Persist course schedule data | PC client (sw1, sw2) |
| **Professor/Manager** | View statistical elaboration only | PC client (manager's office) |
| **Server** | Database + course management components | One or more servers |

---

## 2. Component Diagram

### 2.1 Components Identified

| Component | Stereotype | Responsibility |
|-----------|-----------|----------------|
| **Student** | `<<client>>` | Student application (instances sw1, sw2); provides UI for Read/Insert/Update |
| **Manager** | `<<client>>` | Manager application; provides UI for viewing statistics |
| **SecurityServer** | `<<subsystem>>` | Mediates all client access; enforces authentication/authorization |
| **CourseArchitetture** | `<<subsystem>>` | Course management business logic |
| **DBAccess** | `<<entity>>` | Data access layer for database operations |
| **Office** | `<<entity>>` | Manager office data/entity component |

### 2.2 Interfaces (Provided = Ball, Required = Socket)

| Interface | Provided By | Used By | Purpose |
|-----------|------------|---------|---------|
| `iSecForStud` | SecurityServer | Student | Student authentication gateway |
| `iSecForMan` | SecurityServer | Manager | Manager authentication gateway |
| `iCourseForStud` | CourseArchitetture | Student (via SecurityServer) | Course CRUD operations for students |
| `iCourseForMan` | CourseArchitetture | Manager (via SecurityServer) | Course statistics for managers |
| `iDBAforStud` | DBAccess | SecurityServer (delegated) | Student data persistence |
| `iDBAforCourse` | DBAccess | CourseArchitetture | Course data persistence |
| `iDBAforMan` | DBAccess | SecurityServer (delegated) | Manager data access |
| `iOFF` | Office | Manager | Office/entity access |

### 2.3 Connector Types

- **Assembly connectors** (`<<use>>`): Connect a required interface (socket) to a provided interface (ball) between two components
- **Delegation connectors** (`<<delegate>>`): Forward signals from a component's external interface to its internal realizations

### 2.4 Design Rationale

1. **SecurityServer as mediator**: All client requests pass through SecurityServer, enforcing the principle that no client directly accesses the database
2. **Separation of concerns**: CourseArchitetture handles business logic, DBAccess handles persistence, SecurityServer handles authentication
3. **Replaceability**: Each component communicates only through interfaces, making them independently replaceable
4. **N-Tier consistency**: Client Tier → Security Tier → Application Tier → Data Tier mirrors the sequence diagram architecture

---

## 3. Deployment Diagram

### 3.1 Nodes (Hardware)

| Node | Type | Location |
|------|------|----------|
| **Client Stud** | PC Client | Student workstations (sw1, sw2) |
| **Server** | Server | Central server room |
| **Client Man** | PC Client | Manager's office |

### 3.2 Artifacts (Software Deployed)

| Node | Artifacts |
|------|-----------|
| **Client Stud** | `Stud` (Student Application) |
| **Server** | `DB` (Database), `DBAccess`, `SecStud` (Security), `CourseIs2`, `CourseArch` |
| **Client Man** | `Office` (Manager App), `Manager`, `SecurityServer`, `SecMan` |

### 3.3 Communication Paths

- **Client Stud ↔ Server**: TCP/IP
- **Server ↔ Client Man**: TCP/IP

### 3.4 Relationship to Component Diagram

The deployment diagram shows the **physical realization** of the component diagram:
- Components defined in the Component Diagram are deployed as artifacts on physical nodes
- The SecurityServer component runs on the Server node
- Student and Manager client components run on their respective PC clients
- Communication paths specify the network protocol (TCP/IP)

---

## 4. UML Compliance Checklist

### Component Diagram
- [x] Components shown as rectangles with `<<component>>` stereotype
- [x] Provided interfaces (ball/lollipop notation)
- [x] Required interfaces (socket notation)
- [x] Assembly connectors (ball-and-socket wiring)
- [x] Delegation connectors (`<<delegate>>`)
- [x] Usage dependencies (`<<use>>`)

### Deployment Diagram
- [x] Nodes shown as 3D cubes with `<<node>>` stereotype
- [x] Artifacts shown with `<<artifact>>` stereotype
- [x] Communication paths with protocol labels
- [x] Artifacts nested within their hosting nodes
- [x] Physical topology reflects case study requirements

---

## 5. Files

| File | Description |
|------|-------------|
| `Component_Diagram.drawio` | draw.io source (editable) |
| `Component_Diagram.png` | Exported preview (1280×918) |
| `generate_component_diagram.py` | Python generator script |
| `Deployment_Diagram.drawio` | draw.io source (editable) |
| `Deployment_Diagram.png` | Exported preview (1085×733) |
| `generate_deployment_diagram.py` | Python generator script |
| `component_deployment_explanation.md` | This document |

### Regeneration
```bash
cd /Users/ury/Documents/se322
python3 generate_component_diagram.py
python3 generate_deployment_diagram.py
drawio --export --format png --output Component_Diagram.png Component_Diagram.drawio
drawio --export --format png --output Deployment_Diagram.png Deployment_Diagram.drawio
```
