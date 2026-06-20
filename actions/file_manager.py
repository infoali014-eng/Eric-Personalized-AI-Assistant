import os
import shutil

def handle_create_file(command):
    filepath = command.get("path") or command.get("target")
    content = command.get("content", "")
    if not filepath:
        return "File path unspecified"
        
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Created file {os.path.basename(filepath)}"
    except Exception as e:
        return f"Failed to create file: {e}"

def handle_delete_file(command):
    filepath = command.get("path") or command.get("target")
    if not filepath:
        return "File path unspecified"
        
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return f"Deleted file {os.path.basename(filepath)}"
        else:
            return "File not found"
    except Exception as e:
        return f"Failed to delete file: {e}"

def handle_create_folder(command):
    folderpath = command.get("path") or command.get("target")
    if not folderpath:
        return "Folder path unspecified"
        
    try:
        os.makedirs(folderpath, exist_ok=True)
        return f"Created folder {os.path.basename(folderpath)}"
    except Exception as e:
        return f"Failed to create folder: {e}"

def handle_delete_folder(command):
    folderpath = command.get("path") or command.get("target")
    if not folderpath:
        return "Folder path unspecified"
        
    try:
        if os.path.exists(folderpath):
            shutil.rmtree(folderpath, ignore_errors=True)
            return f"Deleted folder {os.path.basename(folderpath)}"
        else:
            return "Folder not found"
    except Exception as e:
        return f"Failed to delete folder: {e}"

def handle_rename_file(command):
    old_path = command.get("path")
    new_path = command.get("target")
    if not old_path or not new_path:
        return "Source or target path unspecified for rename"
        
    try:
        os.rename(old_path, new_path)
        return f"Renamed {os.path.basename(old_path)} to {os.path.basename(new_path)}"
    except Exception as e:
        return f"Failed to rename file: {e}"
