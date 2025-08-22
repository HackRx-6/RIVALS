import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# --- Import your custom tool functions ---
# These imports assume your tool functions are in their own files as described.
from tools.view_website_source import view_website_source
from tools.visit_url import visit_url
from tools.click_element import click_element

def run_conversation(client, model, messages, tools):
    """
    Main loop to run the conversation with the model, handling tool calls.
    """
    # --- Step 1: Make the initial API call ---
    print("🤖 Calling model with user request...")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    messages.append(response_message)  # Append assistant's response

    # --- Step 2: Check if the model wants to call a tool ---
    if not tool_calls:
        print("🤖 Model provided a direct answer.")
        return response_message.content

    # --- Step 3: Execute tool calls ---
    print(f"🔧 Model wants to use {len(tool_calls)} tool(s)...")
    
    # Mapping of available functions
    available_functions = {
        "view_website_source": view_website_source,
        "visit_url": visit_url,
        "click_element": click_element,
    }

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions.get(function_name)
        
        if not function_to_call:
            print(f"❌ Error: Model requested an unknown function: {function_name}")
            continue

        function_args = json.loads(tool_call.function.arguments)
        print(f"   - Calling function: {function_name} with args: {function_args}")
        
        # --- Call the actual tool function ---
        function_response = function_to_call(**function_args)
        
        print(f"   - Function response received (first 200 chars): {str(function_response)[:200]}...")

        # --- Append the tool's response to the conversation history ---
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(function_response),
            }
        )

    # --- Step 4: Make a second API call with the tool's response ---
    print("🤖 Calling model again with tool results...")
    second_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    
    return second_response.choices[0].message.content

def process_request(user_request: dict) -> dict:
    """
    Takes a user request, orchestrates the OpenAI and tool calls, and returns the final answer.
    
    Args:
        user_request: A dictionary with 'url' and 'questions' keys.
        
    Returns:
        A dictionary containing the final answers.
    """
    # --- Setup ---
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")

    # client = OpenAI(api_key=api_key)


    client = OpenAI(
        api_key="YOUR_API_KEY_PLACEHOLDER", # Can be anything, as the proxy uses the header key.
        base_url="https://register.hackrx.in/llm/openai", # This points all requests to the proxy URL.
        default_headers={
            "x-subscription-key": "sk-spgw-api01-f687cb7fbb4886346b2f59c0d39c8c18"
        }
    )
    model = "gpt-4.1" # Or another model that supports tool calling

    # --- Load Tools ---
    try:
        with open("gpt_tools.json", "r") as f:
            tools = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("browser_tools_schema.json not found. Please ensure it's in the same directory.")

    # --- Format the initial message for the model ---
    messages = [
        {
            "role": "system",
            "content": "Use provided tools to interact with the website. Do not include extra information and answer to the point, dont include the steps, just the answer."
        },
        {
            "role": "user",
            "content": f"Please perform the following tasks on the website {user_request['url']}. Task: {user_request['questions'][0]}"
        }
    ]

    # --- Run the conversation ---
    final_answer = run_conversation(client, model, messages, tools)

    # --- Format and return the final output ---
    output = {
        "answers": [final_answer]
    }
    return output


# --- Example of how to call the function ---
if __name__ == "__main__":
    # This is the example request you provided.
    request_data = {
        "url": "https://register.hackrx.in/showdown/startChallenge/S2V5JTIwZm9yJTIwY2hhbGxlbmdlJTIwaXMlMjAlMjdwYXNzd29yZCUyNyUyMGFuZCUyMGZsYWclMjBpcyUyMCUyN2ZsYWdneSUyNw==",
        "questions": [
            "Go to the website and start the challenge. Complete the challenge and return the answers for the following questions: What is the challenge name?"
        ]
    }
    
    final_output = process_request(request_data)

    print("\n" + "="*50)
    print("✅ Final Answer:")
    print(json.dumps(final_output, indent=2))
    print("="*50)
