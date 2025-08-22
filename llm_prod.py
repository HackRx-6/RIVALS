# llm_agent.py
import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# --- Import the stateful browser class and tool schemas ---
from tools.tools import ToolsFunctionCalling, tool_definitions
from client import get_client, MODEL
async def  run_single_conversation_async(client, model, messages, tools):
    """
    Runs a single, stateful conversation, managing its own browser lifecycle.
    """
    print(f"🤖 Starting new task: {messages[-1]['content'][:70]}...")
    
    # Key Change: Create a dedicated browser session for this task
    browser = ToolsFunctionCalling()
    if not browser.driver:
        return "Error: Failed to initialize browser."

    # Key Change: Map tool names to the METHODS of the browser instance
    available_tools = {
        "navigate": browser.navigate,
        "read_content": browser.read_content,
        "click_element": browser.click_element,
        "input_text": browser.input_text,
    }

    try:
        # The conversation loop for this single task
        while True:
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
                print("✅ Model finished the task.")
                break

            print(f"🛠️ Model wants to use {len(tool_calls)} tool(s)...")
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)
                
                if not function_to_call:
                    print(f"Error: Unknown function '{function_name}'")
                    continue

                function_args = json.loads(tool_call.function.arguments)
                print(f"   - Calling: {function_name}({function_args})")
                
                # Key Change: 'await' the async tool function
                function_response = await function_to_call(**function_args)
                
                messages.append({
                    "tool_call_id": tool_call.id, "role": "tool",
                    "name": function_name, "content": str(function_response),
                })
        
        return messages[-1].content
    
    finally:
        # Key Change: CRITICAL - Ensure the browser is closed after the task is done
        await browser.close()

async def process_request(user_request: dict) -> dict:
    """
    Takes a user request and runs all tasks in parallel.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    # client = AsyncOpenAI(
    #     api_key="YOUR_API_KEY_PLACEHOLDER", # Can be anything, as the proxy uses the header key.
    #     base_url="https://register.hackrx.in/llm/openai", # This points all requests to the proxy URL.
    #     default_headers={
    #         "x-subscription-key": "sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18"
    # })
    # model = "gpt-4.1"
    client = get_client()  # fresh client with updated keys
    tasks = []
    for question in user_request['questions']:
        individual_messages = [
            {"role": "system", "content": "You are a web automation assistant. Start by navigating to the specified URL and then follow the user's website instructions or instructions on the website to complete the task."},
            {"role": "user", "content": f"Please perform the following task on the website {user_request['url']}. Task: {question}"}
        ]
        
        # Each task gets the full list of tool definitions
        task = run_single_conversation_async(client, MODEL, individual_messages, tool_definitions)
        tasks.append(task)

    print(f"🚀 Running {len(tasks)} tasks in parallel...")
    all_answers = await asyncio.gather(*tasks)
    print("✅ All tasks processed.")

    return {"answers": all_answers}

if __name__ == "__main__":
    # Create a mock HTML file for a realistic test
    html_content = """
    <html><body>
        <h1>Welcome!</h1>
        <p>Please enter your name to continue.</p>
        <input type="text" placeholder="Enter your name">
        <button onclick="alert('Submitted!')">Submit</button>
    </body></html>
    """
    with open("test_page.html", "w") as f:
        f.write(html_content)
    
    test_url = 'file://' + os.path.realpath("test_page.html")

    # Define a sample request with a multi-step task
    sample_request = {
        "url": test_url,
        "questions": [
            "Read the main heading, then type 'Agent Smith' into the name field, and finally click the 'Submit' button."
        ]
    }

    results = asyncio.run(process_request(sample_request))

    print("\n--- FINAL RESULTS ---")
    print(json.dumps(results, indent=2))
    print("---------------------")

    os.remove("test_page.html")