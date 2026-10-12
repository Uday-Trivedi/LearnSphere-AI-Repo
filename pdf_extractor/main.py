from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF

app = FastAPI()

# ---------------------------------------------------------
# CORS Configuration
# You can specify your friend's React frontend URL here
# (e.g., "http://localhost:3000" for CRA or "http://localhost:5173" for Vite).
# "*" allows requests from any frontend address during development.
# ---------------------------------------------------------
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    # 1. Validate that the uploaded file is a PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a valid PDF file."
        )

    try:
        # 2. Read the uploaded file bytes
        pdf_bytes = await file.read()

        # 3. Open the PDF document using PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # 4. Extract selectable text from each page
        pages_list = []
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pages_list.append({
                "page_number": page_number + 1,
                "text": page.get_text()
            })

        # 5. Return the extracted data as JSON
        return {
            "filename": file.filename,
            "total_pages": len(pdf_document),
            "pages": pages_list
        }

    except Exception:
        # Handle unreadable, encrypted, or corrupted PDF files
        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF. The file may be corrupt or unreadable."
        )
