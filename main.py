import os
import logging
from urllib.parse import urlparse
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from embedding import process_files
from web_scrap import extract_text_from_url
from file_upload import save_uploaded_file, extract_text_from_pdf, extract_text_from_ppt

logger = logging.getLogger("rich")
app = FastAPI()

# Configure logging settings
logging.basicConfig(filename='upload_logs.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Pydantic model for input validation
class URLInput(BaseModel):
    url: str
# FastAPI endpoint for extracting text from a website
@app.post("/extract-text/", tags=["Website Text Extraction"])
async def extract_text(data: URLInput):
    # Extract the website name from the URL
    website_name = urlparse(data.url).netloc
    # Call the function to extract text from the provided URL
    extract_data = extract_text_from_url(data.url, website_name)
    return extract_data


# Dependency function to get existing folders in the "data" directory
def get_existing_folders(data_dir: str = "data"):
    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        return []
    return [item for item in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, item))]

# FastAPI endpoint to get a list of existing folders
@app.get("/existing_folders_list/", tags=["File list in Data folder"])
async def list_existing_folders(existing_folders: list = Depends(get_existing_folders)):
    return {"existing_folders": existing_folders}


# FastAPI endpoint for uploading a file to a specified folder
@app.post("/upload-file/", tags=["File Upload"])
async def upload_file(folder_name: str = Form(...), file: UploadFile = File(...)):
    try:
        current_directory = os.getcwd()
        full_input_directory = os.path.join(current_directory, "data", folder_name)
        os.makedirs(full_input_directory, exist_ok=True)

        file_path = save_uploaded_file(full_input_directory, file)

        # Check file type and handle accordingly
        if file.filename.lower().endswith(('.txt', '.csv', '.json')):
            return JSONResponse(content={"message": "File uploaded successfully", "folder_name": folder_name, "file_name": file.filename})
        elif file.filename.lower().endswith(('.pdf')):
            text = extract_text_from_pdf(file_path)
            text_file_path = os.path.splitext(file_path)[0] + ".txt"
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)
            return JSONResponse(content={"message": "PDF file uploaded and text extracted successfully",
                                         "folder_name": folder_name, "file_name": file.filename, "text_file_name": os.path.basename(text_file_path)})
        elif file.filename.lower().endswith(('.ppt', '.pptx')):
            text = extract_text_from_ppt(file_path)
            text_file_path = os.path.splitext(file_path)[0] + ".txt"
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(text)
            return JSONResponse(content={"message": "PPT file uploaded and text extracted successfully",
                                         "folder_name": folder_name, "file_name": file.filename, "text_file_name": os.path.basename(text_file_path)})
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Only .txt, .csv, .json, .pdf, .ppt, .pptx files are allowed.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Unsupported file type. Only .txt, .csv, .json, .pdf, .ppt, .pptx files are allowed.")

# FastAPI endpoint for processing files in a specified directory
@app.get("/embedding/", tags=["Embedding"])
def process_with_path_parameter(input_directory: str):
    try:
        # Find the current directory
        current_directory = os.getcwd()
        # Set the output directory for processed files
        output_directory = os.path.join(current_directory, 'embedding')
        # Set the full input directory path
        full_input_directory = os.path.join(current_directory, "data", input_directory)
        # Call the function to process files in the specified directory
        process_file = process_files(full_input_directory, output_directory)
        return process_file
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
