# Lamatic.ai MCP Integration Guide

Complete guide to connect your QR Code Scanner MCP to Lamatic.ai

## 📋 Prerequisites

1. ✅ Deployed QR Scanner (Cloud Run, Render, etc.) - see [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
2. ✅ Lamatic.ai account - https://lamatic.ai/
3. ✅ Your MCP server URL (e.g., `https://qr-scanner-xxx.run.app`)

## 🚀 Step 1: Deploy Your MCP Server

First, deploy to a free platform (if not already done):

```bash
# Using Google Cloud Run (Recommended)
gcloud run deploy qr-scanner \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000

# Get your URL
gcloud run services describe qr-scanner --region us-central1 --format='value(status.url)'
```

Save your deployed URL: `https://qr-scanner-xxx.run.app`

## 🔗 Step 2: Connect to Lamatic.ai

### Open Lamatic Studio

1. Go to **https://lamatic.ai/**
2. Sign in to your account
3. Click on your project or create a new one

### Add MCP Server

1. Navigate to **MCP/Tools** → **MCP** (left sidebar)
2. Click **+ Add MCP**
3. Fill in the configuration:

```
Credential Name:  QR Code Scanner
Host:             https://qr-scanner-xxx.run.app
Type:             http
Headers:          {} (leave empty for public access)
```

4. Click **Test & Save**

## ✅ Step 3: Verify Connection

The "Test & Save" button will verify the connection:

✓ **Success** - Server is reachable
✗ **Failed** - Check your URL is correct and server is running

## 🛠️ Step 4: Use in Flows

### Add MCP Node to Your Flow

1. In your flow editor, click **+ Add Node**
2. Search for **MCP** 
3. Select **MCP Node**
4. Configure:
   - **MCP Server**: Select "QR Code Scanner"
   - **Tool/Resource**: Select from available endpoints
   - **Parameters**: Configure as needed

### Available MCP Operations

Your QR scanner exposes these tools:

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `scan_qr_code_from_file` | Scan from file path | `image_path` |
| `scan_qr_code_from_base64` | Scan base64 image | `image_base64` |

## 📝 Workflow Examples

### Example 1: Simple QR Code Scan

**Flow:**
```
Upload File → MCP: Scan QR Code → Text Generation (analyze result)
```

**MCP Node Config:**
```
Server: QR Code Scanner
Tool: scan_qr_code_from_file
Params:
  - image_path: {{uploadedFile.path}}
```

**Output Variables:**
```
{{qrResult.qr_found}}           // true/false
{{qrResult.scannable}}          // true/false
{{qrResult.qr_codes[0].content}} // QR data
```

### Example 2: Batch QR Code Processing

**Flow:**
```
Loop through images → Upload → Scan with MCP → Store results
```

**MCP Node Config:**
```
Server: QR Code Scanner
Tool: scan_qr_code_from_file
Params:
  - image_path: {{loopItem.filepath}}
```

**Loop Node Config:**
```
Array: {{inputFiles}}
Item variable: loopItem
```

### Example 3: QR Code with AI Analysis

**Flow:**
```
Upload Image → MCP: Scan → Generate Text: Analyze results
```

**Text-Gen Node:**
```
Prompt: "Analyze this QR scan result: {{scanResult}}. 
Is it valid? What does it contain? Any issues?"
```

### Example 4: Database Integration

**Flow:**
```
Upload → Scan with MCP → Store in Database → Respond to user
```

**Database Node Config:**
```
Action: INSERT
Table: qr_scans
Data:
  - image_path: {{uploadedFile.name}}
  - qr_found: {{scanResult.qr_found}}
  - content: {{scanResult.qr_codes[0].content}}
  - timestamp: {{now()}}
```

## 🔐 Advanced Configuration

### Add Authentication (Optional)

If you want to secure your MCP server:

**1. Update your API server:**
```python
# In api_server.py
from fastapi import Header, HTTPException

@app.post("/scan/upload")
async def scan_upload(file: UploadFile = File(...), 
                     authorization: str = Header(None)):
    if authorization != f"Bearer {os.getenv('API_KEY')}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    # ... rest of code
```

**2. Redeploy:**
```bash
gcloud run deploy qr-scanner --source .
```

**3. Update Lamatic MCP Config:**
```
Credential Name:  QR Code Scanner (Secured)
Host:             https://qr-scanner-xxx.run.app
Type:             http
Headers:          {"Authorization": "Bearer your-secret-key"}
```

### Custom Headers

Add headers for rate limiting, API keys, or custom auth:

```json
{
  "Authorization": "Bearer your-api-key",
  "Content-Type": "application/json",
  "X-Custom-Header": "value"
}
```

## 🎯 Best Practices in Lamatic

### 1. Error Handling

Use **Condition Nodes** to handle scan results:

```
MCP Scan ↓
├─ If qr_found == true → Process result
├─ If scannable == false → Alert user
└─ If error → Log error
```

### 2. Variables for Reusability

Store your server URL as a variable:

```
Variables → New Variable
Name: QR_SCANNER_URL
Value: https://qr-scanner-xxx.run.app
```

Then in MCP Node:
```
Host: {{QR_SCANNER_URL}}
```

### 3. Response Mapping

Map MCP responses to use in other nodes:

```
Output from MCP:
{
  "success": true,
  "qr_found": true,
  "scannable": true,
  "qr_codes": [
    {
      "content": "https://example.com",
      "valid": true
    }
  ]
}

Use as:
- {{scanResult.qr_codes[0].content}} in text nodes
- {{scanResult.qr_found}} in conditions
```

### 4. Batch Processing

Use Loop Node with MCP:

```
Loop Node Config:
- Array: {{files}}
- Item variable: currentFile

Inside Loop:
- MCP Node → Scan currentFile
- Data Node → Append to results
```

## 📊 Real-World Use Cases

### Use Case 1: E-commerce Product Verification
```
Customer uploads product image
  ↓
MCP: Scan QR code
  ↓
Generate Text: Verify authenticity
  ↓
Send email: Authenticity report
```

### Use Case 2: Inventory Management
```
Warehouse staff uploads label
  ↓
MCP: Extract QR data
  ↓
API: Update inventory
  ↓
Slack: Send notification
```

### Use Case 3: Document Processing
```
Upload batch of documents
  ↓
Loop: Process each document
  ↓
MCP: Extract QR from each
  ↓
Database: Store results
```

### Use Case 4: Quality Control
```
Manufacturing: Take product photo
  ↓
MCP: Scan QR
  ↓
AI: Analyze quality
  ↓
Decision: Pass/Fail
```

## 🐛 Troubleshooting

### Issue: "Connection Failed"

**Solution:**
1. Check your deployed URL is correct
2. Test manually:
   ```bash
   curl https://qr-scanner-xxx.run.app/health
   ```
3. Verify server is running:
   ```bash
   gcloud run describe qr-scanner --region us-central1
   ```

### Issue: "Authentication Error"

**Solution:**
1. If using headers, verify they're correct:
   ```json
   {"Authorization": "Bearer YOUR-ACTUAL-KEY"}
   ```
2. Check API key hasn't expired
3. Verify header format in Lamatic

### Issue: "Timeout"

**Solution:**
1. Image might be too large - try smaller image
2. MCP server might be sleeping - redeploy:
   ```bash
   gcloud run deploy qr-scanner --source .
   ```
3. Increase timeout in Lamatic flow settings

### Issue: "QR Not Detected"

**Solution:**
1. Ensure QR code is visible and clear
2. Good lighting and contrast needed
3. Image resolution should be at least 100x100px
4. QR code should be at least 50x50px

## 📈 Performance Tips

1. **Cache Results**: Store QR scan results to avoid re-scanning
2. **Batch Processing**: Process multiple images at once
3. **Lazy Load**: Only scan when necessary
4. **Monitor Logs**: Check Lamatic logs for performance

```
Flow Config → Logs → Filter by MCP Node
```

## 🔄 Updating Your MCP Server

When you update the server code:

```bash
# Make changes
# Redeploy
gcloud run deploy qr-scanner --source .

# Lamatic uses the URL, so no reconfiguration needed!
```

## 📚 Lamatic Docs

- **MCP Documentation**: https://lamatic.ai/docs/mcp-tools/mcp
- **MCP Node**: https://lamatic.ai/docs/nodes/ai/mcp-node
- **Text-Gen Node**: https://lamatic.ai/docs/nodes/ai/generate-text-node
- **Flow Variables**: https://lamatic.ai/docs/flows/variables

## 🎓 Recommended Next Steps

1. ✅ Deploy MCP server
2. ✅ Connect to Lamatic
3. ✅ Create simple test flow
4. ✅ Add Text-Gen node for analysis
5. ✅ Build production flow
6. ✅ Test with real images
7. ✅ Deploy to production
8. ✅ Monitor and optimize

## 💡 Tips & Tricks

### Quick Test

Create a simple flow:
```
Manual Trigger → MCP: Scan → Return output
```

Then test by manually triggering with an image URL.

### Share Flows

Once working, share your flow template with others:
- Right-click flow → Share
- Generate public link
- Share in docs/tutorials

### Integration with Text-Gen

Combine with LLM for intelligent analysis:

```
Input: Image file
  ↓
MCP: Scan QR
  ↓
Text-Gen: "Analyze this QR code data: {{qrData}}"
  ↓
Output: AI analysis
```

## 🚨 Rate Limiting

If using free tier, be aware of limits:

- **Cloud Run**: 2M requests/month
- **Render**: ~75 million requests/month
- **HF Spaces**: Unlimited

Monitor usage in your deployment platform dashboard.

## ❓ FAQ

**Q: Can I use my local MCP server?**
A: Yes, if your machine is publicly accessible. Better to use cloud deployment.

**Q: Do I need to authenticate?**
A: Only if you add custom headers. Public access works fine.

**Q: What image formats are supported?**
A: PNG, JPG, BMP, and other common formats OpenCV supports.

**Q: How large can images be?**
A: Max depends on your deployment platform (typically 512MB per request).

**Q: Can I batch process?**
A: Yes! Use Loop Node to process multiple images.

**Q: Is my data stored?**
A: MCP server doesn't store images. Lamatic.ai stores flow logs per their policy.

## 🆘 Support

- **Lamatic Support**: https://lamatic.ai/docs/slack
- **MCP Issues**: Check logs in Lamatic flow debugging
- **Server Issues**: Check Cloud Run logs
  ```bash
  gcloud run logs read qr-scanner --limit 50
  ```

---

Now you have a fully integrated QR code scanner in Lamatic.ai! 🎉

Next: Create your first flow and start scanning QR codes!
