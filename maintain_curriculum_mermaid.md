# Maintain Curriculum — Sequence Diagram (Mermaid)

> **Use Case:** Maintain Curriculum (main)  
> **Includes:** Logon Validation, Create Course, Maintain Schedule  
> **Architecture:** N-Tier (Presentation → Application → Data)

```mermaid
sequenceDiagram
    autonumber
    title Maintain Curriculum — N-Tier Sequence Diagram (SE322)

    actor R as Registrar
    participant RP as RegistrarPortal<br/>«boundary»
    participant UI as CurriculumUI<br/>«boundary»
    participant CT as CurriculumController<br/>«control»
    participant AS as AuthService<br/>«control»
    participant CS as CurriculumService<br/>«control»
    participant CRS as CourseService<br/>«control»
    participant SS as ScheduleService<br/>«control»
    participant CR as CurriculumRepository<br/>«entity»
    participant CRR as CourseRepository<br/>«entity»
    participant SR as ScheduleRepository<br/>«entity»
    participant DB as Database

    Note over R,DB: ── Logon Validation (include) ──
    R->>RP: 1: openPortal()
    RP-->>R: 2: requestLogin()
    R->>UI: 3: enterCredentials(id, password)
    UI->>CT: 4: login(id, password)
    CT->>AS: 5: validate(id, password)
    AS->>AS: 6: validateCredentials()
    AS-->>CT: 7: loginResult(success)
    CT-->>UI: 8: loginStatus(success)
    UI-->>R: 9: showDashboard()

    Note over R,DB: ── Maintain Curriculum (main) ──
    R->>UI: 10: selectMaintainCurriculum()
    UI->>CT: 11: maintainCurriculum()
    CT->>CS: 12: getCurriculum()
    CS->>CR: 13: findAll()
    CR->>DB: 14: SELECT * FROM curriculum
    DB-->>CR: 15: curriculumData
    CR-->>CS: 16: curriculums
    CS-->>CT: 17: curriculumList
    CT-->>UI: 18: displayCurriculum(curriculums)
    UI-->>R: 19: showCurriculumForm()
    R->>UI: 20: updateCurriculum(info)
    UI->>CT: 21: updateCurriculum(info)
    CT->>CS: 22: saveCurriculum(info)
    CS->>CR: 23: save(curriculum)
    CR->>DB: 24: INSERT INTO curriculum
    DB-->>CR: 25: saved
    CR-->>CS: 26: savedCurriculum
    CS-->>CT: 27: saveResult(success)

    Note over R,DB: ── Create Course (include) ──
    CT->>CRS: 28: createCourse(courseInfo)
    CRS->>CRS: 29: validateCourseInfo()
    CRS->>CRR: 30: save(course)
    CRR->>DB: 31: INSERT INTO course
    DB-->>CRR: 32: saved
    CRR-->>CRS: 33: savedCourse

    Note over R,DB: ── Maintain Schedule (include) ──
    CT->>SS: 34: maintainSchedule(scheduleInfo)
    SS->>SS: 35: checkTimeConflict()
    SS->>SR: 36: save(schedule)
    SR->>DB: 37: INSERT INTO schedule
    DB-->>SR: 38: saved
    SR-->>SS: 39: savedSchedule
    SS-->>CT: 40: scheduleResult(success)

    CT-->>UI: 41: showConfirmation(success)
    UI-->>R: 42: maintainCurriculumSuccess()
```

## Reading guide
- Solid arrows `->>` are method **calls**.
- Dashed arrows `-->>` are **return** values.
- Self-arrows (`AS->>AS`, `CRS->>CRS`, `SS->>SS`) represent internal
  validation/conflict-check logic that doesn't cross a tier boundary.
- The four `Note over` rows mark the **Logon Validation** (include),
  **Maintain Curriculum** (main), **Create Course** (include), and
  **Maintain Schedule** (include) phases.
- Tier order across the top: **Presentation → Application → Data**.