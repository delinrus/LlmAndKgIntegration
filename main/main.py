import os

from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings

if __name__ == '__main__':
    embedding_provider = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    movie_plot_vector = Neo4jVector.from_existing_index(
        embedding_provider,
        url="bolt://54.86.80.87:7687",
        username="neo4j",
        password="petition-week-rear",
        index_name="moviePlots",
        embedding_node_property="embedding",
        text_node_property="plot",
    )

    # query = "Give western movie where group of heroes protect innocent people"
    query = "A movie where aliens land and attack earth."

    result = movie_plot_vector.similarity_search(query, k=1)
    for doc in result:
        print(doc.metadata["title"], "-", doc.page_content)

# delinrus@gmail.com
# neo4j+s://09b90eb07e931168e98bd970c1385828.neo4jsandbox.com:7687
