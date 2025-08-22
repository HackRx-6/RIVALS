import os
import json
import asyncio
from openai import AsyncOpenAI # Key Change: Import AsyncOpenAI
from dotenv import load_dotenv

# --- Import your custom tool functions ---
from tools.view_website_source import view_website_source
from tools.visit_url import visit_url
from tools.click_element import click_element
from tools.input_text import input_text

# Key Change: Functions are now 'async def'
async def run_single_conversation_async(client, model, messages, tools):
    """
    Runs a single, self-contained conversation for one independent question.
    """
    # --- Step 1: Make the initial API call ---
    print(f"🤖 Calling model for task: {messages[-1]['content'][:50]}...")
    # Key Change: Use 'await' for the API call
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    messages.append(response_message)

    if not tool_calls:
        return response_message.content

    # (Tool calling logic remains mostly the same, but the final call is awaited)
    available_functions = {
        "view_website_source": view_website_source,
        "visit_url": visit_url,
        "click_element": click_element,
        "input_text": input_text,
    }

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions.get(function_name)
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(**function_args)
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(function_response),
            }
        )

    # Key Change: 'await' the second call
    second_response = await client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return second_response.choices[0].message.content

# Key Change: process_request is now 'async def'
async def process_request(user_request: dict) -> dict:
    """
    Takes a user request and runs all questions in parallel.
    """
    # --- Setup ---
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    # Key Change: Use the AsyncOpenAI client
    client = AsyncOpenAI(
        api_key="YOUR_API_KEY_PLACEHOLDER", # Can be anything, as the proxy uses the header key.
        base_url="https://register.hackrx.in/llm/openai", # This points all requests to the proxy URL.
        default_headers={
            "x-subscription-key": "sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18"
    })
    model = "gpt-4o"

    try:
        with open("gpt_tools.json", "r") as f:
            tools = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("gpt_tools.json not found.")

    # --- Key Change: Create a list of concurrent tasks ---
    tasks = []
    for question in user_request['questions']:
        # Each question gets its own separate conversation history
        individual_messages = [
            {
                "role": "system",
                "content": "You are a web automation assistant. Use the provided tools to interact with the website to answer the user's question. Answer to the point."
            },
            {
                "role": "user",
                "content": f"Please perform the following task on the website {user_request['url']}. Task: {question}"
            }
        ]
        # Create a coroutine for each question and add it to our task list
        task = run_single_conversation_async(client, model, individual_messages, tools)
        tasks.append(task)

    # --- Key Change: Run all tasks concurrently ---
    print(f"🚀 Running {len(tasks)} questions in parallel...")
    all_answers = await asyncio.gather(*tasks)
    print("✅ All questions processed.")

    return {"answers": all_answers}