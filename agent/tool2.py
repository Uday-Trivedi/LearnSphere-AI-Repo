import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Model name configuration (easy to change in one place)
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Mapping of supported subjects to their knowledge base JSON files
KNOWLEDGE_BASES = {
    "dsa": "dsa.json",
    "cn": "cn.json",
    "os": "os.json",
    "aptitude": "aptitude.json",
    "sql": "sql.json",
    "dbms": "sql.json"
}

# Prompt template for competitive exam study planning
EXAM_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["exam_name", "subject", "teacher", "knowledge_base"],
    template="""You are the LearnSphere Competitive Exam Study Planning Assistant.

Create a structured preparation plan using the supplied
competitive examination information and retrieved JSON knowledge base.

EXAMINATION:
{exam_name}

SUBJECT:
{subject}

SELECTED EDUCATOR:
{teacher}

RETRIEVED KNOWLEDGE BASE:
{knowledge_base}

INSTRUCTIONS:

1. Treat the retrieved JSON knowledge base as the primary source.
2. Group the curriculum into 4 to 6 concise weekly modules / study blocks for fast, practical execution.
3. Follow the knowledge-base ordering wherever possible.
4. Keep explanations concise, crisp, and high-impact (bullet points).
5. For each weekly module / study block, provide:
   - Module number and title.
   - Topics & subtopics covered from the knowledge base.
   - Learning objective.
   - Study resource from the knowledge base, when available.
   - Practice or revision activity.
   - Estimated duration (hours).
6. Include regular revision and a final self-assessment.
7. Include mock tests only as recommendations unless the knowledge base explicitly provides particular tests.
8. Do not invent video links, course URLs, playlist names, resource identifiers or lesson numbers.
9. Do not claim that the selected educator has covered a topic unless supported by the retrieved knowledge base.
10. If the knowledge base does not contain enough information, clearly state what is missing.
11. Keep the plan relevant to the selected examination and subject.
12. Return a structured, readable study plan.
13. Do not return Python code or explain your internal reasoning.

OUTPUT STRUCTURE:

Study Plan Title
Exam and Subject Overview
Topics and Learning Sequence
Recommended Study Sessions
Revision Schedule
Practice Strategy
Mock Test and Self-Assessment Strategy
Estimated Total Study Time
Knowledge Base Coverage and Limitations
"""
)


def simple_json_retriever(subject: str):
    """Retrieve and parse the relevant JSON knowledge base file."""
    normalized_subject = subject.strip().lower()
    filename = KNOWLEDGE_BASES.get(normalized_subject)

    if not filename:
        valid_subjects = ", ".join(KNOWLEDGE_BASES.keys())
        return None, f"Error: Unsupported subject '{subject}'. Supported subjects are: {valid_subjects}."

    # Look for knowledge base file in agent/knowledge_base or ../knowledge_base
    current_dir = os.path.dirname(os.path.abspath(__file__))
    potential_paths = [
        os.path.join(current_dir, "knowledge_base", filename),
        os.path.join(current_dir, "..", "knowledge_base", filename),
        os.path.join(os.getcwd(), "knowledge_base", filename),
    ]

    target_path = None
    for path in potential_paths:
        if os.path.exists(path):
            target_path = path
            break

    if not target_path:
        return None, f"Error: Knowledge-base file '{filename}' for subject '{subject}' was not found."

    try:
        with open(target_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data, None
    except Exception as e:
        return None, f"Error: Failed to read or parse knowledge base '{filename}': {str(e)}"


@tool
def generate_exam_study_plan(exam_name: str, subject: str, teacher: str) -> str:
    """Generate a structured competitive exam study plan using retrieved JSON knowledge base."""
    # 1. Retrieve the knowledge base content
    kb_data, error_message = simple_json_retriever(subject)
    if error_message:
        return error_message

    # Format the retrieved JSON cleanly and compactly for fast processing
    if isinstance(kb_data, dict) and "topics" in kb_data:
        compact_kb = {
            "subject": kb_data.get("subject_name", subject),
            "total_topics": kb_data.get("total_topics", len(kb_data["topics"])),
            "total_hours": kb_data.get("total_hours"),
            "curriculum": [
                {
                    "topic": t.get("name"),
                    "difficulty": t.get("difficulty"),
                    "hours": t.get("hours"),
                    "concepts": t.get("concepts", [])[:4]
                }
                for t in kb_data.get("topics", [])
            ]
        }
        kb_string = json.dumps(compact_kb, indent=2)
    else:
        kb_string = json.dumps(kb_data, indent=2)

    # 2. Validate Google API Key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return "Error: GOOGLE_API_KEY is not configured or missing in .env. Please set a valid Gemini API key."

    # 3. Call Gemini to generate the plan
    try:
        llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            google_api_key=api_key,
            temperature=0.2
        )
        chain = EXAM_PROMPT_TEMPLATE | llm
        response = chain.invoke({
            "exam_name": exam_name,
            "subject": subject,
            "teacher": teacher,
            "knowledge_base": kb_string
        })
        return response.content
    except Exception as e:
        return f"Error while calling Gemini API: {str(e)}"
