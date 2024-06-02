import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
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
from typing import Optional, Tuple
import asyncio
import os
from typing import Tuple
from gpt_researcher import GPTResearcher

ROOT_DIR = "./"
VALID_FILE_TYPES = {"py", "txt", "md", "cpp", "c", "java", "js", "html", "css", "ts", "json"}
memory = ConversationBufferMemory(memory_key="chat_history")

@tool
def researcher(question: str, context: str) -> Tuple[str, bool]:
    """
    Conducts research based on a given question and context, and generates a research report.

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
    # TODO handle multiple matches
    for root, dirs, files in os.walk(path):
        if filename in files:
            return os.path.join(root, filename)
    return None


@tool
def create_file(filename: str, content: str = "", directory=""):
    """Creates a new file and content in the specified directory."""
    try:
        file_stem, file_type = filename.split(".")
        assert file_type in VALID_FILE_TYPES
    except:
        return f"Invalid filename {filename} - must end with a valid file type: {valid_file_types}"
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


# List of tools to use
tools = [
    ShellTool(ask_human_input=True),
    create_directory,
    # create_react_app_with_vite,
    find_file,
    create_file,
    update_file,
    researcher
    # Add more tools if needed
]


# Configure the language model
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)


# Set up the prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert web developer.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Bind the tools to the language model
llm_with_tools = llm.bind_tools(tools)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# Main loop to prompt the user
while True:
    user_prompt = input("Prompt: ")
    list(agent_executor.stream({"input": user_prompt}))
    # Create a simple frontend webapp using Vanilla HTML, CSS, and JS, that implements a MineSweeper game. Make sure to include all the necessary JS logic and the CSS to show the 2D grid
    # Context  
    """
    There is a MineSweeper game implemenentation in ./minesweeper. In the current implementation there is only one issue that you need to fix:\n1. When the user completes the game that is all the cells except the miner cells are uncovered there is no you win alert. \n    Do not use React only Vanilla HTML, CSS and JS. Current implementation is Vanilla, continue on it\n    Current working directory for the minesweeper game is /workspace/ai-school-developer/minesweeper $ ls > index.html  script.js  styles.css

        There is a MineSweeper game implemenentation in ./minesweeper. I want to log the location of all the mines with console.log to facilitate testing. Without changing any of the current files, read the script.js and let me know what console.log(...) and where i can add it to enable this behaviour on game start\n Current working directory for the minesweeper game is /workspace/ai-school-developer/minesweeper $ ls > index.html  script.js  styles.css
    """