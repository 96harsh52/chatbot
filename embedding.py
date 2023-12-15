import os
import difflib
import pandas as pd
from openai import OpenAI

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "API_key"

def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def is_similar(text1, text2, threshold=0.9):
    try:
        d = difflib.SequenceMatcher(None, text1, text2)
        return d.ratio() >= threshold
    except Exception as e:
        return f"Error comparing texts: {str(e)}"

def get_embedding(text, model="text-embedding-ada-002"):
    try:
        text = text.replace("\n", " ")
        res = client.embeddings.create(input=[text], model=model)
        return res.data[0].embedding
    except Exception as e:
        return f"Error getting embedding: {str(e)}"

def process_files(input_directory, output_directory):
    print(input_directory,output_directory)
    try:
        # List to store data for DataFrame
        df_data = []

        # Dictionary to store file content
        file_contents = {}

        # Iterate through each file in the directory
        for filename in os.listdir(input_directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(input_directory, filename)

                # Read text from the file
                file_text = read_text_file(file_path)

                # Check similarity with existing files
                include_file = True
                for existing_filename, existing_text in file_contents.items():
                    if is_similar(file_text, existing_text):
                        include_file = False
                        break

                # If not similar to existing files, add to dictionary and DataFrame data
                if include_file:
                    file_contents[filename] = file_text
                    df_data.append([filename, file_text])

        # Create a DataFrame from the collected data
        columns = ['File_Name', 'text']
        df = pd.DataFrame(df_data, columns=columns)

        # Function to get text embeddings
        df['embedding'] = df['text'].apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))

        # Extract file name from input_directory
        folder_name = os.path.basename(input_directory)
        print("fgfgfgfgf",folder_name)

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Specify the output file path
        output_file_path = os.path.join(output_directory, f'{folder_name}_embedded.csv')
        print(output_file_path)

        # If the file already exists, delete it
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        # Save the DataFrame to a CSV file with embeddings
        df.to_csv(output_file_path, index=False)

        return f"CSV file '{output_file_path}' created successfully."

    except Exception as e:
        return f"Error processing files: {str(e)}"


# Initialize OpenAI client
client = OpenAI()

# # Specify input and output directories
# # input_directory = 'D:\CG-Vks\chatbot_1\data\www.geeks5g.com'
# # output_directory = 'D:/CG-Vks/Final_chatbot/t'
# #
# # # Process files
# # result = process_files(input_directory, output_directory)
# # print(result)
