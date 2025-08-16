"""
Application Configuration
Centralized configuration for the infection cluster detection app
"""

from modules.analysis_orchestrator import AnalysisType


class AppConfig:
    DEFAULT_ANALYSIS_TYPE = AnalysisType.MOCK
    DEFAULT_PROMPT_TYPE = "standard"


config = AppConfig()
