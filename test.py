import os
import re
from main import load_knowledge_base  # assuming your load function is in main.py

# Load the knowledge base
knowledge_base = load_knowledge_base()

# Print some links from the knowledge base to verify they're loaded correctly
for section in ["course_content", "discourse_posts"]:
    for fname, text in knowledge_base[section].items():
        links = re.findall(r'(https?://[^\s)"]+)', text)
        if links:
            print(f"{fname} has links: {links[:2]}")
