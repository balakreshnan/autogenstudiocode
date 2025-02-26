import asyncio
import sys
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat, RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
import os

from dotenv import load_dotenv
load_dotenv()

source_file_path = "./scode/"

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
        "MultimodalWebSurfer",
        model_client=model_client,
        downloads_folder="./downs",
        debug_dir="./debug",
        headless = False,
        to_resize_viewport=True,
        description="A web surfing assistant that can browse and interact with web pages.",
        start_page="https://www.bing.com",  # Optional: Initial page
        animate_actions=True,
        browser_data_dir="./browser_data",
    )
    team = MagenticOneGroupChat([surfer], model_client=model_client, max_turns=3)
    # Define a team
    # team = RoundRobinGroupChat([surfer], max_turns=3)
    #await Console(team.run_stream(task="Navigate to the AutoGen readme on GitHub."))
    # await Console(team.run_stream(task="Summarize latest updates from Accenture newsroowm."))
    # await Console(team.run_stream(task="Summarize latest news from venture beat all things in AI."))
    await Console(team.run_stream(task="Summarize latest news from Techmeme all things in AI."))
    await surfer.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())