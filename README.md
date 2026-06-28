# ZeroTrust Hub — AI Cybersecurity Dashboard

Enterprise-grade, AI-powered Security Operations Center (SOC) dashboard for monitoring cyber threats, scanning vulnerabilities, analyzing malware, and providing intelligent security recommendations.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React 19)                      │
│         Vite · Tailwind CSS · Framer Motion · Axios          │
├─────────────────────────────────────────────────────────────┤
│                        API (REST/WS)                         │
├─────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI/Python)                   │
│     SQLAlchemy · Celery · Redis · JWT · WebSockets           │
├─────────────────────────────────────────────────────────────┤
│                     PostgreSQL Database                       │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** with custom dark cyberpunk theme
- **Framer Motion** for animations
- **React Router** for navigation
- **TanStack Query** for data fetching
- **Zustand** for state management
- **Zod** for validation
- **Lucide Icons** for UI icons
- **Recharts** for data visualization

### Backend
- **FastAPI** (Python 3.12)
- **SQLAlchemy** ORM
- **Alembic** for migrations
- **JWT** authentication with refresh tokens
- **Passlib + bcrypt** for password hashing
- **Celery + Redis** for task queuing
- **WebSockets** for real-time notifications
- **OpenAI/Gemini** AI integration

### Database
- **PostgreSQL** with 15 normalized tables

### DevOps
- **Docker** + Docker Compose
- **Nginx** reverse proxy
- **GitHub Actions** CI/CD

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### 1. Clone & Setup

```bash
git clone <repo-url>
cd zerotrust-hub

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env

# Frontend
cd ../frontend
npm install
```

### 2. Configure Environment

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/zerotrust
SECRET_KEY=your-very-long-secret-key
OPENAI_API_KEY=sk-...       # Optional: AI features
NVD_API_KEY=...              # Optional: CVE sync
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start Development

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

The app will be available at `http://localhost:5173`.

### Docker Deployment

```bash
docker-compose up -d
```

Access the app at `http://localhost`.

---

## Default Credentials

| Role     | Email                  | Password    |
|----------|------------------------|-------------|
| Admin    | admin@zerotrust.com    | Admin123!   |
| Analyst  | analyst@zerotrust.com  | Analyst123! |
| Viewer   | viewer@zerotrust.com   | Viewer123!  |

---

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

| Prefix               | Description              |
|----------------------|--------------------------|
| `/api/auth`          | Authentication & tokens  |
| `/api/users`         | User management (admin)  |
| `/api/dashboard`     | Dashboard statistics     |
| `/api/cves`          | CVE vulnerability data   |
| `/api/threats`       | Threat intelligence      |
| `/api/scans`         | Vulnerability scanning   |
| `/api/ai`            | AI chat assistant        |
| `/api/reports`       | Security reports         |
| `/api/notifications` | User notifications       |
| `/api/files`         | File upload/malware scan |
| `/api/settings`      | System settings (admin)  |
| `/api/audit-logs`    | Audit trail (admin)      |
| `/api/api-keys`      | API key management       |
| `/ws/{token}`        | WebSocket notifications  |

---

## Features

### Executive Dashboard
- Real-time threat score with severity breakdowns
- Active alerts and critical vulnerability counters
- Security health percentage with trend indicators
- Interactive severity distribution bars
- Top threats monitoring list
- AI-generated security recommendations
- Recent activity feed

### Threat Intelligence
- Real-time threat feed with IOCs (IPs, domains, hashes)
- Threat severity classification (Critical/High/Medium/Low)
- Confidence scoring with visual indicators
- Source attribution and tracking
- MITRE ATT&CK mapping ready

### Vulnerability Scanner
- Configurable scan targets (IP, domain, URL)
- Multiple scan types (quick, full, vulnerability, port)
- Scan status tracking and history
- Architecture-ready for Nmap, OpenVAS, Nessus

### CVE Explorer
- Search by CVE ID, title, description
- Filter by severity level
- Vendor and product search
- CVSS score visualization
- Remediation guidance
- NVD API sync integration

### Network Monitor
- Active host discovery
- Open port detection
- Device status tracking (online/offline/suspicious)
- OS fingerprinting
- Live connection monitoring

### Malware Scanner
- Secure file upload with SHA256/MD5 hashing
- File type detection via python-magic
- VirusTotal integration ready
- YARA rule matching architecture
- AI-powered malware analysis (with API key)

### Password Analyzer
- Real-time password strength evaluation
- Entropy calculation (bits)
- Brute-force time estimation
- Character set analysis (lower, upper, digits, special)
- Common password detection
- AI-powered recommendations

### AI Security Assistant
- Context-aware cybersecurity conversations
- Vulnerability and CVE explanation
- Security best practices guidance
- Incident response assistance
- Secure coding advice
- Log analysis support
- Conversation history with persistent storage
- OpenAI GPT-4 and Gemini support

### Notifications
- Real-time WebSocket push notifications
- Severity-categorized alerts
- Read/unread tracking
- Bulk mark-as-read
- Auto-refresh polling

### Reports
- Multiple report types (security, vulnerability, incident, compliance)
- Status tracking (draft, generated)
- PDF/CSV export ready
- Executive summary generation
- Technical findings documentation
- Risk assessment framework
- Recommendation tracking

### Admin Panel (RBAC)
- **3 roles**: Admin, Analyst, Viewer
- User management with CRUD operations
- Role-based permission system
- API key management
- System settings configuration
- Audit log viewer with filtering
- Granular resource-level permissions

---

## Project Structure

```
zerotrust-hub/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, dependencies
│   │   ├── database/      # Session, engine, base
│   │   ├── models/        # SQLAlchemy models (15 tables)
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic layer
│   │   ├── routers/       # API endpoint definitions
│   │   ├── middleware/     # CORS, rate limiting, security headers
│   │   ├── utils/         # Helper functions
│   │   └── tests/         # Pytest test suite
│   ├── main.py            # FastAPI application entry
│   ├── seed_data.py       # Database seeder
│   ├── websocket_manager.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   │   ├── auth/      # ProtectedRoute
│   │   │   └── layout/    # Sidebar, Header, Layout
│   │   ├── pages/         # Route pages (17 pages)
│   │   ├── services/      # Axios API client
│   │   ├── store/         # Zustand auth store
│   │   └── types/         # TypeScript interfaces
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## Security

- JWT authentication with short-lived access tokens + refresh tokens
- Passwords hashed with bcrypt
- SQLAlchemy ORM prevents SQL injection
- Input validation via Pydantic schemas
- CORS configured for allowed origins
- Rate limiting on all endpoints
- Secure HTTP headers (HSTS, XSS, XFO, nosniff)
- OWASP Top 10 compliant architecture
- Audit logging for all sensitive operations
- Role-based access control (RBAC)

---

## Database Schema

15 tables: `users`, `roles`, `permissions`, `role_permissions`, `audit_logs`, `vulnerabilities`, `scans`, `threats`, `malware_reports`, `files`, `ai_conversations`, `ai_conversation_messages`, `reports`, `notifications`, `settings`, `api_keys`

---

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend build validation
cd frontend
npm run build
```

---

## License

MIT
