"""
ADO Integration Tools for LangGraph
Simple tools for ADO API calls with hardcoded credentials
"""

import os
import base64
import requests
import urllib.parse
from typing import Annotated, Optional, List, Dict
from langchain_core.tools import tool

# Hardcoded ADO Configuration
ADO_ORGANIZATION = "agentic-framework-hackathon"
ADO_PROJECT = "Agentic Framework"
PAT_TOKEN = ""

def _get_auth_header():
    """Get authentication header for ADO API calls"""
    credentials = f":{PAT_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

@tool
def read_requirements_file() -> str:
    """
    Read the requirements.md file from the current directory.
    
    Returns:
        Content of requirements.md file
    """
    try:
        requirements_file = "requirements.md"
        if not os.path.exists(requirements_file):
            return f"❌ Requirements file not found: {requirements_file}"
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"✅ Requirements file loaded successfully!\n\nContent:\n{content}"
        
    except Exception as e:
        return f"❌ Error reading requirements file: {str(e)}"

@tool
def test_ado_connection() -> str:
    """
    Test connection to Azure DevOps using hardcoded credentials.
    
    Returns:
        Connection test result
    """
    try:
        auth_header = _get_auth_header()
        
        # Test connection
        encoded_project = urllib.parse.quote(ADO_PROJECT)
        test_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/_apis/projects/{encoded_project}?api-version=7.0"
        response = requests.get(test_url, headers=auth_header, timeout=10)
        
        if response.status_code == 200:
            return f"✅ ADO connection successful!\nOrganization: {ADO_ORGANIZATION}\nProject: {ADO_PROJECT}"
        else:
            return f"❌ ADO connection failed: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error testing ADO connection: {str(e)}"

