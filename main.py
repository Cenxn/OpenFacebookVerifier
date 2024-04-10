import os
from dotenv import load_dotenv
import re
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

    class_regex = re.compile(r'(public\s+)?class\s+(\w+)\s*{.*?}', re.DOTALL)
    matches = class_regex.finditer(user_input)
    for match in matches:
        class_name = match.group(2)  # access class name
        class_code = match.group(0)  # access class code

        file_content = imports + class_code

        # Create a .java file for each class
        file_name = os.path.join(output_dir, f"{class_name}.java")
        with open(file_name, 'w') as file:
            file.write(file_content)
            file_paths.append(file_name)
            print(f"[Generated] {file_name}")

    return file_paths


def get_multi_line_input(msg="Enter text (type 'END' on a new line to finish): "):
    print(msg)
    lines = []
    while True:
        line = input()
        if line == "END":  # 用户输入END时结束输入
            break
        lines.append(line)
    return "\n".join(lines)


def run_infer_on_file(java_file_li):
    """
    Using Facebook Infer to Analyse Specified Java File
    :param java_file_li: Path to the Java file to be analysed
    :return:
    """
    command = [

    ]


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


if __name__ == '__main__':
    main()

