# PAAW Building Plan 🐾

> Step-by-step implementation guide for building PAAW from scratch.

---

## Overview

We'll build PAAW incrementally, with each step producing a **working, testable system**. No big bang — every milestone is usable.

```
Week 1-2: Core Foundation (You can chat with PAAW via CLI)
Week 3-4: Memory System (PAAW remembers things)
Week 5-6: Web UI + Channels (Chat from browser, Telegram)
Week 7-8: Tools + Polish (PAAW can take actions)
```

---

## Phase 1: Core Foundation 🏗️

**Goal:** A working agent you can chat with via CLI.

### Step 1.1: Project Setup
**Time:** 2-3 hours

```
paaw/
├── pyproject.toml          # Dependencies, project config
├── .env.example            # Environment template
├── .gitignore
├── docker-compose.yaml     # PostgreSQL + Valkey
├── Dockerfile
├── README.md
└── paaw/
    ├── __init__.py
    └── config.py           # Load env vars, settings
```

**Tasks:**
- [ ] Initialize Python project with `uv` or `poetry`
- [ ] Set up dependencies:
  ```
  litellm          # LLM gateway
  asyncio          # Async runtime
  asyncpg          # PostgreSQL driver
  valkey           # Cache/pubsub
  typer            # CLI framework
  rich             # Pretty terminal output
  pydantic         # Data validation
  python-dotenv    # Env vars
  ```
- [ ] Create docker-compose with PostgreSQL + AGE + pgvector + Valkey
- [ ] Create config.py to load settings
- [ ] Verify: `docker compose up` works, can connect to DB

**Deliverable:** Empty project that runs, connects to DB.

---

### Step 1.2: Basic Brain (LLM)
**Time:** 3-4 hours

```
paaw/
└── paaw/
    ├── brain/
    │   ├── __init__.py
    │   └── llm.py          # LiteLLM wrapper
    └── main.py             # Simple test
```

**Tasks:**
- [ ] Create `llm.py` with async LiteLLM wrapper
- [ ] Support model selection (GPT-4o-mini, Claude, Ollama)
- [ ] Handle streaming responses
- [ ] Add retry logic with exponential backoff
- [ ] Test: Can send message, get response

```python
# Goal: This should work
from paaw.brain import LLM

llm = LLM()
response = await llm.chat("Hello, who are you?")
print(response)  # "I'm an AI assistant..."
```

**Deliverable:** Can talk to any LLM via unified interface.

---

### Step 1.3: Event Loop + Agent Core
**Time:** 3-4 hours

```
paaw/
└── paaw/
    ├── agent.py            # PAAW agent class
    ├── models.py           # Core data models
    └── main.py             # Entry point with event loop
```

**Tasks:**
- [ ] Define core models (UnifiedMessage, Task, Response)
- [ ] Create Agent class that:
  - Receives messages
  - Calls LLM with system prompt
  - Returns responses
- [ ] Set up async event loop in main.py
- [ ] Add graceful shutdown handling

```python
# Goal: This should work
agent = Agent()
response = await agent.process(
    UnifiedMessage(content="What's 2+2?", channel="cli")
)
print(response)  # "2+2 equals 4"
```

**Deliverable:** Agent that processes messages through LLM.

---

### Step 1.4: CLI Channel
**Time:** 2-3 hours

```
paaw/
└── paaw/
    └── cli/
        ├── __init__.py
        └── main.py         # Typer CLI app
```

**Tasks:**
- [ ] Create Typer CLI app
- [ ] `paaw chat` - Interactive chat mode
- [ ] `paaw ask "question"` - One-shot question
- [ ] `paaw status` - Show status (placeholder for now)
- [ ] Pretty output with Rich
- [ ] Handle Ctrl+C gracefully

```bash
# Goal: This should work
$ paaw chat
🐾 PAAW is ready! Type your message (Ctrl+C to exit)

You: Hello!
PAAW: Hey! I'm PAAW, your personal assistant. How can I help?

You: What's the weather?
PAAW: I don't have access to weather data yet, but I'll learn soon!
```

**Deliverable:** Can chat with PAAW from terminal.

---

### Step 1.5: System Prompt + Personality
**Time:** 2 hours

