import os
from openai import OpenAI
from dotenv import load_dotenv

async def generate_code_input_from_file(question: str, code_file_path: str) -> str:
    """
    Generates a precise standard input string for a given code file based on a natural language question.

    This tool reads a Python script from a file, analyzes a question for input values,
    and then uses an LLM to construct the exact string that can be piped as standard
    input to the code.

    Args:
        question: The natural language question containing the input values.
        code_file_path: The local file path to the Python code snippet.

    Returns:
        A formatted string ready to be used as standard input for the code,
        or an error message if the file is not found or generation fails.
    """
    try:
        # --- Read the code from the specified file path ---
        with open(code_file_path, 'r') as f:
            code = f.read()

    except FileNotFoundError:
        return f"Error: The code file was not found at the specified path: {code_file_path}"
    except Exception as e:
        return f"Error: An unexpected error occurred while reading the code file: {e}"

    try:
       

        # --- Construct the Prompt for the LLM ---
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
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert programmer assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )

        # --- Extract and return the formatted string ---
        formatted_input = response.choices[0].message.content.strip()
        return formatted_input

    except Exception as e:
        return f"Error: An unexpected error occurred while generating the input string: {e}"
