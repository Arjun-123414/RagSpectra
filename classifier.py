from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(temperature=0) # add ,api_key="sk-proj"

prompt = PromptTemplate(
    input_variables=["text"],
    template="""
You are a construction domain expert.

Given the following vendor bid text, classify it into ONE category only:
HVAC, Roofing, Electricity.

If unclear, choose the closest match.

Text:
{text}

Return ONLY the category name.
"""
)

def classify_chunk(text):
    response = llm.invoke(prompt.format(text=text))
    return response.content

