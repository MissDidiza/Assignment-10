# Assignment-10
# 🎒 CampusFind — Smart Lost & Found System

> A web-based platform that helps university students and staff report, search, and reclaim lost items using AI-assisted matching and real-time notifications.

---

## Project Description

CampusFind is a **Smart Campus Lost & Found System** designed to replace the inefficient paper-based and bulletin-board approaches that most universities still rely on. Students who lose items (phones, ID cards, bags, keys, laptops) can log a report in seconds. Staff who find items can upload a photo and description. The system's AI matching engine then compares lost and found reports automatically — notifying potential matches in real time.

Once completed, the system will provide:

- A **web portal** for students and staff to submit lost/found reports with photos
- An **AI-powered matching engine** that compares descriptions and images to surface probable matches
- **Real-time email and in-app notifications** when a match is detected
- An **admin dashboard** for campus security/admin staff to manage item handover workflows
- A **statistics and audit trail** so the institution can track recovery rates

---

## 📁 Repository Structure

### Assignment 3 — System Specification & Architecture
| File | Description |
|---|---|
| [SPECIFICATION.md](./SPECIFICATION.md) | Full system specification — domain, problem statement, scope, functional & non-functional requirements, user stories |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | C4 architectural diagrams — System Context, Container, Component, and Code level diagrams |

### Assignment 4 — Stakeholder & System Requirements Documentation
| File | Description |
|---|---|
| [STAKEHOLDERS.md](./STAKEHOLDERS.md) | Stakeholder analysis — 7 stakeholders with roles, concerns, pain points, and success metrics |
| [REQUIREMENTS.md](./REQUIREMENTS.md) | System Requirements Document — 12 functional requirements and 13 non-functional requirements with acceptance criteria and traceability matrix |
| [REFLECTION.md](./REFLECTION.md) | Reflection on challenges faced in balancing competing stakeholder needs |

### Assignment 5 — Use Case Modeling and Test Case Development
| File | Description |
|---|---|
| [USE_CASES.md](./USE_CASES.md) | Use case diagram (Mermaid), actor explanations, and 8 detailed use case specifications with basic and alternative flows |
| [TEST_CASES.md](./TEST_CASES.md) | 15 functional test cases and 3 non-functional test cases (performance, security, scalability) in table format |
| [REFLECTION_A5.md](./REFLECTION_A5.md) | Reflection on challenges in translating requirements into use cases and test cases |

---

## 👤 Author

**[Your Name]**
Student Number: [Your Student Number]
Course: Software Engineering
Submitted: March 2026

### Assignment 6 — Agile User Stories, Backlog, and Sprint Planning
| File | Description |
|---|---|
| [AGILE_PLANNING.md](./AGILE_PLANNING.md) | 14 user stories with acceptance criteria, MoSCoW prioritised product backlog with story point estimates, and full Sprint 1 plan with 20 task breakdowns |
| [REFLECTION_A6.md](./REFLECTION_A6.md) | Reflection on challenges of Agile planning as a solo developer — prioritisation, estimation, sprint scope, and traceability |

### Assignment 7 — GitHub Project Templates and Kanban Board
| File | Description |
|---|---|
| [template_analysis.md](./template_analysis.md) | Comparison table of 4 GitHub project templates, chosen template justification, and custom column design |
| [kanban_explanation.md](./kanban_explanation.md) | Definition of Kanban, explanation of how the CampusFind board visualises workflow, limits WIP, and supports Agile principles |
| [REFLECTION_A7.md](./REFLECTION_A7.md) | Reflection on template selection challenges and comparison of GitHub Projects vs Trello vs Jira |

#### Kanban Board Column Structure
| Backlog | To Do | In Progress | Testing | Blocked | Done |
|---|---|---|---|---|---|
| Future sprint stories | Sprint 1 tasks (WIP: 6) | Active work (WIP: 3) | Awaiting verification (WIP: 3) | Cannot proceed | Verified and deployed |