```
paaw/
├── configs/
│   └── prompts/
│       └── system.md       # PAAW's personality
└── paaw/
    └── brain/
        └── prompts.py      # Load and format prompts
```

**Tasks:**
- [ ] Write PAAW's system prompt (personality, constraints)
- [ ] Create prompt loader
- [ ] Add user context placeholder (for later)
- [ ] Test different personalities

**Deliverable:** PAAW has a consistent personality.

---

### 🎯 Phase 1 Checkpoint

At this point you have:
- ✅ Working Docker environment
- ✅ LLM integration (any model)
- ✅ CLI chat interface
- ✅ Basic agent that responds

**Test it:**
```bash
docker compose up -d
paaw chat
# Have a conversation!
```

---

## Phase 2: Mental Model System 🧠

**Goal:** PAAW builds a mental model of YOU — understanding who you are, what matters to you, and how to help.

### Step 2.1: Apache AGE Graph Setup
**Time:** 3-4 hours

```
paaw/
├── scripts/
│   └── init-graph.sql      # AGE graph setup
└── paaw/
    └── mental_model/
        ├── __init__.py
        └── graph.py        # AGE connection & queries
```

**Tasks:**
- [ ] Update docker-compose to use `apache/age` image
- [ ] Initialize AGE graph extension
- [ ] Create graph named 'paaw'
- [ ] Test Cypher queries work via asyncpg
- [ ] Create helper functions for common graph ops

**Test:**
```python
# Goal: This should work
async with get_db() as db:
    result = await db.execute("""
        SELECT * FROM cypher('paaw', $$
            CREATE (u:User {name: 'test'})
            RETURN u
        $$) AS (u agtype)
    """)
```

**Deliverable:** Graph database ready for mental model.

---

### Step 2.2: Node & Edge Types
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── mental_model/
        ├── nodes.py        # Node type definitions
        └── edges.py        # Edge type definitions
```

**Tasks:**
- [ ] Define node types (Python dataclasses):
  - User (root, singleton)
  - Domain (work, health, finance, lifestyle, people)
  - Person (people in user's life)
  - Project (things being worked on)
  - Goal (measurable objectives)
  - Memory (conversation snippets)
- [ ] Define edge types:
  - HAS_DOMAIN, CHILD_OF, KNOWS, RELATES_TO
  - WORKS_ON, MENTIONED_IN, AFFECTS
- [ ] Each node has: id, type, label, context, key_facts, attributes
- [ ] Attributes are flexible (dict) — not rigid schema!

```python
@dataclass
class GraphNode:
    id: str
    type: str  # "user", "domain", "person", "project", "goal", "memory"
    label: str
    context: str = ""
    key_facts: list[str] = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
```

**Deliverable:** Node/edge types defined.

---

### Step 2.3: Mental Model Tool
**Time:** 5-6 hours

```
paaw/
└── paaw/
    └── mental_model/
        └── tool.py         # Mental model tool interface
```

**Tasks:**
- [ ] Implement Mental Model Tool operations:
  ```python
  # Reading
  get_user_context()           # For system prompt
  get_node(node_id)            # Get single node
  get_node_with_context(node_id)  # Node + ancestors + memories
  search_nodes(query)          # Find relevant nodes
  search_memories(query, scope_node_id?)
  
  # Writing  
  create_node(type, label, parent_id?, context?)
  update_node(node_id, context?, key_facts?, attributes?)
  create_edge(from_id, to_id, edge_type, context?)
  add_memory(content, belongs_to: list[node_id])
  ```
- [ ] All operations use Cypher queries through AGE
- [ ] Test: Can CRUD nodes and edges

**Deliverable:** LLM can interact with mental model.

---

### Step 2.4: Message → Node Routing
**Time:** 4-5 hours

```
paaw/
└── paaw/
    └── brain/
        └── search.py       # Keyword extraction & fuzzy search
