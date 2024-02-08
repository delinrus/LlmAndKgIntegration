import os

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

if __name__ == '__main__':
    chat_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    prompt = PromptTemplate(
        template="""You are a surfer dude, having a conversation about the surf conditions on the beach.
    Respond using surfer slang.

    Question: {question}
    """,
        input_variables=["question"],
    )

    chat_chain = LLMChain(llm=chat_llm, prompt=prompt)

    response = chat_chain.invoke({"question": "What is the weather like?"})

    print(response)
