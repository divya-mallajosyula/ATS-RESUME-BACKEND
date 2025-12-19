# Deployment Guide - ATS Resume Analyzer Backend

This guide covers deploying the Flask backend to various cloud platforms.

## 🚀 Quick Deploy Options

### Option 1: Render (Recommended - Free Tier Available)

1. **Sign up** at [render.com](https://render.com)

2. **Create New Web Service**
   - Connect your GitHub repository
   - Select the repository: `ATS-RESUME-BACKEND`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Set Environment Variables:**
   ```
   MONGO_URI=your_mongodb_connection_string
   DB_NAME=ats_analyzer
   SECRET_KEY=your-secret-key
   FLASK_ENV=production
   FRONTEND_URL=your-frontend-url
   PORT=5000
   ```

4. **Deploy!**

**Render automatically uses `render.yaml` if present.**

---

### Option 2: Railway (Easy Deployment)

1. **Sign up** at [railway.app](https://railway.app)

2. **New Project → Deploy from GitHub**
   - Select your repository
   - Railway auto-detects Python

3. **Set Environment Variables:**
   - Go to Variables tab
   - Add all variables from `.env`

4. **Configure:**
   - Root Directory: `backend`
   - Start Command: `gunicorn app:app`

5. **Deploy!**

---

### Option 3: Heroku

1. **Install Heroku CLI:**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create App:**
   ```bash
   cd backend
   heroku create ats-resume-analyzer
   ```

4. **Set Environment Variables:**
   ```bash
   heroku config:set MONGO_URI=your_mongodb_connection_string
   heroku config:set DB_NAME=ats_analyzer
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set FLASK_ENV=production
   heroku config:set FRONTEND_URL=your-frontend-url
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

---

### Option 4: Docker Deployment

#### Build and Run Locally:
```bash
cd backend
docker build -t ats-resume-analyzer .
docker run -p 5000:5000 --env-file .env ats-resume-analyzer
```

#### Deploy to Docker Hub:
```bash
# Build
docker build -t yourusername/ats-resume-analyzer .

# Push
docker push yourusername/ats-resume-analyzer
```

#### Deploy to Any Container Platform:
- **Fly.io**: `flyctl launch`
- **DigitalOcean App Platform**: Use Dockerfile
- **AWS ECS/Fargate**: Use Dockerfile
- **Google Cloud Run**: Use Dockerfile

---

## 📋 Environment Variables Required

Create these in your deployment platform:

```env
# MongoDB (Required)
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=ats_analyzer

# Flask (Required)
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=production
FLASK_DEBUG=False

# Server (Optional - auto-set by platform)
PORT=5000

# CORS (Required)
FRONTEND_URL=https://your-frontend-domain.com

# File Upload (Optional)
MAX_FILE_SIZE=5242880
```

---

## 🔧 Platform-Specific Notes

### Render
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ Uses `render.yaml` automatically
- ✅ HTTPS included

### Railway
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ Simple configuration
- ✅ Uses `railway.json`

### Heroku
- ⚠️ No free tier (paid only)
- ✅ Easy deployment
- ✅ Uses `Procfile`
- ✅ Add-ons available

### Docker
- ✅ Works everywhere
- ✅ Consistent environment
- ✅ Easy scaling

---

## 🧪 Testing Deployment

After deployment, test your API:

```bash
# Health check
curl https://your-app-url.com/health

# Test upload
curl -X POST https://your-app-url.com/api/upload-resume \
  -F "file=@resume.pdf"
```

---

## 🔒 Security Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Update `FRONTEND_URL` to production domain
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Review CORS settings
- [ ] Keep MongoDB credentials secure

---

## 📊 Monitoring

### Health Check Endpoint
```
GET /health
```

### Logs
- **Render**: Dashboard → Logs
- **Railway**: Deployments → View Logs
- **Heroku**: `heroku logs --tail`

---

## 🐛 Troubleshooting

### Common Issues:

1. **Port binding error:**
   - Ensure `PORT` env var is set
   - Use `0.0.0.0` as host

2. **MongoDB connection failed:**
   - Check `MONGO_URI` is correct
   - Verify MongoDB Atlas IP whitelist includes platform IPs

3. **Import errors:**
   - Ensure `requirements.txt` is complete
   - Check Python version matches `runtime.txt`

4. **CORS errors:**
   - Update `FRONTEND_URL` in environment variables
   - Check CORS origins in `app.py`

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Gunicorn Docs](https://gunicorn.org/)

---

## 🎯 Recommended: Render

For easiest deployment, use **Render**:
1. Free tier available
2. Auto-deploy from GitHub
3. Automatic HTTPS
4. Simple configuration

Just connect your GitHub repo and set environment variables!