```

**Tasks:**
- [ ] Keyword extraction (no LLM needed):
  - Remove stopwords
  - Extract capitalized words (names, places)
  - Match against known node labels
- [ ] Fuzzy node search using PostgreSQL:
  - ILIKE for substring matching
  - Full-text search with ts_vector
  - Search in label, context, key_facts
  - Return ranked results
- [ ] Fast (<10ms) — no LLM call!

```python
# Goal: This should work
async def search_nodes(keywords: list[str]) -> list[Node]:
    """Fuzzy search for nodes matching keywords."""
    patterns = [f"%{kw}%" for kw in keywords]
    
    return await db.fetch("""
        SELECT *, 
            CASE WHEN label ILIKE ANY($1) THEN 10 ELSE 0 END +
            CASE WHEN context ILIKE ANY($1) THEN 5 ELSE 0 END as score
        FROM nodes
        WHERE label ILIKE ANY($1) OR context ILIKE ANY($1)
        ORDER BY score DESC
        LIMIT 5
    """, patterns)

# Examples:
# search(["raj"]) → person_raj, domain_work (mentions raj)
# search(["wife"]) → person_priya (context: "Siva's wife")
# search(["running"]) → goal_running
```

**Deliverable:** Fast fuzzy node search without LLM.

---

### Step 2.5: Context Assembly + Node Tagging
**Time:** 4-5 hours

```
paaw/
└── paaw/
    └── mental_model/
        └── context.py      # Context loading & prompt building
```

**Tasks:**
- [ ] Always include root nodes summary in prompt (~500 tokens)
- [ ] Add matched node details from keyword search
- [ ] Add instruction for LLM to tag relevant nodes
- [ ] Parse `<nodes>` from LLM response
- [ ] Load tagged nodes for NEXT conversation turn

```python
# System prompt structure
SYSTEM_PROMPT = """
You are PAAW, {user.name}'s personal assistant.

USER: {identity + personality + patterns}

MENTAL MODEL:
├── 👥 People: {people_summary}
├── 💼 Work: {work_summary}
├── 🏃 Health: {health_summary}
└── 📋 Tasks: {pending_count} pending

{matched_node_details if any}

At end of response, output: <nodes>relevant,node,ids</nodes>
"""

# Goal: This flow should work
# 1. User: "Raj is being difficult"
# 2. Keyword search finds: person_raj, domain_work
# 3. Prompt includes raj's context + memories
# 4. LLM responds + outputs: <nodes>person_raj,work,goal_indie</nodes>
# 5. goal_indie loaded for NEXT turn (LLM made connection!)
```

**Deliverable:** Efficient context assembly with node tagging.

---

### Step 2.6: Integrate with Agent
**Time:** 4-5 hours

**Tasks:**
- [ ] Update Agent flow:
  1. Extract keywords from message (fast, no LLM)
  2. Search nodes by keywords (fast, <10ms)
  3. Build prompt with root nodes + matched nodes
  4. Call LLM (single call!)
  5. Parse `<nodes>` tags from response
  6. Async: Extract memories, update access counts
  7. Load tagged nodes for next turn
- [ ] Memory extraction (same LLM call or async after)
- [ ] One LLM call per message!

**Deliverable:** Agent uses mental model efficiently.

---

### Step 2.7: Onboarding ("Tell Me About Yourself")
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── onboarding/
        ├── __init__.py
        ├── flow.py         # Onboarding flow
        └── extractor.py    # Extract graph from freeform text
```

**Tasks:**
- [ ] Detect new user (no User node)
- [ ] Single prompt: "Tell me about yourself"
- [ ] LLM extracts structured data from freeform response:
  ```python
  # User says: "I'm Siva, dev in Chennai, building PAAW..."
  # LLM extracts:
  {
    "user": {"name": "Siva", "location": "Chennai"},
    "people": [{"label": "Priya", "relationship": "wife"}],
    "projects": [{"label": "PAAW", "status": "active"}],
    "observations": ["Night owl", "Should exercise more"]
  }
  ```
- [ ] Build initial graph from extracted data
- [ ] Show user what PAAW understood
- [ ] Let user correct if needed

**Deliverable:** New users get proper onboarding.

---

### Step 2.8: Task Nodes & Execution
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── mental_model/
        └── tasks.py        # Task operations
