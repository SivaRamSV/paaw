"""
PAAW Onboarding - Minimal user creation flow.

Philosophy: Only create the User node during onboarding.
Everything else emerges organically from conversation.
"""

from paaw.onboarding.flow import OnboardingFlow, OnboardingResult

__all__ = ["OnboardingFlow", "OnboardingResult"]
