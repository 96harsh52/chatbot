import os
import logging
from urllib.parse import urlparse
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from embedding import process_files
import uvicorn
from web_scrap import extract_text_from_url
from file_upload import save_uploaded_file, extract_text_from_pdf, extract_text_from_ppt

# Set up logging
logger = logging.getLogger("rich")
app = FastAPI()

# Configure logging settings
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Pydantic model for input validation
class URLInput(BaseModel):
    url: str

# FastAPI endpoint for extracting text from a website
@app.post("/extract-text/", tags=["Website Text Extraction"])
async def extract_text(data: URLInput):
    try:
        # Extract the website name from the URL
        website_name = urlparse(data.url).netloc
        # Call the function to extract text from the provided URL
        extract_data = extract_text_from_url(data.url, website_name)
        return extract_data
    except Exception as e:
        return extract_data


# Dependency function to get existing folders in the "data" directory
def get_existing_folders(data_dir: str = "data"):
    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        return []
    return [item for item in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, item))]

# FastAPI endpoint to get existing folders
@app.get("/existing-folders/", tags=["Folders"])
async def read_existing_folders():
    try:
        existing_folders = get_existing_folders()
        return JSONResponse(content={"status": 200, "message":existing_folders})
    except Exception as e:
        raise JSONResponse(content={"status":401, "massage":f"An error occurred: {str(e)}"})


# FastAPI endpoint for uploading a file to a specified folder
@app.post("/upload-file/", tags=["File Upload"])
async def upload_file(folder_name: str = Form(...), file: UploadFile = File(...)):
    try:
        # Check if the file is valid
        allowed_extensions = {'.txt', '.docx', '.doc', '.pdf', '.ppt', '.pptx'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            return JSONResponse(content={"status": 401, "message": "Unsupported file type. Only .txt, .csv, .json, .pdf, .ppt, .pptx files are allowed."})

        current_directory = os.getcwd()
        full_input_directory = os.path.join(current_directory, "data", folder_name)

        # Only create the folder if the file type is allowed
        os.makedirs(full_input_directory, exist_ok=True)

        # Save the uploaded file to the specified folder
        file_path = save_uploaded_file(full_input_directory, file)

        # Return success response
        return JSONResponse(content={"status": 200, "message": "File uploaded successfully"})

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return JSONResponse(content={"status": 500, "message": "Internal server error"})


# FastAPI endpoint for processing files in a specified directory


@app.get("/embedding/", tags=["Embedding"])
def process_with_path_parameter(input_directory: str):
    try:
        current_directory = os.getcwd()
        output_directory = os.path.join(current_directory, 'embedding')
        full_input_directory = os.path.join(current_directory, "data", input_directory)
        process_file = process_files(full_input_directory, output_directory)

        if process_file["status"] == 200:
            return JSONResponse(content={"status": 200, "message": "Files processed successfully", "data": process_file})
        elif process_file["status"] == 401:
            return JSONResponse(content={"status": 401, "message": process_file["message"]})
        else:
            raise JSONResponse(content={"status":401, "message":f"An error occurred during file processing: {process_file['message']}"})

    except ValueError as ve:
        return JSONResponse(content={"status": 401, "message": f"ValueError: {str(ve)}"})
    except Exception as e:
        return JSONResponse(content={"status": 401, "message": f"An error occurred during file processing: {str(e)}"})


if __name__ == '__main__':
    uvicorn.run(app,host = "127.0.0.1",port = 8000)