import asyncio
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import MagenticOneGroupChat, RoundRobinGroupChat
from autogen_agentchat.agents import UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_ext.agents.video_surfer import VideoSurfer
from autogen_agentchat.conditions import TextMentionTermination
import os

async def main() -> None:
    """
    Main function to run the video agent.
    """

    # model_client = OpenAIChatCompletionClient(model="gpt-4o-2024-08-06")
    model_client = AzureOpenAIChatCompletionClient(model="gpt-4o",
                                               azure_deployment="gpt-4o-2", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                               api_version="2024-10-21",
                                               temperature=0.0,
                                               seed=42,
                                               maz_tokens=4096)


    # Define an agent
    video_agent = VideoSurfer(
        name="VideoSurfer",
        model_client=model_client
        )

    web_surfer_agent = UserProxyAgent(
        name="User"
    )

    # Define termination condition
    termination = TextMentionTermination("TERMINATE")

    # Define a team
    agent_team = RoundRobinGroupChat([video_agent], termination_condition=termination)

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(task="Summarize video Autogen-MagenticOneWebSurfer.mp4?")
    await Console(stream)

asyncio.run(main())