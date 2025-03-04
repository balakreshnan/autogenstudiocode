import requests
import json
from azure.identity import DefaultAzureCredential

# Create an instance of DefaultAzureCredential
credential = DefaultAzureCredential()


# Replace with your actual access token
access_token = credential.get_token("https://graph.microsoft.com/.default").token

# Microsoft Graph API endpoint
graph_url = "https://graph.microsoft.com/v1.0/me/joinedTeams"

# Headers for the request, including the Authorization token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

try:
    # Make the GET request to the Microsoft Graph API
    response = requests.get(graph_url, headers=headers)

    # Check if the request was successful (status code 200)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    # Parse the JSON response
    teams_data = response.json()
    print('Response: ' , teams_data)

    # Check if the 'value' key exists in the response
    if 'value' in teams_data:
        teams = teams_data['value']

        # Display the teams in a formatted way
        print("Joined Teams:")
        print("-------------")
        for team in teams:
            print(f"Team Name: {team['displayName']}")
            print(f"Team ID: {team['id']}")
            print(f"Description: {team['description']}")
            print("-------------")
    else:
        print("No 'value' key found in the response.")
        print("Response:", teams_data)  # Print the whole response for debugging

except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"Something went wrong: {err}")
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    print(f"Response text: {response.text}") # Print the raw response text for debugging
except Exception as e:
    print(f"An unexpected error occurred: {e}")
