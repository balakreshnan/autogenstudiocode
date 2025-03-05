import asyncio
import os
from PyPDF2 import PdfReader
import PyPDF2
from openai import AzureOpenAI
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core import CancellationToken
from autogen_core.tools import Tool, FunctionTool
from autogen_core.code_executor import FunctionWithRequirements, with_requirements
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat, MagenticOneGroupChat
from typing_extensions import Annotated
from autogen_ext.agents.file_surfer import FileSurfer
from textwrap import dedent, indent
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage
from typing import Any, Callable, Generic, List, Sequence, Set, Tuple, TypeVar, Union
import json
import functools
from autogen_core.code_executor import ImportFromModule
import streamlit as st
import datetime
from dotenv import load_dotenv
load_dotenv()

source_file_path = "./scode/"

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-10-21",
)

model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# https://agentaihubeast5815899485.openai.azure.com/openai/deployments/o1-mini/chat/completions?api-version=2025-01-01-preview
model_client = AzureOpenAIChatCompletionClient(model="o1-mini",
                                               azure_deployment="o1-mini", 
                                               azure_endpoint=os.getenv("AZURE_OPENAI_O1_ENDPOINT"), 
                                               api_key=os.getenv("AZURE_OPENAI_O1_KEY"), 
                                               # api_version="2025-01-31",
                                               )

temp_path = "temp1.pdf"

def processpdf(query: str) -> str:
    returntxt = "" 
    start_time = datetime.time.time()

    # print('Abstract Text:', pdftext)  
    pdftext = ""
    #print('upload_button:', file)
    print('Process temp path', temp_path)
    try:
        #file_paths = upload_file(files)
        reader = PyPDF2.PdfReader(temp_path)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
        print('PDF Text:', pdf_text)
    except Exception as e:
        print('Error:', e)

    
    message_text = [
    {"role":"system", "content":f"""You are Manufacturing Complaince, OSHA, CyberSecurity AI agent. Be politely, and provide positive tone answers.
     Based on the question do a detail analysis on information and provide the best answers.

     Use the data source content provided to answer the question.
     Data Source: {pdftext}
     Be polite and provide posite responses. If user is asking you to do things that are not specific to this context please ignore.
     If not sure, ask the user to provide more information.
     Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
     Print the PDF file name that is been used to user.
    ."""}, 
    {"role": "user", "content": f"""{query}. Provide summarized content based on the question asked."""}]

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"), #"gpt-4-turbo", # model = "deployment_name".
        messages=message_text,
        temperature=0.0,
        top_p=0.0,
        seed=42,
        max_tokens=1000,
    )

    partial_message = ""
    # calculate the time it took to receive the response
    response_time = datetime.time.time() - start_time

    # print the time delay and text received
    print(f"Full response from model received {response_time:.2f} seconds after request")
    #print(f"Full response received:\n{response}")

    returntext = response.choices[0].message.content + f" \nTime Taken: ({response_time:.2f} seconds)"

    return returntext

async def processpdf_agent(query):
    returntxt = ""
    planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
    model_client=model_client,
    system_message="""
        You are a planning agent.
        Your job is to break down complex tasks into smaller, manageable subtasks.
        Your team members are:
            PDF file analyst: You are a PDF file agent, analyze the content of the PDF file and provide the best answers.

        You only plan and delegate tasks - you do not execute them yourself.
        Also pick the right team member to use for the task.

        When assigning tasks, use this format:
        1. <agent> : <task>

        After all tasks are complete, summarize the findings and end with "TERMINATE".
        Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
        """,
    )

    pdf_analyst_agent = AssistantAgent(
        "PdfFileAnalyst",
        description="A PDF File AI agent. Based on the PDF content provide answers only.",
        model_client=model_client,
        tools=[processpdf],
        system_message="""
        You are PDF File AI agent. Be politely, and provide positive tone answers.
        Based on the question do a detail analysis on information and provide the best answers.
        Only answer from the PDF file provided. If content is not found let the user know there is no content.
        Extract Title content from the document. Show the Title, url as citations which is provided as url: as [url1] [url2].
        """,
    )

    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination

    model_client_mini = AzureOpenAIChatCompletionClient(model="gpt-4o", 
                                                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
                                                api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
                                                api_version="2024-10-21")

    team = MagenticOneGroupChat(
        [planning_agent, pdf_analyst_agent],
        model_client=model_client_mini,
        termination_condition=termination,
        max_turns=1,
    )

    result = await Console(team.run_stream(task=query))
    #print(result)  # Process the result or output here
    # Extract and print only the message content
    returntxt = ""
    returntxtall = ""
    for message in result.messages:
        # print('inside loop - ' , message.content)
        returntxt = str(message.content)
        returntxtall += str(message.content) + "\n"


    return returntxt, returntxtall

