import streamlit as st
import subprocess
import json
import os
import tempfile

def transcribe_audio(mp3_path, output_dir):
    """ Transcribes MP3 audio using Whisper and saves JSON output """
    command = [
        "whisper", mp3_path,
        "--model", "small",
        "--word_timestamps", "True",
        "--output_format", "json",
        "--output_dir", output_dir
    ]
    subprocess.run(command, check=True)
    
    json_filename = os.path.join(output_dir, os.path.splitext(os.path.basename(mp3_path))[0] + ".json")
    
    with open(json_filename, "r") as f:
        return json.load(f), json_filename

def mp3_word_timestamp_tool():
    st.header("🎤 MP3 to Word & Sentence-Level Timestamps")
    st.write("Upload an MP3 file to generate timestamps.")

    uploaded_mp3 = st.file_uploader("Upload MP3 File", type=["mp3"])

    if st.button("Generate Timestamps"):
        if uploaded_mp3:
            st.success("Processing... This may take a few minutes.")

            # Save uploaded MP3 to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(uploaded_mp3.read())
                mp3_path = temp_file.name

            output_dir = tempfile.mkdtemp()
            timestamps, json_filename = transcribe_audio(mp3_path, output_dir)

            st.success("Timestamps Generated Successfully!")

            # Show preview in collapsed mode
            with st.expander("🔍 View Timestamps (First 5 Segments)"):
                st.json(timestamps["segments"][:5])

            # Format JSON properly before saving
            formatted_json_path = os.path.join(output_dir, "generated_timestamps.json")
            with open(formatted_json_path, "w", encoding="utf-8") as f:
                json.dump(timestamps, f, indent=4, ensure_ascii=False)

            # Provide download button for formatted JSON
            with open(formatted_json_path, "rb") as file:
                st.download_button("📥 Download JSON", file, "generated_timestamps.json", mime="application/json")

            # Cleanup
            os.remove(mp3_path)
            os.remove(json_filename)
            os.remove(formatted_json_path)

        else:
            st.error("Please upload an MP3 file.")

if __name__ == "__main__":
    mp3_word_timestamp_tool()
