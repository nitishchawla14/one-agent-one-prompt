from langchain_core.messages import AIMessage, ToolMessage
import os
from fastapi import FastAPI
from pydantic import BaseModel
from agent import workflow

class QueryRequest(BaseModel):
    query: str


app_fastapi = FastAPI()

agent = workflow.compile()

@app_fastapi.post("/ask")
async def ask_openai(request: QueryRequest):
    # Generate a unique thread ID for each request to maintain session isolation
    thread_id = f"thread_{hash(request.query) % 10000}"
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": request.query}]},
        config={"configurable": {"thread_id": thread_id}}
    )
    
    messages = []
    for m in result["messages"]:
        if isinstance(m, AIMessage):
            messages.append({"type": "ai", "content": m.content})
        elif isinstance(m, ToolMessage):
            messages.append({"type": "tool", "content": m.content})
 
    return {"messages": messages}