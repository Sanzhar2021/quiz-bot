import google.generativeai as genai
from dotenv import load_dotenv  # 👈
load_dotenv()
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY")
)

for m in genai.list_models():
    print(m.name, "—", m.supported_generation_methods)
