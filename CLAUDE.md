# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Alice is a ReAct-based intelligent agent framework combining a **Rust TUI** (Terminal User Interface), **Python logic engine**, and **Docker sandbox** for secure task execution. The architecture implements a three-tier isolation pattern: presentation (Rust), control (Python), and execution (containerized sandbox).

## Development Commands

### Python Environment Setup

The host machine requires minimal Python dependencies:
```bash
# Install host-side dependencies (agent.py, tui_bridge.py, config.py)
pip install openai python-dotenv

# Container dependencies (requirements.txt) are auto-installed during Docker build
```

### Building and Running

```bash
# Build and run the application (release mode recommended)
cargo run --release

# Build only (debug mode)
cargo build

# Build release binary
cargo build --release
```

**Note**: The project uses Rust edition 2024 (released February 2025 with Rust 1.85). Ensure your Rust toolchain is up to date (`rustup update`).

### Docker Management

```bash
# Build the sandbox image manually (auto-built on first run)
docker build -t alice-sandbox:latest -f Dockerfile.sandbox .

# Check container status
docker ps -a --filter name=alice-sandbox-instance

# Stop/remove container if needed
docker stop alice-sandbox-instance
docker rm alice-sandbox-instance

# Rebuild container from scratch
docker rmi alice-sandbox:latest
```

### Testing Skills

```bash
# List available skills
# In the TUI, send: toolkit list

# Refresh skill registry (discovers new skills)
# In the TUI, send: toolkit refresh
```

## Architecture

### Three-Layer Design

1. **TUI Layer (Rust)**: `src/main.rs`
   - Built with Ratatui for terminal rendering
   - Handles user input, message display, thinking process visualization
   - Communicates with Python bridge via stdin/stdout JSON protocol
   - Real-time streaming display with auto-scroll
   - Mouse support: scroll wheel navigation in chat and sidebar areas
   - Keyboard shortcuts:
     - **Enter**: Send message
     - **Esc**: Interrupt current operation (sets `interrupted` flag in agent state)
     - **Ctrl+O**: Toggle thinking sidebar visibility
     - **Ctrl+C**: Quit application
     - **Up/Down**: Manual scroll (disables auto-scroll)

2. **Logic Engine (Python)**: `agent.py` + `tui_bridge.py`
   - `agent.py`: Core state machine, memory management, built-in command interception
   - `tui_bridge.py`: Bridges TUI ↔ Agent, manages streaming, parses thinking vs content
   - `snapshot_manager.py`: Auto-discovers skills, generates context snapshots
   - Implements multi-tier memory system (Working Memory, STM, LTM)

3. **Sandbox (Docker)**: `Dockerfile.sandbox`
   - Ubuntu 24.04 with Python venv, Node.js, Playwright
   - Persistent container (`alice-sandbox-instance`) with volume mounts
   - Only mounts `skills/` and `alice_output/` (isolates prompts, memory, source code)
   - All task execution happens inside this container

### Communication Protocol

**Rust ↔ Python**: JSON messages over stdin/stdout
- `{"type": "status", "content": "..."}` - Agent state updates (displayed in status line)
- `{"type": "thinking", "content": "..."}` - Thinking content (routed to sidebar)
- `{"type": "content", "content": "..."}` - Response content (routed to main chat)
- `{"type": "tokens", "total": N, "prompt": M, "completion": K}` - Token usage (displayed in TUI footer)
- `{"type": "error", "content": "..."}` - Error messages

**Python → Agent**: Text streaming with special markers
- Thinking sections: `<thought>...</thought>`, `<reasoning>...</reasoning>`, `<thinking>...</thinking>`, or triple backticks
- Content sections: Normal text outside thinking markers
- Built-in commands: Intercepted before LLM call (see Built-in Commands section)

**Interrupt Mechanism**: When user presses Esc, the TUI sends a thread-safe signal to stop streaming. The agent checks `self.interrupted` flag during tool execution and LLM streaming to gracefully halt operations.

### Memory System

Four-tier memory hierarchy managed by `agent.py`:

1. **Working Memory** (`memory/working_memory.md`): Last 30 rounds of conversation (configurable via `WORKING_MEMORY_MAX_ROUNDS`)
2. **Short-Term Memory (STM)** (`memory/short_term_memory.md`): Recent facts, discoveries, progress notes
3. **Long-Term Memory (LTM)** (`memory/alice_memory.md`): Persistent lessons, user preferences, critical insights
4. **Todo List** (`memory/todo.md`): Active task tracking

Memory is automatically injected into context at each turn. The system auto-prunes Working Memory when it exceeds the round limit.

### Skill System

Skills are auto-discovered from `skills/` directory:
- Each skill is a folder containing `SKILL.md` (YAML frontmatter + Markdown)
- Required YAML fields: `name`, `description`
- Optional: `license`, `allowed-tools`, `metadata`
- `SnapshotManager` scans skills on startup and provides summaries to reduce context

**Important**: Always read `SKILL.md` before invoking a skill, as different LLM models may use tools differently.

## Built-in Commands

These commands are intercepted by `agent.py` and executed on the host (not in the sandbox):

