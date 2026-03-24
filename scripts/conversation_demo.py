"""
Demo: Conversation storage with smart summarization

This simulates how conversations will be stored and summarized.
Run: python scripts/conversation_demo.py
"""

from datetime import datetime, timedelta
import json

# Configuration
MAX_RECENT_MESSAGES = 10      # Always keep last N messages in full
SUMMARIZE_THRESHOLD = 15      # When total messages exceed this, summarize older ones
SUMMARIZE_BATCH_SIZE = 10     # How many messages to summarize at once


class ConversationDemo:
    """Simulates conversation storage with summarization."""
    
    def __init__(self):
        # This would be stored in the graph node attributes
        self.conversation = {
            "id": f"conv_user_default_{datetime.now().strftime('%Y-%m-%d')}",
            "label": datetime.now().strftime("%B %d, %Y"),
            "started_at": datetime.now().isoformat(),
            "message_count": 0,
            "messages": [],        # Recent messages (full content)
            "summaries": [],       # Summarized older messages
            "tools_used": [],
        }
    
    def add_message(self, role: str, content: str, tool_calls: list = None):
        """Add a message and trigger summarization if needed."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        if tool_calls:
            msg["tool_calls"] = tool_calls
        
        self.conversation["messages"].append(msg)
        self.conversation["message_count"] += 1
        
        # Check if we need to summarize
        self._maybe_summarize()
    
    def _maybe_summarize(self):
        """Summarize older messages if we exceed threshold."""
        total_messages = len(self.conversation["messages"])
        
        if total_messages > SUMMARIZE_THRESHOLD:
            # Calculate how many to summarize
            messages_to_summarize = total_messages - MAX_RECENT_MESSAGES
            
            if messages_to_summarize >= SUMMARIZE_BATCH_SIZE:
                # Take oldest batch
                batch = self.conversation["messages"][:SUMMARIZE_BATCH_SIZE]
                
                # Generate summary (in real code, this would call LLM)
                summary = self._generate_summary(batch)
                
                # Add to summaries
                self.conversation["summaries"].append({
                    "messages_covered": f"{self.conversation['message_count'] - total_messages + 1}-{self.conversation['message_count'] - total_messages + SUMMARIZE_BATCH_SIZE}",
                    "timestamp": datetime.now().isoformat(),
                    "summary": summary,
                    "message_count": len(batch),
                })
                
                # Remove summarized messages, keep recent ones
                self.conversation["messages"] = self.conversation["messages"][SUMMARIZE_BATCH_SIZE:]
                
                print(f"\n🔄 SUMMARIZATION TRIGGERED!")
                print(f"   - Summarized {SUMMARIZE_BATCH_SIZE} messages")
                print(f"   - Remaining recent messages: {len(self.conversation['messages'])}")
                print(f"   - Total summaries: {len(self.conversation['summaries'])}")
    
    def _generate_summary(self, messages: list) -> str:
        """Generate summary of messages (simulated - would use LLM)."""
        # In real code: await self.llm.chat("Summarize this conversation: ...")
        
        topics = set()
        for msg in messages:
            content = msg["content"].lower()
            if "ai" in content or "research" in content:
                topics.add("AI research")
            if "code" in content or "python" in content:
                topics.add("coding")
            if "weather" in content:
                topics.add("weather")
            if "search" in content or "find" in content:
                topics.add("web search")
        
        return f"User discussed: {', '.join(topics) if topics else 'general topics'}. {len(messages)} messages exchanged."
    
    def get_context_for_llm(self) -> str:
        """Build context string for LLM (summaries + recent messages)."""
        parts = []
        
        # Add summaries first (older context, condensed)
        if self.conversation["summaries"]:
            parts.append("=== Earlier Today ===")
            for s in self.conversation["summaries"]:
                parts.append(f"[Messages {s['messages_covered']}]: {s['summary']}")
            parts.append("")
        
        # Add recent messages (full context)
        if self.conversation["messages"]:
            parts.append("=== Recent Messages ===")
            for msg in self.conversation["messages"]:
                role = "You" if msg["role"] == "assistant" else "User"
                parts.append(f"{role}: {msg['content'][:100]}...")
        
        return "\n".join(parts)
    
    def print_state(self):
        """Print current conversation state."""
        print("\n" + "="*60)
        print(f"📅 Conversation: {self.conversation['label']}")
        print(f"📊 Total messages: {self.conversation['message_count']}")
        print(f"📝 Recent messages (full): {len(self.conversation['messages'])}")
        print(f"📋 Summaries: {len(self.conversation['summaries'])}")
        print("="*60)


def run_demo():
    """Simulate a day's conversation with summarization."""
    print("\n" + "🎬 CONVERSATION DEMO: Smart Summarization")
    print("="*60)
    print(f"Config: MAX_RECENT={MAX_RECENT_MESSAGES}, THRESHOLD={SUMMARIZE_THRESHOLD}, BATCH={SUMMARIZE_BATCH_SIZE}")
    print("="*60)
    
    conv = ConversationDemo()
    
    # Simulate messages throughout the day
    sample_messages = [
        ("user", "Hi PAAW, good morning!"),
        ("assistant", "Good morning! 🐾 How can I help you today?"),
        ("user", "What's the weather like today?"),
        ("assistant", "Let me search for that... It's sunny, 25°C in Bangalore."),
        ("user", "Can you search for latest AI research papers?"),
        ("assistant", "Searching for AI research... Found several papers on GPT-5 and Claude 4."),
        ("user", "Tell me more about GPT-5"),
        ("assistant", "GPT-5 was released last month with improved reasoning capabilities..."),
        ("user", "How does it compare to Claude?"),
        ("assistant", "Both are excellent. GPT-5 excels at coding, Claude at analysis..."),
        ("user", "Can you help me write some Python code?"),
        ("assistant", "Of course! What would you like to build?"),
        ("user", "A data pipeline that processes CSV files"),
        ("assistant", "Here's a basic structure for your pipeline..."),
        ("user", "Can you add error handling?"),
        ("assistant", "Sure, here's the updated code with try/except blocks..."),
        ("user", "What about logging?"),
        ("assistant", "Added structlog for structured logging..."),
        ("user", "Perfect! Now let's discuss my meeting tomorrow"),
        ("assistant", "What's the meeting about?"),
        ("user", "It's a presentation on AI adoption in our company"),
        ("assistant", "I can help you prepare! What aspects would you like to cover?"),
        ("user", "ROI and implementation challenges"),
        ("assistant", "Great topics. Let me search for some statistics..."),
        ("user", "Also find case studies"),
        ("assistant", "Found 5 relevant case studies from Fortune 500 companies..."),
    ]
    
    print("\n📨 Simulating messages...\n")
    
    for i, (role, content) in enumerate(sample_messages, 1):
        print(f"  [{i:2d}] {role.upper()}: {content[:50]}...")
        conv.add_message(role, content)
        
        # Show state at key points
        if i == 10:
            print("\n  --- After 10 messages ---")
            conv.print_state()
        elif i == 16:
            print("\n  --- After 16 messages (threshold crossed!) ---")
            conv.print_state()
        elif i == len(sample_messages):
            print("\n  --- Final state ---")
            conv.print_state()
    
    # Show what context would be sent to LLM
    print("\n\n📤 CONTEXT FOR LLM (what PAAW sees):")
    print("-"*60)
    print(conv.get_context_for_llm())
    print("-"*60)
    
    # Token estimation
    context = conv.get_context_for_llm()
    estimated_tokens = len(context.split()) * 1.3  # Rough estimate
    print(f"\n📊 Estimated tokens: ~{int(estimated_tokens)}")
    print(f"   Without summarization would be: ~{int(conv.conversation['message_count'] * 50 * 1.3)}")
    print(f"   Savings: ~{int((conv.conversation['message_count'] * 50 * 1.3) - estimated_tokens)} tokens")


if __name__ == "__main__":
    run_demo()
