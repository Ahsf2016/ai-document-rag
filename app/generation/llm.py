import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

print("API key loaded:", os.getenv("GROQ_API_KEY") is not None)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_answer(question: str, context: str) -> str:

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the context,
say that the information is not present in the document.

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content