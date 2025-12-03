# SimpleAnalysis - Stock Analysis Platform

A comprehensive stock analysis platform for Indian markets (NSE/BSE) built with FastAPI and React.

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: MongoDB (with Motor async driver)
- **Authentication**: JWT tokens (15 min access, 7 day refresh)
- **Cache**: Redis
- **Data Source**: Yahoo Finance (yfinance)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS

## Project Structure

```
simpleanalysis/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Security, database, cache
│   │   ├── models/          # MongoDB models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── api/            # API client
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── store/          # Zustand stores
    │   └── types/          # TypeScript types
    ├── package.json
    └── .env.example
```

## Quick Start with Docker (Recommended)

The easiest way to run the entire application:

```bash
# Clone the repository
git clone <your-repo-url>
cd simpleanalysis

# Start all services (MongoDB, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

The application will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

### Development with Docker

For development, use the dev compose file to run only MongoDB and Redis:

```bash
# Start only MongoDB and Redis
docker-compose -f docker-compose.dev.yml up -d

# Run backend locally
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd app
python main.py

# Run frontend locally (in another terminal)
cd frontend
npm install
npm run dev
```

## Manual Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (local or MongoDB Atlas)
- Redis (optional for Phase 1, required for Phase 2+)
- Docker & Docker Compose (for containerized setup)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set your values:
   # - SECRET_KEY (generate with: openssl rand -hex 32)
   # - MONGODB_URL (your MongoDB connection string)
   # - REDIS_URL (if using Redis)
   ```

5. **Run the backend**
   ```bash
   cd app
   python main.py
   # Or use uvicorn:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/api/docs

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # Or with tailwindcss and postcss:
   npm install -D tailwindcss postcss autoprefixer
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default: http://localhost:8000/api/v1)
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

Frontend will be available at: http://localhost:3000

## Phase 1 Completed Features

### Backend
✅ FastAPI application setup with async support
✅ MongoDB connection with Motor
✅ JWT authentication (access + refresh tokens)
✅ User registration and login
✅ Password hashing with bcrypt
✅ User profile management
✅ Database indexes for performance
✅ CORS configuration
✅ API documentation (Swagger/OpenAPI)

### Frontend
✅ React + TypeScript + Vite setup
✅ React Router with protected routes
✅ Zustand state management
✅ Axios API client with JWT interceptors
✅ Automatic token refresh
✅ Login page
✅ Registration page
✅ Dashboard page
✅ Tailwind CSS styling

## API Endpoints (Phase 1)

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update user profile
- `PUT /api/v1/auth/password` - Change password

### Health
- `GET /health` - Health check
- `GET /` - API info

## Testing the Application

### 1. Start MongoDB
```bash
# If using local MongoDB:
mongod --dbpath /path/to/data

# Or use MongoDB Atlas (cloud)
```

### 2. Start Backend
```bash
cd backend/app
python main.py
```

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

### 4. Test Flow
1. Navigate to http://localhost:3000
2. Click "Register here" to create an account
3. Fill in the registration form
4. After successful registration, login with your credentials
5. You'll be redirected to the Dashboard

## Development

### Backend Development
- API docs available at `/api/docs` (Swagger UI)
- MongoDB accessed via Motor (async)
- Add new endpoints in `app/api/v1/`
- Add models in `app/models/`
- Add schemas in `app/schemas/`

### Frontend Development
- Hot reload enabled with Vite
- Add new pages in `src/pages/`
- Add components in `src/components/`
- API calls in `src/api/`
- State management in `src/store/`

## Next Steps (Phase 2)

- Watchlist management
- Excel upload functionality
- Index-based watchlist creation (Nifty50, Bank Nifty, etc.)
- Stock search with Yahoo Finance integration
- Redis caching for stock data

## Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=simpleanalysis
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running
- Check MONGODB_URL in .env
- Verify network connectivity

### CORS Errors
- Check CORS_ORIGINS in backend .env
- Ensure frontend URL is whitelisted

### Token Refresh Issues
- Check SECRET_KEY matches between requests
- Verify token expiration settings

## License

Proprietary - All rights reserved

## Support

For issues and questions, please create an issue in the repository.
