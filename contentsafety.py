import requests
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()

# Define the variables
endpoint = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT")  # Replace with your actual endpoint
analyzerId = "contentunder"  # Replace with your actual analyzer ID
api_version = "2024-12-01-preview"
key = os.getenv("CONTENT_UNDERSTANDING_KEY")  # Replace with your actual subscription key
fileUrl = "https://cdn.pixabay.com/photo/2016/03/08/20/03/flag-1244649_1280.jpg"  # Replace with the URL of the file you want to analyze

# Construct the URL
url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}:analyze"

# Set up headers
headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/json"
}

# Set up query parameters
params = {
    "api-version": api_version
}

# Set up the request body
data = {
    "url": fileUrl
}

# Make the POST request
response = requests.post(url, headers=headers, params=params, json=data)

# Print the status code and response headers
print(f"Status Code: {response.status_code}")
print("Response Headers:")
for header, value in response.headers.items():
    print(f"{header}: {value}")

# Print the response content
print("\nResponse Content:")
print(response.text)