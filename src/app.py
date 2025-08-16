from modules.analysis_orchestrator import AnalysisType
from ui.sidebar import render_sidebar
from styles.custom_css import load_custom_css
from app_config import config
import streamlit as st
import os

st.set_page_config(
    page_title="Data Entry - Microbiology & Transfers",
    page_icon="🦠",
    layout="wide"
)

load_custom_css()
render_sidebar()

st.title("🦠 Data Entry - Microbiology & Transfers")
st.markdown("---")

col1, col2 = st.columns(2)

# Load Microbiology Data
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

        if "saved_microbiology" not in st.session_state:
            st.session_state.saved_microbiology = []

        file_already_saved = any(
            item.get("filename") == uploaded_micro.name and item.get(
                "content") == content
            for item in st.session_state.saved_microbiology
        )

        if not file_already_saved:
            st.session_state.saved_microbiology.append({
                "filename": uploaded_micro.name,
                "content": content
            })
            st.success("✅ Microbiology file automatically saved!")

        st.text_area(
            "File content:",
            value=content,
            height=200,
            key="micro_content_display",
            disabled=True
        )

# Load Transfers Data
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

        if "saved_transfers" not in st.session_state:
            st.session_state.saved_transfers = []

        file_already_saved = any(
            item.get("filename") == uploaded_transfer.name and item.get(
                "content") == content
            for item in st.session_state.saved_transfers
        )

        if not file_already_saved:
            st.session_state.saved_transfers.append({
                "filename": uploaded_transfer.name,
                "content": content
            })
            st.success("✅ Transfers file automatically saved!")

        st.text_area(
            "File content:",
            value=content,
            height=200,
            key="transfer_content_display",
            disabled=True
        )

st.markdown("---")

# Data Analysis Section
st.subheader("📈 Data Analysis")

micro_data = st.session_state.get("saved_microbiology", [])
transfer_data = st.session_state.get("saved_transfers", [])
has_data = bool(micro_data and transfer_data)

if not has_data:
    if not micro_data and not transfer_data:
        st.info(
            "ℹ️ Please upload both Microbiology and Transfers CSV files to enable analysis")
    elif not micro_data:
        st.info("ℹ️ Please upload Microbiology CSV file to enable analysis")
    elif not transfer_data:
        st.info("ℹ️ Please upload Transfers CSV file to enable analysis")

analysis_button = st.button(
    "📊 Generate Analysis",
    type="primary",
    use_container_width=False,
    disabled=not has_data
)

if analysis_button and has_data:
    with st.spinner("🔍 Analyzing data..."):
        from modules.analysis_orchestrator import run_analysis_workflow

        analysis_results = run_analysis_workflow(
            micro_data, transfer_data, analysis_type=config.DEFAULT_ANALYSIS_TYPE)
        formatted_results = analysis_results.get("formatted_results", None)

        st.session_state.formatted_analysis = formatted_results

        st.success("✅ Analysis completed!")

if "formatted_analysis" in st.session_state:
    st.subheader("📊 Analysis Results")

    with st.expander("View detailed analysis", expanded=True):
        st.text(st.session_state.formatted_analysis)

st.markdown("---")

# AI Summary Section
if "formatted_analysis" in st.session_state:
    st.markdown("**🤖 AI Analysis**")
    if st.button("🤖 Generate AI Summary", type="primary", use_container_width=False):
        provider = st.session_state.get("selected_provider", "")
        model = st.session_state.get("selected_model", "")
        api_key = st.session_state.get("api_key", "")

        if not api_key:
            st.error("❌ Please configure your AI API key in the sidebar.")
        else:
            with st.spinner(f"🤖 Generating AI summary with {provider}..."):
                from modules.ai_summary import generate_ai_summary, generate_mock_summary
                from prompts.analysis_prompts import format_prompt

                formatted_prompt = format_prompt(
                    st.session_state.formatted_analysis,
                    prompt_type=config.DEFAULT_PROMPT_TYPE
                )

                summary_result = generate_ai_summary(
                    formatted_prompt,
                    provider,
                    model,
                    api_key
                )

                if summary_result["success"]:
                    st.session_state.ai_summary = summary_result["content"]
                    st.success("✅ AI summary generated!")
                else:
                    st.warning(f"⚠️ AI API failed: {summary_result['error']}")
                    st.info("🔄 Using mock summary instead...")
                    st.session_state.ai_summary = generate_mock_summary(
                        st.session_state.formatted_analysis
                    )

if "ai_summary" in st.session_state:
    st.subheader("🤖 AI Summary")

    with st.expander("View AI summary", expanded=True):
        st.markdown(st.session_state.ai_summary)
