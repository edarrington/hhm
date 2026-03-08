# HHM - Happy Household Manager

An AI-powered household management assistant built on Cogneon's architecture. HHM is a warm, friendly companion that manages household operations through voice and text interfaces, with persistent memory that learns family dynamics and preferences.

## 🎯 Core Features

- **Voice + Text Interaction** - Communicate naturally via voice or chat
- **Household Management** - Centralized hub for family coordination
- **Smart Integrations**:
  - 📧 Google Gmail (read/write)
  - 📅 Google Calendar (create/manage events)
  - 📄 Google Drive (document management)
  - ✅ Todoist (task management)
- **Persistent Memory** - Learns family relationships, preferences, and patterns
- **Multi-User** - Shared household access for all family members
- **Multi-Platform** - Web, iOS, and Android

## 📋 Project Structure

```
hhm/
├── docs/              # Project documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── USER_GUIDE.md
├── backend/           # Python FastAPI backend
│   ├── src/
│   │   ├── api/       # REST API endpoints
│   │   ├── voice/     # Voice service
│   │   ├── skills/    # Plugin system
│   │   ├── integrations/  # Google APIs, Todoist
│   │   └── memory/    # Household memory system
│   ├── tests/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/          # React web app
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── ios/               # Swift/SwiftUI app
│   └── HHM.xcodeproj
├── android/           # Kotlin/Compose app
│   └── build.gradle
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hhm.git
   cd hhm
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Install dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

5. **Run development servers**
   ```bash
   # Backend (from backend directory)
   python -m src.voice.server
   
   # Frontend (from frontend directory)
   npm start
   ```

## 🏗️ Architecture

HHM is built on Cogneon's proven architecture with household-specific enhancements:

- **Backend**: FastAPI + Python for voice service and APIs
- **Voice**: Azure OpenAI Realtime API for natural conversation
- **Memory**: Redis Stack for household context and learning
- **Database**: PostgreSQL for persistent state
- **Frontend**: React for web, SwiftUI for iOS, Jetpack Compose for Android

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [User Guide](docs/USER_GUIDE.md)

## 🔐 Security & Privacy

- Household-level authentication
- OAuth 2.0 for Google integrations
- Encrypted data in transit and at rest
- Audit logging for all operations
- User consent for integrations

## 📊 Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Backend infrastructure
- Household authentication
- Memory system setup

### Phase 2: Integrations (Weeks 3-5)
- Gmail, Calendar, Drive, Todoist skills
- Memory extraction

### Phase 3: Voice (Weeks 6-8)
- Voice service
- Text chat API

### Phase 4: Web (Weeks 9-11)
- React web application
- Voice + text UI

### Phase 5: Mobile (Weeks 12-16)
- iOS app
- Android app

### Phase 6-7: Polish & Deploy (Weeks 17-20)
- Advanced memory features
- Production deployment

## 🤝 Contributing

[Contributing guidelines to be added]

## 📄 License

[License to be determined]

## 🙋 Support

For issues or questions, please open a GitHub issue.

---

**Built with ❤️ using Cogneon's architecture**

Based on: [Cogneon/Eon](https://github.com/vyente-ruffin/cogneon)
