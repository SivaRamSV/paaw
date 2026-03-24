# Skill & Job Specification Guide

> **Version**: 2.0  
> **Date**: March 21, 2026

This document defines the standard formats for skills and jobs in PAAW.

---

## Skills

Skills define **what PAAW can do**. Each skill is a specialized capability that sub-agents use to execute jobs.

### Directory Structure

```
skills/
├── web_researcher/
│   └── skill.md
├── birthday_reminder/
│   └── skill.md
├── task_decomposer/
│   └── skill.md
└── {skill_id}/
    └── skill.md
```

### Skill Template (skill.md)

```markdown
# {Skill Name}

## Persona
A 2-3 sentence description of who this skill is. This becomes the sub-agent's 
identity when executing jobs. Write in second person ("You are...").

Example:
"You are a skilled web researcher who finds accurate, relevant information 
from the internet. You search intelligently, verify sources, and synthesize 
findings into clear, actionable summaries."

## How You Work
Step-by-step description of the methodology this skill follows.
Be specific - this guides the sub-agent's approach.

Example:
1. Formulate effective search queries based on the goal
2. Search using DuckDuckGo (search tool)
3. Review results and identify the most relevant sources
4. If needed, fetch full content from promising URLs
5. Synthesize findings into a clear summary
6. Always cite your sources with URLs

## Tools You Use
List of MCP tools this skill has access to:
- tool_name_1 (description of when to use it)
- tool_name_2 (description of when to use it)

Example:
- search (DuckDuckGo web search)
- fetch_content (get full webpage content)

## Output Format
Description or template of the expected output format.

Example:
```
## Summary
[Key findings in 2-3 sentences]

## Details
[Bullet points of important information]

## Sources
- [Title](URL) - brief note
```

## Keywords
Comma-separated keywords for skill matching when PAAW decides which skill to use.

Example:
research, search, web, news, find, lookup, investigate, discover

## Autonomy
Define what this skill can do without asking for approval:

```yaml
can_call_tools: true          # Can use tools listed above
can_access_web: true          # Can access external websites
can_modify_graph: false       # Can update mental model
max_iterations: 10            # Max ReAct loop iterations
timeout_minutes: 30           # Max execution time
```

## Needs Approval For
Actions that require PAAW or User approval before proceeding:
- send_external_message (sending emails, messages on behalf of user)
- spend_money (any purchases or payments)
- access_sensitive_data (private user information)
- permanent_actions (things that can't be undone)
```

---

## Jobs

Jobs define **what PAAW is assigned to do**. Each job uses a skill to accomplish a specific goal.

### Directory Structure

```
jobs/
├── birthday_check/
│   └── job.md
├── morning_news/
│   └── job.md
├── {dynamic_job_id}/        # Created from chat
│   └── job.md
└── {job_id}/
    └── job.md
```

### Job Template (job.md)

```markdown
# {Job Name}

## Skill
{skill_id}

The skill to use for this job. Must match a skill folder name in skills/.

## Goal
One clear sentence describing what success looks like.
This is what the sub-agent is ultimately trying to achieve.

Example:
"Check if any important people have birthdays in the next 7 days and remind the user."

## Description
Detailed explanation of what the job should accomplish.
Include any specific requirements or constraints.

Example:
"Scan the mental model for Person nodes that have birthday information. 
Calculate which birthdays are coming up within the next week. Generate a 
friendly reminder for the user so they can prepare gifts, make calls, or 
plan celebrations."

## Success Criteria
Measurable criteria for determining if the job is complete:
- Criterion 1 (specific and measurable)
- Criterion 2
- Criterion 3

Example:
- All Person nodes with birthdays are checked
- Birthdays within 7 days are identified
- User receives a clear, actionable reminder
- Special emphasis on birthdays within 1-2 days

## Schedule
Define when this job should run:

```yaml
frequency: manual | once | daily | weekly | monthly | yearly | cron
cron: "0 9 * * *"            # Optional: cron expression (overrides frequency)
time: "09:00"                # For daily jobs
day: 1                       # For monthly (1-31) or weekly (MON-SUN)
timezone: "Asia/Kolkata"     # Optional: defaults to system timezone
```

Examples:
- `frequency: daily, time: 09:00` → Every day at 9 AM
- `frequency: weekly, day: MON, time: 08:00` → Every Monday at 8 AM
- `frequency: cron, cron: "0 */2 * * *"` → Every 2 hours
- `frequency: manual` → Only runs when triggered manually

## Tools Allowed
Explicit list of tools this job can use:
- tool_1
- tool_2

If empty or omitted, uses the skill's default tools.

## Context
Additional context for the LLM when executing this job.
Can include relevant facts, constraints, user preferences.

Example:
"The user values family connections. Mom's birthday is March 22nd, Dad's 
birthday is May 30th. Check today's date and calculate days remaining.
User prefers brief, friendly reminders."

## Parallel Sub-Tasks (Optional)
For complex jobs that can be broken into parallel sub-tasks:

```yaml
subtasks:
  - id: research_gifts
    description: "Search for gift ideas"
    skill: web_researcher
    depends: []
    
  - id: check_budget
    description: "Check user's gift budget"
    skill: simple_reporter
    depends: []
    
  - id: compile_recommendations
    description: "Compile final gift recommendations"
    skill: simple_reporter
    depends: [research_gifts, check_budget]
```

## Serves (Optional)
What user goal, person, or domain this job serves.
Creates relationships in the mental model.

```yaml
serves:
  - type: person
    node_id: person_mom
    relationship: "birthday reminder"
    
  - type: goal
    node_id: goal_family_connections
    relationship: "supports goal"
