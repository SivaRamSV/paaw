# PAAW V3 - Scalable Mental Model Design

> **Date**: March 22, 2026  
> **Status**: Fresh Start  
> **Philosophy**: Scalable. Works in majority of cases.

---

## Core Insight

LLM is NOT a human with memory. Every call is a fresh prompt.  
Memory = What we put in the prompt.  
The mental model exists to **build the right context** for each prompt.

**Scalability Principle**: Design for 1000s of conversations, not just 10.

---

## Mental Model Structure

**It's a GRAPH - many-to-many relationships everywhere!**

```
USER (root)
├── name, location, timezone, preferences
│
├── PAAW (assistant)
│   ├── Skills/
│   │   ├── web_researcher
│   │   └── birthday_reminder
│   └── MCP Tools/
│       ├── search
│       └── fetch_content
│
├── CONVERSATIONS/ ─────────────────────────────────────────────┐
│   │                                                           │
│   ├── Conv-001 (2026-03-22 10:30)                            │
│   │   ├── summary: "Asked about Tamil New Year dates"        │
│   │   ├── messages: [{role, content, timestamp}, ...]        │
│   │   ├── ON_DATE ──→ 2026-03-22                             │
│   │   ├── MENTIONED ──→ [Tamil, Calendar]                    │
│   │   └── EXTRACTED ──→ [Memory: "Tamil New Year is Apr 14"] │
│   │                                                           │
│   ├── Conv-002 (2026-03-22 14:00)                            │
│   │   ├── summary: "Discussed Synopsys layoffs"              │
│   │   ├── ON_DATE ──→ 2026-03-22                             │
│   │   ├── MENTIONED ──→ [Synopsys, Layoffs, Work]            │
│   │   └── EXTRACTED ──→ [Memory: "Synopsys laid off 1000"]   │
│   │                                                           │
│   └── Conv-003 (2026-03-21)                                   │
│       └── ...                                                 │
│                                                               │
├── DATES/ ─────────────────────────────────────────────────────┤
│   │                                                           │
│   ├── 2026-03-22                                             │
│   │   ├── conversations: [Conv-001, Conv-002]                │
│   │   ├── memories: [extracted from convs]                   │
│   │   ├── jobs: [any background jobs run]                    │
│   │   └── events: [calendar events]                          │
│   │                                                           │
│   └── 2026-03-21                                             │
│       └── ...                                                 │
│                                                               │
├── MEMORIES/ ──────────────────────────────────────────────────┤
│   │                                                           │
│   ├── Memory-001                                             │
│   │   ├── content: "Tamil New Year is April 14, 2026"        │
│   │   ├── type: fact                                         │
│   │   ├── importance: 0.7                                    │
│   │   ├── FROM_CONV ──→ Conv-001                             │
│   │   ├── ON_DATE ──→ 2026-03-22                             │
│   │   └── ABOUT ──→ [Tamil, Calendar]                        │
│   │                                                           │
│   └── Memory-002                                             │
│       ├── content: "Synopsys laid off 1000 employees"        │
│       ├── type: fact                                         │
│       ├── importance: 0.8                                    │
│       ├── FROM_CONV ──→ Conv-002                             │
│       ├── ON_DATE ──→ 2026-03-22                             │
│       └── ABOUT ──→ [Synopsys, Layoffs]                      │
│                                                               │
├── ENTITIES/ ──────────────────────────────────────────────────┤
│   │                                                           │
│   ├── Synopsys (type: company)                               │
│   │   ├── BELONGS_TO ──→ Work                                │
│   │   └── ←── ABOUT ←── [Memory-002, Conv-002]               │
│   │                                                           │
│   ├── Tamil (type: topic)                                    │
│   │   ├── BELONGS_TO ──→ Interests                           │
│   │   └── ←── ABOUT ←── [Memory-001, Conv-001]               │
│   │                                                           │
│   └── Layoffs (type: topic)                                  │
│       ├── BELONGS_TO ──→ Work                                │
│       └── ←── ABOUT ←── [Memory-002]                         │
│                                                               │
├── PEOPLE/ ────────────────────────────────────────────────────┤
│   │                                                           │
│   ├── Mom                                                    │
│   │   ├── relationship: mother                               │
│   │   ├── birthday: 1965-05-10                              │
│   │   ├── BELONGS_TO ──→ Family                              │
│   │   └── ←── ABOUT ←── [memories about mom]                 │
│   │                                                           │
│   └── John (coworker)                                        │
│       ├── BELONGS_TO ──→ Work                                │
│       └── ←── ABOUT ←── [memories about John]                │
│                                                               │
├── DOMAINS/ ───────────────────────────────────────────────────┤
│   │                                                           │
│   ├── Work ←── BELONGS_TO ←── [Synopsys, John, Layoffs]      │
│   ├── Family ←── BELONGS_TO ←── [Mom, Dad]                   │
│   └── Interests ←── BELONGS_TO ←── [Tamil, Travel]           │
│                                                               │
├── JOBS/ ──────────────────────────────────────────────────────┤
│   │                                                           │
│   ├── Job-001 (birthday_check)                               │
│   │   ├── status: completed                                  │
│   │   ├── triggered_at: 2026-03-22 08:00                     │
│   │   ├── result: "No birthdays today"                       │
│   │   ├── ON_DATE ──→ 2026-03-22                             │
│   │   └── USED_SKILL ──→ birthday_reminder                   │
│   │                                                           │
│   └── Job-002 (morning_news)                                 │
│       ├── USED_SKILL ──→ web_researcher                      │
│       ├── USED_TOOL ──→ [search]                             │
│       └── ABOUT ──→ [India, News]                            │
│                                                               │
└── EVENTS/ ────────────────────────────────────────────────────┘
    │
    ├── Event-001 (Meeting with John)
    │   ├── time: 2026-03-22 15:00
    │   ├── ON_DATE ──→ 2026-03-22
    │   └── INVOLVES ──→ [John]
    │
    └── Event-002 (Mom's birthday)
        ├── time: 2026-05-10
        ├── ON_DATE ──→ 2026-05-10
        └── INVOLVES ──→ [Mom]
```

