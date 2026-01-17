"""
File Operations Handler
Handles all file and folder operations
"""

import os
import glob
import shutil
import zipfile
import tarfile


class FileOperations:
    def __init__(self):
        pass
    
    def create_folder(self, folder_path):
        """Create a new folder"""
        try:
            if not folder_path or not isinstance(folder_path, str):
                return {"status": "error", "message": "Invalid folder path provided."}
            if os.path.exists(folder_path):
                return {"status": "skipped", "message": f"The folder '{folder_path}' already exists."}
            os.makedirs(folder_path)
            return {"status": "success", "message": f"Successfully created the folder at '{folder_path}'."}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
    
    def create_file(self, file_path, content):
        """Create a new file with content"""
        try:
            if not file_path or not isinstance(file_path, str):
                return {"status": "error", "message": "Invalid file path provided."}
            if os.path.exists(file_path):
                return {"status": "skipped", "message": f"The file '{file_path}' already exists."}
            with open(file_path, 'w') as f:
                f.write(content)
            return {"status": "success", "message": f"Successfully created the file at '{file_path}'."}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred while creating the file: {str(e)}"}
    
    def edit_file(self, file_path, content):
        """Append content to an existing file"""
        try:
            if not file_path or not isinstance(file_path, str):
                return {"status": "error", "message": "Invalid file path provided."}
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"The file '{file_path}' does not exist. Please create it first."}
            with open(file_path, 'a') as f:
                f.write(f"\n{content}")
            return {"status": "success", "message": f"Successfully appended content to the file at '{file_path}'."}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred while editing the file: {str(e)}"}
    
    def list_files(self, directory_path):
        """List all files in a directory"""
        try:
            path_to_list = directory_path if directory_path else '.'
            if not isinstance(path_to_list, str):
                return {"status": "error", "message": "Invalid directory path provided."}
            if not os.path.isdir(path_to_list):
                return {"status": "error", "message": f"The path '{path_to_list}' is not a valid directory."}
            files = os.listdir(path_to_list)
            return {
                "status": "success", 
                "message": f"Found {len(files)} items in '{path_to_list}'.", 
                "files": files, 
                "directory_path": path_to_list
            }
        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
    
    def read_file(self, file_path):
        """Read the contents of a file"""
        try:
            if not file_path or not isinstance(file_path, str):
                return {"status": "error", "message": "Invalid file path provided."}
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"The file '{file_path}' does not exist."}
            if not os.path.isfile(file_path):
                return {"status": "error", "message": f"The path '{file_path}' is not a file."}
            with open(file_path, 'r') as f:
                content = f.read()
            return {
                "status": "success", 
                "message": f"Successfully read the file '{file_path}'.", 
                "content": content
            }
        except Exception as e:
            return {"status": "error", "message": f"An error occurred while reading the file: {str(e)}"}
    
    def file_management(self, operation, source_path=None, target_path=None, 
                    search_pattern=None, file_type=None):
        """Advanced file management operations"""
        try:
            if operation == "search":
                if not search_pattern:
                    return {"status": "error", "message": "Search pattern required"}
                
                results = []
                search_dir = source_path or "."
                
                if file_type:
                    pattern = f"**/*{search_pattern}*{file_type}"
                else:
                    pattern = f"**/*{search_pattern}*"
                
                for file_path in glob.glob(os.path.join(search_dir, pattern), recursive=True):
                    results.append(file_path)
                
                return {"status": "success", "message": f"Found {len(results)} files", "results": results}
            
            elif operation == "move":
                if not source_path or not target_path:
                    return {"status": "error", "message": "Source and target paths required"}
                
                shutil.move(source_path, target_path)
                return {"status": "success", "message": f"Moved {source_path} to {target_path}"}
            
            elif operation == "rename":
                if not source_path or not target_path:
                    return {"status": "error", "message": "Source and target paths required"}
                
                os.rename(source_path, target_path)
                return {"status": "success", "message": f"Renamed {source_path} to {target_path}"}
            
            elif operation == "delete":
                if not source_path:
                    return {"status": "error", "message": "Source path required"}
                
                if os.path.isdir(source_path):
                    shutil.rmtree(source_path)
                    return {"status": "success", "message": f"Deleted directory {source_path}"}
                else:
                    os.remove(source_path)
                    return {"status": "success", "message": f"Deleted file {source_path}"}
            
            elif operation == "organize":
                if not source_path:
                    source_path = "."
                
                organized_count = 0
                for file_path in glob.glob(os.path.join(source_path, "*")):
                    if os.path.isfile(file_path):
                        file_ext = os.path.splitext(file_path)[1].lower()
                        if file_ext:
                            ext_folder = os.path.join(source_path, file_ext[1:].upper() + "_FILES")
                            os.makedirs(ext_folder, exist_ok=True)
                            shutil.move(file_path, os.path.join(ext_folder, os.path.basename(file_path)))
                            organized_count += 1
                
                return {"status": "success", "message": f"Organized {organized_count} files"}
            
            elif operation == "copy":
                if not source_path or not target_path:
                    return {"status": "error", "message": "Source and target paths required"}
                
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy2(source_path, target_path)
                
                return {"status": "success", "message": f"Copied {source_path} to {target_path}"}
            
            else:
                return {"status": "error", "message": "Invalid file management operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"File operation failed: {str(e)}"}
    
    def archive_operations(self, operation, source_path, target_path, format="zip"):
        """Compress and extract files"""
        try:
            if operation == "compress":
                if format == "zip":
                    with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        if os.path.isdir(source_path):
                            for root, dirs, files in os.walk(source_path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    zipf.write(file_path, os.path.relpath(file_path, source_path))
                        else:
                            zipf.write(source_path, os.path.basename(source_path))
                
                elif format in ["tar", "tar.gz"]:
                    mode = "w:gz" if format == "tar.gz" else "w"
                    with tarfile.open(target_path, mode) as tarf:
                        tarf.add(source_path, arcname=os.path.basename(source_path))
                
                return {"status": "success", "message": f"Compressed {source_path} to {target_path}"}
            
            elif operation == "extract":
                if target_path.endswith('.zip'):
                    with zipfile.ZipFile(source_path, 'r') as zipf:
                        zipf.extractall(target_path)
                
                elif source_path.endswith(('.tar', '.tar.gz', '.tgz')):
                    with tarfile.open(source_path, 'r:*') as tarf:
                        tarf.extractall(target_path)
                
                return {"status": "success", "message": f"Extracted {source_path} to {target_path}"}
            
            else:
                return {"status": "error", "message": "Invalid archive operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"Archive operation failed: {str(e)}"}