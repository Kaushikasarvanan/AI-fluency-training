import json

from config import client, MODEL
from tools import TOOLS


# Tool definitions
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "Multiply two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subtract_numbers",
            "description": "Subtract the second number from the first number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "divide_numbers",
            "description": "Divide the first number by the second number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    }
]


def ask_agent(question, max_steps=5):

    # Store previous tool calls
    previous_tool_calls = []

    # Conversation messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI agent. Use tools when needed."
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # Agent loop
    for step in range(max_steps):

        print(f"\n--- Step {step + 1} ---")

        # Ask the LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS
        )

        message = response.choices[0].message

        # If no tool is required, return final answer
        if not message.tool_calls:
            return message.content

        # Add assistant message to conversation
        messages.append(message)

        # Process tool calls
        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name
            arguments_text = tool_call.function.arguments

            # Detect repeated identical tool calls
            call_signature = (tool_name, arguments_text)

            if call_signature in previous_tool_calls:
                return (
                    f"Stopped: repeated tool call detected "
                    f"for '{tool_name}'."
                )

            previous_tool_calls.append(call_signature)

            # Parse JSON arguments
            try:
                arguments = json.loads(arguments_text)
            except json.JSONDecodeError:
                return "Error: Invalid tool arguments."

            print(f"Tool used: {tool_name}")
            print(f"Arguments: {arguments}")

            # Check whether tool exists
            if tool_name not in TOOLS:
                return f"Error: unknown tool '{tool_name}'"

            # Execute tool safely
            try:
                result = TOOLS[tool_name](**arguments)
            except Exception as e:
                return f"Error while running tool: {e}"

            # Limit tool output size
            MAX_OUTPUT_LENGTH = 1000

            result_text = str(result)

            if len(result_text) > MAX_OUTPUT_LENGTH:
                result_text = (
                    result_text[:MAX_OUTPUT_LENGTH]
                    + "\n...[tool output truncated]..."
                )

            print(f"Tool result: {result_text}")

            # Add tool result to conversation
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text
                }
            )

    # Maximum step safety limit
    return (
        "Stopped safely: maximum number of steps reached. "
        "The agent did not continue running."
    )


# Run the agent
if __name__ == "__main__":

    question = input("Ask the agent: ")

    answer = ask_agent(question)

    print("\nAgent:", answer)