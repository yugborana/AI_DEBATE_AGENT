from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

MODEL_NAME = "qwen2.5:1.5b"

def _llm(system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    model = ChatOllama(model=MODEL_NAME, temperature=0.4, streaming=True)
    return prompt | model