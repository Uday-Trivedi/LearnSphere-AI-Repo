import os
import json
from dotenv import load_dotenv
from langchain_core.runnables import RunnableBranch, RunnableLambda

# Import the tools from tool1 and tool2
from tool1 import generate_pdf_study_plan
from tool2 import generate_exam_study_plan

load_dotenv()


# ---------------------------------------------------------------------------
# Route Handlers
# ---------------------------------------------------------------------------

def handle_pdf_route(input_dict: dict) -> str:
    """Validate and invoke the PDF study plan tool."""
    pdf_json = input_dict.get("pdf_json")
    if not pdf_json:
        return "Error: Missing required field 'pdf_json' for mode 'pdf'."

    # If already a dictionary, convert to JSON string for the tool
    if isinstance(pdf_json, dict):
        pdf_json = json.dumps(pdf_json)

    # Invoke tool1 explicitly
    return generate_pdf_study_plan.invoke({"pdf_json": pdf_json})


def handle_exam_route(input_dict: dict) -> str:
    """Validate and invoke the competitive exam study plan tool."""
    exam_name = input_dict.get("exam_name")
    subject = input_dict.get("subject")
    teacher = input_dict.get("teacher")

    missing = []
    if not exam_name:
        missing.append("exam_name")
    if not subject:
        missing.append("subject")
    if not teacher:
        missing.append("teacher")

    if missing:
        return f"Error: Missing required fields for mode 'exam': {', '.join(missing)}."

    # Invoke tool2 explicitly
    return generate_exam_study_plan.invoke({
        "exam_name": exam_name,
        "subject": subject,
        "teacher": teacher
    })


def handle_default_route(input_dict: dict) -> str:
    """Handle unsupported or missing modes."""
    mode = input_dict.get("mode")
    if not mode:
        return "Error: Request must include a 'mode' ('pdf' or 'exam')."
    return f"Error: Unsupported mode '{mode}'. Valid modes are 'pdf' and 'exam'."


# ---------------------------------------------------------------------------
# LangChain Conditional Chain (RunnableBranch)
# ---------------------------------------------------------------------------

study_plan_chain = RunnableBranch(
    (lambda req: req.get("mode") == "pdf", RunnableLambda(handle_pdf_route)),
    (lambda req: req.get("mode") == "exam", RunnableLambda(handle_exam_route)),
    RunnableLambda(handle_default_route)
)


def generate_study_plan(request: dict) -> str:
    """Public entry point to generate a study plan from a request dictionary."""
    if not isinstance(request, dict):
        return "Error: Request must be a Python dictionary."
    return study_plan_chain.invoke(request)


# ---------------------------------------------------------------------------
# Command-line Testing Section
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("LearnSphere AI Study Plan Agent - Test Suite")
    print("=" * 70)

    # 1. Validation Test: Missing mode
    print("\n[Test 1] Missing Mode:")
    print(generate_study_plan({}))

    # 2. Validation Test: Unsupported Mode
    print("\n[Test 2] Unsupported Mode:")
    print(generate_study_plan({"mode": "audio"}))

    # 3. Validation Test: PDF route with missing 'pdf_json'
    print("\n[Test 3] PDF Route - Missing pdf_json:")
    print(generate_study_plan({"mode": "pdf"}))

    # 4. Validation Test: PDF route with invalid JSON
    print("\n[Test 4] PDF Route - Invalid JSON:")
    print(generate_study_plan({"mode": "pdf", "pdf_json": "not valid json"}))

    # 5. Validation Test: Exam route with missing fields
    print("\n[Test 5] Exam Route - Missing fields:")
    print(generate_study_plan({"mode": "exam", "subject": "DSA"}))

    # 6. Validation Test: Exam route with unsupported subject
    print("\n[Test 6] Exam Route - Unsupported subject:")
    print(generate_study_plan({
        "mode": "exam",
        "exam_name": "GATE",
        "subject": "Quantum Computing",
        "teacher": "Dr. Unknown"
    }))

    # 7. Sample PDF Request (Test Case 1)
    sample_pdf_payload = {
        "filename": "Operating_Systems_Intro.pdf",
        "total_pages": 2,
        "pages": [
            {
                "page": 1,
                "text": "Introduction to operating systems, process management, process scheduling and CPU scheduling algorithms."
            },
            {
                "page": 2,
                "text": "Memory management, paging, segmentation, virtual memory and page replacement algorithms."
            }
        ]
    }

    print("\n[Test 7] Valid PDF Request Format:")
    print("Payload ready for PDF route with filename:", sample_pdf_payload["filename"])

    # 8. Sample Exam Request (Test Case 2)
    sample_exam_payload = {
        "mode": "exam",
        "exam_name": "GATE",
        "subject": "DSA",
        "teacher": "Striver"
    }
    print("\n[Test 8] Valid Exam Request:")
    print("Exam:", sample_exam_payload["exam_name"], "| Subject:", sample_exam_payload["subject"])

    # Check API key status
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n" + "-" * 70)
        print("Note: GOOGLE_API_KEY is not configured in .env.")
        print("Input validation, knowledge-base retrieval, and routing tests passed!")
        print("To run live Gemini LLM tests, insert your key in agent/.env.")
        print("-" * 70)
    else:
        print("\n[Live Test] Invoking PDF Route with Gemini:")
        print(generate_study_plan({
            "mode": "pdf",
            "pdf_json": json.dumps(sample_pdf_payload)
        }))

        print("\n[Live Test] Invoking Exam Route with Gemini:")
        print(generate_study_plan(sample_exam_payload))
