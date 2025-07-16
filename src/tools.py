import os
from langchain_core.tools import tool


@tool
def create_wd(path: str) -> None:
    """
    Creates a working directory at the specified path.
    
    This tool creates a new directory (folder) at the given path. It will create
    all necessary parent directories if they don't exist. Use this when you need
    to establish a project structure or create folders for file organization.
    
    Args:
        path (str): The absolute or relative path where the directory should be created.
                   Examples: "project_folder", "/home/user/documents/new_project", 
                   "src/utils", "tests/unit"
    
    Returns:
        None: This tool doesn't return a value but creates the directory structure.
    
    Use cases:
        - Setting up project folder structure
        - Creating directories before placing files in them
        - Organizing code into logical folder hierarchies
        - Preparing workspace for file operations
    
    Note: This operation is safe - it won't fail if the directory already exists.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Working directory created at {path}"
    except Exception as e:
        return f"Error creating working directory: {str(e)}"


@tool
def create_file(file_path: str, content: str) -> None:
    """
    Creates a new file with the specified content at the given path.
    
    This tool creates a new file and writes the provided content to it. If the
    directory structure doesn't exist, it will be created automatically. Use this
    when you need to generate new files such as source code, configuration files,
    documentation, or any text-based files.
    
    Args:
        file_path (str): The path where the file should be created. Can be absolute
                        or relative. Examples: "main.py", "src/utils/helpers.py",
                        "config/settings.json", "README.md"
        content (str): The text content to write to the file. This can be code,
                      configuration, documentation, or any string content.
                      Use proper formatting and indentation as needed.
    
    Returns:
        None: This tool doesn't return a value but creates the file with content.
    
    Use cases:
        - Creating new source code files (Python, JavaScript, etc.)
        - Generating configuration files (JSON, YAML, INI, etc.)
        - Writing documentation files (Markdown, text files)
        - Creating template files or boilerplate code
        - Establishing project files (package.json, requirements.txt, etc.)
    
    Important: This creates a NEW file. If the file already exists, it will be
    overwritten. Use modify_file() to update existing files.
    """
    try:
        # ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        return f"File created at {file_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"


@tool
def modify_file(file_path: str, old_content: str, new_content: str) -> None:
    """
    Modifies an existing file by replacing specific content with new content.
    
    This tool performs precise content replacement in an existing file. It finds
    the exact match of old_content and replaces it with new_content. This is ideal
    for updating specific sections of code, fixing bugs, or making targeted changes
    without rewriting entire files.
    
    Args:
        file_path (str): The path to the existing file that needs to be modified.
                        Examples: "src/main.py", "config/app.json", "README.md"
        old_content (str): The exact content to be replaced. This must match
                          EXACTLY including all whitespace, indentation, and
                          line breaks. Even a single space difference will
                          prevent the replacement from working.
        new_content (str): The new content that will replace the old_content.
                          This can be shorter, longer, or the same length as
                          the old content. Maintain proper formatting and
                          indentation as needed.
    
    Returns:
        None: This tool doesn't return a value but modifies the file content.
    
    Use cases:
        - Fixing bugs in existing code
        - Updating function implementations
        - Modifying configuration values
        - Refactoring code sections
        - Updating documentation
        - Changing variable names or values
    
    Important considerations:
        - The old_content must match EXACTLY (including whitespace)
        - Only the FIRST occurrence of old_content will be replaced
        - The file must exist before using this tool
        - Use create_file() for new files instead
    
    Best practices:
        - Include enough context in old_content to ensure unique matching
        - Preserve indentation and formatting in new_content
        - Test the exact string match before using this tool
    """
    try:
        with open(file_path, 'a') as f:
            contents = f.read()
            contents.replace(old_content, new_content, 1)
            f.write(contents)
        return f"File modified at {file_path}"
    except Exception as e:
        return f"Error modifying file: {str(e)}"


@tool
def delete_file(file_path: str) -> None:
    """
    Deletes a file at the specified path.
    
    This tool permanently removes a file from the filesystem. Use this when you
    need to clean up temporary files, remove outdated files, or delete files
    that are no longer needed in your project.
    
    Args:
        file_path (str): The path to the file that should be deleted. Can be
                        absolute or relative. Examples: "temp.txt", 
                        "src/old_module.py", "logs/debug.log"
    
    Returns:
        None: This tool doesn't return a value but removes the specified file.
    
    Use cases:
        - Cleaning up temporary or cache files
        - Removing outdated source files
        - Deleting log files or debug outputs
        - Removing files that were created by mistake
        - Cleaning up before project restructuring
    
    Important warnings:
        - This operation is PERMANENT and cannot be undone
        - The file will be completely removed from the filesystem
        - Make sure you have backups if the file contains important data
        - The file must exist or an error will occur
    
    Safety considerations:
        - Double-check the file path before deletion
        - Consider moving files to a backup location first
        - Be especially careful with important project files
        - This tool only deletes files, not directories
    """
    try:
        os.remove(file_path)
        return f"File deleted at {file_path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"