```

## Metadata
Auto-generated fields (do not edit manually):

```yaml
created:
  by: chat | file | system
  date: 2026-03-21T09:00:00Z
  user_request: "Remind me about Mom's birthday every year"  # If from chat

stats:
  run_count: 5
  last_run: 2026-03-21T09:00:00Z
  success_rate: 100%
```
```

---

## Examples

### Example Skill: Web Researcher

```markdown
# Web Researcher

## Persona
You are a skilled web researcher who finds accurate, relevant information 
from the internet. You search intelligently, verify sources, and synthesize 
findings into clear, actionable summaries.

## How You Work
1. Understand the research goal clearly
2. Formulate effective search queries (try multiple if needed)
3. Search using DuckDuckGo (search tool)
4. Review results and identify the most relevant sources
5. If needed, fetch full content from promising URLs (fetch_content tool)
6. Synthesize findings into a clear summary
7. Always cite your sources with URLs

## Tools You Use
- search (DuckDuckGo web search - use for finding information)
- fetch_content (get full webpage content - use when search snippets aren't enough)

## Output Format
A structured research report:

```
## Summary
[Key findings in 2-3 sentences]

## Details
[Bullet points of important information]

## Sources
- [Title](URL) - brief note about what this source provided
```

## Keywords
research, search, web, news, find, lookup, investigate, discover, information

## Autonomy
```yaml
can_call_tools: true
can_access_web: true
can_modify_graph: false
max_iterations: 10
timeout_minutes: 30
```

## Needs Approval For
- send_external_message
- access_sensitive_data
```

### Example Job: Morning News Briefing

```markdown
# Morning News Briefing

## Skill
web_researcher

## Goal
Search for and summarize the top news of the day, focusing on tech and AI developments.

## Description
Perform a web search to find the latest news headlines, particularly around 
technology, AI, and any breaking news. Compile a brief morning briefing that 
keeps the user informed about what's happening in the world without overwhelming 
them with information.

## Success Criteria
- Search for today's top news (at least 2 different searches)
- Include tech/AI news if available
- Provide 5-10 key headlines with brief summaries
- Include source links for further reading
- Formatted clearly for quick scanning

## Schedule
```yaml
frequency: daily
time: "08:00"
timezone: "Asia/Kolkata"
```

## Tools Allowed
- search
- fetch_content

## Context
The user is a tech professional in Bangalore, India. Focus on:
- Global tech news (Google, Apple, Microsoft, OpenAI, etc.)
- AI/ML developments and breakthroughs
- India-specific tech news if relevant
- Major world events (brief mention)

Keep it concise - this is a morning briefing, not a deep dive.
User prefers bullet points over paragraphs.

## Serves
```yaml
serves:
  - type: domain
    node_id: domain_work
    relationship: "staying informed for work"
    
  - type: goal
    node_id: goal_stay_updated_tech
    relationship: "supports daily learning"
```

## Metadata
```yaml
created:
  by: file
  date: 2026-03-01T00:00:00Z

stats:
  run_count: 21
  last_run: 2026-03-21T08:00:00Z
  success_rate: 95%
```
```

---

## Creating Jobs from Chat

When a user asks PAAW to do something recurring, PAAW creates a job dynamically:

**User**: "Hey PAAW, can you search for gift ideas for Mom a week before her birthday every year?"

**PAAW's internal process**:
1. Detect intent: CREATE_JOB
2. Extract: goal, schedule, related person
3. Select appropriate skill: web_researcher
4. Create job.md file in jobs/
5. Create Job node in graph
6. Link to Person (Mom) node

**Generated job.md**:
```markdown
# Mom Birthday Gift Research

## Skill
web_researcher

## Goal
Search for thoughtful gift ideas for Mom one week before her birthday.

## Description
Research gift ideas that would be appropriate for Mom based on her interests 
and the user's budget. Compile a list of options with links.

## Success Criteria
- Found at least 5 diverse gift ideas
- Ideas span different price ranges
- Include links for purchasing
- Consider Mom's known interests

## Schedule
```yaml
frequency: yearly
cron: "0 9 15 3 *"  # March 15 at 9 AM (one week before March 22)
```

## Tools Allowed
- search
- fetch_content

## Context
Mom's birthday is March 22nd. She's the user's mother.
Consider her interests when searching (query mental model for details).

## Serves
```yaml
serves:
  - type: person
    node_id: person_mom
    relationship: "birthday gift research"
```

## Metadata
```yaml
created:
  by: chat
  date: 2026-03-21T14:30:00Z
  user_request: "search for gift ideas for Mom a week before her birthday every year"
```
```

---

## Validation Rules

### Skills
- [ ] Has `# {Name}` header
- [ ] Has `## Persona` section
- [ ] Has `## How You Work` section
- [ ] Has `## Tools You Use` section (can be empty)
- [ ] Has `## Keywords` section
- [ ] Skill ID (folder name) is lowercase with underscores

### Jobs
- [ ] Has `# {Name}` header
- [ ] Has `## Skill` section with valid skill_id
- [ ] Has `## Goal` section (one sentence)
- [ ] Has `## Success Criteria` section (at least 1 criterion)
- [ ] Has `## Schedule` section
- [ ] Job ID (folder name) is lowercase with underscores
- [ ] If `## Serves` exists, node_ids must exist in graph

---

*Last updated: March 21, 2026*