**KEY: Everything connects through edges (many-to-many)**

Examples:
- Conversation → ON_DATE → Date, MENTIONED → [entities], EXTRACTED → [memories]
- Memory → FROM_CONV → Conversation, ON_DATE → Date, ABOUT → [entities]
- Entity ← ABOUT ← [memories, conversations, jobs]
- Job → USED_SKILL → Skill, USED_TOOL → [tools], ON_DATE → Date

---

## Node Types

### Core Nodes (always exist)

| Node | Properties | Purpose |
|------|------------|---------|
| `User` | name, location, timezone, preferences | Root of everything |
| `PAAW` | mcp_servers, tools | Assistant capabilities |

### Conversation Nodes (one per chat session)

| Node | Properties | Purpose |
|------|------------|---------|
| `Conversation` | id, started_at, ended_at, summary, message_count | A chat session |
| `Message` | role, content, timestamp, tool_calls | Individual message (optional - can embed in Conversation) |

### Date Nodes (one per day with activity)

| Node | Properties | Purpose |
|------|------------|---------|
| `Date` | date (YYYY-MM-DD) | Index for a day |

### Memory Nodes (extracted insights)

| Node | Properties | Purpose |
|------|------------|---------|
| `Memory` | content, type, importance, timestamp | Extracted fact/preference/episode |

### Entity Nodes (things in user's world)

| Node | Properties | Purpose |
|------|------------|---------|
| `Person` | name, relationship, birthday, notes | People in user's life |
| `Domain` | name, description | Life areas (Work, Family, Health) |
| `Entity` | name, type, notes | Companies, places, topics |

### Activity Nodes

| Node | Properties | Purpose |
|------|------------|---------|
| `Job` | id, name, status, triggered_at, result | Background task execution |
| `Event` | title, time, description, recurring | Calendar events |

---

## Edge Types (Complete Reference)

