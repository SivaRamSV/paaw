# Track Berkshire Hathaway - New CEO Watch

## Meta
created: 2026-03-24
created_by: server_room
status: active

## Uses Skill
web_researcher

## Goal
Quick daily check on Berkshire Hathaway news. Flag anything that deviates from Buffett's value investing philosophy.

## What To Find
- Any major Berkshire Hathaway news from the last 24 hours
- New investments or acquisitions (if any)
- Any red flags against Buffett's philosophy (speculation, crypto, excessive debt)

## Delivery
- Format: 3-5 bullet points max
- Length: Under 500 characters
- Only alert on: Major portfolio changes, philosophy violations, CEO statements
- If nothing significant: Send "No major Berkshire updates today"

## Schedule
cron: 0 8 * * *
timezone: Asia/Kolkata

## How To Notify
IMPORTANT: After completing your research, you MUST send the results to Discord channel ID: 1485699544216764540
Use the mcp-discord__discord_login tool first, then use mcp-discord__discord_send with channelId "1485699544216764540" and your formatted message.
Always send a message - either the full briefing or "No major updates today" if nothing significant.

## Context
Buffett's philosophy: long-term value investing, avoid speculation/crypto, no excessive debt, stay in circle of competence.