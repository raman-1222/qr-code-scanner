"""
Example Lamatic.ai Flow Configuration for QR Code Scanner MCP

This is a JSON representation of what your Lamatic flow might look like.
You can use this as reference when building your flows in the Lamatic UI.
"""

# Example 1: Simple QR Code Scan and Analyze

{
  "id": "qr_scanner_basic",
  "name": "QR Code Scanner - Basic",
  "description": "Upload image and scan QR code",
  "nodes": [
    {
      "id": "trigger",
      "type": "trigger",
      "config": {
        "type": "manual"
      }
    },
    {
      "id": "file_upload",
      "type": "widget",
      "config": {
        "type": "file_upload",
        "accepts": ["image/*"]
      }
    },
    {
      "id": "mcp_scan",
      "type": "mcp",
      "config": {
        "server": "QR Code Scanner",
        "tool": "scan_qr_code_from_file",
        "parameters": {
          "image_path": "{{file_upload.output.path}}"
        }
      }
    },
    {
      "id": "output",
      "type": "text_output",
      "config": {
        "template": """
Scan Result:
- QR Found: {{mcp_scan.output.qr_found}}
- Scannable: {{mcp_scan.output.scannable}}
- Content: {{mcp_scan.output.qr_codes[0].content}}
- Message: {{mcp_scan.output.message}}
        """
      }
    }
  ],
  "edges": [
    { "from": "trigger", "to": "file_upload" },
    { "from": "file_upload", "to": "mcp_scan" },
    { "from": "mcp_scan", "to": "output" }
  ]
}


# Example 2: Scan with Conditional Processing

{
  "id": "qr_scanner_conditional",
  "name": "QR Code Scanner - Conditional",
  "description": "Scan QR and process based on result",
  "nodes": [
    {
      "id": "trigger",
      "type": "trigger",
      "config": { "type": "manual" }
    },
    {
      "id": "upload",
      "type": "widget",
      "config": { "type": "file_upload" }
    },
    {
      "id": "mcp_scan",
      "type": "mcp",
      "config": {
        "server": "QR Code Scanner",
        "tool": "scan_qr_code_from_file",
        "parameters": {
          "image_path": "{{upload.output.path}}"
        }
      }
    },
    {
      "id": "check_found",
      "type": "condition",
      "config": {
        "conditions": [
          {
            "path": "{{mcp_scan.output.qr_found}}",
            "operator": "equals",
            "value": true
          }
        ]
      }
    },
    {
      "id": "process_valid",
      "type": "text_generate",
      "config": {
        "prompt": "Analyze this QR code data: {{mcp_scan.output.qr_codes[0].content}}"
      }
    },
    {
      "id": "error_branch",
      "type": "text_output",
      "config": {
        "template": "No QR code found in image"
      }
    }
  ],
  "edges": [
    { "from": "trigger", "to": "upload" },
    { "from": "upload", "to": "mcp_scan" },
    { "from": "mcp_scan", "to": "check_found" },
    { "from": "check_found", "to": "process_valid", "condition": true },
    { "from": "check_found", "to": "error_branch", "condition": false }
  ]
}


# Example 3: Batch QR Code Processing

{
  "id": "qr_scanner_batch",
  "name": "QR Code Scanner - Batch",
  "description": "Process multiple QR codes",
  "nodes": [
    {
      "id": "trigger",
      "type": "trigger",
      "config": { "type": "manual" }
    },
    {
      "id": "files_input",
      "type": "variable",
      "config": {
        "type": "array",
        "defaultValue": []
      }
    },
    {
      "id": "loop_files",
      "type": "loop",
      "config": {
        "array": "{{files_input.output}}",
        "itemVariable": "currentFile"
      }
    },
    {
      "id": "mcp_scan_loop",
      "type": "mcp",
      "config": {
        "server": "QR Code Scanner",
        "tool": "scan_qr_code_from_file",
        "parameters": {
          "image_path": "{{currentFile.path}}"
        }
      }
    },
    {
      "id": "collect_results",
      "type": "variable",
      "config": {
        "type": "array",
        "operation": "append",
        "value": {
          "file": "{{currentFile.name}}",
          "qr_found": "{{mcp_scan_loop.output.qr_found}}",
          "content": "{{mcp_scan_loop.output.qr_codes[0].content}}"
        }
      }
    },
    {
      "id": "output_results",
      "type": "text_output",
      "config": {
        "template": "Processed {{collect_results.output.length}} files"
      }
    }
  ]
}


# Example 4: QR Code with AI Analysis

{
  "id": "qr_scanner_ai",
  "name": "QR Code Scanner - With AI Analysis",
  "description": "Scan QR and use AI to analyze",
  "nodes": [
    {
      "id": "upload",
      "type": "widget",
      "config": { "type": "file_upload" }
    },
    {
      "id": "mcp_scan",
      "type": "mcp",
      "config": {
        "server": "QR Code Scanner",
        "tool": "scan_qr_code_from_file",
        "parameters": {
          "image_path": "{{upload.output.path}}"
        }
      }
    },
    {
      "id": "ai_analyze",
      "type": "text_generate",
      "config": {
        "model": "gpt-4",
        "prompt": """
Analyze this QR code scan result:

QR Found: {{mcp_scan.output.qr_found}}
Scannable: {{mcp_scan.output.scannable}}
Content: {{mcp_scan.output.qr_codes[0].content}}

Please provide:
1. Is the QR code valid?
2. What type of data does it contain?
3. Any security concerns?
4. Suggested next action
        """
      }
    },
    {
      "id": "response",
      "type": "text_output",
      "config": {
        "template": "{{ai_analyze.output}}"
      }
    }
  ]
}


# Example 5: Database Integration

{
  "id": "qr_scanner_database",
  "name": "QR Code Scanner - With Database",
  "description": "Scan and store results",
  "nodes": [
    {
      "id": "upload",
      "type": "widget",
      "config": { "type": "file_upload" }
    },
    {
      "id": "mcp_scan",
      "type": "mcp",
      "config": {
        "server": "QR Code Scanner",
        "tool": "scan_qr_code_from_file",
        "parameters": {
          "image_path": "{{upload.output.path}}"
        }
      }
    },
    {
      "id": "store_db",
      "type": "database",
      "config": {
        "action": "insert",
        "table": "qr_scans",
        "data": {
          "image_path": "{{upload.output.name}}",
          "qr_found": "{{mcp_scan.output.qr_found}}",
          "scannable": "{{mcp_scan.output.scannable}}",
          "content": "{{mcp_scan.output.qr_codes[0].content}}",
          "timestamp": "{{now()}}",
          "raw_result": "{{mcp_scan.output}}"
        }
      }
    },
    {
      "id": "response",
      "type": "text_output",
      "config": {
        "template": "Scanned and stored successfully"
      }
    }
  ]
}


# Configuration Notes:

"""
Replace these values with your actual data:

1. Server Name: "QR Code Scanner" 
   - Must match the credential name in Lamatic MCP settings

2. Tool Names:
   - "scan_qr_code_from_file" - for file path scanning
   - "scan_qr_code_from_base64" - for base64 scanning

3. Variable References:
   - {{nodeId.output}} - access node output
   - {{nodeId.output.fieldName}} - access specific field

4. Available Output Fields:
   - success: boolean
   - qr_found: boolean
   - scannable: boolean
   - qr_count: number
   - qr_codes: array
   - qr_codes[0].content: string (actual QR data)
   - message: string
   - error: string (if failed)

5. Flow Variables:
   - {{now()}} - current timestamp
   - {{trigger.params}} - trigger parameters
   - {{env.VARIABLE_NAME}} - environment variables
"""
