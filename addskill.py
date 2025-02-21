from autogenstudio import AutoGenStudio
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
from dotenv import load_dotenv
load_dotenv()

source_file_path = "./scode/"

model_client = AzureOpenAIChatCompletionClient(model="gpt-4o",
                                               azure_deployment="gpt-4o-2", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21",
                                               temperature=0.0,
                                               seed=42,
                                               maz_tokens=4096)

# Initialize AutoGen Studio
ags = AutoGenStudio()


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

    return java_contents

if __name__ == "__main__":
    
    convert_reader_tool = FunctionTool(
        func=convert_code_in_folder,
        description="Loop through the folder and take .java file, Read the content and convert java code to python code using model memory and save to ./dcode folder.",
        name="convert_reader",
        global_imports=["os", "json", ImportFromModule("PyPDF2", ("PdfReader",)),]
    )


    print("-----------------------------------------------------------------------------------------")
    print(convert_reader_tool.dump_component().model_dump_json())
    print("-----------------------------------------------------------------------------------------")
    #

    skill_name = "convert_reader"
    skill_code = """
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

        return java_contents
    """

    # Add the skill to AutoGen Studio
    ags.add_skill("convert_reader", skill_code)
    
    gallery_name = "convert_reader"
    # Add the skill to the gallery
    ags.add_gallery_item(gallery_name, "skill", {
        "name": skill_name,
        "code": skill_code
    })

    
    # Set the new gallery as default (optional)
    ags.set_default_gallery(gallery_name)