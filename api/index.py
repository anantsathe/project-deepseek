from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import openai
from dotenv import load_dotenv
import markdown
from bs4 import BeautifulSoup
import json
import requests
from openai import OpenAI
import re
from models import Link  # Assuming you have a Link Pydantic model

# Load environment variables
load_dotenv()



app = FastAPI(
    title="TDS Virtual TA",
    description="A virtual Teaching Assistant for IIT Madras Online Degree in Data Science",
    version="1.0.0"
)

# Configure OpenAI
openai.api_key = os.getenv("API_KEY")
openai.api_base = os.getenv("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class AnswerResponse(BaseModel):
    answer: str
    links: List[Link]

# Load course knowledge base (you'll need to implement this)
def load_knowledge_base():
    course_content = {}
    discourse_posts = {}

    course_dir = "./data/course_content"
    for fname in os.listdir(course_dir):
        if fname.endswith(".html") or fname.endswith(".md"):
            with open(os.path.join(course_dir, fname), "r", encoding="utf-8") as f:
                course_content[fname] = f.read()

    discourse_dir = "./data/discourse_posts"
    for fname in os.listdir(discourse_dir):
        if fname.endswith(".md"):
            with open(os.path.join(discourse_dir, fname), "r", encoding="utf-8") as f:
                discourse_posts[fname] = f.read()

    return {
        "course_content": course_content,
        "discourse_posts": discourse_posts
    }


knowledge_base = load_knowledge_base()

@app.post("/api/", response_model=AnswerResponse)
async def answer_question(request: QuestionRequest):
    try:
        # Step 1: Search knowledge base for relevant information
        relevant_content = search_knowledge_base(request.question)
        
        # Step 2: Generate prompt for OpenAI
        prompt = generate_prompt(request.question, relevant_content)
        
        # Step 3: Call OpenAI API
        client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful teaching assistant..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Step 4: Process response and extract links
        answer = response.choices[0].message.content
        links = extract_links(answer, relevant_content)
        
        return {
            "answer": answer,
            "links": links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def search_knowledge_base(question: str) -> dict:
    course_hits = {}
    discourse_hits = {}
    total_chars = 0
    max_chars = 5000  # You can tune this

    keywords = question.lower().split()

    # Search and collect up to max_chars of relevant text
    for fname, content in knowledge_base["course_content"].items():
        if total_chars >= max_chars:
            break
        if any(kw in content.lower() for kw in keywords):
            snippet = content[:1000]
            total_chars += len(snippet)
            course_hits[fname] = snippet

    for fname, content in knowledge_base["discourse_posts"].items():
        if total_chars >= max_chars:
            break
        if any(kw in content.lower() for kw in keywords):
            snippet = content[:1000]
            total_chars += len(snippet)
            discourse_hits[fname] = snippet

    return {
        "course_content": course_hits,
        "discourse_posts": discourse_hits
    }



def generate_prompt(question: str, context: dict) -> str:
    # Generate a comprehensive prompt with question and context
    prompt = f"""
    Question: {question}
    
    Context from course materials:
    {json.dumps(context.get('course_content', {}), indent=2)}
    
    Context from Discourse posts:
    {json.dumps(context.get('discourse_posts', {}), indent=2)}
    
    Please provide a detailed answer with references to the course materials where applicable.
    """
    return prompt


def extract_links(answer: str, context: dict) -> List[Link]:
    links = []
    seen_urls = set()

    for section in ["course_content", "discourse_posts"]:
        for fname, text in context.get(section, {}).items():
            # Find all URLs in the content
            matches = re.findall(r'(https?://[^\s)"]+)', text)

            for url in matches:
                # If URL is in answer or is relevant (even if not explicitly mentioned)
                if url not in seen_urls:
                    # Add the link with a descriptive label
                    links.append(Link(url=url, text=f"Referenced in {fname}"))
                    seen_urls.add(url)

                # Limit to top 2 links to keep response clean
                if len(links) >= 2:
                    return links

    return links

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)