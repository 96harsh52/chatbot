## Prerequisites
Python 3.9
pip (Python package installer)
Installation


## Clone the repository:

git clone https://github.com/your-username/fastapi-file-upload-embedding.git

cd fastapi-file-upload-embedding


## Install dependencies:

pip install -r requirements.txt


## Running Locally
To run the application locally, execute the following command:

uvicorn main:app --reload --port 8000
The application will be accessible at http://127.0.0.1:8000

## Usage

Step 1: File Upload
Send a POST request to /upload-file/ with the desired folder name and the file you want to upload. Supported file types include .txt, .csv, .json, .pdf, .ppt, and .pptx.

Example using http:

http -f POST http://127.0.0.1:8000/upload-file/ folder_name=my_folder file@/path/to/your/file.pdf



Step 2: Extract Text from Website
Send a POST request to /extract-text/ with a JSON payload containing the URL you want to extract text from.

Example using http:

http POST http://127.0.0.1:8000/extract-text/ url="https://example.com"




Step 3: List Existing Folders
Send a GET request to /existing_folders_list/ to get a list of existing folders.

Example using http:

http http://127.0.0.1:8000/existing_folders_list/




Step 4: Process Files for Embedding
Send a GET request to /embedding/ with the input_directory parameter set to the folder name you want to process.

Example using http:

http http://127.0.0.1:8000/embedding/ input_directory=my_folder


## AWS Configuration
If you want to upload files to AWS, you need to modify the upload folder location and embedding folder location accordingly.

Update the upload_file function in main.py to save files to your AWS S3 bucket.

Update the process_with_path_parameter function in main.py to read and write files from/to your AWS S3 bucket.

Make sure to configure your AWS credentials for authentication.
