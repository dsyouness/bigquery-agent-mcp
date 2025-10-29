"""
Configuration dynamique des LLM providers.
Permet de choisir entre différents modèles (Gemini, Claude, OpenAI, Ollama).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature=0):
    """
    Retourne une instance de LLM basée sur la configuration.

    Args:
        temperature: Température du modèle (0 = déterministe, 1 = créatif)

    Returns:
        Instance de LLM compatible LangChain
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY doit être défini dans .env")

        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=temperature
        )

    elif provider == "claude":
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY doit être défini dans .env")

        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=api_key,
            temperature=temperature
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY doit être défini dans .env")

        return ChatOpenAI(
            model="gpt-4",
            openai_api_key=api_key,
            temperature=temperature
        )

    elif provider == "ollama":
        from langchain_community.llms import Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")

        return Ollama(
            base_url=base_url,
            model=model,
            temperature=temperature
        )

    else:
        raise ValueError(
            f"Provider LLM '{provider}' non supporté. "
            f"Choisissez parmi: gemini, claude, openai, ollama"
        )


def get_provider_info():
    """Retourne des informations sur le provider LLM configuré."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    info = {
        "gemini": "Google Gemini Pro",
        "claude": "Anthropic Claude 3.5 Sonnet",
        "openai": "OpenAI GPT-4",
        "ollama": f"Ollama ({os.getenv('OLLAMA_MODEL', 'llama2')})"
    }

    return info.get(provider, "Inconnu")

