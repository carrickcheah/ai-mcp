# Prompt System Documentation

## Abstract

The MCP Prompt System implements model-discoverable prompts using @mcp.prompt decorators. This architecture enables AI models to discover, select, and execute appropriate prompts based on user intent without requiring users to know prompt names or commands. The system enforces tool-binding to prevent hallucination and ensures data accuracy.

## Introduction

This prompt system bridges user queries with specialized prompt templates through intelligent routing. The architecture separates concerns by placing logic in Python handlers, content in Markdown templates, and configuration in YAML files. The model discovers available prompts via list_prompts() and selects the best match for user needs.

## Core Concepts

### 1. Model-Discoverable Prompts
Prompts are registered using @mcp.prompt decorators, making them discoverable to AI models through the MCP protocol. Each prompt includes a name and description that helps the model understand its purpose.

### 2. Tool-Binding
Critical prompts are bound to specific tools that must execute before the prompt. This ensures data accuracy and prevents the model from hallucinating information.

### 3. Intent-Based Selection
The model analyzes user queries to determine intent, then selects the most appropriate prompt from available options.

### 4. Component Assembly
Prompts are assembled from base templates plus optional tone and context components, allowing flexible customization.

## Workflow

```
User Query
    |
    v
Model Analysis
    |
    v
list_prompts() Discovery
    |
    v
Intent Classification
    |
    v
Prompt Selection
    |
    v
Parameter Extraction
    |
    v
Tool Execution (if bound)
    |
    v
Template Loading
    |
    v
Component Assembly
    |
    v
Response Generation
```

### Detailed Flow:

1. **User Input**: User provides natural language query
   ------------------------------------
2. **Model Discovery**: AI calls list_prompts() to see available prompts
   ------------------------------------
3. **Intent Analysis**: Model analyzes query to determine user intent
   ------------------------------------
4. **Prompt Matching**: Model matches intent to best available prompt
   ------------------------------------
5. **Parameter Extraction**: Model extracts required parameters from query
   ------------------------------------
6. **Tool Execution**: If prompt is tool-bound, execute tool first
   ------------------------------------
7. **Template Assembly**: Load template and inject data/components
   ------------------------------------
8. **Response**: Return formatted prompt for execution

## Directory Structure

### /handlers
Python files containing @mcp.prompt decorated functions. These handle the logic of prompt execution, tool binding, and template assembly.

### /templates
Markdown files containing the actual prompt content. Organized by business domain (sales, purchase, general).

### /components
Reusable prompt modifiers:
- **tone/**: Adjusts communication style (professional, friendly, urgent)
- **context/**: Adds domain knowledge (company info, policies)

### /utils
Utility functions for loading templates, assembling components, and routing intents.

### config.yaml
Central configuration defining prompt metadata, tool bindings, and component mappings.

## Implementation Guide

### Adding a New Prompt

1. **Create Template** (templates/domain/prompt_name.md):
```markdown
Task context here.
Data: {data}
Instructions for the model.
```

2. **Create Handler** (handlers/domain_prompts.py):
```python
@mcp.prompt(
    name="prompt_name",
    description="What this prompt does"
)
async def prompt_name(param: str, context: Context) -> list:
    # Load template
    template = loader.load_template("domain/prompt_name.md")
    
    # Execute bound tool if needed
    data = await context.call_tool("tool_name", {"param": param})
    
    # Return formatted prompt
    return [{"role": "user", "content": template.replace("{data}", str(data))}]
```

3. **Update Config** (config.yaml):
```yaml
prompts:
  prompt_name:
    template: "domain/prompt_name.md"
    tool_bound: "tool_name"  # Optional
    components:
      tone: "professional"
```

## Tool Binding

Tool-bound prompts ensure data accuracy by requiring specific tool execution:

```python
@mcp.prompt(name="format_sales_invoice")
async def format_sales_invoice(invoice_id: str, context: Context):
    # Must execute tool first
    data = await context.call_tool("get_sales_detail", {"invoice_no": invoice_id})
    # Then use data in prompt
    return [{"role": "user", "content": template.replace("{data}", str(data))}]
```

## Best Practices

1. **Clear Descriptions**: Write descriptive prompt descriptions for model understanding
2. **Parameter Validation**: Validate required parameters before execution
3. **Error Handling**: Handle tool execution failures gracefully
4. **Template Organization**: Group templates by business domain
5. **Component Reuse**: Use components for common modifications
6. **Tool Binding**: Bind prompts to tools when data accuracy is critical

## Migration Path

### Phase 1: File-Based (Current)
Templates stored as .md files, configuration in YAML.

### Phase 2: Database Storage
Move templates to database for dynamic updates without deployment.

### Phase 3: Microservice
Enterprise prompt management service with versioning and A/B testing.