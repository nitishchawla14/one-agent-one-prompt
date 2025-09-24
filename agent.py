import os
from langchain_openai import AzureChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from prompts import requirements_generator_prompt, supervisor_prompt, ado_integration_prompt, pbip_generator_prompt
from requirements_generator_tool import read_sow_and_rules, save_requirements_file, list_current_directory
from ado_integration_tool import (
    read_requirements_file, 
    test_ado_connection, 
    check_existing_features,
    create_ado_feature, 
    create_ado_user_story, 
    create_ado_task,
    query_work_items_by_feature,
    update_work_item_state,
    bulk_update_work_items_state
)
from pbip_generator_tool import (
    analyze_requirements_for_pbip,
    discover_azure_sql_schema,
    generate_pbip_structure,
    generate_tmdl_files,
    generate_pbip_documentation
)

load_dotenv()
api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hackathon-ai-foundry.cognitiveservices.azure.com/")
model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

model = AzureChatOpenAI(
    model=model_name,
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)


# Create Agents

requirements_generator_agent = create_react_agent(
    model=model,
    tools=[read_sow_and_rules, save_requirements_file, list_current_directory],
    name="requirements_generator_agent",
    prompt=requirements_generator_prompt
)

ado_integration_agent = create_react_agent(
    model=model,
    tools=[
        read_requirements_file, 
        test_ado_connection,
        check_existing_features, 
        create_ado_feature, 
        create_ado_user_story, 
        create_ado_task,
        query_work_items_by_feature,
        update_work_item_state,
        bulk_update_work_items_state
    ],
    name="ado_integration_agent",
    prompt=ado_integration_prompt
)

pbip_generator_agent = create_react_agent(
    model=model,
    tools=[
        analyze_requirements_for_pbip,
        discover_azure_sql_schema,
        generate_pbip_structure,
        generate_tmdl_files,
        generate_pbip_documentation
    ],
    name="pbip_generator_agent",
    prompt=pbip_generator_prompt
)

# Create Supervisor with default state
workflow = create_supervisor(
    [requirements_generator_agent, ado_integration_agent, pbip_generator_agent],
    model=model,
    prompt=supervisor_prompt
)