| From | Edge | To | Purpose |
|------|------|----|---------|
| Conversation | `ON_DATE` | Date | When conversation happened |
| Conversation | `MENTIONED` | Entity/Person | Entities discussed |
| Conversation | `EXTRACTED` | Memory | Memories from this conversation |
| Memory | `FROM_CONV` | Conversation | Source conversation |
| Memory | `ON_DATE` | Date | When memory was created |
| Memory | `ABOUT` | Entity/Person/Domain | What the memory is about |
| Entity | `BELONGS_TO` | Domain | Categorization |
| Person | `BELONGS_TO` | Domain | Categorization |
| Job | `ON_DATE` | Date | When job ran |
| Job | `USED_SKILL` | Skill | Which skill was used |
| Job | `USED_TOOL` | Tool | Which MCP tools were called |
| Job | `ABOUT` | Entity | What the job was about |
| Event | `ON_DATE` | Date | When event occurs |
| Event | `INVOLVES` | Person | Who's involved |
| User | `HAS_ASSISTANT` | PAAW | Ownership |
| User | `HAS_DOMAIN` | Domain | User's life domains |
| User | `KNOWS` | Person | User's relationships |

**Cypher Query Examples:**

```cypher
-- "What do I know about Synopsys?" (memories + conversations)
MATCH (e:Entity {name: 'Synopsys'})
OPTIONAL MATCH (e)<-[:ABOUT]-(m:Memory)-[:ON_DATE]->(d:Date)
OPTIONAL MATCH (e)<-[:MENTIONED]-(c:Conversation)
RETURN e, collect(DISTINCT m) as memories, collect(DISTINCT c) as conversations

-- "What happened on March 22?" (everything for a day)
MATCH (d:Date {date: '2026-03-22'})
OPTIONAL MATCH (c:Conversation)-[:ON_DATE]->(d)
OPTIONAL MATCH (m:Memory)-[:ON_DATE]->(d)
OPTIONAL MATCH (j:Job)-[:ON_DATE]->(d)
OPTIONAL MATCH (ev:Event)-[:ON_DATE]->(d)
RETURN d, collect(c) as convs, collect(m) as memories, collect(j) as jobs, collect(ev) as events

-- "What did we talk about recently?" (recent conversations)
MATCH (c:Conversation)-[:ON_DATE]->(d:Date)
WHERE d.date >= '2026-03-15'
RETURN c.summary, d.date ORDER BY d.date DESC, c.started_at DESC

-- "Find memories about Work domain"
MATCH (dom:Domain {name: 'Work'})<-[:BELONGS_TO]-(e)
MATCH (m:Memory)-[:ABOUT]->(e)
RETURN m.content, e.name ORDER BY m.timestamp DESC

-- "What tools did job use?"
MATCH (j:Job {id: 'job-001'})-[:USED_TOOL]->(t:Tool)
RETURN t.name
```

---

## Context Building Strategy

**Goal**: Build the right context for EVERY LLM call. Not too much, not too little.

### Context Layers (in order of priority)

```
Layer 1: ALWAYS INCLUDE (small, essential)
├── User basics (name, timezone, location)
├── Today's date
├── PAAW capabilities (tools available)
└── Current conversation history (this session)

Layer 2: RECENCY (what happened recently)
├── Last N conversations (summaries, not full content)
├── Recent memories (last 7 days)
└── Today's events/jobs

Layer 3: RELEVANCE (semantic search based on message)
├── Memories ABOUT mentioned entities
├── Past conversations MENTIONING similar topics
├── Related entities and their context
└── Domain context if domain detected

Layer 4: ON-DEMAND (only if needed)
├── Full conversation history (if "what did we discuss")
├── Deep entity details (if asking about specific thing)
└── Job history (if asking about past tasks)
```

### Context Budget

```python
# Token limits per layer (approximate)
CONTEXT_BUDGET = {
    'layer1_essential': 500,    # Always included
    'layer2_recency': 1000,     # Recent stuff
    'layer3_relevance': 1500,   # Searched content
    'layer4_ondemand': 1000,    # If needed
    'conversation_history': 2000,  # Current session
    # Total: ~6000 tokens for context, rest for response
}
```

