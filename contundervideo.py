import requests
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()

# Define the variables
endpoint = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT")  # Replace with your actual endpoint
analyzerId = "videosummary"  # Replace with your actual analyzer ID
api_version = "2024-12-01-preview"
key = os.getenv("CONTENT_UNDERSTANDING_KEY")  # Replace with your actual subscription key
fileUrl = "https://cdn.pixabay.com/photo/2016/03/08/20/03/flag-1244649_1280.jpg"  # Replace with the URL of the file you want to analyze

url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}?api-version={api_version}"

headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/json"
}

with open("request_video.json", "r") as file:
    data = file.read()

response = requests.put(url, headers=headers, data=data)

print(response.status_code)
print(response.text)

url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}:analyze?api-version={api_version}"

headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/json"
}

data = json.dumps({"url": fileUrl})

response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.text)

result = json.loads(response.text)
operationId = result["id"]

url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}/results/{operationId}?api-version={api_version}"

headers = {
    "Ocp-Apim-Subscription-Key": key
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)

result = json.loads(response.text)
operationId = result["id"]