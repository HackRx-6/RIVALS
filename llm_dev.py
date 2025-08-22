# llm_agent.py
import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# --- Import the stateful browser class and tool schemas ---
from tools.tools import ToolsFunctionCalling, tool_definitions

async def run_single_conversation_async(client, model, messages, tools):
    """
    Runs a single, stateful conversation, managing its own browser lifecycle.
    """
    print(f"🤖 Starting new task: {messages[-1]['content'][:70]}...")
    
    # Key Change: Create a dedicated browser session for this task
    browser = ToolsFunctionCalling()
    # if not browser.driver:
    #     return "Error: Failed to initialize browser."

    # Key Change: Map tool names to the METHODS of the browser instance
    available_tools = {
        "navigate": browser.navigate,
        "read_content": browser.read_content,
        "click_element": browser.click_element,
        "input_text": browser.input_text,
        "generate_code": browser.generate_code,
        "generate_code_input_from_file": browser.generate_code_input_from_file,
        "run_python_with_input": browser.run_python_with_input,
        "observe_attribute_change": browser.observe_attribute_change,
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
        if browser:
            await browser.close()
        pass

async def process_request(user_request: dict) -> dict:
    """
    Takes a user request and runs all tasks in parallel.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    client = AsyncOpenAI()
    model = "gpt-4.1"
    
    context_data = {k: v for k, v in user_request.items() if k !='questions'}
    context_str = "\n".join([f"- : {value}" for key, value in context_data.items()])
    
    tasks = []
    for question in user_request['questions']:
        user_prompt = (
            "Please perform the following task based on the provided context.\n\n"
            f"## Context\n{context_str.lower()}\n\n"
            f"## Task\n{question.lower()}"
    )
        individual_messages = [
            {"role": "system", "content": "Your goal is to complete the user's task by using the available tools in a step-by-step manner. First, analyze the user's request and the context. Execute the plan by calling the necessary tools. If a tool fails or the result is unexpected, adjust your plan. Finally, provide a concise and direct answer to the original task. make sure to do anything in the tools complete the task. Don't ask further queries or give follow ups. Only respond with the final answer dont explain your reasoning. If it is code output just give the output don't explain , if the answer from code is empty return empty string"},
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