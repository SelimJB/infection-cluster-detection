import streamlit as st

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

# Sidebar with counters
with st.sidebar:
    st.header("📊 Statistics")

    micro_count = len(st.session_state.get("saved_microbiology", []))
    transfer_count = len(st.session_state.get("saved_transfers", []))

    st.metric("🔬 Microbiology", micro_count)
    st.metric("🚑 Transfers", transfer_count)
    st.metric("📊 Total", micro_count + transfer_count)
