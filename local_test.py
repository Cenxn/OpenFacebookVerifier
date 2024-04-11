import os
from dotenv import load_dotenv
import re
import subprocess
from openai import OpenAI

def get_response(prompt, previous_messages=[]):
    """
    Sends a request to the GPT model and retrieves the response.
    Incorporates previous dialogue for continuity.
    :param prompt: The current prompt to send.
    :param previous_messages: A list of previous messages and responses for continuity.
    :return: A tuple containing the updated messages list and the latest GPT response.
    """
    client = OpenAI()
    chat_messages = previous_messages + [{"role": "user", "content": prompt}]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=chat_messages
    )

    response_text = completion.choices[0].message.content if completion.choices else ""
    updated_messages = previous_messages + [{"role": "user", "content": prompt},
                                            {"role": "assistant", "content": response_text}]

    return updated_messages, response_text


def initial_request():
    """
        Prompts the user to enter their question following a specific structure
        and ensures the input matches the expected format.
        :return: input message
        """
    print("Please enter each class and its description following this structure:")
    print("ClassName: Class function description and requirements.")
    print("Type 'END' on a new line to finish.")

    input_pattern = re.compile(r"([^:]+)\s*:\s*(.+)")  # Pattern to match "ClassName: Description"
    inputs = []

    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        match = input_pattern.match(line)
        if match:
            inputs.append(match.groups())
        else:
            print("Input does not match expected format. Please try again.")

        # Format the user input into a single string for the request
    request_text = "Write a programme in Java that performs the following functions:\n"
    for cls_name, description in inputs:
        request_text += f"Define a [{cls_name}] class, [{description}].\n"

    return request_text


def main():
    load_dotenv()
    messages_list = [{"role": "system", "content": "You are a helpful assistant."}]


if __name__ == '__main__':
    main()
