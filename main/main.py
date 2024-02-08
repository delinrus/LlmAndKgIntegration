import os

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

if __name__ == '__main__':
    chat_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    instructions = SystemMessage(content="""
    You are a surfer dude, having a conversation about the surf conditions on the beach.
    Respond using surfer slang.
    """)

    question = HumanMessage(content="What is the weather like?")

    response = chat_llm.invoke([
        instructions,
        question
    ])

    print(response.content)
