import os

from langchain.chains import RetrievalQA
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")
    chat_llm = ChatOpenAI(openai_api_key=api_key)
    embedding_provider = OpenAIEmbeddings(openai_api_key=api_key)

    movie_plot_vector = Neo4jVector.from_existing_index(
        embedding_provider,
        url="bolt://54.86.80.87:7687",
        username="neo4j",
        password="petition-week-rear",
        index_name="moviePlots",
        embedding_node_property="embedding",
        text_node_property="plot",
    )

    plot_retriever = RetrievalQA.from_llm(
        llm=chat_llm,
        retriever=movie_plot_vector.as_retriever(),
        verbose=True,
        return_source_documents=True
    )

    result = plot_retriever.invoke(
        {"query": "A movie where aliens land and attack earth."}
    )

    print(result)

    # query = "Give western movie where group of heroes protect innocent people"
    # query = "A movie where aliens land and attack earth."

# delinrus@gmail.com
# neo4j+s://09b90eb07e931168e98bd970c1385828.neo4jsandbox.com:7687
