# 🚀 AI-Powered Quiz API

A production-ready REST API for dynamic AI-powered quiz generation, robust attempt tracking, automated scoring, and detailed analytics. Built with **Django**, **Django REST Framework (DRF)**, and **PostgreSQL**.

---

## 📋 Table of Contents

- [Introduction](#introduction)
- [Local Setup Instructions](#local-setup-instructions)
- [Database Schema & Model Relationships](#database-schema--model-relationships)
- [API Endpoint Overview](#api-endpoint-overview)
- [Design Decisions & Trade-offs](#design-decisions--trade-offs)
- [Handling AI Integration](#handling-ai-integration)
- [Challenges Faced & Solutions](#challenges-faced--solutions)
- [Testing Approach](#testing-approach)

---

## 🛠 Introduction

This API provides the foundation for an interactive educational quiz platform. It allows users to register, authenticate securely via JWT, and generate real-time multiple-choice quizzes on any topic using Google's **Gemini AI** model via the backend. The API handles enforcing attempts, recording individual answers, preventing score tampering, and generating performance analytics.

---

## ⚡ Local Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL Server running (`localhost:5432`)

### 1. Clone & Setup Virtual Environment
```bash
# Clone the repository
cd quiz_api
python -m venv venv

# Activate venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration (PostgreSQL)
Ensure your PostgreSQL server is running. Open your `psql` shell or pgAdmin to create the database:
```sql
CREATE DATABASE quiz_db;
```

### 4. Configure Environment Variables
Create a `.env` file in the root `quiz_api` directory:
```env
# Django
DJANGO_SECRET_KEY=your-secure-secret-key-here
DEBUG=True

# Database Connections
DB_NAME=quiz_db
DB_USER=postgres
DB_PASSWORD=admin         # Change this to your local postgres password 
DB_HOST=localhost
DB_PORT=5432

# External Integrations
GEMINI_KEY=your_gemini_api_key_here
```

### 5. Run Migrations & Start Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional, to access the Django Admin
python manage.py runserver
```

**Visit:** `http://localhost:8000/swagger/` for the interactive API Swagger documentation.

---

## 🗄 Database Schema & Model Relationships

The API leverages a highly relational schema mapped to PostgreSQL.

```
┌──────────┐       ┌──────────┐       ┌────────────┐
│   User   │──1:N──│   Quiz   │──1:N──│  Question  │
│──────────│       │──────────│       │────────────│
│ id       │       │ id       │       │ id         │
│ username │       │ title    │       │ quiz_id FK │
│ email    │       │ topic    │       │ text       │
│ password │       │ difficulty│      │ options [] │ (JSONField)
│ role     │       │ created_by│      │ correct_ans│
│ created_at│      │ created_at│      │ explanation│
└──────────┘       └──────────┘       └────────────┘
      │                  │
      │   ┌──────────┐   │
      └─N─│ Attempt  │─N─┘
          │──────────│
          │ id       │──1:N──┌──────────┐
          │ user_id  │       │  Answer  │
          │ quiz_id  │       │──────────│
          │ score    │       │ id       │
          │ status   │       │ attempt  │
          │ started  │       │ question │
          │ completed│       │ selected │
          └──────────┘       │ is_correct│
                             └──────────┘
```

- **User**: Custom `AbstractUser` mapped to `USER` and `ADMIN` roles.
- **Quiz ↔ Question**: 1-to-Many relational structure characterizing generated assessments.
- **User ↔ Attempt ↔ Answer**: Represents the stateful process of taking a quiz. The Attempt encapsulates aggregate data (score, finalized status), while Answer tracks granular question responses.

---

## 🔗 API Endpoint Overview

### Authentication (`apps.users`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register standard or admin user | ❌ |
| POST | `/api/auth/login/` | Receive JWT access/refresh tokens | ❌ |
| GET | `/api/auth/profile/` | Fetch current logged-in user profile | ✅ |

### Quiz Management (`apps.quizzes`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|------|
| GET | `/api/quizzes/` | Query paginated list of quizzes | ✅ |
| POST | `/api/quizzes/generate/` | Generate quiz dynamically via Gemini AI | ✅ |
| GET | `/api/quizzes/{id}/` | Get specific quiz data alongside all questions | ✅ |

### Attempts & Scoring (`apps.attempts`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|------|
| POST | `/api/attempts/start/` | Begin tracking a new attempt for a quiz | ✅ |
| POST | `/api/attempts/{id}/answer/` | Lock-in a specific question's answer | ✅ |
| POST | `/api/attempts/{id}/submit/` | Finalize attempt. Calculate real-time score. | ✅ |
| GET | `/api/attempts/history/` | View historical attempts of current user | ✅ |

### Analytics (`apps.analytics`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|------|
| GET | `/api/analytics/overview/` | Total attempts, aggregations, average accuracy | ✅ |
| GET | `/api/analytics/topic/` | Performance aggregated dynamically per topic | ✅ |

---

## 🧠 Design Decisions & Trade-offs

1. **Monolithic Modularity using Django Apps**
   - **Decision:** The API is structured into highly independent domains (`users`, `quizzes`, `ai_integration`, `attempts`, `analytics`).
   - **Rationale / Trade-off:** Opted for a modular monolith. It grants exceptional separation of concerns—easier testing and robust code—without incurring the infrastructural overhead (DevOps and network latency) required by a full microservices architecture. It's the perfect sweet spot for an evolving product.
   
2. **PostgreSQL JSONField vs Native 'Options' Model**
   - **Decision:** Questions leverage PostgreSQL's `JSONField` to store multiple-choice `options`. 
   - **Rationale / Trade-off:** By storing an array of strings in a single column instead of building a separate `Option` SQL table (1:M to Questions), database lookup query times are vastly improved. The trade-off is slightly less strict relational validation inside the database layer, which I mitigated by enforcing schema validation inside the DRF serializers.

3. **Synchronous Real-Time Scoring**
   - **Decision:** Scores are calculated instantaneously during the `POST /api/attempts/{id}/submit/` request using atomic ORM aggregations.
   - **Rationale / Trade-off:** While massive enterprise systems might delegate scoring to background tasks (e.g., Celery/Redis), that would be premature over-engineering here. It would also degrade real-time UX. Score tracking in this context is lightweight (aggregating a boolean `is_correct` field).

---

## 🤖 Handling AI Integration

To reliably support Generative AI for unpredictable educational topics, I built the AI subsystem using a **Strategy Pattern Boundary**:

1. **Extensible Architecture:** The `GeminiProvider` natively encapsulates Google's `gemini-2.5-flash` model via HTTP requests, but the `ai_integration/providers.py` interface is built to seamlessly plug in OpenAI, Claude, or DeepSeek if requirements shift.
2. **Prompt Engineering for Structured JSON:** The `gemini-2.5-flash` endpoint is natively instructed (`application/json`) to return a strict array of object schemas (`question_text`, `options`, `correct_answer`, `explanation`). This prevents hallucinated formatting that breaks parsing code.
3. **The Mock Fallback Mechanism:** Rate limits (`HTTP 429`) or vendor outages inevitably happen. I baked in exponential backoff retry loops. If the real AI is exhausted, the system automatically degrades to a **`MockProvider`** that seamlessly returns deterministic template-based questions. *Because of this, the API endpoint is guaranteed to never break for end-users, even if the API Key expires.*

---

## 🚧 Challenges Faced & Solutions

1. **Standardizing API Exceptions:** 
   - **Challenge:** Unhandled logic errors or generic Django `404/500` failures often returned ugly HTML payloads, which breaks client JSON parsers in REST architectures.
   - **Solution:** I implemented a custom global Exception handler in DRF (`utils.exceptions.custom_exception_handler`). It gracefully intercepts errors, formatting them identically (`{ "error": "Internal Server Error", "details": ... }`), prioritizing a stable frontend integration.

2. **Atomic Integrity When Attempting Quizzes:**
   - **Challenge:** Tech-savvy users could theoretically submit multiple `POST` requests rapidly to inflate their score, or answer the same question multiple times.
   - **Solution:** I implemented strict State Machine validation. An attempt begins in `in_progress`. Once the user hits `/submit/`, the status transitions to `completed`. The `record_answer` service enforces database-level uniqueness across `(attempt_id, question_id)` and hard-rejects updates on finalized attempts (`HTTP 400`).

3. **Handling ORM Property Collisions:**
   - **Challenge:** Adding `.annotate(question_count=Count('questions'))` optimization strictly against QuerySets collided with an existing `@property def question_count()` on the `Quiz` model.
   - **Solution:** Promptly deleted the `@property` from Python space to prioritize native SQL aggregation mechanisms, pushing the load efficiently into PostgreSQL rather than executing O(N) queries during Python object instantiation.

---

## 🧪 Testing Approach

A robust testing cycle handles verification of core mechanics and edge-cases:

- Executable via: `python manage.py test apps --verbosity=2`
- **Unit Testing Business Logic**: Extensive testing validates custom scoring mechanisms, Attempt constraints, and JWT Authentication flows.
- **API Simulation:** Simulated DRF HTTP clients natively post answers to the API and evaluate HTTP Status Codes protecting against unauthorized modifications.
- **AI Mock Resilience:** Designed assertions to simulate what happens when AI endpoints return 500s or hit 429 Rate Limits, verifying the system effectively degrades to the fallback `MockProvider`.

*A total of 31 test cases currently pass indicating 100% confidence in the system's foundational core.*
