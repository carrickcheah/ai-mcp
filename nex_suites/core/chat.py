from core.claude import Claude
from mcp_client import MCPClient
from core.tools import ToolManager
from anthropic.types import MessageParam


class Chat:
    def __init__(self, claude_service: Claude, clients: dict[str, MCPClient]):
        self.claude_service: Claude = claude_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[MessageParam] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = ""

        await self._process_query(query)

        # Check if the query needs tools
        query_lower = query.lower().strip()
        simple_messages = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye', 
                          'why', 'what', 'who', 'when', 'where', 'how', 'ok', 'okay', 'yes', 'no']
        
        # Determine if we should include tools
        needs_tools = True
        if len(query_lower) < 20 and any(query_lower == msg or query_lower.startswith(msg + ' ') for msg in simple_messages):
            needs_tools = False
        
        # Keywords that indicate tool usage needed
        tool_keywords = ['sales', 'invoice', 'revenue', 'august', 'september', 'month', 
                        'detail', 'show', 'get', 'list', 'report', 'data']
        if any(keyword in query_lower for keyword in tool_keywords):
            needs_tools = True

        while True:
            # Only get tools if needed
            tools = await ToolManager.get_all_tools(self.clients) if needs_tools else None
            
            response = self.claude_service.chat(
                messages=self.messages,
                tools=tools,
            )

            self.claude_service.add_assistant_message(self.messages, response)

            if response.stop_reason == "tool_use":
                print(self.claude_service.text_from_message(response))
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                self.claude_service.add_user_message(
                    self.messages, tool_result_parts
                )
            else:
                final_text_response = self.claude_service.text_from_message(
                    response
                )
                break

        return final_text_response