@tool
def check_existing_features(
    feature_name: Annotated[str, "Name of the feature to search for"]
) -> str:
    """
    Check if a feature with the given name already exists in ADO.
    
    Args:
        feature_name: Name of the feature to search for
        
    Returns:
        Feature search results
    """
    try:
        auth_header = _get_auth_header()
        encoded_project = urllib.parse.quote(ADO_PROJECT)
        
        # Query for Features using WIQL
        query_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{encoded_project}/_apis/wit/wiql?api-version=7.0"
        
        wiql_query = {
            "query": f"SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.WorkItemType] = 'Feature' AND [System.Title] CONTAINS '{feature_name}' ORDER BY [System.Id]"
        }
        
        headers = {**auth_header, "Content-Type": "application/json"}
        response = requests.post(query_url, json=wiql_query, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return f"❌ Could not search features: {response.status_code}"
        
        query_result = response.json()
        work_items = query_result.get('workItems', [])
        
        if not work_items:
            return f"✅ No existing feature found with name containing '{feature_name}'"
        
        # Get detailed information for found features
        feature_ids = [str(item['id']) for item in work_items]
        details_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{encoded_project}/_apis/wit/workitems?ids={','.join(feature_ids)}&$expand=fields&api-version=7.0"
        
        details_response = requests.get(details_url, headers=auth_header, timeout=30)
        
        if details_response.status_code != 200:
            return f"❌ Could not get feature details: {details_response.status_code}"
        
        features_data = details_response.json()
        result = f"🔍 Found {len(work_items)} existing features with name containing '{feature_name}':\n\n"
        
        for feature in features_data.get('value', []):
            fields = feature.get('fields', {})
            feature_id = feature.get('id')
            title = fields.get('System.Title', 'Untitled')
            state = fields.get('System.State', 'Unknown')
            url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_workitems/edit/{feature_id}"
            result += f"- ID: {feature_id} | Title: {title} | State: {state}\n  URL: {url}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error checking existing features: {str(e)}"

@tool
def create_ado_feature(
    feature_title: Annotated[str, "Title for the Feature"],
    feature_description: Annotated[str, "Description for the Feature"]
) -> str:
    """
    Create a Feature work item in Azure DevOps.
    
    Args:
        feature_title: Feature title
        feature_description: Feature description
        
    Returns:
        Feature creation result with ID
    """
    try:
        auth_header = _get_auth_header()
        
        # Create Feature
        encoded_project = urllib.parse.quote(ADO_PROJECT)
        api_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{encoded_project}/_apis/wit/workitems/$Feature?api-version=7.0"
        
        feature_data = [
            {"op": "add", "path": "/fields/System.Title", "value": feature_title},
            {"op": "add", "path": "/fields/System.Description", "value": feature_description},
            {"op": "add", "path": "/fields/System.Tags", "value": "PowerBI;Fabric;Generated"}
        ]
        
        headers = {**auth_header, "Content-Type": "application/json-patch+json"}
        response = requests.post(api_url, json=feature_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            feature = response.json()
            feature_id = feature.get('id')
            feature_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_workitems/edit/{feature_id}"
            return f"✅ Feature created successfully!\nID: {feature_id}\nTitle: {feature_title}\nURL: {feature_url}"
        else:
            return f"❌ Failed to create Feature: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error creating Feature: {str(e)}"

@tool
def create_ado_user_story(
    story_title: Annotated[str, "Title for the User Story"],
    story_description: Annotated[str, "Description/content for the User Story"],
    parent_feature_id: Annotated[str, "ID of parent Feature to link to"]
) -> str:
    """
    Create a User Story work item in Azure DevOps.
    
    Args:
        story_title: User Story title
        story_description: User Story description/content
        parent_feature_id: Parent Feature ID to link to
        
    Returns:
        User Story creation result with ID
    """
    try:
        auth_header = _get_auth_header()
        
        # Create User Story
        encoded_project = urllib.parse.quote(ADO_PROJECT)
        api_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{encoded_project}/_apis/wit/workitems/$User%20Story?api-version=7.0"
        
        work_item_data = [
            {"op": "add", "path": "/fields/System.Title", "value": story_title},
            {"op": "add", "path": "/fields/System.Description", "value": story_description},
            {"op": "add", "path": "/fields/System.Tags", "value": "PowerBI;Fabric;Generated"},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": 2},
            {
                "op": "add",
                "path": "/relations/-", 
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"https://dev.azure.com/{ADO_ORGANIZATION}/{encoded_project}/_apis/wit/workItems/{parent_feature_id}"
                }
            }
        ]
        
        headers = {**auth_header, "Content-Type": "application/json-patch+json"}
        response = requests.post(api_url, json=work_item_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            story = response.json()
            story_id = story.get('id')
            story_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_workitems/edit/{story_id}"
            return f"✅ User Story created successfully!\nID: {story_id}\nTitle: {story_title}\nURL: {story_url}"
        else:
            return f"❌ Failed to create User Story: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error creating User Story: {str(e)}"

@tool
def create_ado_task(
    task_title: Annotated[str, "Title for the Task"],
    task_description: Annotated[str, "Description for the Task"],
    parent_story_id: Annotated[str, "ID of parent User Story to link to"]
) -> str:
    """
    Create a Task work item in Azure DevOps.
    
    Args:
        task_title: Task title
        task_description: Task description
        parent_story_id: Parent User Story ID to link to
        
    Returns:
        Task creation result with ID
    """
    try:
        auth_header = _get_auth_header()
        
        # Create Task
        encoded_project = urllib.parse.quote(ADO_PROJECT)
        api_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{encoded_project}/_apis/wit/workitems/$Task?api-version=7.0"
        
        work_item_data = [
            {"op": "add", "path": "/fields/System.Title", "value": task_title},
            {"op": "add", "path": "/fields/System.Description", "value": task_description},
            {"op": "add", "path": "/fields/System.Tags", "value": "PowerBI;Fabric;Generated;Task"},
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse", 
                    "url": f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_apis/wit/workItems/{parent_story_id}"
                }
            }
        ]
        
        headers = {**auth_header, "Content-Type": "application/json-patch+json"}
        response = requests.post(api_url, json=work_item_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            task = response.json()
            task_id = task.get('id')
            task_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_workitems/edit/{task_id}"
            return f"✅ Task created successfully!\nID: {task_id}\nTitle: {task_title}\nURL: {task_url}"
        else:
            return f"❌ Failed to create Task: {response.status_code} - {response.text}"
            
    except Exception as e:

        return f"❌ Error creating Task: {str(e)}"