### Implementation

```python
async def build_context(user_id: str, message: str, conversation_history: list) -> str:
    context_parts = []
    
    # Layer 1: Essential (always)
    user = await get_user(user_id)
    paaw = await get_paaw_node()
    today = date.today().isoformat()
    
    context_parts.append(f"""
=== USER ===
Name: {user.name}
Location: {user.location}
Timezone: {user.timezone}
Today: {today}

=== YOUR CAPABILITIES ===
MCP Tools: {', '.join(paaw.tools)}
""")
    
    # Layer 2: Recency
    recent_convs = await get_recent_conversations(days=7, limit=5)
    recent_memories = await get_recent_memories(days=7, limit=10)
    
    if recent_convs:
        context_parts.append(f"""
=== RECENT CONVERSATIONS ===
{format_conversation_summaries(recent_convs)}
""")
    
    if recent_memories:
        context_parts.append(f"""
=== RECENT MEMORIES ===
{format_memories(recent_memories)}
""")
    
    # Layer 3: Relevance (semantic search)
    keywords = extract_keywords(message)
    
    # Search entities mentioned
    relevant_entities = await search_entities(keywords)
    if relevant_entities:
        # Get memories about these entities
        entity_memories = await get_memories_about(relevant_entities)
        context_parts.append(f"""
=== RELEVANT CONTEXT ===
Entities: {format_entities(relevant_entities)}
Related memories: {format_memories(entity_memories)}
""")
    
    # Detect if asking about past conversation
    if needs_conversation_history(message):  # "what did we discuss", "earlier", etc.
        past_convs = await search_conversations(keywords)
        context_parts.append(f"""
=== PAST CONVERSATIONS ===
{format_full_conversations(past_convs)}
""")
    
    return '\n'.join(context_parts)
```

---

## Conversation Management

### Conversation Lifecycle

```python
# 1. Start conversation (on first message)
async def start_conversation(user_id: str) -> Conversation:
    conv = Conversation(
        id=generate_id(),
        started_at=datetime.now(),
        messages=[],
    )
    # Link to today
    await link_to_date(conv, date.today())
    return conv

# 2. Add messages during conversation
async def add_message(conv: Conversation, role: str, content: str, tool_calls=None):
    conv.messages.append(Message(
        role=role,
        content=content,
        timestamp=datetime.now(),
        tool_calls=tool_calls,
    ))

# 3. End conversation (after timeout or explicit end)
async def end_conversation(conv: Conversation):
    conv.ended_at = datetime.now()
    
    # Generate summary
    conv.summary = await llm.summarize_conversation(conv.messages)
    
    # Extract entities mentioned
    entities = await llm.extract_entities(conv.messages)
    for entity in entities:
        node = await get_or_create_entity(entity)
        await create_edge(conv, 'MENTIONED', node)
    
    # Extract memories
    memories = await llm.extract_memories(conv.messages)
    for memory in memories:
        mem_node = await create_memory(memory)
        await create_edge(conv, 'EXTRACTED', mem_node)
        await create_edge(mem_node, 'FROM_CONV', conv)
        
        # Link memory to mentioned entities
        for entity in memory.about:
            await create_edge(mem_node, 'ABOUT', entity)
    
    # Save to graph
    await save_conversation(conv)
```

### Memory Extraction

```python
async def extract_memories(messages: list[Message]) -> list[Memory]:
    """LLM extracts what's worth remembering from a conversation."""
    
    prompt = """Analyze this conversation and extract memories worth keeping.

For each memory, provide:
- content: The actual information (fact, preference, event)
- type: 'fact' | 'preference' | 'episode' | 'insight'
- importance: 0.0-1.0 (how important is this to remember?)
- about: List of entity names this is about

Examples of good memories:
- "User's mom's birthday is May 10" (fact, importance: 0.9)
- "User prefers morning meetings" (preference, importance: 0.6)
- "User was stressed about Synopsys layoffs on March 22" (episode, importance: 0.7)

Conversation:
{messages}

Return JSON array of memories. Only include things worth remembering long-term.
"""
    
    result = await llm.chat(prompt.format(messages=format_messages(messages)))
    return parse_memories(result)
```

