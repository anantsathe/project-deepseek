import zipfile
import os
import markdown
from bs4 import BeautifulSoup
import json

def process_downloaded_threads(zip_path: str):
    """Process the downloaded_threads.zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("data/course_content")
    
    # Process the extracted files
    knowledge_base = {}
    
    for root, dirs, files in os.walk("data/course_content"):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    html = markdown.markdown(content)
                    soup = BeautifulSoup(html, 'html.parser')
                    # Extract relevant information and add to knowledge_base
                    
    return knowledge_base

def process_discourse_posts(zip_path: str):
    """Process the markdown_files.zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("data/discourse_posts")
    
    # Process the extracted files
    discourse_data = {}
    
    for root, dirs, files in os.walk("data/discourse_posts"):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract metadata and content
                    # Add to discourse_data
                    
    return discourse_data