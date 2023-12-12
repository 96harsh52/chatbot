import os
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

def is_link(s: bytes or str):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    parsed_url = urlparse(s)
    return parsed_url.scheme in ['http', 'https']

def extract_text_from_url(url, website_name):
    # Create a "data" folder if it doesn't exist
    if not os.path.exists("data"):
        os.mkdir("data")

    # Create a folder with the website name inside the "data" folder
    website_folder = os.path.join("data", website_name)
    if not os.path.exists(website_folder):
        os.mkdir(website_folder)

    header = {'User-Agent': 'NodePing'}
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        with open(f'{website_name}_error.log', 'a', encoding='utf-8') as log_file:
            log_file.write(f"Failed to fetch the content from the URL: {url}\n")
        return f"Failed to fetch the content from the URL: {url}\n"

    soup = BeautifulSoup(response.content, 'html.parser')
    links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            links.append(href)

    valid_links = list(filter(is_link, links))

    # Counter for incrementing the page name
    counter = 1

    for valid_url in valid_links:
        response = requests.get(valid_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_text = soup.get_text()
            cleaned_text = ' '.join(all_text.split())

            # Extract page_name from the original URL with an increment
            page_name = f"{os.path.basename(urlparse(url).path)}_{counter}"

            # Save data as a text file in the website folder inside the "data" folder
            file_path = os.path.join(website_folder, page_name + '.txt')

            # If the file doesn't exist, create a new file
            save_text_to_file(file_path, cleaned_text)

            with open(f'upload_logs.log', 'a', encoding='utf-8') as log_file:
                log_file.write(f"Successfully extracted text from {valid_url} and updated {website_folder}/{page_name}.txt\n")

            # Increment the counter
            counter += 1
        else:
            with open(f'error.log', 'a', encoding='utf-8') as log_file:
                log_file.write(f"Failed to fetch the content from the URL: {valid_url}\n")

    return f"Successfully extracted text from all valid links"

def save_text_to_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

# Example usage
# url = 'https://www.geeks5g.com/'
# website_name = 'gree'
# print(extract_text_from_url(url, website_name))

