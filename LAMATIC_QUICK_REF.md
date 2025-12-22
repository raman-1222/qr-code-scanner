# Lamatic.ai MCP Quick Reference

## 📋 Checklist

- [ ] Deploy MCP server to cloud (see QUICK_DEPLOY.md)
- [ ] Copy deployment URL
- [ ] Open Lamatic.ai studio
- [ ] Go to MCP/Tools → MCP
- [ ] Click "+ Add MCP"
- [ ] Configure:
  - Credential Name: `QR Code Scanner`
  - Host: `https://your-deployment-url`
  - Type: `http`
  - Headers: `{}` (empty)
- [ ] Click "Test & Save"
- [ ] Create new flow
- [ ] Add MCP Node
- [ ] Select "QR Code Scanner"
- [ ] Configure tool parameters
- [ ] Test flow
- [ ] Deploy

## 🔗 Configuration Template

```
Credential Name:  QR Code Scanner
Host:             https://qr-scanner-xxx.run.app
Type:             http
Headers:          {}
```

## 🛠️ MCP Node Configuration

**For File Scanning:**
```
Tool: scan_qr_code_from_file
Parameters:
  image_path: {{nodeOutput.filePath}}
```

**For Base64 Scanning:**
```
Tool: scan_qr_code_from_base64
Parameters:
  image_base64: {{nodeOutput.base64Data}}
```

## 📤 Output Variables

```javascript
// Access in other nodes as:
{{mcpNodeName.output}}

// Specific fields:
{{mcpNodeName.output.qr_found}}           // boolean
{{mcpNodeName.output.scannable}}          // boolean
{{mcpNodeName.output.qr_count}}           // number
{{mcpNodeName.output.qr_codes}}           // array
{{mcpNodeName.output.qr_codes[0].content}} // string
{{mcpNodeName.output.message}}            // string
```

## 🎯 Common Patterns

### Pattern 1: Simple Scan
```
Upload Node → MCP: Scan → Text Output
```

### Pattern 2: Conditional Processing
```
Upload → MCP: Scan → Condition Check (qr_found?) 
  ├─ True: Process data
  └─ False: Show error
```

### Pattern 3: Batch Processing
```
Loop (files) → MCP: Scan → Append results
```

### Pattern 4: AI Analysis
```
Upload → MCP: Scan → Text-Gen: Analyze → Output
```

## 🚀 Deployment Links

**Quick Deploy Guide**: See [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

**Free Deployment Options**:
- Google Cloud Run: https://cloud.google.com/run
- Render: https://render.com
- HF Spaces: https://huggingface.co/spaces

## 🔐 Optional: Add Authentication

If you want to secure your endpoint:

**1. Modify API server:**
```python
# api_server.py - Add to endpoints you want to secure

from fastapi import Header, HTTPException

async def verify_api_key(authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {os.getenv('API_KEY')}":
        raise HTTPException(status_code=401)
    return authorization
```

**2. Update Lamatic Headers:**
```json
{
  "Authorization": "Bearer your-secret-key"
}
```

## 📞 Support

- Lamatic Docs: https://lamatic.ai/docs/mcp-tools/mcp
- MCP Node Docs: https://lamatic.ai/docs/nodes/ai/mcp-node
- Slack Support: https://lamatic.ai/docs/slack

## 🎓 Learning Path

1. **Beginner**: Simple scan → output result
2. **Intermediate**: Conditional processing + Text-Gen
3. **Advanced**: Batch processing + Database integration
4. **Expert**: Custom auth + Rate limiting + Monitoring

---

**Remember**: Your MCP server URL is like `https://qr-scanner-abc123.run.app` - make sure it's deployed first!
