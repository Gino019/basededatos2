# 🎭 Enmask — Static Data Masking Platform

> A production-ready, non-containerized Static Data Masking (SDM) platform for hybrid **PostgreSQL** and **MongoDB** environments.

---

## Architecture Overview

```
EnmascaradoDatos/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py                        # FastAPI entrypoint
│       ├── core/                          # Config, logging, exceptions
│       ├── domain/
│       │   ├── entities/                  # Connection, MaskingRule, MaskingJob
│       │   └── interfaces/                # Repository & Strategy ABCs
│       ├── infrastructure/
│       │   ├── db/                        # postgres_client, mongodb_client
│       │   ├── masking/                   # Substitution, Hashing, Redaction, Nullification
│       │   └── repositories/              # MemoryRepository (generic)
│       ├── application/
│       │   ├── schemas.py                 # Pydantic DTOs
│       │   └── services/                  # connection_service, masking_service, job_orchestrator
│       └── api/
│           ├── deps.py
│           └── routers/                   # connections, rules, jobs, reports
└── frontend/
    ├── index.html
    ├── vite.config.ts
    └── src/
        ├── main.tsx / App.tsx             # React + react-router-dom
        ├── index.css                      # Premium design system
        ├── types/                         # TypeScript interfaces
        ├── services/api.ts                # REST API calls
        ├── hooks/useToast.ts              # Toast notification hook
        ├── components/                    # Sidebar, ToastContainer
        └── pages/                         # Dashboard, Connections, Rules, Jobs
```

---

## 🚀 Despliegue en Railway (Recomendado)

