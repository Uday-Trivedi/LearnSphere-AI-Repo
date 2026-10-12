import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env file
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

print(f"1. Sending 'Hi' to Gemini ({model})...")

try:
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3
    )
    response = llm.invoke("Hi! Say hello in 5 words.")
    print("2. Response received:")
    print(response.content)
except Exception as e:
    print("Error:", e)
