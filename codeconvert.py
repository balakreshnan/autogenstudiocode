import asyncio
import os
from PyPDF2 import PdfReader
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core.tools import Tool, FunctionTool
from autogen_core.code_executor import FunctionWithRequirements, with_requirements
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat, MagenticOneGroupChat
from typing_extensions import Annotated
from autogen_ext.agents.file_surfer import FileSurfer
from textwrap import dedent, indent
from typing import Any, Callable, Generic, List, Sequence, Set, Tuple, TypeVar, Union
import json
import functools
from autogen_core.code_executor import ImportFromModule
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AzureAISearchTool
# [START enable_tracing]
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
load_dotenv()

connection_string = os.environ["PROJECT_CONNECTION_STRING_EASTUS2"] 

# print(f"Connection string: {connection_string}")

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=connection_string,
)

# Enable Azure Monitor tracing
application_insights_connection_string = project_client.telemetry.get_connection_string()
if not application_insights_connection_string:
    print("Application Insights was not enabled for this project.")
    print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
    exit()
configure_azure_monitor(connection_string=application_insights_connection_string)

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

source_file_path = "./scode/"

model_client = AzureOpenAIChatCompletionClient(model="gpt-4o",
                                               azure_deployment="gpt-4o-2", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21",
                                               temperature=0.0,
                                               seed=42,
                                               maz_tokens=4096)



@with_requirements(global_imports=["from PyPDF2 import PdfReader", "import os", "import json"], python_packages=["PyPDF2"])
def read_pdfs_in_folder(folder_path: str) -> str:
    pdf_contents = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(root, file)
                try:
                    reader = PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    pdf_contents[file] = text
                except Exception as e:
                    print(f"Error reading {file}: {str(e)}")

    return pdf_contents

@with_requirements(global_imports=["from PyPDF2 import PdfReader", "import os", "import json"], python_packages=["PyPDF2"])
def read_code_in_folder(folder_path: str) -> str:
    java_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))

    write_to_file(java_files, 'filetoprocess.txt')
    return java_files

def write_to_file(file_list, output_filename):
    with open(output_filename, 'w') as f:
        for file_path in file_list:
            f.write(f"{file_path}\n")

# @with_requirements(global_imports=["from PyPDF2 import PdfReader", "import os", "import json"], python_packages=["PyPDF2"])
# def read_code_in_folder(folder_path: str) -> str:
#     code_contents = {}

#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             if file.lower().endswith('.java'):
#                 file_path = os.path.join(root, file)
#                 try:
#                     with open(file_path, 'r') as f:
#                         code = f.read()
#                     code_contents[file] = code
#                 except Exception as e:
#                     print(f"Error reading {file}: {str(e)}")

#     return code_contents

@with_requirements(global_imports=["from PyPDF2 import PdfReader", "import os", "import json"], python_packages=["PyPDF2"])
def convert_code_in_folder(folder_path: str) -> str:
    java_files = []
    java_contents = ""
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                java_files.append(file_path)
                # Read the content of each Java file
                with open(file_path, 'r', encoding='utf-8') as f:
                    java_contents += f"// File: {file_path}\n"
                    java_contents += f.read()
                    java_contents += "\n\n"  # Add some separation between files

    # Optionally, write the list of files to filetoprocess.txt
    # write_to_file(java_files, 'filetoprocess.txt')
    
    return java_contents

def write_to_file(file_list, output_filename):
    with open(output_filename, 'w') as f:
        for file_path in file_list:
            f.write(f"{file_path}\n")