### Conversation Session Management

```python
# In-memory conversation tracking (per user session)
class ConversationManager:
    def __init__(self):
        self._active_conversations: dict[str, Conversation] = {}
        self._conversation_timeout = timedelta(minutes=30)
    
    async def get_or_create(self, user_id: str) -> Conversation:
        if user_id in self._active_conversations:
            conv = self._active_conversations[user_id]
            # Check if timed out
            if datetime.now() - conv.last_activity > self._conversation_timeout:
                await self.end_conversation(user_id)
                return await self.create_new(user_id)
            return conv
        return await self.create_new(user_id)
    
    async def create_new(self, user_id: str) -> Conversation:
        conv = await start_conversation(user_id)
        self._active_conversations[user_id] = conv
        return conv
    
    async def end_conversation(self, user_id: str):
        if user_id in self._active_conversations:
            conv = self._active_conversations.pop(user_id)
            await end_conversation(conv)
```

---

## Agent Loop (like Claude)

```python
class PAWAgent:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.mcp_client = MCPClient()
        
    async def chat(self, user_id: str, message: str) -> str:
        # Get or create conversation
        conv = await self.conversation_manager.get_or_create(user_id)
        
        # Add user message
        await conv.add_message('user', message)
        
        # Build context from mental model
        context = await build_context(user_id, message, conv.messages)
        
        # Get available tools
        tools = await self.mcp_client.get_tools()
        
        # Build messages for LLM
        system_prompt = f"""You are PAAW (Personal AI Assistant Workspace).

{context}

You have access to tools. Use them when needed to help the user.
Be concise and helpful. Remember context from this conversation.
"""
        
        messages = self._build_llm_messages(conv.messages)
        
        # Main loop - agent can call tools multiple times
        max_iterations = 10
        for i in range(max_iterations):
            response = await llm.chat(
                system=system_prompt,
                messages=messages,
                tools=tools,
                return_full_response=True,
            )
            
            # If LLM wants to call tools
            if response.tool_calls:
                # Add assistant message with tool calls
                await conv.add_message('assistant', response.content, response.tool_calls)
                messages.append({
                    'role': 'assistant',
                    'content': response.content,
                    'tool_calls': response.tool_calls,
                })
                
                # Execute tools
                for tool_call in response.tool_calls:
                    result = await self.mcp_client.execute(
                        tool_call.name, 
                        tool_call.arguments
                    )
                    # Add tool result
                    await conv.add_message('tool', result, tool_id=tool_call.id)
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': result,
                    })
                continue
            
            # Otherwise, we have the final response
            final_response = response.content
            await conv.add_message('assistant', final_response)
            break
        
        return final_response
    
    def _build_llm_messages(self, conv_messages: list) -> list:
        """Convert conversation messages to LLM format."""
        return [
            {'role': m.role, 'content': m.content}
            for m in conv_messages
        ]
```

---

## What Gets Deleted

- ❌ `agents/` - No sub-agents
- ❌ `attention/` - No attention manager  
- ❌ `orchestrator/` - No job orchestrator
- ❌ `queue/` - No message queue
- ❌ `scheduler/` - Simplified (jobs folder only)
- ❌ Complex job decomposition
- ❌ Skills with personas
- ❌ Trails

---

## What Gets Kept & Simplified

| Module | Status | Notes |
|--------|--------|-------|
| `brain/llm.py` | Keep | LLM wrapper with tool calling |
| `tools/mcp_client.py` | Keep | MCP tool execution |
| `mental_model/` | **Rebuild** | New scalable graph schema |
| `onboarding/` | Keep | Initial user setup |
| `api/server.py` | **Simplify** | Remove job/orchestrator references |
| `cli/` | Keep | CLI interface |
| `agent.py` | **Rebuild** | Simple tool-calling loop |

---

## Graph Schema (Apache AGE)

