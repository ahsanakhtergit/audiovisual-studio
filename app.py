import os
import streamlit as st
from tts_tool import tts_tool
from mp3_to_mp4_tool import mp3_to_mp4_tool
from mp4_animation_tool import mp4_animation_tool
from mp4_subtitle_animation_tool import mp4_subtitle_animation_tool
from mp3_word_timestamp_tool import mp3_word_timestamp_tool  # New Import

# Set page configuration
st.set_page_config(
    page_title="AudioVisual Studio",
    page_icon="🎥",
    layout="wide",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        margin-top: -50px;
        padding-top: 0;
    }
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
        text-align: center;
    }
    .card:hover {
        transform: scale(1.05);
    }
    .card h3 {
        margin: 0;
        font-size: 24px;
        color: #4CAF50;
    }
    .card p {
        margin: 10px 0;
        color: #555;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = "Text-to-Speech"

# Title
st.title("🎥 AudioVisual Studio")
st.markdown("---")

# Cards for the tools
col1, col2, col3, col4, col5 = st.columns(5)  # Added extra column for new tool

with col1:
    if st.button("📝 Text-to-Speech"):
        st.session_state.selected_tool = "Text-to-Speech"
    st.markdown("""<div class="card"><h3>📝 Text-to-Speech</h3><p>Convert text to speech.</p></div>""", unsafe_allow_html=True)

with col2:
    if st.button("🎧 MP3 to MP4"):
        st.session_state.selected_tool = "MP3 to MP4"
    st.markdown("""<div class="card"><h3>🎧 MP3 to MP4</h3><p>Convert MP3 files to MP4 videos.</p></div>""", unsafe_allow_html=True)

with col3:
    if st.button("🎬 MP4 Animation"):
        st.session_state.selected_tool = "MP4 Animation"
    st.markdown("""<div class="card"><h3>🎬 MP4 Animation</h3><p>Add word highlights to videos.</p></div>""", unsafe_allow_html=True)

with col4:
    if st.button("🎞 MP4 Subtitle Animation"):
        st.session_state.selected_tool = "MP4 Subtitle Animation"
    st.markdown("""<div class="card"><h3>🎞 MP4 Subtitle Animation</h3><p>Create animated subtitles for videos.</p></div>""", unsafe_allow_html=True)

with col5:  # Added new button for MP3 Word Timestamp
    if st.button("🎤 MP3 Word Timestamps"):
        st.session_state.selected_tool = "MP3 Word Timestamps"
    st.markdown("""<div class="card"><h3>🎤 MP3 Word Timestamps</h3><p>Generate word-level speech timestamps.</p></div>""", unsafe_allow_html=True)

# Tool Sections
st.markdown("---")

if st.session_state.selected_tool == "Text-to-Speech":
    tts_tool()
elif st.session_state.selected_tool == "MP3 to MP4":
    mp3_to_mp4_tool()
elif st.session_state.selected_tool == "MP4 Animation":
    mp4_animation_tool()
elif st.session_state.selected_tool == "MP4 Subtitle Animation":
    mp4_subtitle_animation_tool()
elif st.session_state.selected_tool == "MP3 Word Timestamps":  # New case
    mp3_word_timestamp_tool()

st.markdown("---")
st.markdown("© 2025 AudioVisual Studio. All rights reserved.")
