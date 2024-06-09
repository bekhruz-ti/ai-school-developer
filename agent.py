import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langsmith import traceable
from langchain_community.tools.shell.tool import ShellTool
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
import subprocess
import uuid
from typing import Optional, Tuple
import asyncio
import os
from typing import Tuple
from gpt_researcher import GPTResearcher
from github_integrations import call_github_toolkit

ROOT_DIR = "./"
memory = ConversationBufferMemory(memory_key="chat_history")

@tool
def generate_iac(prompt: str, file_type: str) -> bool:
    """
    Generates Infrastructure-as-Code (IaC) based on a given prompt and saves the output to a file.

    Parameters:
    prompt (str): Succint prompt to generate IaC. Up to 10 words.
    file_path (str): The path to the file where the output will be saved.

    Returns:
    bool: A boolean indicating success (True) or failure (False).
    """
    file_path = f"./{uuid.uuid4()}.{file_type.strip('.')}"
    print(f"Saving contents at {file_path}")
    try:
        # Run the aiac command with the given prompt and save the output to the specified file
        result = subprocess.run(
            ["aiac", "get", prompt, "-q", f"--output-file={file_path}"],
            check=True,
            capture_output=True,
            text=True
        )
        print(create_file(file_path, result.stdout))
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return e.stderr

@tool
def researcher(question: str, context: str) -> Tuple[str, bool]:
    """
    Conducts research based on a given question and context, and generates a research report. To be used given unexpected errors in implemented code.

    Parameters:
    question (str): The research question.
    context (str): The context or background information relevant to the question.

    Returns:
    Tuple[str, bool]: A tuple containing the research report and a boolean indicating success.
    """
    researcher = GPTResearcher(query=question, report_type="research_report")
    base_url = os.environ.pop("OPENAI_BASE_URL", None)
    try:
        research_result = asyncio.run(researcher.conduct_research())
        report = asyncio.run(researcher.write_report())
        return report, True
    finally:
        if base_url:
            os.environ["OPENAI_BASE_URL"] = base_url

@tool
def create_directory(directory: str) -> str:
    """
    Create a new writable directory with the given directory name if it does not exist.
    If the directory exists, it ensures the directory is writable.

    Parameters:
    directory (str): The name of the directory to create.

    Returns:
    str: Success or error message.
    """
    if ".." in directory:
        return f"Cannot make a directory with '..' in path"
    try:
        os.makedirs(directory, exist_ok=True)
        subprocess.run(["chmod", "u+w", directory], check=True)
        return f"Directory successfully '{directory}' created and set as writeable."
    except subprocess.CalledProcessError as e:
        return f"Failed to create or set writable directory '{directory}': {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


@tool
def find_file(filename: str, path: str) -> Optional[str]:
    """
    Recursively searches for a file in the given path.
    Returns string of full path to file, or None if file not found.
    """
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)
    return None


@tool
def create_file(filename: str, content: str = "", directory=""):
    """Creates a new file and content in the specified directory."""

    directory_path = os.path.join(ROOT_DIR, directory)
    file_path = os.path.join(directory_path, filename)
    if not os.path.exists(file_path):
        try:
            with open(file_path, "w")as file:
                file.write(content)
            print(f"File '{filename}' created successfully at: '{file_path}'.")
            return f"File '{filename}' created successfully at: '{file_path}'."
        except Exception as e:
            print(f"Failed to create file '{filename}' at: '{file_path}': {str(e)}")
            return f"Failed to create file '{filename}' at: '{file_path}': {str(e)}"
    else:
        print(f"File '{filename}' already exists at: '{file_path}'.")
        return f"File '{filename}' already exists at: '{file_path}'."


@tool
def update_file(filename: str, content: str, directory: str = ""):
    """Updates, appends, or modifies an existing file with new content."""
    if directory:
        file_path = os.path.join(ROOT_DIR, directory, filename)
    else:
        file_path = find_file(filename, ROOT_DIR)

    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "a") as file:
                file.write(content)
            return f"File '{filename}' updated successfully at: '{file_path}'"
        except Exception as e:
            return f"Failed to update file '{filename}' at: '{file_path}' - {str(e)}"
    else:
        return f"File '{filename}' not found at: '{file_path}'"


tools = [
    ShellTool(ask_human_input=True),
    create_directory,
    find_file,
    create_file,
    update_file,
    researcher,
    generate_iac,
    call_github_toolkit
]


llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert web developer."),
        MessagesPlaceholder("chat_history", optional=True),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_tools(tools)

agent = (
    {
        "input": lambda x: x["input"],
        "chat_history": lambda x: memory.buffer_as_messages,
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

if __name__ == "__main__": 
    while True:
        user_prompt = input("Prompt: ")
        chat_history = memory.buffer_as_messages
        list(agent_executor.stream({"input": user_prompt, "chat_history": chat_history}))