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
    except subprocess.CalledProcessError as e:
        print(f"Error running Infer: {e.stderr}")

def get_response(prompt):
    pass


def initial_request(prompt):
    pass


def main():
    mk_dir(output_dir)
    print(f'[Initialization] Create output folder at {output_dir}')

    # load .env
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        user_question = input("Enter your question for GPT-3: ")
    else:
        print("No OpenAI API key found in environment. Proceeding to generate Java file based on input.")
        user_input = get_multi_line_input()
        generated_java_li = generate_java_file(user_input=user_input, output_dir=output_dir)
        for java_file in generated_java_li:
            run_infer_on_file(java_file)


if __name__ == '__main__':
    main()

