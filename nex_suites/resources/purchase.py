"""Purchase management resources for MCP server."""

import json
import logging
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import get_db_connection

logger = logging.getLogger(__name__)


async def purchase_summary_month() -> str:
    """
    Current month's procurement summary for dashboard.
    Returns total POs, spending, supplier count, and comparison with previous month.
    """
    try:
        async with get_db_connection() as db:
            now = datetime.now()
            current_month_start = datetime(now.year, now.month, 1)

            # Calculate previous month dates
            if now.month == 1:
                prev_month_start = datetime(now.year - 1, 12, 1)
                prev_month_end = datetime(now.year, 1, 1) - timedelta(seconds=1)
            else:
                prev_month_start = datetime(now.year, now.month - 1, 1)
                prev_month_end = current_month_start - timedelta(seconds=1)

            # Current month query
            current_query = """
                SELECT
                    COUNT(DISTINCT PurchaseOrderId_i) as po_count,
                    COUNT(DISTINCT SupplierId_i) as supplier_count,
                    COALESCE(SUM(TotalAmount_d), 0) as total_amount
                FROM tbl_purchase_order
                WHERE OrderDate_dd >= %s AND OrderDate_dd < %s
            """

            current_result = await db.fetch_one(current_query, (current_month_start, now))

            # Previous month query
            prev_result = await db.fetch_one(current_query, (prev_month_start, prev_month_end))

            # Calculate percentage changes
            prev_total = float(prev_result['total_amount']) if prev_result and prev_result['total_amount'] else 0
            current_total = float(current_result['total_amount']) if current_result and current_result['total_amount'] else 0

            if prev_total > 0:
                change_percentage = ((current_total - prev_total) / prev_total) * 100
            else:
                change_percentage = 100 if current_total > 0 else 0

            return json.dumps({
                "month": now.strftime("%B %Y"),
                "po_count": int(current_result['po_count']) if current_result else 0,
                "supplier_count": int(current_result['supplier_count']) if current_result else 0,
                "total_amount": current_total,
                "currency": "RM",
                "change_from_last_month": round(change_percentage, 2),
                "previous_month_total": prev_total
            })

    except Exception as e:
        logger.exception("Failed to fetch purchase summary")
        return json.dumps({"error": f"Failed to fetch purchase summary: {str(e)}"})


async def suppliers_top10() -> str:
    """
    Top 10 suppliers by purchase volume.
    Returns supplier details with total purchase amount and order count.
    """
    try:
        async with get_db_connection() as db:
            # Calculate date range (last 12 months)
            end_date = datetime.now()
            start_date = end_date - relativedelta(months=12)

            query = """
                SELECT
                    s.SuppId_i as supplier_id,
                    s.IntId_v as supplier_code,
                    s.SuppName_v as supplier_name,
                    COUNT(DISTINCT po.PurchaseOrderId_i) as order_count,
                    COALESCE(SUM(po.TotalAmount_d), 0) as total_amount,
                    COALESCE(AVG(po.TotalAmount_d), 0) as avg_order_value
                FROM tbl_supplier s
                INNER JOIN tbl_purchase_order po ON s.SuppId_i = po.SupplierId_i
                WHERE po.OrderDate_dd >= %s AND po.OrderDate_dd <= %s
                GROUP BY s.SuppId_i, s.IntId_v, s.SuppName_v
                ORDER BY total_amount DESC
                LIMIT 10
            """

            results = await db.fetch_all(query, (start_date, end_date))

            # Calculate total spending for percentage
            total_query = """
                SELECT COALESCE(SUM(TotalAmount_d), 0) as grand_total
                FROM tbl_purchase_order
                WHERE OrderDate_dd >= %s AND OrderDate_dd <= %s
            """

            total_result = await db.fetch_one(total_query, (start_date, end_date))
            grand_total = float(total_result['grand_total']) if total_result and total_result['grand_total'] else 0

            suppliers = []
            for idx, supplier in enumerate(results, 1):
                supplier_total = float(supplier['total_amount'])
                percentage = (supplier_total / grand_total * 100) if grand_total > 0 else 0

                suppliers.append({
                    "rank": idx,
                    "supplier_id": supplier['supplier_id'],
                    "supplier_code": supplier['supplier_code'] or "N/A",
                    "supplier_name": supplier['supplier_name'] or "Unknown",
                    "order_count": int(supplier['order_count']),
                    "total_amount": supplier_total,
                    "avg_order_value": float(supplier['avg_order_value']),
                    "percentage_of_total": round(percentage, 2)
                })

            return json.dumps({
                "period": f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}",
                "suppliers": suppliers,
                "grand_total": grand_total,
                "currency": "RM"
            })

    except Exception as e:
        logger.exception("Failed to fetch top suppliers")
        return json.dumps({"error": f"Failed to fetch top suppliers: {str(e)}"})


