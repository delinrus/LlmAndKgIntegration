import os

from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

if __name__ == '__main__':
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo-instruct", temperature=0)

    template = PromptTemplate(template="""
    You are a cockney fruit and vegetable seller.
    Your role is to assist your customer with their fruit and vegetable needs.
    Respond using cockney rhyming slang.

    Tell me about the following fruit: {fruit}
    """, input_variables=["fruit"])

    response = llm.invoke(template.format(fruit="apple"))

    print(response)
