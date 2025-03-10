import json

# Path to your .jsonl file
file_path = "unittestdata01-2-1.JSONL"

# Path to save the JSONL file
output_file = "output1.jsonl"

# Open and read the .jsonl file
with open(file_path, 'r') as file:
    for line in file:
        # Parse each line as a JSON object
        json_obj = json.loads(line.strip())

        # Write data to JSONL file
        with open(output_file, 'a+') as file:
            json_line = json.dumps(json_obj)  # Convert dictionary to JSON string
            file.write(json_line + '\n')  # Write JSON string followed by a newline character
        
        # Evaluate or process the JSON object
        # print(json_obj)  # Replace with your evaluation logic





print(f"Data saved to {output_file}")