### Assignment 8 — Object State Modeling and Activity Workflow Modeling
| File | Description |
|---|---|
| [STATE_DIAGRAMS.md](./STATE_DIAGRAMS.md) | State transition diagrams for 8 critical system objects: User Account, Lost Report, Found Report, AI Match Record, Handover Record, Notification, JWT Session, and Item Photo — each with Mermaid diagram and full explanation |
| [ACTIVITY_DIAGRAMS.md](./ACTIVITY_DIAGRAMS.md) | Activity workflow diagrams for 8 complex system workflows with swimlanes, decision nodes, and parallel actions — including full traceability table to requirements and user stories |
| [REFLECTION_A8.md](./REFLECTION_A8.md) | Reflection on state granularity, parallel action modeling, aligning UML with Agile stories, and the difference between state diagrams and activity diagrams |

### Assignment 9 — Domain Modeling and Class Diagram Development
| File | Description |
|---|---|
| [DOMAIN_MODEL.md](./DOMAIN_MODEL.md) | Domain model for 7 key entities (User, Report, Photo, MatchRecord, Handover, Notification, Session) with attributes, methods, relationships, and business rules |
| [CLASS_DIAGRAM.md](./CLASS_DIAGRAM.md) | Full Mermaid.js class diagram with 7 domain classes, 7 service classes, 9 enumerations, multiplicity, composition, association, and dependency relationships — plus design decision explanations and traceability table |
| [REFLECTION_A9.md](./REFLECTION_A9.md) | Reflection covering abstraction challenges, relationship type decisions, alignment with Assignments 4, 5, and 8, trade-offs made, and OO design lessons learned |

### Assignment 10 — From Class Diagrams to Code with Creational Patterns

**Language:** Python 3.11
**Why Python:** Rich ecosystem for AI/ML libraries (sentence-transformers, TensorFlow) used in the AI Matching Service. Clear, readable syntax that maps closely to UML class diagrams. Excellent testing support via pytest.

#### Directory Structure
```
/src                        # Domain entity class implementations
  enums.py                  # All enumeration types
  user.py                   # User entity
  report.py                 # Report entity
  photo.py                  # Photo entity
  match_record.py           # MatchRecord entity
  handover.py               # Handover entity
  notification.py           # Notification entity

/creational_patterns        # All 6 creational design patterns
  simple_factory.py         # NotificationFactory
  factory_method.py         # LostReportCreator / FoundReportCreator
  abstract_factory.py       # ProductionServiceFactory / TestingServiceFactory
  builder.py                # ReportBuilder + ReportDirector
  prototype.py              # ReportPrototypeCache + CloneableReport
  singleton.py              # MatchingConfig + DatabaseConnectionPool

/tests                      # Unit tests
  test_classes.py           # Tests for all domain entity classes
  test_creational_patterns.py  # Tests for all 6 patterns
```

#### Creational Pattern Rationale
| Pattern | CampusFind Use Case | Justification |
|---|---|---|
| Simple Factory | `NotificationFactory` creates all notification types | Centralises 6 notification types behind one interface — callers don't need to know construction details |
| Factory Method | `LostReportCreator` / `FoundReportCreator` | Lost and Found reports have different post-submission behaviour; Factory Method delegates creation to the right subclass |
| Abstract Factory | `ProductionServiceFactory` / `TestingServiceFactory` | Swapping email (SendGrid→Mock) and storage (Cloudinary→Local) for testing requires changing only one factory |
| Builder | `ReportBuilder` + `ReportDirector` | Report has 7 required fields and optional photos; Builder prevents incomplete objects and makes construction readable |
| Prototype | `ReportPrototypeCache` | Admin and test environments need many similar reports; cloning pre-configured templates avoids redundant validation |
| Singleton | `MatchingConfig` + `DatabaseConnectionPool` | AI matching threshold must be globally consistent; DB connections must not be duplicated |

#### Running Tests
```bash
pip install pytest
pytest tests/ -v
```

| File | Description |
|---|---|
| [src/](./src/) | Python implementation of all 7 domain entity classes from Assignment 9 |
| [creational_patterns/](./creational_patterns/) | All 6 creational design pattern implementations |
| [tests/](./tests/) | Unit tests for domain classes and all creational patterns |
| [CHANGELOG.md](./CHANGELOG.md) | Full changelog tracking all assignment progress |
