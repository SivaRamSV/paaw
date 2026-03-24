# PAAW 🐾

**Personal AI Assistant that Works** - A privacy-first AI assistant with persistent memory.

```
 ██████╗  █████╗  █████╗ ██╗    ██╗
 ██╔══██╗██╔══██╗██╔══██╗██║    ██║
 ██████╔╝███████║███████║██║ █╗ ██║
 ██╔═══╝ ██╔══██║██╔══██║██║███╗██║
 ██║     ██║  ██║██║  ██║╚███╔███╔╝
 ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ 
```

🌐 **Website**: [paaw.online](https://paaw.online)

## Features

- 🧠 **Mental Model** - Remembers you, your work, your preferences
- 🔧 **Tool Integration** - Web search, Discord, and more via MCP
- ⏰ **Scheduled Jobs** - Background tasks that run on schedule
- 🔒 **Privacy First** - All data stays on your machine
- 💬 **Multi-Channel** - Web UI, CLI, Discord (coming: Telegram, Slack)

## Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- An LLM API key (Anthropic, OpenAI, or Groq)

### Setup

```bash
# Clone the repo
git clone https://github.com/SivaRamSV/paaw.git
cd paaw

# One-command start
./start.sh
```

The script will:
1. Check prerequisites
2. Create `.env` from template (add your API key when prompted)
3. Start all services (PostgreSQL, Valkey, SearXNG, PAAW)
4. Wait for everything to be ready

### Access

- **Web UI**: http://localhost:8080
- **Health Check**: http://localhost:8080/health
- **Search Engine**: http://localhost:8888 (SearXNG)

### Commands

```bash
./start.sh          # Start PAAW
./start.sh stop     # Stop all services
./start.sh restart  # Restart PAAW
./start.sh logs     # View logs
./start.sh status   # Check service status
```

## Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Start infrastructure (DB, cache, search)
docker compose up -d postgres valkey searxng

# Copy and configure environment
cp .env.example .env
# Edit .env and add your API key

# Run PAAW
python -m paaw.main

# Or use CLI
paaw chat
paaw status
paaw jobs list
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key | One of these |
| `OPENAI_API_KEY` | OpenAI API key | required |
| `GROQ_API_KEY` | Groq API key | |
| `LLM_DEFAULT_MODEL` | Model to use (default: `claude-sonnet-4-6`) | No |
| `DATABASE_URL` | PostgreSQL connection string | Auto in Docker |
| `DISCORD_TOKEN` | Discord bot token for notifications | No |

### Jobs

Jobs are defined in `jobs/*/job.md`. Example:

```markdown
# Morning News Briefing

## Uses Skill
web_researcher

## Goal
Find top tech and AI news of the day.

## Schedule
cron: 0 8 * * *
timezone: Asia/Kolkata

## How To Notify
Send to Discord channel ID: 1234567890
```

### Skills

Skills define reusable capabilities in `skills/*/skill.md`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         PAAW                                │
├─────────────────────────────────────────────────────────────┤
│  Web UI (8080)  │  CLI  │  Discord  │  Scheduler            │
├─────────────────────────────────────────────────────────────┤
│                    Agent (LLM + Tools)                      │
├─────────────────────────────────────────────────────────────┤
│  Mental Model (Graph)  │  Conversations  │  Jobs            │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL + AGE  │  Valkey  │  MCP Servers (SearXNG...)   │
└─────────────────────────────────────────────────────────────┘
```

## License

MIT
