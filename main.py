import asyncio
import json
from typing import Dict
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import uvicorn

app = FastAPI()

# Allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral"

# Agents
AGENTS: Dict[str, str] = {
    "planner": "You are a planning agent. Break the user's request into subtasks.",
    "data-collector": "You are a data collection agent. Mock or describe needed data.",
    "analyzer": "You are an analysis agent. Analyze the data and find insights.",
    "visualizer": "You are a visualization agent. Suggest chart types and produce JSON chartData if possible.",
    "reporter": "You are a report agent. Summarize everything clearly."
}

AGENT_MODEL_MAP = {agent: DEFAULT_MODEL for agent in AGENTS.keys()}

# Jinja2 template setup
templates = Jinja2Templates(directory="templates")


#  Serve Frontend 
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


#  Call Ollama 
async def call_ollama(prompt: str, model: str = DEFAULT_MODEL, timeout: float = 60.0) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
    data = resp.json()
    return data.get("response", "") if isinstance(data, dict) else str(data)


#  SSE Event Formatter
def sse_event(event: str, data_obj) -> str:
    return f"event: {event}\ndata: {json.dumps(data_obj)}\n\n"


#  Streaming Endpoint 
@app.get("/process_sse")
async def process_sse(query: str = Query(..., min_length=1)):
    async def stream_events():
        yield sse_event("system", {"status": "started", "query": query})
        agent_outputs: Dict[str, str] = {}

        for agent_id, role_prompt in AGENTS.items():
            yield sse_event("agent_start", {"id": agent_id})
            prompt = f"{role_prompt}\n\nUser request: {query}\n\nRespond concisely."

            last_exc = None
            attempts = 0
            while attempts < 3:
                attempts += 1
                yield sse_event("agent_progress", {"id": agent_id, "progress": 10, "attempt": attempts})
                try:
                    model = AGENT_MODEL_MAP.get(agent_id, DEFAULT_MODEL)
                    result_text = await call_ollama(prompt, model=model)
                    agent_outputs[agent_id] = result_text
                    yield sse_event("agent_progress", {"id": agent_id, "progress": 80})
                    yield sse_event("agent_completed", {"id": agent_id, "result": result_text})
                    break
                except Exception as e:
                    last_exc = str(e)
                    yield sse_event("agent_error", {"id": agent_id, "error": last_exc, "attempt": attempts})
                    await asyncio.sleep(0.5)
            else:
                yield sse_event("agent_status_final", {"id": agent_id, "status": "failed", "error": last_exc})

        # Final aggregation
        try:
            aggregator_prompt = (
                "You are an aggregator agent. Combine the following agent outputs:\n\n"
                f"User request: {query}\n\nOutputs:\n{json.dumps(agent_outputs, indent=2)}\n\n"
                "Produce JSON with: title, executive_summary, findings, recommendations, chartData (optional)."
            )
            agg_result = await call_ollama(aggregator_prompt)
            yield sse_event("complete", {"status": "done", "aggregate": agg_result})
        except Exception as e:
            yield sse_event("complete", {"status": "done_with_errors", "error": str(e)})

    return StreamingResponse(stream_events(), media_type="text/event-stream")


#  Non-Streaming Endpoint 
@app.post("/query")
async def query_endpoint(payload: Dict):
    q = payload.get("query")
    if not q:
        return JSONResponse(status_code=400, content={"error": "query required"})

    results = {}
    for agent_id, role_prompt in AGENTS.items():
        try:
            prompt = f"{role_prompt}\n\nUser request: {q}"
            res = await call_ollama(prompt, model=AGENT_MODEL_MAP.get(agent_id, DEFAULT_MODEL))
            results[agent_id] = res
        except Exception as e:
            results[agent_id] = f"ERROR: {str(e)}"

    try:
        aggregate_prompt = (
            f"You are an aggregator. Combine these agent outputs into a short report.\n\nUser request: {q}\n\n"
            f"Outputs: {json.dumps(results)}"
        )
        agg = await call_ollama(aggregate_prompt)
    except Exception as e:
        agg = f"AGGREGATION_ERROR: {str(e)}"

    return {"query": q, "agents": results, "aggregate": agg}


#  Entry Point 
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
