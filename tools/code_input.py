import os
from openai import OpenAI
from dotenv import load_dotenv

def generate_code_input(question: str, code: str) -> str:
    """
    Generates a precise standard input string for a given code snippet based on a natural language question.

    This tool uses an LLM to analyze a question for input values and a code snippet
    for its input reading format (e.g., single line, multi-line). It then constructs
    the exact string that can be piped as standard input to the code.

    Args:
        question: The natural language question containing the input values.
        code: The Python code snippet that will consume the input.

    Returns:
        A formatted string ready to be used as standard input for the code,
        or an error message if the generation fails.
    """
    try:
        # --- Setup OpenAI Client ---
        # It's recommended to have OPENAI_API_KEY in your .env file
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY not found in environment variables."
        
        client = OpenAI(api_key=api_key)

        # --- Construct the Prompt for the LLM ---
        # This prompt is carefully designed to instruct the model on its task.
        prompt = f"""
You are an expert programmer and your task is to generate the precise standard input string for a given Python script based on a natural language question.

Analyze the provided question to extract all necessary input values.
Then, analyze the provided Python code to understand how it reads from standard input (e.g., input(), input().split(), loops, etc.).

Your final output must be a single string that can be directly piped into the script to run it successfully. Do not include any explanation, code, or markdown formatting. Only provide the raw input string.

---
*Question:*
{question}

---
*Code:*
python
{code}

---
*Formatted Input String:*
"""

        # --- Call the OpenAI API ---
        response = client.chat.completions.create(
            model="gpt-4-turbo", # Or another capable model
            messages=[
                {"role": "system", "content": "You are an expert programmer assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0, # Set to 0 for deterministic output
        )

        # --- Extract and return the formatted string ---
        formatted_input = response.choices[0].message.content.strip()
        return formatted_input

    except Exception as e:
        return f"Error: An unexpected error occurred while generating the input string: {e}"

# --- Example Usage ---
if _name_ == '_main_':
    # --- Example 1: Input on a single line ---
    question1 = "Write a program that takes two integers, 15 and 25, and prints their sum."
    code1 = """
a, b = map(int, input().split())
print(a + b)
"""
    print("--- Test Case 1: Single-line input ---")
    input_string1 = generate_code_input(question1, code1)
    print(f"Question: '{question1}'")
    print(f"Generated Input String:\n---\n{input_string1}\n---")
    print("-" * 40)

    # --- Example 2: Input on multiple lines ---
    question2 = "Given a list of 3 names, 'Alice', 'Bob', and 'Charlie', print each name on a new line."
    code2 = """
n = 3
for _ in range(n):
    name = input()
    print(f"Hello, {name}")
"""
    print("--- Test Case 2: Multi-line input ---")
    input_string2 = generate_code_input(question2, code2)
    print(f"Question: '{question2}'")
    print(f"Generated Input String:\n---\n{input_string2}\n---")
    print("-" * 40)

    # --- Example 3: Mixed input types ---
    question3 = "You are given a count of 2 students. The first student is named 'John Doe' with a score of 95.5. The second is 'Jane Smith' with a score of 88.0. Process their data."
    code3 = """
n = int(input())
for _ in range(n):
    name = input()
    score = float(input())
    print(f"Student: {name}, Score: {score}")
"""
    print("--- Test Case 3: Mixed multi-line input ---")
    input_string3 = generate_code_input(question3, code3)
    print(f"Question: '{question3}'")
    print(f"Generated Input String:\n---\n{input_string3}\n---")
    print("-" * 40)