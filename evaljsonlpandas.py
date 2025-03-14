import pandas as pd
import json

# Specify the path to your JSONL file
file_path = "output2.jsonl"

# Read the JSONL file and load it into a list of dictionaries
data = []
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line.strip()))

# Convert the list of dictionaries to a Pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)