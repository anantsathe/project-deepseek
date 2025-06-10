# 🤖 TDS Virtual TA

A virtual Teaching Assistant for the **Tools in Data Science** course offered by IIT Madras' Online Degree Program.

This app uses OpenAI's language model to answer student questions based on:

- ✅ Course content (`tds.s-anand.net`)
- ✅ Discourse forum posts (Jan–Apr 2025)

Deployed publicly on **Vercel**, this API can receive a student’s question (and optional image) and return a relevant answer with supporting links.

---

## 📌 Features

- FastAPI-based backend
- Uses OpenAI API via `aipipe.org` proxy
- Searches course content and Discourse markdown files
- Extracts and returns relevant supporting links
- Compatible with [`promptfoo`](https://github.com/promptfoo/promptfoo) for evaluation

---

## 🚀 API Endpoint

> POST `/api/`  
> Accepts a JSON payload:

```json
{
  "question": "Should I use GPT-3.5 or GPT-4o-mini?",
  "image": "<optional base64-encoded image>"
}
Returns:

json
Copy
Edit
{
  "answer": "Use GPT-3.5-turbo for this assignment as per ...",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/...",
      "text": "Clarification by TA"
    }
  ]
}
🗂️ Folder Structure
pgsql
Copy
Edit
tds-virtual-ta/
├── api/
│   └── index.py           ← FastAPI app entrypoint
├── models.py              ← Pydantic models
├── data/
│   ├── course_content/    ← Extracted HTML/MD files
│   └── discourse_posts/   ← Extracted markdown files
├── requirements.txt
├── vercel.json
├── LICENSE
└── README.md              ← You are here
⚙️ Setup Instructions
1. Install dependencies
bash
Copy
Edit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
2. Set environment variables
Create a .env file:

ini
Copy
Edit
API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://aipipe.org/openai/v1
3. Run locally
bash
Copy
Edit
uvicorn api.index:app --reload
4. Test the API
bash
Copy
Edit
curl -X POST http://localhost:8000/api/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the deadline for Project 1?"}'
🧪 Evaluation with promptfoo
To evaluate:

Replace the url in project-tds-virtual-ta-promptfoo.yaml with your Vercel endpoint.

Run:

bash
Copy
Edit
npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
📝 License
This project is licensed under the MIT License.

👨‍🎓 Author
Developed by Anant Sathe
For the January 2025 semester of Tools in Data Science, IIT Madras
GitHub: @anantsathe