def build_agent():
    # Example usage of the tool directly
    with tracer.start_as_current_span(scenario) as x: 
        x.set_attribute("Test_attribute", "Bala")       

        code_reader_tool = FunctionTool(
            func=read_code_in_folder,
            description="Loop through the folder and take .java file and create a list of java files to process. Provide the full directory path as input.",
            name="file_reader",
            global_imports=["os", "json", ImportFromModule("PyPDF2", ("PdfReader",)),]
        )

        # Step 2: Define an Agent and Add the Tool
        agent = AssistantAgent(
            name="assistant_with_java_reader",
            model_client=model_client,
            tools=[code_reader_tool],  # Add the tool to the agent's list of tools
            handoffs=["convert_agent"],  # No handoffs for this agent
        )

        convert_reader_tool = FunctionTool(
            func=convert_code_in_folder,
            description="Loop through the folder and take .java file and convert to python code and save to ./dcode folder. Tool will provide the files to process.",
            name="convert_reader",
            global_imports=["os", "json", ImportFromModule("PyPDF2", ("PdfReader",)),]
        )
        # Step 3: Define an Agent and Add the Tool
        convert_agent = AssistantAgent(
            name="convert_agent",
            model_client=model_client,
            tools=[convert_reader_tool],  # Add the tool to the agent's list of tools
            handoffs=["write_agent"],  # No handoffs for this agent
        )

        code_write_tool = FunctionTool(
            func=convert_code_in_folder,
            description="Given the java file please cnvert to python please save them to ./dcode folder.",
            name="code_write",
            #global_imports=["os", "json", ImportFromModule("PyPDF2", ("PdfReader",)),]
        )
        # Step 4: Define an Agent and Add the Tool
        code_write_agent = AssistantAgent(
            name="write_agent",
            model_client=model_client,
            tools=[code_write_tool],  # Add the tool to the agent's list of tools
            handoffs=[],  # No handoffs for this agent
            system_message="You are java to python conversion agent. Please convert the java code to python and save to ./dcode folder."
        )

        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(max_messages=25)
        termination = text_mention_termination | max_messages_termination

        team = MagenticOneGroupChat([agent, convert_agent, code_write_agent], 
                                    termination_condition=termination, 
                                    max_turns=1,
                                    model_client=model_client)

        query = f"Can you loop files in current folder ./scode and convert to python and store to ./dcode folder?"
        # summarize ./papers
        # Extract the generated code
        response = asyncio.run(team.run(task=query))
        last_message = response.messages
        print("-----------------------------------------------------------------------------------------")

        for message in response.messages:
            print("-----------------------------------------------------------------------------------------")
            print('Messages: ' , message)
            print('Messages Source: ' , message.source)
            print('Messages Content: ' , message.content)
            print("-----------------------------------------------------------------------------------------")

        print("-----------------------------------------------------------------------------------------")
        print("Now it's time to print the token usage metrics for the agents.")
        print("-----------------------------------------------------------------------------------------")
        # Initialize a dictionary to store per-agent token usage
        agent_token_usage = {}
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # Process each message
        for message in response.messages:
            source = message.source
            usage = message.models_usage

            if usage:
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens

                # Update per-agent token usage
                if source != "file_agent":            
                    if source not in agent_token_usage:
                        agent_token_usage[source] = {"prompt_tokens": 0, "completion_tokens": 0}

                    agent_token_usage[source]["prompt_tokens"] += prompt_tokens
                    agent_token_usage[source]["completion_tokens"] += completion_tokens

                    # Update total token counts
                    total_prompt_tokens += prompt_tokens
                    total_completion_tokens += completion_tokens
                else:
                    print(f"File Agent: Message = {message}")

        # Display per-agent token usage
        for agent, usage in agent_token_usage.items():
            print(f"{agent}: Prompt Tokens = {usage['prompt_tokens']}, Completion Tokens = {usage['completion_tokens']}")

        # Display total token usage
        print(f"Total Prompt Tokens: {total_prompt_tokens}")
        print(f"Total Completion Tokens: {total_completion_tokens}")
        print(f"Total Token Usage: {total_prompt_tokens + total_completion_tokens}")
        print("-----------------------------------------------------------------------------------------")

        #print('Response: \n' , response)
        #parse_agent_response(response)
        print("-----------------------------------------------------------------------------------------")
        #print('Agent JSON:', team.dump_component().model_dump_json())
        #serialized = team.dump_component().model_dump(mode='python')
        #print(f"Serialized team: {json.dumps(serialized)}")
        print("-----------------------------------------------------------------------------------------")
    x.end()

# Step 4: Test the Agent with the Tool
if __name__ == "__main__":
    #asyncio.run(build_agent())
    build_agent()