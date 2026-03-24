"""
PAAW Test Configuration

Basic tests to verify the setup works.
"""

import pytest


def test_import_paaw():
    """Test that paaw can be imported."""
    import paaw

    assert paaw.__version__ == "0.1.0"


def test_import_config():
    """Test that config loads."""
    from paaw.config import settings

    assert settings.app_name == "PAAW"


def test_import_models():
    """Test that models can be imported."""
    from paaw.models import UnifiedMessage, Channel

    msg = UnifiedMessage(
        channel=Channel.CLI,
        user_id="test-user",
        content="Hello!",
    )
    assert msg.content == "Hello!"
    assert msg.channel == Channel.CLI


def test_import_agent():
    """Test that agent can be imported."""
    from paaw.agent import Agent

    # Just test import, don't instantiate (needs LLM config)
    assert Agent is not None


def test_import_llm():
    """Test that LLM can be imported."""
    from paaw.brain.llm import LLM

    assert LLM is not None


@pytest.mark.asyncio
async def test_llm_chat():
    """Test LLM chat (requires API key)."""
    pytest.skip("Requires API key - run manually")

    from paaw.brain.llm import LLM

    llm = LLM()
    response = await llm.chat("Say 'hello' and nothing else.")
    assert "hello" in response.lower()