```

**Tasks:**
- [ ] Task node type (status, priority, due_date, result)
- [ ] Create tasks from conversations
- [ ] List pending tasks
- [ ] Mark tasks complete (result becomes memory)
- [ ] Link tasks to related nodes (BELONGS_TO)

```python
# Goal: This should work
async def create_task(label, belongs_to, due_date=None):
    # Creates Task node linked to relevant nodes
    pass

async def complete_task(task_id, result):
    # Marks complete AND creates Memory from result
    pass
```

**Deliverable:** PAAW can track and execute tasks.

---

### Step 2.9: Mental Model Updates & Corrections
**Time:** 2-3 hours

```
paaw/
└── paaw/
    └── mental_model/
        ├── updates.py      # Handle updates from LLM
        └── history.py      # Audit trail
```

**Key Principle: The mental model must be ADAPTABLE.** Facts change.

**Update Types:**
- Correction: "Actually, that's wrong..."
- Factual update: "We moved to Bangalore"
- Status change: "PAAW is done! I shipped it"
- Relationship change: "We got divorced"

**Tasks:**
- [ ] Parse `<update>` blocks from LLM response:
  ```python
  # LLM outputs:
  # <update>
  #   node_id: domain_work
  #   field: context
  #   old_value: "Works at TechCorp"
  #   new_value: "Left TechCorp, now indie"
  #   reason: status_change
  # </update>
  ```
- [ ] Apply updates to graph nodes
- [ ] Create `updates` table for audit trail:
  ```sql
  CREATE TABLE updates (
    id UUID PRIMARY KEY,
    node_id TEXT,
    field TEXT,
    old_value JSONB,
    new_value JSONB,
    reason TEXT,  -- correction, new_info, status_change
    source TEXT,  -- conversation, manual
    created_at TIMESTAMP
  );
  ```
- [ ] Handle explicit corrections: "PAAW, that's wrong"
- [ ] Add to system prompt: instruct LLM to output `<update>` blocks

**Deliverable:** PAAW can update its understanding when facts change.

---

### Step 2.10: Maintenance (No Decay!)
**Time:** 2-3 hours

```
paaw/
└── paaw/
    └── mental_model/
        └── maintenance.py  # Background maintenance
```

**Key Principle: NO DECAY, NO DELETION.** Memories are permanent.

**Tasks:**
- [ ] Node context consolidation:
  - Periodically ask LLM to update context from recent memories
  - Summarize patterns into node context
- [ ] Track memory access for relevance scoring:
  - Update last_accessed and access_count on retrieval
- [ ] Check for upcoming tasks/events (proactive)
- [ ] Run via scheduler (daily)

**Deliverable:** Mental model self-maintains WITHOUT deleting anything.

---

### 🎯 Phase 2 Checkpoint

At this point you have:
- ✅ Apache AGE graph database
- ✅ Unified node model (everything is a node)
- ✅ Mental model tool (CRUD for all node types)
- ✅ Keyword search + fuzzy matching (fast routing)
- ✅ Context assembly from graph
- ✅ Agent that learns from every conversation
- ✅ Conversational onboarding ("Tell me about yourself")
- ✅ Task creation & execution
- ✅ **Adaptable mental model (updates & corrections)**
- ✅ Smart retrieval (relevance-based, no decay)
- ✅ Task creation & execution
- ✅ Smart retrieval (relevance-based, no decay)

**Test it:**
```bash
paaw chat
# Go through onboarding
# Have conversations about different topics
# "Book a hotel in Ooty for my anniversary" — creates task
# "What do you know about me?" — shows mental model
# Exit and come back — it remembers EVERYTHING!
# "Show me my mental model" — visualizes graph (ASCII for now)
```

---

## Phase 3: Web UI + Channels 🌐

**Goal:** Chat from browser, add Telegram support.

### Step 3.1: FastAPI Server
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── api/
        ├── __init__.py
        ├── server.py       # FastAPI app
        └── routes/
            ├── __init__.py
            ├── chat.py     # WebSocket chat
            └── health.py   # Health endpoint
```

**Tasks:**
- [ ] Set up FastAPI with async
- [ ] WebSocket endpoint for chat
- [ ] Health check endpoint
- [ ] CORS for local development
- [ ] Integrate with Agent
- [ ] Test: Can chat via WebSocket

**Deliverable:** API server running.

---

