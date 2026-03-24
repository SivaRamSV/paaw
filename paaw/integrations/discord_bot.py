"""
Discord Bot Listener for PAAW.

This bot listens for messages on Discord and forwards them to PAAW's API,
allowing you to chat with PAAW from your mobile Discord app.

Usage:
    python -m paaw.integrations.discord_bot

Configuration:
    Set DISCORD_BOT_TOKEN in environment or .env file
    Or it will read from mcp/servers.json
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import aiohttp
import discord
from discord import Intents

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class PAWWDiscordBot(discord.Client):
    """Discord bot that forwards messages to PAAW."""
    
    def __init__(self, paaw_url: str = "http://localhost:8080", **kwargs):
        # Set up intents - we need message content
        intents = Intents.default()
        intents.message_content = True  # Required - enable in Discord Developer Portal
        intents.guilds = True
        intents.dm_messages = True
        # Note: members intent requires approval for 100+ servers, disabled by default
        # intents.members = True
        
        super().__init__(intents=intents, **kwargs)
        
        self.paaw_url = paaw_url
        self.session: aiohttp.ClientSession | None = None
        
        # Track which channels to respond in (empty = respond everywhere bot is mentioned or DM'd)
        self.allowed_channels: set[int] = set()
        
        # Bot's user ID (set after login)
        self.bot_user_id: int | None = None
        
        # File to track last processed timestamp
        self.state_file = Path(__file__).parent.parent.parent / "logs" / "discord_bot_state.json"
    
    async def setup_hook(self):
        """Called when bot is ready to set up resources."""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
        await super().close()
    
    async def on_ready(self):
        """Called when bot successfully connects to Discord."""
        self.bot_user_id = self.user.id
        print(f"🐾 PAAW Discord Bot is online!")
        print(f"   Logged in as: {self.user.name} ({self.user.id})")
        print(f"   Connected to {len(self.guilds)} server(s)")
        print(f"   PAAW API: {self.paaw_url}")
        print()
        print("📱 You can now chat with PAAW from Discord!")
        print("   - DM the bot directly")
        print("   - Or @mention the bot in a channel")
        print()
        
        # Check for missed messages while bot was offline
        await self.process_missed_messages()
    
    async def process_missed_messages(self):
        """
        Process messages that were sent while the bot was offline.
        
        This checks:
        1. Recent DMs to the bot
        2. Recent mentions in servers
        
        And responds to any that haven't been responded to.
        """
        print("🔍 Checking for missed messages...")
        missed_count = 0
        
        # Load last online timestamp and known DM channels
        last_online = None
        saved_dm_channel_ids = []
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                    last_online = datetime.fromisoformat(state.get("last_online", ""))
                    saved_dm_channel_ids = state.get("dm_channel_ids", [])
                    print(f"   Last online: {last_online}")
                    print(f"   Known DM channels: {len(saved_dm_channel_ids)}")
        except Exception as e:
            print(f"   Could not load state: {e}")
        
        try:
            # Check DMs - fetch saved DM channels
            for dm_channel_id in saved_dm_channel_ids:
                try:
                    channel = await self.fetch_channel(dm_channel_id)
                    if not isinstance(channel, discord.DMChannel):
                        continue
                    
                    # Get the last message in this DM
                    last_messages = [msg async for msg in channel.history(limit=1)]
                    
                    if not last_messages:
                        continue
                    
                    last_msg = last_messages[0]
                    
                    # If the last message was from the user (not from us), it's unanswered!
                    if last_msg.author.id != self.bot_user_id and not last_msg.author.bot:
                        missed_count += 1
                        print(f"   📨 Found unanswered DM from {last_msg.author.name}: {last_msg.content[:50]}...")
                        
                        # Respond to it now
                        async with channel.typing():
                            response = await self.call_paaw(
                                last_msg.content,
                                str(last_msg.author.id),
                                last_msg.author.name
                            )
                        
                        if response:
                            await last_msg.reply(f"*(Sorry for the delay, I was offline)*\n\n{response}")
                except discord.NotFound:
                    print(f"   ⚠️ DM channel {dm_channel_id} no longer exists")
                except discord.Forbidden:
                    pass  # Can't access this DM
                except Exception as e:
                    print(f"   ⚠️ Error checking DM channel {dm_channel_id}: {e}")
            
            # Check mentions in servers
            for guild in self.guilds:
                for channel in guild.text_channels:
                    try:
                        # Check if we can read this channel
                        if not channel.permissions_for(guild.me).read_message_history:
                            continue
                        
                        # Get last 20 messages
                        async for message in channel.history(limit=20):
                            # Skip our own messages
                            if message.author.id == self.bot_user_id:
                                continue
                            
                            # Skip bot messages
                            if message.author.bot:
                                continue
                            
                            # Skip if before last online (already processed)
                            if last_online and message.created_at.replace(tzinfo=None) < last_online:
                                continue
                            
                            # Check if we were mentioned
                            if self.user not in message.mentions:
                                continue
                            
                            # Check if we already responded
                            responded = False
                            async for later_msg in channel.history(after=message, limit=10):
                                if later_msg.author.id == self.bot_user_id and message.author in later_msg.mentions:
                                    responded = True
                                    break
                                # Also check if we replied to the message
                                if later_msg.author.id == self.bot_user_id and later_msg.reference and later_msg.reference.message_id == message.id:
                                    responded = True
                                    break
                            
                            if not responded:
                                missed_count += 1
                                content = message.content.replace(f"<@{self.bot_user_id}>", "").replace(f"<@!{self.bot_user_id}>", "").strip()
                                print(f"   📨 Found missed mention from {message.author.name} in #{channel.name}: {content[:50]}...")
                                
                                async with channel.typing():
                                    response = await self.call_paaw(
                                        content,
                                        str(message.author.id),
                                        message.author.name
                                    )
                                
                                if response:
                                    await message.reply(f"*(Sorry for the delay, I was offline)*\n\n{response}")
                    except discord.Forbidden:
                        pass  # Can't access this channel
                    except Exception as e:
                        print(f"   ⚠️ Error checking channel {channel.name}: {e}")
        
        except Exception as e:
            print(f"   ⚠️ Error processing missed messages: {e}")
        
        # Save current timestamp
        self._save_state()
        
        if missed_count > 0:
            print(f"✅ Responded to {missed_count} missed message(s)")
        else:
            print("✅ No missed messages found")
    
    def _save_state(self):
        """Save bot state (last online timestamp and known DM channels)."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing state to preserve DM channel IDs
            existing_dm_channels = []
            if self.state_file.exists():
                try:
                    with open(self.state_file) as f:
                        existing = json.load(f)
                        existing_dm_channels = existing.get("dm_channel_ids", [])
                except:
                    pass
            
            with open(self.state_file, 'w') as f:
                json.dump({
                    "last_online": datetime.utcnow().isoformat(),
                    "dm_channel_ids": existing_dm_channels
                }, f)
        except Exception as e:
            print(f"   ⚠️ Could not save state: {e}")
    
    def _add_dm_channel(self, channel_id: int):
        """Add a DM channel ID to the state file for future recovery."""
        try:
            existing = {"dm_channel_ids": []}
            if self.state_file.exists():
                with open(self.state_file) as f:
                    existing = json.load(f)
            
            dm_ids = existing.get("dm_channel_ids", [])
            if channel_id not in dm_ids:
                dm_ids.append(channel_id)
                existing["dm_channel_ids"] = dm_ids
                
                with open(self.state_file, 'w') as f:
                    json.dump(existing, f)
                print(f"   📝 Saved DM channel {channel_id} for future recovery")
        except Exception as e:
            print(f"   ⚠️ Could not save DM channel: {e}")
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore messages from the bot itself
        if message.author.id == self.bot_user_id:
            return
        
        # Ignore messages from other bots
        if message.author.bot:
            return
        
        # Check if we should respond to this message
        should_respond = False
        content = message.content
        
        # Always respond to DMs
        if isinstance(message.channel, discord.DMChannel):
            should_respond = True
            # Save DM channel ID for future missed message recovery
            self._add_dm_channel(message.channel.id)
        
        # Respond if bot is mentioned
        elif self.user in message.mentions:
            should_respond = True
            # Remove the mention from the content
            content = content.replace(f"<@{self.bot_user_id}>", "").strip()
            content = content.replace(f"<@!{self.bot_user_id}>", "").strip()
        
        # Respond if in allowed channels (if configured)
        elif self.allowed_channels and message.channel.id in self.allowed_channels:
            should_respond = True
        
        if not should_respond:
            return
        
        # Don't respond to empty messages
        if not content.strip():
            return
        
        # Show typing indicator while processing
        async with message.channel.typing():
            response = await self.call_paaw(content, str(message.author.id), message.author.name)
        
        # Send the response
        if response:
            # Discord has a 2000 char limit, split if needed
            if len(response) <= 2000:
                await message.reply(response)
            else:
                # Split into chunks
                chunks = [response[i:i+1990] for i in range(0, len(response), 1990)]
                for i, chunk in enumerate(chunks):
                    if i == 0:
                        await message.reply(chunk)
                    else:
                        await message.channel.send(chunk)
        else:
            await message.reply("Sorry, I couldn't process that. PAAW might be offline.")
    
    async def call_paaw(self, message: str, user_id: str, username: str) -> str | None:
        """
        Send a message to PAAW's API and get the response.
        
        Args:
            message: The user's message
            user_id: Discord user ID
            username: Discord username
            
        Returns:
            PAAW's response text, or None if failed
        """
        if not self.session:
            return None
        
        try:
            # Call PAAW's chat API
            # We use the JSON API endpoint for programmatic access
            async with self.session.post(
                f"{self.paaw_url}/api/chat",
                json={
                    "message": message,
                    "user_id": f"discord_{user_id}",  # Prefix to identify Discord users
                    "channel": "discord",
                    "metadata": {
                        "username": username,
                        "platform": "discord"
                    }
                },
                timeout=aiohttp.ClientTimeout(total=120)  # 2 min timeout for LLM
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", data.get("message", ""))
                else:
                    print(f"PAAW API error: {resp.status}")
                    text = await resp.text()
                    print(f"Response: {text[:200]}")
                    return None
                    
        except asyncio.TimeoutError:
            print("PAAW API timeout")
            return "Sorry, I'm taking too long to respond. Try again?"
        except aiohttp.ClientError as e:
            print(f"PAAW API connection error: {e}")
            return None
        except Exception as e:
            print(f"Error calling PAAW: {e}")
            return None


def get_discord_token() -> str | None:
    """
    Get Discord bot token from various sources.
    
    Priority:
    1. DISCORD_BOT_TOKEN environment variable
    2. DISCORD_TOKEN environment variable
    3. mcp/servers.json discord config (with env var expansion)
    """
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check environment variables
    token = os.environ.get("DISCORD_BOT_TOKEN") or os.environ.get("DISCORD_TOKEN")
    if token:
        return token
    
    # Check MCP servers config
    try:
        config_path = Path(__file__).parent.parent.parent / "mcp" / "servers.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
            
            # Look for discord server config
            servers = config.get("mcpServers", {})
            for name, server in servers.items():
                if "discord" in name.lower():
                    env = server.get("env", {})
                    token = env.get("DISCORD_TOKEN") or env.get("DISCORD_BOT_TOKEN")
                    if token:
                        # Expand environment variable references like ${VAR}
                        if token.startswith("${") and token.endswith("}"):
                            var_name = token[2:-1]
                            token = os.environ.get(var_name)
                        return token
    except Exception as e:
        print(f"Error reading MCP config: {e}")
    
    return None


async def main():
    """Run the Discord bot."""
    token = get_discord_token()
    
    if not token:
        print("❌ No Discord bot token found!")
        print()
        print("Set one of these:")
        print("  1. DISCORD_BOT_TOKEN environment variable")
        print("  2. DISCORD_TOKEN in mcp/servers.json")
        print()
        sys.exit(1)
    
    # Get PAAW URL from config or default
    paaw_url = os.environ.get("PAAW_URL", "http://localhost:8080")
    
    print("🐾 Starting PAAW Discord Bot...")
    print(f"   PAAW URL: {paaw_url}")
    print()
    
    bot = PAWWDiscordBot(paaw_url=paaw_url)
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ Invalid Discord bot token!")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
