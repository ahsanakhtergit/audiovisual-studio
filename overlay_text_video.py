import cv2
import moviepy.editor as mp
import json
import numpy as np

# Load Whisper output JSON
with open("audio.json", "r") as f:
    data = json.load(f)

# Load video
video = mp.VideoFileClip("input_video.mp4")
width, height = int(video.w), int(video.h)
fps = int(video.fps)

# Create output video writer (without audio)
temp_video_path = "temp_video.mp4"
out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

# Extract sentence-wise data
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

# Append the last sentence
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
    time_sec = video.reader.pos / fps

    # Find the active sentence
    active_sentence = None
    for sentence in sentences:
        if sentence["start"] <= time_sec <= sentence["end"]:
            active_sentence = sentence
            break
    
    if active_sentence:
        base_text = active_sentence["text"]
        words = active_sentence["words"]
        
        # Define text position and style
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        base_color = (255, 255, 255)  # White text
        highlight_color = (0, 0, 255)  # Red highlight
        background_color = (0, 0, 0)  # Black rectangle
        
        # Get text size
        text_size = cv2.getTextSize(base_text, font, font_scale, thickness)[0]
        x = (width - text_size[0]) // 2
        y = height // 2
        
        # Draw black rectangle as background for text
        cv2.rectangle(img, (x - 10, y - 40), (x + text_size[0] + 10, y + 10), background_color, -1)

        # Draw base sentence text
        word_x = x
        for word in words:
            word_size = cv2.getTextSize(word["word"] + " ", font, font_scale, thickness)[0]
            cv2.putText(img, word["word"], (word_x, y), font, font_scale, base_color, thickness, cv2.LINE_AA)
            word_x += word_size[0]

        # Highlight words as they are spoken
        word_x = x
        for word in words:
            word_size = cv2.getTextSize(word["word"] + " ", font, font_scale, thickness)[0]
            if word["start"] <= time_sec <= word["end"]:
                cv2.putText(img, word["word"], (word_x, y), font, font_scale, highlight_color, thickness, cv2.LINE_AA)
            word_x += word_size[0]
    
    out.write(img)

out.release()
print("Video processing completed. Merging with audio...")

# Merge audio back
final_output = "output_video.mp4"
processed_video = mp.VideoFileClip(temp_video_path)
processed_video = processed_video.set_audio(video.audio)
processed_video.write_videofile(final_output, codec="libx264", fps=fps)

print("Final video with audio saved as output_video.mp4")
