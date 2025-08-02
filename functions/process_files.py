import os
import subprocess


def get_files_info(working_directory, directory="."):
    real_working_dir = os.path.abspath(working_directory)
    joined_path = os.path.join(real_working_dir, directory)
    joined_real_path = os.path.abspath(joined_path)
    passed = check_directory(real_working_dir, joined_real_path, directory)

    if passed == "yes":
        file_info_str = f"result for '{directory}' directory\n"
        for entry in os.listdir(joined_real_path):
            file_info_str += f"- {entry}: file_size={os.path.getsize(f"{joined_real_path}/{entry}")}bytes, is_dir={os.path.isdir(f"{joined_real_path}/{entry}")}\n"
        return file_info_str
    else:
        return passed


def get_file_content(working_directory, file_path):
    real_working_dir = os.path.abspath(working_directory)
    joined_path = os.path.join(real_working_dir, file_path)
    joined_real_path = os.path.abspath(joined_path)
    passed = check_directory(real_working_dir, joined_real_path, file_path)

    if passed == "yes":
        if os.path.isfile(joined_real_path):
            with open(joined_real_path, "r") as file:
                file_contents = file.read(10000)
                return file_contents
        else:
            return f'Error: File not found or is not a regular file: "{file_path}"'
    else:
        return passed


def write_file(working_directory, file_path, content):
    real_working_dir = os.path.abspath(working_directory)
    joined_path = os.path.join(real_working_dir, file_path)
    joined_real_path = os.path.abspath(joined_path)
    passed = check_directory(real_working_dir, joined_real_path, file_path)

    if passed == "yes" or passed == f'Error: "{file_path}" is not a directory':
        try:
            with open(joined_real_path, "w") as file:
                file_contents = file.write(content)
                return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        except Exception as e:
            return f"Error Writing to file {e}"
    else:
        return passed


def run_python_file(working_directory, file_path, args=[]):
    real_working_dir = os.path.abspath(working_directory)
    joined_path = os.path.join(real_working_dir, file_path)
    joined_real_path = os.path.abspath(joined_path)
    passed = check_directory(real_working_dir, joined_real_path, file_path)

    if passed == f'Error: "{file_path}" is not a directory':
        return print(f'Error: File "{file_path}" not found.')
    elif file_path[-3:] != ".py":
        return print(f'Error: "{file_path}" is not a Python file.')
    elif passed == "yes":
        try:
            cmd = ["python3", joined_real_path] + args
            result = subprocess.run(
                cmd,
                timeout=30,
                capture_output=True,
                text=True,
            )
        except Exception as e:
            return f"Error: executing Python file: {e}"

        print(
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\n{result.returncode}"
        )
    elif (
        passed
        == f'Error: Cannot list "{file_path}" as it is outside the permitted working directory'
    ):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'


def check_directory(real_working_dir, joined_real_path, directory=None):

    if os.path.commonpath([real_working_dir, joined_real_path]) != real_working_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if directory == None:
        return "No directory provided"
    if os.path.exists(joined_real_path) == False:
        return f'Error: "{directory}" is not a directory'
    if joined_real_path.startswith(real_working_dir):
        return "yes"