### 1. Preparar cuentas
- [Railway.app](https://railway.app) - Crea cuenta gratuita
- [MongoDB Atlas](https://cloud.mongodb.com) - Cluster gratuito
- [Google Cloud Console](https://console.cloud.google.com) - Para OAuth

### 2. Configurar MongoDB Atlas
1. Crea cluster gratuito
2. Crea usuario de base de datos
3. Whitelist IP: `0.0.0.0/0` (para Railway)
4. Copia la connection string: `mongodb+srv://usuario:password@cluster.mongodb.net/enmask_meta`

### 3. Configurar Google OAuth
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea proyecto → APIs & Services → Credentials
3. Crea "OAuth 2.0 Client ID" → Web application
4. Authorized redirect URIs: `https://tu-backend.railway.app/api/v1/auth/google/callback`
5. Copia Client ID

### 4. Desplegar Backend
1. `git clone <tu-repo>` o sube el código
2. En Railway: New Project → Deploy from GitHub
3. Selecciona la carpeta `backend/`
4. Variables de entorno (Environment Variables):
   ```
   SECRET_KEY=tu_clave_muy_segura
   GOOGLE_CLIENT_ID=tu_google_client_id
   ADMIN_EMAILS=tu_email@example.com
   REPOSITORY_BACKEND=mongodb
   MONGODB_META_URI=mongodb+srv://...
   BACKEND_CORS_ORIGINS=https://tu-frontend.railway.app
   ```
5. Deploy → Copia la URL del backend

### 5. Desplegar Frontend
1. En Railway: New Project → Deploy from GitHub
2. Selecciona la carpeta `frontend/`
3. Variables de entorno:
   ```
   VITE_API_URL=https://tu-backend.railway.app/api/v1
   VITE_GOOGLE_CLIENT_ID=tu_google_client_id
   ```
4. Deploy → ¡Listo!

### 6. Configurar CORS final
- En el backend de Railway, actualiza `BACKEND_CORS_ORIGINS` con la URL exacta del frontend

---

## 🏃‍♂️ Desarrollo Local
| npm        | ≥ 9       |

> **Optional**: A running PostgreSQL or MongoDB instance (only required when actually running masking jobs).

---

## 1 — Backend Setup

### 1.1 Create a virtual environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 1.2 Install dependencies

```powershell
pip install -r requirements.txt
```

### 1.3 Configure environment variables

```powershell
Copy-Item .env.example .env
# Edit .env if needed (CORS origins, etc.)
```

The default `.env` works out-of-the-box for local development.

### 1.4 Run the API server

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API Base**: `http://localhost:8000/api/v1`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 2 — Frontend Setup

### 2.1 Install Node dependencies

```powershell
cd ..\frontend
npm install
```

### 2.2 Run the dev server

```powershell
npm run dev
```

- **Frontend**: `http://localhost:5173`

The Vite dev server is pre-configured to proxy `/api` calls to `http://localhost:8000`, so **no CORS issues** during development.

---

## 3 — End-to-End Usage

### Step 1 — Add a Connection

Navigate to **Connections** → click **Add Connection**. Fill in your PostgreSQL or MongoDB credentials.

**PostgreSQL example:**
```
Type:     postgres
Host:     localhost
Port:     5432
Database: mydb
Username: postgres
Password: secret
```

### Step 2 — Create Masking Rules

Navigate to **Masking Rules** → click **New Rule**. Define which table/collection and column to mask.

**Available strategies:**

| Strategy      | Description                                         |
|---------------|-----------------------------------------------------|
| `hashing`     | SHA-256 deterministic hash (same input → same output)|
| `substitution`| Replace with realistic Faker data (name, email, etc.)|
| `redaction`   | Replace all characters with `*`                     |
| `nullification`| Set the field value to `NULL` / `None`             |

### Step 3 — Run a Job

Navigate to **Jobs** → click **New Job**. Select a connection and the rules to apply → click **▶ Run**. The job runs in the background and the status auto-refreshes.

---

## 4 — Optional: PostgreSQL Sample Schema

If you want to test with PostgreSQL, run this in HeidiSQL or psql:

```sql
CREATE DATABASE masking_demo;

\c masking_demo

CREATE TABLE users (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL,
    email    TEXT NOT NULL,
    phone    TEXT,
    address  TEXT
);

INSERT INTO users (name, email, phone, address) VALUES
  ('Alice Smith',  'alice@example.com',  '+1-555-0100', '123 Maple St'),
  ('Bob Johnson',  'bob@example.com',    '+1-555-0101', '456 Oak Ave'),
  ('Carol White',  'carol@example.com',  '+1-555-0102', '789 Pine Rd');
```

Create rules targeting table `users` columns `name`, `email`, `phone` with strategies of your choice.

---

## 5 — Optional: MongoDB Sample Data

```javascript
use masking_demo

db.customers.insertMany([
  { name: "Alice Smith",  email: "alice@example.com", phone: "+1-555-0100" },
  { name: "Bob Johnson",  email: "bob@example.com",   phone: "+1-555-0101" },
])
```

Create rules targeting collection `customers` columns `name`, `email`.

---

## API Reference

| Method | Endpoint                        | Description              |
|--------|---------------------------------|--------------------------|
| GET    | `/api/v1/connections/`          | List all connections     |
| POST   | `/api/v1/connections/`          | Create a connection      |
| DELETE | `/api/v1/connections/{id}`      | Delete a connection      |
| GET    | `/api/v1/rules/`                | List all rules           |
| POST   | `/api/v1/rules/`                | Create a masking rule    |
| DELETE | `/api/v1/rules/{id}`            | Delete a rule            |
| GET    | `/api/v1/jobs/`                 | List all jobs            |
| POST   | `/api/v1/jobs/`                 | Create a job             |
| POST   | `/api/v1/jobs/{id}/run`         | Run a job (background)   |
| GET    | `/api/v1/jobs/{id}`             | Get job status           |
| GET    | `/api/v1/reports/summary`       | Get platform summary     |

---

## Notes

- **State is in-memory**: Connections, rules, and jobs are stored in memory and reset on server restart. For persistence, swap `MemoryRepository` with a SQLite/JSON file-backed implementation.
- **Masking is destructive**: Running a job will permanently update the target database rows/documents. Test on a copy of your data first.
- **Determinism**: The `hashing` strategy produces the same output for the same input + salt, making it suitable for referential integrity across tables.

---

## Docker Compose

Run the full stack with PostgreSQL, MongoDB, backend, and frontend:

```powershell
cd ..\EnmascaradoDatos
docker-compose up --build
```

Then:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
