import chainlit as cl
import requests
import asyncio
 
API_URL = "http://localhost:8000/ask"
 
@cl.on_message
async def on_message(msg: cl.Message):
    response = requests.post(API_URL, json={"query": msg.content})
    response.raise_for_status()
    data = response.json()
 
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