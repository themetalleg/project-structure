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
    
    rules.append(".git/")  # Ensure .git directory is ignored
    return rules

def should_ignore(path, ignore_rules):
    """Determine if the path should be ignored based on the .gitignore rules."""
    path = path.replace(os.sep, '/')  # Normalize path for cross-platform compatibility
    for rule in ignore_rules:
        if rule.endswith('/'):
            rule = rule.rstrip('/')
            # Check entire path for presence of ignored directory
            if any(rule == part for part in path.split('/')):
                return True
        elif fnmatch.fnmatch(path, rule):
            return True
    return False

def is_text_file(file_name):
    """Check if a file is likely to be a text file based on its extension."""
    text_file_extensions = ['.txt', '.py', '.html', '.css', '.js', '.md', '.json', '.xml', '.yml', '.ini', '.cfg', '.conf']
    return any(file_name.endswith(ext) for ext in text_file_extensions)

def collect_files(start_path, ignore_rules, output_filename):
    """Recursively collect all files and directories, respecting .gitignore rules and ignoring the output file."""
    project_structure = {}
    non_text_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.log', '.webp', '.ai', '.ttf', '.woff', '.woff2', '.eot']

    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_rules)]  # Filter directories right away

        for file_name in files:
            full_file_path = os.path.join(root, file_name)
            relative_file_path = os.path.relpath(full_file_path, start_path)
            # Skip the output file specifically
            if relative_file_path == output_filename:
                continue
            if not should_ignore(relative_file_path, ignore_rules):
                file_extension = os.path.splitext(file_name)[1].lower()
                if file_extension in non_text_extensions or file_name.lower() == 'get-pip.py':
                    if root not in project_structure:
                        project_structure[root] = []
                    project_structure[root].append((full_file_path, "Content ignored due to file type or rules"))
                else:
                    try:
                        with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        if root not in project_structure:
                            project_structure[root] = []
                        project_structure[root].append((full_file_path, content))
                    except UnicodeDecodeError:
                        if root not in project_structure:
                            project_structure[root] = []
                        project_structure[root].append((full_file_path, "Content ignored due to decoding error"))

    return project_structure


def save_structure(structure, output_path):
    """Save the collected file structure to a file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        for path, files in structure.items():
            file.write(f"{10*'#'} Directory: {path} {10*'#'}\n")
            for file_name, content in files:
                file.write(f"{10*'-'} File: {file_name} {10*'-'}\n")
                file.write(f"{content}\n\n")

def main():
    project_root = '.'  # Current directory, change if necessary
    output_file = 'project_structure.txt'  # Define the output filename
    gitignore_rules = load_gitignore_rules('.gitignore')
    project_structure = collect_files(project_root, gitignore_rules, output_file)
    save_structure(project_structure, output_file)
    print('Project structure has been saved to', output_file)

if __name__ == '__main__':
    main()
