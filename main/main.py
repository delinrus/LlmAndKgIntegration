import os

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.chains import RetrievalQA, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_community.tools.youtube.search import YouTubeSearchTool
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(openai_api_key=api_key)
    embedding_provider = OpenAIEmbeddings(openai_api_key=api_key)

    prompt = PromptTemplate(
        template="""
        You are a movie expert. You find movies from a genre or plot. 

        ChatHistory:{chat_history} 
        Question:{input}
        """,
        input_variables=["chat_history", "input"]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chat_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

    youtube = YouTubeSearchTool()

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
        llm=llm,
        retriever=movie_plot_vector.as_retriever(),
        verbose=True,
        return_source_documents=True
    )


    def run_retriever(query):
        results = plot_retriever.invoke({"query": query})
        # format the results
        movies = '\n'.join([doc.metadata["title"] + " - " + doc.page_content for doc in results["source_documents"]])
        return movies


    tools = [
        Tool.from_function(
            name="Movie Chat",
            description="For when you need to chat about movies. The question will be a string. Return a string.",
            func=chat_chain.run,
            return_direct=True
        ),
        Tool.from_function(
            name="Movie Trailer Search",
            description="Use when needing to find a movie trailer. The question will include the word 'trailer'. Return a link to a YouTube video.",
            func=youtube.run,
            return_direct=True
        ),
        Tool.from_function(
            name="Movie Plot Search",
            description="For when you need to compare a plot to a movie. The question will be a string. Return a string.",
            func=run_retriever,
            return_direct=True
        )
    ]

    agent_prompt = hub.pull("hwchase17/react-chat")
    agent = create_react_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        max_interations=3,
        verbose=True,
        handle_parse_errors=True)

    while True:
        q = input("> ")
        response = agent_executor.invoke({"input": q})
        print(response["output"])

    # query = "Give western movie where group of heroes protect innocent people"
    # query = "A movie where aliens land and attack earth."

# delinrus@gmail.com
# neo4j+s://09b90eb07e931168e98bd970c1385828.neo4jsandbox.com:7687
