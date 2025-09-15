# How to Run Document Converter

## Quick Start

### 1. Open Terminal and Navigate to Project
```bash
cd /Users/carrickcheah/Project/mcp_root/nex3_ai/backend/nex_suites
```

### 2. Run with Your Actual Directories
```bash
# Using your real paths
uv run python main.py --roots /Users/carrickcheah/Downloads /Users/carrickcheah/Documents /tmp

# Or with just Downloads
uv run python main.py --roots /Users/carrickcheah/Downloads
```

### 3. Example Commands to Try in Chat

Once the app starts and you see the `>` prompt, try these commands:

#### Check Available Roots
```
list my root directories
```

#### Browse Directories
```
show files in /Users/carrickcheah/Downloads
```

#### Find Documents
```
find all PDF files
find all images
find receipt
```

#### Convert Documents

If you have a PDF in Downloads:
```
convert /Users/carrickcheah/Downloads/document.pdf to markdown
```

If you have an image:
```
convert /Users/carrickcheah/Downloads/receipt.jpg to text
convert /Users/carrickcheah/Downloads/invoice.png to json
```

## Test File Creation

If you don't have test files, create some:

### 1. Create a Test Text File
```bash
echo "RECEIPT #12345
Date: 2024-01-15
Amount: $99.99
Company: Test Corp" > /Users/carrickcheah/Downloads/test_receipt.txt
```

### 2. Save an Image as Test
Save any receipt or invoice image to `/Users/carrickcheah/Downloads/` as `test_receipt.jpg` or `test_receipt.png`

### 3. Test Conversion
```
convert /Users/carrickcheah/Downloads/test_receipt.txt to markdown
```

## Expected Output Examples

### Markdown Format
```markdown
# RECEIPT

**Receipt No:** 12345

| Field | Value |
|-------|-------|
| **Date** | 2024-01-15 |
| **Amount** | $99.99 |
| **Company** | Test Corp |
```

### JSON Format
```json
{
  "pages": [{
    "page": 1,
    "text": "RECEIPT #12345...",
    "items": [
      {"type": "field", "key": "receipt_no", "value": "12345"},
      {"type": "field", "key": "amount", "value": "$99.99"}
    ]
  }]
}
```

## Troubleshooting

### If you get "Access denied"
- Make sure the file is in one of your root directories
- Use full absolute paths starting with `/Users/carrickcheah/`

### If OCR doesn't work on images
- Install tesseract first:
  ```bash
  brew install tesseract
  ```

### If you can't find files
- Make sure they exist:
  ```bash
  ls -la /Users/carrickcheah/Downloads/*.pdf
  ls -la /Users/carrickcheah/Downloads/*.jpg
  ```

## Security Note

The app will ONLY access files in the directories you specify with `--roots`. It cannot access:
- System files in `/etc`, `/usr`, etc.
- Other users' home directories
- Any directory not explicitly granted

This is by design for security!