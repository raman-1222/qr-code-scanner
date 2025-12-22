# Free Deployment Guide for QR Code Scanner

Deploy your MCP server for **FREE** on multiple platforms.

## ⭐ Best Free Options (Ranked)

| Platform | Monthly Free | Setup Time | Best For | Link Longevity |
|----------|-------------|-----------|---------|----------------|
| **Google Cloud Run** | 2M requests | 10 min | Production-ready | ✅ Permanent |
| **Render** | 750 hours | 5 min | Development | ✅ Permanent |
| **Railway** | $5/month | 5 min | Quick testing | ⚠️ Limited hours |
| **Hugging Face Spaces** | Unlimited | 5 min | ML projects | ✅ Permanent |
| **Replit** | Unlimited | 3 min | Development | ⚠️ May sleep |

---

## 🚀 Option 1: Google Cloud Run (RECOMMENDED - FREE)

### Best for: Production use, high reliability

**Advantages:**
- Free tier: 2 million requests/month
- Pay-as-you-go after that
- Always-on (no sleeping)
- Official Google support
- Easily integrable with other Google services

### Setup (10 minutes)

**1. Create Google Cloud Account**
```bash
# Go to https://cloud.google.com/free
# Sign up (free tier includes Cloud Run)
```

**2. Install Google Cloud CLI**
```bash
# Windows
choco install google-cloud-sdk

# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
```

**3. Initialize and Deploy**
```bash
# Initialize
gcloud init
gcloud config set project PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy
gcloud run deploy qr-scanner \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1
```

**4. Get Your URL**
```bash
gcloud run services describe qr-scanner --region us-central1 --format='value(status.url)'
```

### Usage
```bash
# Scan file
curl "https://qr-scanner-xxx.run.app/scan/file?image_path=/path/to/image.jpg"

# Upload and scan
curl -X POST -F "file=@label.jpg" https://qr-scanner-xxx.run.app/scan/upload

# Base64 scan
curl -X POST https://qr-scanner-xxx.run.app/scan/base64 \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "..."}'
```

---

## 🎯 Option 2: Render (FREE - Easy Setup)

### Best for: Quick deployment, simple hosting

**Advantages:**
- 750 free compute hours/month (enough for always-on)
- Easy GitHub integration
- Simple deployment process

### Setup (5 minutes)

**1. Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/qr-scanner.git
git push -u origin main
```

**2. Create on Render.com**
- Go to https://render.com
- Sign up with GitHub
- Click "New +" → "Web Service"
- Connect your repository
- Configure:
  - **Name:** qr-scanner
  - **Environment:** Docker
  - **Plan:** Free
  - **Port:** 8000

**3. Deploy**
- Click "Create Web Service"
- Wait ~2 minutes for deployment
- Get URL from dashboard

### Usage
Same as Cloud Run above (just different URL)

---

## 🤗 Option 3: Hugging Face Spaces (FREE - Unlimited)

### Best for: ML/AI projects, unlimited access

**Advantages:**
- Unlimited free tier
- Great for AI/ML projects
- Easy file uploads
- Built-in version control

### Setup (5 minutes)

**1. Create Space**
- Go to https://huggingface.co/spaces
- Click "Create new Space"
- Name: `qr-code-scanner`
- License: MIT
- Space SDK: Docker

**2. Upload Files**
```bash
# Clone the space
git clone https://huggingface.co/spaces/username/qr-code-scanner
cd qr-code-scanner

