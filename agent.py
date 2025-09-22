import os
from langchain_openai import AzureChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from prompts import requirements_generator_prompt, supervisor_prompt, ado_integration_prompt
from requirements_generator_tool import read_sow_and_rules, save_requirements_file, list_current_directory
from ado_integration_tool import (
    read_requirements_file, 
    test_ado_connection, 
    check_existing_features,
    create_ado_feature, 
    create_ado_user_story, 
    create_ado_task
)

load_dotenv()
api_key = os.getenv("AZURE_OPENAI_API_KEY", "7EXkVTZPPpX2GZvFo4b1ACpqIMafxy0U8lzvNf2VzRsRUtdLKPiYJQQJ99BIACYeBjFXJ3w3AAAAACOGQLba")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hackathon-ai-foundry.cognitiveservices.azure.com/")
model_name = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

model = AzureChatOpenAI(
    model=model_name,
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    temperature=0.2
)



# Define Tools
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def web_search(query: str) -> str:
    """Search the web for information."""
    return (
        "Here are the headcounts for each of the FAANG companies in 2024:\n"
        "1. **Facebook (Meta)**: 67,317 employees.\n"
        "2. **Apple**: 164,000 employees.\n"
        "3. **Amazon**: 1,551,000 employees.\n"
        "4. **Netflix**: 14,000 employees.\n"
        "5. **Google (Alphabet)**: 181,269 employees."
    )

# Create Agents
math_agent = create_react_agent(
    model=model,
    tools=[add, multiply],
    name="math_expert",
    prompt="You are a math expert. Always use one tool at a time."
)

research_agent = create_react_agent(
    model=model,
    tools=[web_search],
    name="research_expert",
    prompt="You are a world-class researcher with access to web search. Do not do any math."
)

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
        create_ado_task
    ],
    name="ado_integration_agent",
    prompt=ado_integration_prompt
)

# Create Supervisor with default state
workflow = create_supervisor(
    [research_agent, math_agent, requirements_generator_agent, ado_integration_agent],
    model=model,
    prompt=supervisor_prompt
)