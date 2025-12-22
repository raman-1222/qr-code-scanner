# Quick Start: Deploy & Use Your QR Scanner

Get your QR scanner online in **5 minutes** for FREE.

## 🚀 Step 1: Choose Platform

Pick one (I recommend **Google Cloud Run**):

```
✅ Google Cloud Run    - Best (always-on, free tier)
✅ Render              - Easy (simple setup)
✅ HuggingFace Spaces  - Great for ML projects
✅ Railway             - Quick testing
✅ Replit              - Simplest
```

## 📋 Step 2: Deploy to Cloud Run (Easiest)

### Install Google Cloud CLI
```bash
# Windows
choco install google-cloud-sdk

# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### Deploy
```bash
# Initialize
gcloud init

# Deploy
gcloud run deploy qr-scanner \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### Get Your URL
```bash
gcloud run services describe qr-scanner --region us-central1 --format='value(status.url)'
```

**That's it!** You now have a public URL like: `https://qr-scanner-xxx.run.app`

---

## 🔗 Step 3: Use Your Scanner

### Option A: Use Python Client

```python
from qr_client import QRScannerClient

# Your deployed URL
API_URL = "https://qr-scanner-xxx.run.app"
client = QRScannerClient(API_URL)

# Scan a file
result = client.scan_upload("path/to/label.jpg")
print(result)

# Batch scan
results = client.batch_scan(["label1.jpg", "label2.jpg", "label3.jpg"])
print(results)
```

### Option B: Use cURL

```bash
API_URL="https://qr-scanner-xxx.run.app"

# Health check
curl $API_URL/health

# Upload and scan
curl -X POST -F "file=@label.jpg" $API_URL/scan/upload

# Base64 scan
curl -X POST $API_URL/scan/base64 \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"..."}'
```

### Option C: Use with Gemini

```python
import requests
import base64
import google.generativeai as genai

API_URL = "https://qr-scanner-xxx.run.app"

def scan_qr(image_path):
    """Call deployed QR scanner"""
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_URL}/scan/upload", files=files)
    return response.json()

# Use in Gemini request
genai.configure(api_key="YOUR_GEMINI_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")

result = scan_qr("product-label.jpg")
response = model.generate_content(f"""
Check this QR code scan result: {result}
Is it valid? What data does it contain?
""")

print(response.text)
```

### Option D: Use with JavaScript

```javascript
const API_URL = "https://qr-scanner-xxx.run.app";

// Upload and scan
async function scanQRCode(file) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${API_URL}/scan/upload`, {
    method: "POST",
    body: formData
  });
  
  return await response.json();
}

// Example: File input handler
document.getElementById("fileInput").addEventListener("change", async (e) => {
  const result = await scanQRCode(e.target.files[0]);
  console.log(result);
});
```

---

## 📊 API Endpoints

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/health` | GET | Check if service is running |
| `/scan/file` | GET | Scan from file path (if accessible) |
| `/scan/upload` | POST | Upload image and scan |
| `/scan/base64` | POST | Scan base64 encoded image |
| `/scan/batch` | POST | Scan multiple images |

---

## 📝 Usage Examples

### Example 1: Batch Process Labels
```python
from qr_client import QRScannerClient
import os

API_URL = "https://qr-scanner-xxx.run.app"
client = QRScannerClient(API_URL)

# Process all JPGs in directory
images = [f for f in os.listdir("./labels") if f.endswith(".jpg")]
results = client.batch_scan([f"./labels/{img}" for img in images])

# Print results
for result in results["results"]:
    print(f"{result['name']}: {'✓ Scannable' if result['result']['scannable'] else '✗ Not scannable'}")
```

### Example 2: Integration with Database
```python
import requests
import json
from datetime import datetime

API_URL = "https://qr-scanner-xxx.run.app"

def log_qr_scan(image_path, database):
    """Scan and log to database"""
    
    # Scan
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_URL}/scan/upload", files=files)
    
    result = response.json()
    
    # Log to database
    entry = {
        "timestamp": datetime.now().isoformat(),
        "image": image_path,
        "qr_found": result.get("qr_found"),
        "scannable": result.get("scannable"),
        "content": result.get("qr_codes", [{}])[0].get("content") if result.get("qr_found") else None
    }
    
    # Save to database
    database.insert_one(entry)
    return entry
```

### Example 3: Real-time Web Dashboard
```html
<!DOCTYPE html>
<html>
<head>
    <title>QR Scanner Dashboard</title>
</head>
<body>
    <h1>QR Code Scanner</h1>
    <input type="file" id="fileInput" accept="image/*">
    <div id="result"></div>

    <script>
        const API_URL = "https://qr-scanner-xxx.run.app";
        
        document.getElementById("fileInput").addEventListener("change", async (e) => {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append("file", file);
            
            const response = await fetch(`${API_URL}/scan/upload`, {
                method: "POST",
                body: formData
            });
            
            const result = await response.json();
            
            document.getElementById("result").innerHTML = `
                <h2>Result:</h2>
                <pre>${JSON.stringify(result, null, 2)}</pre>
            `;
        });
    </script>
</body>
</html>
```

---

## 🔐 Security Tips

1. **Never hardcode API URLs** - Use environment variables
2. **Rate limiting** - Cloud Run has free tier limits
3. **Authentication** - Add API key if needed:
   ```python
   # In api_server.py
   @app.get("/scan/upload")
   async def scan_upload(file: UploadFile, api_key: str = Header(None)):
       if api_key != os.getenv("API_KEY"):
           raise HTTPException(status_code=401, detail="Invalid API key")
       # ... rest of code
   ```

---

## 📈 Monitoring & Scaling

### Cloud Run Monitoring
```bash
# View logs
gcloud run logs read qr-scanner --limit 50

# View metrics
gcloud run describe qr-scanner --region us-central1

# Update resources
gcloud run deploy qr-scanner \
  --memory 1Gi \
  --cpu 2 \
  --concurrency 100
```

---

## 🆘 Troubleshooting

### "Service unavailable"
- Check Cloud Run dashboard for errors
- Verify API URL is correct
- Try `/health` endpoint

### "Request timeout"
- Increase timeout in client
- Image might be too large
- Try uploading smaller image

### "File not found"
- Use `/scan/upload` instead of `/scan/file`
- Or provide full path to `/scan/file`

---

## 💰 Cost

**Cloud Run Free Tier:**
- 2 million requests/month ✅
- 360,000 GB-seconds/month ✅
- Outbound traffic included ✅

**After free tier:**
- $0.00002400 per request
- $0.00001667 per GB-second
- Usually <$1/month for hobby projects

---

## 📚 Learn More

- [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) - Detailed guides for all platforms
- [API Documentation](README.md#api-reference) - Full API reference
- [Cloud Run Docs](https://cloud.google.com/run/docs) - Official docs

---

## ✅ Checklist

- [ ] Choose platform
- [ ] Deploy
- [ ] Get URL
- [ ] Test health endpoint
- [ ] Test scan endpoint
- [ ] Integrate with your app
- [ ] Share with others
- [ ] Monitor usage

That's it! You now have a public QR scanner API! 🎉
