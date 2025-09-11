"""
Sales-related prompt handlers
Tool-bound prompts for accurate data processing
"""

from mcp.server.fastmcp import Context


async def format_sales_invoice(
    invoice_id: str,
    context: Context
) -> list:
    """
    Tool-bound prompt that formats sales invoice data.
    Must execute get_sales_detail tool first to get accurate data.
    """
    
    # Execute bound tool to get invoice data
    try:
        invoice_data = await context.call_tool(
            "get_sales_detail", 
            {"invoice_no": invoice_id}
        )
    except Exception as e:
        return [{
            "role": "user",
            "content": f"Error retrieving invoice {invoice_id}: {str(e)}. Please check the invoice number and try again."
        }]
    
    # Load template (simplified for now - would use loader in production)
    prompt_template = """
You are a sales data formatting specialist. Display sales invoice result in tabular form. limit to 20 rows.

Given the following invoice data:
{data}

Please format this information as follows:

1. **Customer Information Section**
   - Display customer name, contact, and address in a clear structured format
   - Include customer ID and registration details if available

2. **Invoice Details Table**
   - Create a professional markdown table with these columns:
     * Item Description
     * Quantity
     * Unit Price
     * Total Amount
   - Include all line items from the invoice
   - Add a total row at the bottom

3. **Executive Summary**
   - Write exactly 50 words summarizing:
     * Customer name and invoice date
     * Total invoice value
     * Number of items purchased
     * Key products or services
     * Any notable aspects of the transaction

Format everything using clean markdown. Ensure numbers are properly formatted with currency symbols where appropriate.
"""
    
    # Replace data placeholder
    final_prompt = prompt_template.replace("{data}", str(invoice_data))
    
    return [{
        "role": "user",
        "content": final_prompt
    }]


async def analyze_sales_trends(
    period: str,
    context: Context
) -> list:
    """
    Analyzes sales data trends for the specified period.
    Tool-bound to get_sales for accurate data retrieval.
    """
    
    # Execute bound tool to get sales data
    try:
        sales_data = await context.call_tool(
            "get_sales",
            {"period": period}
        )
    except Exception as e:
        return [{
            "role": "user",
            "content": f"Error retrieving sales data for {period}: {str(e)}. Please check the period format and try again."
        }]
    
    prompt_template = """
You are a sales analytics expert.

Analyze the following sales data for the period: {period}
{data}
Display sales invoice result in tabular form. limit to 20 rows.

Provide a comprehensive analysis including:

1. **Trend Analysis**
   - Identify patterns in sales volume
   - Highlight peak and low periods
   - Calculate growth rates if applicable

2. **Key Metrics**
   - Total sales value
   - Average transaction size
   - Number of transactions
   - Top performing products/services

3. **Insights**
   - Notable observations from the data
   - Comparison with typical patterns
   - Potential factors influencing trends

4. **Recommendations**
   - Strategic suggestions based on trends
   - Areas for improvement
   - Opportunities to explore

Present findings in a clear, structured format using markdown.
"""
    
    final_prompt = prompt_template.replace("{period}", period).replace("{data}", str(sales_data))
    
    return [{
        "role": "user",
        "content": final_prompt
    }]


async def summarize_sales_data(
    period: str,
    context: Context
) -> list:
    """
    Creates executive summary of sales data.
    Flexible prompt that can work with various data formats.
    """
    
    # Get sales data
    try:
        sales_data = await context.call_tool(
            "get_sales",
            {"period": period}
        )
    except Exception as e:
        return [{
            "role": "user",
            "content": f"Error retrieving sales data: {str(e)}"
        }]
    
    prompt_template = """
Create an executive summary of the following sales data for {period}:
{data}
Display sales invoice result in tabular form. limit to 20 rows.
Summary Requirements:
- Start with a one-sentence overview
- Include total sales value and transaction count
- Highlight top 3 performing items
- Note any significant patterns
- Keep total length under 200 words
- Use bullet points for clarity

Focus on actionable insights for management review.
"""
    
    final_prompt = prompt_template.replace("{period}", period).replace("{data}", str(sales_data))
    
    return [{
        "role": "user",
        "content": final_prompt
    }]