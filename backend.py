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
from tools.flight_tool import search_flights #this is the flight search function from flight_tool.py
from tools.tavily_tool import tavily_search #this is the hotel search function from tavily_tool.py

import sqlite3 #this is for the sqlite database to store the state of the graph
from langgraph.checkpoint.sqlite import SqliteSaver #this is the checkpointing mechanism to save the state of the graph


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


#itinerary agent
def itinerary_agent(state: TravelState):
    prompt = f"""Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

Make the itinerary practical, budget-aware, and easy to follow.
"""

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


#final agent
def final_agent(state: TravelState):
    final_prompt = f"""Generate the final travel response for the user.

User Request:
{state['user_query']}

Flights:
{state['flight_results']}

Hotels:
{state['hotel_results']}

Itinerary:
{state['itinerary']}

Format the final answer beautifully using these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight API may not provide ticket prices if pricing is unavailable.
- Keep the response useful for real travel planning.
"""

    response = llm.invoke([
        SystemMessage(content="You are a professional AI travel booking assistant."),
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }



#checkpointer
conn = sqlite3.connect(database="travel.db", check_same_thread=False)
checkpoint = SqliteSaver(conn)


#graph
graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

travel_graph = graph.compile(checkpointer=checkpoint)



# Function to run the travel agent
def run_travel_agent(user_input: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = travel_graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }

# response = run_travel_agent("Plan a 7 days Japan trip from Bangladesh")
# print(response)