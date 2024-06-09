import os
from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def call_github_toolkit(action: str, context: str):
    """
    Calls the GitHub toolkit to perform specified actions with provided context.

    Parameters:
    action (str): Description of the type of action to perform using GitHub toolkit.
    context (str): Information surrounding the specific action to be performed.

    Returns:
    str: Result of the GitHub action.
    """
    github = GitHubAPIWrapper()
    toolkit = GitHubToolkit.from_github_api_wrapper(github)
    github_tools = toolkit.get_tools()

    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    github_agent = (
        {
            "input": lambda x: x["input"],
            "chat_history": lambda x: memory.buffer_as_messages,
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                x["intermediate_steps"]
            ),
        }
        | llm.bind_tools(github_tools)
        | OpenAIToolsAgentOutputParser()
    )

    github_agent_executor = AgentExecutor(agent=github_agent, tools=github_tools, verbose=True, memory=memory)
    input_data = {"input": f"{action}\n{context}"}
    result = github_agent_executor.run(input_data)
    return result

if __name__=="__main__":
    print(call_github_toolkit('Read file minsweeper index html. what does it do', ''))