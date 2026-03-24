# PAAW Architecture 🐾

> **PAAW** (pronounced "paw") — Your personal AI assistant that lives on your machine, **builds a mental model of YOU** through a fractal knowledge graph, and is reachable via any channel you prefer.
>
> 🌐 **Website:** [paaw.online](https://paaw.online)

---

## Table of Contents

1. [Vision](#vision)
2. [The Mental Model](#the-mental-model)
3. [Core Principles](#core-principles)
4. [High-Level Architecture](#high-level-architecture)
5. [Component Deep Dive](#component-deep-dive)
   - [Event Loop](#1-event-loop)
   - [Brain (LLM)](#2-brain-llm-layer)
   - [Mental Model (Graph)](#3-mental-model-graph-layer)
   - [Channels](#4-channels)
   - [Tools (MCP)](#5-tools-mcp)
   - [System Services](#6-system-services)
   - [Web UI & CLI](#7-web-ui--cli)
6. [Data Models](#data-models)
7. [Context Management](#context-management)
8. [Onboarding Flow](#onboarding-flow)
9. [Security Model](#security-model)
10. [Deployment](#deployment)
11. [Tech Stack](#tech-stack)
12. [Project Structure](#project-structure)
13. [Build Phases](#build-phases)
14. [Summary](#summary)

---

## Vision

PAAW is a **digital being** that:

- **Lives** on a machine (your laptop, a Raspberry Pi, a VPS — anywhere Docker runs)
- **Breathes** via a heartbeat system (always on, self-monitoring)
- **Communicates** through any channel (Web UI, CLI, Telegram, Slack, WhatsApp, Discord)
- **Thinks** using any LLM (local via Ollama, or cloud via OpenAI/Anthropic/etc.)
- **Understands YOU** via a fractal mental model graph (not just chat history)
- **Acts** through pluggable tools (MCP protocol)
- **Grows** with you over time, deepening its understanding

### The Human Friend Analogy

Think about a close friend who has known you for 10 years. They know:

| A 10-Year Friend Knows | PAAW Learns |
|------------------------|-------------|
| Your name, where you're from | Identity node |
| Your communication style | Personality patterns |
| When you're stressed (and need space) | Behavioral observations |
| Who matters to you (names, relationships) | People graph |
| Your patterns (morning person? procrastinator?) | Lifestyle patterns |
| Your values (what you'd never compromise on) | Core beliefs |
| Your quirks (hates small talk? loves chai?) | Preferences |
| What you're working on, struggling with | Work & Projects |
| Your dreams and fears | Goals & Concerns |

**PAAW builds this understanding organically through conversation, not forms.**

---

## The Mental Model

### The Core Idea: A Fractal, Interconnected Graph

PAAW doesn't store rigid database rows. It builds a **living mental model** of you — a graph that grows, evolves, and deepens over time.

Think of it like the universe:
- **Zoomed out**: Everything looks like organized clusters
- **Zoomed in**: Each cluster is fuzzy, organic, unique
- **Everything is connected**: Not a tree, a **web** of relationships

```
                                    ┌─────────────────┐
                                    │   UNIVERSE      │
                                    │ (All knowledge) │
                                    └────────┬────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                         ┌────────┐    ┌────────┐    ┌────────┐
                         │Concepts│    │ People │    │ Places │
                         └───┬────┘    └────────┘    └────────┘
                             │
                    ┌────────┼────────┐
                    ▼        ▼        ▼
              ┌──────────┐ ┌────┐ ┌────────┐
              │   Tech   │ │ AI │ │  ...   │
              └────┬─────┘ └──┬─┘ └────────┘
                   │          │
                   └────┬─────┘
                        ▼
       ┌────────────────────────────────────────────────────────────┐
       │                         SIVARAM                             │
       │                    (A node in the universe)                 │
       │                                                             │
       │  This is where PAAW's focus is — understanding THIS human   │
       │  as deeply as possible, with all their complexity           │
       └────────────────────────────────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ PEOPLE  │   │  WORK   │   │ HEALTH  │   │ FINANCE │
    │         │   │         │   │         │   │         │
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │             │
    (Family,      (Job, PAAW    (Fitness,     (Savings,
     Friends,      project,      Diet,         Investments)
     Colleagues)   Skills)       Sleep)
```

### The Fractal Nature

**Zoomed out** — The user looks like organized life domains:
```
📍 Sivaram
├── 👥 People
├── 💼 Work  
├── 🏃 Health
└── 💰 Finance
```

**Zoomed in** (on Work) — Complexity emerges:
```
💼 Work
├── current_state: "Building PAAW, employed at TechCorp"
├── context: "Senior dev who wants independence..."
├── key_facts: ["10+ yrs exp", "prefers backend"]
├── Job/
│   ├── company: "TechCorp"
│   ├── satisfaction: "meh" (PAAW inferred this!)
│   └── memories: [conversations about work stress]
├── Projects/
│   └── PAAW/
│       ├── status: "active"
│       ├── progress: "Phase 1 complete"
│       ├── context: "Personal AI assistant..."
│       └── memories: [all PAAW conversations]
└── Career Goals/
    └── context: "Wants to go indie eventually"
```

**Zoomed in more** (on PAAW project) — Even more detail:
```
📁 PAAW Project
├── context: "Building an AI that truly remembers..."
├── key_facts: ["Using Claude", "Graph memory", "Privacy-first"]
├── blockers: ["Need to design memory system"]
├── Components/
│   ├── Memory System (current focus)
│   ├── LLM Integration (done)
│   └── CLI (done)
└── memories: [every conversation about PAAW]
```

### Not a Tree — A Web

Every node can connect to multiple other nodes:

```
Sivaram ──SPEAKS──► Tamil ──ORIGIN──► Tamil Nadu ──PART_OF──► India
    │                                      │
    └──LIVES_IN──► Chennai ──LOCATED_IN────┘
    │
    └──WORKS_ON──► PAAW ──USES──► Claude ──MADE_BY──► Anthropic
    │                │
    │                └──INSPIRED_BY──► Frustration ──FELT_BY──► Sivaram (circular!)
    │
    └──KNOWS──► Priya (wife) ──WORKS_AT──► Hospital
    │              │
    │              └──FRIEND_OF──► Kavitha ──KNOWN_BY──► Sivaram (multi-path!)
    │
    └──INTERESTED_IN──► AI ──SUBSET_OF──► Tech ──CAREER_IN──► Sivaram
```

### The Fuzziness Principle

LLMs are probabilistic. Humans are fuzzy. **PAAW embraces this.**

**No rigid schemas.** Each node has:
- A **skeleton** (always present): `context`, `key_facts`, `memories`
- **Flexible attributes** (whatever makes sense for that node)

```python
# A Person node
{
    "type": "person",
    "label": "Priya",
    "context": "Sivaram's wife, doctor at Apollo Hospital",
    "key_facts": ["Very supportive", "Night shifts sometimes"],
    "memories": [→ conversations mentioning her],
    "attributes": {
        "relationship": "wife",
        "occupation": "doctor"
    }
}

# A Project node (different attributes!)
{
    "type": "project", 
    "label": "PAAW",
    "context": "Personal AI assistant Sivaram is building",
    "key_facts": ["Graph memory", "Claude-powered", "Privacy-first"],
    "memories": [→ all PAAW conversations],
    "attributes": {
        "status": "active",
        "progress": "Phase 1 complete",
        "repo": "github.com/SivaRamSV/paaw"
    }
}

# A Goal node (yet different attributes!)
{
    "type": "goal",
    "label": "Exercise More",
    "context": "Sivaram wants to get fit, keeps procrastinating",
    "key_facts": ["Tried gym, didn't stick", "Prefers morning"],
    "memories": [→ health-related conversations],
    "attributes": {
        "progress": 10,
        "target": "Run 5K",
        "deadline": null  # fuzzy!
    }
}
```

### The User Node (Root)

The root of PAAW's understanding:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 USER (Root)                                      │
│  ═══════════════════════════════════════════════════════════════════════════════ │
│                                                                                  │
│  Identity:                     │  Personality:                                   │
│  ├─ name: "Siva"               │  ├─ communication_style: "direct, no fluff"    │
│  ├─ preferred_name: "Siva"     │  ├─ decision_making: "analytical then gut"     │
│  ├─ gender: "male"             │  ├─ stress_response: "goes quiet, needs space" │
│  ├─ age_range: "30s"           │  ├─ motivation: "building things that matter"  │
│  ├─ location: "Chennai, India" │  └─ pet_peeves: ["fluff", "slow responses"]    │
│  ├─ timezone: "Asia/Kolkata"   │                                                │
│  └─ languages: ["Tamil", "En"] │  Patterns:                                     │
│                                │  ├─ active_hours: "night owl, peaks 10pm-2am"  │
│  Story:                        │  ├─ work_style: "deep focus blocks"            │
│  "A builder at heart. Started  │  └─ energy: "weekends = recharge"              │
│   coding young, worked at big  │                                                │
│   companies, now wants to      │  Key Facts: (things PAAW learned)              │
│   build his own things. Values │  ├─ "prefers examples over theory"             │
│   depth over breadth, hates    │  ├─ "hates when I repeat myself"               │
│   wasting time, appreciates    │  ├─ "uses 'da' when comfortable"               │
│   directness."                 │  └─ "appreciates smart pushback"               │
│                                                                                  │
│  Children: [People, Work, Lifestyle, Health, Finance, Dreams, ...]              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Organic Growth

**Week 1**: Basic model from onboarding questions
```
📍 Sivaram (Chennai, Tamil Nadu, Software Dev)
├── 💼 Work
│   └── Building PAAW
└── 🏃 Health
    └── Wants to exercise more
```

**Week 4**: Model has grown organically
```
📍 Sivaram
├── 👥 People
│   ├── 👨‍👩‍👧 Family
│   │   ├── Priya (wife, doctor)
│   │   └── Parents (in Madurai)
│   └── 💼 Work
│       └── Raj (boss, "difficult")
├── 💼 Work
│   ├── TechCorp (job, "meh")
│   └── PAAW (passion project)
├── 🏃 Health
│   └── Exercise goal (10%)
└── ☕ Preferences
    └── Filter coffee addict
```

**Month 3**: Deep understanding
```
📍 Sivaram
├── 👥 People (12 nodes)
├── 💼 Work (8 nodes)
├── 🏃 Health (4 nodes)
├── 💰 Finance (3 nodes)
├── 📚 Learning (5 nodes)
├── 🎯 Goals (7 active)
├── ☕ Preferences (15 facts)
└── 💭 Dreams
    └── "Go indie by 35"

PAAW now knows:
- When Sivaram is stressed (short messages)
- Tuesday evenings are sacred (gaming)
- Career frustration is building
- Filter coffee = instant mood boost
```

### The Visualization

Users can explore their mental model:

```
"PAAW, show me what you know about me"

┌────────────────────────────────────────────────────────────────┐
│  Your Mental Model                           [Zoom +] [Zoom -] │
│                                                                │
│                        ┌──────────┐                            │
│                        │  Sivaram │                            │
│                        └────┬─────┘                            │
│              ┌──────────────┼──────────────┬──────────┐       │
│              ▼              ▼              ▼          ▼       │
│         ┌────────┐    ┌────────┐    ┌────────┐  ┌────────┐   │
│         │ People │    │  Work  │    │ Health │  │Finance │   │
│         │  (12)  │    │  (8)   │    │  (4)   │  │  (3)   │   │
│         └───┬────┘    └───┬────┘    └────────┘  └────────┘   │
│             │             │                                   │
│        ┌────┴────┐   ┌────┴────┐                             │
│        ▼         ▼   ▼         ▼                             │
│    ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                      │
│    │Family│ │ Work │ │ Job  │ │ PAAW │ ← Click to explore   │
│    └──────┘ └──────┘ └──────┘ └──────┘                      │
│                                                              │
│  Click any node to see details & memories                   │
│  Tell me if something's wrong: "PAAW, that's not right"     │
└────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. **Simple & Elegant**
- Minimal core (~5 modules), everything else is plugins
- One Docker container, one command to run
- No over-engineering — complexity only when needed

### 2. **Privacy First**
- All data stays on YOUR machine
- Local LLM support (Ollama)
- No telemetry, no cloud dependency (except LLM API if you choose)

### 3. **Fully Open Source**
- Every component uses truly open source licenses
- No AGPL, no source-available, no proprietary dependencies

### 4. **Goal-Oriented Memory**
- Not just chat history — a structured graph of goals, memories, and learnings
- Each goal has its own context window
- Memory decays over time (like human memory)

### 5. **Channel Agnostic**
- Message PAAW on Slack at work, WhatsApp at home, voice while driving
- Same agent, same memory, same brain

### 6. **Traceable & Auditable**
- Every action logged
- Every decision explainable
- Full audit trail

### 7. **Autonomous**
- PAAW runs indefinitely without human supervision
- Self-healing on errors (retry, fix, continue)
- Notifies user on failures instead of crashing

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER CONTAINER "paaw"                        │
│                    (Minimal Permissions)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                        PAAW AGENT                            │ │
│  │                                                             │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │                   EVENT LOOP                           │ │ │
│  │  │                   (Always On)                          │ │ │
│  │  │                                                        │ │ │
│  │  │  • Listens for messages from channels                  │ │ │
│  │  │  • Runs heartbeat checks                               │ │ │
│  │  │  • Executes scheduled tasks                            │ │ │
│  │  │  • Handles tool callbacks                              │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  │                            │                                │ │
│  │                            ▼                                │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │                      BRAIN                             │ │ │
│  │  │                    (LiteLLM)                           │ │ │
│  │  │                                                        │ │ │
│  │  │  • Router: Message → Goal mapping                      │ │ │
│  │  │  • Planner: Break into tasks                           │ │ │
│  │  │  • Thinker: LLM reasoning                              │ │ │
│  │  │  • Executor: Self-healing task execution               │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  │                            │                                │ │
│  │              ┌─────────────┴─────────────┐                 │ │
│  │              ▼                           ▼                 │ │
│  │  ┌─────────────────────┐   ┌─────────────────────────┐    │ │
│  │  │    MEMORY TOOL      │   │    EXTERNAL TOOLS       │    │ │
│  │  │    (Built-in)       │   │    (MCP Protocol)       │    │ │
│  │  │                     │   │                         │    │ │
│  │  │  • Strict protocol  │   │  • Web Search           │    │ │
│  │  │  • Add/retrieve     │   │  • Calendar             │    │ │
│  │  │  • Goal graph ops   │   │  • GitHub               │    │ │
│  │  │  • Context loading  │   │  • Telegram/Slack/WA    │    │ │
│  │  │  • Summarize/archive│   │  • Any MCP server       │    │ │
│  │  └─────────┬───────────┘   └─────────────────────────┘    │ │
│  │            │                                               │ │
│  │            ▼                                               │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │              PostgreSQL + AGE + pgvector              │ │ │
│  │  │                   (Graph Memory)                       │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │   CHANNELS            │  │   SYSTEM SERVICES    │            │
│  │                       │  │                      │            │
│  │  • Web UI (:8080)     │  │  • Heartbeat         │            │
│  │  • CLI                │  │  • Scheduler         │            │
│  │  • Telegram           │  │  • Audit Log         │            │
│  │  • Slack              │  │  • Health Checks     │            │
│  │  • WhatsApp           │  │                      │            │
│  │  • Discord            │  │                      │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                         VALKEY                            │  │
│  │              (Pub/Sub, Cache, Task Queue)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Deep Dive

### 1. Event Loop

The heart of PAAW — an async event loop that never stops.

```python
async def main():
    # Initialize components
    db = await Database.connect()
    memory = MemoryTool(db)
    brain = Brain(memory)
    channels = await start_channels(brain)
    scheduler = Scheduler(brain)
    heartbeat = Heartbeat()
    
    # Run forever
    await asyncio.gather(
        channels.listen(),      # Messages from all channels
        scheduler.run(),        # Scheduled tasks
        heartbeat.run(),        # Health monitoring
    )
```

**Event Sources:**
| Event | Source | Handler |
|-------|--------|---------|
| User message | Channels (Telegram, Web, etc.) | `brain.process()` |
| Heartbeat tick | Timer (every 30s) | `heartbeat.check()` |
| Scheduled task | Scheduler (cron-like) | `brain.execute_task()` |
| Tool callback | MCP tools | `brain.handle_callback()` |

---

### 2. Brain (LLM Layer)

The thinking engine. Model-agnostic via LiteLLM.

```
┌─────────────────────────────────────────────────────────┐
│                        BRAIN                             │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ROUTER                                           │   │
│  │  "What goal does this message relate to?"         │   │
│  │                                                   │   │
│  │  Input: "How's my Rust learning going?"           │   │
│  │  Output: Goal("learning.rust")                    │   │
│  │                                                   │   │
│  │  Uses: Embedding similarity + keyword matching    │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CONTEXT LOADER                                   │   │
│  │  "Load relevant memories for this goal"           │   │
│  │                                                   │   │
│  │  • Goal's context window (recent + summarized)    │   │
│  │  • Related memories (semantic search)             │   │
│  │  • Parent goal context (light)                    │   │
│  │  • User preferences                               │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  THINKER (LLM)                                    │   │
│  │  "Reason about the request"                       │   │
│  │                                                   │   │
│  │  Model selection:                                 │   │
│  │  • Simple query → cheap/fast model (GPT-4o-mini) │   │
│  │  • Complex reasoning → powerful model (Claude)   │   │
│  │  • Private data → local model (Ollama)           │   │
│  │                                                   │   │
│  │  LiteLLM unifies all providers                   │   │
│  └──────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │  EXECUTOR                                         │   │
│  │  "Perform actions with self-healing"              │   │
│  │                                                   │   │
│  │  for attempt in range(max_retries):               │   │
│  │      try:                                         │   │
│  │          result = execute(action)                 │   │
│  │          verify(result)                           │   │
│  │          return result                            │   │
│  │      except Error as e:                           │   │
│  │          fix_action = llm.fix(action, error=e)    │   │
│  │          continue                                 │   │
│  │  notify_user("Failed after N attempts")           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**LiteLLM Configuration:**
```yaml
# configs/llm.yaml

models:
  default: gpt-4o-mini              # Fast, cheap for simple tasks
  reasoning: claude-sonnet-4-20250514    # Complex planning
  private: ollama/llama3.2          # Local, private data
  embedding: text-embedding-3-small # For semantic search

routing:
  # Simple queries → fast model
  simple: [status_check, greeting, clarification]
  # Complex tasks → powerful model  
  complex: [planning, analysis, multi_step]
  # Sensitive data → local model
  private: [personal_info, health, finance]
```

---

### 3. Mental Model (Graph Layer)

The soul of PAAW. A fractal knowledge graph stored in PostgreSQL with Apache AGE.

#### Philosophy: Emergent Structure, Not Imposed Categories

**The Core Principle**: The only thing we know for certain is that we're talking to a **human (User)**. Everything else — domains, people, goals, projects — **emerges from conversation**.

Think about how human memory works:
- You don't have pre-defined "folders" for Work, Family, Health
- You meet someone → a "Person" concept forms
- You start a job → a "Work" context emerges
- Structure is **discovered**, not declared

**PAAW works the same way:**

```
WRONG (Current):                      RIGHT (New):
─────────────────                     ─────────────
Onboarding asks:                      Onboarding creates:
"What domains?"                       → Just the User node
"Who are your people?"                
"What are your goals?"                Everything else emerges:
                                      → User mentions mom 
Then creates:                            → Person node created
→ Hardcoded Domain nodes                 → Linked to User
→ Hardcoded Person nodes              → User mentions work
→ Hardcoded Goal nodes                   → Domain node created
                                         → Linked to User
Structure is IMPOSED                  → Mom's birthday mentioned
                                         → Memory linked to Person:Mom
                                      
                                      Structure EMERGES
```

#### The Single Unified Model

**Every piece of information is a Node.** 
**Every relationship is an Edge.**
**The LLM decides what nodes to create and how to link them.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE UNIFIED NODE MODEL                               │
│                                                                             │
│   Node Types (not pre-created, emerge as needed):                            │
│   ├── User     - Root node, the human we're serving (ONLY certainty)        │
│   ├── Person   - People in user's life (emerges when mentioned)             │
│   ├── Domain   - Life areas (emerges from context)                          │
│   ├── Project  - Things being built (emerges when discussed)                │
│   ├── Goal     - Objectives (emerges from aspirations)                      │
│   ├── Memory   - Facts, observations, episodes (constantly created)         │
│   ├── Task     - Actionable items (emerges from commitments)                │
│   └── Event    - Important dates, milestones (emerges from mentions)        │
│                                                                             │
│   The LLM decides:                                                          │
│   - WHEN to create a new node (vs reuse existing)                           │
│   - WHAT type it should be                                                  │
│   - WHERE it connects (parent node)                                         │
│   - WHAT attributes matter for that node                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### How It Works: The Entity-Memory Pattern

When the user says something, the LLM does two things:

1. **Recognizes entities** (new or existing):
   - "My mom" → Is there a Person:Mom? If not, create one linked to User
   - "My work project" → Is there a Project? If not, create one

2. **Attaches memories** to those entities:
   - "Mom's birthday is March 22" → Memory linked to Person:Mom

```
User: "My mom's name is Velammal, her birthday is March 22nd"

LLM thinks:
1. "Mom" → new Person entity, parent is User, relationship is "mother"
2. "Velammal" → that's her name, attribute of the Person
3. "Birthday March 22" → a Memory attached to Person:Mom

LLM outputs:
<entity>
type: Person
label: Mom (Velammal)
parent: user_default
context: User's mother
attributes:
  relationship: mother
  name: Velammal
</entity>

<memory>
content: Mom's birthday is March 22nd every year
belongs_to: person_mom_(velammal)
</memory>

System:
1. Creates Person node (if doesn't exist)
2. Links Person → User with CHILD_OF edge
3. Creates Memory node
4. Links Memory → Person with BELONGS_TO edge
```

#### The Smart Linking System

The system needs to be intelligent about linking:

```python
# When processing <entity>:
async def process_entity(entity_data):
    entity_id = generate_id(entity_data['type'], entity_data['label'])
    
    # Check if similar entity exists
    existing = await find_similar_entity(
        type=entity_data['type'],
        label=entity_data['label'],
        parent=entity_data['parent']
    )
    
    if existing:
        # Update existing entity with new info
        await update_node(existing.id, entity_data)
        return existing.id
    else:
        # Create new entity
        await create_node(entity_id, entity_data)
        await create_edge(entity_id, entity_data['parent'], CHILD_OF)
        return entity_id

# When processing <memory>:
async def process_memory(memory_data):
    belongs_to = memory_data['belongs_to']
    
    # Check if target exists
    if await node_exists(belongs_to):
        # Link to existing node
        await create_memory_linked_to(belongs_to)
    else:
        # Target doesn't exist - this shouldn't happen if 
        # <entity> is processed before <memory>
        # Fallback: link to user
        await create_memory_linked_to('user_default')
        log.warning(f"Memory target {belongs_to} not found, linked to user")
```

#### Processing Order Matters

```
<entity> blocks → processed FIRST (create/update nodes)
<memory> blocks → processed SECOND (link to nodes created above)
<update> blocks → processed THIRD (modify existing nodes)
```

This ensures memories always have valid targets to link to.

#### Example: Organic Graph Growth

**Turn 1: Onboarding**
```
User: "I'm Sivaram, I go by Shibu, I work at Synopsys"

Graph after:
┌──────────┐
│  User    │
│ (Shibu)  │
└────┬─────┘
     │
     ▼
┌──────────┐
│  Domain  │
│  (Work)  │
│ Synopsys │
└──────────┘
```

**Turn 2: Family mention**
```
User: "My mom's name is Velammal, birthday is March 22"

Graph after:
┌──────────┐
│  User    │
│ (Shibu)  │
└────┬─────┘
     │
     ├──────────────┐
     ▼              ▼
┌──────────┐  ┌──────────┐
│  Domain  │  │  Person  │
│  (Work)  │  │  (Mom)   │
└──────────┘  └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │  Memory  │
              │ Bday 3/22│
              └──────────┘
```

**Turn 3: Work detail**
```
User: "I'm working on a cool project at work called Apollo"

Graph after:
┌──────────┐
│  User    │
│ (Shibu)  │
└────┬─────┘
     │
     ├──────────────┬──────────────┐
     ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Domain  │  │  Person  │  │ Project  │
│  (Work)  │  │  (Mom)   │  │ (Apollo) │
└────┬─────┘  └────┬─────┘  └──────────┘
     │              │              │
     │              ▼              │
     │        ┌──────────┐        │
     │        │  Memory  │        │
     │        │ Bday 3/22│        │
     │        └──────────┘        │
     │                            │
     └────────────┬───────────────┘
                  ▼
           (both linked to User
            as children, Project
            also related to Work domain)
```

#### The Fuzziness Principle (Unchanged)# PROJECT - Things user is working on
project:
  status: string                 # "active", "paused", "completed"
  progress: string | number      # Fuzzy or specific

# GOAL - Measurable objectives
goal:
  status: string                 # "active", "in_progress", "completed"
  progress: number | null        # 0-100 if measurable
  target: string | null          # "Run 5K 3x/week"

# MEMORY - Permanent records from conversations
memory:
  content: string                # The actual memory text
  memory_type: string            # "fact", "observation", "episode", "preference"
  emotional_weight: float        # 0-1, how significant (breakthroughs = high)
  source_channel: string         # "cli", "web", "telegram"
  access_count: int              # How often retrieved (relevance signal)

# TASK - Actionable items PAAW can execute
task:
  status: string                 # "pending", "in_progress", "completed", "failed"
  priority: string               # "high", "medium", "low"
  due_date: datetime | null
  assigned_by: string            # "user" or "paaw" (proactive)
  result: string | null          # What happened when executed

# EVENT - Calendar events, milestones
event:
  date: datetime
  recurring: string | null       # "yearly", "weekly", null
  reminder_before: string | null # "1 week", "1 day"
```

#### Edge Types

```yaml
# Structural (hierarchy)
HAS_DOMAIN:      User → Domain
CHILD_OF:        Project → Domain (hierarchical nesting)

# Belonging (memories, tasks, events connect to multiple nodes)
BELONGS_TO:      Memory → Node (can have MULTIPLE!)
                 Task → Node
                 Event → Node

# Relationships
KNOWS:           User → Person
AFFECTS:         Node → Node (inferred: "Raj frustration → Go Indie motivation")
BLOCKED_BY:      Goal → Node (dependencies)

# Temporal
PRECEDED_BY:     Event → Event
COMPLETED_WITH:  Task → Memory (task result becomes memory)
```

#### Memory Retrieval (No Decay, Smart Retrieval)

**Memories are NEVER deleted.** Retrieval is based on RELEVANCE, not arbitrary decay.

```python
# Retrieval scoring
relevance_score = (
    semantic_match(query, memory.content) * 0.4 +   # How related to current topic
    recency_boost(memory.last_accessed) * 0.2 +     # Recent = slight boost
    memory.emotional_weight * 0.25 +                 # Breakthroughs always surface
    memory.access_count * 0.05 +                     # Frequently relevant = boost
    connection_count(memory) * 0.1                   # Well-connected = important
)

# Old memories STILL surface if relevant
# "Worked out in 2020" surfaces when discussing fitness in 2026
```

#### Apache AGE Cypher Examples

```cypher
-- Create a memory that BELONGS_TO multiple nodes
CREATE (m:Memory {
    id: 'mem_001',
    content: 'Raj changed requirements again, worked till 3am',
    memory_type: 'episode',
    emotional_weight: 0.7,
    access_count: 0,
    source_channel: 'cli',
    created_at: datetime()
})
WITH m
MATCH (raj:Person {label: 'Raj'})
MATCH (work:Domain {label: 'Work'})
CREATE (m)-[:BELONGS_TO]->(raj)
CREATE (m)-[:BELONGS_TO]->(work);

-- Create a task linked to person and event
CREATE (t:Task {
    id: 'task_001',
    label: 'Book Ooty hotel for anniversary',
    status: 'pending',
    priority: 'high',
    due_date: date('2026-04-10'),
    assigned_by: 'user'
})
WITH t
MATCH (priya:Person {label: 'Priya'})
MATCH (anniv:Event {label: 'Anniversary'})
CREATE (t)-[:BELONGS_TO]->(priya)
CREATE (t)-[:BELONGS_TO]->(anniv);

-- Get all memories for a node (by relevance, not decay)
MATCH (n {id: $node_id})<-[:BELONGS_TO]-(m:Memory)
RETURN m
ORDER BY 
    m.emotional_weight DESC,
    m.access_count DESC,
    m.last_accessed DESC
LIMIT 10;

-- Get pending tasks with their context
MATCH (t:Task {status: 'pending'})-[:BELONGS_TO]->(related)
RETURN t, collect(related.label) as context
ORDER BY t.priority DESC, t.due_date ASC;

-- Find cross-domain connections
MATCH (m:Memory)-[:BELONGS_TO]->(n1)
MATCH (m)-[:BELONGS_TO]->(n2)
WHERE n1 <> n2
RETURN m.content, n1.label, n2.label;

-- Task completion creates memory
MATCH (t:Task {id: $task_id})
SET t.status = 'completed', t.result = $result
CREATE (m:Memory {
    id: randomUUID(),
    content: $result,
    memory_type: 'episode',
    emotional_weight: 0.5,
    created_at: datetime()
})
WITH t, m
MATCH (t)-[:BELONGS_TO]->(related)
CREATE (m)-[:BELONGS_TO]->(related)
CREATE (t)-[:COMPLETED_WITH]->(m);
```
    CREATE (u)-[:KNOWS {relationship: 'wife', since: '2018'}]->(p:Person {
        id: 'person_priya',
        label: 'Priya',
        context: 'Sivaram wife, doctor at Apollo',
        key_facts: ['Very supportive', 'Night shifts'],
        occupation: 'Doctor'
    })
    RETURN p
$$) AS (p agtype);

-- Create cross-connection (Priya mentioned in PAAW conversation)
SELECT * FROM cypher('paaw', $$
    MATCH (p:Person {id: 'person_priya'})
    MATCH (m:Memory {id: 'mem_123'})
    CREATE (p)-[:MENTIONED_IN {context: 'User said Priya supports PAAW project'}]->(m)
$$) AS (result agtype);

-- Load context for a node (get node + children + memories)
SELECT * FROM cypher('paaw', $$
    MATCH (n {id: 'domain_work'})
    OPTIONAL MATCH (n)-[:HAS_CHILD]->(child)
    OPTIONAL MATCH (n)<-[:BELONGS_TO]-(mem:Memory)
    RETURN n, collect(DISTINCT child) AS children, collect(DISTINCT mem) AS memories
$$) AS (n agtype, children agtype, memories agtype);

-- Traverse up to get parent context
SELECT * FROM cypher('paaw', $$
    MATCH path = (n {id: 'project_paaw'})-[:CHILD_OF*1..3]->(ancestor)
    RETURN [node IN nodes(path) | node.context] AS context_chain
$$) AS (context_chain agtype);

-- Find all connections to a person
SELECT * FROM cypher('paaw', $$
    MATCH (p:Person {id: 'person_priya'})-[r]-(connected)
    RETURN type(r) AS relationship, connected.label AS node, r.context AS context
$$) AS (relationship agtype, node agtype, context agtype);
```

---

### 4. Channels

How users communicate with PAAW. All channels normalize to a unified message format.

```
┌─────────────────────────────────────────────────────────┐
│                      CHANNELS                            │
│                                                          │
│     User                                                 │
│      │                                                   │
│      ├───── Web UI (localhost:8080) ──────────┐         │
│      │         WebSocket                       │         │
│      │                                         │         │
│      ├───── CLI (terminal) ───────────────────┤         │
│      │         stdin/stdout                    │         │
│      │                                         │         │
│      ├───── Telegram ─────────────────────────┤         │
│      │         Bot API (PAAW polls)             │         │
│      │                                         │         │
│      ├───── Slack ────────────────────────────┤         │
│      │         Socket Mode (WebSocket out)     │         │
│      │                                         │         │
│      ├───── WhatsApp ─────────────────────────┤         │
│      │         Web Bridge (outbound)           │         │
│      │                                         │         │
│      └───── Discord ──────────────────────────┤         │
│                Bot (WebSocket out)             │         │
│                                                │         │
│                                                ▼         │
│  ┌─────────────────────────────────────────────────┐    │
│  │                    GATEWAY                       │    │
│  │                                                  │    │
│  │  Normalizes all messages to:                    │    │
│  │                                                  │    │
│  │  UnifiedMessage {                               │    │
│  │    id: string                                   │    │
│  │    channel: "web" | "cli" | "telegram" | ...    │    │
│  │    user_id: string                              │    │
│  │    content: string                              │    │
│  │    attachments: list                            │    │
│  │    reply_to: string | null                      │    │
│  │    timestamp: datetime                          │    │
│  │    metadata: dict                               │    │
│  │  }                                              │    │
│  │                                                  │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                                │
│                         ▼                                │
│                   PAAW BRAIN                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### Channel Connection Types

| Channel | Direction | Auth | How it works |
|---------|-----------|------|--------------|
| **Web UI** | Local | None (localhost) | FastAPI serves React app, WebSocket for chat |
| **CLI** | Local | None | Typer CLI, connects to PAAW via HTTP |
| **Telegram** | PAAW → Out | Bot Token | Long polling, PAAW asks Telegram for new messages |
| **Slack** | PAAW → Out | App Token | Socket Mode, PAAW opens WebSocket to Slack |
| **WhatsApp** | PAAW → Out | QR Scan | WhatsApp Web bridge, PAAW runs headless client |
| **Discord** | PAAW → Out | Bot Token | Discord.py, PAAW opens WebSocket to Discord |

**All connections are OUTBOUND. No public IP needed. No webhooks. Works behind any firewall.**

---

### 5. Tools (MCP)

External capabilities via Model Context Protocol.

```
┌─────────────────────────────────────────────────────────┐
│                      TOOL LAYER                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │                 TOOL MANAGER                      │   │
│  │                                                   │   │
│  │  • Discovers available MCP servers               │   │
│  │  • Permission check before every call            │   │
│  │  • Audit logs every tool usage                   │   │
│  │  • Remembers tool preferences per goal           │   │
│  └──────────────────────┬───────────────────────────┘   │
│                         │                                │
│         ┌───────────────┼───────────────┐               │
│         │               │               │               │
│         ▼               ▼               ▼               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │
│  │  BUILT-IN  │  │   LOCAL    │  │    REMOTE      │    │
│  │    TOOLS   │  │    MCP     │  │      MCP       │    │
│  │            │  │  SERVERS   │  │    SERVERS     │    │
│  │ • Memory   │  │            │  │                │    │
│  │   (graph)  │  │ • Custom   │  │ • GitHub       │    │
│  │ • Web      │  │   servers  │  │ • Google       │    │
│  │   Search   │  │   you      │  │ • Any public   │    │
│  │ • Notes    │  │   create   │  │   MCP server   │    │
│  └────────────┘  └────────────┘  └────────────────┘    │
│                                                          │
│  ALL TOOLS USE MCP PROTOCOL                             │
│  Adding a tool = add config, zero code changes          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### Tool Configuration

```yaml
# configs/tools.yaml

tools:
  # Built-in (shipped with PAAW)
  - name: memory
    type: builtin
    description: "Read/write to the goal-based memory graph"
    
  - name: web_search
    type: builtin
    description: "Search the web using DuckDuckGo"
    
  # Local MCP servers
  - name: github
    type: mcp
    command: "npx @modelcontextprotocol/server-github"
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
      
  # Remote MCP servers
  - name: calendar
    type: mcp
    url: "http://localhost:3001/mcp"
```

---

### 6. System Services

Background services that keep PAAW healthy.

#### Heartbeat

```python
class Heartbeat:
    """
    Proves PAAW is alive. Runs every 30 seconds.
    """
    
    async def check(self):
        health = {
            "db": await self.check_db(),
            "valkey": await self.check_valkey(), 
            "llm": await self.check_llm(),
            "memory": self.memory_stats(),
            "channels": self.channel_health(),
            "system": self.system_resources()
        }
        
        if not all(health.values()):
            await self.handle_unhealthy(health)
        
        await self.log_health(health)
```

#### Scheduler

```python
class Scheduler:
    """
    Cron-like scheduled tasks.
    """
    
    tasks = [
        # Context maintenance (NO DECAY!)
        ("0 3 * * *", "context.consolidate"),   # Daily 3am: update node contexts
        
        # Proactive tasks
        ("* * * * *", "tasks.check_due"),       # Every minute: check due tasks
        ("0 9 * * *", "checkin.morning"),       # Daily 9am: morning check-in (if enabled)
        ("0 0 * * *", "events.check_upcoming"), # Daily: check upcoming events
    ]
```

#### Audit Log

```python
class Audit:
    """
    Immutable log of every action.
    """
    
    async def log(self, action: Action):
        # Write to append-only log
        await self.db.execute("""
            INSERT INTO audit_log (
                timestamp, action_type, input, output,
                tool_used, model_used, goal_id, 
                channel, user_id, status, duration_ms
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """, ...)
        
        # Also write to file (backup)
        self.file.write(json.dumps(action) + "\n")
```

---

### 7. Web UI & CLI

#### Web UI

```
┌────────────────────────────────────────────────────────────┐
│  PAAW Web UI (localhost:8080)                                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HEADER                                              │   │
│  │  🐾 PAAW    [Chat] [Graph] [Settings]    Status: 🟢   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────┐  ┌───────────────────────────┐   │
│  │      CHAT VIEW       │  │       GRAPH VIEW          │   │
│  │                      │  │                           │   │
│  │  ┌────────────────┐  │  │     ┌──────┐             │   │
│  │  │ PAAW: Hey! How  │  │  │     │ User │             │   │
│  │  │ can I help?    │  │  │     └──┬───┘             │   │
│  │  └────────────────┘  │  │   ┌────┴────┐            │   │
│  │                      │  │   │         │            │   │
│  │  ┌────────────────┐  │  │ ┌─┴──┐   ┌──┴─┐         │   │
│  │  │ You: What's    │  │  │ │Work│   │Life│         │   │
│  │  │ up today?      │  │  │ └─┬──┘   └────┘         │   │
│  │  └────────────────┘  │  │   │                      │   │
│  │                      │  │ ┌─┴──┐                   │   │
│  │  ┌────────────────┐  │  │ │Rust│ ← click to       │   │
│  │  │ PAAW: You have  │  │  │ └────┘   explore        │   │
│  │  │ 3 meetings...  │  │  │                         │   │
│  │  └────────────────┘  │  │  [Zoom] [Filter]        │   │
│  │                      │  │                         │   │
│  │  [Type message...]   │  │  DETAILS PANEL          │   │
│  │                      │  │  (when node clicked)    │   │
│  └──────────────────────┘  └───────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  STATUS BAR: Heartbeat ✓ │ Nodes: 156 │ Uptime: 3d  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

#### CLI

```bash
# Start PAAW (Docker)
$ docker compose up -d

# Chat
$ paaw chat
🐾 PAAW is ready! Type your message (Ctrl+C to exit)
You: What's my schedule?
PAAW: You have 3 meetings today...

# Status
$ paaw status
┌─────────────────────────────┐
│ PAAW Status                  │
├─────────────────────────────┤
│ Heartbeat: ✓ Healthy        │
│ Uptime: 3 days, 4 hours     │
│ Memory nodes: 156           │
│ Goals: 12 active            │
└─────────────────────────────┘

# View graph
$ paaw graph
Opening http://localhost:8080/graph ...

# ASCII graph
$ paaw graph --ascii
Sivaram
├── Work
│   ├── Tasks (3 pending)
│   └── Meetings (2 today)
├── Health
│   └── Run 5K (60%)
└── Learning
    └── Rust (40%)

# Show mental model
$ paaw model
Opening your mental model...
```

---

## Data Models

### Unified Message

```python
@dataclass
class UnifiedMessage:
    id: str
    channel: str          # "web", "telegram", "slack", etc.
    user_id: str
    content: str
    attachments: list[Attachment]
    reply_to: str | None  # For threaded conversations
    timestamp: datetime
    metadata: dict        # Channel-specific data
```

### Graph Node (Base)

```python
@dataclass
class GraphNode:
    id: str
    type: str             # "user", "domain", "person", "project", "goal", "memory"
    label: str            # Human-readable name
    path: str | None      # Hierarchical path: "work/projects/paaw"
    
    # The soul (LLM-maintained)
    story: str | None     # Origin story, why it matters
    context: str          # Current understanding
    key_facts: list[str]  # Important learned facts
    
    # Flexible attributes (type-specific)
    attributes: dict      # Whatever makes sense for this node
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_accessed: datetime
```

### Memory Node

```python
@dataclass
class MemoryNode(GraphNode):
    type: str = "memory"
    
    # Memory-specific
    content: str          # The actual memory text
    memory_type: str      # "fact", "observation", "preference", "episode"
    strength: float       # 0-1, decays over time
    
    # Source
    source_channel: str
    source_message_id: str
    source_timestamp: datetime
    
    # Optional embedding for semantic search
    embedding: list[float] | None
    
    # What nodes this memory belongs to
    belongs_to: list[str]  # Node IDs
```

### Task

```python
@dataclass  
class Task:
    id: str
    description: str      # Plain English
    node_id: str | None   # Which node this relates to
    
    # Execution
    action: str           # What to do
    params: dict          # Action parameters
    
    # Self-healing
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Result
    status: str = "pending"
    result: Any = None
    error: str | None = None
    attempts: int = 0
```

---

## Context Management

### Memory as a Tool

Memory access is a **structured tool**, not raw DB access. PAAW follows strict protocols.

```yaml
# Mental Model Tool Protocol

operations:
  
  # READING
  get_user_context:
    description: "Get user's overall context for system prompt"
    returns:
      identity: dict
      personality: dict
      key_facts: list[string]
  
  get_node_context:
    description: "Load context for a specific node"
    params:
      node_id: required
      include_ancestors: bool (default: true)
      include_memories: bool (default: true)
      max_tokens: int (default: 2000)
    returns:
      node: GraphNode
      ancestors: list[{context, key_facts}]
      recent_memories: list[Memory]
  
  route_message:
    description: "Classify message to relevant nodes"
    params:
      message: required
    returns:
      nodes: list[{node_id, relevance}]
      suggested_new_node: dict | null
  
  search_memories:
    description: "Search memories (keyword or semantic)"
    params:
      query: required
      scope_node_id: optional
      limit: int (default: 10)
    returns:
      memories: list[Memory]
  
  # WRITING
  add_memory:
    description: "Store a new memory"
    params:
      content: required
      memory_type: required (fact|observation|preference|episode)
      belongs_to: list[node_id]
      source_channel: required
    returns:
      memory_id: string
  
  update_node:
    description: "Update a node's context/facts"
    params:
      node_id: required
      context: optional
      key_facts: optional
      attributes: optional
    returns:
      success: bool
  
  create_node:
    description: "Create a new node in the graph"
    params:
      type: required
      label: required
      parent_id: optional
      initial_context: optional
    returns:
      node_id: string
  
  create_edge:
    description: "Create connection between nodes"
    params:
      from_node: required
      to_node: required
      edge_type: required
      context: optional
    returns:
      success: bool
```

### Context Loading Strategy

```
User: "How's the PAAW memory system going?"
            │
            ▼
┌─────────────────────────────────────┐
│ 1. ROUTE TO NODE(S)                 │
│    LLM: "This relates to PAAW →     │
│          Memory System"             │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 2. LOAD NODE CONTEXT                │
│                                     │
│    Memory System node:              │
│    • context (current understanding)│
│    • key_facts                      │
│    • recent memories (last 5)       │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 3. LOAD ANCESTORS (light)           │
│                                     │
│    PAAW → Work → User               │
│    Just context + key_facts each    │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ 4. ASSEMBLE PROMPT                  │
│                                     │
│    User personality + node context  │
│    + ancestors + memories           │
│                                     │
│    ~3000 tokens (focused!)          │
└─────────────────────────────────────┘
```

### Memory Maintenance (Background Tasks)

**Key Principle: NO DECAY, NO DELETION.** Memories are permanent. We only:
1. Update node contexts (consolidation)
2. Update access counts (for relevance scoring)

```python
# Daily: Consolidate node contexts
async def consolidate_contexts():
    """Use LLM to update node contexts from recent memories."""
    
    for node in await get_active_nodes():
        recent_memories = await get_recent_memories(node.id, days=7)
        
        if recent_memories:
            # Ask LLM to update the node's context
            updated = await llm.update_context(
                current_context=node.context,
                current_facts=node.key_facts,
                new_memories=recent_memories
            )
            
            await update_node(node.id, 
                context=updated.context,
                key_facts=updated.key_facts
            )

# On access: Update memory access stats
async def on_memory_accessed(memory_id: str):
    """Track when memories are retrieved (for relevance scoring)."""
    await db.execute("""
        SELECT * FROM cypher('paaw', $$
            MATCH (m:Memory {id: $memory_id})
            SET m.last_accessed = datetime(),
                m.access_count = m.access_count + 1
        $$) AS (result agtype)
    """, memory_id=memory_id)

# Weekly: Check for tasks due soon
async def check_upcoming_tasks():
    """Proactively remind about upcoming tasks/events."""
    tasks = await db.execute("""
        SELECT * FROM cypher('paaw', $$
            MATCH (t:Task)
            WHERE t.status = 'pending' 
            AND t.due_date <= datetime() + duration('P7D')
            RETURN t
        $$) AS (t agtype)
    """)
    
    for task in tasks:
        await notify_user(f"Upcoming: {task.label}")
```

---

## Onboarding Flow

### Philosophy: "Tell Me About Yourself"

Instead of asking multiple questions like a form, PAAW uses a single open-ended prompt:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FIRST LAUNCH                                          │
│                                                                                 │
│  🐾 "Hey! I'm PAAW — your Personal AI Assistant that Works.                     │
│                                                                                 │
│      I'm different from other AI assistants. I actually remember you.           │
│      I build a mental model of who you are, what matters to you,                │
│      and how I can best help.                                                  │
│                                                                                 │
│      To get started, just tell me about yourself — who you are,                │
│      what you're working on, what's on your mind. I'll figure out              │
│      the rest from there.                                                      │
│                                                                                 │
│      Everything stays on YOUR machine. Privacy-first. 🔒"                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Example Onboarding

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  User: "I'm Siva, software dev in Chennai. Work at TechCorp but honestly       │
│         not loving it — my boss Raj keeps changing requirements last minute.   │
│         On the side I'm building PAAW, that's you! My wife Priya is a doctor,  │
│         she's super supportive. I should really exercise more but keep         │
│         putting it off. Oh and I'm a night owl, code best after 10pm."         │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ PAAW EXTRACTS (via LLM):                                                 │   │
│  │                                                                          │   │
│  │ User: name="Siva", location="Chennai", pattern="night owl"               │   │
│  │ Domains: Work, People, Health                                            │   │
│  │ People: Raj (boss, difficult), Priya (wife, doctor, supportive)          │   │
│  │ Projects: PAAW (side project, active)                                    │   │
│  │ Observations: "Not loving TechCorp", "Should exercise more"              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  PAAW: "Got it, Siva! Here's what I understood:                                │
│                                                                                 │
│         📍 Chennai, night owl (best after 10pm)                                │
│         💼 Software dev at TechCorp — not loving it, boss Raj is tricky        │
│         🔧 Building PAAW on the side (hey, that's me!)                         │
│         👥 Wife Priya is a doctor, super supportive                            │
│         🏃 Want to exercise more (I'll remind you... gently)                   │
│                                                                                 │
│         Anything I missed or got wrong?"                                       │
│                                                                                 │
│  User: "Nope, that's pretty much it!"                                          │
│                                                                                 │
│  PAAW: "Perfect. I'll keep learning as we chat. What can I help with today?"   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Why This Works Better

| Old Approach (Questions) | New Approach (Tell Me) |
|--------------------------|------------------------|
| Feels like a form | Feels like meeting a friend |
| User waits for each question | User shares what's on their mind |
| Fixed structure | Natural, flexible |
| 2 minutes of Q&A | 30 seconds of sharing |

---

## Conversation Flow (Optimized)

### The Key Insight: Root Nodes Always in Prompt

Instead of routing then loading context, we:
1. Always include root-level nodes in the system prompt
2. Use fast keyword search to find specific nodes
3. Ask LLM to tag relevant nodes at end of response
4. Load detailed context for NEXT turn based on tags

### System Prompt Structure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      SYSTEM PROMPT (every message)                              │
│                                                                                 │
│  You are PAAW, a personal AI assistant for {user.name}.                        │
│                                                                                 │
│  USER PROFILE:                                                                  │
│  Location: {Chennai} | Languages: {Tamil, English} | Style: {Direct, no fluff} │
│  Pattern: {Night owl, peaks after 10pm}                                        │
│                                                                                 │
│  MENTAL MODEL (root nodes):                                                     │
│  ├── 👥 People: Priya (wife, doctor), Raj (boss, difficult)                    │
│  ├── 💼 Work: TechCorp (job, unhappy), PAAW (project, active)                  │
│  ├── 🏃 Health: Running goal (in progress)                                     │
│  ├── 💰 Finance: Indie goal (saving up)                                        │
│  └── 📋 Tasks: 2 pending                                                       │
│                                                                                 │
│  {If keyword search found specific nodes, include their details here}          │
│                                                                                 │
│  IMPORTANT: At the end of your response, output relevant node IDs:             │
│  <nodes>comma,separated,node_ids</nodes>                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        OPTIMIZED CONVERSATION FLOW                              │
│                                                                                 │
│  USER: "Raj is being difficult again"                                          │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  STEP 1: KEYWORD SEARCH (no LLM, <10ms)                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  keywords = extract(message) → ["raj", "difficult"]                            │
│                                                                                 │
│  matched = search_nodes(keywords)                                              │
│  → person_raj (label match, score: 10)                                         │
│  → domain_work (context contains "raj", score: 5)                              │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  STEP 2: BUILD PROMPT                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  System: {user profile + root nodes}                                           │
│                                                                                 │
│  Matched context:                                                              │
│    Raj: "Difficult boss at TechCorp. Pattern of changing reqs mid-sprint."    │
│    Recent memories: ["Changed reqs last week", "Worked till 3am"]              │
│                                                                                 │
│  User: "Raj is being difficult again"                                          │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  STEP 3: LLM RESPONSE                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  "The mid-sprint changes again? 😤 This is becoming a pattern.                 │
│   What did he change this time?"                                               │
│                                                                                 │
│  <nodes>person_raj,domain_work,goal_indie</nodes>                              │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  STEP 4: POST-PROCESS (async, after response sent)                             │
│  ─────────────────────────────────────────────────────────────────────────────  │
│                                                                                 │
│  1. Parse nodes: [person_raj, domain_work, goal_indie]                         │
│     → LLM connected Raj frustration to indie goal!                             │
│                                                                                 │
│  2. Load goal_indie context for NEXT turn                                      │
│                                                                                 │
│  3. Create memory: "Raj being difficult again" → [person_raj, domain_work]     │
│                                                                                 │
│  4. Update access_count for person_raj, domain_work                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Updating the Mental Model (Corrections & Changes)

The mental model must be **adaptable** - facts change, people move, situations evolve.

#### Types of Updates

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MENTAL MODEL UPDATES                                    │
│                                                                                 │
│  1. CORRECTION - User corrects wrong info                                      │
│     "Actually, Raj isn't my boss anymore - I quit last week"                   │
│     → Update person_raj context                                                 │
│     → Maybe update domain_work too                                             │
│     → Store as memory with type "correction"                                    │
│                                                                                 │
│  2. FACTUAL UPDATE - New information                                           │
│     "We moved to Bangalore"                                                    │
│     → Update user.location                                                     │
│     → Store as memory                                                          │
│                                                                                 │
│  3. STATUS CHANGE - State transitions                                          │
│     "PAAW is done! I shipped it"                                               │
│     → Update project_paaw.status = "completed"                                 │
│     → Create memory (milestone)                                                │
│                                                                                 │
│  4. RELATIONSHIP CHANGE - Connections evolve                                   │
│     "Priya and I got divorced"                                                 │
│     → Update edge person_priya → user (type: "ex-wife")                        │
│     → Potentially archive or reduce prominence                                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Detection in LLM Response

The LLM detects updates and outputs them in the response:

```
System Prompt Addition:
────────────────────────
When the user provides new information that UPDATES existing facts, output:
<update>
  node_id: the node to update
  field: which field (context, key_facts, attributes, status)
  old_value: what PAAW currently thinks (for confirmation)
  new_value: the corrected/updated value
  reason: why (correction, new info, status change)
</update>

You can output multiple <update> blocks if needed.
```

#### Example Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  USER: "Oh btw I quit TechCorp last week. Going full-time on PAAW!"            │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  CURRENT MENTAL MODEL:                                                         │
│  • domain_work.context: "Works at TechCorp as senior dev. Unhappy."            │
│  • project_paaw.status: "active" (side project)                                │
│  • goal_indie.status: "in_progress"                                            │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  LLM RESPONSE:                                                                 │
│                                                                                 │
│  "Wait, you actually did it?! 🎉 That's HUGE! After all those late nights      │
│   and Raj's mid-sprint changes... you finally pulled the trigger.              │
│   How does it feel? And how's the runway looking?"                             │
│                                                                                 │
│  <update>                                                                      │
│    node_id: domain_work                                                        │
│    field: context                                                              │
│    old_value: "Works at TechCorp as senior dev. Unhappy."                      │
│    new_value: "Left TechCorp (quit). Now full-time indie."                     │
│    reason: status_change                                                       │
│  </update>                                                                     │
│  <update>                                                                      │
│    node_id: project_paaw                                                       │
│    field: attributes.priority                                                  │
│    old_value: "side_project"                                                   │
│    new_value: "main_focus"                                                     │
│    reason: status_change                                                       │
│  </update>                                                                     │
│  <update>                                                                      │
│    node_id: goal_indie                                                         │
│    field: status                                                               │
│    old_value: "in_progress"                                                    │
│    new_value: "achieved"                                                       │
│    reason: milestone                                                           │
│  </update>                                                                     │
│                                                                                 │
│  <nodes>domain_work,project_paaw,goal_indie,person_raj</nodes>                 │
│                                                                                 │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  POST-PROCESS:                                                                 │
│                                                                                 │
│  1. Parse <update> blocks                                                      │
│  2. Apply updates to graph                                                     │
│  3. Create memory: "Quit TechCorp, going full-time on PAAW" (milestone)        │
│  4. Log update history (for debugging/audit)                                   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### Update History (Audit Trail)

We track all updates for transparency:

```python
# Updates table (PostgreSQL, not graph)
updates:
  id: uuid
  node_id: string
  field: string
  old_value: jsonb
  new_value: jsonb
  reason: string  # correction, new_info, status_change, user_edit
  source: string  # conversation, manual, consolidation
  created_at: datetime
  
# Query: "What changed about this node?"
SELECT * FROM updates WHERE node_id = 'domain_work' ORDER BY created_at DESC;

# Query: "What corrections has user made?"
SELECT * FROM updates WHERE reason = 'correction' ORDER BY created_at DESC;
```

#### User-Initiated Corrections

User can explicitly correct PAAW:

```
User: "PAAW, that's wrong - I never worked at Google"

PAAW: "Oh sorry about that! Let me fix that. I had:
       'Worked at Google 2018-2020'
       
       What's the correct info?"

User: "I worked at Microsoft, not Google"

PAAW: "Got it! Updated your work history. Anything else I got wrong?"
```

The key principles:
1. **Detect updates automatically** - LLM recognizes when info changes
2. **Confirm before major changes** - For significant updates, verify
3. **Keep audit trail** - Track what changed and why
4. **Never lose old info** - Updates table preserves history
5. **Allow explicit corrections** - User can always say "that's wrong"

### Fuzzy Node Search

PostgreSQL + AGE supports fuzzy/probabilistic search:

```python
async def search_nodes(keywords: list[str], limit: int = 10) -> list[Node]:
    """
    Search nodes with fuzzy matching. Returns ranked results.
    """
    # Build patterns for ILIKE (case-insensitive substring match)
    patterns = [f"%{kw}%" for kw in keywords]
    
    # Build tsquery for full-text search
    tsquery = " | ".join(keywords)  # "raj | difficult"
    
    results = await db.fetch("""
        WITH label_matches AS (
            -- Exact/substring match on label (highest priority)
            SELECT *, 10 as score FROM nodes 
            WHERE label ILIKE ANY($1)
        ),
        context_matches AS (
            -- Full-text search on context
            SELECT *, ts_rank(search_vector, to_tsquery($2)) * 5 as score
            FROM nodes
            WHERE search_vector @@ to_tsquery($2)
        ),
        key_fact_matches AS (
            -- Search in key_facts array
            SELECT *, 3 as score FROM nodes
            WHERE EXISTS (
                SELECT 1 FROM unnest(key_facts) fact 
                WHERE fact ILIKE ANY($1)
            )
        )
        
        SELECT id, label, type, context, key_facts, SUM(score) as relevance
        FROM (
            SELECT * FROM label_matches
            UNION ALL SELECT * FROM context_matches  
            UNION ALL SELECT * FROM key_fact_matches
        ) combined
        GROUP BY id, label, type, context, key_facts
        ORDER BY relevance DESC
        LIMIT $3
    """, patterns, tsquery, limit)
    
    return results

# Examples:
# "raj" → finds person_raj (label), domain_work (context mentions raj)
# "wife" → finds person_priya (context: "wife")
# "running progress" → finds goal_running (label + context)
```

### Why This Is Better

| Aspect | Before | After |
|--------|--------|-------|
| Routing | LLM call (~500ms) | Keyword search (<10ms) |
| Context loading | Before response | After response (for next turn) |
| LLM calls per message | 2-4 | 1 |
| Latency | ~2-3 seconds | ~1 second |
| Cost | $$$$ | $ |

┌─────────────────────────────────────────────────────────────────────────────────┐
│  THE MENTAL MODEL (Show what PAAW learned)                                      │
│  ═════════════════════════════════════════                                      │
│                                                                                 │
│  PAAW: "Alright Siva, here's my starting picture of you:                       │
│                                                                                 │
│         ┌─────────────────────────────────┐                                    │
│         │ 📍 Siva                          │                                    │
│         │ Chennai | Tamil + English       │                                    │
│         │ Night owl | Direct communicator │                                    │
│         ├─────────────────────────────────┤                                    │
│         │ 💼 Work: Software Dev            │                                    │
│         │    └─ Project: PAAW (active)    │                                    │
│         │ 🏃 Health: Wants more exercise   │                                    │
│         └─────────────────────────────────┘                                    │
│                                                                                 │
│         This will grow as we talk. Ready to get started?"                      │
│                                                                                 │
│  [Show me my graph] [Let's chat!]                                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### What PAAW Learns From This

```python
# After onboarding, the graph has:

User Node:
{
    "id": "user_siva",
    "type": "user",
    "label": "Siva",
    "identity": {
        "name": "Sivaram",
        "preferred_name": "Siva",
        "location": "Chennai, India",
        "timezone": "Asia/Kolkata",
        "languages": ["Tamil", "English"]
    },
    "personality": {
        "communication_style": "direct, no fluff",
        "active_hours": "night owl, peaks after 10pm"
    },
    "context": "Software dev in Chennai building PAAW. Values directness, 
                hates when AI forgets. Night owl.",
    "key_facts": [
        "Building PAAW - wants AI that remembers",
        "Frustrated by AI amnesia",
        "Prefers direct communication",
        "Night owl - productive after 10pm"
    ]
}

Domain: Work
{
    "id": "domain_work",
    "type": "domain",
    "label": "Work",
    "context": "Software developer, working on side project PAAW"
}

Project: PAAW  
{
    "id": "project_paaw",
    "type": "project",
    "label": "PAAW",
    "context": "Personal AI assistant project. Motivated by frustration 
                with AI assistants that forget everything.",
    "attributes": {
        "status": "active"
    }
}

Domain: Health
{
    "id": "domain_health", 
    "type": "domain",
    "label": "Health",
    "context": "Wants to exercise more, keeps procrastinating"
}

Goal: Exercise
{
    "id": "goal_exercise",
    "type": "goal",
    "label": "Exercise More",
    "context": "User mentioned wanting more time for exercise",
    "attributes": {
        "status": "not_started"
    }
}
```

### Continuous Learning (Post-Onboarding)

After onboarding, PAAW keeps learning:

```
Week 1:
- User mentions "wife" → PAAW creates People/Family/Wife node
- User vents about boss → Work context updated, Person node created

Week 2:  
- User asks for restaurant recommendations → Preferences/Food discovered
- User mentions "Priya" (wife's name) → Wife node updated

Month 1:
- PAAW notices user messages get shorter when stressed
- PAAW learns Tuesday evenings are sacred (gaming with friends)
- Career frustration pattern detected → updates Work context

Month 3:
- Deep understanding of user's communication patterns
- Can predict topics from message tone
- Proactively helpful: "You usually forget your 10am meeting on Mondays..."
```

---

## Security Model

### Container as Sandbox

PAAW runs in a Docker container with minimal permissions:

```yaml
# docker-compose.yaml

services:
  paaw:
    security_opt:
      - no-new-privileges:true    # Can't escalate
    read_only: true               # Read-only filesystem  
    tmpfs:
      - /tmp                      # Only /tmp writable
    mem_limit: 512m               # Memory limit
    cpus: 1.0                     # CPU limit
    
    # No access to:
    # - Host filesystem
    # - Docker socket
    # - Privileged operations
```

### Audit Trail

Every action is logged:

```python
AuditEntry:
  timestamp: datetime
  action_type: str
  input: json
  output: json
  tool_used: str | None
  model_used: str
  goal_id: str | None
  channel: str
  user_id: str
  status: str
  duration_ms: int
```

User can:
- View all actions in Web UI
- Export audit log
- Ask "why did you do X?" and trace back

---

## Deployment

### Single Command

```bash
# Clone
git clone https://github.com/SivaRamSV/paw.git
cd paw

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
docker compose up -d

# Open
open http://localhost:8080
```

### Docker Compose

```yaml
version: '3.8'

services:
  paaw:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://paaw:paw@postgres:5432/paw
      - VALKEY_URL=valkey://valkey:6379
      - LLM_API_KEY=${LLM_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - paaw-config:/app/configs
      - paaw-logs:/app/logs
    depends_on:
      - postgres
      - valkey
    restart: unless-stopped

  postgres:
    image: apache/age:latest
    environment:
      - POSTGRES_USER=paw
      - POSTGRES_PASSWORD=paw
      - POSTGRES_DB=paw
    volumes:
      - paaw-data:/var/lib/postgresql/data

  valkey:
    image: valkey/valkey:latest

volumes:
  paaw-data:
  paaw-config:
  paaw-logs:
```

### Runs On

- **Laptop** — for personal use
- **Raspberry Pi** — always-on home server
- **VPS ($5/mo)** — accessible from anywhere
- **Any cloud** — AWS, GCP, Azure, DigitalOcean

---

## Tech Stack

| Component | Technology | License |
|-----------|------------|---------|
| **Language** | Python 3.12+ | PSF |
| **Async** | asyncio + uvloop | MIT |
| **Web Framework** | FastAPI | MIT |
| **Database** | PostgreSQL + Apache AGE | PostgreSQL + Apache 2.0 |
| **Vector Search** | pgvector | PostgreSQL License |
| **Cache/Pub-Sub** | Valkey | BSD-3 |
| **LLM Gateway** | LiteLLM | MIT |
| **Local LLM** | Ollama | MIT |
| **CLI** | Typer + Rich | MIT |
| **Web UI** | React + React Flow | MIT |
| **Styling** | TailwindCSS | MIT |
| **Telegram** | python-telegram-bot | LGPL |
| **Slack** | slack-bolt | MIT |
| **WhatsApp** | whatsapp-web.js (bridge) | MIT |
| **Containerization** | Docker | Apache 2.0 |

**100% open source. Zero proprietary dependencies.**

---

## Project Structure

```
paaw/
├── paaw/
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   ├── config.py                  # Configuration (Pydantic)
│   │
│   ├── agent.py                   # PAAW agent core
│   │
│   ├── brain/                     # Thinking
│   │   ├── __init__.py
│   │   ├── llm.py                 # LiteLLM wrapper
│   │   ├── prompts.py             # System prompts
│   │   ├── router.py              # Message → Node routing
│   │   └── extractor.py           # Extract facts/memories from convo
│   │
│   ├── mental_model/              # The Soul of PAAW
│   │   ├── __init__.py
│   │   ├── graph.py               # Apache AGE operations
│   │   ├── nodes.py               # Node types & schemas
│   │   ├── edges.py               # Edge types
│   │   ├── tool.py                # Mental model tool interface
│   │   ├── context.py             # Context loading/assembly
│   │   └── maintenance.py         # Decay, consolidation
│   │
│   ├── onboarding/                # First-time setup
│   │   ├── __init__.py
│   │   ├── flow.py                # Conversational onboarding
│   │   ├── questions.py           # Question bank
│   │   └── builder.py             # Build initial graph
│   │
│   ├── channels/                  # Communication
│   │   ├── __init__.py
│   │   ├── gateway.py             # Unified message handling
│   │   ├── web.py                 # WebSocket chat
│   │   ├── cli.py                 # CLI channel
│   │   ├── telegram.py            # Telegram bot
│   │   ├── slack.py               # Slack bot
│   │   └── discord.py             # Discord bot
│   │
│   ├── tools/                     # External tools (MCP)
│   │   ├── __init__.py
│   │   ├── manager.py             # Tool registry
│   │   └── mcp.py                 # MCP client
│   │
│   ├── system/                    # System services
│   │   ├── __init__.py
│   │   ├── heartbeat.py           # Health monitoring
│   │   ├── scheduler.py           # Background tasks
│   │   └── audit.py               # Action logging
│   │
│   ├── api/                       # Web API
│   │   ├── __init__.py
│   │   ├── server.py              # FastAPI app
│   │   └── routes/
│   │       ├── chat.py            # WebSocket chat
│   │       ├── graph.py           # Graph visualization API
│   │       └── status.py          # Health API
│   │
│   └── cli/                       # CLI interface
│       ├── __init__.py
│       └── main.py                # Typer app
│
├── ui/                            # React frontend
│   ├── package.json
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Chat/              # Chat interface
│   │   │   ├── Graph/             # Mental model visualization
│   │   │   └── Settings/          # Settings UI
│   │   └── hooks/
│   └── dist/                      # Built output
│
├── scripts/
│   └── init-db.sql                # Database initialization
│
├── docker-compose.yaml
├── Dockerfile
├── pyproject.toml
├── README.md
├── ARCHITECTURE.md                # This file
└── BUILDING_PLAN.md               # Step-by-step build guide
```

---

## Build Phases

### Phase 1: Foundation ✅ COMPLETE
- [x] Project setup (pyproject.toml, Docker)
- [x] Configuration system (Pydantic)
- [x] Brain with LiteLLM (Claude Sonnet 4.6)
- [x] Basic Agent core
- [x] CLI channel (`paaw chat`, `paaw ask`)
- [x] FastAPI server with WebSocket
- [x] System prompts

### Phase 2: Mental Model ✅ MOSTLY COMPLETE
- [x] PostgreSQL + Apache AGE setup
- [x] Graph schema (emergent structure, minimal hardcoding)
- [x] Graph operations (create/read/update nodes & edges)
- [x] Context loading from graph
- [x] Onboarding flow (simplified - just creates User node)
- [x] Entity creation via `<entity>` tags
- [x] Memory creation via `<memory>` tags
- [x] Basic visualization (`/viz` endpoint with D3)
- [ ] Memory decay (future)

### Phase 3: Skills & Jobs System ✅ COMPLETE
- [x] Directory structure (skills/, jobs/, mcp/)
- [x] Skill loader (skill.md parsing)
- [x] Job loader (job.md parsing)
- [x] Tools registry (MCP config, simulated calls)
- [x] Scheduler runner (tick loop, due detection)
- [x] Job executor (skill loading, context building)
- [x] Sample skill (simple_reporter)
- [x] Sample job (test_scheduler)
- [x] PAAW node (assistant entity in mental model)
- [x] Trail nodes (execution history in graph)
- [x] Real MCP integration (DuckDuckGo via MCP protocol)
- [x] Web UI: Dashboard with jobs, skills, trails

### Phase 4: Web UI & Chat
- [ ] Split-screen: Chat + Live graph
- [ ] Goals/Jobs dashboard
- [ ] Trails viewer
- [ ] Node detail view (click to explore)
- [ ] Create jobs via UI
- [ ] Settings UI

### Phase 5: Channels & Notifications
- [ ] Telegram integration (for alerts)
- [ ] Slack integration
- [ ] Unified message handling
- [ ] Job notifications via channels

### Phase 6: Advanced
- [ ] More tools (email, calendar, web scraping)
- [ ] Voice (Whisper + TTS)
- [ ] Proactive assistance
- [ ] Multi-user support
- [ ] Mobile-friendly UI

---

## Skills & Jobs System

### Overview

PAAW is a **personal assistant that works**. The core loop:

1. **User defines goals** and assigns jobs to PAAW
2. **PAAW wears skill hats** to execute jobs effectively
3. **Jobs run on schedule**, creating trails of execution
4. **Mental model grows** as a byproduct of work

### Architecture

```
User (root)
│
├── PAAW (assistant node)
│   │
│   ├── Skills/ (how to do things)
│   │   ├── skill_investment_analyst
│   │   ├── skill_research_assistant
│   │   └── skill_email_manager
│   │
│   └── Jobs/ (assigned work)
│       ├── job_monitor_gold
│       │   ├── uses: skill_investment_analyst
│       │   ├── serves: goal_build_portfolio
│       │   └── trails...
│       └── job_daily_summary
│
├── Goals/ (what user wants to achieve)
│   ├── goal_build_portfolio ◄── job_monitor_gold serves this
│   └── goal_switch_jobs
│
├── People/
│   ├── person_mom
│   └── person_dad
│
└── Domains/
    └── domain_work
```

### Skills (skill.md)

Skills are **personas/expertise** that PAAW can wear. Stored in `skills/` directory.

```markdown
# skills/investment_analyst/skill.md

# Investment Analyst

## Persona
You are a seasoned investment analyst with expertise in commodities,
stocks, and market trends.

## Domain Knowledge
- Gold prices: goldprice.org
- Stocks: Yahoo Finance
- Crypto: CoinGecko

## Tools You Use
- web_scrape
- notify_telegram

## How You Work
1. Always cite data sources
2. Compare to recent trends
3. Identify significant moves (>2% is notable)
4. Be concise but thorough

## Keywords
investment, stock, gold, silver, commodity, price, market, portfolio
```

### Jobs (job.md)

Jobs are **tasks assigned to PAAW**. Stored in `jobs/` directory.

```markdown
# jobs/monitor_gold/job.md

# Monitor Gold Price

## Skill
investment_analyst

## Goal
Track gold prices and alert on significant moves.

## Success Criteria
- Alert if price < $1800 or > $2100
- Daily summary at 9 PM

## Schedule
- Check: Every 1 hour
- Summary: Daily 21:00
- Duration: 30 days

## Context
User considering gold investment. Budget: $5000.
```

### The Scheduler (Minimal Python)

The Python scheduler is **dumb** - just a timer:

```python
# Every 5 minutes
async def scheduler_tick():
    # Load active jobs from mental model
    active_jobs = await db.get_nodes_by_type("Job", status="active")
    
    # Pass to PAAW - LLM decides what's due
    await paaw.process(
        message="SCHEDULER_TICK",
        context={"jobs": active_jobs, "time": now()}
    )
```

PAAW (the LLM) is **smart**:
- Reads job definitions
- Checks last_run, decides if due
- Loads relevant skill
- Executes with allowed tools
- Records trail
- Notifies if needed

### Trail Nodes

Every job execution creates a Trail node:

```
Trail Node:
- id: trail_20260321_120000
- parent: job_monitor_gold
- started_at: 2026-03-21T12:00:00
- completed_at: 2026-03-21T12:00:15
- status: success
- tools_used: [web_scrape]
- result: {price: 1950, source: "goldprice.org"}
- decision: "Price within range, no alert needed"
- actions_taken: []
```

### Tool Validation

Before accepting a job, PAAW checks if required tools are available:

```
User: "Monitor gold prices for me"

PAAW checks:
- Job needs: web_scrape, notify_telegram
- Available: web_scrape ✓, notify_telegram ✗

PAAW: "I can monitor gold prices, but I can't send Telegram alerts yet.
       That tool isn't configured. I can notify you via CLI instead,
       or you can set up the Telegram tool first. What would you prefer?"
```

---

## Summary

PAAW is:

- **A capable assistant** that works 24/7 on your behalf
- **Skills-based** — wears expert hats for different tasks
- **Goal-oriented** — jobs serve your goals, not just busywork
- **Transparent** — full trails of what was done and why
- **LLM-native** — minimal hardcoding, LLM decides execution
- **Tool-aware** — knows its capabilities and limitations
- **Privacy-first** — all data local, all open source

```
         ╭─────────────────────────────────────────────────────╮
         │                                                     │
         │   "PAAW, monitor gold prices for me"                │
         │                                                     │
         │   🐾 Got it! I'll track gold every hour.            │
         │                                                     │
         │   📊 Using: Investment Analyst skill                │
         │   🎯 Serves: Your "Build Portfolio" goal            │
         │   ⏰ Schedule: Hourly checks, daily summary 9 PM    │
         │   🔔 Alerts: If < $1800 or > $2100                  │
         │                                                     │
         │   I'll start right away. Check the Jobs dashboard   │
         │   to see progress and trails. 🐾                    │
         │                                                     │
         ╰─────────────────────────────────────────────────────╯
```

**The goal: An AI assistant that actually gets things done.**

Let's build this! 🐾