# Copy your files
cp -r /path/to/qr_code_scanner/* .

# Commit and push
git add .
git commit -m "Add QR scanner"
git push
```

**3. Access**
- Auto-builds and deploys
- URL: `https://huggingface.co/spaces/username/qr-code-scanner`

---

## 🚂 Option 4: Railway (FREE - $5/month credit)

### Best for: Quick testing and development

**Advantages:**
- $5/month free credit (enough for testing)
- GitHub integration
- Simple deployment

### Setup (5 minutes)

**1. Go to Railway.app**
- https://railway.app
- Sign up with GitHub

**2. Create Project**
- Click "New Project"
- Select "GitHub Repo"
- Connect your qr-scanner repo
- Add environment variables

**3. Configure**
```
PORT=8000
```

**4. Deploy**
- Automatically deploys on push
- Get URL from dashboard

---

## 💻 Option 5: Replit (FREE - May sleep)

### Best for: Quick prototyping, learning

**Advantages:**
- Free tier available
- No setup required
- Instant deployment

### Setup (3 minutes)

**1. Go to Replit.com**
- Create account
- Click "Import from GitHub"
- Paste your repo URL

**2. Configure**
- Click "Run" 
- Replit auto-detects Python
- Sets up environment

**3. Deploy**
- Click "Deploy"
- Get shareable URL

---

## 🔗 Using Your Deployed Server

### With Python
```python
import requests
import base64

API_URL = "https://your-deployment-url.run.app"

# Scan from file
response = requests.get(f"{API_URL}/scan/file", params={
    "image_path": "/path/to/image.jpg"
})
print(response.json())

# Upload and scan
with open("label.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{API_URL}/scan/upload", files=files)
    print(response.json())

# Batch scan
images = []
for img_file in ["label-001.jpg", "label-002.jpg"]:
    with open(img_file, "rb") as f:
        images.append({
            "name": img_file,
            "data": base64.b64encode(f.read()).decode()
        })

response = requests.post(f"{API_URL}/scan/batch", json={"images": images})
print(response.json())
```

### With cURL
```bash
API_URL="https://your-deployment-url.run.app"

# Health check
curl $API_URL/health

# Scan file
curl "$API_URL/scan/file?image_path=/path/to/image.jpg"

# Upload file
curl -X POST -F "file=@label.jpg" $API_URL/scan/upload

# Base64
curl -X POST $API_URL/scan/base64 \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"..."}'
```

### With JavaScript/Node.js
```javascript
const API_URL = "https://your-deployment-url.run.app";

// Health check
const health = await fetch(`${API_URL}/health`).then(r => r.json());
console.log(health);

// Upload and scan
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const result = await fetch(`${API_URL}/scan/upload`, {
    method: "POST",
    body: formData
}).then(r => r.json());

console.log(result);
```

### With Gemini (Direct Integration)
```python
import requests
import os

API_URL = "https://your-deployment-url.run.app"

# Use in custom Gemini prompt
def scan_with_deployed_api(image_base64):
    response = requests.post(
        f"{API_URL}/scan/base64",
        json={"image_base64": image_base64}
    )
    return response.json()

# In Gemini prompt
result = scan_with_deployed_api(image_base64)
print(f"Scan result: {result}")
```

---

## 📊 Comparison & Pricing

| Feature | Cloud Run | Render | HF Spaces | Railway | Replit |
|---------|-----------|--------|-----------|---------|--------|
| Monthly Cost | Free | Free | Free | Free | Free |
| Always On | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| Setup Time | 10 min | 5 min | 5 min | 5 min | 3 min |
| Requests/month | 2M free | Unlimited | Unlimited | Limited | Limited |
| GitHub Integration | ✅ | ✅ | ✅ | ✅ | ✅ |
| Custom Domain | ✅ | ✅ | ❌ | ✅ | ❌ |
| CPU Limit | 1 vCPU | Unlimited | 2 vCPU | Limited | 0.5 vCPU |
| Memory | 512MB | 0.5GB | 2GB | 512MB | 512MB |

---

## 🚨 Important Notes

1. **Always-On vs Sleep**
   - Cloud Run & Render stay always-on
   - Replit & Railway may go to sleep after inactivity

2. **Rate Limits**
   - Cloud Run: 2M free requests/month
   - Others: Generous limits or unlimited

3. **Security**
   - Never commit API keys
   - Use environment variables
   - Use `.gitignore`

4. **Monitoring**
   - Cloud Run has built-in monitoring
   - Check logs in platform dashboard

5. **Custom Domain**
   - Cloud Run & Render support custom domains
   - Can add SSL certificate

---

## 🔄 Updating Your Deployment

### Cloud Run
```bash
gcloud run deploy qr-scanner --source .
```

### Render
- Auto-deploys on GitHub push
- Manual redeploy in dashboard

### HF Spaces
- Auto-deploys on git push
- Manual redeploy in dashboard

### Railway
- Auto-deploys on GitHub push

### Replit
- Auto-deploys on any change

---

## 📋 Deployment Checklist

- [ ] Choose platform (I recommend Cloud Run)
- [ ] Create account
- [ ] Configure deployment settings
- [ ] Deploy successfully
- [ ] Get deployment URL
- [ ] Test health endpoint: `/health`
- [ ] Test scan endpoint
- [ ] Share URL with others
- [ ] Monitor usage in dashboard

---

## 🆘 Troubleshooting

### "Port already in use"
```bash
# Cloud Run handles this automatically
# For local testing, use different port:
python api_server.py --port 8001
```

### "Image not found"
- Ensure image path is correct
- For uploads, use `/scan/upload` endpoint
- For base64, use `/scan/base64` endpoint

### "Deployment takes too long"
- Cloud Run: ~2 minutes
- Render: ~2 minutes
- HF Spaces: ~1 minute
- Be patient, it's worth it!

### "Service not responding"
- Check health endpoint: `/health`
- Check logs in platform dashboard
- Verify environment variables

---

## 🎉 Next Steps

1. Choose your platform (Cloud Run recommended)
2. Follow the setup guide
3. Deploy in 5-10 minutes
4. Share your URL
5. Use it with your Gemini/Claude apps!

## Support

- Cloud Run Docs: https://cloud.google.com/run/docs
- Render Docs: https://render.com/docs
- HF Spaces: https://huggingface.co/spaces
- Railway: https://railway.app/docs
- Replit: https://docs.replit.com
