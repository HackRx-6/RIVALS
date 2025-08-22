import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# --- Import the stateful browser class and tool schemas ---
from tools.browser_tools import BrowserSession, tool_definitions

async def run_single_conversation_async(client, model, messages, tools):
    """
    Runs a single, stateful conversation, managing its own browser lifecycle.
    """
    print(f"🤖 Starting new task: {messages[-1]['content'][-70:]}...")

    # A dedicated browser session is created for this task
    browser = BrowserSession()
    if not browser.driver:
        return "Error: Failed to initialize browser."

    # Map tool names to the METHODS of the browser instance
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

            print(f"🛠️  Model wants to use {len(tool_calls)} tool(s)...")
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)
                
                if not function_to_call:
                    print(f"Error: Unknown function '{function_name}'")
                    continue

                function_args = json.loads(tool_call.function.arguments)
                print(f"  - Calling: {function_name}({function_args})")
                
                # 'await' the async tool function
                function_response = await function_to_call(**function_args)
                
                messages.append({
                    "tool_call_id": tool_call.id, "role": "tool",
                    "name": function_name, "content": str(function_response),
                })
        
        # Ensure content exists before accessing it
        final_content = response_message.content if response_message else "No final message content from model."
        return final_content
    
    finally:
        # CRITICAL - Ensure the browser is closed after the task is done
        await browser.close()

async def process_request(user_request: dict) -> dict:
    """
    Takes a user request, formats it with general context, and runs all tasks in parallel.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    client = AsyncOpenAI(api_key=api_key)
    model = "gpt-4-turbo-preview"  # Using a recommended model for tool use
    
    # --- KEY CHANGE: Create a generalized context from the request ---
    # Copy all keys from the user request EXCEPT for 'questions'
    context_data = {k: v for k, v in user_request.items() if k != 'questions'}
    
    # Format the context into a string for the prompt
    context_str = "\n".join([f"- {key}: {value}" for key, value in context_data.items()])
    
    tasks = []
    for question in user_request['questions']:
        # --- KEY CHANGE: More generalized system and user prompts ---
        user_prompt = (
            "Please perform the following task based on the provided context.\n\n"
            f"## Context\n{context_str}\n\n"
            f"## Task\n{question}"
        )

        individual_messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Analyze the provided context and use the available tools to complete the user's task. If the context contains a 'url', your first step should be to navigate to it."},
            {"role": "user", "content": user_prompt}
        ]
        
        # Each task gets the full list of tool definitions
        task = run_single_conversation_async(client, model, individual_messages, tool_definitions)
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
    
    # Generate a platform-independent file URI
    test_url = 'file:///' + os.path.realpath("test_page.html").replace('\\', '/')

    # Define a sample request with a multi-step task and extra context
    sample_request = {
        "url": test_url,
        "user_id": "test-user-123", # Example of extra data
        "questions": [
            "Read the main heading, then type 'Agent Smith' into the name field, and finally click the 'Submit' button."
        ]
    }

    results = asyncio.run(process_request(sample_request))

    print("\n--- FINAL RESULTS ---")
    print(json.dumps(results, indent=2))
    print("---------------------")

    os.remove("test_page.html")