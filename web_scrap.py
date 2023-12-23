import os  # Importing the os module for working with the file system
import requests  # Importing the requests module for making HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for HTML parsing
from urllib.parse import urlparse  # Importing urlparse for parsing URLs
from datetime import datetime  # Importing datetime for timestamping
from concurrent.futures import ThreadPoolExecutor  # Importing ThreadPoolExecutor for parallel processing

def is_link(s: bytes or str):
    """Check if the given string is a valid link."""
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    parsed_url = urlparse(s)
    return parsed_url.scheme in ['http', 'https']  # Checking if the scheme is 'http' or 'https'

def extract_text_from_url(url, website_name):
    """
    Extract text content from the given URL and save it in separate files for each valid link.

    Parameters:
    - url (str): The URL of the website to extract text from.
    - website_name (str): The name of the website for creating a data folder.

    Returns:
    - dict: A dictionary with status and message indicating the result.
    """
    try:
        # Create a "data" folder if it doesn't exist
        if not os.path.exists("data"):
            os.mkdir("data")

        # Create a folder with the website name inside the "data" folder
        website_folder = os.path.join("data", website_name)

        # Get all links from the URL
        header = {'User-Agent': 'NodePing'}  # Setting the User-Agent header for the request
        response = requests.get(url, headers=header)  # Making an HTTP GET request to the URL
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')  # Creating a BeautifulSoup object for HTML parsing
        links = [link.get('href') for link in soup.find_all('a')]

        # Filter valid links
        valid_links = [link for link in links if is_link(link)]

        # If there are valid links, proceed with creating folders and extracting text
        if valid_links:
            # Create a folder with the website name inside the "data" folder
            if not os.path.exists(website_folder):
                os.mkdir(website_folder)

            with ThreadPoolExecutor(max_workers=10) as executor:  # Using ThreadPoolExecutor for parallel processing
                futures = [executor.submit(process_link, valid_url, website_folder) for
                           valid_url in valid_links]

                for future in futures:
                    try:
                        future.result()
                    except requests.RequestException as e:
                        with open(f'error.log', 'a', encoding='utf-8') as log_file:
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            log_file.write(f"[{timestamp}] Error during background processing: {str(e)}\n")

        else:
            # If no valid links found, log an error and return a message
            with open(f'{website_name}_error.log', 'a', encoding='utf-8') as log_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_file.write(f"[{timestamp}] No valid links found in the URL: {url}\n")
            return {"status": 404, "message": f"No valid links found in the URL: {url}"}

    except requests.RequestException as e:
        # If there is an issue fetching the content from the URL, log an error and return a message
        with open(f'{website_name}_error.log', 'a', encoding='utf-8') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(f"[{timestamp}] Failed to fetch the content from the URL: {url}\n")
        return {"status": 401, "message": f"Failed to fetch the content from the URL: {url}"}

    return {"status": 200, "message": "Successfully extracted text from all valid links"}

def process_link(valid_url, website_folder):
    """
    Process a valid link by fetching its content and saving it in a text file.

    Parameters:
    - valid_url (str): The valid URL to process.
    - website_folder (str): The folder path for the website's data.

    Raises:
    - requests.RequestException: If there is an issue fetching the content from the URL.
    """
    try:
        response = requests.get(valid_url)  # Making an HTTP GET request to the valid URL
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')  # Creating a BeautifulSoup object for HTML parsing
        all_text = soup.get_text()  # Extracting all text from the HTML
        cleaned_text = ' '.join(all_text.split())  # Cleaning up the text content

        # Extract page_name from the second-to-last part of the URL
        page_name = valid_url.split('/')[-2]

        # Save data as a text file in the website folder inside the "data" folder
        file_path = os.path.join(website_folder, page_name + '.txt')

        # If the file doesn't exist, create a new file
        save_text_to_file(file_path, cleaned_text)

        with open(f'logs.log', 'a', encoding='utf-8') as log_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_file.write(
                f"[{timestamp}] Successfully extracted text from {valid_url} and updated {website_folder}/{page_name}.txt\n")

    except requests.RequestException as e:
        raise e

def save_text_to_file(file_path, text):
    """
    Save the given text content to a file.

    Parameters:
    - file_path (str): The file path where the text content will be saved.
    - text (str): The text content to be saved.
    """
    with open(file_path, 'w', encoding='utf-8') as file:  # Opening a file for writing
        file.write(text)  # Writing the text content to the file

# Example usage
# url = 'https://www.geeks5g.com/'
# website_name = 'gree'
# print(extract_text_from_url(url, website_name))
