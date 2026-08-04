import os
import certifi
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict, Annotated
import operator
import uuid
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import(
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq
from tools.flight_tool import search_flights

# load the GROQ_API_KEY from the environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")   
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")

# initialize the ChatGroq model with the specified model and API key
llm = ChatGroq(
    model = "llama-3.3-70b-versatile", 
    api_key = GROQ_API_KEY
)

# test the model by sending a simple message and printing the response
# response = llm.invoke("Hello, how are you?")
# print(response)



# Create state
class TravelState(TypedDict):
    message: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# Define agent functions

#flight agent
def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "message": [
            AIMessage(content="Flight results fetched successfully.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


#hotel agent
def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "message": [
            AIMessage(content="Hotel results fetched successfully.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }