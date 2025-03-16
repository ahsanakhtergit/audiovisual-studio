import streamlit as st
import cv2
import moviepy.editor as mp
import json
import numpy as np
import os

def apply_subtitle_style(frame, subtitle, width, height, template, time_sec, words):
    """Apply different subtitle styles based on selected template"""
    img = frame.copy()
    img.setflags(write=1)  # Fix OpenCV read-only error

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 3
    base_color = (255, 255, 255)  # White text
    highlight_color = (0, 0, 255)  # Red highlight
    background_color = (0, 0, 0)  # Black background

    # Calculate text placement
    text_size = cv2.getTextSize(subtitle, font, font_scale, thickness)[0]
    x = (width - text_size[0]) // 2
    y = height - 80  # Subtitle position

    # Add background for better readability
    cv2.rectangle(img, (x - 10, y - 40), (x + text_size[0] + 10, y + 10), background_color, -1)

    word_x = x  # Start position for words

    for word in words:
        word_text = word["word"] + " "  # Add space for proper spacing
        word_size = cv2.getTextSize(word_text, font, font_scale, thickness)[0]

        # Highlight the word only when it's being spoken
        if word["start"] <= time_sec <= word["end"]:
            cv2.putText(img, word_text, (word_x, y), font, font_scale, highlight_color, thickness, cv2.LINE_AA)
        else:
            cv2.putText(img, word_text, (word_x, y), font, font_scale, base_color, thickness, cv2.LINE_AA)

        word_x += word_size[0]  # Move to the next word position

    return img

def mp4_subtitle_animation_tool():
    st.header("🎞 MP4 Subtitle Animation")
    st.write("Upload an MP4 file and an Audio JSON file to create an animated subtitle video.")

    uploaded_mp4 = st.file_uploader("Upload MP4 Video", type=["mp4"])
    uploaded_json = st.file_uploader("Upload Audio JSON File", type=["json"])

    # Template selection
    templates = ["Classic Subtitles", "Pop-up Text", "Typewriter Effect", "Bold & Flashy", "Minimalistic"]
    selected_template = st.selectbox("Choose Subtitle Animation Style", templates)

    if st.button("Generate Animated Subtitle Video"):
        if uploaded_mp4 and uploaded_json:
            st.success(f"Processing with {selected_template}...")

            # Save uploaded files
            mp4_path = "input_video.mp4"
            json_path = "audio.json"

            with open(mp4_path, "wb") as f:
                f.write(uploaded_mp4.read())
            with open(json_path, "wb") as f:
                f.write(uploaded_json.read())

            # Load JSON
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                st.error("Invalid JSON format.")
                return

            # Load video
            video = mp.VideoFileClip(mp4_path)
            width, height = int(video.w), int(video.h)
            fps = int(video.fps)

            temp_video_path = "temp_video.mp4"
            out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

            sentences = []
            current_sentence = ""
            current_start = None
            words_data = []

            for segment in data["segments"]:
                for word in segment["words"]:
                    if current_sentence and word["start"] - words_data[-1]["end"] > 0.5:
                        sentences.append({
                            "text": current_sentence.strip(),
                            "start": current_start,
                            "end": words_data[-1]["end"],
                            "words": words_data
                        })
                        current_sentence = ""
                        words_data = []

                    if not current_sentence:
                        current_start = word["start"]

                    current_sentence += word["word"] + " "
                    words_data.append(word)

            if current_sentence:
                sentences.append({
                    "text": current_sentence.strip(),
                    "start": current_start,
                    "end": words_data[-1]["end"],
                    "words": words_data
                })

            # Process video frames
            for frame in video.iter_frames(fps=fps, dtype="uint8"):
                img = frame.copy()
                img.setflags(write=1)  # Fix read-only error
                time_sec = video.reader.pos / fps

                # Find the active sentence
                active_sentence = None
                for sentence in sentences:
                    if sentence["start"] <= time_sec <= sentence["end"]:
                        active_sentence = sentence
                        break

                if active_sentence:
                    subtitle = active_sentence["text"]
                    img = apply_subtitle_style(img, subtitle, width, height, selected_template, time_sec, active_sentence["words"])

                out.write(img)

            out.release()
            st.success("Video processing completed. Merging with audio...")

            # Merge audio back
            final_output = "output_video.mp4"
            processed_video = mp.VideoFileClip(temp_video_path)
            processed_video = processed_video.set_audio(video.audio)
            processed_video.write_videofile(final_output, codec="libx264", fps=fps)

            st.success("Final video with subtitles is ready!")
            st.video(final_output)

            # Download Option
            with open(final_output, "rb") as file:
                st.download_button("Download Video", file, final_output, mime="video/mp4")
        else:
            st.error("Please upload both an MP4 and JSON file.")
