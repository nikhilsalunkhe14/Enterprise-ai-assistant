# Enterprise AI Assistant - Phase 2: Conversation Persistence

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

3. **Run backend server:**
```bash
python main-phase2.py
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

3. **Run frontend:**
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
python main-phase2.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm install --package-lock-file package-new.json
npm start
```

## 📋 **NEW API ENDPOINTS**

### **Conversations:**
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/` - Get user's conversations
- `GET /api/conversations/{id}` - Get conversation with messages
- `POST /api/conversations/{id}/messages` - Send message
- `DELETE /api/conversations/{id}` - Delete conversation
- `PUT /api/conversations/{id}` - Update conversation title

### **Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout user

## 🗂️ **DATABASE SCHEMA**

### **Conversations Table:**
- `id` (Primary Key)
- `user_id` (Foreign Key to users)
- `title` (Conversation title)
- `created_at` (Timestamp)

### **Messages Table:**
- `id` (Primary Key)
- `conversation_id` (Foreign Key to conversations)
- `role` ('user' or 'assistant')
- `content` (Message content)
- `created_at` (Timestamp)

## 🎨 **FRONTEND FEATURES**

### **Sidebar:**
- ✅ **Conversation List** - Shows all user conversations
- ✅ **Create New** - Modal to create new conversation
- ✅ **Click to Open** - Load conversation messages
- ✅ **Delete** - Delete conversation with confirmation
- ✅ **Message Count** - Shows number of messages per conversation
- ✅ **Active State** - Highlights current conversation

### **Chat Interface:**
- ✅ **Message Display** - User and assistant messages
- ✅ **Send Messages** - Real-time message sending
- ✅ **Auto-scroll** - Scroll to latest message
- ✅ **Timestamps** - Show message times
- ✅ **Loading States** - Visual feedback
- ✅ **Empty State** - Prompt to select conversation

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

## 🎯 **TESTING THE SYSTEM**

1. **Start both services** (backend on 8000, frontend on 3000)
2. **Login** to the application
3. **Create Conversation** - Click + button in sidebar
4. **Send Messages** - Type and send messages
5. **Switch Conversations** - Click different conversations
6. **Delete Conversation** - Click trash icon
7. **Refresh Page** - Verify persistence

## 📊 **PHASE 2 FEATURES**

### **Backend Features:**
- ✅ **Conversation Management** - CRUD operations
- ✅ **Message Persistence** - All messages saved
- ✅ **User Isolation** - Users see only their conversations
- ✅ **Message History** - Complete chat history
- ✅ **Relationships** - Proper foreign key constraints
- ✅ **API Documentation** - Auto-generated FastAPI docs

### **Frontend Features:**
- ✅ **Real-time Chat** - Instant message display
- ✅ **Conversation Sidebar** - Full conversation management
- ✅ **Persistent State** - Conversations survive refresh
- ✅ **Responsive Design** - Works on all screen sizes
- ✅ **User Experience** - Smooth interactions
- ✅ **Error Handling** - Graceful error management

## 🚀 **PRODUCTION READY**

This conversation persistence system includes:
- **Database Integrity** - Proper relationships and constraints
- **Security** - User isolation and authentication
- **Scalability** - Efficient queries and pagination ready
- **Performance** - Optimized database operations
- **User Experience** - Professional chat interface

## 📋 **NEXT PHASE**

**Phase 2 Complete! Ready for Phase 3: ChatGPT-like UI**

The conversation persistence system is fully functional and production-ready with:
- Complete CRUD operations
- Real-time messaging
- Professional UI
- Database persistence
- User authentication integration

---

## 🎉 **PHASE 2 COMPLETE**

**✅ Conversation persistence is fully implemented and working!**

**🚀 Ready for Phase 3: ChatGPT-like UI?**
