import streamlit as st
import asyncio
from edge_tts import VoicesManager, Communicate
import os

async def list_voices(gender=None, language=None):
    # Create a VoicesManager instance
    voices_manager = await VoicesManager.create()
    voices = voices_manager.voices

    # Filter voices based on gender and language
    filtered_voices = []
    for voice in voices:
        voice_gender = voice["Gender"].lower()
        voice_locale = voice["Locale"].lower()

        # Gender filter
        gender_match = (
            (gender.lower() == voice_gender) or
            (gender == "any")
        )

        # Language filter
        language_match = (
            (language.lower() in voice_locale) or
            (language == "any")
        )

        if gender_match and language_match:
            filtered_voices.append(voice)

    return filtered_voices

async def generate_audio(text, voice, output_file):
    # Use edge_tts to generate audio
    communicate = Communicate(text, voice)
    await communicate.save(output_file)

def tts_tool():
    st.write("Convert text to speech and generate audio files.")

    # Input: Text or file upload
    text_input = st.text_area("Enter Text:", placeholder="Type or paste your text here...")
    uploaded_file = st.file_uploader("Or upload a text file:", type=["txt"])

    # Gender and language selection
    st.subheader("Filter Voices")
    gender = st.radio("Select Gender:", ["Male", "Female", "Any"])
    language = st.selectbox("Select Language:", ["en", "es", "fr", "de", "it", "Any"])  # Use language codes

    # Get filtered voices
    filtered_voices = asyncio.run(list_voices(gender, language))

    # Display filtered voice models
    st.subheader("Available Voice Models")
    if filtered_voices:
        voice_options = {voice["Name"]: voice["Name"] for voice in filtered_voices}
        selected_voice = st.selectbox("Select Voice:", list(voice_options.keys()))
    else:
        st.warning("No voice models found for the selected gender and language.")
        return

    # Preview selected voice
    if st.button("Preview Voice"):
        # Use edge_tts to preview the voice
        preview_text = "This is a preview of the selected voice model."
        asyncio.run(generate_audio(preview_text, selected_voice, "preview_audio.mp3"))
        st.audio("preview_audio.mp3", format="audio/mp3")
        st.write("Previewing voice model...")

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Audio"):
            if text_input or uploaded_file:
                text_to_speak = text_input if text_input else uploaded_file.getvalue().decode("utf-8")
                asyncio.run(generate_audio(text_to_speak, selected_voice, "generated_audio.mp3"))
                st.success("Audio file generated successfully!")
            else:
                st.error("Please enter text or upload a file.")
    with col2:
        if st.button("Test Generated Audio"):
            if os.path.exists("generated_audio.mp3"):
                st.audio("generated_audio.mp3", format="audio/mp3")
            else:
                st.error("No audio file found. Please generate the audio first.")

    # Download generated audio
    if os.path.exists("generated_audio.mp3"):
        with open("generated_audio.mp3", "rb") as f:
            audio_bytes = f.read()
        st.download_button(
            label="Download Audio",
            data=audio_bytes,
            file_name="generated_audio.mp3",
            mime="audio/mp3"
        )