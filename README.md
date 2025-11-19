# AI Debate Agent

An intelligent debate simulation system powered by AI, where the system generates two opposing stances on a topic, arguments for both sides, rebuttals, and renders a final verdict. Built with **Streamlit**, **LangChain**, and **LangGraph**.

## Overview

The AI Debate Agent is a sophisticated application that automates debate generation and adjudication. Given a topic, the system:

1. **Generates opposing stances** - Creates two contrasting viewpoints
2. **Develops opening arguments** - Each side presents their case (150-250 words)
3. **Generates rebuttals** - Each side responds to the opponent's arguments (80-150 words)
4. **Judges the debate** - A neutral AI judge evaluates both sides and declares a winner
5. **Produces a comprehensive report** - Markdown-formatted summary of the entire debate

## Features

- 🤖 **AI-Powered Debate Generation** - Uses LLM-driven agents to create realistic debates
- 💾 **Persistent Storage** - SQLite-based storage with LangGraph's checkpointing system
- 🧵 **Thread Management** - Maintain multiple concurrent debates with thread tracking
- 📊 **Visual Interface** - Interactive Streamlit UI with sidebar navigation
- ⚖️ **Neutral Judging** - Independent AI judge evaluates arguments objectively
- 📝 **Markdown Output** - Well-formatted debate summaries with structured sections

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── debate/
│   ├── __init__.py       # Package initialization
│   ├── graph.py          # LangGraph workflow definition
│   ├── nodes.py          # Debate generation nodes
│   ├── llm.py            # LLM configuration
│   ├── prompts.py        # System prompts for each debate role
│   ├── state.py          # Debate state schema
│   ├── models.py         # Pydantic data models
│   └── utils.py          # Utility functions
├── requirements.txt      # Python dependencies
└── memory.db            # SQLite database (generated at runtime)
```

## Architecture

### Core Components

#### **Debate Graph** (`debate/graph.py`)
- Implements a multi-stage workflow using LangGraph
- Nodes are executed sequentially and in parallel where applicable:
  - `stances` → `debater_a` + `debater_b` → `rebuttal_a` + `rebuttal_b` → `judge` → `assemble`
- Uses SQLiteSaver for checkpoint persistence

#### **Debate Nodes** (`debate/nodes.py`)
- **stance_generator**: Parses topic and creates two opposing stances
- **debater_a / debater_b**: Generate opening arguments from their perspectives
- **rebuttal_a / rebuttal_b**: Create focused rebuttals to opponent arguments
- **judge**: Evaluates both sides and declares a winner
- **assemble_output**: Formats results into markdown

#### **LLM Configuration** (`debate/llm.py`)
- Uses **Ollama** with **qwen2.5:1.5b** model
- Configured with temperature=0.4 for balanced creativity and consistency
- Streaming enabled for real-time response generation

#### **Prompts** (`debate/prompts.py`)
- Carefully crafted system prompts for each role
- Ensures strict adherence to stance assignment
- Prevents hallucination and maintains debate integrity

#### **State Management** (`debate/state.py`)
- TypedDict-based state schema tracking:
  - Topic and stances
  - Opening arguments
  - Rebuttals
  - Verdict and final markdown output
  - Debate round tracking

### User Interface (`app.py`)
- **Streamlit-based** web interface
- Sidebar with debate history and new debate button
- Real-time node execution progress display
- Chat-like interface for easy interaction
- Thread-based conversation management

## Installation

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running with qwen2.5:1.5b model

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-debate-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Ollama is running**
   ```bash
   # In a separate terminal
   ollama serve
   
   # Pull the model if not already available
   ollama pull qwen2.5:1.5b
   ```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Interface

1. **Start a New Debate**
   - Click "New Debate" in the sidebar
   - Enter your debate topic in the chat input box

2. **View Your Debate**
   - The system generates stances, arguments, rebuttals, and verdict
   - Progress updates show which node is executing
   - Final markdown summary displays in the chat

3. **Manage Debates**
   - Sidebar shows your debate history
   - Click any debate to view its results
   - Create new debates without losing previous ones

## Configuration

### Model Selection
Edit `debate/llm.py` to change the LLM model:
```python
MODEL_NAME = "qwen2.5:1.5b"  # Change this to another Ollama model
```

### Temperature & Streaming
Adjust creativity vs consistency in `debate/llm.py`:
```python
model = ChatOllama(model=MODEL_NAME, temperature=0.4, streaming=True)
```

### Database Location
The SQLite database is created at `memory.db` in the project root. Change this in `app.py` if needed:
```python
DEBATE_DB = "memory.db"
```

## Dependencies

- **Streamlit** - Web UI framework
- **LangChain Core** - LLM abstraction layer
- **LangChain Ollama** - Ollama integration
- **LangGraph** - Computational graph framework
- **Pydantic** - Data validation
- **SQLite3** - Database (built-in, via SqliteSaver)

See `requirements.txt` for pinned versions.

## How It Works

### Debate Workflow

```
1. User enters topic
   ↓
2. System generates two opposing stances
   ↓
3. Debater A writes opening argument (in parallel with B)
4. Debater B writes opening argument
   ↓
5. Debater A writes rebuttal (in parallel with B)
6. Debater B writes rebuttal
   ↓
7. Judge evaluates both sides
   ↓
8. Results assembled into markdown summary
   ↓
9. Display in Streamlit UI
```

### State Flow
- Each node updates the shared `DebateState`
- LangGraph handles node execution and state management
- SqliteSaver persists state to SQLite for recovery and history
- Streamlit sessions track thread IDs for multi-debate support

## Performance Considerations

- **Model Size**: qwen2.5:1.5b is lightweight and fast (~2-5 minutes per debate)
- **Parallelization**: Debater nodes and rebuttal nodes run in parallel
- **Temperature**: Set to 0.4 to balance creativity with consistency
- **Database**: SQLite is sufficient for moderate usage; consider PostgreSQL for production

## Troubleshooting

### "Failed to import backend" Error
- Ensure the `debate` package is importable
- Check that `__init__.py` exists in the `debate/` directory

### Ollama Connection Issues
- Verify Ollama is running: `ollama serve`
- Check model availability: `ollama list`
- Pull model if needed: `ollama pull qwen2.5:1.5b`

### Slow Response Times
- Ensure adequate system resources (CPU/RAM)
- Consider using a larger model if debates feel rushed
- Check Ollama process is not competing with other tasks

### Database Errors
- Delete `memory.db` to reset (will lose debate history)
- Ensure write permissions in project directory

## Future Enhancements

- [ ] Support for multiple LLM models
- [ ] Configurable debate parameters (rounds, word counts)
- [ ] Export debates to various formats (PDF, JSON)
- [ ] Multi-turn user interaction during debates
- [ ] Audience/scoring system
- [ ] Advanced analytics and debate statistics
- [ ] Web API backend (FastAPI)
- [ ] Docker containerization

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on the repository.

---

**Built with** 🤖 LLMs, 📊 LangGraph, and ⚡ Streamlit
