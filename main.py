import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai.types import UsageMetadata
from google.genai import types
from functions.call_function import call_function, available_functions
from functions.schema import (
    schema_get_file_content,
    schema_get_files_info,
    schema_run_python_file,
    schema_write_file,
)
from prompts import system_prompt


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
model_name = "gemini-2.5-flash"


def main():
    verbose_logging = False
    if len(sys.argv) < 2:
        print("Error: The prompt is required.", file=sys.stderr)
        sys.exit(1)
    print(sys.argv)
    user_prompt = sys.argv[1]

    for arg in sys.argv:
        if arg == "--verbose":
            verbose_logging = True

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    client = genai.Client(api_key=api_key)
    for i in range(10):
        try:
            final_response = generate_content(client, messages, verbose_logging)
            if final_response:
                print("Final response:")
                print(final_response)
                break
        except Exception as e:
            print(f"Error in generate_content: {e}")


def generate_content(client, messages, verbose_logging):
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    if verbose_logging:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    if response.candidates:
        for candidate in response.candidates:
            function_call_content = candidate.content
            messages.append(function_call_content)

    if not response.function_calls:
        return response.text

    function_responses = []
    if response.function_calls:
        for func in response.function_calls:
            print(f"- Calling function: {func.name}")
            func_output = call_function(func, verbose_logging)
            if not func_output.parts[0].function_response.response:
                raise Exception(
                    "Fatal error: Failed to receive a proper function response from call_function"
                )
            else:
                function_responses.append(func_output.parts[0])
            if verbose_logging == True:
                print(f"-> {func_output.parts[0].function_response.response['result']}")
        messages.append(
            types.Content(
                role="tool",
                parts=function_responses,
            )
        )


if __name__ == "__main__":
    main()
