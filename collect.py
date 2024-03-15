import os
import fnmatch

def load_gitignore_rules(gitignore_path):
    """Load and return the list of rules from the .gitignore file."""
    rules = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as file:
            for line in file:
                stripped_line = line.strip()
                # Skip empty lines and comments
                if stripped_line and not stripped_line.startswith('#'):
                    rules.append(stripped_line)
    return rules

def should_ignore(path, ignore_rules):
    """Determine if the path should be ignored based on the .gitignore rules."""
    for rule in ignore_rules:
        # Check if rule applies to directories
        if rule.endswith('/'):
            directory = rule.rstrip('/')
            if directory in path.split(os.sep):
                return True
        elif fnmatch.fnmatch(path, rule):  # This line should be changed.
            return True
    return False


def is_text_file(file_name):
    """Check if a file is likely to be a text file based on its extension."""
    text_file_extensions = ['.txt', '.py', '.html', '.css', '.js', '.md', '.json', '.xml', '.yml', '.ini', '.cfg', '.conf']
    return any(file_name.endswith(ext) for ext in text_file_extensions)


def collect_files(start_path, ignore_rules):
    """Recursively collect all files and directories, respecting .gitignore rules."""
    project_structure = {}
    # Ensure this list is lowercase for case-insensitive comparison
    non_text_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.log', '.webp', '.ai', '.ttf', '.woff', '.woff2', '.eot']

    for root, dirs, files in os.walk(start_path):
        relative_root = os.path.relpath(root, start_path)

        # Check if current directory should be ignored
        if should_ignore(relative_root, ignore_rules):
            dirs[:] = []  # Don't walk into ignored directories
            continue

        for file_name in files:
            full_file_path = os.path.join(root, file_name)  # Full path
            relative_file_path = os.path.join(relative_root, file_name)  # Relative path from project root
            if not should_ignore(relative_file_path, ignore_rules):
                # Make comparison case-insensitive and ensure it starts with a dot
                file_extension = os.path.splitext(file_name)[1].lower()

                # Check if the file is a non-text file or the 'get-pip.py' file
                if file_extension in non_text_extensions or file_name.lower() == 'get-pip.py':
                    if relative_root not in project_structure:
                        project_structure[relative_root] = []
                    project_structure[relative_root].append((full_file_path, "Content ignored due to file type or rules"))
                else:
                    # It's considered a text file, so read and add its content
                    try:
                        with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        if relative_root not in project_structure:
                            project_structure[relative_root] = []
                        project_structure[relative_root].append((full_file_path, content))
                    except UnicodeDecodeError:
                        # Handle unexpected binary files that don't decode properly
                        if relative_root not in project_structure:
                            project_structure[relative_root] = []
                        project_structure[relative_root].append((full_file_path, "Content ignored due to decoding error"))

    return project_structure




def save_structure(structure, output_path):
    """Save the collected file structure to a file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        for path, files in structure.items():
            file.write(f"Directory: {path}\n")
            for file_name, content in files:
                file.write(f"  File: {file_name}\n")
                file.write(f"{content}\n\n")

def main():
    project_root = '.'  # Current directory, change if necessary
    gitignore_rules = load_gitignore_rules('.gitignore')
    project_structure = collect_files(project_root, gitignore_rules)
    save_structure(project_structure, 'project_structure.txt')
    print('Project structure has been saved to project_structure.txt')

if __name__ == '__main__':
    main()