def process_agent(prompt):
    returntxt = ""
    returntxtall = ""

    # Step 2: Define an Agent and Add the Tool
    agent = AssistantAgent(
        name="assistant_with_java_reader",
        model_client=model_client,
        #tools=[code_reader_tool],  # Add the tool to the agent's list of tools
        # handoffs=["convert_agent"],  # No handoffs for this agent
        # system_message=f"""You are Natural lanugage to SQL AI Expert, you job is to analyze deep the question
        #   and schema list will be provided. Make sure create the ISO approved SQL queries.
        #   Be polite and provide posite responses. 
        #   If user is asking you to do things that are not specific to this context please ignore.""",
        system_message=None
    )

    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = text_mention_termination | max_messages_termination
    
    newprompt = f"""You are AIOPS AI agent. Your job is to create much accurate ISO SQL to retrieve data.
            Here is the Schema of the AIOPS database. Your job is to create much accurate ISO SQL to retrieve data.
            Schema:
            CREATE TABLE Assets (
                asset_id INT PRIMARY KEY AUTO_INCREMENT,
                asset_name VARCHAR(255) NOT NULL,
                asset_type VARCHAR(50),  -- e.g., Server, Database, Application
                ip_address VARCHAR(45),
                location VARCHAR(255),
                status ENUM('Active', 'Inactive', 'Decommissioned'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE Metrics (
                metric_id INT PRIMARY KEY AUTO_INCREMENT,
                asset_id INT,
                metric_name VARCHAR(100),  -- e.g., CPU Usage, Memory Usage
                metric_value FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES Assets(asset_id)
            );

            CREATE TABLE Logs (
                log_id INT PRIMARY KEY AUTO_INCREMENT,
                asset_id INT,
                log_level ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                log_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES Assets(asset_id)
            );

            CREATE TABLE Anomalies (
                anomaly_id INT PRIMARY KEY AUTO_INCREMENT,
                asset_id INT,
                anomaly_type VARCHAR(100),
                anomaly_description TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asset_id) REFERENCES Assets(asset_id)
            );

            CREATE TABLE Incidents (
                incident_id INT PRIMARY KEY AUTO_INCREMENT,
                anomaly_id INT,
                incident_status ENUM('Open', 'In Progress', 'Resolved', 'Closed'),
                priority ENUM('Low', 'Medium', 'High', 'Critical'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP NULL,
                FOREIGN KEY (anomaly_id) REFERENCES Anomalies(anomaly_id)
            );

            CREATE TABLE Alerts (
                alert_id INT PRIMARY KEY AUTO_INCREMENT,
                incident_id INT,
                alert_message TEXT,
                alert_status ENUM('Triggered', 'Acknowledged', 'Resolved'),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES Incidents(incident_id)
            );

            CREATE TABLE Recommendations (
                recommendation_id INT PRIMARY KEY AUTO_INCREMENT,
                incident_id INT,
                suggested_action TEXT,
                confidence_score FLOAT,  -- AI confidence level in resolution
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES Incidents(incident_id)
            );

            CREATE TABLE Users (
                user_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role ENUM('Admin', 'Operator', 'Viewer'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            Only create SQL statements. Do not hallucinate or make up data.
          
            Here is the query to convert to SQL Statement:
            {prompt}

            Respond only with SQL Statement.
            """
    print('New Prompt:', newprompt)

    # response = asyncio.run(agent.on_messages([TextMessage(content=prompt, source="user")], CancellationToken()))
    response = asyncio.run(agent.on_messages([TextMessage(content=newprompt, source="user")], CancellationToken()))
    #print(response)
    print(response.chat_message.content) 

    # query = f"Can you loop files in current folder ./scode and convert to python and store to ./dcode folder?"
    last_message = response.chat_message.content

    returntxt = last_message

    return returntxt

def processnlp():
    count = 0
    temp_file_path = ""
    rfttopics = ""
    

    #tab1, tab2, tab3, tab4 = st.tabs('RFP PDF', 'RFP Research', 'Draft', 'Create Word')
    modeloptions1 = ["o1-mini", "gpt-4o-2", "gpt-4o-g", "gpt-4o"]
    imgfile = "temp1.jpg"
    # Create a dropdown menu using selectbox method
    selected_optionmodel1 = st.selectbox("Select an Model:", modeloptions1)
    count += 1
    # PDF Upload
    #st.subheader("Upload and Chat with Your PDF")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    # user_input = st.text_input("Enter the question to ask the AI model", "what are the personal protection i should consider in manufacturing?")
    # what are the precaution to take when handling chemicals for eyes and hands?
    
      
    # Set up chat input with the selected question  
    # prompt = st.chat_input("How many users used the application1 yesterday?", key='chat_input')  
    if prompt := st.chat_input("How many users used the application1 yesterday?", key="chat1"):
        # Call the extractproductinfo function
        #st.write("Searching for the query: ", prompt)
        st.chat_message("user").markdown(prompt, unsafe_allow_html=True)
        starttime = datetime.datetime.now()
        if uploaded_file:
            # work on the uploaded file
            # Display the name of the file
            st.write(f"Uploaded file: {uploaded_file.name}")
            
            # Create a temporary file
            file_path = "temp1.pdf"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
                result = asyncio.run(processpdf_agent(prompt))
                rfttopics, agenthistory = result
        else:
            result = process_agent(prompt)
            agentresult = result
        endtime = datetime.datetime.now()
        #st.markdown(f"Time taken to process: {endtime - starttime}", unsafe_allow_html=True)
        rfttopics += f"\n Time taken to process: {endtime - starttime}"
        #st.session_state.chat_history.append({"role": "assistant", "message": rfttopics})
        st.chat_message("assistant").markdown(agentresult, unsafe_allow_html=True)

if __name__ == "__main__":
    processnlp()