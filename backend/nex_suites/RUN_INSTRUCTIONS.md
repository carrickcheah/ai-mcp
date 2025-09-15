# How to Run Document Converter

## Quick Start (NEW - No Configuration Needed!)

### 1. Open Terminal and Navigate to Project
```bash
cd /Users/carrickcheah/Project/mcp_root/nex3_ai/backend/nex_suites
```

### 2. Run Without Any Arguments (Uses Smart Defaults)
```bash
uv run python main.py
```

The app will automatically use these directories if they exist:
- ~/Downloads
- ~/Documents
- ~/Desktop
- /tmp

### 3. Run with Custom Directories (Optional)
```bash
# Using your specific paths
uv run python main.py --roots /Users/carrickcheah/Downloads /Users/carrickcheah/Documents /tmp

# Or with just Downloads
uv run python main.py --roots /Users/carrickcheah/Downloads
```

## Example Commands to Try in Chat

Once the app starts and you see the `>` prompt, try these commands:

### Check Available Roots
```
list my root directories
```

### Browse Directories
```
show files in Downloads
show files in ~/Downloads
```

### Find Documents
```
find all PDF files
find all images
find receipt
find invoice
```

### Convert Documents

#### If you have a PDF in Downloads:
```
convert receipt.pdf to markdown
convert invoice.pdf to text
convert document.pdf to json
```

#### If you have an image:
```
convert receipt.jpg to text
convert invoice.png to json
convert screenshot.png to markdown
```

#### With full path:
```
convert /Users/carrickcheah/Downloads/document.pdf to markdown
```

## Test File Creation

If you don't have test files, create some:

### 1. Create a Test Text File
```bash
echo "RECEIPT #12345
Date: 2024-01-15
Amount: $99.99
Company: Test Corp
Item: Office Supplies
Quantity: 2
Tax: $8.99
Total: $108.98" > ~/Downloads/test_receipt.txt
```

### 2. Create a Test Invoice
```bash
echo "INVOICE
Invoice No: SI25080001
Date: 2024-08-15
Customer: ABC Corporation

ITEMS:
1. Product A - $50.00 x 2 = $100.00
2. Product B - $75.00 x 1 = $75.00

Subtotal: $175.00
Tax (10%): $17.50
TOTAL: $192.50" > ~/Downloads/test_invoice.txt
```

### 3. Test Conversion
```
convert test_receipt.txt to markdown
convert test_invoice.txt to json
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
| **Item** | Office Supplies |
| **Quantity** | 2 |
| **Tax** | $8.99 |
| **Total** | $108.98 |

## Summary
This receipt from Test Corp dated 2024-01-15 shows a purchase of 2 office supplies items for $99.99 plus $8.99 tax, totaling $108.98.
```

### JSON Format
```json
{
  "pages": [{
    "page": 1,
    "text": "INVOICE...",
    "metadata": {
      "invoice_no": "SI25080001",
      "date": "2024-08-15",
      "customer": "ABC Corporation",
      "total": "$192.50"
    },
    "items": [
      {"description": "Product A", "price": "$50.00", "quantity": "2", "amount": "$100.00"},
      {"description": "Product B", "price": "$75.00", "quantity": "1", "amount": "$75.00"}
    ]
  }]
}
```

## Troubleshooting

### If you get "Access denied"
- The file must be in one of your root directories
- Without --roots, only ~/Downloads, ~/Documents, ~/Desktop, /tmp are accessible
- Use full absolute paths or relative paths from current directory

### If OCR doesn't work on images
Install tesseract first:
```bash
brew install tesseract
```

### If you can't find files
Check they exist:
```bash
ls -la ~/Downloads/*.pdf
ls -la ~/Downloads/*.jpg
ls -la ~/Downloads/*.png
```

### If the app doesn't start
Check dependencies:
```bash
uv sync
```

## What Changed with Smart Defaults?

**Before**: You HAD to specify --roots
```bash
uv run python main.py --roots /Users/carrickcheah/Downloads  # Required
```

**Now**: Works automatically!
```bash
uv run python main.py  # No arguments needed!
```

The app intelligently detects and uses:
- Your Downloads folder (most common for files to convert)
- Your Documents folder (for saved documents)
- Your Desktop (for screenshots and quick files)
- /tmp directory (for temporary conversions)

## Security Note

The app will ONLY access files in:
1. Directories you specify with `--roots` OR
2. Default safe directories (~/Downloads, ~/Documents, ~/Desktop, /tmp)

It cannot access:
- System files in `/etc`, `/usr`, etc.
- Other users' home directories
- Any directory not explicitly granted

This is by design for security!

## Advanced Usage

### Verbose Mode
```bash
uv run python main.py -v        # Show warnings
uv run python main.py -vv       # Show info
uv run python main.py -vvv      # Show debug
```

### Custom Model
```bash
uv run python main.py --model claude-3-5-sonnet-latest
```

### Multiple MCP Servers
```bash
uv run python main.py --servers another_server.py third_server.py
```