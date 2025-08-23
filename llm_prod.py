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
    Manages per-task conversation with function calling loop.
    """
    print("🤖 Starting task:", messages[-1]["content"][:70])
    browser = ToolsFunctionCalling()
    available_tools = {
        "navigate": browser.navigate,
        "read_content": browser.read_content,
        "click_element": browser.click_element,
        "input_text": browser.input_text,
        "generate_code": browser.generate_code,
        "generate_code_input_from_file": browser.generate_code_input_from_file,
        "run_python_with_input": browser.run_python_with_input,
        "query_expander": browser.query_expander,
        "monitor_html_changes": browser.monitor_html_changes,
        "interpret_changes": browser.interpret_changes,
        "click_and_monitor": browser.click_and_monitor,
    }

    try:
        while True:
            resp = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            assistant_msg = resp.choices[0].message
            messages.append(assistant_msg)

            if not assistant_msg.tool_calls:
                print("✅ No tool_calls — finished.")
                break

            for tool_call in assistant_msg.tool_calls:
                fname = tool_call.function.name
                args = {}
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    pass

                print(f"Calling tool {fname} with", args)
                if fname in available_tools:
                    result = await available_tools[fname](**args)
                else:
                    result = {"error": f"Tool {fname} not found"}

                # Add the tool response
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

    finally:
        await browser.close()

    return messages[-1].content



async def process_request(user_request: dict) -> dict:
    """
    Takes a user request and runs all tasks in parallel.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    client = AsyncOpenAI(
        api_key="YOUR_API_KEY_PLACEHOLDER",
        base_url="https://register.hackrx.in/llm/openai",
        default_headers={
            "x-subscription-key": "sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18"
        })
    model = "gpt-5-mini"
    
    context_data = {k: v for k, v in user_request.items() if k != 'questions'}
    context_str = "\n".join([f"- : {value}" for key, value in context_data.items()])
    
    tasks = []
    for question in user_request['questions']:
        user_prompt = (
            "Please perform the following task based on the provided context.\n\n"
            f"## Context\n{context_str}\n\n"
            f"## Task\n{question}"
        )
        individual_messages = [
            {"role": "system", "content": """You are an expert web automation agent specializing in pattern recognition and sequential interactions. Your primary goal is to complete user tasks efficiently using the available tools.
    ALWAYS TRY TO BE PREIF AN WRITE CODE AND INPUTS FAST
CORE PRINCIPLES:
1. Always start by navigating to the specified URL
2. For immediate pattern sequences, use click_and_monitor when clicking a button for the first time with text in it.
3. For delayed or existing patterns, use regular monitor_html_changes
4. Make sure we have achieved core task objectives before ending the task.
5. For GitHub tasks type the name of the file you think the code will be in and keep trying until you find it.
             
PATTERN DETECTION STRATEGY:
- For buttons that start patterns ("Start Pattern", "Begin", "Play", etc.): Use click_and_monitor
- For ongoing patterns: Use monitor_html_changes with start_immediately=true
- Look for class changes, color shifts, highlighting, or flashing effects
- Extract exact sequence order from timestamps

SEQUENCE EXECUTION:
- After pattern detection, use click_grid_sequence if JSON sequence data is provided
- Use JavaScript click for better reliability on grid elements

GRID CLICKING TIPS:
- Use css_selector parameter for precise element targeting
- Convert array notation (div.pad[31]) to proper CSS (.pad:nth-of-type(32))
- Use class_name for elements with multiple classes
- Avoid text_content for grid elements without visible text

RESPONSE FORMAT:
- Provide only the final result
- For successful pattern completion, confirm the sequence was executed
- No explanations or follow-up questions
             """},
            {"role": "user", "content": user_prompt}
        ]
        
        task = run_single_conversation_async(client, model, individual_messages, tool_definitions)
        tasks.append(task)

    print(f"🚀 Running {len(tasks)} tasks in parallel...")
    all_answers = await asyncio.gather(*tasks)
    print("✅ All tasks processed.")

    return {"answers": all_answers}

if __name__ == "__main__":
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