async def purchase_pending_approval() -> str:
    """
    POs pending approval count and details.
    Returns count, total value, and breakdown by urgency.
    """
    try:
        async with get_db_connection() as db:
            # Main query for pending POs
            query = """
                SELECT
                    COUNT(*) as count,
                    COALESCE(SUM(TotalAmount_d), 0) as total_value,
                    MIN(OrderDate_dd) as oldest_date,
                    MAX(OrderDate_dd) as newest_date
                FROM tbl_purchase_order
                WHERE ApprovalStatus_c = 'PENDING'
                   OR ApprovalStatus_c IS NULL
                   OR UPPER(ApprovalStatus_c) = 'WAITING'
            """

            result = await db.fetch_one(query)

            # Breakdown by amount ranges (urgency levels)
            breakdown_query = """
                SELECT
                    CASE
                        WHEN TotalAmount_d >= 100000 THEN 'high'
                        WHEN TotalAmount_d >= 50000 THEN 'medium'
                        WHEN TotalAmount_d >= 10000 THEN 'low'
                        ELSE 'minimal'
                    END as urgency,
                    COUNT(*) as count,
                    COALESCE(SUM(TotalAmount_d), 0) as total
                FROM tbl_purchase_order
                WHERE ApprovalStatus_c = 'PENDING'
                   OR ApprovalStatus_c IS NULL
                   OR UPPER(ApprovalStatus_c) = 'WAITING'
                GROUP BY urgency
                ORDER BY
                    CASE urgency
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END
            """

            breakdown = await db.fetch_all(breakdown_query)

            # Calculate days pending for oldest
            oldest_date = result['oldest_date'] if result and result['oldest_date'] else None
            days_oldest = (datetime.now() - oldest_date).days if oldest_date else 0

            urgency_breakdown = {}
            for item in breakdown:
                urgency_breakdown[item['urgency']] = {
                    "count": int(item['count']),
                    "total_value": float(item['total'])
                }

            return json.dumps({
                "total_count": int(result['count']) if result else 0,
                "total_value": float(result['total_value']) if result and result['total_value'] else 0,
                "oldest_pending_days": days_oldest,
                "oldest_date": oldest_date.strftime("%Y-%m-%d") if oldest_date else None,
                "newest_date": result['newest_date'].strftime("%Y-%m-%d") if result and result['newest_date'] else None,
                "urgency_breakdown": urgency_breakdown,
                "currency": "RM"
            })

    except Exception as e:
        logger.exception("Failed to fetch pending approvals")
        return json.dumps({"error": f"Failed to fetch pending approvals: {str(e)}"})


async def purchase_overdue_deliveries() -> str:
    """
    Overdue deliveries alert data.
    Returns list of overdue POs with supplier details and days overdue.
    """
    try:
        async with get_db_connection() as db:
            # Query for overdue deliveries
            query = """
                SELECT
                    po.PurchaseOrderId_i as po_id,
                    po.PONumber_v as po_number,
                    po.OrderDate_dd as order_date,
                    po.ExpectedDeliveryDate_dd as expected_date,
                    po.TotalAmount_d as amount,
                    s.SuppId_i as supplier_id,
                    s.IntId_v as supplier_code,
                    s.SuppName_v as supplier_name,
                    s.Phone_v as supplier_phone,
                    DATEDIFF(NOW(), po.ExpectedDeliveryDate_dd) as days_overdue
                FROM tbl_purchase_order po
                INNER JOIN tbl_supplier s ON po.SupplierId_i = s.SuppId_i
                WHERE po.ExpectedDeliveryDate_dd < NOW()
                  AND (po.DeliveryStatus_c = 'PENDING'
                       OR po.DeliveryStatus_c IS NULL
                       OR UPPER(po.DeliveryStatus_c) = 'WAITING'
                       OR UPPER(po.DeliveryStatus_c) = 'PARTIAL')
                ORDER BY days_overdue DESC
                LIMIT 50
            """

            results = await db.fetch_all(query)

            overdue_list = []
            total_overdue_value = 0

            for po in results:
                days_overdue = int(po['days_overdue']) if po['days_overdue'] else 0
                amount = float(po['amount']) if po['amount'] else 0
                total_overdue_value += amount

                # Determine severity based on days overdue
                if days_overdue > 30:
                    severity = "critical"
                elif days_overdue > 14:
                    severity = "high"
                elif days_overdue > 7:
                    severity = "medium"
                else:
                    severity = "low"

                overdue_list.append({
                    "po_id": po['po_id'],
                    "po_number": po['po_number'] or f"PO-{po['po_id']}",
                    "order_date": po['order_date'].strftime("%Y-%m-%d") if po['order_date'] else None,
                    "expected_date": po['expected_date'].strftime("%Y-%m-%d") if po['expected_date'] else None,
                    "days_overdue": days_overdue,
                    "severity": severity,
                    "amount": amount,
                    "supplier": {
                        "id": po['supplier_id'],
                        "code": po['supplier_code'] or "N/A",
                        "name": po['supplier_name'] or "Unknown",
                        "phone": po['supplier_phone'] or "N/A"
                    }
                })

            # Summary statistics
            summary = {
                "total_overdue": len(overdue_list),
                "total_value": total_overdue_value,
                "critical_count": sum(1 for po in overdue_list if po['severity'] == "critical"),
                "high_count": sum(1 for po in overdue_list if po['severity'] == "high"),
                "medium_count": sum(1 for po in overdue_list if po['severity'] == "medium"),
                "low_count": sum(1 for po in overdue_list if po['severity'] == "low"),
                "max_days_overdue": max((po['days_overdue'] for po in overdue_list), default=0)
            }

            return json.dumps({
                "summary": summary,
                "overdue_orders": overdue_list,
                "currency": "RM",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    except Exception as e:
        logger.exception("Failed to fetch overdue deliveries")
        return json.dumps({"error": f"Failed to fetch overdue deliveries: {str(e)}"})