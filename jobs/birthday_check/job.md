# Birthday Check

## Meta
created: 2026-03-01
created_by: system
status: active

## Goal
Check for upcoming birthdays in the next 7 days and remind user to prepare wishes or gifts.

## Watch For
- Birthdays in next 7 days
- People user cares about (family, close friends)
- Any birthday-related tasks or commitments

## Alert Rules
- Alert on: Birthday within next 3 days
- Also alert: Birthday exactly 7 days away (for planning)
- Skip: Already notified this week for same person

## Schedule
cron: 0 9 * * *
timezone: Asia/Kolkata

## How To Notify
Post to #general channel on Discord if there's an upcoming birthday.

## Tools Required
(none - uses mental model only)

## Related Context
- domain: personal
- notes: Check Person nodes in mental model for birthday attributes. User values personal relationships.
