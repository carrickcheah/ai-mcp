from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.sales import get_sales

mcp = FastMCP("Nex Sales MCP", log_level="ERROR")


# Register the get_sales tool
@mcp.tool(
    name="get_sales",
    description="Get sales/purchase order data for a specified time period"
)
async def get_sales_tool(
    period: str = Field(description="Time period (e.g., 'AUG', 'last 3 months', '2024', '6 months')")
) -> str:
    """
    Get sales/purchase order data for a specified period.
    Returns formatted report with transaction details and summary.
    """
    return await get_sales(period)


# Legacy document tools (keeping for compatibility)
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    """Read a document by its ID."""
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


if __name__ == "__main__":
    mcp.run(transport="stdio")
