import os
import json
import asyncio
from typing import Any
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx
from pathlib import Path
load_dotenv()

class MCPClient:
    def __init__(self):
        self._mcp_process = None
        self._client_session = None
        self.session = None

    async def __aenter__(self):
        cwd_path = os.getenv("MCP_NODE_PATH", "D:/Projects/dev/mcp-node/mcp-node")
        if not os.path.isdir(cwd_path):
            raise FileNotFoundError(f"[MCPClient] Invalid MCP_NODE_PATH: {cwd_path}")

        server_params = StdioServerParameters(
            command="node",
            args=[
                "--experimental-strip-types",
                "--no-warnings=ExperimentalWarning",
                "src/app.ts",
                "start-server",
                "--allow-tools=searchSingleIndex,saveObject,partialUpdateObject,batch,listIndices"
            ],
            cwd=cwd_path
        )

        self._mcp_process = stdio_client(server_params)
        read, write = await self._mcp_process.__aenter__()
        self._client_session = ClientSession(read, write)
        self.session = await self._client_session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client_session:
            await self._client_session.__aexit__(exc_type, exc_val, exc_tb)
        if self._mcp_process:
            await self._mcp_process.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        if not self.session:
            raise ConnectionError("MCP client is not connected.")

        print(f"[MCPClient] Calling '{tool_name}' with arguments: {json.dumps(kwargs, indent=2)}")
        try:
            result = await self.session.call_tool(tool_name, arguments=kwargs)
            if hasattr(result, 'content') and result.content:
                content_item = result.content[0]
                if hasattr(content_item, 'text'):
                    return json.loads(content_item.text)
            return result
        except Exception as e:
            print(f"[ERROR] Failed to call tool '{tool_name}': {e}")
            return {"error": str(e)}

async def AIModel(user_message: str) -> str:
    system_prompt = """
    You are an AI agent for a disaster relief system. Decide which Algolia index to use for a user's query.
    Use:
    - 'Relief_Shelter' if the query is about shelter, food, water, beds, or medical aid.
    - 'disaster_alerts' if the query is about ongoing disasters, warnings, floods, earthquakes, or emergencies.
    Return ONLY the index name as plain text.
    """

    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("REFERER_URL", "http://localhost:5173"),
        "X-Title": "Relief Finder AI Chat"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            index = response.json()['choices'][0]['message']['content'].strip()
            return index
    except Exception as e:
        print(f"[ERROR] Failed to fetch index from AI model: {e}")
        return "Relief_Shelter"

async def searchIndex(index_name: str, user_message: str):
    async with MCPClient() as mcp:
        result = await mcp.call_tool("searchSingleIndex",
            applicationId=os.getenv("ALGOLIA_APPLICATION_ID"),
            indexName=index_name,
            requestBody={
                "indexName": index_name,
                "query": user_message,
                "params": "hitsPerPage=5"
            }
        )
        return result

async def generateResult(user_message: str):
    index_name = await AIModel(user_message)
    print(f"[INFO] Selected index: {index_name}")
    data = await searchIndex(index_name, user_message)

    if "hits" in data and data["hits"]:
        top = data["hits"][0]

        # Read response prompt template
        prompt_path = Path("chat_assistant/prompts/response_prompt.txt")
        prompt_template = prompt_path.read_text()

        # Inject dynamic values
        prompt = prompt_template.replace("{{index_name}}", index_name)
        prompt = prompt.replace("{{query}}", user_message)
        prompt = prompt.replace("{{top_result_json}}", json.dumps(top, indent=2))

        # Send this prompt to OpenRouter
        payload = {
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
                {"role": "system", "content": "You are a helpful disaster assistant."},
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("REFERER_URL", "http://localhost:5173"),
            "X-Title": "Relief Finder AI Chat"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()['choices'][0]['message']['content'].strip()
                return result
        except Exception as e:
            print(f"[ERROR] Failed to generate paragraph from AI: {e}")
            return "We found data, but couldn't generate a summary."

    return "No results found for your query."