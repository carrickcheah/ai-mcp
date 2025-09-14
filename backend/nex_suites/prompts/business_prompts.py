"""Business prompts for MCP server - Purchase and Procurement focused."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


async def generate_purchase_report_prompt(month: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate a comprehensive purchase report prompt for the specified month.

    Args:
        month: Optional month name (e.g., "January", "December").
               Defaults to current month if not specified.

    Returns:
        List containing the user message for Claude to generate the report.
    """
    target_month = month or datetime.now().strftime("%B")
    current_year = datetime.now().year

    prompt_content = f"""Generate a comprehensive purchase report for {target_month} {current_year}.

Please follow these steps:

1. **Data Collection**:
   - First, check the purchase://summary/month resource to get the monthly overview
   - Review the suppliers://top10 resource to identify key suppliers
   - Check purchase://pending-approval for any bottlenecks
   - Review purchase://overdue-deliveries for delivery issues

2. **Report Structure**:

   📊 **EXECUTIVE SUMMARY**
   - Total procurement spend for {target_month}
   - Number of purchase orders processed
   - Key achievements and concerns (3-4 bullet points)

   💰 **FINANCIAL OVERVIEW**
   - Total spending: RM [amount]
   - Number of POs: [count]
   - Average PO value: RM [calculated]
   - Month-over-month change: [percentage]%

   🏢 **TOP SUPPLIERS ANALYSIS**
   - List top 5 suppliers with:
     * Supplier name and code
     * Total purchase amount
     * Number of orders
     * Percentage of total spend

   ⚠️ **RISK INDICATORS**
   - Pending approvals: [count] POs worth RM [amount]
   - Overdue deliveries: [count] orders
   - Supplier concentration risk (if any supplier > 30% of spend)

   💡 **OPTIMIZATION OPPORTUNITIES**
   - Identify potential bulk purchase opportunities
   - Suggest supplier consolidation if applicable
   - Highlight price variance for similar items

   📈 **RECOMMENDATIONS**
   - 3-5 actionable recommendations for next month
   - Focus on cost reduction and efficiency improvements

3. **Analysis Requirements**:
   - Compare with previous month's performance
   - Identify trends and patterns
   - Highlight any unusual spending patterns
   - Flag any compliance or approval delays

Please ensure the report is data-driven, actionable, and formatted for executive presentation."""

    return [{
        "role": "user",
        "content": prompt_content
    }]


