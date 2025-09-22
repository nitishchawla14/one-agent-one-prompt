"""
Simple Requirements Generator Tool for LangGraph
Just reads SOW and Rules files and creates requirements.md
"""

import os
from typing import Annotated
from datetime import datetime
from langchain_core.tools import tool

@tool
def read_sow_and_rules() -> str:
    """
    Read the SOW and Rules files from the current directory.
    This tool reads sample_sow.md and FabricPowerBIRules.md files.
    
    Returns:
        Content of sample_sow.md and FabricPowerBIRules.md files
    """
    try:
        current_dir = os.getcwd()
        print(f"Current working directory: {current_dir}")
        
        # List files in current directory for debugging
        files_in_dir = os.listdir(current_dir)
        print(f"Files in directory: {files_in_dir}")
        
        # Read SOW file
        sow_file = "sample_sow.md"
        sow_full_path = os.path.join(current_dir, sow_file)
        
        if not os.path.exists(sow_full_path):
            return f"❌ SOW file not found: {sow_full_path}\nFiles in directory: {files_in_dir}"
        
        with open(sow_full_path, 'r', encoding='utf-8') as f:
            sow_content = f.read()
        
        print(f"✅ SOW file read successfully. Length: {len(sow_content)} characters")
        
        # Read Rules file  
        rules_file = "FabricPowerBIRules.md"
        rules_full_path = os.path.join(current_dir, rules_file)
        
        if not os.path.exists(rules_full_path):
            return f"❌ Rules file not found: {rules_full_path}\nFiles in directory: {files_in_dir}"
            
        with open(rules_full_path, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        print(f"✅ Rules file read successfully. Length: {len(rules_content)} characters")
        
        return f"""✅ Files read successfully!

SOW CONTENT (Length: {len(sow_content)} characters):
---START SOW---
{sow_content}
---END SOW---

RULES CONTENT (Length: {len(rules_content)} characters):
---START RULES---
{rules_content}
---END RULES---"""
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ Error reading files: {str(e)}\n\nFull error details:\n{error_details}"

@tool
def save_requirements_file(
    content: Annotated[str, "The requirements content to save"]
) -> str:
    """
    Save the generated requirements content to requirements.md file.
    If the file exists, it will be replaced.
    
    Args:
        content: The requirements document content
        
    Returns:
        Success message with file details
    """
    try:
        current_dir = os.getcwd()
        filename = "requirements.md"
        full_path = os.path.join(current_dir, filename)
        
        print(f"Saving to: {full_path}")
        print(f"Content length: {len(content)} characters")
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = os.path.getsize(full_path)
        
        return f"✅ Requirements file saved successfully!\n📄 File: {full_path}\n📊 Size: {file_size} bytes"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ Error saving file: {str(e)}\n\nFull error details:\n{error_details}"

@tool
def list_current_directory() -> str:
    """
    List all files in the current directory for debugging purposes.
    
    Returns:
        List of files in the current directory
    """
    try:
        current_dir = os.getcwd()
        files = os.listdir(current_dir)
        
        result = f"Current directory: {current_dir}\n\nFiles found:\n"
        for file in sorted(files):
            if os.path.isfile(file):
                size = os.path.getsize(file)
                result += f"📄 {file} ({size} bytes)\n"
            else:
                result += f"📁 {file}/\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"