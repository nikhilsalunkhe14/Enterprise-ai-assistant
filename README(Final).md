# 🚀 Enterprise AI Assistant - Deployment Guide

## 📋 Overview

This is a comprehensive **Enterprise AI Assistant** application that provides intelligent IT project delivery guidance using advanced AI technologies. The application consists of a FastAPI backend with MongoDB Atlas integration and a modern JavaScript frontend.

### 🎯 Key Features
- **🤖 AI-Powered Chat**: Advanced conversational AI with Groq API
- **👥 User Management**: Secure authentication with JWT tokens
- **💬 Conversation Management**: Create, rename, export conversations
- **🎤 Voice Input**: Speech-to-text functionality
- **📄 Export Options**: PDF, Markdown, JSON export capabilities
- **🔧 Settings Management**: Model selection and configuration
- **🌐 Modern UI**: Responsive, professional interface

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend     │    │    Backend      │    │   MongoDB       │
│                 │    │                 │    │                 │
│ • index.html   │◄──►│ • FastAPI       │◄──►│ • Atlas         │
│ • JavaScript   │    │ • Auth Service  │    │ • Users         │
│ • TailwindCSS  │    │ • Chat API      │    │ • Conversations │
│ • Voice Input  │    │ • WebSocket     │    │ • Messages      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 Quick Start Guide

### 📦 Prerequisites

Ensure you have the following installed:
- **Node.js** (v14 or higher)
- **Python** (v3.10 or higher)
- **MongoDB Atlas** account (free tier available)
- **Groq API Key** (get from [groq.com](https://groq.com))

---

## 🔧 Setup Instructions

### 1️⃣ **Backend Setup**

#### **1.1 Install Python Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

#### **1.2 Environment Configuration**
Create a `.env` file in the `backend/` directory:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/your_database
DATABASE_NAME=chatgpt_clone

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Groq AI API Configuration
GROK_API_KEY=your_groq_api_key_here

# Application Configuration
PORT=8000
DEBUG=true

# CORS Configuration
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

#### **1.3 Start Backend Server**
```bash
cd backend
python main_new.py
```

**Expected Output:**
```
ChatGPT Clone Backend is ready!
INFO: Uvicorn running on http://0.0.0.0:8000
✅ Connected to MongoDB Atlas successfully
```

---

### 2️⃣ **Frontend Setup**

#### **2.1 Install Node.js Dependencies**
```bash
cd frontend
npm install
```

#### **2.2 Start Frontend Server**
```bash
cd frontend
npm start
```

**Expected Output:**
```
Available on:
  http://127.0.0.1:5500/frontend/index.html
Hit CTRL-C to stop the server
```

---

## 🌐 Access the Application

### **Main Application URL**
```
http://127.0.0.1:5500/frontend/index.html
```

### **Default Login Credentials**
- **Email**: `test@example.com`
- **Password**: `test123`

---

## 🔑 API Keys Setup

### **Groq API Key**
1. Visit [groq.com](https://groq.com)
2. Create an account and get your API key
3. Add it to your `.env` file:
   ```env
   GROK_API_KEY=gsk_your_api_key_here
   ```

### **MongoDB Atlas Setup**
1. Create a free account at [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a new cluster
3. Get your connection string
4. Add it to your `.env` file:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database
   ```

---

## 🐳 Docker Deployment (Optional)

### **Using Docker Compose**
```bash
# Build and start all services
docker-compose up --build

# Stop services
docker-compose down
```

### **Services Included**
- **Frontend**: Port 3000
- **Backend**: Port 8000
- **PostgreSQL**: Port 5432
- **Redis**: Port 6379

---

## 📱 Application Features

### **🔐 Authentication**
- User registration and login
- JWT token-based authentication
- Secure session management

### **💬 Chat Interface**
- Real-time messaging with AI
- Voice input support
- Message history
- Conversation management

### **📤 Export Functionality**
- **Individual Conversations**: Export single chats
- **Multiple Formats**: PDF, Markdown, JSON, TXT
- **Professional Layout**: Beautifully formatted exports

### **⚙️ Settings**
- Model selection (GPT-3.5, GPT-4, Claude 3)
- Token limit configuration
- Conversation management

---

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Backend Not Starting**
```bash
# Check Python version
python --version

# Install dependencies
pip install -r backend/requirements.txt

# Check environment variables
cat backend/.env
```

#### **2. Frontend Not Loading**
```bash
# Check Node.js version
node --version

# Install dependencies
npm install

# Start server
npm start
```

#### **3. Database Connection Issues**
```bash
# Check MongoDB URL format
echo $MONGODB_URL

# Test connection
python -c "from database.mongodb import mongodb_manager; import asyncio; asyncio.run(mongodb_manager.connect())"
```

#### **4. API Key Issues**
```bash
# Verify Groq API key
curl -H "Authorization: Bearer $GROK_API_KEY" https://api.groq.com/v1/models
```

---

## 📊 Project Structure

```
PROMPT/
├── backend/
│   ├── main_new.py              # Main FastAPI application
│   ├── requirements.txt          # Python dependencies
│   ├── .env                     # Environment variables
│   ├── routes/                  # API routes
│   ├── services/                # Business logic
│   └── database/                # Database models
├── frontend/
│   ├── index.html               # Main application page
│   ├── package.json             # Node.js dependencies
│   └── js/                      # JavaScript modules
├── docker-compose.yml           # Docker configuration
├── Dockerfile                   # Docker image definition
└── README(Final).md            # This file
```

---

## 🚀 Production Deployment

### **Environment Variables Required**
- `MONGODB_URL`: MongoDB Atlas connection string
- `GROK_API_KEY`: Groq API key
- `SECRET_KEY`: JWT secret key
- `JWT_SECRET`: JWT secret for token validation

### **Security Considerations**
- Change all default passwords and secrets
- Use HTTPS in production
- Enable CORS for your domain
- Set up proper database indexing
- Monitor API usage and costs

---

## 📞 Support & Maintenance

### **Health Checks**
- **Backend Health**: `http://localhost:8000/health`
- **Frontend Status**: Check browser console for errors
- **Database Status**: Verify MongoDB Atlas connection

### **Performance Monitoring**
- Monitor API response times
- Track database query performance
- Monitor user activity and storage usage

### **Backup Strategy**
- Regular MongoDB Atlas backups
- Export important conversations
- Monitor storage usage

---

## 🎯 Next Steps

1. **✅ Extract this ZIP file**
2. **✅ Follow the setup instructions above**
3. **✅ Configure your API keys**
4. **✅ Start the application**
5. **✅ Test all features**

### **For Technical Support**
- Check the troubleshooting section
- Review the error logs
- Verify all environment variables
- Ensure all dependencies are installed

---

## 📄 License

MIT License - This project is open source and available for commercial use.

---

**🎉 Congratulations! Your Enterprise AI Assistant is ready to use!**

*For any issues or questions, refer to the troubleshooting section or check the application logs.*
