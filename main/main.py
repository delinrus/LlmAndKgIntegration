import os

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

if __name__ == '__main__':
    chat_llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

    prompt = PromptTemplate(
        template="""
        You are a movie expert. You find movies from a genre or plot.

        ChatHistory:{chat_history}
        Question:{input}
        """,
        input_variables=["chat_history", "input"],
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chat_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

    tools = [
        Tool.from_function(
            name="Movie Chat",
            description="For when you need to chat about movies. The question will be a string. Return a string.",
            func=chat_chain.run,
            return_direct=True,
        )
    ]

    agent_prompt = hub.pull("hwchase17/react-chat")
    agent = create_react_agent(llm, tools, agent_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)

    while True:
        q = input("> ")
        response = agent_executor.invoke({"input": q})
        print(response["output"])


# delinrus@gmail.com
# neo4j+s://09b90eb07e931168e98bd970c1385828.neo4jsandbox.com:7687