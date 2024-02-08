if __name__ == '__main__':
    from langchain_community.graphs import Neo4jGraph

    graph = Neo4jGraph(
        url="bolt://54.86.80.87:7687",
        username="neo4j",
        password="petition-week-rear"
    )

    result = graph.query("""
    MATCH (m:Movie{title: 'Toy Story'}) 
    RETURN m.title, m.plot, m.poster
    """)

    print("Result")
    print(result)
    print("Graph schema")
    print(graph.schema)

# delinrus@gmail.com
# neo4j+s://09b90eb07e931168e98bd970c1385828.neo4jsandbox.com:7687
