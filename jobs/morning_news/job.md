# Morning News Briefing

## Meta
created: 2026-03-01
created_by: system
status: active

## Uses Skill
web_researcher

## Goal
Find top tech and AI news of the day. Keep user informed without overwhelming.

## What To Find
- Global tech news (Google, Apple, Microsoft, OpenAI)
- AI/ML developments and breakthroughs
- India-specific tech news if relevant

## Delivery
- Format: 5-7 key headlines with one-line summaries as bullet points
- Length: Under 1500 characters
- Only alert on: Breaking tech news, major AI announcements
- Skip: Routine product updates, minor market movements

## Schedule
cron: 0 8 * * *
timezone: Asia/Kolkata

## How To Notify
IMPORTANT: After completing your research, you MUST send the results to Discord channel ID: 1485699544216764540
Use the mcp-discord__discord_login tool first, then use mcp-discord__discord_send with channelId "1485699544216764540" and your formatted message.
Always send a message - either the full briefing or "No major updates today" if nothing significant.

## Context
User is a tech professional. Prefers bullet points over paragraphs. This is a quick morning briefing, not a deep dive.
