import os
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_structured_llm(
    model: str = "gemini-3.1-flash",
    temperature: float = 0.1,
):
    """
    Returns a base Gemini LLM instance.
    """
    return ChatGoogleGenerativeAI(
        model=model,
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=temperature,
        max_retries=6,
    )


def extract_structured_output(
    query: str,
    schema: Type[BaseModel],
    model: str = "gemini-2.5-flash",
):
    """
    Takes a natural language query + Pydantic schema
    and returns structured output.
    """

    llm = get_structured_llm(model=model)
    structured_llm = llm.with_structured_output(schema)

    return structured_llm.invoke(query)