```sql
-- Initialize graph
SELECT create_graph('mental_model');

-- Create node labels
SELECT create_vlabel('mental_model', 'User');
SELECT create_vlabel('mental_model', 'PAAW');
SELECT create_vlabel('mental_model', 'Conversation');
SELECT create_vlabel('mental_model', 'Date');
SELECT create_vlabel('mental_model', 'Memory');
SELECT create_vlabel('mental_model', 'Entity');
SELECT create_vlabel('mental_model', 'Person');
SELECT create_vlabel('mental_model', 'Domain');
SELECT create_vlabel('mental_model', 'Job');
SELECT create_vlabel('mental_model', 'Event');
SELECT create_vlabel('mental_model', 'Skill');
SELECT create_vlabel('mental_model', 'Tool');

-- Create edge labels
SELECT create_elabel('mental_model', 'ON_DATE');
SELECT create_elabel('mental_model', 'FROM_CONV');
SELECT create_elabel('mental_model', 'MENTIONED');
SELECT create_elabel('mental_model', 'EXTRACTED');
SELECT create_elabel('mental_model', 'ABOUT');
SELECT create_elabel('mental_model', 'BELONGS_TO');
SELECT create_elabel('mental_model', 'KNOWS');
SELECT create_elabel('mental_model', 'HAS_ASSISTANT');
SELECT create_elabel('mental_model', 'HAS_DOMAIN');
SELECT create_elabel('mental_model', 'USED_SKILL');
SELECT create_elabel('mental_model', 'USED_TOOL');
SELECT create_elabel('mental_model', 'INVOLVES');
```

---

## Implementation Steps

### Step 1: Clean Database & Codebase
- [x] Drop all graph data
- [x] Remove dead code (orchestrator, queue, agents, etc.)
- [x] Clean up imports

### Step 2: Implement Mental Model Schema
- [ ] `mental_model/schema.py` - Node and edge definitions
- [ ] `mental_model/graph.py` - CRUD operations for graph
- [ ] `mental_model/context.py` - Context building logic
- [ ] `mental_model/search.py` - Semantic search for relevance

### Step 3: Implement Conversation Management
- [ ] `conversation/manager.py` - Conversation lifecycle
- [ ] `conversation/memory.py` - Memory extraction

### Step 4: Rebuild Agent
- [ ] `agent.py` - Simple tool-calling loop
- [ ] Integrate mental model context
- [ ] Integrate conversation management

### Step 5: Simplify API
- [ ] `api/server.py` - Clean endpoints
- [ ] Remove all job/orchestrator code

### Step 6: Test
- [ ] Chat works
- [ ] Tools work (search)
- [ ] Conversations saved
- [ ] Memories extracted
- [ ] Context includes relevant info

---

## File Structure (Target)

```
paaw/
├── __init__.py
├── agent.py              # Main agent with tool loop
├── config.py             # Configuration
├── main.py               # Entry point
├── models.py             # Pydantic models
│
├── api/
│   ├── __init__.py
│   └── server.py         # FastAPI endpoints
│
├── brain/
│   ├── __init__.py
│   ├── llm.py            # LLM wrapper
│   └── prompts.py        # System prompts
│
├── conversation/         # NEW
│   ├── __init__.py
│   ├── manager.py        # Conversation lifecycle
│   └── memory.py         # Memory extraction
│
├── mental_model/
│   ├── __init__.py
│   ├── schema.py         # Node/edge definitions
│   ├── graph.py          # Graph CRUD
│   ├── context.py        # Context building
│   └── search.py         # Semantic search
│
├── tools/
│   ├── __init__.py
│   ├── mcp_client.py     # MCP client
│   └── registry.py       # Tool registry
│
├── onboarding/
│   ├── __init__.py
│   ├── extractor.py
│   └── flow.py
│
└── cli/
    ├── __init__.py
    └── main.py
```

---

## Future (Not Now)

- Jobs/scheduling (add back when core works)
- Skills as templates
- Multiple users
- Different channels (Telegram, etc.)
- Event reminders

---

*Scalable by design. Simple in execution.*
