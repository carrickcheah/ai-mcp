"""Sales management tools for MCP server."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pydantic import Field
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_db_connection
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("sales-tools")
logger = logging.getLogger(__name__)


def parse_period(period: str) -> tuple[datetime, datetime]:
    """
    Parse flexible period strings like 'AUG', 'last 3 months', '2024', etc.
    
    Returns:
        Tuple of (start_date, end_date)
    """
    period_lower = period.lower().strip()
    now = datetime.now()
    
    # Month names
    months = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
        'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }
    
    # Check for month names
    for month_name, month_num in months.items():
        if month_name in period_lower:
            # Determine year (current year if month hasn't passed, otherwise last year)
            year = now.year
            if month_num > now.month:
                year -= 1
            
            start_date = datetime(year, month_num, 1)
            # Last day of month
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
            
            return start_date, end_date
    
    # Check for "last X months/days/years"
    if 'last' in period_lower:
        parts = period_lower.split()
        try:
            num = int(parts[1])
            if 'month' in period_lower:
                start_date = now - relativedelta(months=num)
            elif 'day' in period_lower:
                start_date = now - timedelta(days=num)
            elif 'year' in period_lower:
                start_date = now - relativedelta(years=num)
            else:
                start_date = now - relativedelta(months=1)  # Default to 1 month
            
            return start_date.replace(hour=0, minute=0, second=0, microsecond=0), now
        except (IndexError, ValueError):
            pass
    
    # Check for year (e.g., "2024")
    try:
        year = int(period)
        return datetime(year, 1, 1), datetime(year, 12, 31, 23, 59, 59)
    except ValueError:
        pass
    
    # Check for "X months/days/years"
    parts = period_lower.split()
    if len(parts) >= 2:
        try:
            num = int(parts[0])
            if 'month' in period_lower:
                start_date = now - relativedelta(months=num)
            elif 'day' in period_lower:
                start_date = now - timedelta(days=num)
            elif 'year' in period_lower:
                start_date = now - relativedelta(years=num)
            else:
                start_date = now - relativedelta(months=1)
            
            return start_date.replace(hour=0, minute=0, second=0, microsecond=0), now
        except ValueError:
            pass
    
    # Default to last month
    start_date = now - relativedelta(months=1)
    return start_date.replace(hour=0, minute=0, second=0, microsecond=0), now


@mcp.tool(
    name="get_sales",
    description="Get sales invoice data for a specified time period with transaction details and summary"
)
async def get_sales(
    period: str = Field(description="Time period (e.g., 'AUG', 'last 3 months', '2024', '6 months')"),
    *,
    context: Context
) -> str:
    """
    Get sales invoice data for a specified period.
    Returns formatted report with transaction details and summary.
    
    Args:
        period: Time period to fetch data for
        context: MCP context for logging and progress
    
    Returns:
        Formatted sales report string
    """
    try:
        # Initialize operation
        await context.info(f"Starting sales query for period: {period}")
        
        # Parse the period
        start_date, end_date = parse_period(period)
        await context.info(f"Date range: {start_date.date()} to {end_date.date()}")
        
        async with get_db_connection() as db:
            # Query for sales invoices in the period
            await context.info("Connecting to database and executing query...")
            
            query = """
                SELECT 
                    TxnDate_dd as txn_date,
                    DocRef_v as invoice_no,
                    GrandTotal_d as amount
                FROM tbl_sinvoice_txn
                WHERE TxnDate_dd >= %s AND TxnDate_dd <= %s
                ORDER BY TxnDate_dd DESC
            """
            
            all_records = await db.fetch_all(query, (start_date, end_date))
            await context.info(f"Retrieved {len(all_records)} records from database")
            
            if not all_records:
                await context.info("No records found for the specified period")
                return f"No sales invoices found for period: {period} ({start_date.date()} to {end_date.date()})"
            
            # Calculate statistics
            await context.info("Calculating statistics...")
            total_amount = sum(float(rec['amount'] or 0) for rec in all_records)
            total_count = len(all_records)
            avg_amount = total_amount / total_count if total_count > 0 else 0
            
            amounts = [float(rec['amount'] or 0) for rec in all_records if rec['amount']]
            min_amount = min(amounts) if amounts else 0
            max_amount = max(amounts) if amounts else 0
            
            # Format the report
            await context.info("Formatting report...")
            
            report = []
            report.append("=== Sales Report ===")
            report.append(f"Period: {period.upper()} ({start_date.date()} to {end_date.date()})")
            report.append("")
            
            # 1. Transaction details (cap at 30)
            report.append("1. Transaction Details (Latest 30 records):")
            report.append("-" * 70)
            report.append(f"{'Date':<12} | {'Invoice No':<20} | {'Amount':>15}")
            report.append("-" * 70)
            
            display_records = all_records[:30]
            for rec in display_records:
                txn_date = rec['txn_date'].strftime('%Y-%m-%d') if rec['txn_date'] else 'N/A'
                invoice_no = str(rec['invoice_no'] or 'N/A')[:20]
                amount = float(rec['amount'] or 0)
                report.append(f"{txn_date:<12} | {invoice_no:<20} | RM{amount:>13,.2f}")
            
            report.append("-" * 70)
            
            if total_count > 30:
                report.append(f"* Showing 30 of {total_count} total records")
            
            # 2. Total count
            report.append("")
            report.append(f"2. Total Sales Invoices: {total_count}")
            
            # 3. Amount summary
            report.append("")
            report.append("3. Amount Summary:")
            report.append(f"   Total: RM{total_amount:,.2f}")
            report.append(f"   Average per Invoice: RM{avg_amount:,.2f}")
            report.append(f"   Min Amount: RM{min_amount:,.2f}")
            report.append(f"   Max Amount: RM{max_amount:,.2f}")
            
            await context.info("Report generation completed successfully")
            
            return "\n".join(report)
            
    except Exception as e:
        logger.exception("Failed to get sales data")
        return f"Error fetching sales data: {str(e)}"


@mcp.tool(
    name="get_sales_detail",
    description="Read the detail of a sales invoice and return comprehensive information including customer and items"
)
async def get_sales_detail(
    invoice_no: str = Field(description="Invoice number to retrieve details for (e.g., 'INV001', 'SI25080001')"),
    *,
    context: Context
) -> str:
    """
    Get detailed information about a specific sales invoice.
    Joins invoice transaction, order items, and supplier/customer data.
    
    Args:
        invoice_no: The invoice number to look up
        context: MCP context for logging and progress
    
    Returns:
        Formatted invoice details including customer info and line items
    """
    try:
        await context.info(f"Starting invoice detail query for: {invoice_no}")
        
        async with get_db_connection() as db:
            await context.info("Connecting to database...")
            # Query for invoice header with customer details
            header_query = """
                SELECT 
                    inv.TxnDate_dd as txn_date,
                    inv.DocRef_v as invoice_no,
                    inv.GrandTotal_d as grand_total,
                    inv.CustId_i as customer_id,
                    sup.IntId_v as customer_code,
                    sup.SuppName_v as customer_name
                FROM tbl_sinvoice_txn inv
                LEFT JOIN tbl_supplier sup ON inv.CustId_i = sup.SuppId_i
                WHERE inv.DocRef_v = %s
            """
            
            await context.info("Fetching invoice header...")
            header = await db.fetch_one(header_query, (invoice_no,))
            
            if not header:
                await context.info(f"Invoice {invoice_no} not found")
                return f"Invoice '{invoice_no}' not found in the system."
            
            # Query for invoice line items
            # Join via TxnId_i
            items_query = """
                SELECT 
                    item.QtyStatus_c as qty_status,
                    item.ItemId_i as item_id,
                    item.Remark_v as item_description,
                    item.Qty_d as quantity,
                    item.Price_d as unit_price,
                    item.LineTotal_d as line_total
                FROM tbl_sorder_item item
                INNER JOIN tbl_sinvoice_txn inv ON item.TxnId_i = inv.TxnId_i
                WHERE inv.DocRef_v = %s
                ORDER BY item.RowId_i
            """
            
            await context.info("Fetching line items...")
            items = await db.fetch_all(items_query, (invoice_no,))
            
            # Format the detailed report
            await context.info("Formatting invoice details...")
            report = []
            report.append("=== Sales Invoice Details ===")
            report.append("")
            
            # Header information
            report.append("Invoice Information:")
            report.append("-" * 50)
            report.append(f"Invoice No: {header['invoice_no']}")
            report.append(f"Date: {header['txn_date'].strftime('%Y-%m-%d') if header['txn_date'] else 'N/A'}")
            report.append(f"Grand Total: RM{float(header['grand_total'] or 0):,.2f}")
            report.append("")
            
            # Customer information
            report.append("Customer Information:")
            report.append("-" * 50)
            report.append(f"Customer ID: {header['customer_id'] or 'N/A'}")
            report.append(f"Customer Code: {header['customer_code'] or 'N/A'}")
            report.append(f"Customer Name: {header['customer_name'] or 'N/A'}")
            report.append("")
            
            # Line items
            if items:
                report.append("Line Items:")
                report.append("-" * 80)
                report.append(f"{'Item Code':<15} | {'Description':<25} | {'Qty':<8} | {'Price':<10} | {'Total':<12} | {'Status':<10}")
                report.append("-" * 80)
                
                for item in items:
                    item_id = str(item.get('item_id', 'N/A'))[:15]
                    description = str(item.get('item_description', 'N/A'))[:25] if item.get('item_description') else 'N/A'
                    quantity = float(item.get('quantity', 0))
                    unit_price = float(item.get('unit_price', 0))
                    line_total = float(item.get('line_total', 0))
                    qty_status = str(item.get('qty_status', 'N/A'))[:10]
                    
                    report.append(
                        f"{item_id:<15} | {description:<25} | {quantity:<8.2f} | "
                        f"RM{unit_price:<8.2f} | RM{line_total:<10.2f} | {qty_status:<10}"
                    )
                
                report.append("-" * 80)
                
                # Summary
                total_items = len(items)
                total_quantity = sum(float(item.get('quantity', 0)) for item in items)
                report.append(f"Total Items: {total_items}")
                report.append(f"Total Quantity: {total_quantity:.2f}")
            else:
                report.append("No line items found for this invoice.")
            
            await context.info("Invoice details generation completed")
            
            return "\n".join(report)
            
    except Exception as e:
        logger.exception("Failed to get sales invoice details")
        await context.info(f"Error occurred: {str(e)}")
        return f"Error fetching invoice details: {str(e)}"


# async def create_sales_order(
#     customer_id: str,
#     items: List[Dict[str, Any]],
#     delivery_date: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Create a new sales order.
    
#     Args:
#         customer_id: Customer identifier
#         items: List of order items with product_id, quantity, price
#         delivery_date: Optional delivery date
    
#     Returns:
#         Sales order details with order_id
#     """
#     try:
#         # TODO: Implement database logic
#         order_id = f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
#         return {
#             "order_id": order_id,
#             "customer_id": customer_id,
#             "items": items,
#             "delivery_date": delivery_date,
#             "status": "created",
#             "created_at": datetime.now().isoformat()
#         }
#     except Exception:
#         logger.exception("Failed to create sales order")
#         raise


# async def get_sales_order(order_id: str) -> Dict[str, Any]:
#     """
#     Retrieve sales order details.
    
#     Args:
#         order_id: Sales order identifier
    
#     Returns:
#         Sales order details
#     """
#     try:
#         # TODO: Implement database logic
#         return {
#             "order_id": order_id,
#             "status": "pending",
#             "message": "Database integration pending"
#         }
#     except Exception:
#         logger.exception("Failed to get sales order")
#         raise


# async def list_sales_orders(
#     customer_id: Optional[str] = None,
#     status: Optional[str] = None,
#     limit: int = 100
# ) -> List[Dict[str, Any]]:
#     """
#     List sales orders with optional filters.
    
#     Args:
#         customer_id: Filter by customer
#         status: Filter by order status
#         limit: Maximum number of results
    
#     Returns:
#         List of sales orders
#     """
#     try:
#         # TODO: Implement database logic
#         return []
#     except Exception:
#         logger.exception("Failed to list sales orders")
#         raise