# 🚀 AI IT Project Delivery Assistant - Deployment Guide

## 📋 **DEPLOYMENT CHECKLIST**

### ✅ **Pre-Deployment Requirements**
- [x] `requirements.txt` with all dependencies
- [x] `render.yaml` configuration file
- [x] Dynamic port handling in `main.py`
- [x] Frontend uses `window.location.origin`
- [x] Environment variable for `GROQ_API_KEY`
- [x] `.gitignore` for clean deployment

## 🌐 **DEPLOYMENT STEPS**

### **1. Push to GitHub**
```bash
git init
git add .
git commit -m "Ready for Render deployment"
git branch -M main
git remote add origin https://github.com/yourusername/ai-it-project-assistant.git
git push -u origin main
```

### **2. Deploy to Render**
1. Go to [render.com](https://render.com)
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Select `ai-it-project-assistant` repository
6. Render will auto-detect `render.yaml`
7. Set environment variable:
   - **GROQ_API_KEY**: Your Groq API key
8. Click "Create Web Service"

### **3. Verify Deployment**
- Wait for build to complete (2-3 minutes)
- Visit your app: `https://ai-it-project-assistant.onrender.com`
- Test with sample query
- Check logs in Render dashboard

## 🔧 **ENVIRONMENT VARIABLES**

### **Required**
```
GROQ_API_KEY=your_groq_api_key_here
PORT=10000  # (Set by Render automatically)
```

### **Optional**
```
ENVIRONMENT=production
DATABASE_URL=sqlite:///./ai_agent.db
```

## 📊 **DEPLOYMENT ARCHITECTURE**

```
┌─────────────────┐
│   Render.com   │
│   (Frontend)   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   FastAPI      │
│   (Backend)    │
│   Port: $PORT   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Groq API     │
│   (LLM)        │
└─────────────────┘
```

## 🚨 **TROUBLESHOOTING**

### **Build Fails**
- Check `requirements.txt` format
- Verify Python version compatibility
- Check `render.yaml` syntax

### **App Not Loading**
- Verify `GROQ_API_KEY` is set
- Check Render logs
- Ensure port is dynamic (`$PORT`)

### **API Errors**
- Check Groq API key validity
- Verify rate limits
- Check CORS settings

## 📈 **MONITORING**

### **Render Dashboard**
- Build logs
- Runtime logs
- Metrics (CPU, Memory)
- Error tracking

### **Health Checks**
```bash
curl https://your-app.onrender.com/health
```

## 🔄 **UPDATES**

### **To Update**
1. Push changes to GitHub
2. Render auto-deploys
3. Monitor build logs

### **Rollback**
1. Go to Render dashboard
2. Click "Deploy" → "Redeploy"
3. Select previous commit

## 📞 **SUPPORT**

### **Render Documentation**
- [Render Docs](https://render.com/docs)

### **Common Issues**
- Memory limits (Free tier: 512MB)
- Build timeouts (15 minutes)
- Cold starts (30 seconds)

---

**🎉 Your AI Assistant is ready for production deployment!**
