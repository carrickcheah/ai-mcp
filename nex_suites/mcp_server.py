from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field
import sys
from pathlib import Path
from tools.sales import get_sales, get_sales_detail
from prompts.handlers.sales_prompts import (
    format_sales_invoice,
    analyze_sales_trends,
    summarize_sales_data
)


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))



mcp = FastMCP("Nex Sales MCP", log_level="ERROR")


# Register the get_sales tool
@mcp.tool(
    name="get_sales",
    description="Get sales/purchase order data for a specified time period"
)
async def get_sales_tool(
    period: str = Field(description="Time period (e.g., 'AUG', 'last 3 months', '2024', '6 months')"),
    *,
    context: Context
) -> str:
    """
    Get sales/purchase order data for a specified period.
    Returns formatted report with transaction details and summary.
    """
    return await get_sales(period, context=context)


# Register the get_sales_detail tool
@mcp.tool(
    name="get_sales_detail",
    description="Get detailed information about a specific sales invoice including customer info and line items"
)
async def get_sales_detail_tool(
    invoice_no: str = Field(description="Invoice number to retrieve details for (e.g., '2508000932', 'SI25080001')"),
    *,
    context: Context
) -> str:
    """
    Get detailed information about a specific sales invoice.
    Returns customer information and line items.
    """
    return await get_sales_detail(invoice_no, context=context)


# Register sales prompts
@mcp.prompt(
    name="format_sales_invoice",
    description="Formats sales invoice data with customer details, line items table, and 50-word executive summary"
)
async def format_sales_invoice_prompt(
    invoice_id: str,
    context: Context
) -> list:
    """Register the format_sales_invoice prompt."""
    return await format_sales_invoice(invoice_id, context)


@mcp.prompt(
    name="analyze_sales_trends",
    description="Analyzes sales patterns and trends for a specified period with insights and recommendations"
)
async def analyze_sales_trends_prompt(
    period: str,
    context: Context
) -> list:
    """Register the analyze_sales_trends prompt."""
    return await analyze_sales_trends(period, context)


@mcp.prompt(
    name="summarize_sales_data",
    description="Creates a concise executive summary of sales data for quick review"
)
async def summarize_sales_data_prompt(
    period: str,
    context: Context
) -> list:
    """Register the summarize_sales_data prompt."""
    return await summarize_sales_data(period, context)


if __name__ == "__main__":
    mcp.run(transport="stdio")
