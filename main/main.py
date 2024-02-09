import os

from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(openai_api_key=api_key)
    graph = Neo4jGraph(
        url="bolt://54.86.80.87:7687",
        username="neo4j",
        password="petition-week-rear",
    )

    CYPHER_GENERATION_TEMPLATE = """
    You are an expert Neo4j Developer translating user questions into Cypher to answer questions about movies and provide recommendations.
    Convert the user's question based on the schema.

    Instructions:
    Use only the provided relationship types and properties in the schema.
    Do not use any other relationship types or properties that are not provided.
    For movie titles that begin with "The", move "the" to the end, For example "The 39 Steps" becomes "39 Steps, The".

    Schema: {schema}
    Question: {question}
    """

    # If no data is returned, do not attempt to answer the question.
    # Only respond to questions that require you to construct a Cypher statement.
    # Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
    # Do not include any explanations or apologies in your responses.
    # Do not include any text except the generated Cypher statement.

    cypher_generation_prompt = PromptTemplate(
        template=CYPHER_GENERATION_TEMPLATE,
        input_variables=["schema", "question"],
    )

    cypher_chain = GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        cypher_prompt=cypher_generation_prompt,
        verbose=True
    )

    # result = cypher_chain.invoke({"query": "What role did Tom Hanks play in Toy Story?"})
    # cypher_chain.invoke({"query": "What movies has Tom Hanks acted in?"})
    # cypher_chain.invoke({"query": "How many movies has Tom Hanks directed?"})
    result = cypher_chain.invoke({"query": "Who acted in The Matrix and what roles did they play?"})

    print(result)

# delinrus@gmail.com
# neo4j+s://09b90eb07e931168e98bd970c1385828.neo4jsandbox.com:7687
