import os
from langchain_core.tools import tool


@tool
def create_wd(path: str) -> None:
    """
    **PRIMARY PURPOSE**: Creates a new directory/folder at the specified path.

    **WHEN TO USE**:
    - When you need to create a new folder structure for organizing files
    - Before creating files in a directory that doesn't exist yet
    - Setting up project directories like "src/", "tests/", "docs/", etc.
    - Creating nested folder structures in one operation

    **BEHAVIOR**:
    - Creates the directory and ALL parent directories if they don't exist
    - Will NOT fail if the directory already exists (safe to use repeatedly)
    - Similar to running "mkdir -p" in terminal

    **PARAMETERS**:
        path (str): The directory path to create. Can be:
                   - Relative: "my_project", "src/utils", "tests/unit"
                   - Absolute: "/home/user/projects/new_app", "C:/projects/app"
                   - Nested: "deep/nested/folder/structure"

    **RETURNS**:
        str: Success message with created path, or error message if failed

    **EXAMPLES**:
        create_wd("my_new_project")           # Creates folder in current directory
        create_wd("src/components")           # Creates nested structure
        create_wd("/home/user/workspace")     # Creates with absolute path
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Working directory created at {path}"
    except Exception as e:
        return f"Error creating working directory: {str(e)}"


@tool
def create_file(file_path: str, content: str) -> None:
    """
    **PRIMARY PURPOSE**: Creates a brand new file with specified content.

    **WHEN TO USE**:
    - Creating new source code files (.py, .js, .html, etc.)
    - Generating configuration files (.json, .yaml, .ini, etc.)
    - Writing documentation files (.md, .txt, .rst)
    - Creating project setup files (requirements.txt, package.json, etc.)
    - Establishing template or boilerplate files

    **BEHAVIOR**:
    - Creates ALL necessary parent directories automatically
    - OVERWRITES existing files without warning
    - Writes content exactly as provided (preserves formatting)

    **PARAMETERS**:
        file_path (str): Where to create the file. Examples:
                        - "main.py" (current directory)
                        - "src/utils/helper.py" (creates src/utils/ if needed)
                        - "/absolute/path/config.json"
        content (str): Exact text content for the file. Include proper:
                      - Indentation and whitespace
                      - Line breaks (\n)
                      - Code syntax and formatting

    **RETURNS**:
        str: Success message with file path, or error message if failed

    **WARNING**: This OVERWRITES existing files! Use modify_file() for edits.

    **EXAMPLES**:
        create_file("app.py", "print('Hello World')")
        create_file("config/db.json", '{"host": "localhost"}')
        create_file("README.md", "# My Project\n\nDescription here")
    """
    try:
        # ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)
        return f"File created at {file_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"


@tool
def modify_file(file_path: str, old_content: str, new_content: str) -> str:
    """
    **PRIMARY PURPOSE**: Updates existing files by replacing specific content.

    **WHEN TO USE**:
    - Fixing bugs in existing code
    - Updating function implementations
    - Changing configuration values
    - Refactoring specific code sections
    - Updating imports or variable names
    - Making targeted edits without rewriting entire files

    **BEHAVIOR**:
    - Finds EXACT match of old_content and replaces with new_content
    - Only replaces the FIRST occurrence found
    - File must already exist (use create_file() for new files)
    - Preserves all other file content unchanged

    **PARAMETERS**:
        file_path (str): Path to existing file to modify
        old_content (str): EXACT text to replace (must match perfectly including:
                          - All whitespace and indentation
                          - Line breaks and spacing
                          - Capitalization and punctuation)
        new_content (str): Replacement text (can be longer/shorter than original)

    **RETURNS**:
        str: Success message, "Content not found" error, or other error message

    **CRITICAL**: old_content must match EXACTLY or replacement will fail!

    **EXAMPLES**:
        modify_file("app.py", "def hello():\n    print('hi')", "def hello():\n    print('Hello World!')")
        modify_file("config.json", '"debug": false', '"debug": true')
    """
    try:
        with open(file_path, "r") as f:
            contents = f.read()

        if old_content not in contents:
            return f"Content not found in {file_path}"

        contents = contents.replace(old_content, new_content, 1)

        with open(file_path, "w") as f:
            f.write(contents)
        return f"File modified at {file_path}"
    except Exception as e:
        return f"Error modifying file: {str(e)}"


@tool
def delete_file(file_path: str) -> str:
    """
    **PRIMARY PURPOSE**: Permanently removes a file from the filesystem.

    **WHEN TO USE**:
    - Cleaning up temporary or cache files
    - Removing outdated source files
    - Deleting log files or debug outputs
    - Removing files created by mistake
    - Cleaning up before project restructuring

    **BEHAVIOR**:
    - PERMANENTLY deletes the file (cannot be undone)
    - Only works on files, not directories
    - Will fail if file doesn't exist

    **PARAMETERS**:
        file_path (str): Path to file to delete. Examples:
                        - "temp.txt"
                        - "src/old_module.py"
                        - "logs/debug.log"

    **RETURNS**:
        str: Success message with deleted path, or error message if failed

    **DANGER**: This operation is PERMANENT and IRREVERSIBLE!

    **SAFETY TIPS**:
    - Double-check file path before deletion
    - Consider backing up important files first
    - This tool only deletes FILES, not directories

    **EXAMPLES**:
        delete_file("temp.log")              # Remove temporary file
        delete_file("old_code.py")           # Remove outdated source
        delete_file("cache/session.tmp")     # Clean cache file
    """
    try:
        os.remove(file_path)
        return f"File deleted at {file_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"


@tool
def read_file(file_path: str) -> str:
    """
    **PRIMARY PURPOSE**: Reads and returns the complete content of any text file.

    **WHEN TO USE**:
    - Examining existing code before making changes
    - Reading configuration files to understand settings
    - Reviewing documentation or README files
    - Checking file contents to determine what modifications are needed
    - Understanding project structure and existing implementations

    **BEHAVIOR**:
    - Returns the ENTIRE file content as a single string
    - Preserves all formatting, indentation, and line breaks
    - Works with any text-based file format
    - Will fail if file doesn't exist or isn't readable

    **PARAMETERS**:
        file_path (str): Path to file to read. Examples:
                        - "main.py" (current directory)
                        - "src/config.json"
                        - "docs/README.md"
                        - "/absolute/path/to/file.txt"

    **RETURNS**:
        str: Complete file contents, or error message if file cannot be read

    **USE BEFORE**: Making changes to understand current file state

    **EXAMPLES**:
        read_file("package.json")            # Check project dependencies
        read_file("src/main.py")             # Review source code
        read_file("config/settings.ini")     # Read configuration
    """
    try:
        with open(file_path, "r") as f:
            contents = f.read()
        return contents
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def list_directory(path: str = ".", max_depth: int = None) -> str:
    """
    **PRIMARY PURPOSE**: Shows all files and folders in a directory tree structure.

    **WHEN TO USE**:
    - Exploring an unknown codebase structure
    - Understanding project organization before making changes
    - Finding where specific types of files are located
    - Getting an overview of a directory's contents
    - Discovering what files exist in nested folders

    **BEHAVIOR**:
    - Recursively explores all subdirectories
    - Shows hierarchical structure with indentation
    - Uses emojis to distinguish files (📄) from folders (📁)
    - Can limit exploration depth to avoid overwhelming output

    **PARAMETERS**:
        path (str): Directory to explore. Defaults to current directory (".")
                   Examples: ".", "src", "/absolute/path/to/folder"
        max_depth (int): Maximum levels deep to explore. None = unlimited
                        Examples: 1 (only immediate children), 3 (up to 3 levels)

    **RETURNS**:
        str: Formatted tree view of all files and directories

    **USEFUL FOR**: Getting bearings in unfamiliar codebases

    **EXAMPLES**:
        list_directory(".")                  # Show current directory structure
        list_directory("src", max_depth=2)   # Explore src/ up to 2 levels deep
        list_directory("/project/root")      # Show absolute path contents
    """

    def _list_directory_recursive(current_path: str, current_depth: int = 0) -> list:
        """Helper function to recursively build directory tree"""
        items = []

        if max_depth is not None and current_depth >= max_depth:
            return items

        try:
            all_items = os.listdir(current_path)
            dirs = []
            files = []

            for item in all_items:
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    dirs.append(item)
                else:
                    files.append(item)

            indent = "  " * current_depth

            for file_name in sorted(files):
                items.append(f"{indent}📄 {file_name}")

            for dir_name in sorted(dirs):
                items.append(f"{indent}📁 {dir_name}/")

                subdir_path = os.path.join(current_path, dir_name)
                sub_items = _list_directory_recursive(subdir_path, current_depth + 1)
                items.extend(sub_items)

        except PermissionError:
            items.append(f"{indent}❌ Permission denied")
        except Exception as e:
            items.append(f"{indent}❌ Error: {str(e)}")

        return items

    try:
        items = _list_directory_recursive(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
