# Enterprise AI Assistant - Phase 1 Authentication

## 🚀 **HOW TO RUN**

### **Backend Setup**

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install dependencies:**
```bash
pip install -r requirements-auth-new.txt
```

3. **Run the backend server:**
```bash
python main-auth.py
```

The backend will start on `http://localhost:8000`

### **Frontend Setup**

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install --package-lock-file package-new.json
```

3. **Run the frontend:**
```bash
npm start
```

The frontend will start on `http://localhost:3000`

### **Quick Start (Both Services)**

Open two terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
pip install -r requirements-auth-new.txt
python main-auth.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install --package-lock-file package-new.json
npm start
```

## 📋 **API ENDPOINTS**

### **Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

### **Health:**
- `GET /` - API info
- `GET /health` - Health check

## 🔧 **ENVIRONMENT VARIABLES**

### **Backend (.env):**
```env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./app.db
```

### **Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
```

## 🗂️ **FOLDER STRUCTURE**

```
backend/
├── models/
│   ├── user.py              # User model
│   └── schemas.py          # Pydantic schemas
├── routes/
│   └── auth.py             # Authentication routes
├── services/
│   ├── auth_service.py      # User authentication logic
│   └── jwt_service.py      # JWT token management
├── database/
│   └── connection.py       # Database connection
├── main-auth.py            # FastAPI application
└── requirements-auth-new.txt # Python dependencies

frontend/
├── src/
│   └── App-new.js         # React authentication app
├── public/
│   └── index-new.html      # HTML template
└── package-new.json        # Node.js dependencies
```

## 🔒 **SECURITY FEATURES**

- ✅ **Password Hashing** - Bcrypt with salt
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **CORS Protection** - Configurable cross-origin policy
- ✅ **Input Validation** - Pydantic models for data validation
- ✅ **Session Management** - Token expiration and validation
- ✅ **SQL Injection Protection** - SQLAlchemy ORM

## 🎯 **TESTING THE SYSTEM**

1. **Register a new user:**
   - Visit `http://localhost:3000`
   - Click "Don't have an account? Register"
   - Fill in name, email, password
   - Submit

2. **Login:**
   - Use your credentials to login
   - You'll be redirected to dashboard

3. **Test API endpoints:**
   - Visit `http://localhost:8000/docs` for API documentation
   - Test authentication endpoints

## 🚀 **PRODUCTION DEPLOYMENT**

### **Backend:**
```bash
pip install gunicorn
gunicorn main-auth:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Frontend:**
```bash
npm run build
# Serve build folder with nginx or similar
```

## 📊 **DATABASE SCHEMA**

### **Users Table:**
- `id` (Primary Key)
- `email` (Unique, Indexed)
- `password_hash` (Bcrypt hash)
- `name` (User's full name)
- `created_at` (Timestamp)
- `last_login` (Timestamp, nullable)
- `is_active` (Boolean, default true)

## 🎉 **READY FOR PHASE 2**

The authentication system is complete and production-ready!

**Next Phase: Conversation Persistence**
