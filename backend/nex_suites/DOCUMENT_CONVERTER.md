# Document Converter with Roots Security

A secure document conversion system that converts PDFs and images (JPEG, PNG) to multiple formats (text, markdown, JSON) with OCR support, following the cli_root security patterns.

## Features

### 🔒 Roots Security
- **Controlled Access**: Only access files within explicitly granted root directories
- **Security Validation**: Every file operation checks `is_path_allowed()`
- **User Control**: Users specify which directories the app can access

### 📄 Document Conversion
- **Input Formats**: PDF, JPG, JPEG, PNG
- **Output Formats**:
  - **Text**: Plain text with structured formatting
  - **Markdown**: Tables and formatted sections
  - **JSON**: Structured data with metadata
- **OCR Support**: Automatic text extraction from images
- **Receipt/Invoice Parsing**: Intelligent field extraction

### 🔍 File Discovery
- **Find Documents**: Search for documents by pattern
- **Directory Browsing**: List files within allowed roots
- **Auto-Discovery**: Claude can find files without full paths

## Installation

Dependencies are already installed via:
```bash
uv add pdfplumber pillow pytesseract opencv-python
```

## Usage

### 1. Start with Roots

```bash
# Grant access to specific directories
python main.py --roots /Documents /Downloads

# With additional options
python main.py --roots /Documents /Downloads --model claude-3-opus --verbose
```

### 2. Available Commands in Chat

#### List Available Roots
```
"List my root directories"
"What directories can you access?"
```

#### Find Documents
```
"Find all PDF files"
"Search for invoices"
"Find receipt images"
"Look for *.pdf in Documents"
```

#### Convert Documents
```
"Convert /Documents/receipt.pdf to markdown"
"Extract text from the invoice image"
"Convert the document to JSON format"
"Save the conversion as /Documents/output.md"
```

#### Browse Directories
```
"List files in /Documents"
"Show me what's in the Downloads folder"
```

## Output Examples

### Text Format
```
RESIT RASMI     No. Resit : 2025E0004343673

PERKESO

Tarikh Masa          :     09/09/2025 09:03:48 PM
Tarikh Bayaran       :     09/09/2025
Kod Majikan          :     B3901000913X
Nama Majikan         :     ASIAJAYA TILING CONSTRUCTION SDN BHD
Jumlah Bayaran       :     RM28.80
```

### Markdown Format
```markdown
# RESIT RASMI

**No. Resit:** 2025E0004343673

## PERKESO

| Field | Value |
|-------|-------|
| **Tarikh Masa** | 09/09/2025 09:03:48 PM |
| **Nama Majikan** | ASIAJAYA TILING CONSTRUCTION SDN BHD |
| **Jumlah Bayaran** | RM28.80 |
```

### JSON Format
```json
{
  "pages": [{
    "page": 1,
    "text": "RESIT RASMI...",
    "md": "# RESIT RASMI\n\n**No. Resit:**...",
    "images": [{
      "name": "receipt.png",
      "width": 595,
      "height": 842
    }]
  }],
  "items": [
    {"type": "field", "key": "receipt_no", "value": "2025E0004343673"},
    {"type": "field", "key": "total_amount", "value": "RM28.80"}
  ]
}
```

## Architecture

### Module Structure
```
nex_suites/
├── core/
│   ├── roots_manager.py      # CLI argument parsing & validation
│   └── utils.py              # File URL conversion utilities
├── tools/
│   ├── document_converter.py # Core conversion logic
│   └── filesystem.py         # Roots security & file operations
├── mcp_server.py            # MCP tool registration (decorators only)
├── mcp_client.py            # Client with roots support
└── main.py                  # Entry point with roots initialization
```

### Security Flow
1. User provides roots via CLI: `--roots /Documents`
2. Client stores roots as `Root` objects
3. Server requests roots via `ctx.session.list_roots()`
4. Every file operation validates with `is_path_allowed()`
5. Access denied if path outside roots

### Conversion Pipeline
1. **Input Validation**: Check file exists and format supported
2. **Text Extraction**:
   - PDF: Use pdfplumber
   - Image: Use pytesseract with OpenCV preprocessing
3. **Data Parsing**: Extract structured fields (receipts, invoices)
4. **Format Output**: Convert to requested format (text/markdown/JSON)

## Testing

Run the test suite:
```bash
uv run python test_document_converter.py
```

Test with real files:
```bash
# Create test directory
mkdir -p /tmp/test_docs

# Copy some PDFs/images there
cp ~/Documents/*.pdf /tmp/test_docs/

# Run with test directory as root
python main.py --roots /tmp/test_docs

# In chat:
> Find all documents
> Convert the first PDF to markdown
```

## Security Considerations

1. **Never bypass `is_path_allowed()`** - All file operations must validate
2. **Resolve paths to absolute** - Prevent directory traversal attacks
3. **Validate before access** - Check exists and is within roots
4. **Clear error messages** - Tell user which roots are allowed

## Troubleshooting

### OCR Not Working
- Install tesseract: `brew install tesseract` (Mac) or `apt-get install tesseract-ocr` (Linux)
- Check language data: `tesseract --list-langs`

### Permission Denied
- Ensure directories exist and are readable
- Check roots are specified correctly
- Use `--verbose` flag for detailed logging

### No Documents Found
- Verify roots contain the files
- Check file extensions are supported
- Use glob patterns: `*.pdf`, `receipt*`

## Future Enhancements

- [ ] Add support for Word documents (.docx)
- [ ] Implement batch conversion
- [ ] Add OCR confidence scores
- [ ] Support for multi-language OCR
- [ ] Table extraction improvements
- [ ] Add Excel output format

## Credits

This implementation follows the security patterns from cli_root, adapting them for document processing while maintaining the same robust access control model.