import os
import tempfile
import streamlit as st
from moviepy.editor import AudioFileClip, ColorClip, CompositeVideoClip
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import wave
import json

# Set the path to the ImageMagick binary
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

def transcribe_audio_to_word_timings(input_mp3):
    """Convert MP3 to WAV and transcribe it using the Vosk model."""
    # Convert MP3 to WAV (Vosk requires WAV format)
    audio = AudioSegment.from_mp3(input_mp3)
    audio.export("temp.wav", format="wav")

    # Load Vosk model
    model_path = "models/vosk-model-small-en-us-0.15"  # Path to the Vosk model
    model = Model(model_path)

    # Open the WAV file
    wf = wave.open("temp.wav", "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())
    recognizer.SetWords(True)  # Enable word-level timings

    word_timings = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if "result" in result:
                for word in result["result"]:
                    word_timings.append((word["word"], word["start"], word["end"]))

    # Get the final result
    final_result = json.loads(recognizer.FinalResult())
    if "result" in final_result:
        for word in final_result["result"]:
            word_timings.append((word["word"], word["start"], word["end"]))

    return word_timings

def mp3_to_mp4_tool():
    st.write("Convert MP3 files to MP4 videos.")

    # Input: MP3 file upload
    mp3_file = st.file_uploader("Upload MP3 File:", type=["mp3"])

    # Aspect ratio selection
    aspect_ratio = st.selectbox("Select Aspect Ratio:", ["16:9", "4:3", "1:1"], index=0)

    # Generate video
    if st.button("Generate Video"):
        if mp3_file:
            # Save the uploaded MP3 file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(mp3_file.getbuffer())
                mp3_path = tmp_file.name

            try:
                # Load the MP3 file
                audio_clip = AudioFileClip(mp3_path)

                # Create a blank video with the selected aspect ratio
                if aspect_ratio == "16:9":
                    width, height = 1920, 1080
                elif aspect_ratio == "4:3":
                    width, height = 1440, 1080
                else:
                    width, height = 1080, 1080

                # Create a green background using ColorClip
                background = ColorClip(size=(width, height), color=(0, 255, 0), duration=audio_clip.duration)

                # Combine background and audio
                final_clip = CompositeVideoClip([background]).set_audio(audio_clip)

                # Save the video
                output_file = "generated_video.mp4"
                final_clip.write_videofile(output_file, fps=24)

                st.success("Video generated successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Close the audio clip to release the file handle
                audio_clip.close()
                # Clean up the temporary file
                os.unlink(mp3_path)
        else:
            st.error("Please upload an MP3 file.")

    # Preview and download
    if st.button("Preview Video"):
        if os.path.exists("generated_video.mp4"):
            st.video("generated_video.mp4")
        else:
            st.error("No video file found. Please generate the video first.")

    if os.path.exists("generated_video.mp4"):
        with open("generated_video.mp4", "rb") as f:
            video_bytes = f.read()
        st.download_button("Download Video", video_bytes, file_name="generated_video.mp4", mime="video/mp4")