### Step 3.2: Basic Web UI
**Time:** 4-5 hours

```
paaw/
└── ui/
    ├── package.json
    ├── index.html
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   │   └── Chat/
    │   │       ├── ChatWindow.tsx
    │   │       ├── Message.tsx
    │   │       └── Input.tsx
    │   └── hooks/
    │       └── useWebSocket.ts
    └── vite.config.ts
```

**Tasks:**
- [ ] Set up React + Vite + TailwindCSS
- [ ] Create chat UI components
- [ ] WebSocket connection to API
- [ ] Message history display
- [ ] Input with send button
- [ ] Typing indicator
- [ ] Build and serve from FastAPI

**Deliverable:** Can chat via web browser at localhost:8080.

---

### Step 3.3: Channel Gateway
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── channels/
        ├── __init__.py
        ├── gateway.py      # Unified message handler
        ├── base.py         # Base channel class
        ├── web.py          # Web channel (WebSocket)
        └── cli.py          # CLI channel (refactor)
```

**Tasks:**
- [ ] Create Channel base class
- [ ] Implement Gateway that:
  - Receives from any channel
  - Normalizes to UnifiedMessage
  - Routes to Agent
  - Returns response to correct channel
- [ ] Refactor CLI to use Gateway
- [ ] Refactor Web to use Gateway
- [ ] Test: Same agent, multiple channels

**Deliverable:** Unified channel system.

---

### Step 3.4: Telegram Integration
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── channels/
        └── telegram.py     # Telegram bot
```

**Tasks:**
- [ ] Create Telegram channel using `python-telegram-bot`
- [ ] Long polling (no webhooks needed)
- [ ] Handle text messages
- [ ] Handle basic commands (/start, /help, /status)
- [ ] Connect to Gateway
- [ ] Test: Chat via Telegram

**Deliverable:** Can chat with PAAW on Telegram.

---

### Step 3.5: Graph Visualization
**Time:** 4-5 hours

```
paaw/
└── ui/
    └── src/
        └── components/
            └── Graph/
                ├── GraphView.tsx    # React Flow graph
                └── NodePanel.tsx    # Details panel
```

**Tasks:**
- [ ] Add API endpoint to fetch goal graph
- [ ] Create React Flow visualization
- [ ] Show goals as nodes, relationships as edges
- [ ] Click node to see details
- [ ] Zoom and pan
- [ ] Filter by status

**Deliverable:** Visual graph of goals and memories.

---

### 🎯 Phase 3 Checkpoint

At this point you have:
- ✅ Web UI for chat
- ✅ Telegram integration
- ✅ Unified channel gateway
- ✅ Graph visualization

**Test it:**
```bash
docker compose up -d
open http://localhost:8080
# Chat in browser
# Chat on Telegram
# Same memory, same agent!
```

---

## Phase 4: Tools + System Services 🔧

**Goal:** PAAW can take actions, runs autonomously.

### Step 4.1: Tool System (MCP)
**Time:** 4-5 hours

```
paaw/
└── paaw/
    └── tools/
        ├── __init__.py
        ├── manager.py      # Tool registry
        ├── mcp.py          # MCP client
        └── builtins/
            ├── __init__.py
            └── web_search.py
```

**Tasks:**
- [ ] Create Tool Manager to register tools
- [ ] Define tool interface (name, description, parameters, execute)
- [ ] Implement MCP client for external tools
- [ ] Create built-in web search tool (DuckDuckGo)
- [ ] Integrate tools with Agent (function calling)
- [ ] Test: Agent can search the web

**Deliverable:** PAAW can use tools.

---

### Step 4.2: Self-Healing Executor
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── brain/
        └── executor.py     # Self-healing execution
```

**Tasks:**
- [ ] Create Executor that:
  - Runs tasks with timeout
  - Catches errors
  - Asks LLM to fix and retry
  - Gives up after N attempts
  - Notifies user on failure
- [ ] Add to Agent pipeline
- [ ] Test: Handles failures gracefully

**Deliverable:** Robust task execution.

---

### Step 4.3: Heartbeat + Health
**Time:** 2-3 hours

```
paaw/
└── paaw/
    └── system/
        ├── __init__.py
        └── heartbeat.py    # Health monitoring
