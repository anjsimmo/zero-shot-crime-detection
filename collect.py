import openai
import pandas as pd
import sys
import os
import re
from gpt_cache import get_cache, put_cache
import time

try:
    # load OPENAI_API_KEY from openai_secrets.py if it exists
    import openai_secrets
except:
    pass

if not os.environ.get("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY environment variable not found")

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Get the output file and labels file from command-line arguments
if len(sys.argv) > 1:
    output_file = sys.argv[1]
else:
    output_file = "output.csv"

if len(sys.argv) > 2:
    labels_file = sys.argv[2]
else:
    labels_file = "test_001_labels.txt"

def gpt(prompt, model="gpt-4"):
    # prompt GPT, using cached response if we have already made this query
    response = get_cache(prompt, f"cache-{model}.json")
    if response:
        return response
    
    retries = 0
    while not response:
        try:
            response = openai.ChatCompletion.create(
              #model="gpt-3.5-turbo",
              model=model,
              messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except openai.error.RateLimitError as e:
            if retries < 8:
                print(f"Hit rate limit, retries={retries}\n", e)
                retries += 1
                time.sleep(2 ** retries) # 1, 2, 4, 8, 16, 32, 64, 128 sec.
                continue
            raise
        except openai.error.InvalidRequestError as e:
            # unable to respond (e.g. token limit)
            return None
    
    put_cache(prompt, response, f"cache-{model}.json")
    return response


# Load data from test_001_labels.txt
with open(labels_file, "r") as file:
    lines = file.readlines()

# Initialize an empty list to store the data for the spreadsheet
data = []

# This is to verify that txt file has expected format before continuing
for line in lines:
    # Split the line into video name and manual description
    video_name, manual_description = line.split(" ", 1)
    manual_description = manual_description.strip()
    print(video_name, manual_description)
        
# Open a log file to store the OpenAI responses
with open("gpt_responses.log", "w") as log_file:
    for line in lines:
        # Split the line into video name and manual description
        video_name, manual_description = line.split(" ", 1)
        manual_description = manual_description.strip()

        if manual_description:
            # Format the prompt for the GPT response
            prompt = f"""SURVEILLANCE VIDEO DESCRIPTION:
{manual_description}

TASK:
List possible explanations, and categorise them as one of [Abuse, Arrest, Arson, Assault, Burglary, Explosion, Fighting, Road Accident, Robbery, Shooting, Shoplifting, Stealing, Vandalism, Normal]. Then determine which category is most likely. Let's think step by step. Finally, output one line containing a single category in quotes. Do not include anything other than the category on the final line."""

            # Call the OpenAI API with the formatted prompt
            #response = openai.Completion.create(engine="text-chatgpt-002", prompt=prompt, max_tokens=100, n=1, stop=None, temperature=0.7)
            response = gpt(prompt)
            
            if response == None:
                # invalid request
                gpt_response = ""
            else:
                # Get the GPT response from the API result
                gpt_response = response["choices"][0]["message"]["content"]
        else:
            gpt_response = ""
        
        gpt_final_response = gpt_response.split("\n")[-1]
        if '"' in gpt_final_response:
            # the answer is in quotes
            gpt_final_response = gpt_final_response.split('"')[-2]
            gpt_final_response = gpt_final_response.split(".")[0] # remove punctuation
            gpt_final_response = gpt_final_response.replace(' ', '') # remove whitespace
        elif re.match(r'.*\[(.*)\].*',  gpt_final_response):
            # the answer is in []
            gpt_final_response = re.match(r'.*\[(.*)\].*',  gpt_final_response).groups()[0]
            gpt_final_response = gpt_final_response.split(".")[0] # remove punctuation
            gpt_final_response = gpt_final_response.replace(' ', '') # remove whitespace

        if gpt_final_response not in ["Abuse", "Arrest", "Arson", "Assault", "Burglary", "Explosion", "Fighting", "RoadAccident", "Robbery", "Shooting", "Shoplifting", "Stealing", "Vandalism", "Normal"]:
            # did not match expected output format
            gpt_final_response = f'__invalid__'
        
        if gpt_response == "":
            # couldn't process due to missing input or inability to process
            gpt_final_response = f'__invalid_input__'

        # Print the response to the console
        print(f"Video: {video_name}\nGPT Response: {gpt_response}\n")

        # Write the response to the log file
        log_file.write(f"Video: {video_name}\nGPT Response: {gpt_response}\n\n")

        # Append the current row data to the data list
        data.append([video_name, manual_description, gpt_response, gpt_final_response])

# Create a pandas DataFrame with the data and column names
df = pd.DataFrame(data, columns=["video_name", "manual_description", "gpt_response", "gpt_final_response"])

# Save the DataFrame to an CSV file
df.to_csv(output_file, index=False)