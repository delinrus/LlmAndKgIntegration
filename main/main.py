import os

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

if __name__ == '__main__':
    chat_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    prompt = PromptTemplate(
        template="""You are a surfer dude, having a conversation about the surf conditions on the beach.
    Respond using surfer slang.

    Context: {context}
    Question: {question}
    """,
        input_variables=["context", "question"],
    )

    chat_chain = LLMChain(llm=chat_llm, prompt=prompt)

    current_weather = """
        {
            "surf": [
                {"beach": "Fistral", "conditions": "6ft waves and offshore winds"},
                {"beach": "Polzeath", "conditions": "Flat and calm"},
                {"beach": "Watergate Bay", "conditions": "3ft waves and onshore winds"}
            ]
        }"""

    response = chat_chain.invoke(
        {
            "context": current_weather,
            "question": "What is the weather like on Watergate Bay?",
        }
    )

    print(response)