```

**Tasks:**
- [ ] Create Heartbeat service:
  - Check DB connection
  - Check Valkey connection
  - Check LLM availability
  - Check memory stats
- [ ] Run every 30 seconds
- [ ] Log health status
- [ ] API endpoint for status
- [ ] Test: Detects unhealthy state

**Deliverable:** Health monitoring active.

---

### Step 4.4: Scheduler
**Time:** 3-4 hours

```
paaw/
└── paaw/
    └── system/
        └── scheduler.py    # Cron-like tasks
```

**Tasks:**
- [ ] Create Scheduler with cron-like syntax
- [ ] Built-in tasks:
  - Memory decay (hourly)
  - Memory consolidation (daily)
  - Reminder checks (every minute)
- [ ] User-scheduled tasks (reminders)
- [ ] Test: Tasks run on schedule

**Deliverable:** Scheduled tasks working.

---

### Step 4.5: Audit Logging
**Time:** 2-3 hours

```
paaw/
└── paaw/
    └── system/
        └── audit.py        # Action logging
```

**Tasks:**
- [ ] Log every action to DB:
  - Timestamp, type, input, output
  - Tool used, model used
  - Goal, channel, user
  - Status, duration
- [ ] Also write to append-only file
- [ ] API endpoint to view logs
- [ ] Test: All actions logged

**Deliverable:** Full audit trail.

---

### 🎯 Phase 4 Checkpoint

At this point you have:
- ✅ Tool system with MCP support
- ✅ Self-healing executor
- ✅ Heartbeat monitoring
- ✅ Scheduled tasks
- ✅ Audit logging

**Test it:**
```bash
paaw chat
You: Search the web for latest Rust news
PAAW: [Uses web search tool, returns results]

paaw status
# Shows health, uptime, stats
```

---

## Phase 5: Polish + More Channels 🎨

**Goal:** Production-ready, more integrations.

### Step 5.1: Slack Integration
**Time:** 3-4 hours

- [ ] Socket Mode (outbound WebSocket)
- [ ] Handle mentions and DMs
- [ ] Thread support

### Step 5.2: Discord Integration
**Time:** 3-4 hours

- [ ] Discord.py bot
- [ ] Handle mentions and DMs
- [ ] Server support

### Step 5.3: WhatsApp Bridge
**Time:** 4-5 hours

- [ ] whatsapp-web.js bridge (Node.js subprocess)
- [ ] QR code authentication
- [ ] Handle messages

### Step 5.4: Settings UI
**Time:** 3-4 hours

- [ ] LLM configuration
- [ ] Channel configuration
- [ ] Preferences UI

### Step 5.5: Memory Maintenance UI
**Time:** 3-4 hours

- [ ] View all memories
- [ ] Edit/delete memories
- [ ] View audit log

---

## Development Guidelines

### Testing Strategy

```
Unit Tests:       Each module has tests
Integration:      Test channels + agent + memory
End-to-End:       Full conversation flows
```

### Code Style

- Python 3.12+, async everywhere
- Type hints on everything
- Pydantic for data validation
- Black + Ruff for formatting/linting

### Commit Convention

```
feat: Add memory tool interface
fix: Handle empty context gracefully
docs: Update building plan
refactor: Split agent into modules
test: Add memory search tests
```

### Branch Strategy

```
main        ← stable, deployable
develop     ← integration branch
feat/xxx    ← feature branches
```

---

## Quick Reference: What to Build First

If you want to get something working FAST, here's the minimal path:

```
1. Project setup (30 min)
2. LLM wrapper (1 hour)
3. Agent + CLI (2 hours)
4. System prompt (30 min)

→ You can now chat with PAAW!

5. Database schema (2 hours)
6. Memory store (2 hours)
7. Integrate memory (2 hours)

→ PAAW now remembers!

8. FastAPI server (1 hour)
9. Basic web UI (3 hours)

→ Chat in browser!
```

**Total to MVP: ~15-20 hours of focused work**

---

## Let's Go! 🚀

Ready to start? Let's begin with **Step 1.1: Project Setup**.

```bash
mkdir paaw && cd paaw
# Let's build something awesome! 🐾
```