async def analyze_supplier_performance_prompt(supplier_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyze supplier performance metrics and provide recommendations.

    Args:
        supplier_id: Optional specific supplier ID to analyze.
                    If not provided, analyzes all top suppliers.

    Returns:
        List containing the user message for supplier performance analysis.
    """
    if supplier_id:
        analysis_target = f"supplier ID {supplier_id}"
        instruction = f"Focus the analysis on supplier with ID: {supplier_id}"
    else:
        analysis_target = "top 10 suppliers"
        instruction = "Analyze the top 10 suppliers from the suppliers://top10 resource"

    prompt_content = f"""Conduct a comprehensive supplier performance analysis for {analysis_target}.

**Analysis Framework**:

1. **Data Gathering**:
   - {instruction}
   - Check purchase://overdue-deliveries for any delivery issues
   - Review purchase order history and patterns

2. **Performance Metrics to Evaluate**:

   📊 **VOLUME METRICS**
   - Total purchase volume (RM)
   - Number of orders placed
   - Average order value
   - Order frequency and consistency

   ⏱️ **RELIABILITY METRICS**
   - On-time delivery rate
   - Number of overdue deliveries
   - Average days overdue (if applicable)
   - Order fulfillment accuracy

   💰 **FINANCIAL METRICS**
   - Price competitiveness
   - Payment terms offered
   - Volume discounts available
   - Year-over-year price changes

   🎯 **QUALITY INDICATORS**
   - Return/rejection rate (if available)
   - Compliance with specifications
   - Response time to queries
   - Problem resolution efficiency

3. **Comparative Analysis**:
   - Benchmark against other suppliers in same category
   - Compare with industry standards
   - Identify best and worst performers

4. **Risk Assessment**:

   🚨 **SUPPLY CHAIN RISKS**
   - Single source dependencies
   - Geographic concentration
   - Financial stability concerns
   - Capacity constraints

5. **Output Format**:

   For each supplier, provide:
   - **Performance Score**: (Excellent/Good/Fair/Poor)
   - **Key Strengths**: 2-3 positive points
   - **Areas of Concern**: 2-3 improvement areas
   - **Recommended Actions**: Specific next steps

6. **Strategic Recommendations**:
   - Suppliers to increase business with
   - Suppliers requiring performance improvement plans
   - Suppliers to consider replacing
   - Opportunities for consolidation

Please provide data-driven insights with specific examples and actionable recommendations."""

    return [{
        "role": "user",
        "content": prompt_content
    }]


async def optimize_procurement_prompt() -> List[Dict[str, Any]]:
    """
    Generate procurement optimization suggestions based on current data.

    Returns:
        List containing the user message for procurement optimization analysis.
    """
    prompt_content = """Perform a comprehensive procurement optimization analysis and provide cost-saving recommendations.

**Optimization Analysis Framework**:

1. **Current State Assessment**:
   - Analyze purchase://summary/month for spending patterns
   - Review suppliers://top10 for supplier concentration
   - Check purchase://pending-approval for process bottlenecks
   - Examine purchase://overdue-deliveries for supply chain issues

2. **Cost Optimization Opportunities**:

   💰 **IMMEDIATE SAVINGS** (Quick Wins)
   - Identify duplicate purchases across departments
   - Find items purchased from multiple suppliers at different prices
   - Highlight small, frequent orders that could be consolidated
   - Spot maverick spending (purchases outside preferred suppliers)

   📦 **BULK PURCHASE OPPORTUNITIES**
   - Items with consistent monthly demand suitable for bulk buying
   - Calculate potential savings from volume discounts
   - Recommend optimal order quantities (EOQ)
   - Suggest quarterly or annual contracts for regular items

   🤝 **SUPPLIER CONSOLIDATION**
   - Identify categories with too many suppliers
   - Calculate admin cost savings from reducing supplier base
   - Recommend primary and backup supplier strategy
   - Estimate negotiation leverage from consolidated volumes

3. **Process Improvements**:

   ⚡ **EFFICIENCY GAINS**
   - Analyze approval delays and their impact
   - Identify bottlenecks in the procurement process
   - Suggest approval threshold adjustments
   - Recommend automation opportunities

   📊 **SPENDING ANALYTICS**
   - Categories with highest spend variance
   - Seasonal patterns to leverage
   - Off-contract spending percentage
   - Emergency purchase frequency and cost impact

4. **Strategic Sourcing Recommendations**:

   🎯 **CATEGORY STRATEGIES**
   - High-value categories needing strategic approach
   - Low-value, high-frequency items for automation
   - Critical items requiring dual sourcing
   - Commodities suitable for spot buying

   📈 **NEGOTIATION PRIORITIES**
   - Top 3 suppliers for renegotiation
   - Key terms to negotiate (price, payment, delivery)
   - Estimated savings potential
   - Recommended negotiation timeline

5. **Implementation Roadmap**:

   **MONTH 1** - Quick Wins
   - List 3-5 immediate actions
   - No-approval-needed changes
   - Estimated savings: RM [amount]

   **MONTH 2-3** - Process Optimization
   - System and process improvements
   - Supplier consolidation initiatives
   - Estimated savings: RM [amount]

   **MONTH 4-6** - Strategic Initiatives
   - Contract renegotiations
   - Long-term agreements
   - Estimated savings: RM [amount]

6. **ROI Calculation**:
   - Total potential savings identified
   - Implementation costs (if any)
   - Net savings projection
   - Payback period

Please provide specific, data-backed recommendations with clear implementation steps and measurable outcomes."""

    return [{
        "role": "user",
        "content": prompt_content
    }]