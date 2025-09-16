```
# Multi-Agent Business System

A web-based application that leverages multiple AI agents to process business-related queries, powered by FastAPI and Ollama's `mistral` model. This system enables interactive analysis, visualization, and reporting of mock business data.

## Overview
This project implements a multi-agent framework where agents collaborate to handle user queries. It includes a Planner to break down tasks, a Data Collector to generate data, an Analyzer for insights, a Visualizer for charts, and a Report Generator for summaries, all served through a browser interface.

## Features
- **Planner Agent**: Decomposes queries into subtasks.
- **Data Collector Agent**: Mocks or generates relevant data.
- **Analyzer Agent**: Derives insights from data.
- **Visualizer Agent**: Generates simple charts (when applicable).
- **Report Generator Agent**: Produces final aggregated reports.

## Prerequisites
- **Python 3.8+**
- **Ollama** (for AI model hosting)
- **Windows, macOS, or Linux**

## Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>  # Replace with your repository URL if applicable
cd multiagent
```

### 2. Set Up a Virtual Environment
```bash
python -m venv multiagent_venv
multiagent_venv\Scripts\activate  # On Windows
# Or: source multiagent_venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
Install the required Python packages using the provided requirements file:
```bash
pip install -r requirements.txt
```

### 4. Install and Configure Ollama
- Download and install Ollama from [ollama.com](https://ollama.com/).
- Pull the `mistral` model:
  ```bash
  ollama pull mistral
  ```
- Start the Ollama server:
  ```bash
  ollama serve
  ```

## Usage
1. Start the application:
   ```bash
   python main.py
   ```
2. Open your browser and navigate to `http://127.0.0.1:8000/`.
3. Enter a query (e.g., "Summarize sales trends for Q1") in the textarea and click "Process Request".
4. Monitor the agent progress and view the final result on the page.

## Example Queries
- `Say hello` - Tests basic connectivity. *Expected: A greeting like "Hello!"*
- `Summarize the sales data for January` - Generates a simple sales summary. *Expected: e.g., "January sales: $10,000"*
- `Analyze customer feedback: 'Great product, poor support'` - Performs sentiment analysis. *Expected: e.g., "Positive on product, negative on support"*
- `Show a pie chart of sales by region: North $5000, South $3000, East $2000` - Creates a pie chart. *Expected: A chart with 50% North, 30% South, 20% East*
- `Generate a detailed report on quarterly revenue trends and customer satisfaction for Q1` - Produces a comprehensive report. *Expected: e.g., "Q1 Revenue: $30,000, 80% satisfaction"*

## Troubleshooting
- **Connection Errors**: Ensure Ollama is running on `127.0.0.1:11434`. Test with `curl -X POST http://localhost:11434/api/generate -d '{"model": "mistral", "prompt": "Hello"}'`. Check for port conflicts with `netstat -aon | findstr :11434` and kill with `taskkill /PID <PID> /F` if needed.
- **500 Errors**: Increase available memory (close other apps, aim for >6 GiB) or adjust the timeout in `main.py` (line 40) to 120 seconds.
- **Loading Delays**: Model loading (e.g., `mistral`) may take 2-5 minutes on CPU. Wait for `Server listening on 127.0.0.1:60018` in Ollama logs.
- **Agent Failures**: Retry failed agents via UI buttons. Ensure `mistral` is pulled with `ollama pull mistral`.

## Contributing
Fork this repository, make improvements, and submit pull requests. Report issues on the GitHub page if applicable.


## Acknowledgments
- Built with FastAPI, Uvicorn, HTTPX, Jinja2, and Ollama.
- Inspired by xAI's multi-agent system concepts.
```

