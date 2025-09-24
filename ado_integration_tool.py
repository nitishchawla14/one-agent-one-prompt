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

@tool
def query_work_items_by_feature(
    feature_name: Annotated[str, "The name of the feature to search for"]
) -> str:
    """
    Query all work items (user stories and tasks) associated with a specific feature.
    
    Args:
        feature_name: The name of the feature to search for
        
    Returns:
        List of work items with their IDs, titles, and current states
    """
    try:
        auth_header = _get_auth_header()
        
        # WIQL query to find all work items under a feature
        wiql_query = f"""
        SELECT [System.Id], [System.WorkItemType], [System.Title], [System.State], [System.AssignedTo]
        FROM WorkItemLinks
        WHERE ([Source].[System.TeamProject] = @project 
               AND [Source].[System.WorkItemType] = 'Feature' 
               AND [Source].[System.Title] CONTAINS '{feature_name}')
        AND ([System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward')
        AND ([Target].[System.TeamProject] = @project)
        ORDER BY [System.Id]
        """
        
        # Execute WIQL query
        wiql_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_apis/wit/wiql?api-version=7.1-preview.2"
        wiql_data = {"query": wiql_query}
        
        headers = {**auth_header, "Content-Type": "application/json"}
        response = requests.post(wiql_url, json=wiql_data, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return f"❌ Failed to query work items: {response.status_code} - {response.text}"
            
        wiql_result = response.json()
        work_item_relations = wiql_result.get('workItemRelations', [])
        
        if not work_item_relations:
            return f"❌ No work items found for feature: {feature_name}"
        
        # Get work item IDs (exclude the feature itself)
        work_item_ids = []
        for relation in work_item_relations:
            if relation.get('target'):
                work_item_ids.append(str(relation['target']['id']))
        
        if not work_item_ids:
            return f"❌ No child work items found for feature: {feature_name}"
        
        # Get detailed work item information
        work_items_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_apis/wit/workitems?ids={','.join(work_item_ids)}&api-version=7.1-preview.3"
        
        response = requests.get(work_items_url, headers=auth_header, timeout=30)
        
        if response.status_code != 200:
            return f"❌ Failed to get work item details: {response.status_code} - {response.text}"
            
        work_items = response.json().get('value', [])
        
        result = f"✅ Found {len(work_items)} work items for feature '{feature_name}':\n\n"
        
        for item in work_items:
            item_id = item.get('id')
            fields = item.get('fields', {})
            work_item_type = fields.get('System.WorkItemType', 'Unknown')
            title = fields.get('System.Title', 'No Title')
            state = fields.get('System.State', 'Unknown')
            assigned_to = fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned')
            
            result += f"• {work_item_type} #{item_id}: {title}\n"
            result += f"  State: {state} | Assigned: {assigned_to}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error querying work items: {str(e)}"

@tool
def update_work_item_state(
    work_item_id: Annotated[int, "The ID of the work item to update"],
    new_state: Annotated[str, "The new state (e.g., 'Active', 'Resolved', 'Closed', 'Done')"]
) -> str:
    """
    Update the state of a specific work item (user story or task).
    
    Args:
        work_item_id: The ID of the work item to update
        new_state: The new state to set (common states: Active, Resolved, Closed, Done)
        
    Returns:
        Success or error message
    """
    try:
        auth_header = _get_auth_header()
        
        # Update work item state
        api_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_apis/wit/workItems/{work_item_id}?api-version=7.1-preview.3"
        
        update_data = [
            {"op": "add", "path": "/fields/System.State", "value": new_state}
        ]
        
        headers = {**auth_header, "Content-Type": "application/json-patch+json"}
        response = requests.patch(api_url, json=update_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            work_item = response.json()
            title = work_item.get('fields', {}).get('System.Title', 'Unknown')
            work_item_type = work_item.get('fields', {}).get('System.WorkItemType', 'Unknown')
            work_item_url = f"https://dev.azure.com/{ADO_ORGANIZATION}/{ADO_PROJECT}/_workitems/edit/{work_item_id}"
            
            return f"✅ {work_item_type} updated successfully!\nID: {work_item_id}\nTitle: {title}\nNew State: {new_state}\nURL: {work_item_url}"
        else:
            return f"❌ Failed to update work item: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error updating work item: {str(e)}"

@tool
def bulk_update_work_items_state(
    feature_name: Annotated[str, "The name of the feature whose work items to update"],
    new_state: Annotated[str, "The new state to set for all work items"],
    work_item_type_filter: Annotated[Optional[str], "Optional filter by work item type ('User Story', 'Task', or leave empty for all)"] = None
) -> str:
    """
    Update the state of all work items associated with a specific feature.
    
    Args:
        feature_name: The name of the feature whose work items to update
        new_state: The new state to set (e.g., 'Active', 'Resolved', 'Closed', 'Done')
        work_item_type_filter: Optional filter to update only specific work item types
        
    Returns:
        Summary of updates performed
    """
    try:
        # First, query the work items
        query_result = query_work_items_by_feature(feature_name)
        
        if "❌" in query_result:
            return query_result  # Return the error from the query
            
        # Extract work item IDs from the query result using simple parsing
        work_items_to_update = []
        lines = query_result.split('\n')
        
        for line in lines:
            if line.strip().startswith('•'):
                # Parse line like "• Task #123: Task Title"
                try:
                    parts = line.split('#')
                    if len(parts) > 1:
                        id_part = parts[1].split(':')[0].strip()
                        work_item_id = int(id_part)
                        
                        work_item_type = line.split('#')[0].replace('•', '').strip()
                        
                        # Apply filter if specified
                        if work_item_type_filter is None or work_item_type_filter.lower() in work_item_type.lower():
                            work_items_to_update.append((work_item_id, work_item_type))
                except:
                    continue  # Skip lines that can't be parsed
        
        if not work_items_to_update:
            return f"❌ No work items found to update for feature '{feature_name}'"
        
        # Update each work item
        results = []
        success_count = 0
        error_count = 0
        
        for work_item_id, work_item_type in work_items_to_update:
            update_result = update_work_item_state(work_item_id, new_state)
            
            if "✅" in update_result:
                success_count += 1
                results.append(f"✅ {work_item_type} #{work_item_id} updated to {new_state}")
            else:
                error_count += 1
                results.append(f"❌ {work_item_type} #{work_item_id} failed to update")
        
        summary = f"✅ Bulk update completed for feature '{feature_name}':\n"
        summary += f"• Successfully updated: {success_count} work items\n"
        summary += f"• Failed updates: {error_count} work items\n"
        summary += f"• New state: {new_state}\n\n"
        summary += "Details:\n" + "\n".join(results)
        
        return summary
        
    except Exception as e:
        return f"❌ Error performing bulk update: {str(e)}"
