import os
import sys

import pathspec


def load_gitignore(gitignore_path):
    """Load the .gitignore file and return a pathspec matcher."""
    with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
        gitignore_content = f.read()
    return pathspec.PathSpec.from_lines('gitwildmatch', gitignore_content.splitlines())


def is_binary_file(filepath):
    """Check if the file is a binary file by looking at its extension."""
    binary_extensions = (
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg',  # images
        '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',                # office files
        '.pdf',                                                           # pdf
        '.zip', '.tar', '.gz', '.rar', '.7z',                             # archives
        '.exe', '.dll', '.so', '.dylib',                                  # binaries
        '.ai',                                                            # adobe files
        '.otf', '.ttf',                                                   # font files
        '.json'                                                           # data files
    )
    return filepath.endswith(binary_extensions)


def collect_files_and_folders(root_dir, gitignore_spec, max_depth):
    """Collect all files and folders in the project directory, ignoring those specified in .gitignore and binary files."""
    collected_items = []
    root_depth = root_dir.rstrip(os.sep).count(os.sep)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_depth = dirpath.rstrip(os.sep).count(os.sep) - root_depth

        if current_depth > max_depth:
            # Skip directories beyond the max depth
            dirnames[:] = []
            continue

        relative_dirpath = os.path.relpath(dirpath, root_dir)
        if relative_dirpath == '.':
            relative_dirpath = ''

        # Exclude .git directory
        if '.git' in dirnames:
            dirnames.remove('.git')

        if 'tools' in dirnames:
            dirnames.remove('tools')

        # Check if the directory is ignored
        if gitignore_spec.match_file(relative_dirpath):
            continue

        # Collect directories
        for dirname in dirnames:
            relative_dirname = os.path.join(relative_dirpath, dirname)
            if not gitignore_spec.match_file(relative_dirname):
                collected_items.append(relative_dirname + '/')

        # Collect files
        for filename in filenames:
            relative_filepath = os.path.join(relative_dirpath, filename)
            if not gitignore_spec.match_file(relative_filepath) and not is_binary_file(relative_filepath):
                collected_items.append(relative_filepath)

    return collected_items


def read_file_contents(filepath):
    """Read and return the contents of a file, removing any NUL characters."""
    try:
        with open(filepath, 'rb') as f:
            contents = f.read()
            contents = contents.replace(b'\x00', b'')  # Remove NUL characters
            return contents.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Error reading {filepath}: {e}"


def save_structure_to_file(structure, root_dir, filepath):
    """Save the collected structure and contents to a file."""
    with open(filepath, 'w', encoding='utf-8', errors='ignore', newline='\n') as f:
        for item in structure:
            full_path = os.path.join(root_dir, item)
            if os.path.isdir(full_path):
                f.write(f"\n########## Directory: {item} ##########\n")
            else:
                f.write(f"\n########## File: {item} ##########\n")
                contents = read_file_contents(full_path)
                f.write(f"\nContents of {item}:\n{contents}\n")
                f.write("####################################\n")


def main():
    # Check if a root directory is provided as an argument, or prompt the user
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = input(
            "Please enter the root directory path (or press Enter to use current directory): ")
        if not project_root:
            # Use the script's directory as default
            project_root = os.path.dirname(os.path.abspath(__file__))

    # Validate the project root
    if not os.path.isdir(project_root):
        print(f"Error: {project_root} is not a valid directory.")
        return

    # Get the max depth from the user
    try:
        max_depth = int(input("Enter the maximum directory depth to collect: "))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    gitignore_path = '.gitignore'
    output_file = 'project_structure.txt'

    if not os.path.isfile(gitignore_path):
        print("No .gitignore file found")
        return

    gitignore_spec = load_gitignore(gitignore_path)
    collected_items = collect_files_and_folders(project_root, gitignore_spec, max_depth)

    save_structure_to_file(collected_items, project_root, output_file)
    print(f"Project structure saved to {output_file}")


if __name__ == "__main__":
    main()
