import streamlit as st
import os


def render_sidebar():
    """
    Render the complete sidebar with AI configuration and statistics
    """
    with st.sidebar:
        _render_ai_configuration()


def _render_ai_configuration():
    """
    Render the AI configuration section
    """
    st.header("🤖 AI Configuration")

    # Model provider selection
    model_provider = st.selectbox(
        "Choose AI Provider:",
        options=["OpenAI (ChatGPT)", "Anthropic (Claude)"],
        index=0
    )

    # Model variant selection based on provider
    if model_provider == "OpenAI (ChatGPT)":
        model = st.selectbox(
            "Model:",
            options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"],
            index=0
        )
        api_key_label = "🔑 OpenAI API Key"
        api_key_help = "Enter your OpenAI API key from platform.openai.com"
    else:
        model = st.selectbox(
            "Model:",
            options=["claude-3-haiku-20240307",
                     "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
            index=1
        )
        api_key_label = "🔑 Anthropic API Key"
        api_key_help = "Enter your Anthropic API key from console.anthropic.com"

    api_key = _handle_api_key_input(
        model_provider, api_key_label, api_key_help)

    _show_configuration_status(api_key, model_provider)

    st.session_state.selected_provider = model_provider
    st.session_state.selected_model = model
    st.session_state.api_key = api_key


def _handle_api_key_input(model_provider, api_key_label, api_key_help):
    """
    Handle API key input with persistence from multiple sources
    """
    # Try to get saved API key from different sources
    saved_api_key = ""

    # Method 1: Try from st.secrets
    try:
        if model_provider == "OpenAI (ChatGPT)":
            saved_api_key = st.secrets["OPENAI_API_KEY"]
        else:
            saved_api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass

    # Method 2: Try from environment variables
    if not saved_api_key:
        if model_provider == "OpenAI (ChatGPT)":
            saved_api_key = os.getenv("OPENAI_API_KEY", "")
        else:
            saved_api_key = os.getenv("ANTHROPIC_API_KEY", "")

    # Method 3: Try from session state (current session)
    if not saved_api_key:
        session_key = f"api_key_{model_provider.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        saved_api_key = st.session_state.get(session_key, "")

    api_key = st.text_input(
        api_key_label,
        type="password",
        help=api_key_help,
        placeholder="sk-..." if model_provider == "OpenAI (ChatGPT)" else "sk-ant-...",
        value=saved_api_key
    )

    if api_key:
        session_key = f"api_key_{model_provider.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        st.session_state[session_key] = api_key

    return api_key


def _show_configuration_status(api_key, model_provider):
    """
    Show current configuration status and help information
    """
    if api_key:
        st.success(f"✅ {model_provider.split('(')[0].strip()} configured")

        _show_api_key_source(api_key, model_provider)
    else:
        st.warning("⚠️ Please enter your API key")

        # _show_api_key_help()


def _show_api_key_source(api_key, model_provider):
    """
    Show where the API key is coming from
    """
    secrets_key = ""
    try:
        secrets_key = st.secrets["OPENAI_API_KEY" if model_provider ==
                                 "OpenAI (ChatGPT)" else "ANTHROPIC_API_KEY"]
    except:
        pass

    env_key = os.getenv("OPENAI_API_KEY" if model_provider ==
                        "OpenAI (ChatGPT)" else "ANTHROPIC_API_KEY", "")

    if api_key and api_key == secrets_key:
        st.info("🔒 API key from st.secrets")
    elif api_key and api_key == env_key:
        st.info("🌍 API key from environment")
    else:
        st.info("💾 API key from current session")


def _show_api_key_help():
    """
    Show help information for API key persistence
    """
    with st.expander("💡 How to save API key permanently"):
        st.markdown("""
        **Option 1: Environment Variables (Recommended for local dev)**
        ```bash
        # Add to your ~/.zshrc or ~/.bashrc
        export OPENAI_API_KEY="your-key-here"
        export ANTHROPIC_API_KEY="your-key-here"
        ```
        
        **Option 2: Streamlit Secrets (For deployment)**
        Create `.streamlit/secrets.toml`:
        ```toml
        OPENAI_API_KEY = "your-key-here"
        ANTHROPIC_API_KEY = "your-key-here"
        ```
        
        **Option 3: Current session only**
        Just enter your key above - it will persist during this session.
        """)
