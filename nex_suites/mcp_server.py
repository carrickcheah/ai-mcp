from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools import sales


mcp = FastMCP("Nex Sales MCP", log_level="ERROR")



################################################################
##                        Define Tools                        ## 
################################################################

# Register the get_sales tool
@mcp.tool(
    name="get_sales",
    description="Get sales/purchase order data for a specified time period"
)
async def get_sales(
    period: str = Field(description="Time period (e.g., 'AUG', 'last 3 months', '2024', '6 months')"),
    *,
    context: Context
) -> str:
    """
    Get sales/purchase order data for a specified period.
    Returns formatted report with transaction details and summary.
    """
    return await sales.get_sales(period, context=context)


# Register the get_sales_detail tool
@mcp.tool(
    name="get_sales_detail",
    description="Get detailed information about a specific sales invoice including customer info and line items"
)
async def get_sales_detail(
    invoice_no: str = Field(description="Invoice number to retrieve details for (e.g., '2508000932', 'SI25080001')"),
    *,
    context: Context
) -> str:
    """
    Get detailed information about a specific sales invoice.
    Returns customer information and line items.
    """
    return await sales.get_sales_detail(invoice_no, context=context)


if __name__ == "__main__":
    mcp.run(transport="stdio")
