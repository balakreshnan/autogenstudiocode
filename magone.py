import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import MagenticOneGroupChat, RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_core.tools import Tool, FunctionTool
from autogen_core.code_executor import ImportFromModule
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

# Create an email-sending function
def send_email(to_email: str, subject: str, body: str) -> str:
    # Email configuration (replace with your SMTP server details)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("GOOGLE_EMAIL")
    sender_password = os.getenv("GOOGLE_APP_PASSWORD")

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
    
    return f"Email sent to {to_email} with subject: {subject}"

# Create a user proxy agent with the ability to send emails
class EmailUserProxyAgent(UserProxyAgent):
    def send_email_task(self, to_email, subject, body):
        send_email(to_email, subject, body)
        return f"Email sent to {to_email} with subject: {subject}"
    
async def main() -> None:
    # model_client = OpenAIChatCompletionClient(model="gpt-4o")

    # assistant = AssistantAgent(
    #     "Assistant",
    #     model_client=model_client,
    # )
    # team = MagenticOneGroupChat([assistant], model_client=model_client)
    # await Console(team.run_stream(task="Provide a different proof for Fermat's Last Theorem"))
    # https://microsoft.github.io/autogen/stable/reference/python/autogen_ext.agents.web_surfer.html#autogen_ext.agents.web_surfer.MultimodalWebSurfer

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

    emailagent_tool = FunctionTool(
        func=send_email,
        description="Send Email to address and subject with content.",
        name="emailagent",
        global_imports=["os", "smtplib", ImportFromModule("email.mime.multipart", 
                                                          ("MIMEMultipart",)),ImportFromModule("email.mime", ("MIMEText",)),]
    )

    emailagent = AssistantAgent(
        name="emailagent",
        model_client=model_client,
        tools=[emailagent_tool],  # Add the tool to the agent's list of tools
        handoffs=["convert_agent"],  # No handoffs for this agent
        description="Read the content of Java files in the folder and create a list of files to process."
    )
    
    team = MagenticOneGroupChat([surfer, emailagent], model_client=model_client, max_turns=3)
    # Define a team
    # team = RoundRobinGroupChat([surfer], max_turns=3)
    #await Console(team.run_stream(task="Navigate to the AutoGen readme on GitHub."))
    # await Console(team.run_stream(task="Summarize latest updates from Accenture newsroowm."))
    # await Console(team.run_stream(task="Summarize latest news from venture beat all things in AI."))
    # await Console(team.run_stream(task="Summarize latest news from Techmeme."))
    # await Console(team.run_stream(task="Access Wisconsin DMV web site and download Motorists driver license handbook as pdf."))
    # await Console(team.run_stream(task="Summarize latest updates from Accenture newsroowm and email babal@microsoft.com with subject Accenture news."))
    await Console(team.run_stream(task="Summarize Top 10 latest updates from techmeme and email babal@microsoft.com."))
    await surfer.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())