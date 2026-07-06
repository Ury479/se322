# Maintain Curriculum — Sequence Diagram (UML + N-Tier Architecture)

## 1. Use case coverage

The diagram captures the **Maintain Curriculum** use case and the three
*include* relationships specified in the SE322 assignment:

| Flow | Phase in diagram | Messages |
|------|------------------|----------|
| **Logon Validation** (include) | Top band | 1 – 9 |
| **Maintain Curriculum** (main)  | Middle band | 10 – 27, 41 – 42 |
| **Create Course** (include)     | Lower band  | 28 – 33 |
| **Maintain Schedule** (include) | Bottom band | 34 – 40 |

`Maintain Curriculum` is the *main* flow; the three other flows fire
**inside** it whenever their pre-conditions are met:

- The user must clear **Logon Validation** before reaching the
  *Maintain Curriculum* page (steps 1 – 9 gate the entire diagram).
- The controller calls **Create Course** when new course rows must be
  appended (steps 28 – 33).
- The controller calls **Maintain Schedule** when course times must be
  re-checked and persisted (steps 34 – 40).

This satisfies the UML rule that *include* fragments are referenced from
the base use case and execute on every invocation when the condition
holds.

---

## 2. Why the diagram is UML-correct

| UML requirement | How it is satisfied |
|-----------------|---------------------|
| **Objects & lifelines** | 12 lifelines (1 actor + 11 objects). Every participant has a dashed lifeline, activation bars marking periods of focus, and a clear head box. |
| **Time ordering** | Messages are numbered 1 → 42 top-to-bottom; each step is reachable from the previous one. |
| **Messages & returns** | Solid arrows with filled triangle heads = synchronous calls (e.g. `login()`). Dashed arrows with open heads = return values (e.g. `loginResult(success)`). |
| **Self-messages** | `validateCredentials()`, `validateCourseInfo()`, and `checkTimeConflict()` are shown as self-arrows that exit right and loop back, indicating intra-object logic. |
| **Stereotypes** | Each object is labelled with its UML stereotype in `<<guillemets>>`: actor, boundary, control, entity — the standard GRASP/Bruce-Douglass classification for OO systems. |
| **Activation bars** | White rectangles on lifelines show when an object is processing. They grow *rightward* (longer = deeper nesting) so the visual depth matches the call depth. |
| **Encapsulation** | The Presentation Tier never speaks to the Data Tier directly — every call passes through an Application-Tier controller/service. |

---

## 3. Why the diagram follows N-Tier Architecture

N-Tier architecture mandates that an upper tier never bypasses a lower
tier to talk to the one below it. The diagram is laid out in three
horizontal bands, and *every* arrow obeys the band boundaries:

```
┌───────────────────────────────────────────────────────────────┐
│ PRESENTATION TIER                                             │
│   Registrar ─ RegistrarPortal ─ CurriculumUI                  │
└─────────────────────┬─────────────────────────────────────────┘
                      │ (only downward calls)
┌─────────────────────▼─────────────────────────────────────────┐
│ APPLICATION TIER                                              │
│   CurriculumController → AuthService / CurriculumService /    │
│                         CourseService / ScheduleService       │
└─────────────────────┬─────────────────────────────────────────┘
                      │ (only downward calls)
┌─────────────────────▼─────────────────────────────────────────┐
│ DATA TIER                                                     │
│   CurriculumRepository / CourseRepository /                   │
│   ScheduleRepository ─ Database                               │
└───────────────────────────────────────────────────────────────┘
```

Concrete examples from the diagram:

- Step **4** (`UI → CT`): the boundary `CurriculumUI` calls the
  controller — *never* the service or repository directly.
- Step **12** (`CT → CS`): the controller delegates business logic to
  the service — services do not call other services except when one
  needs another's capability (e.g. `CT → CRS` and `CT → SS` for the
  include flows).
- Steps **14 / 24 / 31 / 37** (`Repository → Database`): the repository
  is the **only** object allowed to issue SQL. The Database lifeline
  never replies to anything except a repository — services and
  controllers stay one tier away from the storage engine.
- Return messages always travel back up the same tier they came from
  on (e.g. step **7** `AS → CT` returns through the Application Tier
  only).

This guarantees the **separation-of-concerns** property of N-Tier
systems: presentation logic (validation, formatting, screen flow) is
isolated from business logic (registration rules, conflict checks),
which is itself isolated from persistence logic (SQL, transactions).

---

## 4. Why the diagram is appropriate for SE322

- **Complete coverage** of one main use case + three includes — matches
  the assignment brief.
- **42 numbered messages** — detailed enough to demonstrate
  understanding, but each message is a single line of business English
  (no parameter explosions).
- **Three output formats** are provided:
  1. `Maintain_Curriculum_Sequence_Diagram.drawio` — draw.io native
     file (import directly into app.diagrams.net or the desktop
     client; PNG export at 1423 × 1933 px ready to drop into a Word
     report).
  2. `maintain_curriculum_sequence.puml` — PlantUML, ideal for
     version-controlled documentation.
  3. `maintain_curriculum_mermaid.md` — Mermaid block that renders
     inline on GitHub, GitLab, and most Markdown previews.
- **Visual conventions** match the SE322 marking guide:
  pure black-and-white (no coloured fills), `Helvetica` typography,
  consistent 14 px lifeline spacing, and right-margin N-Tier
  brackets so a reader can immediately see which tier each lifeline
  belongs to.

---

## 5. Files

| File | Purpose |
|------|---------|
| `Maintain_Curriculum_Sequence_Diagram.drawio` | draw.io source — importable directly |
| `generate_maintain_curriculum.py` | Python generator that built the `.drawio` file |
| `maintain_curriculum_sequence.puml` | PlantUML equivalent |
| `maintain_curriculum_mermaid.md` | Mermaid equivalent (renders on GitHub) |
| `maintain_curriculum_explanation.md` | This document |

To regenerate the draw.io file from the Python script:

```bash
cd /Users/ury/Documents/se322
python3 generate_maintain_curriculum.py
```