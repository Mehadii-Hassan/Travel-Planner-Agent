# Travel Planner Agent

A modern AI-powered travel planning application that helps users create personalized trip itineraries using LangGraph, FastAPI, and large language models. The app combines flight suggestions, hotel ideas, and a polished travel plan into a single experience.

## Features

- AI-generated travel itineraries from a single natural-language prompt
- Flight suggestions using the AviationStack API
- Hotel and destination research using Tavily search
- FastAPI-based web frontend with a modern responsive UI
- Persistent travel planning state through LangGraph checkpoints
- Health check and REST API endpoint for integration

## Tech Stack

- Python 3.11
- FastAPI
- Jinja2 + HTML/CSS/JavaScript frontend
- LangGraph for multi-agent orchestration
- LangChain + Groq LLM
- Tavily search API
- AviationStack flight data API
- SQLite for checkpointing

## Project Structure

```text
Travel-Planner-Agent/
├── app.py                 # FastAPI application entrypoint
├── backend.py             # LangGraph travel planning workflow
├── requirements.txt       # Python dependencies
├── templates/             # HTML frontend templates
├── static/                # CSS and JavaScript files
├── tools/                 # Flight and hotel search tool modules
└── travel.db              # SQLite checkpoint database (created at runtime)
```

## Installation

Create and activate a Conda environment:

```bash
conda create -n travel python=3.11 -y
conda activate travel
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
DEFAULT_ORIGIN_IATA=DAC
```

### Notes

- `GROQ_API_KEY` is required for the LLM workflow.
- `TAVILY_API_KEY` is used for hotel and destination research.
- `AVIATIONSTACK_API_KEY` is used for flight data lookup.
- `DEFAULT_ORIGIN_IATA` is optional and defaults to `DAC` if not provided.

## Running the Application

Start the server:

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:8000/
```

## API Endpoints

- `GET /` — Home page
- `POST /api/travel` — Submit a travel request and receive an itinerary response
- `GET /health` — Health check endpoint

## Example Usage

You can ask for plans like:

- "Plan a 7-day trip to Japan from Bangladesh"
- "Create a 5-day family vacation to Bali with beach resorts"
- "Suggest a luxury honeymoon itinerary to Santorini"

## License

This project is open-source and available under the MIT license.
