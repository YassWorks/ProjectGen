import os
from langchain_core.tools import tool

@tool
def create_wd(path: str) -> None:
    """Creates a working directory at the specified path."""
    # try:
    #     os.makedirs(path, exist_ok=True)
    #     return f"Working directory created at {path}"
    # except Exception as e:
    #     return f"Error creating working directory: {str(e)}"
    pass
    
@tool
def create_file(file_path: str, content: str) -> None:
    """Creates a file with the specified content. Can be used to insert code into a new file."""
    # try:
    #     # ensure the directory exists
    #     os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
    #     with open(file_path, 'w') as f:
    #         f.write(content)
    #     return f"File created at {file_path}"
    # except Exception as e:
    #     return f"Error creating file: {str(e)}"
    pass
    
@tool
def modify_file(file_path: str, old_content: str, new_content: str) -> None:
    """
    Modifies a file by replacing old content with new content.
    Args:
        file_path (str): The path to the file to be modified.
        old_content (str): The content to be replaced which must exactly match the contents in the file including whitespaces.
        new content (str): The new content to replace the old content with.
    """
    # try:
    #     with open(file_path, 'a') as f:
    #         contents = f.read()
    #         contents.replace(old_content, new_content, 1)
    #         f.write(contents)
    #     return f"File modified at {file_path}"
    # except Exception as e:
    #     return f"Error modifying file: {str(e)}"
    pass
    
@tool
def delete_file(file_path: str) -> None:
    """Deletes a file at the specified path."""
    # try:
    #     os.remove(file_path)
    #     return f"File deleted at {file_path}"
    # except Exception as e:
    #     return f"Error deleting file: {str(e)}"
    pass