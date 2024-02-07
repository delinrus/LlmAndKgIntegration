import os

from langchain_openai import OpenAI

if __name__ == '__main__':
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    response = llm.invoke("What is Neo4j?")

    print(response)
