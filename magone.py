import asyncio
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
import os

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


async def main() -> None:
    # model_client = OpenAIChatCompletionClient(model="gpt-4o")

    # assistant = AssistantAgent(
    #     "Assistant",
    #     model_client=model_client,
    # )
    # team = MagenticOneGroupChat([assistant], model_client=model_client)
    # await Console(team.run_stream(task="Provide a different proof for Fermat's Last Theorem"))

    surfer = MultimodalWebSurfer(
        "WebSurfer",
        model_client=model_client,
    )
    team = MagenticOneGroupChat([surfer], model_client=model_client)
    await Console(team.run_stream(task="What is the UV index in Melbourne today?"))


asyncio.run(main())