```bash
# Memory management
memory "content to remember"           # Add to STM
memory "critical lesson" --ltm         # Add to LTM

# Task tracking
todo "task description or update"      # Update todo.md

# Prompt modification
update_prompt "new system prompt"      # Update prompts/alice.md

# Skill registry
toolkit list                           # List available skills
toolkit refresh                        # Scan skills/ for new skills
```

## Configuration

Environment variables (`.env` file):
- `API_KEY`: Required - OpenAI-compatible API key
- `API_BASE_URL`: Default: `https://api-inference.modelscope.cn/v1/`
- `MODEL_NAME`: Required - Model identifier (e.g., `qwen-plus`, `gpt-4o`)
- `WORKING_MEMORY_MAX_ROUNDS`: Default: 30 - Conversation rounds to retain before auto-pruning

Paths (`config.py`):
- `DEFAULT_PROMPT_PATH`: `prompts/alice.md`
- `MEMORY_FILE_PATH`: `memory/alice_memory.md`
- `TODO_FILE_PATH`: `memory/todo.md`
- `SHORT_TERM_MEMORY_FILE_PATH`: `memory/short_term_memory.md`
- `WORKING_MEMORY_FILE_PATH`: `memory/working_memory.md`
- `ALICE_OUTPUT_DIR`: `alice_output/`

**Important**: All `.env` values are loaded via `python-dotenv`. Missing required variables will cause startup to fail with clear error messages.

## Key Implementation Details

### Data Flow Architecture

**User Input Flow**:
1. Rust TUI captures keystrokes → builds input string
2. On Enter: writes message to Python subprocess stdin
3. `tui_bridge.py` reads stdin → passes to `agent.py`
4. Agent processes (checks built-in commands → LLM API call → tool execution in Docker)
5. Response streams back through `StreamManager` → JSON messages to stdout
6. Rust TUI reads stdout → parses JSON → updates UI state → renders

**Tool Execution Flow**:
1. Agent receives tool call from LLM (e.g., Python script execution)
2. Writes script to temporary file inside Docker container via `docker exec`
3. Executes via `docker exec alice-sandbox-instance python /tmp/script.py`
4. Captures stdout/stderr, returns to LLM for processing
5. Skills directory (`skills/`) is mounted read-only in container for skill script access

### Stream Processing (`tui_bridge.py`)

The `StreamManager` class handles incremental text streaming with buffer-based lookahead to correctly classify content vs thinking sections. Key features:
- **Buffer Management**: Maintains a 10MB buffer with overflow protection to prevent OOM
- **Smart Prefix Retention**: Holds back partial tag matches at buffer boundaries to avoid mis-splitting
- **Multi-Tag Support**: Recognizes triple backticks and XML-style tags (`<thought>`, `<reasoning>`, `<thinking>`)
- **State Persistence**: Maintains `in_code_block` state across chunk boundaries for accurate parsing

### Container Management (`agent.py`)

The `_ensure_docker_environment()` method:
1. Validates Docker installation
2. Auto-builds sandbox image if missing
3. Starts persistent container with minimal volume mounts
4. Container runs indefinitely (`sleep infinity`) and executes commands via `docker exec`

### Thinking Display Logic

The TUI renders thinking content in a sidebar (toggled with Ctrl+O). Thinking sections are extracted by looking for:
- Triple backticks (```)
- `<thought>...</thought>`
- `<reasoning>...</reasoning>`
- `<thinking>...</thinking>`

Content sections appear in the main chat area.

### Memory Pruning Strategy

When Working Memory exceeds `WORKING_MEMORY_MAX_ROUNDS`:
1. Extract the oldest 50% of rounds
2. Send to LLM with summarization prompt
3. Append summary to STM
4. Delete processed rounds from Working Memory
5. Log operation to `alice_runtime.log`

## Special Workflow Notes

- **Alice Personality**: The system prompt (`prompts/alice.md`) defines a self-improving agent persona that actively uses memory commands and self-reflection
- **Persona Update**: Alice can modify her own system prompt via `update_prompt` command
- **Skill Development**: Follow `agent-skills-spec_cn.md` for skill creation guidelines
- **Docker Isolation**: Source code, prompts, and memory files are NOT mounted in the container - only skills and output directory

## Common Development Tasks

### Adding a New Skill

1. Create folder in `skills/my-new-skill/`
2. Add `SKILL.md` with proper YAML frontmatter
3. Include scripts/resources as needed
4. Run `toolkit refresh` in TUI to register

### Modifying System Prompt

Either:
- Edit `prompts/alice.md` directly, OR
- Use `update_prompt "content"` command in TUI

### Debugging Stream Processing

Check `alice_runtime.log` for detailed logs from both `AliceAgent` and `TuiBridge` loggers.

### Container Dependencies

If sandbox needs new Python packages:
1. Add to `requirements.txt`
2. Rebuild container: `docker rmi alice-sandbox:latest && cargo run --release`

Container will auto-rebuild with new dependencies on next startup.

### Python Bridge Development

The `tui_bridge.py` module runs as a subprocess spawned by the Rust TUI:
- Handles stdin (user messages) → agent processing → stdout (JSON responses)
- Run manually for debugging: `python tui_bridge.py` (reads from stdin, outputs JSON)
- Check `alice_runtime.log` for Python-side logs from both `AliceAgent` and `TuiBridge` loggers
