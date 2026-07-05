# English Explanation: Why the "Register for Courses" Sequence Diagram Follows N-Tier Architecture

## N-Tier Architecture Overview

The sequence diagram for the **Register for Courses** use case follows the **N-Tier (3-Tier plus External System) architecture** taught in SE322. This architecture separates the system into distinct layers, each with a specific responsibility. Communication flows strictly from one tier to the next — the Presentation Tier never directly accesses the Data Tier, and each tier communicates only with its immediate neighbor.

## Tier Breakdown

### 1. Presentation Tier (Student + RegistrationUI)
The Presentation Tier is responsible for user interaction and visual display only. It contains **no business logic**.

- **Student (Actor):** Represents the end-user who triggers use cases.
- **RegistrationUI (Boundary):** The user interface that displays forms, course lists, and confirmation messages. It captures input (Steps 1, 6, 14) and renders output (Steps 5, 13, 31). It never makes decisions about whether a registration is valid — it simply forwards the request.

**Evidence in the diagram:** Messages 1-2, 5-7, 12-15, 30-31 all involve the Presentation Tier. Notice that RegistrationUI never speaks directly to a Repository or Database — it always delegates to the Controller.

### 2. Application Tier (RegistrationController + RegistrationService + BillingService)
The Application Tier contains **all business logic and orchestration**. This is where rules are validated, decisions are made, and workflows are coordinated.

**RegistrationController (Control):** Acts as a facade/mediator between the UI and the services. It receives requests from the UI, delegates to the appropriate service, and returns results. It does not contain domain-specific business rules — it orchestrates.

- Messages 2-4: Handles authentication flow
- Messages 7, 12: Coordinates course catalog display
- Messages 15, 29-30: Mediates registration requests

**RegistrationService (Control):** Contains the core business logic for the registration use case. This is where:
- The system checks if a course exists (Step 17)
- The system checks for scheduling conflicts (Step 19)
- The system verifies course capacity (Step 21)
- The system persists the registration (Step 23)
- The system initiates billing (Step 25)

**BillingService (Control):** Translates registration events into billing requests. It abstracts the external BillingSystem so that RegistrationService does not need to know the details of the external API.

**Evidence in the diagram:** Steps 8-11, 16-29 all involve the Application Tier. The business logic (conflict checking, capacity checking, invoice generation) is concentrated here, never in the UI or the database.

### 3. Data Tier (CourseRepository + RegistrationRepository)
The Data Tier is responsible for **data persistence and retrieval only**. It contains no business logic.

- **CourseRepository (Entity):** Retrieves course data from the database. Used for browsing courses (Step 9), checking existence (Step 17), and capacity checking (Step 21).
- **RegistrationRepository (Entity):** Manages registration records. Used for conflict checking (Step 19) and saving new registrations (Step 23).

**Evidence in the diagram:** Steps 9-10, 17-18, 19-20, 21-22, 23-24 all involve the Data Tier. These are simple create/read/check operations — no business decisions are made here.

### 4. External System (BillingSystem)
External systems are systems outside our control that we integrate with. They are treated as a separate tier because they have their own architecture and constraints.

- **BillingSystem (External Actor):** An external financial system that handles invoice creation. The BillingService communicates with it through a service boundary.

**Evidence in the diagram:** Steps 26-27 show the interaction with BillingSystem. The dashed return arrow indicates that the system waits for confirmation from the external system before proceeding.

## Key N-Tier Properties Demonstrated

### A. Strict Layering
Messages flow strictly downward (call) and upward (return):
- Presentation → Application → Data
- No skipping: Presentation never calls Data directly
- No reverse flow: Data never calls Application without being asked

### B. Separation of Concerns
- **Presentation:** All rendering, no decisions
- **Application:** All decisions, no rendering or storage
- **Data:** All storage, no decisions

### C. Reusability
- The same RegistrationService could serve a different UI (mobile app, admin portal) without modification
- The same CourseRepository could serve different services

### D. Maintainability
- If the billing rules change, only BillingService is modified
- If the database changes, only the repositories are affected
- If the UI framework changes, only RegistrationUI is affected

## Conclusion

This sequence diagram strictly follows the N-Tier architecture pattern taught in SE322. Each message can be traced to the correct tier, and business logic is properly isolated in the Application Tier. The diagram clearly demonstrates that the Student only interacts with the Presentation Tier, business rules live in the Application Tier, data storage is handled by the Data Tier, and external integrations are isolated through service boundaries.
