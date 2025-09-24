import chainlit as cl
import httpx
import asyncio
 
API_URL = "http://localhost:8000/ask"
 
@cl.on_message
async def on_message(msg: cl.Message):
    # Show loading message
    loading_msg = cl.Message(content="🤔 Processing your request...")
    await loading_msg.send()
    
    try:
        # Use async HTTP client with longer timeout
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
            response = await client.post(API_URL, json={"query": msg.content})
            response.raise_for_status()
            data = response.json()
            
        # Remove loading message
        await loading_msg.remove()
        
    except httpx.TimeoutException:
        await loading_msg.remove()
        await cl.Message(content="⏱️ Request timed out. The agent is taking longer than expected. Please try again.").send()
        return
    except Exception as e:
        await loading_msg.remove()
        await cl.Message(content=f"❌ Error communicating with API: {str(e)}").send()
        return
 
    final_answer = cl.Message(content="")
    await final_answer.send()
 
    async def stream_word_by_word(prefix, text):
        await final_answer.stream_token(prefix + " ")
        words = text.split()
        for word in words:
            await final_answer.stream_token(word + " ")
            await asyncio.sleep(0.05)
        await final_answer.stream_token("\n")
        await final_answer.update()
 
    for m in data["messages"]:
        if m["type"] == "ai":
            await stream_word_by_word("🔨", m["content"])
        elif m["type"] == "tool":
            await stream_word_by_word("🤖", m["content"])
 
    await final_answer.update()