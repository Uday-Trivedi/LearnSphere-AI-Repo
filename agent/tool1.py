import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Model name configuration (easy to change in one place)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Prompt template for PDF-based study planning
PDF_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["pdf_content", "filename", "total_pages"],
    template="""You are the LearnSphere AI Study Planning Assistant.

Your task is to create a practical study plan using the
content extracted from a student's uploaded PDF.

SOURCE DOCUMENT:
{pdf_content}

DOCUMENT NAME:
{filename}

TOTAL PAGES:
{total_pages}

INSTRUCTIONS:

1. Read the supplied document content carefully.
2. Identify the actual topics and subtopics present in it.
3. Arrange topics in a logical learning order.
4. Divide the material into 3 to 5 focused study sessions. Keep explanations concise and actionable.
5. Estimate the time needed for each session.
6. For each session, include:
   - Session number.
   - Topic.
   - Subtopics to cover.
   - Learning objective.
   - Recommended study activity.
   - Practice questions or revision activity.
   - Estimated duration.
   - Relevant source page numbers when available.
7. Include a final revision session covering the identified topics.
8. Adjust the plan to the amount of material actually provided.
9. Do not introduce unrelated syllabus topics.
10. Do not invent information, formulas, page references or
    resource links.
11. If the extracted text is incomplete, acknowledge the limitation.
12. Keep explanations understandable for a student.
13. Return a structured, readable study plan.
14. Do not return Python code or explain your internal reasoning.

OUTPUT STRUCTURE:

Study Plan Title
Document Overview
Topics Identified
Recommended Study Sessions
Revision Strategy
Practice and Self-Assessment
Estimated Total Study Time
Source Coverage and Limitations
"""
)

@tool
def generate_pdf_study_plan(pdf_json: str) -> str:
    """Generate a structured study plan from PDF text extraction JSON."""
    # 1. Parse and validate the input JSON
    try:
        if isinstance(pdf_json, str):
            data = json.loads(pdf_json)
        elif isinstance(pdf_json, dict):
            data = pdf_json
        else:
            return "Error: Invalid input format. Expected a JSON string or dictionary."
    except json.JSONDecodeError:
        return "Error: Could not parse input as valid JSON."

    filename = data.get("filename", "Uploaded_Document.pdf")
    total_pages = data.get("total_pages", 0)
    pages = data.get("pages", [])

    if not pages:
        return "Error: The provided PDF JSON contains no pages or extracted text."

    # 2. Extract page text preserving page numbers
    page_texts = []
    for p in pages:
        page_num = p.get("page") or p.get("page_number", "?")
        text = p.get("text", "").strip()
        page_texts.append(f"--- Page {page_num} ---\n{text}")

    pdf_content = "\n\n".join(page_texts)

    # 3. Validate Google API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "Error: GOOGLE_API_KEY is not configured or missing in .env. Please set a valid Gemini API key."

    # 4. Call Gemini to generate the study plan
    try:
        llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            google_api_key=api_key,
            temperature=0.2
        )
        chain = PDF_PROMPT_TEMPLATE | llm
        response = chain.invoke({
            "pdf_content": pdf_content,
            "filename": filename,
            "total_pages": total_pages
        })
        return response.content
    except Exception as e:
        return f"Error while calling Gemini API: {str(e)}"
