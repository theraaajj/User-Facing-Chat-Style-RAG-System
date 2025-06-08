import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from core import tool_functions as tools

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client (pointed to local Ollama server)
client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),  # Fallback if env var missing
    api_key=os.getenv("OLLAMA_API_KEY", "ollama")  # Dummy key for local use
)

# Define tool schema metadata to include in LLM system prompt
tool_schemas = [
    {
        "type": "function",
        "function": {
            "name": "get_documents_by_president",
            "description": "Fetch documents signed by a specific president during a given month.",
            "parameters": {
                "type": "object",
                "properties": {
                    "president_name": {"type": "string"},
                    "month": {"type": "string", "description": "Format: YYYY-MM"}
                },
                "required": ["president_name", "month"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_documents_by_topic",
            "description": "Fetch documents by keyword appearing in title or summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic_keywords": {"type": "string"}
                },
                "required": ["topic_keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_documents_by_date_range",
            "description": "Fetch documents published between two dates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"}
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_documents",
            "description": "Fetch the most recent federal register documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 5}
                },
                "required": []
            }
        }
    }
]

# Maps tool name returned by LLM to the actual backend Python function
FUNCTION_MAP = {
    "get_documents_by_president": tools.get_documents_by_president,
    "get_documents_by_topic": tools.get_documents_by_topic,
    "get_documents_by_date_range": tools.get_documents_by_date_range,
    "get_latest_documents": tools.get_latest_documents
}

def call_agent(user_input: str) -> str:
    """
    Main function to interact with the agent:
    - Sends user input to LLM
    - Handles tool call(s) if LLM requests them
    - Returns summarized final response from LLM

    Args:
        user_input (str): User's question/query.

    Returns:
        str: Final response from agent (LLM).
    """
    # Step 1: Initial LLM call with user message and tool definitions
    response = client.chat.completions.create(
        model="phi3",  # Change model name as per your Ollama model
        messages=[
            {"role": "system", "content": "You are an assistant that uses tools to help answer user questions about US federal registry data."},
            {"role": "user", "content": user_input}
        ],
        tools=tool_schemas,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # Step 2: Check if tool is called
    if message.tool_calls:
        results = []

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            try:
                func_args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                func_args = {}

            tool_function = FUNCTION_MAP.get(func_name)
            if not tool_function:
                return f"Unknown function requested: {func_name}"

            try:
                result = tool_function(**func_args)
                output = str(result) if result else "No results found."
                results.append({"tool_call_id": tool_call.id, "output": output})
            except Exception as e:
                results.append({"tool_call_id": tool_call.id, "output": f"Error: {str(e)}"})

        # Step 3: Return results back to LLM for final summarization
        final_response = client.chat.completions.create(
            model="qwen:0.5b",
            messages=[
                {"role": "system", "content": "You are an assistant that uses tools to help answer user questions about US federal registry data."},
                {"role": "user", "content": user_input},
                message,
                *[
                    {
                        "role": "tool",
                        "tool_call_id": r["tool_call_id"],
                        "content": r["output"]
                    } for r in results
                ]
            ]
        )

        return final_response.choices[0].message.content

    # Step 4: If no tool needed, just return direct LLM response
    return message.content
