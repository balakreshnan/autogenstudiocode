import requests
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()

# Define the variables
endpoint = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT")  # Replace with your actual endpoint
analyzerId = "contentundersch"  # Replace with your actual analyzer ID
api_version = "2024-12-01-preview"
key = os.getenv("CONTENT_UNDERSTANDING_KEY")  # Replace with your actual subscription key
fileUrl = "https://cdn.pixabay.com/photo/2016/03/08/20/03/flag-1244649_1280.jpg"  # Replace with the URL of the file you want to analyze

operationId = "0a2987af-e368-4a8d-98bf-99320065a0e4"

url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}/results/{operationId}?api-version={api_version}"

headers = {
    "Ocp-Apim-Subscription-Key": key
}

response = requests.get(url, headers=headers)

print(response.status_code)
# print(response.text)

rs = json.loads(response.text)
#print(rs["status"])

rs1 = rs["result"]
#print(rs1)
# print(rs1["contents"])[0]["fields"]["Title"]["valueString"]
# Extract and print the valueString content
if rs1.get("contents"):
    for content in rs1["contents"]:
        title_field = content.get("fields", {}).get("Title", {})
        value_string = title_field.get("valueString")
        if value_string:
            print('Content extracted: ' , value_string)