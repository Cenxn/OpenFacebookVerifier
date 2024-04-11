import os
from dotenv import load_dotenv
import re
import subprocess
import openai

output_dir = './output'


def mk_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def extract_imports(code):
    # Use regular expressions to match all import statements.
    imports_regex = re.compile(r'^import\s+.*?;$', re.MULTILINE)
    imports = imports_regex.findall(code)
    return "\n".join(imports) + "\n\n" if imports else ""


def generate_java_file(user_input, output_dir):
    file_paths = []
    imports = extract_imports(user_input)

    # Initialize counters and buffers
    brace_counter = 0
    class_code = ""
    in_class = False
    class_name = ""

    for line in user_input.split("\n"):
        if "class" in line and not in_class:
            # Assuming class name is always after 'class' keyword and before any '{'
            class_name = re.search(r"class\s+(\w+)", line).group(1)
            in_class = True
            class_code = line + "\n"
            brace_counter = line.count("{") - line.count("}")
        elif in_class:
            brace_counter += line.count("{") - line.count("}")
            class_code += line + "\n"
            if brace_counter == 0:
                # Class ends when brace_counter returns to zero
                file_content = imports + class_code
                file_name = os.path.join(output_dir, f"{class_name}.java")
                with open(file_name, 'w') as file:
                    file.write(file_content)
                    file_paths.append(file_name)
                    print(f"[Generated] {file_name}")
                # Reset for next class
                in_class = False
                class_code = ""
                class_name = ""

    return file_paths


def get_multi_line_input(msg="Enter text (type 'END' on a new line to finish): "):
    print(msg)
    lines = []
    while True:
        line = input()
        if line == "END":  # End input when user inputs END
            break
        lines.append(line)
    return "\n".join(lines)


def run_infer_on_file(java_file):
    """
    Using Facebook Infer to Analyse Specified Java File
    :param java_file_li: Path to the Java file to be analysed
    :return:
    """
    command = ['infer', 'run', '--', 'javac', java_file]

    try:
        result = subprocess.run(command, check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        if result.stderr or "ERROR" in result.stdout:
            error_msg = result.stderr if result.stderr else result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Infer: {e.stderr}")

    return error_msg


def get_response(prompt, previous_messages=[]):
    """
    Sends a request to the GPT model and retrieves the response.
    Incorporates previous dialogue for continuity.
    :param prompt: The current prompt to send.
    :param previous_messages: A list of previous messages and responses for continuity.
    :return: A tuple containing the updated messages list and the latest GPT response.
    """
    messages = previous_messages.copy()
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Add GPT's response to the messages list for context in future requests
    messages.append({"role": "assistant", "content": response.choices[0].message['content']})

    return messages, response.choices[0].message['content']


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
    mk_dir(output_dir)
    print(f'[Initialization] Create output folder at {output_dir}')

    # load .env
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("Let's get basic information of your request for GPT-3!")
        request_text = initial_request()
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        attempts = 0

        while attempts < 5:
            messages, responses = get_response(request_text, messages)
            generate_java_files = generate_java_file(responses, output_dir)
            all_files_valid = True

            for java_file in generate_java_files:
                error_msg = run_infer_on_file(java_file)
                if error_msg:
                    print(f"Error detected by Facebook Infer in {java_file}: {error_msg}"
                          f"\n ... Recall GPT-3 to recover it ...")
                    all_files_valid = False
                    os.remove(java_file)
                    break

            if all_files_valid:
                print("All Java files are valid. Process completed.")
                return
            else:
                attempts += 1
                print(f"Attempt {attempts}/5. Adjusting request...")

    else:
        print("No OpenAI API key found in environment. Proceeding to generate Java file based on input.")
        user_input = get_multi_line_input()
        generated_java_li = generate_java_file(user_input=user_input, output_dir=output_dir)
        for java_file in generated_java_li:
            run_infer_on_file(java_file)


if __name__ == '__main__':
    main()

