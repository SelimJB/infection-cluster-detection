"""
Custom CSS styles for the Streamlit application
"""
import streamlit as st


def load_custom_css():
    """
    Load custom CSS styles for the application
    """
    st.markdown("""
    <style>
    /* Green primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    .stButton > button[kind="primary"]:focus {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.5) !important;
    }
    .stButton > button[kind="primary"]:disabled {
        background-color: #6c757d !important;
        border-color: #6c757d !important;
        color: #fff !important;
        opacity: 0.65 !important;
    }
    
    /* Secondary buttons styling */
    .stButton > button[kind="secondary"] {
        background-color: #6c757d !important;
        border-color: #6c757d !important;
        color: white !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #5a6268 !important;
        border-color: #545b62 !important;
    }
    
    /* Custom styling for file upload areas */
    .stFileUploader > div {
        border: 2px dashed #28a745 !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }
    
    /* Custom styling for success messages */
    .stSuccess {
        background-color: #d4edda !important;
        border-color: #c3e6cb !important;
        color: #155724 !important;
    }
    
    /* Custom styling for info messages */
    .stInfo {
        background-color: #d1ecf1 !important;
        border-color: #bee5eb !important;
        color: #0c5460 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def load_minimal_css():
    """
    Load minimal CSS styles (just green buttons)
    """
    st.markdown("""
    <style>
    .stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    .stButton > button[kind="primary"]:disabled {
        background-color: #6c757d !important;
        border-color: #6c757d !important;
        opacity: 0.65 !important;
    }
    </style>
    """, unsafe_allow_html=True)
