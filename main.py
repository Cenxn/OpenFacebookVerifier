import os
from dotenv import load_dotenv
import re
import subprocess
from openai import OpenAI

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

    class_definition_pattern = re.compile(r"\bclass\s+\w+(\s+\w+)*\s*{$")

    for line in user_input.split("\n"):
        # Detecting class definitions using regular expressions
        match = class_definition_pattern.search(line)
        if match and not in_class:
            words = line.split()
            class_name = words[words.index("class") + 1]
            in_class = True
            class_code = line + "\n"
            brace_counter += line.count("{")
        elif in_class:
            # Update brace_counter for open and close braces
            brace_counter += line.count("{")
            brace_counter -= line.count("}")
            class_code += line + "\n"
            if brace_counter == 0: # Check if the current class block has ended
                # Class ends when brace_counter returns to zero
                file_content = imports + class_code
                file_name = os.path.join(output_dir, f"{class_name}.java")
                with open(file_name, 'w') as file:
                    file.write(file_content)
                    file_paths.append(file_name)
                    print(f"[Generated] {file_name}")
                # Reset for next class processing
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
    error_msg = None
    try:
        result = subprocess.run(command, check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        if "ERROR" in result.stderr or "error:" in result.stderr:
            error_msg = result.stderr if result.stderr else result.stdout
            if "No issues found" in error_msg:
                error_msg = None
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
    mk_dir(output_dir)
    print(f'[Initialization] Create output folder at {output_dir}')

    # load .env
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        print("Let's get basic information of your request for GPT-3!")
        request_text = initial_request()
        messages_list = [{"role": "system", "content": "You are an AI programming assistant."
                                                       "Output the code in a single code block."
                                                       "Avoid wrapping the whole response in triple backticks."
                                                       "You can only give one reply for each conversation turn."}]
        attempts = 0

        while attempts < 5:
            messages_list, responses = get_response(request_text, previous_messages=messages_list)
            generate_java_files = generate_java_file(responses, output_dir)
            all_files_valid = True

            for java_file in generate_java_files:
                error_msg = run_infer_on_file(java_file)
                if error_msg:
                    error_info = f"There is a error detected by Facebook Infer in class {java_file}," \
                                 f" it report that: \n {error_msg}, please recover it, " \
                                 f"and regenerate the fixed class code."
                    print(f"Error detected by Facebook Infer in {java_file}: {error_msg}"
                          f"\n ... Recall GPT-3 to recover it ...")
                    all_files_valid = False
                    os.remove(java_file)
                    request_text = error_info
                    break

            if all_files_valid:
                print("All Java files are valid. Process completed.")
                break
            else:
                attempts += 1
                print(f"Attempt {attempts}/5. Adjusting request...")
        # Save messages_list to a text file after all attempts are complete
        log_file_path = os.path.join(output_dir, "dialogue_log.txt")
        with open(log_file_path, 'w') as log_file:
            for message in messages_list:
                log_file.write(f'{message["role"]}: {message["content"]}\n')
        print(f"Dialogue log saved to {log_file_path}")

    else:
        print("No OpenAI API key found in environment. Proceeding to generate Java file based on input.")
        user_input = get_multi_line_input()
        generated_java_li = generate_java_file(user_input=user_input, output_dir=output_dir)
        for java_file in generated_java_li:
            run_infer_on_file(java_file)


if __name__ == '__main__':
    main()

