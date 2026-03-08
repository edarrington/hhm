# HHM Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   USER INTERFACE LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  • Web Frontend (React + WebRTC + Chat)                     │
│  • iOS App (Swift + SwiftUI)                                │
│  • Android App (Kotlin + Jetpack Compose)                   │
│  • Multi-user household authentication                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND SERVICE LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  • Voice Service (Python + FastAPI + WebRTC)                │
│  • REST API (Household endpoints)                           │
│  • Skill Orchestration (Plugin system)                      │
│  • Hosting: Azure Container Apps or AWS ECS                │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────────────┐
         ▼             ▼                     ▼
    ┌─────────┐  ┌──────────┐       ┌─────────────┐
    │  Azure  │  │ Memory   │       │Integration  │
    │ OpenAI  │  │ Service  │       │ Adapters    │
    │ / Gemini│  │(Redis)   │       │(Gmail/Todoist)
    └─────────┘  └──────────┘       └─────────────┘
        (LLM)      (Vector DB)        (APIs)
```

## Component Details

### 1. Voice Service
- WebRTC peer connection handling
- Real-time audio streaming
- Household context injection
- Multi-user session management

### 2. REST API
- `/api/auth/` - Authentication endpoints
- `/api/household/` - Household data
- `/api/tasks/` - Todoist integration
- `/api/calendar/` - Google Calendar
- `/api/email/` - Gmail operations
- `/api/drive/` - Google Drive
- `/api/memory/` - Household memory

### 3. Skills System
Each integration is a pluggable skill:
- **CalendarSkill** - Google Calendar operations
- **GmailSkill** - Email management
- **DriveSkill** - Document management
- **TodoistSkill** - Task management
- **MemorySkill** - Fact extraction and retrieval

### 4. Memory System
- Household-level memory storage
- Vector search (Redis Stack)
- Automatic fact extraction
- Types:
  - Family relationships
  - Task patterns
  - Schedule habits
  - Preferences
  - Important dates

### 5. Authentication
- Household ID + User ID model
- Multi-user support
- OAuth for Google integrations
- Todoist API token management

## Data Flow

```
1. User Input
   ├─ Voice (WebRTC) or Text (REST)
   
2. Authentication & Context
   ├─ Validate household + user
   ├─ Retrieve household memory
   
3. Intent Recognition
   ├─ LLM determines action
   ├─ Selects appropriate skill(s)
   
4. Skill Execution
   ├─ Gmail: Read/send emails
   ├─ Calendar: Manage events
   ├─ Drive: Handle documents
   ├─ Todoist: Manage tasks
   
5. Memory Update
   ├─ Extract facts from interaction
   ├─ Store in Redis
   ├─ Update household memory
   
6. Response
   ├─ Generate response text
   ├─ Stream to user (voice or text)
```

## Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend | Python + FastAPI | Async-first, excellent AI/ML integration |
| Voice | Azure OpenAI Realtime API | Low-latency, high quality |
| Memory | Redis Stack | Vector search + persistence |
| Database | PostgreSQL | Relational data, reliability |
| Web | React + TypeScript | Modern UI, strong ecosystem |
| iOS | Swift + SwiftUI | Native performance, modern framework |
| Android | Kotlin + Compose | Modern language, Compose maturity |
| Cloud | Azure or AWS | Managed services, scalability |
| CI/CD | GitHub Actions | Native GitHub integration |

## Database Schema

### Tables
- `households` - Household records
- `household_members` - User mappings
- `integrations` - OAuth tokens (encrypted)
- `conversations` - Chat history
- `memories` - Household facts/events
- `tasks` - Synced Todoist tasks
- `calendar_events` - Synced calendar events
- `audit_log` - Operation tracking

## Security Considerations

1. **Authentication**
   - Household-level auth
   - Multi-user support
   - Session management

2. **Data Access**
   - Household-scoped queries
   - User identity tracking
   - OAuth token encryption

3. **Privacy**
   - GDPR/CCPA compliance
   - Audit logging
   - Data retention policies

## Deployment

### Development
```bash
docker-compose up
```

### Production
- Azure Container Apps or AWS ECS
- Cloud databases (Azure DB / RDS)
- CDN for frontend
- Rate limiting and quotas
- Monitoring and alerting

## Scalability

- Stateless service design (horizontal scaling)
- Redis for distributed memory
- PostgreSQL read replicas
- API rate limiting
- Message queues for async tasks (future)
