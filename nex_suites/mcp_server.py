from mcp.server.fastmcp import FastMCP, Context
from pydantic import Field
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools import sales
from resources import purchase
from prompts import business_prompts


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


################################################################
##                      Define Resources                      ##
################################################################

@mcp.resource("purchase://summary/month")
async def purchase_summary_month_resource() -> str:
    """
    Current month's procurement summary for dashboard.
    Returns total POs, spending, supplier count, and comparison with previous month.
    """
    return await purchase.purchase_summary_month()


@mcp.resource("suppliers://top10")
async def suppliers_top10_resource() -> str:
    """
    Top 10 suppliers by purchase volume.
    Returns supplier details with total purchase amount and order count.
    """
    return await purchase.suppliers_top10()


@mcp.resource("purchase://pending-approval")
async def purchase_pending_approval_resource() -> str:
    """
    POs pending approval count and details.
    Returns count, total value, and breakdown by urgency.
    """
    return await purchase.purchase_pending_approval()


################################################################
##                      Define Prompts                        ##
################################################################

@mcp.prompt(
    name="generate_purchase_report",
    description="Generate comprehensive monthly purchase report with insights and recommendations"
)
async def generate_purchase_report_prompt(
    month: Optional[str] = Field(None, description="Month name (e.g., 'January'). Defaults to current month.")
) -> List[Dict[str, Any]]:
    """
    Generate a comprehensive purchase report for the specified month.
    Includes financial overview, supplier analysis, and optimization opportunities.
    """
    return await business_prompts.generate_purchase_report_prompt(month)


@mcp.prompt(
    name="analyze_supplier_performance",
    description="Analyze supplier performance metrics and provide improvement recommendations"
)
async def analyze_supplier_performance_prompt(
    supplier_id: Optional[str] = Field(None, description="Specific supplier ID to analyze. Analyzes top 10 if not specified.")
) -> List[Dict[str, Any]]:
    """
    Conduct comprehensive supplier performance analysis.
    Evaluates reliability, pricing, quality, and provides strategic recommendations.
    """
    return await business_prompts.analyze_supplier_performance_prompt(supplier_id)


@mcp.prompt(
    name="optimize_procurement",
    description="Generate procurement optimization suggestions and cost-saving opportunities"
)
async def optimize_procurement_prompt() -> List[Dict[str, Any]]:
    """
    Perform procurement optimization analysis to identify cost savings.
    Includes bulk purchase opportunities, supplier consolidation, and process improvements.
    """
    return await business_prompts.optimize_procurement_prompt()


if __name__ == "__main__":
    mcp.run(transport="stdio")
