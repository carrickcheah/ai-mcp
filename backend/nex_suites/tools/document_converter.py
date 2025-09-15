"""
Document conversion module for PDF and image files.
Supports conversion to text, markdown, and JSON formats.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Literal, Optional, List
import pdfplumber
from PIL import Image
import pytesseract
import cv2
import numpy as np


class DocumentConverter:
    """Handles document conversion operations to multiple formats."""

    SUPPORTED_INPUT_FORMATS = ["pdf", "jpg", "jpeg", "png"]
    OUTPUT_FORMATS = ["text", "markdown", "json"]

    @classmethod
    def validate_input(cls, input_path: str) -> Path:
        """Validate the input file exists and is supported."""
        input_file = Path(input_path)

        if not input_file.exists():
            raise ValueError(f"Input file not found: {input_path}")

        extension = input_file.suffix.lower()[1:]
        if extension not in cls.SUPPORTED_INPUT_FORMATS:
            raise ValueError(f"Unsupported format '{extension}'. Supported: {cls.SUPPORTED_INPUT_FORMATS}")

        return input_file

    @classmethod
    async def convert(cls, input_path: str, output_format: Literal["text", "markdown", "json"]) -> str:
        """Convert document to specified format."""
        input_file = cls.validate_input(input_path)

        # Extract raw data based on file type
        if input_file.suffix.lower() == ".pdf":
            raw_data = cls.extract_from_pdf(input_file)
        else:
            raw_data = cls.extract_from_image(input_file)

        # Format output based on requested format
        if output_format == "text":
            return cls.format_as_text(raw_data)
        elif output_format == "markdown":
            return cls.format_as_markdown(raw_data)
        elif output_format == "json":
            return cls.format_as_json(raw_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    @classmethod
    def extract_from_pdf(cls, pdf_path: Path) -> Dict[str, Any]:
        """Extract structured data from PDF."""
        pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                tables = page.extract_tables() or []

                # Clean up text
                text = cls.clean_text(text)

                pages.append({
                    "page": page_num,
                    "text": text,
                    "tables": tables,
                    "width": page.width,
                    "height": page.height
                })

        # Try to parse structured data from the text
        full_text = "\n".join(p["text"] for p in pages)
        parsed = cls.parse_receipt_data(full_text)

        return {
            "pages": pages,
            "type": "pdf",
            "parsed": parsed,
            "filename": pdf_path.name
        }

    @classmethod
    def extract_from_image(cls, image_path: Path) -> Dict[str, Any]:
        """Extract text from image using OCR."""
        # Load and preprocess image for better OCR
        image = Image.open(image_path)

        # Convert to OpenCV format for preprocessing
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Preprocess for better OCR accuracy
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.medianBlur(thresh, 1)

        # Convert back to PIL for pytesseract
        processed_image = Image.fromarray(denoised)

        # Extract text with different configurations
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_image, config=custom_config)

        # Clean up text
        text = cls.clean_text(text)

        # Parse structured data from text
        parsed = cls.parse_receipt_data(text)

        return {
            "raw_text": text,
            "parsed": parsed,
            "type": "image",
            "filename": image_path.name,
            "images": [{
                "name": image_path.name,
                "width": image.width,
                "height": image.height,
                "original_width": image.width,
                "original_height": image.height
            }]
        }

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix common OCR issues
        text = text.replace(' :', ':')
        text = text.replace(' ,', ',')
        # Restore line breaks for structure
        text = re.sub(r'([:\.])\s+', r'\1\n', text)
        return text.strip()

    @classmethod
    def parse_receipt_data(cls, text: str) -> Dict[str, Any]:
        """Parse receipt/invoice data into structured format."""
        data = {}
        lines = text.split('\n')

        # Common patterns for receipts/invoices
        patterns = {
            "receipt_no": [
                r"No\.?\s*Resit\s*[:]\s*(\S+)",
                r"Receipt\s*No\.?\s*[:]\s*(\S+)",
                r"Invoice\s*No\.?\s*[:]\s*(\S+)"
            ],
            "datetime": [
                r"Tarikh\s*Masa\s*[:]\s*(.+?)(?:\n|$)",
                r"Date\s*Time\s*[:]\s*(.+?)(?:\n|$)",
                r"Date\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "payment_date": [
                r"Tarikh\s*Bayaran\s*[:]\s*(.+?)(?:\n|$)",
                r"Payment\s*Date\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "payment_type": [
                r"Jenis\s*Bayaran\s*[:]\s*(.+?)(?:\n|$)",
                r"Payment\s*Type\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "company_code": [
                r"Kod\s*Majikan\s*[:]\s*(\S+)",
                r"Company\s*Code\s*[:]\s*(\S+)",
                r"Employer\s*Code\s*[:]\s*(\S+)"
            ],
            "company_name": [
                r"Nama\s*Majikan\s*[:]\s*(.+?)(?:\n|$)",
                r"Company\s*Name\s*[:]\s*(.+?)(?:\n|$)",
                r"Employer\s*Name\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "payment_method": [
                r"Kaedah\s*Bayaran\s*[:]\s*(.+?)(?:\n|$)",
                r"Payment\s*Method\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "transaction_id": [
                r"FPX\s*Transaksi\s*ID\s*[:]\s*(\S+)",
                r"Transaction\s*ID\s*[:]\s*(\S+)",
                r"Reference\s*No\.?\s*[:]\s*(\S+)"
            ],
            "bank": [
                r"Bank\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "total_amount": [
                r"Jumlah\s*Bayaran\s*[:]\s*(.+?)(?:\n|$)",
                r"Total\s*Amount\s*[:]\s*(.+?)(?:\n|$)",
                r"Total\s*[:]\s*(.+?)(?:\n|$)"
            ],
            "notes": [
                r"Catatan\s*[:]\s*(.+?)(?:\n|$)",
                r"Notes\s*[:]\s*(.+?)(?:\n|$)",
                r"Remarks\s*[:]\s*(.+?)(?:\n|$)"
            ]
        }

        # Try to extract each field
        full_text = '\n'.join(lines)
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    data[field] = match.group(1).strip()
                    break

        # Look for payment items (numbered list)
        payment_items = []
        for line in lines:
            item_match = re.match(r"(\d+)\.\s*(.+)", line)
            if item_match:
                payment_items.append({
                    "number": item_match.group(1),
                    "description": item_match.group(2).strip()
                })

        if payment_items:
            data["payment_items"] = payment_items

        # Extract PERKESO specific data if present
        if "PERKESO" in full_text:
            data["organization"] = "PERKESO"

        # Extract title if present
        if "RESIT RASMI" in full_text:
            data["document_type"] = "RESIT RASMI"

        return data

    @classmethod
    def format_as_text(cls, data: Dict[str, Any]) -> str:
        """Format as plain text (like Image #1)."""
        output = []

        if data.get("parsed"):
            parsed = data["parsed"]

            # Document header
            if parsed.get("document_type"):
                header = parsed["document_type"]
                if parsed.get("receipt_no"):
                    header += f"     No. Resit : {parsed['receipt_no']}"
                output.append(header)
                output.append("")

            # Organization
            if parsed.get("organization"):
                output.append(parsed["organization"])
                output.append("")

            # Format fields with consistent spacing
            field_mappings = [
                ("Tarikh Masa", "datetime"),
                ("Tarikh Bayaran", "payment_date"),
                ("Jenis Bayaran", "payment_type"),
                ("Kod Majikan", "company_code"),
                ("Nama Majikan", "company_name"),
                ("Kaedah Bayaran", "payment_method"),
                ("FPX Transaksi ID", "transaction_id"),
                ("Bank", "bank"),
                ("Jumlah Bayaran", "total_amount"),
                ("Catatan", "notes")
            ]

            for label, field_key in field_mappings:
                if field_key in parsed:
                    value = parsed[field_key]
                    output.append(f"{label:<20} :     {value}")

            # Add payment items if present
            if "payment_items" in parsed:
                output.append("")
                for item in parsed["payment_items"]:
                    output.append(f"{item['number']}. {item['description']}")

        else:
            # Fallback to raw text
            if data["type"] == "pdf":
                for page in data.get("pages", []):
                    output.append(f"Page {page['page']}:")
                    output.append(page.get("text", ""))
                    output.append("")
            else:
                output.append(data.get("raw_text", ""))

        # Add footer note if present
        if "Resit ini adalah cetakan komputer" in str(data.get("raw_text", "")):
            output.append("")
            output.append('"Resit ini adalah cetakan komputer dan tandatangan tidak diperlukan."')

        return "\n".join(output)

    @classmethod
    def format_as_markdown(cls, data: Dict[str, Any]) -> str:
        """Format as markdown with tables."""
        output = []

        if data.get("parsed"):
            parsed = data["parsed"]

            # Document header
            if parsed.get("document_type"):
                output.append(f"# {parsed['document_type']}")
                output.append("")

            if parsed.get("receipt_no"):
                output.append(f"**No. Resit:** {parsed['receipt_no']}")
                output.append("")

            # Organization section
            if parsed.get("organization"):
                output.append(f"## {parsed['organization']}")
                output.append("")

            # Create markdown table for main fields
            output.append("| Field | Value |")
            output.append("|-------|-------|")

            field_mappings = [
                ("Tarikh Masa", "datetime"),
                ("Tarikh Bayaran", "payment_date"),
                ("Kod Majikan", "company_code"),
                ("Nama Majikan", "company_name"),
                ("Kaedah Bayaran", "payment_method"),
                ("FPX Transaksi ID", "transaction_id"),
                ("Bank", "bank"),
                ("Jumlah Bayaran", "total_amount"),
                ("Catatan", "notes")
            ]

            for label, field_key in field_mappings:
                if field_key in parsed:
                    value = parsed[field_key]
                    output.append(f"| **{label}** | {value} |")

            # Add payment items section if present
            if "payment_items" in parsed:
                output.append("")
                output.append("### Jenis Bayaran")
                output.append("")
                for item in parsed["payment_items"]:
                    output.append(f"{item['number']}. {item['description']}")

        else:
            # Fallback to raw content
            output.append("# Document Content")
            output.append("")
            if data["type"] == "pdf":
                for page in data.get("pages", []):
                    output.append(f"## Page {page['page']}")
                    output.append("")
                    output.append("```")
                    output.append(page.get("text", ""))
                    output.append("```")
                    output.append("")
            else:
                output.append("```")
                output.append(data.get("raw_text", ""))
                output.append("```")

        # Add metadata section
        output.append("")
        output.append("---")
        output.append("*Generated from: " + data.get("filename", "unknown") + "*")

        return "\n".join(output)

    @classmethod
    def format_as_json(cls, data: Dict[str, Any]) -> str:
        """Format as JSON (like Image #2)."""
        json_output = {
            "pages": [],
            "charts": [],
            "items": []
        }

        if data["type"] == "pdf":
            # Structure for PDF
            for page in data.get("pages", []):
                page_data = {
                    "page": page["page"],
                    "text": page["text"],
                    "md": "",  # Could be populated with markdown version
                    "images": []
                }

                if page.get("tables"):
                    page_data["tables"] = page["tables"]

                json_output["pages"].append(page_data)

        elif data["type"] == "image":
            # Structure for image OCR results
            page_data = {
                "page": 1,
                "text": data.get("raw_text", ""),
                "md": cls.format_as_markdown(data),  # Include markdown version
                "images": data.get("images", [])
            }

            # Add OCR confidence if available
            if "ocr_confidence" in data:
                page_data["confidence"] = data["ocr_confidence"]

            json_output["pages"].append(page_data)

        # Add parsed items as structured data
        if data.get("parsed"):
            for key, value in data["parsed"].items():
                if key == "payment_items":
                    # Add payment items as separate items
                    for item in value:
                        json_output["items"].append({
                            "type": "payment_item",
                            "number": item["number"],
                            "description": item["description"]
                        })
                else:
                    # Add regular fields
                    json_output["items"].append({
                        "type": "field",
                        "key": key,
                        "value": value,
                        "lvl": 1
                    })

        # Add metadata
        json_output["metadata"] = {
            "filename": data.get("filename", ""),
            "type": data.get("type", ""),
            "processed_at": None  # Could add timestamp
        }

        return json.dumps(json_output, indent=2, ensure_ascii=False)