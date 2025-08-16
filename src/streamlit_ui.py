import streamlit as st
import os

st.set_page_config(
    page_title="Data Entry - Microbiology & Transfers",
    page_icon="🦠",
    layout="wide"
)

st.title("🦠 Data Entry - Microbiology & Transfers")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔬 Microbiology Data")

    uploaded_micro = st.file_uploader(
        "📁 Drag & Drop your Microbiology CSV file",
        type=['csv'],
        key="micro_uploader",
        help="Drag and drop your CSV file or click to browse"
    )
    if uploaded_micro is not None:
        content = uploaded_micro.read().decode("utf-8")
        st.success(f"✅ File '{uploaded_micro.name}' loaded successfully!")

        st.text_area(
            "File content:",
            value=content,
            height=200,
            key="micro_content_display",
            disabled=True
        )

        if st.button("💾 Save this Microbiology file", type="primary", key="save_micro_file"):
            if "saved_microbiology" not in st.session_state:
                st.session_state.saved_microbiology = []
            st.session_state.saved_microbiology.append({
                "filename": uploaded_micro.name,
                "content": content
            })
            st.success("✅ Microbiology file saved!")

with col2:
    st.subheader("🚑 Transfers Data")

    uploaded_transfer = st.file_uploader(
        "📁 Drag & Drop your Transfers CSV file",
        type=['csv'],
        key="transfer_uploader",
        help="Drag and drop your CSV file or click to browse"
    )

    if uploaded_transfer is not None:
        content = uploaded_transfer.read().decode("utf-8")
        st.success(f"✅ File '{uploaded_transfer.name}' loaded successfully!")

        st.text_area(
            "File content:",
            value=content,
            height=200,
            key="transfer_content_display",
            disabled=True
        )

        if st.button("💾 Save this Transfers file", type="primary", key="save_transfer_file"):
            if "saved_transfers" not in st.session_state:
                st.session_state.saved_transfers = []
            st.session_state.saved_transfers.append({
                "filename": uploaded_transfer.name,
                "content": content
            })
            st.success("✅ Transfers file saved!")

# Sidebar with AI configuration and counters
with st.sidebar:
    st.header("🤖 AI Configuration")

    # Model selection
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
    else:  # Anthropic Claude
        model = st.selectbox(
            "Model:",
            options=["claude-3-haiku-20240307",
                     "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
            index=1
        )
        api_key_label = "🔑 Anthropic API Key"
        api_key_help = "Enter your Anthropic API key from console.anthropic.com"

    # API Key input with persistence
    saved_api_key = ""

    # Method 1: Try from st.secrets (recommended for deployment)
    try:
        if model_provider == "OpenAI (ChatGPT)":
            saved_api_key = st.secrets["OPENAI_API_KEY"]
        else:
            saved_api_key = st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass

    # Method 2: Try from environment variables (local development)
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

    if api_key:
        st.success(f"✅ {model_provider.split('(')[0].strip()} configured")

        secrets_key = ""
        try:
            secrets_key = st.secrets["OPENAI_API_KEY" if model_provider ==
                                     "OpenAI (ChatGPT)" else "ANTHROPIC_API_KEY"]
        except:
            pass

        env_key = os.getenv("OPENAI_API_KEY" if model_provider ==
                            "OpenAI (ChatGPT)" else "ANTHROPIC_API_KEY", "")

        if saved_api_key and saved_api_key == secrets_key:
            st.info("🔒 API key from st.secrets")
        elif saved_api_key and saved_api_key == env_key:
            st.info("🌍 API key from environment")
        else:
            st.info("💾 API key from current session")
    else:
        st.warning("⚠️ Please enter your API key")

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

    st.markdown("---")

    # Store selected configuration in session state
    st.session_state.selected_provider = model_provider
    st.session_state.selected_model = model
    st.session_state.api_key = api_key
