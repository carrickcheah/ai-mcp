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


async def get_sales(
    period: str = Field(description="Time period (e.g., 'AUG', 'last 3 months', '2024', '6 months')")
) -> str:
    """
    Get sales/purchase order data for a specified period.
    Returns formatted report with transaction details and summary.
    
    Args:
        period: Time period to fetch data for
    
    Returns:
        Formatted sales report string
    """
    try:
        # Parse the period
        start_date, end_date = parse_period(period)
        
        async with get_db_connection() as db:
            # Query for purchase orders in the period
            query = """
                SELECT 
                    TxnDate_dd as txn_date,
                    DocRef_v as po_number,
                    GrandTotal_d as amount
                FROM tbl_porder_txn
                WHERE TxnDate_dd >= %s AND TxnDate_dd <= %s
                ORDER BY TxnDate_dd DESC
            """
            
            all_records = await db.fetch_all(query, (start_date, end_date))
            
            if not all_records:
                return f"No purchase orders found for period: {period} ({start_date.date()} to {end_date.date()})"
            
            # Calculate statistics
            total_amount = sum(float(rec['amount'] or 0) for rec in all_records)
            total_count = len(all_records)
            avg_amount = total_amount / total_count if total_count > 0 else 0
            
            amounts = [float(rec['amount'] or 0) for rec in all_records if rec['amount']]
            min_amount = min(amounts) if amounts else 0
            max_amount = max(amounts) if amounts else 0
            
            # Format the report
            report = []
            report.append("=== Sales/Purchase Order Report ===")
            report.append(f"Period: {period.upper()} ({start_date.date()} to {end_date.date()})")
            report.append("")
            
            # 1. Transaction details (cap at 30)
            report.append("1. Transaction Details (Latest 30 records):")
            report.append("-" * 70)
            report.append(f"{'Date':<12} | {'PO Number':<20} | {'Amount':>15}")
            report.append("-" * 70)
            
            display_records = all_records[:30]
            for rec in display_records:
                txn_date = rec['txn_date'].strftime('%Y-%m-%d') if rec['txn_date'] else 'N/A'
                po_number = str(rec['po_number'] or 'N/A')[:20]
                amount = float(rec['amount'] or 0)
                report.append(f"{txn_date:<12} | {po_number:<20} | RM{amount:>13,.2f}")
            
            report.append("-" * 70)
            
            if total_count > 30:
                report.append(f"* Showing 30 of {total_count} total records")
            
            # 2. Total count
            report.append("")
            report.append(f"2. Total Purchase Orders: {total_count}")
            
            # 3. Amount summary
            report.append("")
            report.append("3. Amount Summary:")
            report.append(f"   Total: RM{total_amount:,.2f}")
            report.append(f"   Average per PO: RM{avg_amount:,.2f}")
            report.append(f"   Min Amount: RM{min_amount:,.2f}")
            report.append(f"   Max Amount: RM{max_amount:,.2f}")
            
            return "\n".join(report)
            
    except Exception as e:
        logger.exception("Failed to get sales data")
        return f"Error fetching sales data: {str(e)}"


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