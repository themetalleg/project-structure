import os
import fnmatch
from typing import List


def load_gitignore_rules(gitignore_path: str) -> List:
    """
    Load and return the list of rules from a .gitignore file.

    Args:
        gitignore_path (str): The path to the .gitignore file.

    Returns:
        list: A list of rules defined in the .gitignore file.
    """
    rules = []  # Initialize an empty list to store rules.
    if os.path.exists(gitignore_path):  # Check if the file exists.
        with open(gitignore_path, 'r') as file:  # Open the file in read mode.
            for line in file:
                stripped_line = line.strip()  # Remove leading/trailing whitespace.
                # Skip empty lines and lines that start with '#'.
                if stripped_line and not stripped_line.startswith('#'):
                    rules.append(stripped_line)
    
    rules.append(".git/")  # Ensure the .git directory is always ignored.
    return rules


def should_ignore(path: str, ignore_rules: List) -> bool:
    """
    Determine if the path should be ignored based on the .gitignore rules.

    Args:
        path (str): The file or directory path to check.
        ignore_rules (list): The list of .gitignore rules.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    path = path.replace(os.sep, '/')  # Normalize path for cross-platform compatibility.
    for rule in ignore_rules:
        if rule.endswith('/'):
            rule = rule.rstrip('/')
            # Check if any part of the path matches the ignored directory.
            if any(rule == part for part in path.split('/')):
                return True
        elif fnmatch.fnmatch(path, rule):  # Match the path against the rule.
            return True
    return False


def is_text_file(file_name: str) -> bool:
    """
    Check if a file is likely to be a text file based on its extension.

    Args:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file is a text file, False otherwise.
    """
    # List of common text file extensions.
    text_file_extensions = ['.txt', '.py', '.html', '.css', '.js', '.md', '.json', '.xml', '.yml', '.ini', '.cfg', '.conf']
    return any(file_name.endswith(ext) for ext in text_file_extensions)


def collect_files(start_path: str, ignore_rules: List, output_filename: str) -> dict:
    """
    Recursively collect all files and directories, respecting .gitignore rules and ignoring the output file.

    Args:
        start_path (str): The starting directory path.
        ignore_rules (list): The list of .gitignore rules.
        output_filename (str): The name of the file where results are written.

    Returns:
        dict: A dictionary representing the structure of the project.
    """
    # Dictionary to store the project structure.
    project_structure = {}
    # List of common non-text file extensions.
    non_text_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.log', '.webp', '.ai', '.ttf', '.woff', '.woff2', '.eot']

    for root, dirs, files in os.walk(start_path):
        # Filter directories that should be ignored.
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_rules)]

        for file_name in files:
            full_file_path = os.path.join(root, file_name)
            relative_file_path = os.path.relpath(full_file_path, start_path)
            if relative_file_path == output_filename:
                continue  # Skip the output file specifically.
            if not should_ignore(relative_file_path, ignore_rules):
                file_extension = os.path.splitext(file_name)[1].lower()
                if file_extension in non_text_extensions or file_name.lower() == 'get-pip.py':
                    # Mark non-text files or specific files to ignore.
                    if root not in project_structure:
                        project_structure[root] = []
                    project_structure[root].append((full_file_path, "Content ignored due to file type or rules"))
                else:
                    # Read and store content of text files.
                    try:
                        with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        if root not in project_structure:
                            project_structure[root] = []
                        project_structure[root].append((full_file_path, content))
                    except UnicodeDecodeError:
                        # Handle files with decoding errors.
                        if root not in project_structure:
                            project_structure[root] = []
                        project_structure[root].append((full_file_path, "Content ignored due to decoding error"))

    return project_structure


def save_structure(structure: dict, output_path: str) -> None:
    """
    Save the collected file structure to a file.

    Args:
        structure (dict): The project structure to save.
        output_path (str): The file path where the structure should be saved.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        for path, files in structure.items():
            file.write(f"{10*'#'} Directory: {path} {10*'#'}\n")
            for file_name, content in files:
                file.write(f"{10*'-'} File: {file_name} {10*'-'}\n")
                file.write(f"{content}\n\n")


def main():
    """
    Main function to execute the script functionalities.
    """
    project_root = '.'  # Current directory, change if necessary
    output_file = 'project_structure.txt'  # Define the output filename
    gitignore_rules = load_gitignore_rules('.gitignore')  # Load .gitignore rules
    project_structure = collect_files(project_root, gitignore_rules, output_file)  # Collect project files
    save_structure(project_structure, output_file)  # Save the project structure
    print('Project structure has been saved to', output_file)


if __name__ == '__main__':
    main()
